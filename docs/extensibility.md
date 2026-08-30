# Extending green_line

## Adding a growth record

Append one `GreenRecord` to `GREEN_RECORDS` in `src/green_line/registry.py`,
using tags from `TAG_VOCABULARY`. Then:

1. Rerun the invariant battery (`uv run pytest tests/test_invariants.py`).
   Tags outside the vocabulary fail closed.
2. Regenerate figures (`uv run python scripts/build_figures.py`); the
   registry digest in `output/figures/figure_registry.json` moves, which is
   the intended drift signal.
3. Update the claim ledger if a numeric row changed; rows are re-derived by
   tests, so a stale ledger fails loudly.

## What adding a record does not touch

- `src/green_line/evaluator.py` — every check takes the registry as data.
- `src/green_line/intake.py` — intake is per-record-shape, not per-record.
- The envelope module — it pins digests, not counts.

## The line's own extension constraint

Green Line carries `opus_stage=None` by design: the four classical stages
are allocated in the set declaration, and a stageless line is the designed
outcome, not a fallback. Do not invent a fifth stage name.
