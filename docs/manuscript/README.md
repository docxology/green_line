# manuscript

The instrument's own paper: `00_abstract.md` … `06_conclusion.md`, plus
`config.yaml`, `references.bib` and `MANUSCRIPT_STATUS.md`.

Formalism blocks are annotated `::: {#def:...}` / `::: {#prop:...}`. Labels,
references and file/anchor/line locations are re-derived from these files into
`data/formalism_claim_ledger.json` by
`uv run python scripts/gen_formalism_ledger.py`, and pinned by
`tests/test_formalism_claim_ledger.py`; a stale or empty ledger fails.

Rendering happens externally through the template engine (see `STANDALONE.md`);
render products stay in the git-ignored `output/`.
