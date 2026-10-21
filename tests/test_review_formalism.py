import json
from pathlib import Path

import pytest
import green_line.formalism_ledger as ledger


def build_in(root: Path):
    manuscript = root / "docs" / "manuscript"
    manuscript.mkdir(parents=True, exist_ok=True)
    original = ledger.ROOT, ledger.MANUSCRIPT, ledger.OUT
    output = root / "ledger.json"
    try:
        ledger.ROOT, ledger.MANUSCRIPT, ledger.OUT = root, manuscript, output
        ledger.build_ledger()
        return json.loads(output.read_text())
    finally:
        ledger.ROOT, ledger.MANUSCRIPT, ledger.OUT = original


def test_g10_block_location_is_actual_source(tmp_path):
    manuscript = tmp_path / "docs" / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "02_method.md").write_text("::: {.unlabelled}\nText\n:::\n::: {.definition #def:moved}\nContent\n:::\n")
    payload = build_in(tmp_path)
    assert payload["claims"][0]["source_path"] == "docs/manuscript/02_method.md"
    (manuscript / "02_method.md").rename(manuscript / "01_introduction.md")
    assert build_in(tmp_path)["claims"][0]["source_path"] == "docs/manuscript/01_introduction.md"


def test_g10_duplicate_declarations_fail(tmp_path):
    manuscript = tmp_path / "docs" / "manuscript"
    manuscript.mkdir(parents=True)
    for name in ("02_method.md", "03_formalism.md"):
        (manuscript / name).write_text("::: {.definition #def:duplicate}\nContent\n:::\n")
    with pytest.raises(ValueError, match="duplicate"):
        build_in(tmp_path)


def test_g10_empty_scan_fails(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        build_in(tmp_path)
