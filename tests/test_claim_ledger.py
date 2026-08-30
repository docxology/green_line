"""Re-derive every claim_ledger.yaml row from the running package."""

from __future__ import annotations

from pathlib import Path

from green_line import GREEN_RECORDS, TAG_VOCABULARY
from green_line.intake import COUNTER_SIGNAL_PHRASES
from green_line.model import GrowthKind

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "data" / "claim_ledger.yaml"


def _numbers() -> dict[str, int]:
    """Parse the one-line ledger row format with the standard library only."""

    numbers: dict[str, int] = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("- {"):
            continue
        body = line[2:].rstrip()
        if body.endswith("}"):
            body = body[:-1]
        row: dict[str, str] = {}
        for part in body.split(", "):
            part = part.lstrip("{").strip()
            key, sep, value = part.partition(": ")
            if sep:
                row[key.strip()] = value.strip()
        if "claim_id" in row and "value" in row:
            numbers[row["claim_id"]] = int(row["value"])
    return numbers


def test_derived_rows_match_the_running_package() -> None:
    numbers = _numbers()
    expected = {
        "record-count": len(GREEN_RECORDS),
        "growth-family-count": len(GrowthKind),
        "tag-vocabulary-size": len(TAG_VOCABULARY),
        "distinct-marker-count": sum(len(r.required_markers) for r in GREEN_RECORDS),
        "applicable-tag-record-cells": sum(len(r.tags) for r in GREEN_RECORDS),
        "tag-record-cell-total": len(GREEN_RECORDS) * len(TAG_VOCABULARY),
        "counter-signal-phrase-count": len(COUNTER_SIGNAL_PHRASES),
        "figure-count": 3,
        "digest-hex-length": 64,
    }
    for claim_id, value in expected.items():
        assert numbers[claim_id] == value, claim_id


def test_per_tag_reach_and_burden() -> None:
    numbers = _numbers()
    for tag in sorted(TAG_VOCABULARY):
        applicable = [r for r in GREEN_RECORDS if tag in r.tags]
        assert numbers[f"{tag}-tag-reach"] == len(applicable), tag
        assert numbers[f"{tag}-marker-burden"] == sum(
            len(r.required_markers) for r in applicable
        ), tag


def test_every_artifact_path_exists() -> None:
    seen: set[str] = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if "artifact_path:" not in line:
            continue
        path = line.split("artifact_path:")[1].split(",")[0].strip()
        assert (ROOT / path).is_file(), path
        seen.add(path)
    assert seen, "no artifact paths; the ledger would be unanchored"
