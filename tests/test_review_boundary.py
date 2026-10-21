from dataclasses import replace

import pytest

from green_line import (
    COUNTER_SIGNAL_PHRASES, CultivationAttempt, GreenRecord, GrowthStatus,
    Observation, read_cultivation,
)
from green_line.intake import clean_labels, dated_labels, registry_shape_error
from datetime import date


RECORD = GreenRecord("practice", "Developing practice", "w",
                     frozenset({"research"}), ("mentor",))


@pytest.mark.parametrize("phrase", COUNTER_SIGNAL_PHRASES)
@pytest.mark.parametrize("form", (str.lower, str.upper, lambda s: "  " + s + "  "))
def test_g01_channels_screen_the_same_labels(phrase, form):
    label = form(phrase)
    ordinary, notes = clean_labels([label], "observation")
    dated, stale, dated_notes = dated_labels((Observation(label),), date(2026, 8, 29), None)
    assert ordinary == dated == frozenset()
    assert not stale
    assert notes == dated_notes
    record = replace(RECORD, required_markers=(phrase,))
    for attempt in (
        CultivationAttempt("learning", RECORD.tags, frozenset({label})),
        CultivationAttempt("learning", RECORD.tags, dated_observations=(Observation(label),)),
    ):
        reading = read_cultivation(attempt, (record,), as_of="2026-08-29")
        assert reading.status is GrowthStatus.NEEDS_MARKER
        assert "set aside" in reading.intake_notes[0]


@pytest.mark.parametrize("token", (None, 42, "", "  "))
def test_g01_malformed_observations_are_excluded(token):
    ordinary, notes = clean_labels([token], "observation")
    dated, stale, dated_notes = dated_labels((Observation(token),), date(2026, 8, 29), None)
    assert ordinary == dated == frozenset()
    assert not stale
    assert notes and dated_notes


def test_g01_legitimate_marker_and_tag_policy():
    assert clean_labels(["  Mentor "], "observation") == (frozenset({"mentor"}), ())
    assert clean_labels(["certified"], "tag") == (frozenset({"certified"}), ())


@pytest.mark.parametrize("record, diagnostic", (
    (replace(RECORD, id=" Practice "), "noncanonical id"),
    (replace(RECORD, tags=frozenset({"Research"})), "noncanonical tag"),
    (replace(RECORD, required_markers=(" Mentor ",)), "noncanonical marker"),
    (replace(RECORD, required_markers=("mentor", "mentor")), "duplicate marker"),
    (replace(RECORD, tags=frozenset({"farming"})), "outside declared vocabulary"),
))
def test_g06_registry_rejects_ambiguous_definitions(record, diagnostic):
    assert diagnostic in (registry_shape_error((record,)) or "")
    reading = read_cultivation(CultivationAttempt("learning", RECORD.tags),
                               (record,), as_of="2026-08-29")
    assert reading.status is GrowthStatus.NEEDS_REWORK
    assert not reading.findings
