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


@dataclass(frozen=True)
class AppSettings:
    database_url: str
    datasets_dir: Path
    indexing_bootstrap_enabled: bool
    llm_proxy_base_url: str | None
    assistant_model_allowlist: tuple[str, ...] = field(default_factory=_default_assistant_model_allowlist)
    institution_profile_path: Path = field(default_factory=_default_institution_profile_path)
    cors_allowed_origins: tuple[str, ...] = field(
        default=("http://0.0.0.0:5173", "http://localhost:5173")
    )

    @classmethod
    def from_env(cls) -> "AppSettings":
        repo_root = Path(__file__).resolve().parents[5]
        datasets_dir = Path(os.getenv("DATASETS_DIR", str(repo_root / "services" / "datasets"))).expanduser()
        default_database_path = repo_root / "services" / "back-end" / ".mais_a_educ.db"
        return cls(
            database_url=os.getenv("DATABASE_URL", f"sqlite+pysqlite:///{default_database_path}"),
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
                default=("http://0.0.0.0:5173", "http://localhost:5173"),
            ),
        )
