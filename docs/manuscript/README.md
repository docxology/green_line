# Green Line manuscript

This directory holds the authored paper, [paper metadata](config.yaml),
[bibliography](references.bib), and [publication status](MANUSCRIPT_STATUS.md).

1. [Abstract](00_abstract.md)
2. [Introduction](01_introduction.md)
3. [Method](02_method.md)
4. [Formalism](03_formalism.md)
5. [Examples](04_examples.md)
6. [Limits](05_limits.md)
7. [Conclusion](06_conclusion.md)
8. [References](99_references.md)

Formalism declarations use `{#def:...}` and `{#prop:...}` labels. Regenerate
`data/formalism_claim_ledger.json` from the project root with
`uv run python scripts/gen_formalism_ledger.py` after changing declaration
labels or source locations. Run `uv run pytest tests/test_formalism_claim_ledger.py`
to check the updated bindings.

The [development guide](../development.md#render-and-validate-the-manuscript)
gives the cover build and pinned render and validation commands.
