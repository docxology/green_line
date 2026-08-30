"""Fail-closed staged intake for Green Line readings.

Intake is deliberately the first stage: hostile or malformed input (blank
descriptions, non-string tags, unreadable dates, counter-signals phrased as
certification) is recorded as set-aside notes instead of crashing or being
invented into values. An empty or unscorable input set is an outcome, never
an exception.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime

from .model import GreenRecord, GrowthKind


#: Phrases that counter-signal drift toward a resume, a competence
#: certification, or a virtue signal. Matched case-insensitively against
#: observation labels; the intake stages such labels aside with a note
#: instead of scoring them.
COUNTER_SIGNAL_PHRASES: tuple[str, ...] = (
    "certified",
    "certification",
    "credential",
    "expert",
    "master",
    "resume",
    "accredited",
    "virtue",
)


def resolve_read_date(as_of: str | date | None) -> date:
    """Resolve the review date the freshness rules are anchored to."""

    if as_of is None:
        return date.today()
    if isinstance(as_of, str):
        try:
            return date.fromisoformat(as_of)
        except ValueError as exc:
            raise ValueError("as_of must be an ISO date in YYYY-MM-DD form") from exc
    if isinstance(as_of, datetime):
        raise TypeError("as_of must be None, an ISO date string, or a datetime.date")
    if isinstance(as_of, date):
        return as_of
    raise TypeError("as_of must be None, an ISO date string, or a datetime.date")


def resolve_max_age(max_age_days: int | None) -> int | None:
    """Validate the optional freshness window before it changes scoring."""

    if max_age_days is None:
        return None
    if isinstance(max_age_days, bool) or not isinstance(max_age_days, int):
        raise TypeError("max_observation_age_days must be a non-negative integer or None")
    if max_age_days < 0:
        raise ValueError("max_observation_age_days must be non-negative")
    return max_age_days


def registry_shape_error(records: tuple[GreenRecord, ...]) -> str | None:
    """Return a blocking note when a registry cannot be safely scored."""

    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, GreenRecord):
            return f"record registry entry {index} is not a GreenRecord record"
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (record.id, record.title, record.wire)
        ):
            return f"record registry entry {index} has blank or non-text fields"
        if record.id in seen_ids:
            return f"record registry contains duplicate id '{record.id}'"
        seen_ids.add(record.id)
        if (
            not isinstance(record.tags, frozenset)
            or not record.tags
            or any(not isinstance(tag, str) or not tag.strip() for tag in record.tags)
        ):
            return f"record '{record.id}' has malformed tags"
        if (
            not isinstance(record.required_markers, tuple)
            or not record.required_markers
            or any(
                not isinstance(label, str) or not label.strip()
                for label in record.required_markers
            )
        ):
            return f"record '{record.id}' has malformed required markers"
        if not isinstance(record.kind, GrowthKind):
            return f"record '{record.id}' has an invalid kind"
    return None


def clean_labels(raw: object, field: str) -> tuple[frozenset[str], tuple[str, ...]]:
    """Normalize a declared label collection without letting bad input crash.

    Returns the kept labels (stripped, lowercased) and intake notes for every
    declaration or token that had to be ignored.
    """

    if isinstance(raw, str) or not isinstance(raw, Iterable):
        return frozenset(), (
            f"{field} declaration is not a collection of labels and was ignored",
        )
    kept: set[str] = set()
    notes: list[str] = []
    for token in raw:
        if not isinstance(token, str) or not token.strip():
            notes.append(f"ignored a malformed {field} label")
            continue
        kept.add(token.strip().lower())
    return frozenset(kept), tuple(notes)


def is_counter_signal(label: str) -> bool:
    """Return whether a label counter-signals certification/resume drift."""

    lowered = label.lower()
    return any(phrase in lowered for phrase in COUNTER_SIGNAL_PHRASES)


def dated_labels(
    records: object,
    read_date: date,
    max_age_days: int | None,
) -> tuple[frozenset[str], frozenset[str], tuple[str, ...]]:
    """Split dated observations into fresh labels, stale labels, and notes.

    Undated records count as fresh. Future-dated or unreadable dates are
    never counted; they are surfaced as notes so the declarer can fix them.
    Counter-signal labels are staged aside with a note and never counted.
    """

    if isinstance(records, str) or not isinstance(records, Iterable):
        return (
            frozenset(),
            frozenset(),
            ("dated observation declaration is not a collection of records",),
        )
    fresh: set[str] = set()
    stale: set[str] = set()
    notes: list[str] = []
    for item in records:
        raw_label = getattr(item, "label", None)
        if not isinstance(raw_label, str) or not raw_label.strip():
            notes.append("ignored a dated observation record without a usable label")
            continue
        label = raw_label.strip().lower()
        if is_counter_signal(label):
            notes.append(
                f"observation '{label}' counter-signals certification or resume "
                "drift and was set aside rather than counted"
            )
            continue
        noted_on = getattr(item, "noted_on", None)
        if noted_on is None:
            fresh.add(label)
            continue
        try:
            noted = date.fromisoformat(noted_on)
        except (TypeError, ValueError):
            notes.append(
                f"observation '{label}' has an unreadable date and was not counted"
            )
            continue
        if noted > read_date:
            notes.append(
                f"observation '{label}' is dated in the future and was not counted"
            )
            continue
        if max_age_days is not None and (read_date - noted).days > max_age_days:
            stale.add(label)
            continue
        fresh.add(label)
    return frozenset(fresh), frozenset(stale), tuple(notes)
