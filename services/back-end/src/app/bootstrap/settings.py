from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _as_tuple(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    return items or default


def _default_institution_profile_path() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "services" / "back-end" / "institution-profile.md"


def _default_assistant_model_allowlist() -> tuple[str, ...]:
    return (
        "us.anthropic.claude-sonnet-4-6",
        "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "minimax.minimax-m2.5",
        "us.amazon.nova-2-lite-v1:0",
    )


def _require_postgres_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    assert database_url, "DATABASE_URL must be set to a PostgreSQL connection string."
    assert database_url.startswith(("postgresql://", "postgresql+")), (
        "DATABASE_URL must use a PostgreSQL connection string."
    )
    return database_url


def _require_minio_credentials() -> tuple[str, str]:
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    assert access_key, "MINIO_ACCESS_KEY must be set."
    assert secret_key, "MINIO_SECRET_KEY must be set."
    return access_key, secret_key


@dataclass(frozen=True)
class AppSettings:
    database_url: str
    datasets_dir: Path
    indexing_bootstrap_enabled: bool
    llm_proxy_base_url: str | None
    minio_access_key: str
    minio_secret_key: str
    assistant_model_allowlist: tuple[str, ...] = field(default_factory=_default_assistant_model_allowlist)
    institution_profile_path: Path = field(default_factory=_default_institution_profile_path)
    cors_allowed_origins: tuple[str, ...] = field(
        default=("http://0.0.0.0:5173", "http://localhost:5173", "http://0.0.0.0:5174", "http://localhost:5174")
    )
    minio_endpoint: str = "localhost:9000"
    minio_export_bucket: str = "conversations"

    @classmethod
    def from_env(cls) -> "AppSettings":
        repo_root = Path(__file__).resolve().parents[5]
        datasets_dir = Path(os.getenv("DATASETS_DIR", str(repo_root / "services" / "datasets"))).expanduser()
        minio_access_key, minio_secret_key = _require_minio_credentials()
        return cls(
            database_url=_require_postgres_database_url(),
            datasets_dir=datasets_dir,
            indexing_bootstrap_enabled=_as_bool(os.getenv("INDEXING_BOOTSTRAP_ENABLED"), default=True),
            llm_proxy_base_url=os.getenv(
                "LLM_PROXY_BASE_URL",
                "https://kviwmiapph.execute-api.us-east-1.amazonaws.com",
            ),
            assistant_model_allowlist=_as_tuple(
                os.getenv("ASSISTANT_MODEL_ALLOWLIST"),
                default=_default_assistant_model_allowlist(),
            ),
            institution_profile_path=Path(
                os.getenv(
                    "INSTITUTION_PROFILE_PATH",
                    str(repo_root / "services" / "back-end" / "institution-profile.md"),
                )
            ).expanduser(),
            cors_allowed_origins=_as_tuple(
                os.getenv("CORS_ALLOWED_ORIGINS"),
                default=("http://0.0.0.0:5173", "http://localhost:5173", "http://0.0.0.0:5174", "http://localhost:5174"),
            ),
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            minio_access_key=minio_access_key,
            minio_secret_key=minio_secret_key,
            minio_export_bucket=os.getenv("MINIO_EXPORT_BUCKET", "conversations"),
        )
