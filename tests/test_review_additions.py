from dataclasses import replace
import json
import pytest

from green_line import (
    CultivationAttempt,
    GreenRecord,
    Observation,
    read_cultivation,
    canonical_reading,
    reading_envelope,
)

RECORD = GreenRecord("one", "Practice", "w", frozenset({"research"}), ("mentor", "log"))
ATTEMPT = CultivationAttempt("practice", RECORD.tags)


def test_a_next_review_never_upgrades_marker_coverage():
    from green_line.records import NextReview

    base = read_cultivation(ATTEMPT, (RECORD,), as_of="2026-08-29")
    attempt = replace(
        ATTEMPT,
        next_review=NextReview(
            "practice again", "What changed?", evidence_would_change="a declared log"
        ),
    )
    planned = read_cultivation(attempt, (RECORD,), as_of="2026-08-29")
    assert planned.status == base.status
    assert planned.findings == base.findings
    assert (
        json.loads(canonical_reading(planned))["normalized_input"]["next_review"][
            "review_on"
        ]
        is None
    )


def test_b_episode_attribution_and_explicit_combination_policy():
    attempt = replace(
        ATTEMPT,
        dated_observations=(
            Observation("mentor", source_ref="declared:mentor", episode_id="episode-a"),
            Observation("log", source_ref="declared:log", episode_id="episode-b"),
        ),
    )
    combined = read_cultivation(
        attempt, (RECORD,), as_of="2026-08-29", episode_policy="combine_declared"
    )
    separate = read_cultivation(
        attempt, (RECORD,), as_of="2026-08-29", episode_policy="single_episode"
    )
    assert combined.status.value == "STAGED"
    assert separate.status.value == "NEEDS_MARKER"
    assert {d.episode_id for d in combined.intake_dispositions} == {
        "episode-a",
        "episode-b",
    }
    assert {d.reason_code for d in separate.intake_dispositions} == {"EPISODE_CONFLICT"}
    one_episode = replace(
        attempt,
        dated_observations=tuple(
            replace(o, episode_id="episode-a") for o in attempt.dated_observations
        ),
    )
    assert (
        read_cultivation(
            one_episode, (RECORD,), as_of="2026-08-29", episode_policy="single_episode"
        ).status.value
        == "STAGED"
    )


def test_c_longitudinal_comparison_is_subject_bound_and_unranked():
    from green_line.comparison import compare_readings

    old = read_cultivation(
        replace(ATTEMPT, dated_observations=(Observation("mentor", "2020-01-01"),)),
        (RECORD,),
        as_of="2026-08-28",
        max_observation_age_days=60,
    )
    new = read_cultivation(
        replace(ATTEMPT, dated_observations=(Observation("mentor", "2026-08-29"),)),
        (RECORD,),
        as_of="2026-08-29",
        max_observation_age_days=60,
    )
    old_envelope = reading_envelope(old, "same subject", ("declared:old",))
    new_envelope = reading_envelope(new, "same subject", ("declared:new",))
    delta = compare_readings(old, old_envelope, new, new_envelope)
    assert delta.refreshed == (("one", "mentor"),)
    assert delta.still_missing == (("one", "log"),)
    assert not hasattr(delta, "score")
    with pytest.raises(ValueError, match="subject"):
        compare_readings(
            old, old_envelope, new, replace(new_envelope, subject_id="peer")
        )
    with pytest.raises(ValueError):
        compare_readings(None, old_envelope, new, new_envelope)


def test_a_invalid_review_dates_are_not_inferred():
    from green_line import NextReview

    for kwargs in (
        {"review_on": "yesterday"},
        {"review_question": " "},
        {"review_on": "20260829"},
    ):
        with pytest.raises(ValueError):
            NextReview(**kwargs)


def test_c_rejects_unmatched_reports_policies_registries_and_reverse_time():
    from green_line import compare_readings

    first = read_cultivation(ATTEMPT, (RECORD,), as_of="2026-08-28")
    second = read_cultivation(ATTEMPT, (RECORD,), as_of="2026-08-29")
    envelope = reading_envelope(first, "subject", ("declared:first",))
    for other in (
        read_cultivation(
            ATTEMPT, (RECORD,), as_of="2026-08-29", max_observation_age_days=0
        ),
        read_cultivation(
            ATTEMPT, (replace(RECORD, title="different"),), as_of="2026-08-29"
        ),
        read_cultivation(ATTEMPT, (RECORD,), as_of="2026-08-27"),
    ):
        with pytest.raises(ValueError):
            compare_readings(
                first,
                envelope,
                other,
                reading_envelope(other, "subject", ("declared:other",)),
            )
    with pytest.raises(ValueError, match="mismatch"):
        compare_readings(first, envelope, second, envelope)


def test_c_added_removed_and_refreshed_are_declarations_only():
    from green_line import compare_readings

    first = read_cultivation(
        replace(ATTEMPT, dated_observations=(Observation("mentor", "2026-08-01"),)),
        (RECORD,),
        as_of="2026-08-28",
    )
    second = read_cultivation(
        replace(ATTEMPT, dated_observations=(Observation("log", "2026-08-29"),)),
        (RECORD,),
        as_of="2026-08-29",
    )

    def envelope(r):
        return reading_envelope(r, "same subject", ("declared:source",))

    delta = compare_readings(first, envelope(first), second, envelope(second))
    assert delta.added == (("one", "log"),)
    assert delta.removed == (("one", "mentor"),)
    refreshed = read_cultivation(
        replace(ATTEMPT, dated_observations=(Observation("mentor", "2026-08-29"),)),
        (RECORD,),
        as_of="2026-08-29",
    )
    assert compare_readings(
        first, envelope(first), refreshed, envelope(refreshed)
    ).refreshed == (("one", "mentor"),)


@pytest.mark.parametrize("blocked_first", (False, True))
def test_c_blocked_description_is_not_a_declaration_delta(blocked_first):
    from green_line import compare_readings

    attempt = replace(ATTEMPT, observations=frozenset({"mentor"}))
    first = read_cultivation(
        replace(attempt, description=" " if blocked_first else "practice"),
        (RECORD,),
        as_of="2026-08-28",
    )
    second = read_cultivation(
        replace(attempt, description="practice" if blocked_first else " "),
        (RECORD,),
        as_of="2026-08-29",
    )
    blocked = first if blocked_first else second
    assert blocked.scope_reason == "INVALID_DESCRIPTION"
    assert blocked.marker_surfaces == ()
    assert any(
        d.label == "mentor" and d.disposition == "accepted"
        for d in blocked.intake_dispositions
    )
    first_envelope = reading_envelope(
        first,
        "same subject",
        ("declared:first",),
        strict=True,
    )
    second_envelope = reading_envelope(
        second,
        "same subject",
        ("declared:second",),
        strict=True,
    )
    with pytest.raises(ValueError, match="scored"):
        compare_readings(first, first_envelope, second, second_envelope)


@pytest.mark.parametrize("blocked_first", (False, True))
def test_c_invalid_registry_cannot_participate_in_comparison(blocked_first):
    from green_line import compare_readings

    first = read_cultivation(
        ATTEMPT,
        (RECORD, RECORD) if blocked_first else (RECORD,),
        as_of="2026-08-28",
    )
    second = read_cultivation(
        ATTEMPT,
        (RECORD,) if blocked_first else (RECORD, RECORD),
        as_of="2026-08-29",
    )
    blocked, scored = (first, second) if blocked_first else (second, first)
    assert blocked.scope_reason == "INVALID_REGISTRY"
    with pytest.raises(ValueError):
        reading_envelope(blocked, "same subject", ("declared:blocked",), strict=True)
    # There is no exportable envelope for this native diagnostic. Another
    # report's valid envelope cannot make the blocked read comparable.
    envelope = reading_envelope(
        scored,
        "same subject",
        ("declared:scored",),
        strict=True,
    )
    with pytest.raises(ValueError, match="scored"):
        compare_readings(first, envelope, second, envelope)


@pytest.mark.parametrize(
    "later_observations,removed,refreshed",
    (
        ((), (("one", "mentor"),), ()),
        ((Observation("mentor", "2026-08-01"),), (), ()),
        ((Observation("mentor", "2026-08-29"),), (), (("one", "mentor"),)),
    ),
)
def test_c_scored_removal_no_change_and_refresh_remain_comparable(
    later_observations,
    removed,
    refreshed,
):
    from green_line import compare_readings

    first = read_cultivation(
        replace(ATTEMPT, dated_observations=(Observation("mentor", "2026-08-01"),)),
        (RECORD,),
        as_of="2026-08-28",
    )
    second = read_cultivation(
        replace(ATTEMPT, dated_observations=later_observations),
        (RECORD,),
        as_of="2026-08-29",
    )
    assert first.scope_reason == second.scope_reason == "APPLIED"
    assert first.status.value == "NEEDS_REWORK"
    delta = compare_readings(
        first,
        reading_envelope(first, "same subject", ("declared:first",), strict=True),
        second,
        reading_envelope(second, "same subject", ("declared:second",), strict=True),
    )
    assert delta.added == ()
    assert delta.removed == removed
    assert delta.refreshed == refreshed
    assert delta.still_missing == (("one", "log"),)
