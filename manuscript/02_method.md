# Method

## Staged reading

A read proceeds in three stages:

1. **Intake** (`green_line.intake`). Input is normalized fail-closed: blank
   descriptions are blocking defects; malformed labels and unreadable or
   future-dated observations become set-aside notes; counter-signal labels
   (certification, credential, resume language) are staged aside with an
   explanatory note and never counted. Nothing crashes on hostile input and
   no value is invented.
2. **Matching** (`green_line.evaluator`). Growth records whose tags intersect
   the attempt's declared tags apply. An empty intersection is the outcome
   `OUTSIDE_SCOPE`, not an exception.
3. **Projection** (`green_line.evaluator`). Each applied record's required
   markers are split into present, missing, and stale surfaces; the status
   projection selects the most demanding reading and the reasons trail
   preserves what the projection compresses.

## Statuses

`STAGED` — all required markers fresh. `NEEDS_MARKER` — gaps are only stale
markers needing refresh, or nothing was declared. `NEEDS_REWORK` — fresh
markers are missing, or a blocking intake defect fired. `OUTSIDE_SCOPE` — no
record applied.

## Determinism

Every read is a pure function of the attempt, the registry, and the review
configuration. Reads are serialized canonically (sorted keys, declaration
order preserved with explicit sorts before emit) and pinned by a SHA-256
digest of both the reading and the registry that produced it.
