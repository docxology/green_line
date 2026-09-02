"""Evaluator behaviour: staged reads, fail-closed paths, empty outcomes."""

from __future__ import annotations


import pytest

from green_line import (
    GREEN_RECORDS,
    CultivationAttempt,
    GrowthStatus,
    Observation,
    SignalStatus,
    registry_digest,
    read_cultivation,
    read_with_surfaces,
)


def test_staged_when_all_markers_fresh(staged_attempt) -> None:
    reading = read_cultivation(
        staged_attempt, as_of="2026-08-29", max_observation_age_days=60
    )
    # several applied records lack markers entirely, so rework outranks refresh
    assert reading.status is GrowthStatus.NEEDS_REWORK
    statuses = {f.status for f in reading.findings}
    assert SignalStatus.STAGED in statuses


def test_apprentice_review_finding_is_staged(staged_attempt) -> None:
    reading = read_cultivation(staged_attempt, as_of="2026-08-29")
    finding = next(f for f in reading.findings if f.record_id == "apprentice-review")
    assert finding.status is SignalStatus.STAGED


def test_outside_scope_when_no_tags_match() -> None:
    reading = read_cultivation(
        CultivationAttempt(description="unrelated", tags=frozenset({"farming"})),
        as_of="2026-08-29",
    )
    assert reading.status is GrowthStatus.OUTSIDE_SCOPE
    assert reading.findings == ()


def test_empty_scan_set_is_outcome_not_exception() -> None:
    reading = read_cultivation(
        CultivationAttempt(description="nothing declared"), as_of="2026-08-29"
    )
    assert reading.status is GrowthStatus.OUTSIDE_SCOPE


def test_blank_description_fails_closed(staged_attempt) -> None:
    attempt = CultivationAttempt(description="   ", tags=staged_attempt.tags)
    reading = read_cultivation(attempt, as_of="2026-08-29")
    assert reading.status is GrowthStatus.NEEDS_REWORK
    assert reading.findings == ()
    assert any("description" in note for note in reading.intake_notes)


def test_malformed_registry_fails_closed() -> None:
    bad = (
        GREEN_RECORDS[0],
        GREEN_RECORDS[0],
    )
    reading = read_cultivation(
        CultivationAttempt(description="x", tags=frozenset({"research"})),
        records=bad,
        as_of="2026-08-29",
    )
    assert reading.status is GrowthStatus.NEEDS_REWORK
    assert reading.findings == ()
    assert any("duplicate" in note for note in reading.intake_notes)


def test_non_record_registry_entry_fails_closed() -> None:
    reading = read_cultivation(
        CultivationAttempt(description="x", tags=frozenset({"research"})),
        records=("not a record",),  # type: ignore[list-item]
        as_of="2026-08-29",
    )
    assert reading.status is GrowthStatus.NEEDS_REWORK


def test_invalid_as_of_raises() -> None:
    with pytest.raises(ValueError):
        read_cultivation(
            CultivationAttempt(description="x"), as_of="not-a-date"
        )
    with pytest.raises(TypeError):
        read_cultivation(
            CultivationAttempt(description="x"), as_of=20260829  # type: ignore[arg-type]
        )


def test_invalid_max_age_raises() -> None:
    with pytest.raises(TypeError):
        read_cultivation(
            CultivationAttempt(description="x"), max_observation_age_days="60"  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError):
        read_cultivation(
            CultivationAttempt(description="x"), max_observation_age_days=-1
        )
    with pytest.raises(TypeError):
        read_cultivation(
            CultivationAttempt(description="x"), max_observation_age_days=True
        )


def test_stale_only_gap_is_needs_marker(staged_attempt) -> None:
    reading = read_cultivation(
        staged_attempt, as_of="2026-08-29", max_observation_age_days=0
    )
    assert any(
        "stale markers need refresh" in reason
        for f in reading.findings
        for reason in f.reasons
    )
    statuses = {f.status for f in reading.findings}
    assert SignalStatus.NEEDS_MARKER in statuses


def test_surfaces_align_with_findings(staged_attempt) -> None:
    reading, surfaces = read_with_surfaces(staged_attempt, as_of="2026-08-29")
    assert len(reading.findings) == len(surfaces)
    for finding, surface in zip(reading.findings, surfaces):
        assert finding.record_id == surface.record_id


def test_registry_digest_pinned(staged_attempt) -> None:
    reading = read_cultivation(staged_attempt, as_of="2026-08-29")
    assert reading.registry_digest == registry_digest(GREEN_RECORDS)
    assert len(reading.registry_digest) == 64


def test_future_dated_observation_not_counted() -> None:
    attempt = CultivationAttempt(
        description="future dated",
        tags=frozenset({"research"}),
        dated_observations=(Observation("mentor", "2099-01-01"),),
    )
    reading = read_cultivation(attempt, as_of="2026-08-29")
    assert any("future" in note for note in reading.intake_notes)


def test_unreadable_date_not_counted() -> None:
    attempt = CultivationAttempt(
        description="bad date",
        tags=frozenset({"research"}),
        dated_observations=(Observation("mentor", "yesterday"),),
    )
    reading = read_cultivation(attempt, as_of="2026-08-29")
    assert any("unreadable date" in note for note in reading.intake_notes)


def test_malformed_tag_collection_set_aside() -> None:
    attempt = CultivationAttempt(description="x")
    object.__setattr__(attempt, "tags", "research")  # a string, not a collection
    reading = read_cultivation(attempt, as_of="2026-08-29")
    assert any("not a collection" in note for note in reading.intake_notes)
    assert reading.status is GrowthStatus.OUTSIDE_SCOPE


def test_dated_evidence_not_a_collection() -> None:
    reading = read_cultivation(
        CultivationAttempt(description="x", tags=frozenset({"research"})),
        as_of="2026-08-29",
    )
    assert reading.status in (
        GrowthStatus.NEEDS_MARKER,
        GrowthStatus.OUTSIDE_SCOPE,
        GrowthStatus.NEEDS_REWORK,
    )


def test_non_iterable_records_fail_closed() -> None:
    with pytest.raises(TypeError, match="records must be an iterable"):
        read_cultivation(
            CultivationAttempt(description="x", tags=frozenset({"research"})),
            42,  # type: ignore[arg-type]
            as_of="2026-08-29",
        )


def test_registry_digest_failure_fails_closed_with_note() -> None:
    from green_line import GreenRecord

    class _HostileRecord(GreenRecord):
        """Shape-valid, but canonicalization always raises ValueError."""

        def canonical(self) -> dict[str, object]:
            raise ValueError("hostile canonicalization")

    hostile = _HostileRecord(
        "hostile", "t", "w", frozenset({"research"}), ("m",)
    )
    reading = read_cultivation(
        CultivationAttempt(description="x", tags=frozenset({"research"})),
        (hostile,),
        as_of="2026-08-29",
    )
    assert reading.status is GrowthStatus.NEEDS_REWORK
    assert reading.findings == ()
    assert any("could not be digested" in note for note in reading.intake_notes)


def test_present_markers_reason_lists_partially_covered() -> None:
    # apprentice-review needs (mentor, session_log); one fresh marker only
    reading = read_cultivation(
        CultivationAttempt(
            description="partial coverage",
            tags=frozenset({"research"}),
            dated_observations=(Observation("mentor", "2026-08-20"),),
        ),
        as_of="2026-08-29",
    )
    apprentice = next(
        f for f in reading.findings if f.record_id == "apprentice-review"
    )
    assert apprentice.status is SignalStatus.NEEDS_REWORK
    assert any(
        reason.startswith("markers already present: mentor")
        for reason in apprentice.reasons
    )
