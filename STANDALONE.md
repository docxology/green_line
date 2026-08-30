# STANDALONE

This repository is standalone by contract. Every gate below runs with zero
siblings present (no black_line, golden_line, white_line, red_line, line_set,
or witness_register checkout):

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
project registered as `working/green_line` in that checkout's private sidecar.
This repo does not render PDFs itself and contains no render intermediates.
