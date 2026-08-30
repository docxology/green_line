#!/usr/bin/env python3
"""Emit data/binding_declaration.json — the exact LineEntry kwargs a
line_set maintainer will append. Prepared here; applied there."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

ROOT = Path(__file__).resolve().parents[1]
declaration = {
    "id": "green_line",
    "color": "green",
    "question": "What is still growing?",
    "job": (
        "Capacity under development: apprenticeships, skills deliberately not "
        "yet mastered, with marker/counter-signal staging"
    ),
    "must_not_become": "A resume, a competence certification, or a virtue signal",
    "opus_stage": None,
    "working_position": None,
    "package_name": "green_line",
    "registry_noun": "growth records",
    "verdict_noun": "growth status",
}
out = ROOT / "data" / "binding_declaration.json"
out.write_text(json.dumps(declaration, indent=2) + "\n", encoding="utf-8")
print("wrote", out)
