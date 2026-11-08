# Publication and versioned releases

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

Keep previously verified identifiers assigned to their historical editions.
Manual reserve-first publication remains an alternative workflow; it is not a
prerequisite for the explicitly authorized automatic integration below.

After independent read-only audit, commit, create an annotated `vX.Y.Z` tag,
and fast-forward push main and tag through the GitVault repository lease.
Verify both with `git ls-remote`. Inspect authenticated hooks immediately before
creating a GitHub Release. On November 8, 2026, the owner authorized this campaign
with the existing public repositories' Zenodo hooks left active. Retain those
integrations and verify each resulting archive's repository, tag, version, and
contents. Never prefill a DOI or amend an immutable tag to insert one learned
afterward. Without explicit archive authority, a Zenodo hook or inconclusive
inspection still blocks the Release. PyPI, private-source disclosure, and new
private-sibling deposit automation remain unauthorized.
