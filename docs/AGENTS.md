# AGENTS.md — `green_line/docs`

## Scope
- Committed documentation for this instrument. No document here reads or writes
  a sibling repository, and no command here requires one.
- Claims stay narrow and first person: `docs/claim_boundaries.md` is the
  register of record.

## Layout
- `claim_boundaries.md`, `extensibility.md` — boundaries and extension rules.
- `development.md`, `publication.md` — setup/gates and the release procedure.
- `envelopes.md`, `native_reports.md`, `practice_records.md` — output contracts.
- `review_20261020.md` — implementation record for the 0.2.0 review.
- `releases/`, `manuscript/` — release packets and the paper.

## Gotchas
- Every command in these files runs from the repository root with `uv`; keep the
  README and AGENTS verify blocks in sync with the real scripts.
- Never hardcode a number the code can derive: ledgers, digests and counts are
  re-derived by tests, so a stale claim fails the suite.
- Render products stay in git-ignored `output/`; never commit a built PDF/HTML.
