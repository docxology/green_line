"""The versioned Green Line growth-record registry.

Every entry names one capacity deliberately under development, the tags that
make it applicable, and the markers a reader could inspect. The registry is
a development instrument: it describes what is still growing and never
certifies competence, ranks people, or signals virtue.
"""

from __future__ import annotations

from .model import GreenRecord, GrowthKind

#: The reviewed tag vocabulary. Record tags outside this set are
#: unreviewable drift; the invariants battery enforces membership.
TAG_VOCABULARY: frozenset[str] = frozenset(
    {"analysis", "data", "engineering", "research", "teaching", "writing"}
)


GREEN_RECORDS: tuple[GreenRecord, ...] = (
    GreenRecord(
        "apprentice-review",
        "Review under a named mentor",
        "Practise the skill with review from someone who already carries it.",
        frozenset({"research", "analysis", "writing"}),
        ("mentor", "session_log"),
        GrowthKind.APPRENTICESHIP,
    ),
    GreenRecord(
        "deliberate-gaps",
        "Name the skills deliberately not yet mastered",
        "Record what is being learned on purpose and what is being deferred.",
        frozenset({"research", "engineering", "teaching"}),
        ("gap_list", "priority_note"),
        GrowthKind.APPRENTICESHIP,
    ),
    GreenRecord(
        "staged-practice",
        "Stage practice before mastery claims",
        "Keep marker observations at the practice stage; resist premature counter-signals.",
        frozenset({"engineering", "analysis", "teaching"}),
        ("practice_log", "stage_note"),
        GrowthKind.PRACTICE,
    ),
    GreenRecord(
        "smallest-next-step",
        "Use the smallest next step that grows the capacity",
        "Do not add machinery whose output cannot change what is being learned.",
        frozenset({"engineering", "analysis"}),
        ("step", "decision"),
        GrowthKind.METHOD,
    ),
    GreenRecord(
        "failure-tolerant-drills",
        "Make failure conditions explicit in practice",
        "Record what would show the practice is not taking hold.",
        frozenset({"engineering", "research", "analysis"}),
        ("failure", "drill"),
        GrowthKind.VERIFICATION,
    ),
    GreenRecord(
        "teach-to-learn",
        "Leave a teaching trace another learner can follow",
        "A learner should recover the purpose, next step, and evidence without private context.",
        frozenset({"teaching", "writing", "research"}),
        ("teaching_trace", "handoff"),
        GrowthKind.COMMUNICATION,
    ),
    GreenRecord(
        "versioned-practice",
        "Keep practice increments small and reviewable",
        "Record each practice increment so its history can be read and revisited.",
        frozenset({"engineering", "writing"}),
        ("commit", "diff"),
        GrowthKind.STEWARDSHIP,
    ),
    GreenRecord(
        "stated-uncertainty",
        "State what is not yet known alongside what is practised",
        "A practice note without its uncertainty can overstate the capacity.",
        frozenset({"research", "analysis"}),
        ("uncertainty", "limits"),
        GrowthKind.VERIFICATION,
    ),
    GreenRecord(
        "counter-signal-watch",
        "Watch for drift toward certification or resume language",
        "Flag observations phrased as credentials; the intake stages them aside.",
        frozenset({"research", "teaching", "writing"}),
        ("counter_signal", "watch_note"),
        GrowthKind.STEWARDSHIP,
    ),
    GreenRecord(
        "peer-comparison-resisted",
        "Invite review without ranking against peers",
        "A comparison against other learners can turn growth records into a leaderboard.",
        frozenset({"teaching", "research", "writing"}),
        ("reviewer", "review_note"),
        GrowthKind.COMMUNICATION,
    ),
    GreenRecord(
        "data-origin-explicit",
        "Keep practice-data origin and transformations explicit",
        "State where each practice dataset came from and which transforms produced it.",
        frozenset({"data", "analysis"}),
        ("data_origin", "transform_log"),
        GrowthKind.PRACTICE,
    ),
)


def registry_ids() -> tuple[str, ...]:
    """Return registry ids in declaration order."""

    return tuple(record.id for record in GREEN_RECORDS)
