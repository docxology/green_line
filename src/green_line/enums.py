"""Enumerations for growth statuses and growth families.

What the code establishes: typed vocabulary for one instrument's verdicts.
What it does not establish: that any capacity is real, improving, or
safe to rely on.
"""

from __future__ import annotations

from enum import Enum


class SignalStatus(str, Enum):
    """Outcome for one growth record whose stages apply to an attempt."""

    STAGED = "STAGED"
    NEEDS_MARKER = "NEEDS_MARKER"
    NEEDS_REWORK = "NEEDS_REWORK"


class GrowthStatus(str, Enum):
    """Overall outcome for a cultivation attempt."""

    STAGED = "STAGED"
    NEEDS_MARKER = "NEEDS_MARKER"
    NEEDS_REWORK = "NEEDS_REWORK"
    OUTSIDE_SCOPE = "OUTSIDE_SCOPE"


class GrowthKind(str, Enum):
    """The family of deliberate not-yet-mastery a record describes.

    Families exist so the registry can be reviewed for balance: a registry
    that only apprenticeship but never consolidation has drifted from the
    Green Line's purpose of making capacity under development inspectable.
    """

    APPRENTICESHIP = "APPRENTICESHIP"
    PRACTICE = "PRACTICE"
    METHOD = "METHOD"
    VERIFICATION = "VERIFICATION"
    COMMUNICATION = "COMMUNICATION"
    STEWARDSHIP = "STEWARDSHIP"
