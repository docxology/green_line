"""Bind data/formalism_claim_ledger.json to the manuscript blocks."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "docs" / "manuscript"
LEDGER = ROOT / "data" / "formalism_claim_ledger.json"

_BLOCK = re.compile(r"^::: \{(?P<attrs>[^}]*)\}\s*$", re.M)
_LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")
_REFERENCE = re.compile(r"\[@((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-z0-9-]+)\]")


def _declared_labels() -> set[str]:
    labels: set[str] = set()
    for path in sorted(MANUSCRIPT.glob("*.md")):
        for match in _BLOCK.finditer(path.read_text(encoding="utf-8")):
            found = _LABEL.search(match.group("attrs"))
            if found:
                labels.add(found.group(1))
    return labels


def _referenced_labels() -> set[str]:
    refs: set[str] = set()
    for path in sorted(MANUSCRIPT.glob("*.md")):
        refs.update(_REFERENCE.findall(path.read_text(encoding="utf-8")))
    return refs


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _citations() -> set[str]:
    return {
        row["value"] for row in _ledger()["claims"] if row["kind"] == "citation"
    }


def test_every_declared_label_is_in_the_ledger() -> None:
    declared = _declared_labels()
    assert declared, "no labels declared; this gate would be vacuous"
    assert _citations() == declared, sorted(_citations() ^ declared)


def test_every_ledger_citation_is_a_declared_block() -> None:
    assert _citations() <= _declared_labels(), sorted(_citations() - _declared_labels())


def test_every_referenced_label_is_both_declared_and_ledgered() -> None:
    referenced = _referenced_labels()
    assert referenced, "no formalism references found; this gate would be vacuous"
    assert referenced <= _declared_labels(), sorted(referenced - _declared_labels())
    assert referenced <= _citations(), sorted(referenced - _citations())


def test_every_ledger_source_path_exists() -> None:
    for row in _ledger()["claims"]:
        assert (ROOT / row["source_path"]).is_file(), row["claim_id"]
        assert row["freshness"] == "active", row["claim_id"]


def test_ledger_claim_ids_are_unique() -> None:
    rows = _ledger()["claims"]
    assert len({row["claim_id"] for row in rows}) == len(rows)


def test_the_ledger_guard_rejects_an_unlisted_label() -> None:
    planted = _citations() - {"prop:determinism"}
    assert planted != _declared_labels()
    assert _declared_labels() - planted == {"prop:determinism"}


def test_the_ledger_guard_rejects_a_planted_foreign_label() -> None:
    planted = _citations() | {"prop:tier-monotone"}
    assert planted - _declared_labels() == {"prop:tier-monotone"}
