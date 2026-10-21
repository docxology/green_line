# Envelope checks and export

The shared `line.report-envelope/1.0` field set is unchanged.
`report_matches(envelope, reading)` checks the native report pointer, date,
registry digest and status. The legacy `envelope_matches_reading` delegates
to it for compatibility; neither validates envelope identity or provenance.

`validate_envelope` returns explicit structural/identity errors: foreign line
IDs, unsupported schemas, malformed dates/digests/versions, changed nonclaims
and unbounded references are invalid Green envelopes. `strict=True` also
requires a nonblank subject and at least one provenance reference. Ordinary
local reads may be intentionally unnamed (`subject_id=""`); this is a local
profile, not an identified export. Reference containers cannot be text,
bytes or mappings. References are sorted before emission; their syntax does
not establish that they resolve or are accurate.

`provenance_digest` binds the canonical native report and complete declared
envelope, including subject, references, version and nonclaims. It changes
when those declarations change even if `report_matches` stays true. A digest
is an equality check, not source verification or authenticated authorship.

`data/envelopes/manifest.json` binds each envelope to the retained report,
source commit, source file hashes and explicit invocation context. Native
report files contain exactly the canonical bytes, with no trailing newline,
so their whole-file SHA-256 equals `report_ref`. Regenerate into an empty
directory to check byte identity. The named same-subject fixture is used
directly; `gap_list` is explicitly reference-only, not a scored declaration.
Its historic witness subject remains pinned to its original version.

Siblings may co-register native status without interpreting, comparing or
aggregating it. The local frozen field specification remains the standalone
contract; changing a sibling copy is its maintainer's work.
