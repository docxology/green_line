# green_line

The package. `__init__.py` is the public surface; every name in `__all__` must
resolve (`tests/test_public_api.py`).

| Module | Role |
| --- | --- |
| `enums.py` | `SignalStatus`, `GrowthStatus`, `GrowthKind` |
| `records.py` | record, attempt, observation and evaluation-context dataclasses |
| `model.py` | re-exports the typed record model from `records.py` and `enums.py` |
| `dates.py` | the pinned `YYYY-MM-DD` date grammar |
| `registry.py` | `GREEN_RECORDS`, `TAG_VOCABULARY`, `registry_ids` |
| `intake.py` | fail-closed normalization and counter-signal set-aside |
| `evaluator.py` | `read_cultivation`, `read_with_surfaces` |
| `evidence.py` | declaration policy, input snapshot, observation dispositions |
| `serialization.py` | canonical JSON, digests, `replay_reading` |
| `comparison.py` | declaration comparison without ranking or scores |
| `envelope.py` | `line.report-envelope/1.0` export, matching, validation |
| `formalism_ledger.py` | manuscript block ledger derivation |
| `examples.py` | worked and same-subject example bundles |
| `figures/` | deterministic SVG builders and the figure registry |
| `version.py` | the version authority |
