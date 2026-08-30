# AGENTS.md — green_line working contract

## Invariants

1. **Standalone.** The repo installs, tests, checks, builds figures, and
   renders with zero siblings present. Absence of a sibling is the outcome
   `NOT_INSTALLED`, never an exception.
2. **Pure standard library at runtime.** Dev deps only: pytest, pytest-cov,
   ruff.
3. **No mocking framework.** Exercise absent/failing inputs with plain
   callables, real temp dirs, fail-closed paths.
4. **Fail closed.** Every gate fails on an empty scan set; intake sets aside
   unknown/malformed input with notes.
5. **Nothing sorted by accident.** Sort before emit; no dict/set iteration
   order reaches a reading or digest.
6. **Siblings are read-only.** line_set and witness_register integration is
   prepared here (data/binding_declaration.json, data/envelopes/) and
   applied by a maintainer there.
7. **Claims are narrow and first person.** docs/claim_boundaries.md is the
   register of record. Never hardcode a number the code can derive.

## Verify commands

```bash
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run pytest tests/test_formalism_claim_ledger.py
```
