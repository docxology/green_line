from dataclasses import replace
import pytest
from green_line import CultivationAttempt, GreenRecord, GrowthStatus, Observation, read_cultivation

RECORD = GreenRecord("one", "Practice", "w", frozenset({"research"}), ("mentor", "log"))
ATTEMPT = CultivationAttempt("practice", RECORD.tags)


@pytest.mark.parametrize("attempt, records, status, reason", (
    (CultivationAttempt("p"), (RECORD,), GrowthStatus.OUTSIDE_SCOPE, "NO_TAGS"),
    (replace(ATTEMPT, tags=frozenset({"farming"})), (RECORD,), GrowthStatus.OUTSIDE_SCOPE, "UNMATCHED_TAGS"),
    (replace(ATTEMPT, tags="research"), (RECORD,), GrowthStatus.OUTSIDE_SCOPE, "MALFORMED_TAGS"),
    (ATTEMPT, (), GrowthStatus.OUTSIDE_SCOPE, "EMPTY_REGISTRY"),
    (ATTEMPT, (RECORD,), GrowthStatus.NEEDS_MARKER, "APPLIED"),
    (replace(ATTEMPT, observations=frozenset({"banana"})), (RECORD,), GrowthStatus.NEEDS_REWORK, "APPLIED"),
    (replace(ATTEMPT, observations=frozenset({"mentor"})), (RECORD,), GrowthStatus.NEEDS_REWORK, "APPLIED"),
    (replace(ATTEMPT, dated_observations=(Observation("mentor", "2099-01-01"),)), (RECORD,), GrowthStatus.NEEDS_MARKER, "APPLIED"),
))
def test_g07_scope_reasons_and_exact_global_rule(attempt, records, status, reason):
    reading = read_cultivation(attempt, records, as_of="2026-08-29")
    assert reading.status is status
    assert reading.scope_reason == reason


def test_g07_stale_only_and_record_relevance():
    attempt = replace(ATTEMPT, dated_observations=(Observation("mentor", "2020-01-01"), Observation("log", "2020-01-01")))
    reading = read_cultivation(attempt, (RECORD,), as_of="2026-08-29", max_observation_age_days=0)
    assert reading.status is GrowthStatus.NEEDS_MARKER
    assert reading.findings[0].declaration_relevance == "STALE_REQUIRED"
