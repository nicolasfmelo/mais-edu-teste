from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        normalized_key = key.strip()
        normalized_value = value.strip().strip('"').strip("'")
        if normalized_key:
            os.environ.setdefault(normalized_key, normalized_value)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sobe o backend Mais A Educ localmente com uvicorn.")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))  # nosec B104 - local dev runner
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    parser.add_argument(
        "--reload",
        action=argparse.BooleanOptionalAction,
        default=_as_bool(os.getenv("RELOAD"), default=True),
        help="Liga ou desliga o auto-reload do uvicorn.",
    )
    return parser


def main() -> None:
    backend_root = Path(__file__).resolve().parent
    src_dir = backend_root / "src"

    _load_env_file(backend_root / ".env")

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    args = _build_parser().parse_args()
    uvicorn.run(
        "app.main:create_application",
        host=args.host,
        port=args.port,
        factory=True,
        reload=args.reload,
        reload_dirs=[str(src_dir)],
    )


if __name__ == "__main__":
    main()
