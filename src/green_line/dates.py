from __future__ import annotations

from datetime import date
import re


def parse_iso_date(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("date must use YYYY-MM-DD")
    return date.fromisoformat(value)
