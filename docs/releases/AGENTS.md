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
- Follow `docs/publication.md`: the owner authorized the existing automatic
  GitHub-to-Zenodo hooks for this campaign. Preserve them and verify resulting
  archives; never guess or reserve a DOI in source, relabel an old DOI, or amend
  an immutable tag for an identifier learned afterward.
