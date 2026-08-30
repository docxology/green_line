"""Deterministic serialization and digesting for review and drift detection.

The digest is a review instrument: two readers holding the same digest are
talking about the same registry content, and an unexpected digest change is
a drift signal that the growth records were edited. It carries no truth,
competence, or permission semantics of any kind.
"""

from __future__ import annotations

import hashlib
import json

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
        "schema_version": "1.0",
        "status": reading.status.value,
        "read_as_of": reading.read_as_of,
        "registry_digest": reading.registry_digest,
        "intake_notes": list(reading.intake_notes),
        "findings": [
            {
                "record_id": finding.record_id,
                "status": finding.status.value,
                "reasons": list(finding.reasons),
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
