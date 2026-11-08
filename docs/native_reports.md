# Native reports and replay

Dates use exactly the ASCII `YYYY-MM-DD` grammar on every supported runtime.
Compact and week-date forms are excluded even where Python accepts them.
Declaration policy 2.1 pins this grammar; earlier policy identities are
explicitly rejected rather than silently reinterpreted.

`green.native-reading/2.0` replaces the outcome-only `1.0` report. Old bytes
remain historical records; `replay_reading` explicitly rejects unsupported
schemas and evaluator/policy versions rather than guessing a migration.
Regenerate a report from retained declarations if a new read is wanted.

`canonical_reading` archives the normalized input, registry content, complete
evaluation context, typed intake dispositions, marker evidence, surfaces,
scope reason and prose findings. `replay_reading(report)` uses those pinned
values and checks the entire resulting report, including excluded inputs.
Required-marker tuple order is meaningful for presentation and registry
identity; registry record order is not. Findings sort by record ID.

- `reading_digest` identifies native report bytes.
- `context.input_digest` identifies the canonical normalized input.
- `registry_digest` identifies record content; vocabulary and instrument
  identity are separately retained in context.
- Context records the window, evaluator version, lexical policy version and
  digest, declared vocabulary, instrument ID, and episode policy. A different
  window is visible even when it produces the same status.

Registry title and instruction wording are content, not decoration. The current
American-English registry and worked-attempt description produce new registry,
input, report, envelope, and provenance identities even where findings stay the
same. The registry digest is the native content revision marker; schema 2.0 and
declaration policy 2.1 remain unchanged. Current reports pin evaluator 0.4.0,
including its malformed-Unicode intake behavior. Retained historical reports
require their original producer for replay; the current evaluator rejects an
older identity rather than silently migrating or relabeling the report.

Description prose is not archived. Its trimmed-text digest and validity flag
are enough for replay, since its wording does not affect marker matching.
The owner may retain the original description in restricted storage; a
public digest neither grants access nor proves the original text. Optional
commentary, source references and episode IDs are caller assertions and are
public if exported: omit sensitive values. Input normalization deliberately
forgets the content of malformed non-text tokens while retaining their
malformed classification. Reports of invalid registries carry diagnostics
but cannot replay a registry that could not be serialized.

Strings containing surrogate code units are unusable Unicode, not replacement
characters, literal backslash-u text, or valid non-BMP scalars. A malformed
description blocks findings with `INVALID_DESCRIPTION`/`NEEDS_REWORK`. Its
`description_digest` fingerprints canonical ASCII JSON with the sorted keys
`{"code_units":[...],"schema":"green.rejected-text/1"}` using SHA-256; the
integer code units describe the original complete string, not its trimmed form.
Neither description prose nor those code units are published. Other malformed
strings become `{"rejected_text_digest":"..."}` in normalized input under the
same fingerprint rule. Distinct rejected strings retain deterministic input
identities without leaking unencodable text.

These tokens retain exclusion classifications through complete replay: labels
are `MALFORMED_LABEL`, dates `INVALID_DATE`, and optional attribution/commentary
`MALFORMED_METADATA`. Malformed plans retain a `malformed` flag and cannot add
coverage. Usable labels retain counter-signal-before-metadata-before-date
precedence. Valid strings keep the existing non-ASCII canonical bytes without
repair, normalization, or global ASCII escaping. Instrument/vocabulary
configuration with unusable Unicode raises explicitly; malformed registry text
produces an `INVALID_REGISTRY` diagnostic without unsafe text echoes.
Replay also rejects archives whose decoded strings contain surrogate code units
before hashing or derivation, including archives that hide them in JSON escapes.
Fingerprint tokens remain ordinary strict-UTF-8 JSON and need no raw-text decoder.

Custom registries using the built-in vocabulary remain supported. A distinct
vocabulary requires `registry_vocabulary=frozenset(...)` and a distinct
`instrument_id`; both become replay context. Definitions must be lowercase
and trimmed in matching fields, tags must belong to that vocabulary, and
required markers must be unique. No definition is silently repaired.
Native custom instruments, including valid non-ASCII identities, canonicalize
and replay normally. The Green-only envelope producer rejects missing or foreign
native context in both export profiles; a custom registry using the built-in
vocabulary and `instrument_id="green_line"` remains exportable.

Undated declarations remain current by default. Opt-in
`undated_policy="dated_only"` excludes them with UNDATED_PROFILE dispositions;
the chosen profile is versioned in replay context and never inferred.
The finding rule retains the existing
global `bool(fresh or stale)` policy: no observations gives NEEDS_MARKER;
adding unrelated `banana` gives NEEDS_REWORK for a missing `mentor`. This is
an explicit declaration rule, not evidence of a change in capacity.
