# AGENTS.md — `green_line/src`

## Scope
- Committed repository code (`src/green_line/`). Sibling Line Set repositories
  live beside this one and are read-only from here.
- Runtime contract: pure standard library, `requires-python >= 3.10`, no
  third-party import anywhere under `src/`.

## Layout
- `green_line/` — the single package; `green_line/figures/` builds the
  deterministic SVG bundle.

## Gotchas
- `tests/test_standalone_contract.py` re-parses every file here as Python 3.10
  syntax and fails on any sibling import, so keep new syntax 3.10-compatible.
- `pythonpath` in `pyproject.toml` already covers `src`; do not add path
  bootstrapping inside the package.
- Never let dict or set iteration order reach output: readings, digests and
  figures must be stable byte for byte.
