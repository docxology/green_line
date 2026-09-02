# Development

## Setup

```bash
uv sync
```

## Gates

```bash
uv run pytest tests/ --cov=src --cov-report=term   # >= 90
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run pytest tests/test_formalism_claim_ledger.py
```

## Layout

- `src/green_line/` — all runtime code, pure standard library.
- `tests/` — real data, negative controls, a no-mocks scan, envelope
  structure validation against a frozen schema copy.
- `data/` — claim ledger, formalism ledger (generated), envelopes, binding
  declaration.
- `docs/manuscript/` — the instrument's own paper, including a formalism file
  with `::: {#def:/prop:...}` blocks.
