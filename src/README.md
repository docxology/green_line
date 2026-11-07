# src

`src/green_line/` is the only package. `pyproject.toml` puts `.` and `src` on
`pytest`'s `pythonpath` and `scripts/` bootstraps the same path, so nothing here
needs installing before the gates run.

Runtime code is pure standard library at `requires-python >= 3.11`.
`tests/test_standalone_contract.py` retains a Python 3.10 syntax-only check
and rejects sibling-repository imports; it does not establish 3.10 runtime support.
