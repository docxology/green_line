# green_line

A capacity-under-development instrument: the green line of the docxology
line-set. It records what is deliberately still being learned — apprenticeships,
skills not yet mastered — with marker/counter-signal staging.

**Question:** What is still growing?

**Job:** Capacity under development: apprenticeships, skills deliberately not
yet mastered, with marker/counter-signal staging.

**What it is never:** A resume, a competence certification, or a virtue signal.
Observations phrased as certification or credential language are staged aside
by the intake with a note, never scored.

**Opus stage:** None — a stageless line is the designed outcome (all four
classical stages are allocated; see line_set `docs/extensibility.md`).

## Usage

```python
from green_line import CultivationAttempt, Observation, read_cultivation

reading = read_cultivation(
    CultivationAttempt(
        description="Practising formal proof review with a mentor",
        tags=frozenset({"research", "teaching"}),
        dated_observations=(Observation("mentor", "2026-08-01"),),
    ),
    as_of="2026-08-29",
    max_observation_age_days=60,
)
print(reading.status.value)
```

## Verify

```bash
uv sync
uv run pytest tests/ --cov=src --cov-report=term   # all green, cov >= 90
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
```

Standalone by contract: no sibling line, the reader, or the witness register
is needed for any of these commands. See STANDALONE.md.

## The Line Set

This work is one of ten in the Line Set family — eight instruments, their
cross-line reader, and the witness register that co-registers their report
envelopes without aggregation:

- [Black Line](https://github.com/docxology/black_line) — the practice registry of realized craft
- [Golden Line](https://github.com/docxology/golden_line) — the aspiration and horizon registry
- [Red Line](https://github.com/docxology/red_line) — the cognitive-security registry of self-assessments
- [White Line](https://github.com/docxology/white_line) — the absence and omission ledger
- [Silver Line](https://github.com/docxology/silver_line) — the memory-and-succession instrument
- [Violet Line](https://github.com/docxology/violet_line) — the consent ledger of affected parties
- [Blue Line](https://github.com/docxology/blue_line) — the stewardship instrument for maintained commitments
- [The Line Set](https://github.com/docxology/line_set) — the cross-line set reader holding instruments apart
- [The Witness Register](https://github.com/docxology/witness_register) — co-registration without aggregation
