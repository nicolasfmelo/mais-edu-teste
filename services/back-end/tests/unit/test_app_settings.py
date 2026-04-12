from pathlib import Path

import pytest

from app.bootstrap.settings import AppSettings


def test_from_env_requires_database_url() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(AssertionError, match="DATABASE_URL must be set"):
            AppSettings.from_env()


def test_from_env_requires_postgres_database_url() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:////tmp/test.db")

        with pytest.raises(AssertionError, match="PostgreSQL"):
            AppSettings.from_env()


def test_from_env_accepts_postgres_database_url() -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mais_a_educ")

        settings = AppSettings.from_env()

    assert settings.database_url == "postgresql://postgres:postgres@localhost:5432/mais_a_educ"
    assert settings.datasets_dir == Path(__file__).resolve().parents[4] / "services" / "datasets"
