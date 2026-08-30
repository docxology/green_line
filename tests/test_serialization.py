"""Canonical serialization and digest determinism."""

from __future__ import annotations

import json

from green_line import (
    GREEN_RECORDS,
    canonical_registry,
    registry_digest,
    read_cultivation,
    canonical_reading,
    reading_digest,
)


def test_canonical_registry_is_sorted_json() -> None:
    payload = json.loads(canonical_registry(GREEN_RECORDS))
    ids = [row["id"] for row in payload]
    assert ids == sorted(ids)


def test_canonical_registry_tags_sorted() -> None:
    payload = json.loads(canonical_registry(GREEN_RECORDS))
    for row in payload:
        assert row["tags"] == sorted(row["tags"])


def test_reading_digest_deterministic(staged_attempt) -> None:
    r1 = read_cultivation(staged_attempt, as_of="2026-08-29")
    r2 = read_cultivation(staged_attempt, as_of="2026-08-29")
    assert reading_digest(r1) == reading_digest(r2)
    assert canonical_reading(r1) == canonical_reading(r2)


def test_registry_digest_matches_canonical() -> None:
    import hashlib

    expected = hashlib.sha256(
        canonical_registry(GREEN_RECORDS).encode("utf-8")
    ).hexdigest()
    assert registry_digest(GREEN_RECORDS) == expected
