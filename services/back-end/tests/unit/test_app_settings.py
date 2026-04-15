from pathlib import Path

import pytest

from app.bootstrap.settings import AppSettings


def test_from_env_requires_database_url() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")

        with pytest.raises(AssertionError, match="DATABASE_URL must be set"):
            AppSettings.from_env()


def test_from_env_requires_postgres_database_url() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:////tmp/test.db")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")

        with pytest.raises(AssertionError, match="PostgreSQL"):
            AppSettings.from_env()


def test_from_env_accepts_postgres_database_url() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")

        settings = AppSettings.from_env()

    assert settings.database_url == "postgresql://postgres:postgres@localhost:5432/mais_a_educ"
    assert settings.datasets_dir == Path(__file__).resolve().parents[4] / "services" / "datasets"


def test_from_env_requires_minio_access_key() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")
        monkeypatch.delenv("MINIO_ACCESS_KEY", raising=False)
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")

        with pytest.raises(AssertionError, match="MINIO_ACCESS_KEY must be set"):
            AppSettings.from_env()


def test_from_env_requires_minio_secret_key() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.delenv("MINIO_SECRET_KEY", raising=False)

        with pytest.raises(AssertionError, match="MINIO_SECRET_KEY must be set"):
            AppSettings.from_env()


def test_from_env_accepts_legacy_minio_bucket_name() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")
        monkeypatch.setenv("MINIO_BUCKET_NAME", "mais-a-educ")
        monkeypatch.delenv("MINIO_EXPORT_BUCKET", raising=False)

        settings = AppSettings.from_env()

    assert settings.minio_export_bucket == "mais-a-educ"


def test_from_env_uses_default_whisper_download_settings() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")
        monkeypatch.delenv("WHISPER_MODEL_DOWNLOAD_URL", raising=False)
        monkeypatch.delenv("WHISPER_MODEL_AUTO_DOWNLOAD_ENABLED", raising=False)

        settings = AppSettings.from_env()

    assert settings.whisper_model_download_url.startswith("https://drive.google.com/drive/folders/")
    assert settings.whisper_model_auto_download_enabled is True


def test_from_env_allows_overriding_whisper_download_settings() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")
        monkeypatch.setenv("MINIO_ACCESS_KEY", "test-key")
        monkeypatch.setenv("MINIO_SECRET_KEY", "test-secret")
        monkeypatch.setenv("WHISPER_MODEL_DOWNLOAD_URL", "https://example.com/model-folder")
        monkeypatch.setenv("WHISPER_MODEL_AUTO_DOWNLOAD_ENABLED", "false")

        settings = AppSettings.from_env()

    assert settings.whisper_model_download_url == "https://example.com/model-folder"
    assert settings.whisper_model_auto_download_enabled is False
