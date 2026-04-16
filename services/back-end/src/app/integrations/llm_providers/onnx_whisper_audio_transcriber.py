from __future__ import annotations

import logging
import os
import shutil
import subprocess  # nosec B404: required to invoke local ffmpeg for deterministic audio decoding
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import Any

import numpy as np

from app.domain_models.common.exceptions import AudioTranscriptionError

try:
    import onnxruntime as ort
except Exception:  # pragma: no cover - import guard
    ort = None

try:
    from transformers import AutoProcessor
except Exception:  # pragma: no cover - import guard
    AutoProcessor = None


@dataclass(frozen=True)
class _DecodeConfig:
    eos_token_id: int | None
    generation_limit: int


_ENCODER_MODEL_FILENAME = "encoder_model.onnx"
_DECODER_MODEL_FILENAME = "decoder_model.onnx"

_REQUIRED_MODEL_FILES = (
    "config.json",
    "preprocessor_config.json",
    "tokenizer.json",
    _ENCODER_MODEL_FILENAME,
    _DECODER_MODEL_FILENAME,
)

_KNOWN_MODEL_ARTIFACT_FILES = (
    "added_tokens.json",
    "config.json",
    _DECODER_MODEL_FILENAME,
    _ENCODER_MODEL_FILENAME,
    "generation_config.json",
    "mel_filters.bin",
    "merges.txt",
    "normalizer.json",
    "preprocessor_config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
)
_MODEL_DOWNLOAD_TIMEOUT_SECONDS = 600

logger = logging.getLogger(__name__)


class OnnxWhisperAudioTranscriber:
    """Whisper transcription using pure ONNX Runtime sessions on CPU."""

    def __init__(
        self,
        model_dir: Path,
        default_language: str = "pt",
        *,
        model_download_url: str | None = None,
        auto_download_enabled: bool = False,
    ) -> None:
        self._model_dir = model_dir
        self._default_language = default_language
        self._model_download_url = (model_download_url or "").strip() or None
        self._auto_download_enabled = auto_download_enabled
        self._processor: Any | None = None
        self._encoder_session: Any | None = None
        self._decoder_session: Any | None = None
        self._lock = Lock()

    def transcribe(self, *, audio_bytes: bytes, filename: str, language: str | None = None) -> str:
        if not audio_bytes:
            raise AudioTranscriptionError("O arquivo de audio enviado esta vazio.")

        suffix = Path(filename).suffix if filename else ""
        with NamedTemporaryFile(suffix=suffix or ".audio", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = Path(temp_file.name)

        try:
            processor = self._get_processor()
            encoder_session = self._get_encoder_session()
            decoder_session = self._get_decoder_session()
            effective_language = (language or self._default_language or "").strip()
            resolved_language = self._resolve_language(effective_language)

            audio_samples = self._decode_audio_to_pcm_float32(temp_path)
            input_features = processor.feature_extractor(
                audio_samples,
                sampling_rate=16000,
                return_tensors="np",
            )["input_features"].astype(np.float32)

            encoder_input_name = encoder_session.get_inputs()[0].name
            encoder_output_name = encoder_session.get_outputs()[0].name
            encoder_hidden_states = encoder_session.run(
                [encoder_output_name],
                {encoder_input_name: input_features},
            )[0]

            decoder_start_token_id = processor.tokenizer.convert_tokens_to_ids("<|startoftranscript|>")
            prompt_ids = [decoder_start_token_id]
            prompt_ids.extend(
                token_id
                for _, token_id in processor.get_decoder_prompt_ids(
                    language=resolved_language,
                    task="transcribe",
                )
            )

            generated_ids = self._greedy_decode(
                decoder_session=decoder_session,
                encoder_hidden_states=encoder_hidden_states,
                prompt_ids=prompt_ids,
                decode_config=_DecodeConfig(
                    eos_token_id=processor.tokenizer.eos_token_id,
                    generation_limit=160,
                ),
            )
            transcription = processor.tokenizer.decode(
                generated_ids,
                skip_special_tokens=True,
            ).strip()
            if not transcription:
                raise AudioTranscriptionError("Nao foi possivel transcrever o audio enviado.")
            return transcription
        except AudioTranscriptionError:
            raise
        except Exception as exc:  # pragma: no cover - defensive integration guard
            raise AudioTranscriptionError("Falha ao transcrever audio com Whisper ONNX.") from exc
        finally:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass

    def ensure_model_ready(self) -> None:
        self._ensure_model_files_available()

    def _get_processor(self) -> Any:
        if self._processor is not None:
            return self._processor

        with self._lock:
            if self._processor is not None:
                return self._processor

            self._processor = self._build_processor()
            return self._processor

    def _get_encoder_session(self) -> Any:
        if self._encoder_session is not None:
            return self._encoder_session

        with self._lock:
            if self._encoder_session is not None:
                return self._encoder_session

            self._encoder_session = self._build_encoder_session()
            return self._encoder_session

    def _get_decoder_session(self) -> Any:
        if self._decoder_session is not None:
            return self._decoder_session

        with self._lock:
            if self._decoder_session is not None:
                return self._decoder_session

            self._decoder_session = self._build_decoder_session()
            return self._decoder_session

    def _build_processor(self) -> Any:
        self._ensure_model_files_available()

        if AutoProcessor is None:
            raise AudioTranscriptionError(
                "Dependencias de transcricao ONNX nao instaladas. Instale transformers e onnxruntime."
            )

        return AutoProcessor.from_pretrained(  # nosec B615: model_dir is a local repository path
            self._model_dir,
            local_files_only=True,
            revision="main",
        )

    def _ensure_model_files_available(self) -> None:
        self._adopt_downloaded_layout_if_needed()
        missing_files = self._list_missing_model_files()
        if not missing_files:
            return

        if not self._auto_download_enabled:
            raise AudioTranscriptionError(
                f"Arquivos do modelo Whisper ONNX ausentes em {self._model_dir}: {', '.join(missing_files)}."
            )
        if not self._model_download_url:
            raise AudioTranscriptionError(
                "WHISPER_MODEL_DOWNLOAD_URL nao configurada para baixar o modelo Whisper ONNX."
            )

        logger.info(
            "Whisper model files are missing, downloading to %s.",
            self._model_dir,
        )
        self._download_model_files()
        self._adopt_downloaded_layout_if_needed()
        remaining_missing_files = self._list_missing_model_files()
        if remaining_missing_files:
            raise AudioTranscriptionError(
                "Download do modelo Whisper concluido, mas arquivos obrigatorios continuam ausentes: "
                f"{', '.join(remaining_missing_files)}."
            )
        logger.info("Whisper model download completed successfully.")

    def _adopt_downloaded_layout_if_needed(self) -> None:
        source_dir = self._find_model_source_dir()
        if source_dir is None:
            return
        self._move_model_artifacts(source_dir)

    def _find_model_source_dir(self) -> Path | None:
        model_parent_dir = self._model_dir.parent
        if not model_parent_dir.exists():
            return None

        candidates: list[Path] = [model_parent_dir]
        candidates.extend(
            child
            for child in model_parent_dir.iterdir()
            if child.is_dir() and child != self._model_dir
        )
        for candidate in candidates:
            if all((candidate / filename).exists() for filename in _REQUIRED_MODEL_FILES):
                return candidate
        return None

    def _move_model_artifacts(self, source_dir: Path) -> None:
        self._model_dir.mkdir(parents=True, exist_ok=True)
        for artifact_name in _KNOWN_MODEL_ARTIFACT_FILES:
            source_path = source_dir / artifact_name
            target_path = self._model_dir / artifact_name
            if source_path.exists() and source_path != target_path:
                shutil.move(str(source_path), str(target_path))

    def _list_missing_model_files(self) -> list[str]:
        return [
            filename
            for filename in _REQUIRED_MODEL_FILES
            if not (self._model_dir / filename).exists()
        ]

    def _download_model_files(self) -> None:
        command = [
            os.sys.executable,
            "-m",
            "gdown",
            "--folder",
            self._model_download_url,
            "-O",
            str(self._model_dir.parent),
            "--remaining-ok",
            "--quiet",
        ]
        try:
            self._model_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                shell=False,  # nosec B603: fixed command and arguments
                timeout=_MODEL_DOWNLOAD_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise AudioTranscriptionError(
                f"Tempo limite excedido ao baixar o modelo Whisper ONNX ({_MODEL_DOWNLOAD_TIMEOUT_SECONDS}s)."
            ) from exc
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or exc.stdout or "").strip()
            if "No module named gdown" in details:
                raise AudioTranscriptionError("Dependencia gdown nao instalada para baixar o modelo Whisper.") from exc
            if details:
                raise AudioTranscriptionError(
                    f"Falha ao baixar o modelo Whisper ONNX do Google Drive: {details.splitlines()[-1][:240]}"
                ) from exc
            raise AudioTranscriptionError("Falha ao baixar o modelo Whisper ONNX do Google Drive.") from exc
        except Exception as exc:  # pragma: no cover - external download guard
            raise AudioTranscriptionError("Falha ao baixar o modelo Whisper ONNX do Google Drive.") from exc

    def _build_encoder_session(self) -> Any:
        if ort is None:
            raise AudioTranscriptionError("Dependencia onnxruntime nao instalada.")

        return ort.InferenceSession(
            str(self._model_dir / _ENCODER_MODEL_FILENAME),
            providers=["CPUExecutionProvider"],
        )

    def _build_decoder_session(self) -> Any:
        if ort is None:
            raise AudioTranscriptionError("Dependencia onnxruntime nao instalada.")

        return ort.InferenceSession(
            str(self._model_dir / _DECODER_MODEL_FILENAME),
            providers=["CPUExecutionProvider"],
        )

    def _resolve_ffmpeg_binary(self) -> str:
        ffmpeg_binary = shutil.which("ffmpeg")
        if not ffmpeg_binary:
            raise AudioTranscriptionError("FFmpeg nao encontrado no ambiente para decodificar audio.")
        return ffmpeg_binary

    def _decode_audio_to_pcm_float32(self, audio_path: Path) -> np.ndarray:
        ffmpeg_binary = self._resolve_ffmpeg_binary()
        command = [
            ffmpeg_binary,
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(audio_path),
            "-f",
            "f32le",
            "-ac",
            "1",
            "-ar",
            "16000",
            "pipe:1",
        ]
        try:
            result = subprocess.run(  # nosec B603: uses vetted local binary with fixed args and shell disabled
                command,
                check=True,
                capture_output=True,
                shell=False,
                timeout=30,
            )
        except Exception as exc:  # pragma: no cover - external command guard
            raise AudioTranscriptionError("Falha ao converter audio para PCM 16kHz mono.") from exc

        samples = np.frombuffer(result.stdout, dtype=np.float32)
        if samples.size == 0:
            raise AudioTranscriptionError("Nao foi possivel extrair audio valido do arquivo enviado.")
        return samples

    def _resolve_language(self, language: str) -> str | None:
        if not language or language.lower() == "auto":
            return None

        normalized = language.strip().lower()
        aliases = {
            "pt": "portuguese",
            "en": "english",
            "es": "spanish",
        }
        return aliases.get(normalized, normalized)

    def _greedy_decode(
        self,
        *,
        decoder_session: Any,
        encoder_hidden_states: np.ndarray,
        prompt_ids: list[int],
        decode_config: _DecodeConfig,
    ) -> list[int]:
        input_ids = np.array([prompt_ids], dtype=np.int64)
        decoder_input_ids_name = decoder_session.get_inputs()[0].name
        decoder_encoder_hidden_name = decoder_session.get_inputs()[1].name
        decoder_logits_name = decoder_session.get_outputs()[0].name

        for _ in range(decode_config.generation_limit):
            logits = decoder_session.run(
                [decoder_logits_name],
                {
                    decoder_input_ids_name: input_ids,
                    decoder_encoder_hidden_name: encoder_hidden_states,
                },
            )[0]
            next_token_id = int(np.argmax(logits[0, -1, :]))
            input_ids = np.concatenate(
                [input_ids, np.array([[next_token_id]], dtype=np.int64)],
                axis=1,
            )
            if decode_config.eos_token_id is not None and next_token_id == decode_config.eos_token_id:
                break

        return input_ids[0].tolist()
