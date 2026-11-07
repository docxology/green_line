from dataclasses import replace
from pathlib import Path
import hashlib
import json

import pytest

from green_line import canonical_reading, replay_reading
from green_line.examples import build_examples, SAME_SUBJECT_ATTEMPT, source_hashes

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ROOT / "data" / "envelopes"


def test_g08_current_generation_resolves_every_digest_and_replays(tmp_path):
    # A synthetic caller declaration, not an assertion about a real producer commit.
    commit = "a" * 40
    paths = build_examples(tmp_path, source_commit=commit)
    assert paths
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["source_commit"] == commit
    assert source_hashes() == manifest["source_hashes"]
    for row in manifest["examples"]:
        report = (tmp_path / row["report"]).read_text()
        envelope = json.loads((tmp_path / row["envelope"]).read_text())
        assert (
            hashlib.sha256(report.encode()).hexdigest()
            == row["report_sha256"]
            == envelope["report_ref"]
        )
        assert (
            hashlib.sha256((tmp_path / row["envelope"]).read_bytes()).hexdigest()
            == row["envelope_sha256"]
        )
        assert canonical_reading(replay_reading(report)) == report
        payload = json.loads(report)
        assert envelope["native_status"] == payload["status"]
        assert envelope["review_date"] == payload["read_as_of"]
        assert envelope["registry_digest"] == payload["registry_digest"]
        assert envelope["registry_version"] == payload["context"]["evaluator_version"]
        assert row["context"] == payload["context"]


def test_g08_historical_bundle_integrity_and_evaluator_boundary():
    # Historical bytes need their original evaluator, not an implicit migration.
    manifest = json.loads((SHIPPED / "manifest.json").read_text())
    for row in manifest["examples"]:
        report_bytes = (SHIPPED / row["report"]).read_bytes()
        envelope_bytes = (SHIPPED / row["envelope"]).read_bytes()
        envelope = json.loads(envelope_bytes)
        assert (
            hashlib.sha256(report_bytes).hexdigest()
            == row["report_sha256"]
            == envelope["report_ref"]
        )
        assert hashlib.sha256(envelope_bytes).hexdigest() == row["envelope_sha256"]
        with pytest.raises(ValueError, match="unsupported evaluator"):
            replay_reading(report_bytes.decode("utf-8"))


def test_g08_named_fixture_changes_the_generated_report(tmp_path):
    commit = "a" * 40
    build_examples(tmp_path / "original", source_commit=commit)
    changed = replace(SAME_SUBJECT_ATTEMPT, tags=frozenset({"data"}))
    build_examples(
        tmp_path / "changed", source_commit=commit, same_subject_attempt=changed
    )
    name = "green_line_same_subject.report.json"
    assert (tmp_path / "original" / name).read_bytes() != (
        tmp_path / "changed" / name
    ).read_bytes()


def test_g08_rejects_unpinned_sources_and_empty_source_scan(tmp_path):
    with pytest.raises(ValueError, match="immutable"):
        build_examples(tmp_path, source_commit="main")
    with pytest.raises(ValueError, match="empty"):
        source_hashes(tmp_path)
