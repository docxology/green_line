# AGENTS.md — `green_line/docs/releases`

## Scope
- Release packets for this repository's own versions. Published packets are
  historical records and are not rewritten.

## Layout
- `vX.Y.Z.md`, `vX.Y.Z.audit.md`, `vX.Y.Z.validation.json` per release.

## Gotchas
- Record the commands actually run and the measured results; a packet claiming
  an unrun check is worse than no packet.
- `tests/test_version_sync.py` pins the active version and DOI across
  `pyproject.toml`, `CHANGELOG.md`, `CITATION.cff`, `.zenodo.json` and
  `docs/manuscript/config.yaml`; release edits keep them agreeing.
- The Zenodo step is reserve-first and performed by the maintainer: never guess,
  reserve or relabel a DOI in source.
