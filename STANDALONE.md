# STANDALONE

This repository is standalone by contract. Every gate below runs with zero
siblings present (no black_line, golden_line, white_line, red_line, line_set,
silver_line, violet_line, blue_line or witness_register checkout):

```bash
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
```

Coverage may not depend on siblings. Envelope tests validate against a frozen
schema copy of the register's field structure; if a sibling envelope exists
on disk it is parsed read-only as an additional check, and its absence is an
outcome, never an exception.

## Rendering

Manuscript rendering happens through the external template checkout, with the
project registered as `projects/working/green_line` in an isolated export of
the engine's pinned `origin/main`. No family sibling is needed. The engine
is external build tooling; it is not a Green runtime dependency. Never use
an active sibling engine's dirty checkout as the release engine. See
`docs/publication.md`; render products stay in ignored `output/`.
