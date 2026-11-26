# green_line

A capacity-under-development instrument: the green line of the docxology
line-set. It records what is deliberately still being learned — apprenticeships,
skills not yet mastered — with marker/counter-signal staging.

**Question:** What is still growing?

**Job:** Capacity under development: apprenticeships, skills deliberately not
yet mastered, with marker/counter-signal staging.

**What it is never:** A resume, a competence certification, or a virtue signal.
Observation labels matching the global case-insensitive substring policy are
staged aside with a note, never scored; this is lexical screening, not intent detection.

**Opus stage:** None — a stageless line is the designed outcome (all four
classical stages are allocated; see line_set `docs/extensibility.md`).

![green_line record-flow architecture: CultivationAttempt and dated Observation intake with counter-signal lexical staging, 11-record growth registry, cultivation surface reader, and STAGED / NEEDS_MARKER / NEEDS_REWORK / OUTSIDE_SCOPE verdicts and report envelopes](docs/assets/architecture-overview.svg)

## Usage

Install the locked environment with `uv sync --locked` from the repository
root, then run this example with `uv run python`.

```python
from green_line import CultivationAttempt, Observation, read_cultivation

reading = read_cultivation(
    CultivationAttempt(
        description="Practicing formal proof review with a mentor",
        tags=frozenset({"research", "teaching"}),
        dated_observations=(Observation("mentor", "2026-08-01"),),
    ),
    as_of="2026-08-29",
    max_observation_age_days=60,
)
print(reading.status.value)  # NEEDS_REWORK
```

Installation and development require Python 3.11 or later. `NEEDS_REWORK`
here describes missing marker declarations for the selected records.
`STAGED` describes full declared marker coverage at the review date.

## Documentation

Start with the [documentation index](docs/README.md). It links to installation,
verification, report and envelope contracts, and the pinned render commands.
Read the [manuscript](docs/manuscript/README.md) for the method, worked examples,
and limits. [Publication](docs/publication.md) identifies the source edition and
its archive policy.

## The Line Set

This instrument belongs to the [current Line Set declaration](https://github.com/docxology/line_set),
whose colorless Main reader holds the instruments apart. The Witness Register
is outside `LINE_SET` and co-registers report envelopes without aggregation.
Sources may be optional or access-controlled; the roster does not promise public
availability:

- [Black Line](https://github.com/docxology/black_line) — declared practice and evidence-label coverage
- [Golden Line](https://github.com/docxology/golden_line) — the aspiration and horizon registry
- [Red Line](https://github.com/docxology/red_line) — the cognitive-security registry of self-assessments
- [White Line](https://github.com/docxology/white_line) — the absence and omission ledger
- [Silver Line](https://github.com/docxology/silver_line) — the memory-and-succession instrument
- Violet Line — the consent ledger of affected parties; source access may be restricted
- [Blue Line](https://github.com/docxology/blue_line) — the stewardship instrument for maintained commitments
- Copper Line — dimensioned finite-resource allocation arithmetic and burden attribution, not learner progress or permission; source access may be restricted
- Iron Line — scenario-bound recorded recovery comparisons, not competence, reliability, or permission certification; source access may be restricted
- [The Line Set](https://github.com/docxology/line_set) — the cross-line set reader holding instruments apart
- [The Witness Register](https://github.com/docxology/witness_register) — co-registration without aggregation
