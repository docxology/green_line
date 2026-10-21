"""Standalone contract: no sibling import anywhere in this repo."""

from __future__ import annotations

from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent.parent

SIBLING_PACKAGES = (
    "black_line",
    "golden_line",
    "white_line",
    "red_line",
    "line_set",
    "witness_register",
    "silver_line",
    "violet_line",
    "blue_line",
)


def sibling_imports(source: str) -> set[str]:
    modules = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(item.name.split(".")[0] for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".")[0])
    return modules & set(SIBLING_PACKAGES)


def test_no_sibling_imports_in_code() -> None:
    offenders: list[str] = []
    for tree in ("src", "tests", "scripts"):
        for path in (ROOT / tree).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            offenders.extend(f"{path}: {name}" for name in sorted(sibling_imports(text)))
    assert not offenders, offenders


def test_import_policy_rejects_aliases_and_multiple_imports():
    for name in SIBLING_PACKAGES:
        assert sibling_imports(f"import os, {name}.module as alias") == {name}
        assert sibling_imports(f"from {name}.module import item") == {name}
        assert not sibling_imports(f"# import {name}\nvalue = 'import {name}'")


def test_runtime_source_uses_python310_syntax():
    paths = sorted((ROOT / "src").rglob("*.py"))
    assert paths
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 10))


def test_runtime_dependencies_empty() -> None:
    import tomllib

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["dependencies"] == []
    dev = pyproject["dependency-groups"]["dev"]
    joined = " ".join(dev)
    for allowed in ("pytest", "pytest-cov", "ruff"):
        assert allowed in joined
    assert len(dev) == 3
