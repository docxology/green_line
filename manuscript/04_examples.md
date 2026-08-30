# Examples

## A worked read

A learner declares an attempt tagged `research` and `teaching` with
observations `mentor` and `session_log` dated inside the review window. The
records `apprentice-review`, `deliberate-gaps`, `staged-practice`,
`teach-to-learn`, and `stated-uncertainty` apply (by tag intersection).
`apprentice-review` reads STAGED by the finding rule [@def:finding-rule];
the others read NEEDS_MARKER because their markers were not declared. The
overall status follows the aggregation rule [@def:aggregation]. The overall status is NEEDS_MARKER: gaps ask for
practice, not judgment.

## A counter-signal

The same attempt with an added dated observation `certified as expert` gets
that observation staged aside with a note; the read is unchanged, because
certification language is exactly the drift the line refuses to score.

Counter-signal staging follows [@def:counter-signal]; the empty-scan-set
outcome is stated by [@prop:empty-scope], and determinism by [@prop:determinism].
