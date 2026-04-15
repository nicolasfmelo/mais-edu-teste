from pathlib import Path

import pytest

from app.domain_models.common.exceptions import AudioTranscriptionError
from app.integrations.llm_providers import onnx_whisper_audio_transcriber as transcriber_module
from app.integrations.llm_providers.onnx_whisper_audio_transcriber import (
    _REQUIRED_MODEL_FILES,
    OnnxWhisperAudioTranscriber,
)


def _create_required_model_files(model_dir: Path) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    for filename in _REQUIRED_MODEL_FILES:
        (model_dir / filename).write_bytes(b"test")


def test_ensure_model_files_available_raises_when_download_is_disabled(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "whisper-small"
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        auto_download_enabled=False,
    )

    with pytest.raises(AudioTranscriptionError, match="Arquivos do modelo Whisper ONNX ausentes"):
        transcriber._ensure_model_files_available()


def test_ensure_model_files_available_raises_when_gdown_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "models" / "whisper-small"
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        model_download_url="https://drive.google.com/drive/folders/test",
        auto_download_enabled=True,
    )
    monkeypatch.setattr(transcriber_module, "gdown", None)

    with pytest.raises(AudioTranscriptionError, match="Dependencia gdown"):
        transcriber._ensure_model_files_available()


def test_ensure_model_files_available_downloads_folder_when_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "models" / "whisper-small"
    calls = {"count": 0}

    class FakeGDown:
        @staticmethod
        def download_folder(*, url: str, output: str, quiet: bool, remaining_ok: bool):  # noqa: ANN206
            assert "drive.google.com" in url
            assert quiet is True
            assert remaining_ok is True
            calls["count"] += 1
            _create_required_model_files(Path(output) / "whisper-small")
            return ["ok"]

    monkeypatch.setattr(transcriber_module, "gdown", FakeGDown)
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        model_download_url="https://drive.google.com/drive/folders/test",
        auto_download_enabled=True,
    )

    transcriber._ensure_model_files_available()

    assert calls["count"] == 1
    for filename in _REQUIRED_MODEL_FILES:
        assert (model_dir / filename).exists()


def test_ensure_model_files_available_skips_download_when_files_are_present(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "models" / "whisper-small"
    _create_required_model_files(model_dir)
    calls = {"count": 0}

    class FakeGDown:
        @staticmethod
        def download_folder(*, url: str, output: str, quiet: bool, remaining_ok: bool):  # noqa: ANN206
            calls["count"] += 1
            return ["ok"]

    monkeypatch.setattr(transcriber_module, "gdown", FakeGDown)
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        model_download_url="https://drive.google.com/drive/folders/test",
        auto_download_enabled=True,
    )

    transcriber._ensure_model_files_available()

    assert calls["count"] == 0


def test_ensure_model_files_available_adopts_flat_layout_without_redownloading(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    models_root = tmp_path / "models"
    model_dir = models_root / "whisper-small"
    _create_required_model_files(models_root)
    calls = {"count": 0}

    class FakeGDown:
        @staticmethod
        def download_folder(*, url: str, output: str, quiet: bool, remaining_ok: bool):  # noqa: ANN206
            calls["count"] += 1
            return ["ok"]

    monkeypatch.setattr(transcriber_module, "gdown", FakeGDown)
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        model_download_url="https://drive.google.com/drive/folders/test",
        auto_download_enabled=True,
    )

    transcriber._ensure_model_files_available()

    assert calls["count"] == 0
    for filename in _REQUIRED_MODEL_FILES:
        assert (model_dir / filename).exists()
