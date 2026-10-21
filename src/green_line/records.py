"""Frozen record types for growth records, cultivation attempts, and reads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .enums import GrowthKind, GrowthStatus, SignalStatus


@dataclass(frozen=True)
class GreenRecord:
    """One capacity under development: a record, its tags, and required markers.

    ``counter_signals`` are labels whose presence indicates the record has
    drifted toward what it must never become (a resume, a certification, a
    virtue signal); the intake stages them aside with notes rather than
    scoring them.
    """

    id: str
    title: str
    wire: str
    tags: frozenset[str]
    required_markers: tuple[str, ...]
    kind: GrowthKind = GrowthKind.PRACTICE

    def canonical(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "wire": self.wire,
            "tags": sorted(self.tags),
            "required_markers": list(self.required_markers),
            "kind": self.kind.value,
        }


@dataclass(frozen=True)
class Observation:
    """A dated declaration pointing to a growth observation.

    ``noted_on`` is an ISO date string recording when the observation was
    last recorded. Undated observations are treated as current declarations;
    the evaluator does not independently verify them.
    """

    label: str
    noted_on: str | None = None
    source_ref: str | None = None
    episode_id: str | None = None
    commentary: str | None = None


@dataclass(frozen=True)
class CultivationAttempt:
    """A self-declared cultivation item assessed against Green records."""

    description: str
    tags: frozenset[str] = frozenset()
    observations: frozenset[str] = frozenset()
    dated_observations: tuple[Observation, ...] = ()
    next_review: NextReview | None = None


@dataclass(frozen=True)
class NextReview:
    next_practice_step: str | None = None
    review_question: str | None = None
    review_on: str | None = None
    evidence_would_change: str | None = None

    def __post_init__(self) -> None:
        for field in ("next_practice_step", "review_question", "review_on", "evidence_would_change"):
            value = getattr(self, field)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field} must be nonblank text or None")
        if self.review_on is not None and date.fromisoformat(self.review_on).isoformat() != self.review_on:
            raise ValueError("review_on must be a canonical ISO date")


@dataclass(frozen=True)
class RecordFinding:
    """One record-level signal status with a reviewable reason trail."""

    record_id: str
    status: SignalStatus
    reasons: tuple[str, ...]
    declaration_relevance: str = ""


@dataclass(frozen=True)
class MarkerSurfaces:
    """One record's present, missing, and stale required markers."""

    record_id: str
    present: tuple[str, ...]
    missing: tuple[str, ...]
    stale: tuple[str, ...]


@dataclass(frozen=True)
class GreenReading:
    """A complete read of a cultivation attempt.

    ``intake_notes`` records normalization and set-aside observations.
    ``read_as_of`` is the ISO review date the read used, and
    ``registry_digest`` pins the exact record content that produced it.
    """

    status: GrowthStatus
    findings: tuple[RecordFinding, ...]
    intake_notes: tuple[str, ...] = ()
    read_as_of: str = ""
    registry_digest: str = ""
    context: EvaluationContext | None = None
    normalized_input: str = ""
    registry_snapshot: str = ""
    intake_dispositions: tuple[IntakeDisposition, ...] = ()
    marker_surfaces: tuple[MarkerSurfaces, ...] = ()
    marker_evidence: tuple[MarkerEvidence, ...] = ()
    scope_reason: str = ""


@dataclass(frozen=True)
class EvaluationContext:
    max_observation_age_days: int | None
    evaluator_version: str
    policy_version: str
    counter_signal_policy_digest: str
    input_digest: str
    instrument_id: str
    registry_vocabulary: tuple[str, ...]
    episode_policy: str = "combine_declared"
    undated_policy: str = "current"


@dataclass(frozen=True)
class IntakeDisposition:
    label: str | None
    channel: str
    noted_on: str | None
    disposition: str
    reason_code: str
    source_ref: str | None = None
    episode_id: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class MarkerEvidence:
    record_id: str
    label: str
    disposition: str
    declarations: tuple[IntakeDisposition, ...]
