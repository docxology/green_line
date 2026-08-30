"""The common report envelope Green Line exports for co-registration.

A reader holding reports from several independent instruments needs one
uniform way to say "this instrument, about this subject, at this review
moment, said this - and here is the pointer to its complete native report."
The envelope is that data contract and nothing more. It points to the full
canonical reading by digest instead of copying or reinterpreting its fields.

``native_status`` is deliberately typed as this line's own vocabulary - for
Green Line, the single overall marker-coverage status. Envelopes from
different lines must not be compared, ranked, averaged, or merged on
``native_status``. An envelope is a witness record, not a score.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

from .model import GreenReading
from .serialization import reading_digest
from .version import __version__

#: The cross-instrument envelope shape this module exports.
ENVELOPE_SCHEMA = "line.report-envelope/1.0"

#: This instrument's identity inside an envelope.
GREEN_LINE_ID = "green_line"

#: The non-claims every envelope carries, restating the instrument boundary
#: in transportable form.
SCOPE_AND_NONCLAIMS: tuple[str, ...] = (
    "describes declaration coverage of self-declared tags and growth-marker "
    "labels at a stated review date",
    "not a competence, mastery, certification, or hiring claim about any person",
    "not permission: STAGED never authorizes an action, a route, or a release",
    "does not verify that a declared marker exists or supports what it names",
    "does not rank, merge, or evaluate the other line instruments",
)


@dataclass(frozen=True)
class ReadingEnvelope:
    """One instrument's complete reading, referenced without reinterpretation.

    ``report_ref`` is the SHA-256 of the canonical native reading, which
    contains the full derivation - every record finding with its ordered
    reasons trail and every intake note. ``registry_version`` is the package
    version that shipped the registry - record content itself is pinned by
    ``registry_digest``, which the referenced reading also carries.
    ``source_snapshot_refs`` is caller-supplied provenance for the material
    the declarations were made about; the envelope stores, and does not
    verify, those references.
    """

    schema_version: str
    line_id: str
    subject_id: str
    review_date: str
    registry_version: str
    registry_digest: str
    native_status: str
    report_ref: str
    source_snapshot_refs: tuple[str, ...]
    scope_and_nonclaims: tuple[str, ...]


def reading_envelope(
    reading: GreenReading,
    subject_id: str = "",
    source_snapshot_refs: Iterable[str] = (),
) -> ReadingEnvelope:
    """Wrap a reading in the common envelope, pointing at - never
    re-reading - its complete canonical form.

    ``subject_id`` names what was read, in the caller's own reference
    scheme; the evaluator does not verify it. The envelope's ``report_ref``
    is computed from the exact reading supplied, so an envelope can only
    ever point at the derivation that produced its status.
    """

    refs = tuple(source_snapshot_refs)
    if not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise ValueError("source_snapshot_refs must be non-blank strings")
    if not isinstance(subject_id, str):
        raise TypeError("subject_id must be a string")
    return ReadingEnvelope(
        ENVELOPE_SCHEMA,
        GREEN_LINE_ID,
        subject_id,
        reading.read_as_of,
        __version__,
        reading.registry_digest,
        reading.status.value,
        reading_digest(reading),
        refs,
        SCOPE_AND_NONCLAIMS,
    )


def canonical_envelope(envelope: ReadingEnvelope) -> str:
    """Serialize an envelope to stable JSON for archiving beside its report."""

    payload = {
        "schema_version": envelope.schema_version,
        "line_id": envelope.line_id,
        "subject_id": envelope.subject_id,
        "review_date": envelope.review_date,
        "registry_version": envelope.registry_version,
        "registry_digest": envelope.registry_digest,
        "native_status": envelope.native_status,
        "report_ref": envelope.report_ref,
        "source_snapshot_refs": list(envelope.source_snapshot_refs),
        "scope_and_nonclaims": list(envelope.scope_and_nonclaims),
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def envelope_matches_reading(
    envelope: ReadingEnvelope, reading: GreenReading
) -> bool:
    """Return whether an envelope still points at exactly this reading."""

    return (
        envelope.report_ref == reading_digest(reading)
        and envelope.review_date == reading.read_as_of
        and envelope.registry_digest == reading.registry_digest
        and envelope.native_status == reading.status.value
    )


__all__ = [
    "ENVELOPE_SCHEMA",
    "GREEN_LINE_ID",
    "ReadingEnvelope",
    "SCOPE_AND_NONCLAIMS",
    "canonical_envelope",
    "envelope_matches_reading",
    "reading_envelope",
]
