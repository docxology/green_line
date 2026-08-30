"""The line_set binding declaration: parseable, matches this brief."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECLARATION = ROOT / "data" / "binding_declaration.json"


def test_binding_declaration_parses() -> None:
    payload = json.loads(DECLARATION.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)


def test_binding_declaration_matches_brief() -> None:
    payload = json.loads(DECLARATION.read_text(encoding="utf-8"))
    assert payload["id"] == "green_line"
    assert payload["color"] == "green"
    assert payload["question"] == "What is still growing?"
    assert payload["must_not_become"] == (
        "A resume, a competence certification, or a virtue signal"
    )
    assert payload["opus_stage"] is None
    assert payload["working_position"] is None
    assert payload["package_name"] == "green_line"
    assert payload["registry_noun"] == "growth records"
    assert payload["verdict_noun"] == "growth status"


def test_binding_declaration_has_line_entry_kwargs() -> None:
    """Every LineEntry kwarg except working_position must be present."""

    payload = json.loads(DECLARATION.read_text(encoding="utf-8"))
    required = {
        "id",
        "color",
        "question",
        "job",
        "must_not_become",
        "opus_stage",
        "working_position",
        "package_name",
        "registry_noun",
        "verdict_noun",
    }
    assert required <= frozenset(payload)
