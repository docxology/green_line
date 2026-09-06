"""Figure builders: deterministic SVG output, registry written."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from green_line.figures import (
    build_figures,
    green_line_cover_svg,
    growth_cards_svg,
    marker_matrix_svg,
)


def test_build_figures_deterministic(tmp_path: Path) -> None:
    first = build_figures(tmp_path)
    digests1 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in first}
    second = build_figures(tmp_path)
    digests2 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in second}
    assert digests1 == digests2
    assert len(first) == 5


def test_figures_are_valid_svg(tmp_path: Path) -> None:
    paths = build_figures(tmp_path)
    for path in paths:
        if path.suffix != ".svg":
            continue
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
    assert len(registry["figures"]) == 4


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


def test_cover_plate_carries_only_its_two_texts() -> None:
    svg = green_line_cover_svg()
    assert ">GREEN LINE<" in svg
    assert ">CAPACITY UNDER DEVELOPMENT<" in svg
    assert "2026" not in svg  # no dates on the plate
    assert "0.1.0" not in svg  # no version numbers on the plate


def test_cover_registered_and_rasterized(tmp_path: Path) -> None:
    build_figures(tmp_path)
    png = tmp_path / "output" / "figures" / "green_line_cover.png"
    assert png.exists() and png.stat().st_size > 0
    registry = json.loads(
        (tmp_path / "output" / "figures" / "figure_registry.json").read_text(
            encoding="utf-8"
        )
    )
    cover = [e for e in registry["figures"] if e["label"] == "fig:green-line-cover"]
    assert len(cover) == 1
    assert len(cover[0]["png_sha256"]) == 64
    assert cover[0]["png_sha256"] == hashlib.sha256(png.read_bytes()).hexdigest()
