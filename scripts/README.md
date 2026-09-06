# scripts

Thin CLIs over `src/green_line/`. The derivation lives in the package; these
files only bootstrap `src/` onto `sys.path`, guard the command line, and
delegate.

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `build_figures.py` | Build the deterministic figure bundle under `output/figures/` | `green_line.figures.build_figures()` | `uv run python scripts/build_figures.py` |
| `gen_binding.py` | Emit `data/binding_declaration.json` for the line_set maintainer | inline `LineEntry` declaration | `uv run python scripts/gen_binding.py` |
| `gen_envelopes.py` | Generate the witness envelopes under `data/envelopes/` from the real public API | `green_line.read_cultivation`, `green_line.reading_envelope`, `green_line.canonical_envelope` | `uv run python scripts/gen_envelopes.py` |
| `gen_formalism_ledger.py` | Regenerate `data/formalism_claim_ledger.json` from the manuscript blocks | `green_line.formalism_ledger.build_ledger()` | `uv run python scripts/gen_formalism_ledger.py` |

Every script rejects unexpected arguments (exit 2) so a mistyped flag cannot
read as a clean run.
