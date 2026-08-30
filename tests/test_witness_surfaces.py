"""Validate shipped envelopes against the register's field structure.

The schema reference is a frozen copy of the sibling envelope field set. If
the witness_register checkout is present its worked envelope is parsed
read-only as an additional check; its absence is an outcome, not a failure.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENVELOPES = ROOT / "data" / "envelopes"

#: Frozen copy of the sibling worked-envelope field set
#: (witness_register/data/envelopes/black_line_worked.json).
FROZEN_ENVELOPE_FIELDS = frozenset(
    {
        "line_id",
        "native_status",
        "registry_digest",
        "registry_version",
        "report_ref",
        "review_date",
        "schema_version",
        "scope_and_nonclaims",
        "source_snapshot_refs",
        "subject_id",
    }
)


def _load(name: str) -> dict:
    return json.loads((ENVELOPES / name).read_text(encoding="utf-8"))


def test_worked_envelope_field_structure() -> None:
    payload = _load("green_line_worked.json")
    assert frozenset(payload) == FROZEN_ENVELOPE_FIELDS
    assert payload["line_id"] == "green_line"
    assert payload["schema_version"] == "line.report-envelope/1.0"
    assert payload["registry_version"] == "0.1.0"
    assert len(payload["report_ref"]) == 64
    assert payload["native_status"] in {
        "STAGED",
        "NEEDS_MARKER",
        "NEEDS_REWORK",
        "OUTSIDE_SCOPE",
    }


def test_same_subject_envelope_field_structure() -> None:
    payload = _load("green_line_same_subject.json")
    assert frozenset(payload) == FROZEN_ENVELOPE_FIELDS
    assert payload["line_id"] == "green_line"
    assert payload["review_date"] == "2026-07-29"
    assert payload["subject_id"].startswith("witness_register 0.1.0")


def test_envelopes_are_canonical_json() -> None:
    for name in ("green_line_worked.json", "green_line_same_subject.json"):
        raw = (ENVELOPES / name).read_text(encoding="utf-8")
        payload = json.loads(raw)
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        assert raw.strip() == canonical, name


def test_sibling_envelope_parsed_when_present(witness_root: Path) -> None:
    """Read-only sibling check; absence is an outcome, not a failure."""

    if not witness_root.is_dir():
        return  # NOT_INSTALLED: the contract outcome
    sibling = witness_root / "black_line_worked.json"
    if sibling.is_file():
        payload = json.loads(sibling.read_text(encoding="utf-8"))
        assert frozenset(payload) == FROZEN_ENVELOPE_FIELDS
