# Development

## Set up the project

Install [uv](https://docs.astral.sh/uv/) and run commands from the project root
unless the render instructions change directories. The runtime uses Python
3.11 or later and the standard library. The developer environment adds
pytest, pytest-cov, and Ruff. The suite also checks that production source
parses as Python 3.10 syntax.

Install `rsvg-convert` (Debian or Ubuntu package `librsvg2-bin`, macOS package
`librsvg`) and put it on `PATH`. The figure builder and tests use it to
rasterize the cover.

```bash
uv sync --locked
```

## Run a reading

Run the [README example](../README.md#usage) with `uv run python`.
Set `as_of` to pin the review date and `max_observation_age_days` to
enable freshness checking for dated labels. Set
`undated_policy="dated_only"` when the reading should exclude undated labels.
See [native reports](native_reports.md) for replay context and
[practice records](practice_records.md) for episode and comparison policies.

## Verify the checkout

```bash
uv run --locked pytest tests/ --cov=src --cov-report=term
uv run --locked ruff check src tests scripts
uv run --locked python -c "import green_line; print(green_line.__version__)"
uv run --locked python scripts/build_figures.py
```

The full suite enforces the configured 90% branch and statement coverage floor
and checks the claim and formalism ledgers. The figure builder writes the
cover PNG and SVG, growth cards, marker matrix, status-flow diagram, and
registry JSON under `output/figures/`.

To export a new envelope edition, replace the placeholders with the output
directory and full SHA of the producing checkout.

```bash
uv run --locked python scripts/gen_envelopes.py --output-dir <empty-directory> --source-commit <full-sha>
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


## Render and validate the manuscript

Install Pandoc, the matching [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref/releases)
filter, and XeLaTeX with the [pinned template's TeX prerequisites](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/README.md#L565-L574).
Run from a clean Green Line checkout in a directory named `green_line`.
For release verification, use an isolated engine checkout and record its
exact revision.

```bash
green_line_root="$(pwd)"
template_root="$(mktemp -d)/template"
git clone https://github.com/docxology/template "$template_root"
git -C "$template_root" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2

uv sync --locked --python 3.11
uv run --locked --python 3.11 python scripts/build_figures.py
mkdir -p "$template_root/projects/working"
ln -s "$green_line_root" "$template_root/projects/working/green_line"

(
  cd "$template_root" &&
  uv sync --locked --no-dev --python 3.14 &&
  uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/green_line &&
  uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/green_line
)
```

The template resolves the project in its own `projects/working/` tree and
reads the canonical [manuscript configuration](manuscript/config.yaml).
The manuscript uses the generated cover shown in the build outputs.
Inspect the section order, citation, formalism links, and cover in the
following generated files under the Green Line checkout.

- `output/pdf/green_line_combined.pdf`
- `output/web/index.html`
- `output/reports/validation_report.md`
