#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_line.examples import build_examples

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "envelopes")
    parser.add_argument("--source-commit")
    args = parser.parse_args()
    commit = args.source_commit or subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.strip()
    print(f"wrote {len(build_examples(args.output_dir, source_commit=commit))} bundle files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
