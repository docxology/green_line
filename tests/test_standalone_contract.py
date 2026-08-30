"""Standalone contract: no sibling import anywhere in this repo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SIBLING_PACKAGES = (
    "black_line",
    "golden_line",
    "white_line",
    "red_line",
    "line_set",
    "witness_register",
)


def test_no_sibling_imports_in_code() -> None:
    offenders: list[str] = []
    for tree in ("src", "tests", "scripts"):
        for path in (ROOT / tree).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for sibling in SIBLING_PACKAGES:
                if f"import {sibling}" in text or f"from {sibling}" in text:
                    offenders.append(f"{path}: {sibling}")
    assert not offenders, offenders


def test_runtime_dependencies_empty() -> None:
    import tomllib

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["dependencies"] == []
    dev = pyproject["dependency-groups"]["dev"]
    joined = " ".join(dev)
    for allowed in ("pytest", "pytest-cov", "ruff"):
        assert allowed in joined
    assert len(dev) == 3
