# AGENTS.md — `green_line/src/green_line`

## Scope
- The instrument's runtime package: pure standard library, Python >= 3.10.
  Nothing here reads a sibling repository or the network.

## Layout
- `__init__.py` — the public surface (`__all__`); every name must resolve.
- `enums.py`, `records.py`, `model.py`, `dates.py` — vocabulary and grammar.
- `registry.py`, `intake.py`, `evaluator.py`, `evidence.py` — the staged read.
- `serialization.py`, `comparison.py`, `envelope.py` — canonical output.
- `formalism_ledger.py`, `examples.py`, `figures/`, `version.py` — derived data.

## Gotchas
- Public names are exercised by `tests/test_public_api.py`; adding, renaming or
  dropping one is a contract change, so update the tests and docs in the same
  commit.
- `version.py` is the single version authority, checked against
  `pyproject.toml`, `CHANGELOG.md`, `CITATION.cff` and `.zenodo.json`.
- Intake and evaluation fail closed: an unknown or malformed collection is set
  aside with a note, never silently accepted.
