# Native reports and replay

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

Description prose is not archived. Its trimmed-text digest and validity flag
are enough for replay, since its wording does not affect marker matching.
The owner may retain the original description in restricted storage; a
public digest neither grants access nor proves the original text. Optional
commentary, source references and episode IDs are caller assertions and are
public if exported: omit sensitive values. Input normalization deliberately
forgets the content of malformed non-text tokens while retaining their
malformed classification. Reports of invalid registries carry diagnostics
but cannot replay a registry that could not be serialized.

Custom registries using the built-in vocabulary remain supported. A distinct
vocabulary requires `registry_vocabulary=frozenset(...)` and a distinct
`instrument_id`; both become replay context. Definitions must be lowercase
and trimmed in matching fields, tags must belong to that vocabulary, and
required markers must be unique. No definition is silently repaired.

Undated declarations remain current by default. Opt-in
`undated_policy="dated_only"` excludes them with UNDATED_PROFILE dispositions;
the chosen profile is versioned in replay context and never inferred.
The finding rule retains the existing
global `bool(fresh or stale)` policy: no observations gives NEEDS_MARKER;
adding unrelated `banana` gives NEEDS_REWORK for a missing `mentor`. This is
an explicit declaration rule, not evidence of a change in capacity.
