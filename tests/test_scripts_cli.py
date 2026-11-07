"""Thin CLIs reject unintended launches without changing repository data."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_build_figures_cli_rejects_arguments() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_figures.py", "extra"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
    )
    assert result.returncode == 2


def test_gen_formalism_ledger_cli_rejects_arguments() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/gen_formalism_ledger.py", "extra"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
    )
    assert result.returncode == 2


@pytest.mark.parametrize("missing", ("both", "output-dir", "source-commit"))
def test_gen_envelopes_requires_explicit_destination_and_producer(tmp_path, missing):
    destination = tmp_path / "edition"
    args = []
    if missing not in ("both", "output-dir"):
        args.extend(("--output-dir", str(destination)))
    if missing not in ("both", "source-commit"):
        args.extend(("--source-commit", "a" * 40))
    result = subprocess.run(
        [sys.executable, "scripts/gen_envelopes.py", *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 2
    assert not destination.exists()
