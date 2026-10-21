from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
import hashlib
import json
from dataclasses import asdict
from typing import TypeGuard

from .intake import COUNTER_SIGNAL_PHRASES, observation_exclusion
from .records import IntakeDisposition, NextReview
from .dates import parse_iso_date

POLICY_VERSION = "green.declaration-policy/2.1"


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def policy_digest() -> str:
    return content_digest(canonical_json({"phrases": sorted(COUNTER_SIGNAL_PHRASES),
                                         "matching": "lowercase-substring",
                                         "date_grammar": "YYYY-MM-DD",
                                         "version": POLICY_VERSION}))


def _collection(value: object) -> TypeGuard[Iterable[object]]:
    return isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping))


def _label(value: object) -> str | None:
    return value.strip().lower() if isinstance(value, str) and value.strip() else None


def _labels(value: object) -> list[str | None] | None:
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
            entry: dict[str, object] = {"label": _label(getattr(item, "label", None)),
                     "noted_on": noted if isinstance(noted, str) or noted is None else ""}
            for field in ("source_ref", "episode_id", "commentary"):
                value = getattr(item, field, None)
                entry[field] = value.strip() if isinstance(value, str) else None
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    entry["malformed_metadata"] = True
            entries.append(entry)
        entries.sort(key=canonical_json)
    plan = getattr(attempt, "next_review", None)
    plan_payload: dict[str, object] | None
    if plan is not None and not isinstance(plan, NextReview):
        plan_payload = {"malformed": True}
    else:
        plan_payload = asdict(plan) if plan else None
    return canonical_json({
        "description_valid": isinstance(description, str) and bool(description.strip()),
        "description_digest": content_digest(description.strip()) if isinstance(description, str) else None,
        "tags": _labels(getattr(attempt, "tags", None)),
        "observations": _labels(getattr(attempt, "observations", None)),
        "dated_observations": entries,
        "next_review": plan_payload,
    })


def observation_dispositions(snapshot: dict, read_date: date, max_age: int | None,
                             known: frozenset[str]) -> tuple[IntakeDisposition, ...]:
    result = []
    for channel in ("observations", "dated_observations"):
        raw = snapshot[channel]
        if raw is None:
            collection_note = ("observation declaration is not a collection of labels and was ignored"
                    if channel == "observations" else
                    "dated observation declaration is not a collection of records")
            result.append(IntakeDisposition(None, channel, None, "excluded", "MALFORMED_COLLECTION", note=collection_note))
            continue
        for item in raw:
            entry = {"label": item, "noted_on": None} if channel == "observations" else item
            label, noted = entry["label"], entry["noted_on"]
            note: str | None = None
            code, disposition = "UNDATED", "accepted"
            if label is None:
                code, disposition = "MALFORMED_LABEL", "excluded"
                note = "ignored a malformed observation label"
            elif observation_exclusion(label):
                code, disposition, note = "COUNTER_SIGNAL", "excluded", observation_exclusion(label)
            elif entry.get("malformed_metadata"):
                code, disposition, note = "MALFORMED_METADATA", "excluded", f"observation '{label}' has malformed attribution and was not counted"
            elif noted is not None:
                try:
                    day = parse_iso_date(noted)
                except ValueError:
                    code, disposition, note = "INVALID_DATE", "excluded", f"observation '{label}' has an unreadable date and was not counted"
                else:
                    if day > read_date:
                        code, disposition, note = "FUTURE", "excluded", f"observation '{label}' is dated in the future and was not counted"
                    elif max_age is not None and (read_date - day).days > max_age:
                        code, disposition = "STALE", "stale"
                    else:
                        code = "CURRENT"
            if disposition == "accepted" and label not in known:
                code = "UNREQUIRED_" + code
            result.append(IntakeDisposition(label, channel, noted, disposition, code,
                                            entry.get("source_ref"), entry.get("episode_id"), note))
    return tuple(sorted(result, key=lambda d: canonical_json(d.__dict__)))
