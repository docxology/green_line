# releases

One packet per released version, all three files version-named:

- `vX.Y.Z.md` — the exact commands run and the measured results.
- `vX.Y.Z.audit.md` — findings from the independent read-only audit.
- `vX.Y.Z.validation.json` — machine-readable validation record.

`docs/publication.md` defines the reserve-first procedure. `tests/test_version_sync.py`
keeps `pyproject.toml`, `src/green_line/version.py`, `CHANGELOG.md`,
`CITATION.cff`, `.zenodo.json` and `docs/manuscript/config.yaml` in agreement,
including the last verified DOI.
