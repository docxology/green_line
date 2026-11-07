from dataclasses import replace

import pytest

from green_line import (
    COUNTER_SIGNAL_PHRASES,
    CultivationAttempt,
    GreenRecord,
    GrowthStatus,
    Observation,
    read_cultivation,
    read_with_surfaces,
)
from green_line.intake import registry_shape_error


RECORD = GreenRecord(
    "practice", "Developing practice", "w", frozenset({"research"}), ("mentor",)
)


@pytest.mark.parametrize("phrase", COUNTER_SIGNAL_PHRASES)
@pytest.mark.parametrize("form", (str.lower, str.upper, lambda s: "  " + s + "  "))
@pytest.mark.parametrize(
    "noted_on", (None, "2026-08-01", "2020-01-01", "2099-01-01", "bad-date")
)
@pytest.mark.parametrize("undated_policy", ("current", "dated_only"))
def test_g01_channels_screen_the_same_labels(phrase, form, noted_on, undated_policy):
    label = form(phrase)
    record = replace(RECORD, required_markers=(phrase,))
    for attempt in (
        CultivationAttempt("learning", RECORD.tags, frozenset({label})),
        CultivationAttempt(
            "learning", RECORD.tags, dated_observations=(Observation(label, noted_on),)
        ),
    ):
        reading, surfaces = read_with_surfaces(
            attempt,
            (record,),
            as_of="2026-08-29",
            max_observation_age_days=60,
            undated_policy=undated_policy,
        )
        assert reading.status is GrowthStatus.NEEDS_MARKER
        assert not surfaces[0].present and not surfaces[0].stale
        assert surfaces[0].missing == (phrase,)
        assert [
            (d.label, d.disposition, d.reason_code) for d in reading.intake_dispositions
        ] == [(phrase, "excluded", "COUNTER_SIGNAL")]


@pytest.mark.parametrize("token", (None, 42, "", "  "))
def test_g01_malformed_observations_are_excluded(token):
    for attempt in (
        CultivationAttempt("learning", RECORD.tags, (token,)),
        CultivationAttempt(
            "learning", RECORD.tags, dated_observations=(Observation(token),)
        ),
    ):
        reading = read_cultivation(attempt, (RECORD,), as_of="2026-08-29")
        assert reading.status is GrowthStatus.NEEDS_MARKER
        assert [
            (d.disposition, d.reason_code) for d in reading.intake_dispositions
        ] == [("excluded", "MALFORMED_LABEL")]


def test_g01_legitimate_marker_and_tag_policy():
    record = replace(RECORD, tags=frozenset({"certified"}))
    attempt = CultivationAttempt(
        "learning", frozenset({"  Certified "}), frozenset({"  Mentor "})
    )
    reading, surfaces = read_with_surfaces(
        attempt,
        (record,),
        as_of="2026-08-29",
        registry_vocabulary=record.tags,
        instrument_id="tag-normalization",
    )
    assert reading.status is GrowthStatus.STAGED
    assert surfaces[0].present == ("mentor",)


def test_g01_substrings_are_screened_but_commentary_is_not():
    record = replace(RECORD, required_markers=("masterclass_practice", "mentor"))
    attempt = CultivationAttempt(
        "learning",
        RECORD.tags,
        dated_observations=(
            Observation("masterclass_practice", "2026-08-01"),
            Observation("mentor", "2026-08-01", commentary="certified expert"),
        ),
    )
    reading, surfaces = read_with_surfaces(attempt, (record,), as_of="2026-08-29")
    assert surfaces[0].present == ("mentor",)
    assert surfaces[0].missing == ("masterclass_practice",)
    assert {d.label: d.reason_code for d in reading.intake_dispositions} == {
        "masterclass_practice": "COUNTER_SIGNAL",
        "mentor": "CURRENT",
    }


@pytest.mark.parametrize(
    "record, diagnostic",
    (
        (replace(RECORD, id=" Practice "), "noncanonical id"),
        (replace(RECORD, tags=frozenset({"Research"})), "noncanonical tag"),
        (replace(RECORD, required_markers=(" Mentor ",)), "noncanonical marker"),
        (replace(RECORD, required_markers=("mentor", "mentor")), "duplicate marker"),
        (replace(RECORD, tags=frozenset({"farming"})), "outside declared vocabulary"),
    ),
)
def test_g06_registry_rejects_ambiguous_definitions(record, diagnostic):
    assert diagnostic in (registry_shape_error((record,)) or "")
    reading = read_cultivation(
        CultivationAttempt("learning", RECORD.tags), (record,), as_of="2026-08-29"
    )
    assert reading.status is GrowthStatus.NEEDS_REWORK
    assert not reading.findings
