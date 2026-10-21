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
import json
from dataclasses import replace

from .intake import (
    clean_labels,
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
from .registry import TAG_VOCABULARY
from .serialization import canonical_registry, registry_digest
from .records import EvaluationContext, MarkerEvidence
from .evidence import POLICY_VERSION, content_digest, observation_dispositions, policy_digest, snapshot_input
from .version import __version__


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
    registry_vocabulary: frozenset[str] = TAG_VOCABULARY,
    instrument_id: str = "green_line",
    normalized_input: str | None = None,
    episode_policy: str = "combine_declared",
    undated_policy: str = "current",
) -> tuple[GreenReading, tuple[MarkerSurfaces, ...]]:
    """Run the staged read once, returning the reading and surfaces."""

    read_date = resolve_read_date(as_of)
    max_age_days = resolve_max_age(max_observation_age_days)
    if not isinstance(instrument_id, str) or not instrument_id.strip():
        raise ValueError("instrument_id must be nonblank")
    if registry_vocabulary != TAG_VOCABULARY and instrument_id == "green_line":
        raise ValueError("a different vocabulary requires an explicit instrument_id")
    if episode_policy not in ("combine_declared", "single_episode"):
        raise ValueError("unsupported episode_policy")
    if undated_policy not in ("current", "dated_only"):
        raise ValueError("unsupported undated_policy")
    snapshot = normalized_input if normalized_input is not None else snapshot_input(attempt)
    inputs = json.loads(snapshot)
    context = EvaluationContext(max_age_days, __version__, POLICY_VERSION, policy_digest(),
                                content_digest(snapshot), instrument_id,
                                tuple(sorted(registry_vocabulary)), episode_policy, undated_policy)
    try:
        record_set = tuple(records)
    except TypeError as exc:
        raise TypeError(
            "records must be an iterable of GreenRecord records"
        ) from exc
    notes: list[str] = []
    if inputs.get("next_review") == {"malformed": True}:
        notes.append("malformed next_review was set aside; it cannot change marker coverage")
    shape_error = registry_shape_error(record_set, registry_vocabulary)
    registry_snapshot = ""
    if shape_error:
        method_digest = ""
        notes.append(
            f"record registry is not safe to score and must be repaired: {shape_error}"
        )
    else:
        try:
            method_digest = registry_digest(record_set)
            registry_snapshot = canonical_registry(record_set)
            record_set = tuple(sorted(record_set, key=lambda record: record.id))
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
                context, snapshot, registry_snapshot, scope_reason="INVALID_REGISTRY",
            ),
            (),
        )
    blocking = not inputs["description_valid"]
    if blocking:
        notes.append(
            "cultivation description is empty or not text; restate it before reading"
        )
    tags, tag_notes = clean_labels(inputs["tags"], "tag")
    notes.extend(tag_notes)
    dispositions = observation_dispositions(inputs, read_date, max_age_days,
                                            frozenset(m for r in record_set for m in r.required_markers))
    if undated_policy == "dated_only":
        dispositions = tuple(replace(d, disposition="excluded", reason_code="UNDATED_PROFILE",
                                     note="undated declaration was set aside under dated_only")
                             if d.disposition == "accepted" and d.noted_on is None else d
                             for d in dispositions)
    if episode_policy == "single_episode":
        episodes = {d.episode_id for d in dispositions if d.disposition in ("accepted", "stale")}
        if len(episodes) > 1:
            dispositions = tuple(replace(d, disposition="excluded", reason_code="EPISODE_CONFLICT",
                                         note="multiple declared episodes cannot be combined under single_episode")
                                 if d.disposition in ("accepted", "stale") else d for d in dispositions)
    notes.extend(d.note for d in dispositions if d.note)
    if blocking:
        return (
            GreenReading(
                GrowthStatus.NEEDS_REWORK,
                (),
                tuple(notes),
                read_date.isoformat(),
                method_digest,
                context, snapshot, registry_snapshot, dispositions,
                scope_reason="INVALID_DESCRIPTION",
            ),
            (),
        )
    fresh = frozenset(d.label for d in dispositions if d.disposition == "accepted" and d.label is not None)
    stale = frozenset(d.label for d in dispositions if d.disposition == "stale" and d.label is not None)
    observations_declared = bool(fresh or stale)
    surfaces = tuple(
        _surfaces(record, fresh, stale)
        for record in record_set
        if record.tags & tags
    )
    findings = tuple(replace(_finding(item, observations_declared), declaration_relevance=(
        "FRESH_REQUIRED" if item.present else "STALE_REQUIRED" if item.stale
        else "UNRELATED_ONLY" if observations_declared else "NO_COUNTED_DECLARATIONS"))
        for item in surfaces)
    evidence = tuple(MarkerEvidence(s.record_id, label,
                                   "present" if label in s.present else "stale" if label in s.stale else "missing",
                                   tuple(d for d in dispositions if d.label == label))
                     for s in surfaces for label in (*s.present, *s.missing))
    scope = ("EMPTY_REGISTRY" if not record_set else "MALFORMED_TAGS" if tag_notes
             else "NO_TAGS" if not tags else "APPLIED" if findings else "UNMATCHED_TAGS")
    return (
        GreenReading(
            _overall(findings),
            findings,
            tuple(notes),
            read_date.isoformat(),
            method_digest,
            context, snapshot, registry_snapshot, dispositions, surfaces, evidence, scope,
        ),
        surfaces,
    )


def read_cultivation(
    attempt: CultivationAttempt,
    records: Iterable[GreenRecord] = GREEN_RECORDS,
    *,
    as_of: str | date | None = None,
    max_observation_age_days: int | None = None,
    registry_vocabulary: frozenset[str] = TAG_VOCABULARY,
    instrument_id: str = "green_line",
    episode_policy: str = "combine_declared",
    undated_policy: str = "current",
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

    reading, _surfaces_unused = _read(attempt, records, as_of, max_observation_age_days,
                                     registry_vocabulary, instrument_id, episode_policy=episode_policy,
                                     undated_policy=undated_policy)
    return reading


def read_with_surfaces(
    attempt: CultivationAttempt,
    records: Iterable[GreenRecord] = GREEN_RECORDS,
    *,
    as_of: str | date | None = None,
    max_observation_age_days: int | None = None,
    registry_vocabulary: frozenset[str] = TAG_VOCABULARY,
    instrument_id: str = "green_line",
    episode_policy: str = "combine_declared",
    undated_policy: str = "current",
) -> tuple[GreenReading, tuple[MarkerSurfaces, ...]]:
    """Read the attempt and also return each finding's typed surfaces.

    The reading is exactly what ``read_cultivation`` returns for the same
    arguments — one shared staged implementation. The surfaces align
    one-to-one with ``reading.findings`` and preserve what each status
    projection compresses: the record's present, missing, and stale required
    markers as co-present typed data. Like the finding, they describe
    declaration coverage only — never quality, mastery, or certification.
    """

    return _read(attempt, records, as_of, max_observation_age_days,
                 registry_vocabulary, instrument_id, episode_policy=episode_policy,
                 undated_policy=undated_policy)
