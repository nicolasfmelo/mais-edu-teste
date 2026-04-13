from __future__ import annotations

import ast
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[2] / "src" / "app"


def test_engines_do_not_import_upper_layers() -> None:
    violations = _collect_layer_violations(
        layer="engines",
        forbidden_prefixes=("app.services", "app.integrations", "app.delivery"),
    )

    assert violations == []


def test_integrations_do_not_import_engines_outside_langgraph_adapter() -> None:
    violations = _collect_layer_violations(
        layer="integrations",
        forbidden_prefixes=("app.engines",),
        allowed_prefixes=("app.integrations.langgraph",),
    )

    assert violations == []


def test_services_do_not_import_delivery_or_concrete_integrations() -> None:
    violations = _collect_layer_violations(
        layer="services",
        forbidden_prefixes=("app.delivery", "app.integrations.database.models", "app.integrations.object_store"),
        allowed_prefixes=("app.integrations.langgraph",),
    )

    assert violations == []


def _collect_layer_violations(
    *,
    layer: str,
    forbidden_prefixes: tuple[str, ...],
    allowed_prefixes: tuple[str, ...] = (),
) -> list[str]:
    violations: list[str] = []
    layer_root = APP_ROOT / layer
    for file_path in sorted(layer_root.rglob("*.py")):
        module_imports = _extract_imports(file_path)
        for module_name in module_imports:
            if any(module_name.startswith(prefix) for prefix in allowed_prefixes):
                continue
            if any(module_name.startswith(prefix) for prefix in forbidden_prefixes):
                violations.append(f"{file_path.relative_to(APP_ROOT)} -> {module_name}")
    return violations


def _extract_imports(file_path: Path) -> tuple[str, ...]:
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return tuple(imports)
