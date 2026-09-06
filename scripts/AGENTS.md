# AGENTS.md — `green_line/scripts`

## Script contract

Every file in `scripts/` is a thin CLI over `src/`. Business logic belongs in
`src/green_line/`, not here. Scripts bootstrap `src/` onto `sys.path`, reject
unexpected arguments, and delegate to one package entrypoint.

## Files

- `build_figures.py` — calls `green_line.figures.build_figures()` and prints the figure count
- `gen_binding.py` — writes `data/binding_declaration.json`
- `gen_envelopes.py` — writes the witness envelopes under `data/envelopes/` via `green_line`'s public API
- `gen_formalism_ledger.py` — regenerates `data/formalism_claim_ledger.json` via `green_line.formalism_ledger.build_ledger()`

## Canonical commands

```bash
uv run pytest tests/
uv run python scripts/gen_formalism_ledger.py
uv run python scripts/gen_binding.py
uv run python scripts/gen_envelopes.py
uv run python scripts/build_figures.py
```
