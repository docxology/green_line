# Method

## Staged reading

A read proceeds in three stages:

1. **Intake** (`green_line.intake`). Input is normalized fail-closed: blank
   descriptions are blocking defects; malformed labels and unreadable or
   future-dated observations become set-aside notes; counter-signal labels
   (certification, credential, resume language) are staged aside with an
   explanatory note and never counted. Nothing crashes on hostile input and
   no value is invented.
   Ordinary and dated observations share the same lexical exclusion rule;
   tags are normalized separately. Registry matching fields must already be
   lowercase and trimmed, required markers unique, and tags in the declared
   vocabulary. Definitions are rejected rather than silently rewritten.
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
records sorted by canonical ID, required-marker order preserved) and pinned by a SHA-256
digest of both the reading and the registry that produced it.
The native report stores a versioned context including the freshness window
and policy identity. Description prose remains restricted to its owner; a
digest and validity flag are archived, without proving authorship or truth.

## Typed scope and learner-owned review

Native reports distinguish no tags, unmatched tags, malformed tags, empty
registries and applied scope. Per-record relevance distinguishes fresh
required declarations, stale required declarations, unrelated-only labels
and no counted declarations. Under the retained global rule, adding only an
unrelated label can change NEEDS_MARKER to NEEDS_REWORK without changing a
required-marker surface. This is a declaration rule, not a judgment of capacity.

An optional next-review record holds a practice step, question, date and
what declaration would change the reading; it cannot upgrade marker coverage.
Optional source and practice-episode references remain assertions. The replay
context explicitly chooses whether episodes combine. Longitudinal comparison
requires pinned reports for the same declared subject and policy; it reports
added, removed, refreshed and still-missing declarations without ranking or
inferring improvement or decline. Missing reports support no comparison.
Refresh requires either a stale-to-present transition or established later
calendar dating; an unknown date is never ordered before a known date.
