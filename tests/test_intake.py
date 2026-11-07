"""Intake: fail-closed staging, counter-signals, date resolution."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from green_line import (
    CultivationAttempt,
    GreenRecord,
    Observation,
    is_counter_signal,
    read_cultivation,
    read_with_surfaces,
)
from green_line.intake import (
    registry_shape_error,
    resolve_max_age,
    resolve_read_date,
)


def test_counter_signal_detection() -> None:
    assert is_counter_signal("certified as expert")
    assert is_counter_signal("Added to my resume")
    assert is_counter_signal("virtue signaling note")
    assert not is_counter_signal("mentor session held")


def test_observations_drop_malformed_labels() -> None:
    attempt = CultivationAttempt(
        "practice", frozenset({"research"}), ["  Mentor ", "  ", 42, None]
    )
    record = GreenRecord("one", "Practice", "w", attempt.tags, ("mentor",))
    reading, surfaces = read_with_surfaces(attempt, (record,), as_of="2026-08-29")
    assert surfaces[0].present == ("mentor",)
    assert reading.status.value == "STAGED"
    assert [d.reason_code for d in reading.intake_dispositions].count(
        "MALFORMED_LABEL"
    ) == 3


@pytest.mark.parametrize("channel", ("observations", "dated_observations"))
def test_observation_non_collection_is_excluded(channel) -> None:
    attempt = CultivationAttempt("practice", frozenset({"research"}), **{channel: 42})
    record = GreenRecord("one", "Practice", "w", attempt.tags, ("mentor",))
    reading = read_cultivation(attempt, (record,), as_of="2026-08-29")
    assert reading.status.value == "NEEDS_MARKER"
    assert [
        (d.channel, d.disposition, d.reason_code) for d in reading.intake_dispositions
    ] == [(channel, "excluded", "MALFORMED_COLLECTION")]


def test_dated_observations_future_and_unreadable() -> None:
    attempt = CultivationAttempt(
        "practice",
        frozenset({"research"}),
        dated_observations=(
            Observation("ok", "2026-08-01"),
            Observation("future", "2099-01-01"),
            Observation("bad", "not-a-date"),
            Observation("undated"),
        ),
    )
    record = GreenRecord(
        "one", "Practice", "w", attempt.tags, ("ok", "future", "bad", "undated")
    )
    reading, surfaces = read_with_surfaces(
        attempt, (record,), as_of="2026-08-29", max_observation_age_days=60
    )
    assert surfaces[0].present == ("ok", "undated")
    assert surfaces[0].missing == ("future", "bad")
    assert not surfaces[0].stale
    assert {d.label: d.reason_code for d in reading.intake_dispositions} == {
        "ok": "CURRENT",
        "future": "FUTURE",
        "bad": "INVALID_DATE",
        "undated": "UNDATED",
    }


def test_dated_observations_stale_window() -> None:
    attempt = CultivationAttempt(
        "practice",
        frozenset({"research"}),
        dated_observations=(
            Observation("old", "2020-01-01"),
            Observation("new", "2026-08-01"),
        ),
    )
    record = GreenRecord("one", "Practice", "w", attempt.tags, ("old", "new"))
    reading, surfaces = read_with_surfaces(
        attempt, (record,), as_of="2026-08-29", max_observation_age_days=60
    )
    assert surfaces[0].present == ("new",)
    assert surfaces[0].stale == surfaces[0].missing == ("old",)
    assert {d.label: d.disposition for d in reading.intake_dispositions} == {
        "old": "stale",
        "new": "accepted",
    }


def test_resolve_read_date_forms() -> None:
    assert resolve_read_date(None) == date.today()
    assert resolve_read_date("2026-08-29") == date(2026, 8, 29)
    assert resolve_read_date(date(2026, 8, 29)) == date(2026, 8, 29)
    with pytest.raises(TypeError):
        resolve_read_date(42)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        resolve_read_date(datetime(2026, 8, 29))  # type: ignore[arg-type]


def test_resolve_max_age_forms() -> None:
    assert resolve_max_age(None) is None
    assert resolve_max_age(60) == 60
    with pytest.raises(ValueError):
        resolve_max_age(-1)
    with pytest.raises(TypeError):
        resolve_max_age(1.5)  # type: ignore[arg-type]


def test_registry_shape_error_paths() -> None:
    # An empty registry is shape-valid; the empty scan set is an evaluator
    # outcome (OUTSIDE_SCOPE), not an intake defect.
    assert registry_shape_error(()) is None
    assert "not a GreenRecord record" in (
        registry_shape_error(("junk",)) or ""  # type: ignore[list-item]
    )
    from green_line import GREEN_RECORDS, GreenRecord

    blank = GreenRecord("x", "  ", "w", frozenset({"research"}), ("m",))
    assert "blank or non-text" in (registry_shape_error((blank,)) or "")
    bad_tags = GreenRecord("x", "t", "w", frozenset(), ("m",))
    assert "malformed tags" in (registry_shape_error((bad_tags,)) or "")
    bad_markers = GreenRecord("x", "t", "w", frozenset({"research"}), ())
    assert "malformed required markers" in (registry_shape_error((bad_markers,)) or "")
    bad_kind = GreenRecord("x", "t", "w", frozenset({"research"}), ("m",), "PRACTICE")  # type: ignore[arg-type]
    assert "invalid kind" in (registry_shape_error((bad_kind,)) or "")
    ok = GREEN_RECORDS[0]
    assert registry_shape_error((ok,)) is None


def test_registry_shape_error_duplicate_id() -> None:
    from green_line import GREEN_RECORDS, GreenRecord

    ok = GREEN_RECORDS[0]
    duplicate = GreenRecord(ok.id, "same id", "w", frozenset({"research"}), ("m",))
    assert "duplicate id" in (registry_shape_error((ok, duplicate)) or "")
