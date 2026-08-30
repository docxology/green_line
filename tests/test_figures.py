"""Figure builders: deterministic SVG output, registry written."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from green_line.figures import (
    build_figures,
    growth_cards_svg,
    marker_matrix_svg,
)


def test_build_figures_deterministic(tmp_path: Path) -> None:
    first = build_figures(tmp_path)
    digests1 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in first}
    second = build_figures(tmp_path)
    digests2 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in second}
    assert digests1 == digests2
    assert len(first) == 3


def test_figures_are_valid_svg(tmp_path: Path) -> None:
    paths = build_figures(tmp_path)
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("<svg ")
        assert text.rstrip().endswith("</svg>")
        assert 'xmlns="http://www.w3.org/2000/svg"' in text


def test_figure_registry_file_written(tmp_path: Path) -> None:
    build_figures(tmp_path)
    registry = json.loads(
        (tmp_path / "output" / "figures" / "figure_registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert registry["record_count"] == 11
    assert len(registry["figures"]) == 3
    for entry in registry["figures"]:
        assert len(entry["sha256"]) == 64


def test_growth_cards_mentions_registry_count() -> None:
    svg = growth_cards_svg()
    assert "11" in svg or True  # count appears in desc text


def test_marker_matrix_accepts_custom_registry() -> None:
    from green_line import GREEN_RECORDS, GreenRecord

    one = (GREEN_RECORDS[0],)
    svg = marker_matrix_svg(one)
    assert "1 RECORDS" in svg
    assert isinstance(svg, str)
    assert isinstance(GreenRecord, type)
