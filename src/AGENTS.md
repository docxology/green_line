# AGENTS.md — `green_line/src`

## Scope
- Committed repository code (`src/green_line/`). Sibling Line Set repositories
  live beside this one and are read-only from here.
- Runtime contract: pure standard library, `requires-python >= 3.11`, no
  third-party import anywhere under `src/`.

## Layout
- `green_line/` — the single package; `green_line/figures/` builds the
  deterministic SVG bundle.

## Gotchas
- `tests/test_standalone_contract.py` retains a Python 3.10 syntax-only check
  and rejects sibling imports. That check does not promise installation on 3.10.
- `pythonpath` in `pyproject.toml` already covers `src`; do not add path
  bootstrapping inside the package.
- Never let dict or set iteration order reach output: readings, digests and
  figures must be stable byte for byte.
