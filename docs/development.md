# Development

## Setup

Runtime installation and the developer suite require Python >=3.11.
The source AST gate retains a Python 3.10 syntax-only check; this is not a
3.10 installation or runtime-support claim. Use an external GitVault interpreter
and environment. Published release packets record historical interpreter
matrices, not verification of the current source.

`scripts/build_figures.py` rasterizes the cover through `rsvg-convert`, which is
not a Python dependency: install librsvg (`apt-get install librsvg2-bin` on
Debian/Ubuntu, `brew install librsvg` on macOS) so that it is on `PATH`.

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

The envelope command runs today's source. Supply the actual producing commit
only from a matching source checkout, and use a new empty output directory for
a new edition; `--source-commit` does not load that commit. Preserve the historical
bundle in `data/envelopes/`; see its [provenance guide](../data/envelopes/README.md).

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
