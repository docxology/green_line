"""Deterministic serialization and digesting for review and drift detection.

The digest is a review instrument: two readers holding the same digest are
talking about the same registry content, and an unexpected digest change is
a drift signal that the growth records were edited. It carries no truth,
competence, or permission semantics of any kind.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .model import GreenReading, GreenRecord


def canonical_registry(records: tuple[GreenRecord, ...]) -> str:
    """Serialize records into stable JSON for review and comparison."""

    payload = [
        record.canonical() for record in sorted(records, key=lambda item: item.id)
    ]
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def registry_digest(records: tuple[GreenRecord, ...]) -> str:
    """Return a SHA-256 digest of the canonical registry serialization."""

    return hashlib.sha256(canonical_registry(records).encode("utf-8")).hexdigest()


def canonical_reading(reading: GreenReading) -> str:
    """Serialize a reading into stable JSON so results can be archived.

    Two identical reads of the same attempt produce byte-identical output,
    which lets a reading be diffed and cited in a review record.
    """

    payload = {
        "schema_version": "green.native-reading/2.0",
        "status": reading.status.value,
        "read_as_of": reading.read_as_of,
        "registry_digest": reading.registry_digest,
        "intake_notes": list(reading.intake_notes),
        "context": asdict(reading.context) if reading.context else None,
        "normalized_input": json.loads(reading.normalized_input) if reading.normalized_input else None,
        "registry_snapshot": json.loads(reading.registry_snapshot) if reading.registry_snapshot else None,
        "intake_dispositions": [asdict(d) for d in reading.intake_dispositions],
        "marker_surfaces": [asdict(s) for s in reading.marker_surfaces],
        "marker_evidence": [asdict(e) for e in reading.marker_evidence],
        "scope_reason": reading.scope_reason,
        "findings": [
            {
                "record_id": finding.record_id,
                "status": finding.status.value,
                "reasons": list(finding.reasons),
                "declaration_relevance": finding.declaration_relevance,
            }
            for finding in reading.findings
        ],
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def reading_digest(reading: GreenReading) -> str:
    """SHA-256 over the canonical reading; the pointer an envelope carries."""

    return hashlib.sha256(canonical_reading(reading).encode("utf-8")).hexdigest()


def replay_reading(report: str) -> GreenReading:
    from .evaluator import _read
    from .evidence import POLICY_VERSION, canonical_json, content_digest, policy_digest
    from .records import CultivationAttempt
    from .enums import GrowthKind
    from .version import __version__

    try:
        payload = json.loads(report)
        if payload["schema_version"] != "green.native-reading/2.0":
            raise ValueError("unsupported native report schema; no implicit migration")
        context = payload["context"]
        if (context["policy_version"] != POLICY_VERSION
                or context["counter_signal_policy_digest"] != policy_digest()
                or context["evaluator_version"] != __version__):
            raise ValueError("unsupported evaluator or policy identity")
        snapshot = canonical_json(payload["normalized_input"])
        if content_digest(snapshot) != context["input_digest"]:
            raise ValueError("normalized input digest mismatch")
        if payload["registry_snapshot"] is None:
            raise ValueError("invalid registry reports have no replayable registry")
        records = tuple(GreenRecord(row["id"], row["title"], row["wire"],
                                    frozenset(row["tags"]), tuple(row["required_markers"]),
                                    GrowthKind(row["kind"])) for row in payload["registry_snapshot"])
        reading, _ = _read(CultivationAttempt("digest-only replay"), records,
                           payload["read_as_of"], context["max_observation_age_days"],
                           frozenset(context["registry_vocabulary"]), context["instrument_id"],
                           snapshot, context["episode_policy"], context["undated_policy"])
        if canonical_reading(reading) != canonical_json(payload):
            raise ValueError("report differs from replayed derivation")
        return reading
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("malformed native report") from exc
