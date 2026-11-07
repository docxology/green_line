# AGENTS.md — `green_line/data/envelopes`

## Scope
- The historical generated 0.2.0 envelope bundle and its manifest, committed so
  downstream consumers can read it without running this repository's code.
- Generated JSON bytes and producer pins stay unchanged; current editions use
  a new destination. Documentation may clarify the archive's meaning.

## Layout
- `green_line_worked.json`, `green_line_same_subject.json` — canonical envelopes.
- `*.report.json` — the matching native reports, hashed by the envelope's
  `report_ref`.
- `manifest.json` — source commit, source hashes, evaluation context and file
  hashes.

## Gotchas
- Historical byte reproduction requires the matching recorded source checkout
  and hashes before invoking `scripts/gen_envelopes.py --output-dir <empty-directory>
  --source-commit <manifest-source-sha>`. The flag only labels the running producer;
  it neither loads nor verifies that commit.
- A new edition needs its actual committed producer source and a new empty
  destination, for example `output/example-bundles/<actual-producer-sha>`.
  Never omit `--output-dir` for a new edition: the default overwrites this archive.
- `tests/test_review_bundles.py` separates current generation from historical
  hash integrity and replay; historical source hashes need not match current code.
  `test_witness_surfaces.py` checks the frozen envelope field shape.
- Never write into a sibling repository from here.
