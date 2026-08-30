#!/usr/bin/env python3
"""Thin CLI for the deterministic figure builder."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_line.figures import build_figures


def main() -> int:
    if len(sys.argv) != 1:
        print("usage: build_figures.py (no arguments)", file=sys.stderr)
        return 2
    generated = build_figures()
    print(f"generated {len(generated)} figures under output/figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
