# AGENTS.md — `green_line/data/envelopes`

## Scope
- The generated envelope bundle and its manifest, committed so downstream
  consumers can read it without running this repository's code.
- Nothing here is hand-edited.

## Layout
- `green_line_worked.json`, `green_line_same_subject.json` — canonical envelopes.
- `*.report.json` — the matching native reports, hashed by the envelope's
  `report_ref`.
- `manifest.json` — source commit, source hashes, evaluation context and file
  hashes.

## Gotchas
- Regenerate with `uv run python scripts/gen_envelopes.py`; use `--output-dir`
  and `--source-commit` to check byte identity against the pinned commit, which
  must be a full 40-character SHA.
- `tests/test_review_bundles.py` regenerates the bundle from the manifest's
  pinned `source_commit` and requires byte identity; `test_witness_surfaces.py`
  checks the envelope field shape, and `test_audit_regressions.py` pins this
  README's required terms. A stale manifest fails.
- Never write into a sibling repository from here.
