"""Envelope export and read-back verification."""

from __future__ import annotations

import json

import pytest

from green_line import (
    ENVELOPE_SCHEMA,
    GREEN_LINE_ID,
    SCOPE_AND_NONCLAIMS,
    CultivationAttempt,
    canonical_envelope,
    envelope_matches_reading,
    read_cultivation,
    reading_envelope,
    reading_digest,
)


def _reading(staged_attempt):
    return read_cultivation(staged_attempt, as_of="2026-08-29")


def test_envelope_roundtrip(staged_attempt) -> None:
    reading = _reading(staged_attempt)
    envelope = reading_envelope(reading, subject_id="test subject")
    payload = json.loads(canonical_envelope(envelope))
    assert payload["schema_version"] == ENVELOPE_SCHEMA
    assert payload["line_id"] == GREEN_LINE_ID
    assert payload["native_status"] == reading.status.value
    assert payload["report_ref"] == reading_digest(reading)
    assert payload["registry_digest"] == reading.registry_digest
    assert payload["scope_and_nonclaims"] == list(SCOPE_AND_NONCLAIMS)


def test_envelope_matches_reading(staged_attempt) -> None:
    reading = _reading(staged_attempt)
    envelope = reading_envelope(reading, subject_id="s")
    assert envelope_matches_reading(envelope, reading)


def test_envelope_mismatch_detected(staged_attempt) -> None:
    reading = _reading(staged_attempt)
    envelope = reading_envelope(reading, subject_id="s")
    other = read_cultivation(
        CultivationAttempt(description="different", tags=frozenset({"data"})),
        as_of="2026-08-29",
    )
    assert not envelope_matches_reading(envelope, other)


def test_envelope_rejects_bad_refs(staged_attempt) -> None:
    reading = _reading(staged_attempt)
    with pytest.raises(ValueError):
        reading_envelope(reading, source_snapshot_refs=["", " "])
    with pytest.raises(TypeError):
        reading_envelope(reading, subject_id=42)  # type: ignore[arg-type]
