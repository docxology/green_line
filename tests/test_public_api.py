"""Public API surface and version authority."""

from __future__ import annotations

import green_line
from green_line.version import __version__


def test_version_authority() -> None:
    assert green_line.__version__ == __version__
    assert __version__ == "0.1.0"


def test_all_exports_resolve() -> None:
    for name in green_line.__all__:
        assert hasattr(green_line, name), name


def test_scope_and_nonclaims_present() -> None:
    assert green_line.SCOPE_AND_NONCLAIMS
    assert any("certification" in claim for claim in green_line.SCOPE_AND_NONCLAIMS)
