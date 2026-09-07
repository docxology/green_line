"""Thin CLIs behave: no arguments accepted, real subprocess execution."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_build_figures_cli_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_figures.py"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={
            "PYTHONPATH": str(ROOT / "src"),
            # rsvg-convert (cover rasterization) must be reachable on PATH.
            "PATH": os.environ["PATH"],
        },
    )
    assert result.returncode == 0, result.stderr
    assert "5 figures" in result.stdout


def test_build_figures_cli_rejects_arguments() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_figures.py", "extra"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
    )
    assert result.returncode == 2


def test_gen_binding_cli_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/gen_binding.py"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
    )
    assert result.returncode == 0, result.stderr


def test_gen_formalism_ledger_cli_rejects_arguments() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/gen_formalism_ledger.py", "extra"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
    )
    assert result.returncode == 2
