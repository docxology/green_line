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


def _assert_complete_utf8_replay(reading):
    import hashlib

    from green_line import canonical_envelope, reading_digest, reading_envelope
    from green_line.envelope import provenance_digest, report_matches

    report = canonical_reading(reading)
    payload = json.loads(report)
    # Check decoded values too: ASCII JSON escapes must not hide bad text.
    assert json.dumps(payload, ensure_ascii=False).encode("utf-8")
    assert reading.normalized_input.encode("utf-8")
    assert reading.registry_snapshot.encode("utf-8")
    assert reading_digest(reading) == hashlib.sha256(report.encode("utf-8")).hexdigest()
    assert canonical_reading(replay_reading(report)) == report
    envelope = reading_envelope(
        reading, "subject:unicode", ("declared:unicode",), strict=True
    )
    assert report_matches(envelope, reading)
    assert canonical_envelope(envelope).encode("utf-8")
    assert len(provenance_digest(envelope, reading)) == 64
    return report


def test_unpaired_description_code_units_are_private_distinct_and_replayable():
    from green_line import GreenRecord, GrowthStatus

    record = GreenRecord(
        "practice", "Practice", "Record practice.", frozenset({"research"}), ("mentor",)
    )
    texts = (
        "\ud800", "\ud801", "\udc00", "\ud83d\ude00",
        "private-description:\ud800",
    )
    digests, reports = set(), set()
    for text in texts:
        attempt = CultivationAttempt(
            text, record.tags, dated_observations=(Observation("mentor", "2026-08-29"),)
        )
        reading = read_cultivation(attempt, (record,), as_of="2026-08-29")
        assert reading.status is GrowthStatus.NEEDS_REWORK
        assert reading.scope_reason == "INVALID_DESCRIPTION"
        assert reading.findings == reading.marker_surfaces == reading.marker_evidence == ()
        assert [(d.disposition, d.reason_code) for d in reading.intake_dispositions] == [
            ("accepted", "CURRENT")
        ]
        snapshot = json.loads(reading.normalized_input)
        assert snapshot["description_valid"] is False
        assert reading.intake_notes
        report = _assert_complete_utf8_replay(reading)
        assert "private-description:" not in report
        assert json.dumps(text, ensure_ascii=True)[1:-1] not in report
        assert _assert_complete_utf8_replay(
            read_cultivation(attempt, (record,), as_of="2026-08-29")
        ) == report
        digests.add(reading.context.input_digest)
        reports.add(report)
    assert len(digests) == len(reports) == len(texts)


@pytest.mark.parametrize("mixed", (False, True))
def test_malformed_unicode_tags_are_set_aside_without_inventing_scope(mixed):
    from green_line import GrowthStatus

    reports, digests = set(), set()
    for bad in ("\ud800", "\ud801"):
        tags = frozenset({bad, "research"}) if mixed else frozenset({bad})
        attempt = CultivationAttempt("private", tags)
        reading = read_cultivation(attempt, as_of="2026-08-29")
        assert reading.scope_reason == "MALFORMED_TAGS"
        assert reading.status is (
            GrowthStatus.NEEDS_MARKER if mixed else GrowthStatus.OUTSIDE_SCOPE
        )
        assert bool(reading.findings) is mixed
        assert all(not surface.present for surface in reading.marker_surfaces)
        assert any("malformed tag" in note for note in reading.intake_notes)
        report = _assert_complete_utf8_replay(reading)
        assert _assert_complete_utf8_replay(
            read_cultivation(attempt, as_of="2026-08-29")
        ) == report
        reports.add(report)
        digests.add(reading.context.input_digest)
    assert len(reports) == len(digests) == 2


@pytest.mark.parametrize(
    "field, reason",
    (
        ("observations", "MALFORMED_LABEL"),
        ("label", "MALFORMED_LABEL"),
        ("noted_on", "INVALID_DATE"),
        ("source_ref", "MALFORMED_METADATA"),
        ("episode_id", "MALFORMED_METADATA"),
        ("commentary", "MALFORMED_METADATA"),
    ),
)
def test_unusable_observation_text_is_excluded_and_retained_for_replay(field, reason):
    from green_line import GreenRecord, GrowthStatus

    record = GreenRecord(
        "practice", "Practice", "Record practice.", frozenset({"research"}), ("mentor",)
    )
    reports, digests = set(), set()
    for bad in ("\ud800", "\ud801"):
        if field == "observations":
            attempt = CultivationAttempt("private", record.tags, frozenset({bad}))
        else:
            observation = replace(
                Observation("mentor", "2026-08-29"), **{field: bad}
            )
            attempt = CultivationAttempt(
                "private", record.tags, dated_observations=(observation,)
            )
        reading = read_cultivation(attempt, (record,), as_of="2026-08-29")
        assert reading.status is GrowthStatus.NEEDS_MARKER
        assert reading.scope_reason == "APPLIED"
        assert reading.marker_surfaces[0].present == ()
        assert reading.marker_surfaces[0].missing == ("mentor",)
        assert reading.marker_evidence[0].disposition == "missing"
        assert reading.findings[0].declaration_relevance == "NO_COUNTED_DECLARATIONS"
        assert [(d.disposition, d.reason_code) for d in reading.intake_dispositions] == [
            ("excluded", reason)
        ]
        assert reading.intake_notes
        snapshot = json.loads(reading.normalized_input)
        if field in {"source_ref", "episode_id", "commentary"}:
            assert snapshot["dated_observations"][0]["malformed_metadata"] is True
        report = _assert_complete_utf8_replay(reading)
        assert _assert_complete_utf8_replay(
            read_cultivation(attempt, (record,), as_of="2026-08-29")
        ) == report
        reports.add(report)
        digests.add(reading.context.input_digest)
    assert len(reports) == len(digests) == 2


@pytest.mark.parametrize(
    "field", ("next_practice_step", "review_question", "evidence_would_change")
)
def test_malformed_unicode_plan_is_visible_replayable_and_never_adds_coverage(field):
    from green_line import GrowthStatus, NextReview

    attempt = CultivationAttempt("private", frozenset({"research"}))
    baseline = read_cultivation(attempt, as_of="2026-08-29")
    reports, digests = set(), set()
    for bad in ("\ud800", "\ud801"):
        plan = NextReview(**{field: bad}, review_on="2026-09-01")
        changed = read_cultivation(
            replace(attempt, next_review=plan), as_of="2026-08-29"
        )
        assert changed.status is GrowthStatus.NEEDS_MARKER
        assert changed.scope_reason == baseline.scope_reason == "APPLIED"
        assert changed.findings == baseline.findings
        assert changed.marker_surfaces == baseline.marker_surfaces
        assert changed.marker_evidence == baseline.marker_evidence
        assert any("malformed next_review" in note for note in changed.intake_notes)
        report = _assert_complete_utf8_replay(changed)
        reports.add(report)
        digests.add(changed.context.input_digest)
    assert len(reports) == len(digests) == 2


def test_unicode_exclusions_preserve_counter_signal_metadata_and_date_precedence():
    from green_line import GreenRecord, GrowthStatus

    record = GreenRecord(
        "practice", "Practice", "Record practice.", frozenset({"research"}),
        ("mentor", "session_log"),
    )
    entries = (
        Observation("mentor", "2026-08-29"),
        Observation("mentor", "2026-08-28"),
        Observation("session_log", "2026-08-30"),
        Observation("session_log", "\ud800"),
        Observation("session_log", "bad-date", source_ref="\ud800"),
        Observation("certified", "bad-date", source_ref="\ud800"),
        Observation("certified\ud800", "2026-08-29"),
        Observation("other", "2026-08-29", commentary="certified expert"),
    )
    reports = []
    for declarations in (entries, tuple(reversed(entries)), frozenset(entries)):
        attempt = CultivationAttempt(
            "private", record.tags, frozenset({"\ud800"}),
            dated_observations=declarations,
        )
        reading = read_cultivation(
            attempt, (record,), as_of="2026-08-29", max_observation_age_days=0
        )
        assert reading.status is GrowthStatus.NEEDS_REWORK
        assert reading.scope_reason == "APPLIED"
        assert reading.marker_surfaces[0].present == ("mentor",)
        assert reading.marker_surfaces[0].missing == ("session_log",)
        assert reading.marker_surfaces[0].stale == ()
        assert reading.findings[0].declaration_relevance == "FRESH_REQUIRED"
        codes = [d.reason_code for d in reading.intake_dispositions]
        assert sorted(codes) == sorted((
            "CURRENT", "STALE", "FUTURE", "INVALID_DATE", "MALFORMED_METADATA",
            "COUNTER_SIGNAL", "MALFORMED_LABEL", "MALFORMED_LABEL", "UNREQUIRED_CURRENT",
        ))
        mentor = next(e for e in reading.marker_evidence if e.label == "mentor")
        assert mentor.disposition == "present"
        assert {d.reason_code for d in mentor.declarations} == {"CURRENT", "STALE"}
        assert next(
            d for d in reading.intake_dispositions if d.label == "certified"
        ).reason_code == "COUNTER_SIGNAL"
        assert next(
            d for d in reading.intake_dispositions if d.label == "other"
        ).reason_code == "UNREQUIRED_CURRENT"
        reports.append(_assert_complete_utf8_replay(reading))
    assert reports[0] == reports[1] == reports[2]


def test_malformed_instrument_configuration_is_rejected_before_native_output():
    for bad in ("\ud800", "custom-\ud801"):
        with pytest.raises(ValueError) as exc:
            read_cultivation(
                CultivationAttempt("private"), instrument_id=bad, as_of="2026-08-29"
            )
        assert not isinstance(exc.value, UnicodeError)
        assert str(exc.value).encode("utf-8")
