"""Shared fixtures: no mocks, only real data and real temp dirs."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from green_line import (  # noqa: E402
    CultivationAttempt,
    GreenRecord,
    GrowthKind,
    Observation,
)

from green_line.model import GrowthStatus  # noqa: E402


@pytest.fixture
def staged_attempt() -> CultivationAttempt:
    """An attempt whose declared markers fully cover one record."""

    return CultivationAttempt(
        description="Practising proof review with a named mentor",
        tags=frozenset({"research", "teaching"}),
        dated_observations=(
            Observation("mentor", "2026-08-15"),
            Observation("session_log", "2026-08-20"),
        ),
    )


@pytest.fixture
def witness_root() -> Path:
    """The witness_register checkout, when present; absence is an outcome."""

    sibling = ROOT.parent / "witness_register" / "data" / "envelopes"
    return sibling


__all__ = ["CultivationAttempt", "GreenRecord", "GrowthKind", "GrowthStatus", "Observation"]
