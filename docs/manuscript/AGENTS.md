# AGENTS.md — `green_line/docs/manuscript`

## Scope
- The instrument's own paper, kept in this repository. Rendering happens
  externally through the template engine, never through a sibling checkout.

## Layout
- `00_abstract.md` … `06_conclusion.md` and `99_references.md` — ordered sources.
- `config.yaml`, `references.bib` — publication metadata and bibliography.
- `MANUSCRIPT_STATUS.md` — publication-readiness note.

## Gotchas
- Formalism blocks (`::: {#def:...}` / `::: {#prop:...}`) are parsed by
  `green_line.formalism_ledger`; after moving or renaming a label, regenerate
  the ledger, because file/anchor/line locations are pinned.
- `tests/test_formalism_claim_ledger.py` fails on duplicate labels, references
  to missing labels and empty scans.
- `config.yaml` records the DOI for the archived source edition. The current
  manuscript and any new tag require their own publication evidence.
