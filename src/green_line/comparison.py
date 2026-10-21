from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .records import GreenReading, MarkerEvidence
from .envelope import ReadingEnvelope, report_matches, validate_envelope
from .serialization import reading_digest
from .dates import parse_iso_date


def _latest_known_date(evidence: MarkerEvidence) -> date | None:
    accepted = tuple(d for d in evidence.declarations if d.disposition == "accepted")
    if not accepted or any(d.noted_on is None for d in accepted):
        return None
    return max(parse_iso_date(d.noted_on) for d in accepted)


@dataclass(frozen=True)
class DeclarationComparison:
    subject_id: str
    earlier_report_ref: str
    later_report_ref: str
    added: tuple[tuple[str, str], ...]
    removed: tuple[tuple[str, str], ...]
    refreshed: tuple[tuple[str, str], ...]
    still_missing: tuple[tuple[str, str], ...]


def compare_readings(earlier: GreenReading, earlier_envelope: ReadingEnvelope,
                     later: GreenReading, later_envelope: ReadingEnvelope) -> DeclarationComparison:
    if not isinstance(earlier, GreenReading) or not isinstance(later, GreenReading):
        raise ValueError("two pinned reports are required; absence is not decline")
    for reading, envelope in ((earlier, earlier_envelope), (later, later_envelope)):
        if validate_envelope(envelope, strict=True) or not report_matches(envelope, reading):
            raise ValueError("invalid envelope or report mismatch")
    if earlier_envelope.subject_id != later_envelope.subject_id:
        raise ValueError("comparison requires the same declared subject")
    if (earlier.registry_digest != later.registry_digest or earlier.context is None
            or later.context is None):
        raise ValueError("comparison requires the same pinned registry and context")
    left, right = earlier.context, later.context
    if (left.max_observation_age_days, left.policy_version, left.counter_signal_policy_digest,
        left.evaluator_version, left.instrument_id, left.registry_vocabulary, left.episode_policy, left.undated_policy) != (
        right.max_observation_age_days, right.policy_version, right.counter_signal_policy_digest,
        right.evaluator_version, right.instrument_id, right.registry_vocabulary, right.episode_policy, right.undated_policy):
        raise ValueError("comparison requires the same evaluation policy")
    if earlier.read_as_of > later.read_as_of:
        raise ValueError("comparison dates must be chronological")
    present_old = {(s.record_id, label) for s in earlier.marker_surfaces for label in s.present}
    present_new = {(s.record_id, label) for s in later.marker_surfaces for label in s.present}
    missing_old = {(s.record_id, label) for s in earlier.marker_surfaces for label in s.missing}
    missing_new = {(s.record_id, label) for s in later.marker_surfaces for label in s.missing}
    stale_old = {(s.record_id, label) for s in earlier.marker_surfaces for label in s.stale}
    dates_old = {(e.record_id, e.label): _latest_known_date(e)
                 for e in earlier.marker_evidence}
    dates_new = {(e.record_id, e.label): _latest_known_date(e)
                 for e in later.marker_evidence}
    refreshed = stale_old & present_new
    for pair in present_old & present_new:
        old_date, new_date = dates_old[pair], dates_new[pair]
        if old_date is not None and new_date is not None and new_date > old_date:
            refreshed.add(pair)
    return DeclarationComparison(earlier_envelope.subject_id, reading_digest(earlier), reading_digest(later),
                                 tuple(sorted(present_new - present_old - refreshed)),
                                 tuple(sorted(present_old - present_new)), tuple(sorted(refreshed)),
                                 tuple(sorted(missing_old & missing_new)))
