# Development

## Setup

Runtime support is Python >=3.10. The developer suite requires Python >=3.11
because metadata tests use standard-library `tomllib`. The runtime does not
import it. Use an external GitVault interpreter and environment; see the
release packet for the actually exercised interpreter matrix.

```bash
uv sync
```

## Gates

```bash
uv run pytest tests/ --cov=src --cov-report=term   # >= 90
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run pytest tests/test_formalism_claim_ledger.py
uv run python scripts/gen_envelopes.py --output-dir <empty-directory> --source-commit <full-sha>
```

## Layout

- `src/green_line/` — all runtime code, pure standard library.
- `tests/` — real data, negative controls, a no-mocks scan, envelope
  structure validation against a frozen schema copy.
- `data/` — claim ledger, formalism ledger (generated), envelopes, binding
  declaration.
- `docs/manuscript/` — the instrument's own paper, including a formalism file
  with `::: {#def:/prop:...}` blocks.

The AST import policy checks static sibling imports, including aliases and
multiple imports. It does not prove that arbitrary dynamic imports are
impossible. The installed-wheel smoke runs in an isolated environment with
all sibling packages absent. Runtime dependencies remain empty; the only
developer dependencies remain pytest, pytest-cov and ruff. External release
tooling may run a type checker in its own environment without becoming a
project dependency. The committed uv lock pins the developer environment.
