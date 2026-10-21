from dataclasses import replace
from pathlib import Path
import hashlib
import json

import pytest

from green_line import canonical_reading, replay_reading
from green_line.examples import build_examples, SAME_SUBJECT_ATTEMPT, source_hashes, worked_prose

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ROOT / "data" / "envelopes"


def test_g08_regeneration_resolves_every_digest_and_replays(tmp_path):
    manifest = json.loads((SHIPPED / "manifest.json").read_text())
    paths = build_examples(tmp_path, source_commit=manifest["source_commit"])
    assert paths
    for path in paths:
        assert path.read_bytes() == (SHIPPED / path.name).read_bytes()
    assert source_hashes() == manifest["source_hashes"]
    for row in manifest["examples"]:
        report = (tmp_path / row["report"]).read_text()
        envelope = json.loads((tmp_path / row["envelope"]).read_text())
        assert hashlib.sha256(report.encode()).hexdigest() == row["report_sha256"] == envelope["report_ref"]
        assert hashlib.sha256((tmp_path / row["envelope"]).read_bytes()).hexdigest() == row["envelope_sha256"]
        assert canonical_reading(replay_reading(report)) == report
        payload = json.loads(report)
        assert envelope["native_status"] == payload["status"]
        assert envelope["review_date"] == payload["read_as_of"]
        assert envelope["registry_digest"] == payload["registry_digest"]


def test_g08_named_fixture_changes_the_generated_report(tmp_path):
    commit = "a" * 40
    build_examples(tmp_path / "original", source_commit=commit)
    changed = replace(SAME_SUBJECT_ATTEMPT, tags=frozenset({"data"}))
    build_examples(tmp_path / "changed", source_commit=commit, same_subject_attempt=changed)
    name = "green_line_same_subject.report.json"
    assert (tmp_path / "original" / name).read_bytes() != (tmp_path / "changed" / name).read_bytes()


def test_g08_rejects_unpinned_sources_and_empty_source_scan(tmp_path):
    with pytest.raises(ValueError, match="immutable"):
        build_examples(tmp_path, source_commit="main")
    with pytest.raises(ValueError, match="empty"):
        source_hashes(tmp_path)


def test_worked_manuscript_is_generated_from_actual_read():
    text = (ROOT / "docs" / "manuscript" / "04_examples.md").read_text()
    assert worked_prose() in text
