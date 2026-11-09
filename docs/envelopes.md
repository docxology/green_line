# Envelope checks and export

The shared `line.report-envelope/1.0` field set is unchanged.
`report_matches(envelope, reading)` checks the native report pointer, date,
registry digest and status. The legacy `envelope_matches_reading` delegates
to it for compatibility; neither validates envelope identity or provenance.

`reading_envelope` is a Green-only producer: it requires present native context
with `instrument_id="green_line"` before constructing either export profile.
Missing or foreign native identity raises `ValueError`; a custom native
instrument must not be relabeled Green. Custom registries using Green's built-in
vocabulary and Green identity remain exportable without a shipped-registry
digest restriction. Native custom instruments still read and replay in full.
This producer guard does not turn pointer-only `report_matches` or a
caller-constructed envelope into authenticated instrument provenance.

`validate_envelope` returns explicit structural/identity errors: foreign line
IDs, unsupported schemas, malformed dates/digests/versions, changed nonclaims
and unbounded references are invalid Green envelopes. `strict=True` also
requires a nonblank subject and at least one provenance reference. Ordinary
local reads may be intentionally unnamed (`subject_id=""`); this is a local
profile, not an identified export. Reference containers cannot be text,
bytes or mappings. References are sorted before emission; their syntax does
not establish that they resolve or are accurate.
Subject and reference strings must be usable Unicode in both profiles; malformed
text is rejected rather than escaped into an envelope that cannot encode as UTF-8.

`provenance_digest` binds the canonical native report and complete declared
envelope, including subject, references, version and nonclaims. It changes
when those declarations change even if `report_matches` stays true. A digest
is an equality check, not source verification or authenticated authorship.

`data/envelopes/manifest.json` describes the historical 0.2.0 edition: each
retained report, caller-declared producer commit, source file hashes and explicit
invocation context. Native report files contain exactly the canonical bytes,
with no trailing newline, so their whole-file SHA-256 equals `report_ref`.
Historical byte reproduction requires the matching source checkout and hashes,
not just passing its SHA to today's generator. `--source-commit` labels the
running source; it does not load or verify a historical checkout. Both
`--source-commit` and `--output-dir` are required: no implicit HEAD declaration
or historical output directory is selected. Generate 0.4.0 into
`data/current-envelopes/0.4.0/` only after its producer source is committed,
using that actual full SHA and a new empty destination; see
the [edition recipe](../data/envelopes/README.md). The named same-subject fixture
is used directly; `gap_list` is reference-only, not a scored declaration.
Its historical witness subject remains pinned to its original version.

Siblings may co-register native status without interpreting, comparing or
aggregating it. The local frozen field specification remains the standalone
contract; changing a sibling copy is its maintainer's work.
