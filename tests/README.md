# tests

Run from the repository root:
`uv run pytest tests/ --cov=src --cov-report=term` (coverage floor 90, set in
`pyproject.toml`).

The suite uses real data and real temp directories and no mocking framework
(`test_no_mocks.py`). Static gates reject empty scan sets and prove there is no
sibling import anywhere in `src/`, `tests/` or `scripts/`
(`test_standalone_contract.py`, `test_audit_regressions.py`). Metadata tests
read `pyproject.toml` with standard-library `tomllib`, so the developer suite
needs Python >= 3.11 while the runtime stays >= 3.10.
