# scripts

Thin CLIs over `src/green_line/`. The derivation lives in the package; these
files only bootstrap `src/` onto `sys.path`, guard the command line, and
delegate.

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `build_figures.py` | Build the deterministic figure bundle under `output/figures/` | `green_line.figures.build_figures()` | `uv run python scripts/build_figures.py` |
| `gen_binding.py` | Emit `data/binding_declaration.json` for the line_set maintainer | inline `LineEntry` declaration | `uv run python scripts/gen_binding.py` |
| `gen_envelopes.py` | Generate a new example edition; preserve the historical `data/envelopes/` archive | `green_line.read_cultivation`, `green_line.reading_envelope`, `green_line.canonical_envelope` | `uv run python scripts/gen_envelopes.py --output-dir output/example-bundles/<actual-producer-sha> --source-commit <actual-producer-sha>` |
| `gen_formalism_ledger.py` | Regenerate `data/formalism_claim_ledger.json` from the manuscript blocks | `green_line.formalism_ledger.build_ledger()` | `uv run python scripts/gen_formalism_ledger.py` |

The binding generator supplies metadata for Green Line's existing declaration.
It does not admit a color or append another Green entry. `working_position`
remains unset here because the Line Set owner assigns that position.

The figure and formalism generators reject unexpected arguments (exit 2).
The envelope generator requires both `--output-dir` and `--source-commit`;
there is no historical output-directory or implicit HEAD default.

Envelope generation runs the current source, not the supplied commit.
Use a checkout matching the actual producing SHA and a new empty destination;
see `data/envelopes/README.md` for historical reproduction and new-edition provenance.
