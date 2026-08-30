#!/usr/bin/env python3
"""Generate data/formalism_claim_ledger.json from the manuscript blocks."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
OUT = ROOT / "data" / "formalism_claim_ledger.json"

BLOCK = re.compile(r"^::: \{(?P<attrs>[^}]*)\}\s*$", re.M)
LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")

labels: set[str] = set()
for path in sorted(MANUSCRIPT.glob("*.md")):
    for match in BLOCK.finditer(path.read_text(encoding="utf-8")):
        found = LABEL.search(match.group("attrs"))
        if found:
            labels.add(found.group(1))

rows = []
for label in sorted(labels):
    rows.append(
        {
            "claim_id": label.replace(":", "_").replace("-", "_"),
            "kind": "citation",
            "value": label,
            "source": "manuscript/03_formalism.md: block declared with this label",
            "source_path": "manuscript/03_formalism.md",
            "source_tier": "manuscript_formalism_block",
            "freshness": "active",
        }
    )

payload = {
    "schema_version": "1.0",
    "purpose": (
        "Declares the manuscript's formalism-block labels so the render "
        "engine's evidence registry can resolve a [@def:...]/[@prop:...] "
        "cross-reference instead of reporting it as an unsupported citation."
    ),
    "boundary": (
        "A row here records that a label is declared. It is not evidence "
        "that the proposition it names is true."
    ),
    "claims": rows,
}
OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
print("wrote", OUT, "with", len(rows), "rows")
