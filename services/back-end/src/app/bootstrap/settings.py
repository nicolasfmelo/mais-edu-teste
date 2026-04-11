from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


@dataclass(frozen=True)
class AppSettings:
    database_url: str
    datasets_dir: Path
    indexing_bootstrap_enabled: bool
    llm_proxy_base_url: str | None

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
        )
