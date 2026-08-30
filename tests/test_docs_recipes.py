"""Docs stay honest: README/AGENTS name real commands and boundaries."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_readme_names_the_question() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "What is still growing?" in readme
    assert "never" in readme.lower()


def test_claim_boundaries_is_first_person() -> None:
    text = (ROOT / "docs" / "claim_boundaries.md").read_text(encoding="utf-8")
    assert "I do not claim" in text


def test_agents_md_lists_verify_commands() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for command in ("uv sync", "uv run pytest", "uv run ruff check", "build_figures.py"):
        assert command in text, command


def test_extensibility_names_opus_constraint() -> None:
    text = (ROOT / "docs" / "extensibility.md").read_text(encoding="utf-8")
    assert "opus_stage=None" in text or "stageless" in text
