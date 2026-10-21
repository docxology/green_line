from dataclasses import replace
from pathlib import Path
import hashlib
import json
import pytest

from green_line import CultivationAttempt, read_cultivation, reading_envelope


def reading():
    return read_cultivation(CultivationAttempt("practice", frozenset({"research"})),
                            as_of="2026-08-29")


@pytest.mark.parametrize("refs", ("abc", b"abc", {"abc": "def"}))
def test_g04_reference_containers_are_not_split(refs):
    with pytest.raises(TypeError):
        reading_envelope(reading(), source_snapshot_refs=refs)


def test_g04_report_identity_structure_and_provenance_are_distinct():
    from green_line.envelope import report_matches, validate_envelope, provenance_digest
    report = reading()
    envelope = reading_envelope(report, "subject", ("declared:source",))
    assert validate_envelope(envelope, strict=True) == ()
    digest = provenance_digest(envelope, report)
    mutations = {
        "schema_version": "unexpected", "line_id": "another_line", "subject_id": "other",
        "review_date": "2026-08-30", "registry_version": "99.0.0",
        "registry_digest": "0" * 64, "native_status": "STAGED", "report_ref": "0" * 64,
        "source_snapshot_refs": ("another",), "scope_and_nonclaims": (),
    }
    for field, value in mutations.items():
        changed = replace(envelope, **{field: value})
        assert (report_matches(changed, report) is
                (field not in {"review_date", "registry_digest", "native_status", "report_ref"}))
        if field in {"schema_version", "line_id", "scope_and_nonclaims"}:
            assert validate_envelope(changed)
        assert provenance_digest(changed, report) != digest
    local = reading_envelope(report)
    assert not validate_envelope(local)
    assert validate_envelope(local, strict=True)


def test_g08_native_reports_exist_and_resolve():
    root = Path(__file__).resolve().parents[1] / "data" / "envelopes"
    for name in ("green_line_worked", "green_line_same_subject"):
        envelope = json.loads((root / f"{name}.json").read_text())
        report = root / f"{name}.report.json"
        assert report.is_file()
        assert hashlib.sha256(report.read_bytes()).hexdigest() == envelope["report_ref"]


@pytest.mark.parametrize("field, value", (
    ("subject_id", None), ("subject_id", "  "), ("review_date", "yesterday"),
    ("review_date", None), ("review_date", "20260829"), ("registry_version", "dev"), ("registry_version", None),
    ("registry_digest", "invalid"), ("report_ref", None), ("native_status", "APPROVED"),
    ("source_snapshot_refs", "abc"), ("source_snapshot_refs", ("",)),
    ("source_snapshot_refs", ("x" * 2049,)), ("source_snapshot_refs", ("x",) * 33),
))
def test_g04_each_invalid_field_is_rejected(field, value):
    from green_line import validate_envelope
    envelope = reading_envelope(reading(), "subject", ("declared:source",))
    assert validate_envelope(replace(envelope, **{field: value}))


def test_g04_strict_export_requires_identity_and_refs():
    with pytest.raises(ValueError, match="subject_id"):
        reading_envelope(reading(), strict=True)
    with pytest.raises(ValueError, match="source_snapshot_refs"):
        reading_envelope(reading(), "subject", strict=True)
