from dataclasses import replace
import json
import pytest

from green_line import CultivationAttempt, Observation, read_cultivation, canonical_reading, replay_reading
from green_line.intake import registry_shape_error


def test_g05_every_observation_has_a_machine_disposition():
    attempt = CultivationAttempt("private", frozenset({"research"}), observations=("banana", None),
        dated_observations=(Observation("mentor"), Observation("session_log", "2026-08-29"),
            Observation("mentor", "2020-01-01"), Observation("mentor", "2099-01-01"),
            Observation("mentor", "bad-date"), Observation("mentor", 42),
            Observation("certified"), Observation(None), Observation("log", source_ref=" ")))
    reading = read_cultivation(attempt, as_of="2026-08-29", max_observation_age_days=60)
    assert {d.reason_code for d in reading.intake_dispositions} == {
        "UNREQUIRED_UNDATED", "MALFORMED_LABEL", "UNDATED", "CURRENT", "STALE",
        "FUTURE", "INVALID_DATE", "COUNTER_SIGNAL", "MALFORMED_METADATA"}
    assert canonical_reading(replay_reading(canonical_reading(reading))) == canonical_reading(reading)


def test_g05_malformed_optional_plan_is_visible_and_never_upgrades():
    attempt = CultivationAttempt("p", frozenset({"research"}))
    baseline = read_cultivation(attempt, as_of="2026-08-29")
    changed = read_cultivation(replace(attempt, next_review="tomorrow"), as_of="2026-08-29")
    assert baseline.findings == changed.findings
    assert "malformed next_review" in changed.intake_notes[0]


@pytest.mark.parametrize("vocabulary", (frozenset(), frozenset({"Research"}), frozenset({None})))
def test_g06_invalid_declared_vocabulary_has_a_diagnostic(vocabulary):
    assert "vocabulary" in registry_shape_error((), vocabulary)


@pytest.mark.parametrize("kwargs", ({"instrument_id": " "}, {"episode_policy": "implicit"}, {"undated_policy": "implicit"}))
def test_invalid_evaluation_policy_is_rejected(kwargs):
    with pytest.raises(ValueError):
        read_cultivation(CultivationAttempt("p"), **kwargs)


@pytest.mark.parametrize("payload", ("{}", "[]", '{"schema_version":"green.native-reading/2.0"}'))
def test_g03_malformed_archives_fail_closed(payload):
    with pytest.raises(ValueError):
        replay_reading(payload)


def test_g03_an_invalid_registry_report_is_explicitly_not_replayable():
    reading = read_cultivation(CultivationAttempt("p"), records=("bad",), as_of="2026-08-29")
    with pytest.raises(ValueError, match="registry"):
        replay_reading(canonical_reading(reading))


def test_g03_tampered_input_is_rejected():
    reading = read_cultivation(CultivationAttempt("p"), as_of="2026-08-29")
    payload = json.loads(canonical_reading(reading))
    payload["normalized_input"]["tags"] = ["research"]
    with pytest.raises(ValueError, match="digest"):
        replay_reading(json.dumps(payload))
