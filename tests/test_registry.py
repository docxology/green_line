"""Registry invariants: uniqueness, vocabulary membership, digest."""

from __future__ import annotations

from green_line import GREEN_RECORDS, TAG_VOCABULARY, registry_digest, registry_ids
from green_line.model import GrowthKind


def test_registry_ids_unique() -> None:
    ids = registry_ids()
    assert len(ids) == len(set(ids))
    assert len(ids) >= 6


def test_all_tags_in_vocabulary() -> None:
    for record in GREEN_RECORDS:
        assert record.tags <= TAG_VOCABULARY, record.id


def test_all_kinds_valid() -> None:
    for record in GREEN_RECORDS:
        assert isinstance(record.kind, GrowthKind)


def test_all_families_covered() -> None:
    used = {record.kind for record in GREEN_RECORDS}
    assert used == set(GrowthKind)


def test_markers_nonempty() -> None:
    for record in GREEN_RECORDS:
        assert record.required_markers
        assert all(marker.strip() for marker in record.required_markers)


def test_digest_stable_and_order_insensitive() -> None:
    d1 = registry_digest(GREEN_RECORDS)
    d2 = registry_digest(tuple(reversed(GREEN_RECORDS)))
    assert d1 == d2
    assert len(d1) == 64
