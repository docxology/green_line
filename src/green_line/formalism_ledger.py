"""Derivation of ``data/formalism_claim_ledger.json`` from the manuscript blocks."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "docs" / "manuscript"
OUT = ROOT / "data" / "formalism_claim_ledger.json"

BLOCK = re.compile(r"^::: \{(?P<attrs>[^}]*)\}\s*$", re.M)
LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")


def build_ledger() -> str:
    """Derive the citation rows, write the ledger, and return the summary line."""

    labels: dict[str, tuple[str, int]] = {}
    for path in sorted(MANUSCRIPT.glob("*.md")):
        for match in BLOCK.finditer(path.read_text(encoding="utf-8")):
            found = LABEL.search(match.group("attrs"))
            if found:
                label = found.group(1)
                if label in labels:
                    raise ValueError(f"duplicate formalism label: {label}")
                labels[label] = (path.relative_to(ROOT).as_posix(),
                                 path.read_text(encoding="utf-8")[:match.start()].count("\n") + 1)

    if not labels:
        raise ValueError("empty formalism declaration scan")

    rows = []
    for label in sorted(labels):
        source_path, source_line = labels[label]
        rows.append(
            {
                "claim_id": label.replace(":", "_").replace("-", "_"),
                "kind": "citation",
                "value": label,
                "source": f"{source_path}#{label}: block declared with this label",
                "source_path": source_path,
                "source_anchor": label,
                "source_line": source_line,
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
    return f"wrote {OUT} with {len(rows)} rows"
