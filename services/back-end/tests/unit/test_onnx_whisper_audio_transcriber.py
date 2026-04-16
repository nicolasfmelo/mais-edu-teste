from pathlib import Path
import subprocess

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
    def fake_run(args, **kwargs):  # noqa: ANN001, ANN003, ANN202
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=args,
            stderr="No module named gdown",
        )

    monkeypatch.setattr(transcriber_module.subprocess, "run", fake_run)

    with pytest.raises(AudioTranscriptionError, match="Dependencia gdown"):
        transcriber._ensure_model_files_available()


def test_ensure_model_files_available_downloads_folder_when_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_dir = tmp_path / "models" / "whisper-small"
    calls = {"count": 0}

    def fake_run(args, **kwargs):  # noqa: ANN001, ANN003, ANN202
        assert "python" in Path(args[0]).name
        assert args[1:4] == ["-m", "gdown", "--folder"]
        assert "drive.google.com" in args[4]
        assert "--remaining-ok" in args
        assert "--quiet" in args
        assert kwargs["timeout"] > 0
        calls["count"] += 1
        _create_required_model_files(Path(args[6]) / "whisper-small")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(transcriber_module.subprocess, "run", fake_run)
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

    def fake_run(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        calls["count"] += 1
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(transcriber_module.subprocess, "run", fake_run)
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

    def fake_run(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        calls["count"] += 1
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(transcriber_module.subprocess, "run", fake_run)
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        model_download_url="https://drive.google.com/drive/folders/test",
        auto_download_enabled=True,
    )

    transcriber._ensure_model_files_available()

    assert calls["count"] == 0
    for filename in _REQUIRED_MODEL_FILES:
        assert (model_dir / filename).exists()


def test_ensure_model_ready_delegates_to_file_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    model_dir = tmp_path / "models" / "whisper-small"
    transcriber = OnnxWhisperAudioTranscriber(
        model_dir=model_dir,
        auto_download_enabled=False,
    )
    calls = {"count": 0}

    def fake_ensure() -> None:
        calls["count"] += 1

    monkeypatch.setattr(transcriber, "_ensure_model_files_available", fake_ensure)

    transcriber.ensure_model_ready()

    assert calls["count"] == 1
