"""Intake: fail-closed staging, counter-signals, date resolution."""

from __future__ import annotations

from datetime import date

import pytest

from green_line import COUNTER_SIGNAL_PHRASES, Observation, is_counter_signal
from green_line.intake import (
    clean_labels,
    dated_labels,
    registry_shape_error,
    resolve_max_age,
    resolve_read_date,
)


def test_counter_signal_detection() -> None:
    assert is_counter_signal("certified as expert")
    assert is_counter_signal("Added to my resume")
    assert is_counter_signal("virtue signalling note")
    assert not is_counter_signal("mentor session held")


def test_clean_labels_drops_malformed() -> None:
    kept, notes = clean_labels(["  Mentor ", "  ", 42, None], "observation")
    assert kept == frozenset({"mentor"})
    assert len(notes) >= 2


def test_clean_labels_non_collection() -> None:
    kept, notes = clean_labels(42, "observation")
    assert kept == frozenset()
    assert notes == ("observation declaration is not a collection of labels and was ignored",)


def test_dated_labels_future_and_unreadable() -> None:
    fresh, stale, notes = dated_labels(
        (
            Observation("ok", "2026-08-01"),
            Observation("future", "2099-01-01"),
            Observation("bad", "not-a-date"),
            Observation("undated"),
        ),
        date(2026, 8, 29),
        60,
    )
    assert "ok" in fresh and "undated" in fresh
    assert not stale
    assert len(notes) == 2


def test_dated_labels_stale_window() -> None:
    fresh, stale, _ = dated_labels(
        (Observation("old", "2020-01-01"), Observation("new", "2026-08-01")),
        date(2026, 8, 29),
        60,
    )
    assert stale == frozenset({"old"})
    assert "new" in fresh


def test_dated_labels_counter_signal_set_aside() -> None:
    fresh, stale, notes = dated_labels(
        (Observation("certified", "2026-08-01"),),
        date(2026, 8, 29),
        None,
    )
    assert not fresh and not stale
    assert any("set aside" in note for note in notes)


def test_dated_labels_not_a_collection() -> None:
    fresh, stale, notes = dated_labels("nope", date(2026, 8, 29), None)
    assert not fresh and not stale
    assert notes == ("dated observation declaration is not a collection of records",)


def test_resolve_read_date_forms() -> None:
    assert resolve_read_date(None) == date.today()
    assert resolve_read_date("2026-08-29") == date(2026, 8, 29)
    assert resolve_read_date(date(2026, 8, 29)) == date(2026, 8, 29)
    with pytest.raises(TypeError):
        resolve_read_date(42)  # type: ignore[arg-type]


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


def test_counter_signal_phrase_count_is_derivable() -> None:
    assert len(COUNTER_SIGNAL_PHRASES) == 8
