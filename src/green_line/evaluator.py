"""Staged evaluation of capacity-under-development evidence.

Evaluation is deliberately staged: intake normalization runs first, so
hostile or malformed input (non-string labels, unreadable dates, a blank
description, counter-signals phrased as certification) is recorded in
``intake_notes`` instead of crashing or silently passing. Only then are
records matched by tag and scored against the fresh observation set. The
output describes marker coverage and review gaps; it never turns labels into
competence, a certification, or permission for anything.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from .intake import (
    clean_labels,
    dated_labels,
    registry_shape_error,
    resolve_max_age,
    resolve_read_date,
)
from .model import (
    CultivationAttempt,
    GreenRecord,
    GreenReading,
    GrowthStatus,
    MarkerSurfaces,
    RecordFinding,
    SignalStatus,
)
from .registry import GREEN_RECORDS
from .serialization import registry_digest


def _surfaces(
    record: GreenRecord,
    fresh: frozenset[str],
    stale: frozenset[str],
) -> MarkerSurfaces:
    """Split one record's required labels into typed co-present surfaces."""

    present = tuple(item for item in record.required_markers if item in fresh)
    missing = tuple(item for item in record.required_markers if item not in fresh)
    stale_missing = tuple(item for item in missing if item in stale)
    return MarkerSurfaces(record.id, present, missing, stale_missing)


def _finding(
    surfaces: MarkerSurfaces,
    observations_declared: bool,
) -> RecordFinding:
    """Project one record's surfaces onto a status with a reasons trail."""

    if not observations_declared:
        return RecordFinding(
            surfaces.record_id,
            SignalStatus.NEEDS_MARKER,
            ("no observations were declared",),
        )
    if not surfaces.missing:
        return RecordFinding(
            surfaces.record_id,
            SignalStatus.STAGED,
            ("required markers are present: " + ", ".join(surfaces.present),),
        )
    reasons = ["required markers are missing: " + ", ".join(surfaces.missing)]
    if surfaces.present:
        reasons.append("markers already present: " + ", ".join(surfaces.present))
    if surfaces.stale:
        reasons.append("stale markers need refresh: " + ", ".join(surfaces.stale))
    status = (
        SignalStatus.NEEDS_MARKER
        if len(surfaces.stale) == len(surfaces.missing)
        else SignalStatus.NEEDS_REWORK
    )
    return RecordFinding(surfaces.record_id, status, tuple(reasons))


def _overall(findings: tuple[RecordFinding, ...]) -> GrowthStatus:
    statuses = {finding.status for finding in findings}
    if SignalStatus.NEEDS_REWORK in statuses:
        return GrowthStatus.NEEDS_REWORK
    if SignalStatus.NEEDS_MARKER in statuses:
        return GrowthStatus.NEEDS_MARKER
    return GrowthStatus.STAGED if findings else GrowthStatus.OUTSIDE_SCOPE


def _read(
    attempt: CultivationAttempt,
    records: Iterable[GreenRecord],
    as_of: str | date | None,
    max_observation_age_days: int | None,
) -> tuple[GreenReading, tuple[MarkerSurfaces, ...]]:
    """Run the staged read once, returning the reading and surfaces."""

    read_date = resolve_read_date(as_of)
    max_age_days = resolve_max_age(max_observation_age_days)
    try:
        record_set = tuple(records)
    except TypeError as exc:
        raise TypeError(
            "records must be an iterable of GreenRecord records"
        ) from exc
    notes: list[str] = []
    shape_error = registry_shape_error(record_set)
    if shape_error:
        method_digest = ""
        notes.append(
            f"record registry is not safe to score and must be repaired: {shape_error}"
        )
    else:
        try:
            method_digest = registry_digest(record_set)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            method_digest = ""
            notes.append(
                f"record registry could not be digested and must be repaired: {exc}"
            )
    if not method_digest:
        return (
            GreenReading(
                GrowthStatus.NEEDS_REWORK,
                (),
                tuple(notes),
                read_date.isoformat(),
                method_digest,
            ),
            (),
        )
    description = getattr(attempt, "description", None)
    blocking = not isinstance(description, str) or not description.strip()
    if blocking:
        notes.append(
            "cultivation description is empty or not text; restate it before reading"
        )
    tags, tag_notes = clean_labels(getattr(attempt, "tags", None), "tag")
    notes.extend(tag_notes)
    declared, observation_notes = clean_labels(
        getattr(attempt, "observations", None), "observation"
    )
    notes.extend(observation_notes)
    fresh_dated, stale, dated_notes = dated_labels(
        getattr(attempt, "dated_observations", ()), read_date, max_age_days
    )
    notes.extend(dated_notes)
    if blocking:
        return (
            GreenReading(
                GrowthStatus.NEEDS_REWORK,
                (),
                tuple(notes),
                read_date.isoformat(),
                method_digest,
            ),
            (),
        )
    fresh = declared | fresh_dated
    observations_declared = bool(fresh or stale)
    surfaces = tuple(
        _surfaces(record, fresh, stale)
        for record in record_set
        if record.tags & tags
    )
    findings = tuple(_finding(item, observations_declared) for item in surfaces)
    return (
        GreenReading(
            _overall(findings),
            findings,
            tuple(notes),
            read_date.isoformat(),
            method_digest,
        ),
        surfaces,
    )


def read_cultivation(
    attempt: CultivationAttempt,
    records: Iterable[GreenRecord] = GREEN_RECORDS,
    *,
    as_of: str | date | None = None,
    max_observation_age_days: int | None = None,
) -> GreenReading:
    """Read growth records whose tags intersect the attempt's declared tags.

    - ``as_of`` pins the review date (ISO string or :class:`datetime.date`);
      the default is today.
    - ``max_observation_age_days`` enables staleness: dated observations
      older than the window stop counting as fresh, and a finding whose only
      gaps are stale items is ``NEEDS_MARKER`` (refresh), not ``NEEDS_REWORK``.
    - Invalid review configuration raises before scoring. A custom registry
      with malformed records fails closed as ``NEEDS_REWORK`` with no
      findings and an intake note.
    - A blank or non-text description is a blocking intake defect: the
      reading is ``NEEDS_REWORK`` with no findings and an explanatory note.
    - An empty scan set (no record tags intersect the attempt's tags) is the
      outcome ``OUTSIDE_SCOPE``, not an exception.
    """

    reading, _surfaces_unused = _read(attempt, records, as_of, max_observation_age_days)
    return reading


def read_with_surfaces(
    attempt: CultivationAttempt,
    records: Iterable[GreenRecord] = GREEN_RECORDS,
    *,
    as_of: str | date | None = None,
    max_observation_age_days: int | None = None,
) -> tuple[GreenReading, tuple[MarkerSurfaces, ...]]:
    """Read the attempt and also return each finding's typed surfaces.

    The reading is exactly what ``read_cultivation`` returns for the same
    arguments — one shared staged implementation. The surfaces align
    one-to-one with ``reading.findings`` and preserve what each status
    projection compresses: the record's present, missing, and stale required
    markers as co-present typed data. Like the finding, they describe
    declaration coverage only — never quality, mastery, or certification.
    """

    return _read(attempt, records, as_of, max_observation_age_days)
