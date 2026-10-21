from datetime import date
from pathlib import Path
import runpy

import pytest

from green_line import (
    CultivationAttempt, GreenRecord, Observation, read_cultivation, reading_envelope,
    compare_readings,
)
from green_line.intake import dated_labels, resolve_read_date

ROOT = Path(__file__).resolve().parents[1]
RECORD = GreenRecord("one", "Practice", "w", frozenset({"research"}), ("mentor",))


@pytest.mark.parametrize("token", ("20260801", "2026-W31-6", "2026-8-1", "2026-02-30"))
def test_review_dates_and_observation_dates_use_one_portable_grammar(token):
    attempt = CultivationAttempt("p", RECORD.tags, dated_observations=(Observation("mentor", token),))
    reading = read_cultivation(attempt, (RECORD,), as_of="2026-08-29")
    assert reading.intake_dispositions[0].reason_code == "INVALID_DATE"
    assert reading.status.value == "NEEDS_MARKER"
    assert dated_labels(attempt.dated_observations, date(2026, 8, 29), None)[:2] == (frozenset(), frozenset())
    with pytest.raises(ValueError):
        resolve_read_date(token)


def read(label_date):
    return read_cultivation(CultivationAttempt("p", RECORD.tags,
        dated_observations=(Observation("mentor", label_date),)), (RECORD,), as_of="2026-08-29")


@pytest.mark.parametrize("old_date,new_date,refreshed", (
    (None, "2020-01-01", ()),
    ("2026-08-01", "2026-08-01", ()),
    ("2026-08-01", "2026-08-29", (("one", "mentor"),)),
    ("2026-08-29", None, ()),
))
def test_refresh_requires_established_later_dates(old_date, new_date, refreshed):
    older, newer = read(old_date), read(new_date)
    delta = compare_readings(older, reading_envelope(older, "same", ("declared:old",)),
                             newer, reading_envelope(newer, "same", ("declared:new",)))
    assert delta.refreshed == refreshed


@pytest.mark.parametrize("name,gate", (
    ("test_standalone_contract.py", "test_no_sibling_imports_in_code"),
    ("test_no_mocks.py", "test_no_mock_framework_in_source_trees"),
))
@pytest.mark.parametrize("empty_tree", ("src", "tests", "scripts"))
def test_static_gates_reject_empty_real_scan_sets(tmp_path, name, gate, empty_tree):
    for tree in ("src", "tests", "scripts"):
        (tmp_path / tree).mkdir()
        if tree != empty_tree:
            (tmp_path / tree / "clean.py").write_text("value = 1\n")
    namespace = runpy.run_path(str(ROOT / "tests" / name))
    namespace[gate].__globals__["ROOT"] = tmp_path
    with pytest.raises(AssertionError, match="empty"):
        namespace[gate]()


@pytest.mark.parametrize("name,gate,source", (
    ("test_standalone_contract.py", "test_no_sibling_imports_in_code", "import red_line\n"),
    ("test_no_mocks.py", "test_no_mock_framework_in_source_trees", "import unittest" + ".mock\n"),
))
def test_static_gates_reject_real_planted_violations(tmp_path, name, gate, source):
    for tree in ("src", "tests", "scripts"):
        (tmp_path / tree).mkdir()
        (tmp_path / tree / "clean.py").write_text("value = 1\n")
    namespace = runpy.run_path(str(ROOT / "tests" / name))
    namespace[gate].__globals__["ROOT"] = tmp_path
    namespace[gate]()
    (tmp_path / "src" / "planted.py").write_text(source)
    with pytest.raises(AssertionError):
        namespace[gate]()


def test_envelope_readme_identifies_current_bundles():
    from green_line import __version__
    text = (ROOT / "data" / "envelopes" / "README.md").read_text()
    assert f"green_line {__version__}" in text
    for required in ("manifest.json", ".report.json", "--source-commit", "--output-dir"):
        assert required in text
