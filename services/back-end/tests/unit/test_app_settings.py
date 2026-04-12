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
