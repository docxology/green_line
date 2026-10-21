# Publication and reserve-first releases

Release code only when the full suite meets its coverage floor, lint and
type checks pass, examples replay and regenerate, registry/claim/formalism
ledgers agree, figures build, and publication versions agree. Runtime remains
standard library only; external rendering and type-checking tools use their
own GitVault environments. Record exact commands and measured results in a
dated `docs/releases/vX.Y.Z.md` packet, synchronized with CHANGELOG and all
active version declarations. Historical subject versions and schema versions
have separate meanings and are not rewritten.

Render PDF and HTML from the final manuscript through an isolated export of
`template`'s `origin/main`, pin its SHA in the release packet, inspect the
rendered outputs, and record whole-file checksums. Do not change the engine
to make this release pass. Render failures block release and belong in the
report. Keep artifacts and intermediates under GitVault in ignored `output/`.

The active DOI is the last verified version DOI already in CITATION and the
manuscript config. It is not a DOI for a newly tagged version. Do not guess
or reserve a DOI in source, and do not relabel an old DOI as the new version.

Daniel performs the Zenodo step: create a new version of the existing record,
reserve its DOI first, update the publication metadata and rendered edition
with that reserved DOI, then deposit/publish the matching artifacts. Keep the
existing DOI until that reservation is verified.

After independent read-only audit, commit, create an annotated `vX.Y.Z` tag,
and fast-forward push main and tag through the GitVault repository lease.
Verify both with `git ls-remote`. Inspect GitHub hooks before creating a
GitHub Release: any Zenodo webhook, or an inconclusive hook check, means no
Release object. A Release on a linked repository could mint a permanent DOI
outside this reserve-first procedure. An explicit empty hook list permits a
GitHub Release using the packet as its notes.
