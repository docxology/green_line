# Learner-owned review and comparisons

`NextReview` optionally records `next_practice_step`, `review_question`,
`review_on` and `evidence_would_change`. No date is inferred and no promise of
improvement is made. Attach it as `CultivationAttempt(next_review=...)`.
It changes input identity but never findings or coverage status.

`Observation` separates the scored marker ID (`label`) from optional human
`commentary`, `source_ref` and `episode_id`. Commentary is not a scored
marker; the lexical substring rule still screens every marker label. Source
references are declarations, never proof that an artifact exists.

The replay context always records `episode_policy`. `combine_declared`
allows declared markers across episodes to contribute coverage, without
claiming a coherent apprenticeship. `single_episode` sets counted
declarations aside on conflicting episode IDs, including a mixture of named
and unnamed episodes. It never guesses which episode to prefer.

`compare_readings(earlier, earlier_envelope, later, later_envelope)` requires
valid identified envelopes, matching native reports, the same subject,
registry and evaluation policy, and chronological review dates. It returns
pinned report references plus added, removed, refreshed and still-missing
record/marker pairs. A refreshed marker was previously stale or has an
established later accepted declaration date, compared as a calendar date.
An unknown date stays unknown: undated-to-dated is not evidence of refresh.
Removed means no longer declared fresh, not loss
of capacity. Missing reports are rejected without inferring decline. No peer
comparison, score, ranking or skill-change inference is available.
