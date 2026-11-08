from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
import hashlib
import json
from dataclasses import asdict
from typing import TypeGuard

from .intake import COUNTER_SIGNAL_PHRASES, is_unicode_text, observation_exclusion
from .records import IntakeDisposition, NextReview
from .dates import parse_iso_date

POLICY_VERSION = "green.declaration-policy/2.1"


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def policy_digest() -> str:
    return content_digest(
        canonical_json(
            {
                "phrases": sorted(COUNTER_SIGNAL_PHRASES),
                "matching": "lowercase-substring",
                "date_grammar": "YYYY-MM-DD",
                "version": POLICY_VERSION,
            }
        )
    )


def _collection(value: object) -> TypeGuard[Iterable[object]]:
    return isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping))


def _rejected_text(value: str) -> dict[str, str]:
    # Archive only an opaque fingerprint, never rejected description prose.
    # Integer code units distinguish surrogate pairs from valid scalar text.
    fingerprint = content_digest(
        canonical_json(
            {
                "schema": "green.rejected-text/1",
                "code_units": [ord(character) for character in value],
            }
        )
    )
    return {"rejected_text_digest": fingerprint}


def _label(value: object) -> str | dict[str, str] | None:
    if isinstance(value, str) and not is_unicode_text(value):
        return _rejected_text(value)
    return value.strip().lower() if isinstance(value, str) and value.strip() else None


def _labels(value: object) -> list[str | dict[str, str] | None] | None:
    if not _collection(value):
        return None
    return sorted((_label(item) for item in value), key=canonical_json)


def snapshot_input(attempt: object) -> str:
    description = getattr(attempt, "description", None)
    dated = getattr(attempt, "dated_observations", ())
    entries = None
    if _collection(dated):
        entries = []
        for item in dated:
            noted = getattr(item, "noted_on", None)
            entry: dict[str, object] = {
                "label": _label(getattr(item, "label", None)),
                "noted_on": (
                    _rejected_text(noted)
                    if isinstance(noted, str) and not is_unicode_text(noted)
                    else noted
                    if isinstance(noted, str) or noted is None
                    else ""
                ),
            }
            for field in ("source_ref", "episode_id", "commentary"):
                value = getattr(item, field, None)
                entry[field] = (
                    _rejected_text(value)
                    if isinstance(value, str) and not is_unicode_text(value)
                    else value.strip()
                    if isinstance(value, str)
                    else None
                )
                if value is not None and (
                    not is_unicode_text(value) or not value.strip()
                ):
                    entry["malformed_metadata"] = True
            entries.append(entry)
        entries.sort(key=canonical_json)
    plan = getattr(attempt, "next_review", None)
    plan_payload: dict[str, object] | None
    if plan is not None and not isinstance(plan, NextReview):
        plan_payload = {"malformed": True}
    else:
        plan_payload = asdict(plan) if plan else None
        if plan_payload is not None:
            for field, value in tuple(plan_payload.items()):
                if isinstance(value, str) and not is_unicode_text(value):
                    plan_payload[field] = _rejected_text(value)
                    plan_payload["malformed"] = True
    return canonical_json(
        {
            "description_valid": is_unicode_text(description)
            and bool(description.strip()),
            "description_digest": (
                content_digest(description.strip())
                if is_unicode_text(description)
                else _rejected_text(description)["rejected_text_digest"]
                if isinstance(description, str)
                else None
            ),
            "tags": _labels(getattr(attempt, "tags", None)),
            "observations": _labels(getattr(attempt, "observations", None)),
            "dated_observations": entries,
            "next_review": plan_payload,
        }
    )


def observation_dispositions(
    snapshot: dict, read_date: date, max_age: int | None, known: frozenset[str]
) -> tuple[IntakeDisposition, ...]:
    result = []
    for channel in ("observations", "dated_observations"):
        raw = snapshot[channel]
        if raw is None:
            collection_note = (
                "observation declaration is not a collection of labels and was ignored"
                if channel == "observations"
                else "dated observation declaration is not a collection of records"
            )
            result.append(
                IntakeDisposition(
                    None,
                    channel,
                    None,
                    "excluded",
                    "MALFORMED_COLLECTION",
                    note=collection_note,
                )
            )
            continue
        for item in raw:
            entry = (
                {"label": item, "noted_on": None} if channel == "observations" else item
            )
            raw_label, raw_noted = entry["label"], entry["noted_on"]
            label = raw_label if isinstance(raw_label, str) else None
            noted = raw_noted if isinstance(raw_noted, str) else None
            note: str | None = None
            code, disposition = "UNDATED", "accepted"
            if label is None:
                code, disposition = "MALFORMED_LABEL", "excluded"
                note = "ignored a malformed observation label"
            elif (exclusion := observation_exclusion(label)) is not None:
                code, disposition, note = "COUNTER_SIGNAL", "excluded", exclusion
            elif entry.get("malformed_metadata"):
                code, disposition, note = (
                    "MALFORMED_METADATA",
                    "excluded",
                    f"observation '{label}' has malformed attribution and was not counted",
                )
            elif raw_noted is not None:
                try:
                    day = parse_iso_date(noted if noted is not None else "")
                except ValueError:
                    code, disposition, note = (
                        "INVALID_DATE",
                        "excluded",
                        f"observation '{label}' has an unreadable date and was not counted",
                    )
                else:
                    if day > read_date:
                        code, disposition, note = (
                            "FUTURE",
                            "excluded",
                            f"observation '{label}' is dated in the future and was not counted",
                        )
                    elif max_age is not None and (read_date - day).days > max_age:
                        code, disposition = "STALE", "stale"
                    else:
                        code = "CURRENT"
            if disposition == "accepted" and label not in known:
                code = "UNREQUIRED_" + code
            result.append(
                IntakeDisposition(
                    label,
                    channel,
                    noted,
                    disposition,
                    code,
                    entry.get("source_ref")
                    if isinstance(entry.get("source_ref"), str)
                    else None,
                    entry.get("episode_id")
                    if isinstance(entry.get("episode_id"), str)
                    else None,
                    note,
                )
            )
    return tuple(sorted(result, key=lambda d: canonical_json(d.__dict__)))
