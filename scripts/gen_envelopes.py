#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from green_line.examples import build_examples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--source-commit",
        required=True,
        help="actual committed producer SHA; does not load or verify that source",
    )
    args = parser.parse_args()
    print(
        f"wrote {len(build_examples(args.output_dir, source_commit=args.source_commit))} bundle files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
