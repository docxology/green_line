"""Lexical no-mocks gate: no mocking framework anywhere in this repo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Each banned token is split so this file does not match itself.
_BANNED = (
    ("unittest", ".mock"),
    ("Magic", "Mock"),
    ("mocker", ".patch"),
    ("mock", ".patch"),
)


def _banned_tokens() -> tuple[str, ...]:
    return tuple("".join(parts) for parts in _BANNED)


def test_no_mock_framework_in_source_trees() -> None:
    offenders: list[str] = []
    for tree in ("src", "tests", "scripts"):
        for path in (ROOT / tree).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in _banned_tokens():
                if token in text:
                    offenders.append(f"{path}: {token}")
    assert not offenders, offenders


def test_fail_closed_via_real_callable_not_mock() -> None:
    """A failing dependency is exercised with a plain class, not a mock."""

    from green_line import GreenRecord
    from green_line.intake import registry_shape_error

    class NotARecord:
        pass

    assert "not a GreenRecord" in (
        registry_shape_error((NotARecord(),)) or ""
    )
    assert registry_shape_error((GreenRecord("x", "t", "w", frozenset({"research"}), ("m",)),)) is None


def test_absent_sibling_is_outcome_not_exception(witness_root: Path) -> None:
    """The NOT_INSTALLED path: witness_root may not exist; handle honestly."""

    if witness_root.is_dir():
        assert witness_root.name == "envelopes"
    else:
        assert not witness_root.exists()
