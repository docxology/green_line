from dataclasses import replace
import json

import pytest

from green_line import (
    GREEN_RECORDS,
    CultivationAttempt,
    GreenRecord,
    Observation,
    canonical_reading,
    read_cultivation,
    read_with_surfaces,
    registry_digest,
)


ATTEMPT = CultivationAttempt(
    "private description",
    frozenset({"research"}),
    dated_observations=(Observation("mentor", "2026-08-01"),),
)


def test_g02_registry_permutations_have_identical_reports_and_surfaces():
    expected, surfaces = read_with_surfaces(ATTEMPT, as_of="2026-08-29")
    for records in (
        tuple(reversed(GREEN_RECORDS)),
        list(reversed(GREEN_RECORDS)),
        iter(reversed(GREEN_RECORDS)),
        frozenset(GREEN_RECORDS),
    ):
        actual, actual_surfaces = read_with_surfaces(
            ATTEMPT, records, as_of="2026-08-29"
        )
        assert actual_surfaces == surfaces
        assert canonical_reading(actual) == canonical_reading(expected)
    for field, value in (
        ("title", "Changed"),
        ("wire", "A revised practice instruction."),
        ("tags", frozenset({"writing"})),
        ("required_markers", ("other",)),
    ):
        changed = (replace(GREEN_RECORDS[0], **{field: value}), *GREEN_RECORDS[1:])
        assert registry_digest(changed) != registry_digest(GREEN_RECORDS)


def test_g03_report_records_context_and_input_identity():
    a = json.loads(
        canonical_reading(
            read_cultivation(ATTEMPT, as_of="2026-08-29", max_observation_age_days=60)
        )
    )
    b = json.loads(
        canonical_reading(
            read_cultivation(ATTEMPT, as_of="2026-08-29", max_observation_age_days=90)
        )
    )
    assert a["context"]["max_observation_age_days"] == 60
    assert b["context"]["max_observation_age_days"] == 90
    assert a != b
    other = replace(ATTEMPT, description="another private description")
    c = json.loads(canonical_reading(read_cultivation(other, as_of="2026-08-29")))
    assert a["context"]["input_digest"] != c["context"]["input_digest"]
    assert "private description" not in canonical_reading(read_cultivation(ATTEMPT))


def test_g05_archived_typed_evidence_equals_surfaced_result():
    reading, surfaces = read_with_surfaces(
        ATTEMPT, as_of="2026-08-29", max_observation_age_days=0
    )
    payload = json.loads(canonical_reading(reading))
    assert payload["marker_surfaces"]
    assert reading.marker_surfaces == surfaces
    assert payload["intake_dispositions"][0]["reason_code"] == "STALE"
    for record, surface in zip(
        (r for r in sorted(GREEN_RECORDS, key=lambda r: r.id) if r.tags & ATTEMPT.tags),
        surfaces,
    ):
        assert set(surface.stale) <= set(surface.missing)
        assert set(surface.present).isdisjoint(surface.missing)
        assert set(surface.present) | set(surface.missing) == set(
            record.required_markers
        )


def test_g06_custom_vocabulary_requires_explicit_instrument():
    record = GreenRecord("farm", "Practice", "w", frozenset({"farming"}), ("mentor",))
    with pytest.raises(ValueError, match="instrument"):
        read_cultivation(ATTEMPT, (record,), registry_vocabulary=frozenset({"farming"}))
    reading = read_cultivation(
        replace(ATTEMPT, tags=record.tags),
        (record,),
        registry_vocabulary=record.tags,
        instrument_id="farm-practice",
        as_of="2026-08-29",
    )
    assert reading.context.instrument_id == "farm-practice"


def test_g03_archive_replays_without_current_defaults():
    from green_line.serialization import replay_reading

    reading = read_cultivation(ATTEMPT, as_of="2026-08-29", max_observation_age_days=0)
    report = canonical_reading(reading)
    assert canonical_reading(replay_reading(report)) == report
    payload = json.loads(report)
    for path, value in (("schema_version", "1.0"), ("status", "STAGED")):
        changed = {**payload, path: value}
        with pytest.raises(ValueError):
            replay_reading(json.dumps(changed))
    for field in (
        "input_digest",
        "counter_signal_policy_digest",
        "policy_version",
        "evaluator_version",
    ):
        changed = {**payload, "context": {**payload["context"], field: "foreign"}}
        with pytest.raises(ValueError):
            replay_reading(json.dumps(changed))


def test_registry_content_revision_requires_new_report_and_envelope_identities():
    from green_line import reading_envelope, replay_reading

    record = GreenRecord(
        "one", "Practice", "Original instruction.", frozenset({"research"}), ("mentor",)
    )
    original = read_cultivation(ATTEMPT, (record,), as_of="2026-08-29")
    revised = read_cultivation(
        ATTEMPT,
        (replace(record, wire="Revised instruction."),),
        as_of="2026-08-29",
    )
    assert revised.findings == original.findings
    assert revised.registry_digest != original.registry_digest
    original_report, revised_report = (
        canonical_reading(original),
        canonical_reading(revised),
    )
    assert original_report != revised_report
    assert reading_envelope(original, "same", ("declared:one",)).report_ref != (
        reading_envelope(revised, "same", ("declared:one",)).report_ref
    )
    assert canonical_reading(replay_reading(original_report)) == original_report
    payload = json.loads(original_report)
    payload["registry_snapshot"][0]["wire"] = "Revised instruction."
    with pytest.raises(ValueError):
        replay_reading(json.dumps(payload))


def test_opt_in_dated_only_policy_is_visible_and_replayable():
    attempt = CultivationAttempt("p", frozenset({"research"}), frozenset({"mentor"}))
    ordinary = read_cultivation(attempt, as_of="2026-08-29")
    strict = read_cultivation(attempt, as_of="2026-08-29", undated_policy="dated_only")
    assert strict.context.undated_policy == "dated_only"
    assert strict.marker_surfaces != ordinary.marker_surfaces
    assert {d.reason_code for d in strict.intake_dispositions} == {"UNDATED_PROFILE"}
    from green_line import replay_reading

    assert canonical_reading(
        replay_reading(canonical_reading(strict))
    ) == canonical_reading(strict)


def test_dated_replay_retains_every_declaration_and_fresh_marker_precedence():
    from green_line import replay_reading

    record = GreenRecord(
        "practice", "Practice", "w", frozenset({"research"}), ("mentor", "session_log")
    )
    attempt = CultivationAttempt(
        "learning",
        record.tags,
        dated_observations=(
            Observation("mentor", "2026-08-29", source_ref="declared:today"),
            Observation("mentor", "2026-08-28", episode_id="earlier"),
            Observation("session_log", "2026-08-30"),
            Observation("session_log", "20260829"),
            Observation("CERTIFIED", "bad-date", source_ref=""),
            Observation("other", "2026-08-29", commentary="expert"),
        ),
    )
    reading, surfaces = read_with_surfaces(
        attempt, (record,), as_of="2026-08-29", max_observation_age_days=0
    )
    assert surfaces[0].present == ("mentor",)
    assert surfaces[0].missing == ("session_log",)
    assert not surfaces[0].stale
    assert {d.reason_code for d in reading.intake_dispositions} == {
        "CURRENT",
        "STALE",
        "FUTURE",
        "INVALID_DATE",
        "COUNTER_SIGNAL",
        "UNREQUIRED_CURRENT",
    }
    mentor = next(item for item in reading.marker_evidence if item.label == "mentor")
    assert mentor.disposition == "present"
    assert {d.reason_code for d in mentor.declarations} == {"CURRENT", "STALE"}
    report = canonical_reading(reading)
    assert canonical_reading(replay_reading(report)) == report
    payload = json.loads(report)
    assert len(payload["normalized_input"]["dated_observations"]) == 6
    assert any(
        entry["commentary"] == "expert"
        for entry in payload["normalized_input"]["dated_observations"]
    )


def test_valid_unicode_canonical_bytes_and_hashes_remain_unchanged_and_distinct():
    import hashlib

    from green_line import (
        GrowthStatus,
        NextReview,
        canonical_registry,
        reading_digest,
        replay_reading,
    )

    texts = ("ASCII", "café", "🌱", "😀", "\ufffd", r"\ud800", r"\ud83d\ude00")
    digests = set()
    for text in texts:
        label = text.lower()
        record = GreenRecord("practice", text, text, frozenset({"research"}), (label,))
        attempt = CultivationAttempt(
            text,
            record.tags,
            dated_observations=(Observation(label, "2026-08-29", text, text, text),),
            next_review=NextReview(text, text, "2026-09-01", text),
        )
        reading = read_cultivation(attempt, (record,), as_of="2026-08-29")
        assert reading.status is GrowthStatus.STAGED
        assert reading.scope_reason == "APPLIED"
        assert reading.intake_notes == ()
        assert reading.marker_surfaces[0].present == (label,)
        assert reading.marker_surfaces[0].missing == ()
        expected_input = {
            "description_valid": True,
            "description_digest": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "tags": ["research"],
            "observations": [],
            "dated_observations": [
                {
                    "label": label,
                    "noted_on": "2026-08-29",
                    "source_ref": text,
                    "episode_id": text,
                    "commentary": text,
                }
            ],
            "next_review": {
                "next_practice_step": text,
                "review_question": text,
                "review_on": "2026-09-01",
                "evidence_would_change": text,
            },
        }
        expected_input_bytes = json.dumps(
            expected_input, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        expected_registry_bytes = json.dumps(
            [
                {
                    "id": "practice",
                    "title": text,
                    "wire": text,
                    "tags": ["research"],
                    "required_markers": [label],
                    "kind": "PRACTICE",
                }
            ],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        assert reading.normalized_input.encode("utf-8") == expected_input_bytes
        assert (
            reading.context.input_digest
            == hashlib.sha256(expected_input_bytes).hexdigest()
        )
        assert reading.registry_snapshot.encode("utf-8") == expected_registry_bytes
        assert canonical_registry((record,)).encode("utf-8") == expected_registry_bytes
        assert (
            reading.registry_digest
            == hashlib.sha256(expected_registry_bytes).hexdigest()
        )
        report = canonical_reading(reading)
        assert (
            reading_digest(reading)
            == hashlib.sha256(report.encode("utf-8")).hexdigest()
        )
        assert json.dumps(json.loads(report), ensure_ascii=False).encode("utf-8")
        assert canonical_reading(replay_reading(report)) == report
        assert (
            canonical_reading(read_cultivation(attempt, (record,), as_of="2026-08-29"))
            == report
        )
        digests.add(reading.context.input_digest)
    assert len(digests) == len(texts)

    # Hold all other declaration fields fixed: different description identities
    # must not be an incidental consequence of different metadata or plan text.
    descriptions = (*texts, "\ud800", "\ud801", "\ud83d\ude00")
    description_digests, description_reports = set(), set()
    for text in descriptions:
        attempt = CultivationAttempt(
            text,
            frozenset({"research"}),
            dated_observations=(Observation("mentor", "2026-08-29"),),
        )
        reading = read_cultivation(attempt, as_of="2026-08-29")
        assert reading.scope_reason == (
            "APPLIED" if text in texts else "INVALID_DESCRIPTION"
        )
        report = canonical_reading(reading)
        assert canonical_reading(replay_reading(report)) == report
        assert json.dumps(json.loads(report), ensure_ascii=False).encode("utf-8")
        description_digests.add(reading.context.input_digest)
        description_reports.add(report)
    assert len(description_digests) == len(description_reports) == len(descriptions)


def test_valid_unicode_custom_configuration_still_has_full_native_replay():
    from green_line import GrowthStatus, replay_reading

    record = GreenRecord(
        "práctica🌱", "Práctica", "Révision 🌱", frozenset({"jardín🌱"}), ("témoin🌱",)
    )
    attempt = CultivationAttempt(
        "private prose",
        record.tags,
        dated_observations=(Observation("témoin🌱", "2026-08-29"),),
    )
    reading, surfaces = read_with_surfaces(
        attempt,
        (record,),
        as_of="2026-08-29",
        registry_vocabulary=record.tags,
        instrument_id="práctica🌱",
    )
    assert reading.status is GrowthStatus.STAGED
    assert reading.scope_reason == "APPLIED"
    assert reading.context.instrument_id == "práctica🌱"
    assert reading.context.registry_vocabulary == ("jardín🌱",)
    assert surfaces[0].present == ("témoin🌱",)
    report = canonical_reading(reading)
    assert "private prose" not in report
    assert json.dumps(json.loads(report), ensure_ascii=False).encode("utf-8")
    assert canonical_reading(replay_reading(report)) == report
