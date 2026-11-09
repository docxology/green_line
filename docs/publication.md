# Publication and versioned releases

## Source citation and archive objects

Source edition **0.5.0**, dated November 9, 2026. Cite inspected source
through <https://github.com/docxology/green_line> with its version and exact revision.
A source declaration, GitHub Release, source archive, and rendered manuscript
are separate objects; each needs its own publication and qualification evidence.

Previously verified source archive: **0.4.0** /
<https://doi.org/10.5281/zenodo.24069457>. This identifies that SOURCE ZIP only,
not this later source or a standalone rendered manuscript. The older retained
title/DOI reference (`10.5281/zenodo.22833492`) remains historical; its exact
edition version is not established here.

## Release procedure

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

The current source is cited by repository until its exact edition/object is
independently verified. Historical DOIs belong only to their earlier editions,
not to this candidate's own CFF identifiers or active `publication.doi`.

Keep previously verified identifiers assigned to their historical editions.
Manual reserve-first publication remains an alternative workflow; it is not a
prerequisite for the explicitly authorized automatic integration below.

After independent read-only audit, commit, create an annotated `vX.Y.Z` tag,
and fast-forward push main and tag through the GitVault repository lease.
Verify remote main and the peeled tag against the authorized release commit.
Inspect authenticated hooks immediately before creating a GitHub Release.
The November 8, 2026 owner authorization covered that campaign's existing public
Zenodo integrations; it is not blanket future authority. For a future
owner-authorized release, retain the authorized existing public integration and
verify each resulting archive's repository, tag, version, and contents.
A reserved DOI is not a published deposit. Never prefill a DOI or amend an
immutable tag to insert one learned afterward. Without explicit archive
authority, a Zenodo hook or inconclusive inspection still blocks the Release.
PyPI, private-source disclosure, and new private-sibling deposit automation
remain unauthorized.
