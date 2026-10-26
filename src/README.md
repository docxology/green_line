# src

`src/green_line/` is the only package. `pyproject.toml` puts `.` and `src` on
`pytest`'s `pythonpath` and `scripts/` bootstraps the same path, so nothing here
needs installing before the gates run.

Runtime code is pure standard library at `requires-python >= 3.10`;
`tests/test_standalone_contract.py` re-parses every source file as Python 3.10
syntax and rejects any sibling-repository import.
