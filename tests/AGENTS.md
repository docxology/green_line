# AGENTS.md — `green_line/tests`

## Scope
- The committed suite for this repository only. Siblings stay untouched, and a
  missing sibling checkout is an outcome, never an exception.

## Layout
- `conftest.py` — real fixtures plus the optional `witness_root` sibling path.
- `test_intake.py`, `test_evaluator.py`, `test_registry.py`, `test_invariants.py`
  — staged read and registry behaviour.
- `test_serialization.py`, `test_envelope.py`, `test_witness_surfaces.py` —
  canonical output, envelope shape and frozen sibling field copies.
- `test_review_*.py`, `test_audit_regressions.py` — the 2026-10-20 review items
  and the audit corrections.
- `test_claim_ledger.py`, `test_formalism_claim_ledger.py`,
  `test_binding_declaration.py` — ledger and prepared-input gates.
- `test_standalone_contract.py`, `test_no_mocks.py`, `test_installed_wheel.py`
  — boundary, policy and packaging scans.
- `test_public_api.py`, `test_version_sync.py`, `test_docs_recipes.py`,
  `test_scripts_cli.py`, `test_figures.py` — API, version and CLI contracts.

## Gotchas
- No mocking framework: use real temp directories and fail-closed callables.
- An empty scan set must fail; `test_audit_regressions.py` re-points `ROOT` at a
  temporary tree to prove it.
- Metadata tests import `tomllib`, so the suite needs Python >= 3.11 even though
  the runtime supports 3.10.
