#!/usr/bin/env python3
"""Regenerate ``data/formalism_claim_ledger.json`` from the manuscript blocks.

Thin orchestrator: parsing and derivation live in
``green_line.formalism_ledger``; this file only guards the invocation.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_line.formalism_ledger import build_ledger


def main() -> int:
    if len(sys.argv) != 1:
        print("usage: gen_formalism_ledger.py (no arguments)", file=sys.stderr)
        return 2
    print(build_ledger())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
