"""Deterministic Green Line figure builders and registry."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path

from green_line import (
    GREEN_RECORDS,
    TAG_VOCABULARY,
    __version__,
    registry_digest,
)

ROOT = Path(__file__).resolve().parents[3]

PAPER = "#eef4ea"
PANEL = "#f9fcf6"
INK = "#1c221a"
MUTED = "#4e5a4a"
GRID = "#b8c6b2"
GREEN = "#1a7a3a"
DARK_GREEN = "#0f5c2a"
AMBER = "#b45309"
CRIMSON = "#b91c1c"
TEAL = "#00796b"
MINT = "#e2f0e2"
CREAM = "#fffdf8"
GREY = "#f4f6f4"
BODY_FONT = "Arial,Helvetica,sans-serif"
TITLE_FONT = "Georgia,Times New Roman,serif"

COLS = 4
CARD_W = 300
CARD_H = 240
CARD_GAP_X = 325
CARD_GAP_Y = 265
GRID_X = 78
GRID_Y = 205
ROWS = (len(GREEN_RECORDS) + COLS - 1) // COLS
WIDTH = 1400
FOOTER_Y = GRID_Y + ROWS * CARD_GAP_Y + 30
HEIGHT = FOOTER_Y + 110
MIN_FONT = 6

STATUS_FILL = {
    "STAGED": GREEN,
    "NEEDS_MARKER": AMBER,
    "NEEDS_REWORK": CRIMSON,
    "OUTSIDE_SCOPE": MUTED,
}

FAMILY_FILL = {
    "APPRENTICESHIP": DARK_GREEN,
    "PRACTICE": GREEN,
    "METHOD": TEAL,
    "VERIFICATION": AMBER,
    "COMMUNICATION": "#0e7490",
    "STEWARDSHIP": "#4d7c0f",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(
    x: float,
    y: float,
    value: str,
    *,
    size: int = 18,
    fill: str = INK,
    weight: str = "400",
    family: str = BODY_FONT,
    italic: bool = False,
    anchor: str = "",
    letter_spacing: int = 0,
) -> str:
    size = max(size, MIN_FONT)
    attrs = [
        f'x="{x}"',
        f'y="{y}"',
        f'fill="{fill}"',
        f'font-family="{family}"',
        f'font-size="{size}px"',
        f'font-weight="{weight}"',
    ]
    if italic:
        attrs.append('font-style="italic"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if letter_spacing:
        attrs.append(f'letter-spacing="{letter_spacing}px"')
    return "<text " + " ".join(attrs) + ">" + esc(value) + "</text>"

def headline(x: float, y: float, value: str, *, size: int = 28) -> str:
    return text(x, y, value, size=size, weight="700", family=TITLE_FONT, italic=True)


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str = PANEL,
    stroke: str = GRID,
) -> str:
    return (
        '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(w)
        + '" height="' + str(h) + '" rx="12" fill="' + fill + '" stroke="'
        + stroke + '" stroke-width="1.6"/>'
    )


def wrap(value: str, width: int = 40) -> list[str]:
    """Deterministic greedy word wrap for card body text."""

    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = (current + " " + word).strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return lines


def growth_cards_svg() -> str:
    """The registry drawn as cards in declaration order, keyed by family."""

    body = [
        headline(64, 58, "Small markers make a growth surface visible"),
        text(
            64,
            88,
            "Each record names a growth surface; a missing marker asks for practice, not a judgment about talent.",
            size=15,
            fill=MUTED,
        ),
        text(
            64,
            116,
            "SOURCE-DRIVEN SCHEMATIC - REGISTRY DECLARATION ORDER - NOT A COMPETENCE OR MASTERY SCORE",
            size=11,
            fill=MUTED,
            weight="700",
        ),
        rect(50, 150, WIDTH - 100, ROWS * CARD_GAP_Y + 40, fill=PANEL),
    ]
    from green_line.model import GrowthKind

    for index, record in enumerate(GREEN_RECORDS):
        row, col = divmod(index, COLS)
        x = GRID_X + col * CARD_GAP_X
        y = GRID_Y + row * CARD_GAP_Y
        accent = FAMILY_FILL.get(record.kind.value, GREEN)
        body.append(rect(x, y, CARD_W, CARD_H, fill=CREAM, stroke=accent))
        body.append(
            '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(CARD_W)
            + '" height="8" rx="4" fill="' + accent + '"/>'
        )
        body.append(
            text(
                x + 18,
                y + 32,
                str(index + 1).zfill(2) + " - " + record.kind.value,
                size=12,
                fill=accent,
                weight="700",
            )
        )
        for line_index, title_line in enumerate(wrap(record.title, 28)):
            body.append(
                text(x + 18, y + 60 + line_index * 24, title_line, size=17, weight="700")
            )
        for line_index, wire_line in enumerate(wrap(record.wire, 30)):
            body.append(
                text(x + 18, y + 118 + line_index * 21, wire_line, size=15, fill=MUTED)
            )
        body.append(text(x + 18, y + 196, "markers", size=15, fill=accent, weight="700"))
        body.append(
            text(x + 18, y + 220, " - ".join(record.required_markers), size=14, fill=INK)
        )
    legend_x = GRID_X
    body.append(text(legend_x, FOOTER_Y, "Growth families", size=16, fill=INK, weight="700"))
    legend_x += 150
    for kind in GrowthKind:
        accent = FAMILY_FILL.get(kind.value, GREEN)
        body.append(
            '<rect x="' + str(legend_x) + '" y="' + str(FOOTER_Y - 15)
            + '" width="18" height="18" rx="4" fill="' + accent + '"/>'
        )
        body.append(text(legend_x + 26, FOOTER_Y, kind.value.lower(), size=15, fill=INK, weight="700"))
        legend_x += 46 + len(kind.value) * 9
    body.append(text(GRID_X, FOOTER_Y + 48, "Boundary", size=16, fill=INK, weight="700"))
    body.append(
        text(
            GRID_X + 106,
            FOOTER_Y + 48,
            "Green Line describes what is still growing; it never certifies competence or ranks learners.",
            size=16,
            fill=MUTED,
        )
    )
    desc = (
        str(len(GREEN_RECORDS)) + " Green Line growth records drawn as cards in registry "
        "declaration order, colour-keyed to growth families, each naming a growth surface "
        "and its required markers."
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(WIDTH) + '" height="'
        + str(HEIGHT) + '" viewBox="0 0 ' + str(WIDTH) + " " + str(HEIGHT)
        + '" role="img" aria-labelledby="title desc">'
        + '<title id="title">Small markers make a growth surface visible</title>'
        + '<desc id="desc">' + desc + "</desc>"
        + '<rect width="100%" height="100%" fill="' + PAPER + '"/>'
        + "".join(body)
        + "</svg>"
    )


def marker_matrix_svg(records: tuple = GREEN_RECORDS) -> str:
    """Show the registry's marker contract without implying verification."""

    width = 1400
    row_y = 214
    row_h = 60
    body = [
        '<rect width="100%" height="100%" fill="' + PAPER + '"/>',
        headline(64, 58, "The registry's growth-marker contract"),
        text(
            64,
            88,
            "Each record names markers a reader can look for; markers are not the underlying practice or its verification.",
            size=15,
            fill=MUTED,
        ),
        text(
            64,
            114,
            "DERIVED FROM REGISTRY - " + str(len(records)) + " RECORDS - "
            + str(sum(len(r.required_markers) for r in records)) + " REQUIRED MARKERS",
            size=11,
            fill=MUTED,
            weight="700",
        ),
        rect(50, 145, width - 100, len(records) * row_h + 66, fill=PANEL, stroke=GRID),
        text(78, 186, "record", size=16, fill=MUTED, weight="700"),
        text(610, 186, "reviewed tags", size=16, fill=MUTED, weight="700"),
        text(930, 186, "required growth markers", size=16, fill=MUTED, weight="700"),
    ]

    def chip(x: float, y: float, label: str, *, fill: str, stroke: str) -> float:
        chip_width = max(66, 20 + len(label) * MIN_FONT * 1.6)
        body.append(
            '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(chip_width)
            + '" height="30" rx="15" fill="' + fill + '" stroke="' + stroke
            + '" stroke-width="1.2"/>'
        )
        body.append(
            '<text x="' + str(x + chip_width / 2) + '" y="' + str(y + 21)
            + '" fill="' + INK + '" text-anchor="middle" font-family="' + BODY_FONT
            + '" font-size="' + str(MIN_FONT) + 'px">' + esc(label) + "</text>"
        )
        return chip_width

    for index, record in enumerate(records):
        y = row_y + index * row_h
        accent = FAMILY_FILL.get(record.kind.value, GREEN)
        body.append('<rect x="70" y="' + str(y) + '" width="8" height="36" rx="4" fill="' + accent + '"/>')
        body.append(text(94, y + 18, str(index + 1).zfill(2) + "  " + record.title, size=16, weight="700"))
        body.append(text(94, y + 40, record.kind.value.lower(), size=16, fill=accent, weight="700"))
        x = 610
        for tag in sorted(record.tags):
            x += chip(x, y + 6, tag, fill=GREY, stroke=GRID) + 6
        x = 930
        for label in record.required_markers:
            x += chip(x, y + 6, label, fill=MINT, stroke=GREEN) + 6

    legend_y = row_y + len(records) * row_h + 46
    body.append(text(78, legend_y, "Boundary", size=16, fill=INK, weight="700"))
    for offset, sentence in enumerate(
        (
            "The reader can confirm that markers were declared and matched;",
            "it cannot confirm that a mentor existed, a drill ran, or a skill is growing.",
        )
    ):
        body.append(text(174, legend_y + offset * 24, sentence, size=16, fill=MUTED))
    height = legend_y + 24 + 44
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(width) + '" height="'
        + str(height) + '" viewBox="0 0 ' + str(width) + " " + str(height)
        + '" role="img" aria-label="Green Line growth-marker contract matrix">'
        + "".join(body)
        + "</svg>"
    )


def status_flow_svg() -> str:
    """The verdict vocabulary as a deterministic flow schematic."""

    body = [
        '<rect width="100%" height="100%" fill="' + PAPER + '"/>',
        headline(64, 58, "How a read projects onto the status vocabulary"),
        text(
            64,
            88,
            "STAGED means declared markers cover the record; NEEDS_MARKER means refresh; NEEDS_REWORK means practice is missing.",
            size=15,
            fill=MUTED,
        ),
        text(
            64,
            114,
            "SOURCE-DRIVEN SCHEMATIC - THE PROJECTION SELECTS THE MOST DEMANDING READING; SURFACES PRESERVE WHAT IT COMPRESSES",
            size=11,
            fill=MUTED,
            weight="700",
        ),
    ]
    nodes = [
        ("no observations declared", "NEEDS_MARKER", 120),
        ("all required markers fresh", "STAGED", 380),
        ("only stale markers missing", "NEEDS_MARKER", 640),
        ("fresh markers missing", "NEEDS_REWORK", 900),
        ("no record tags matched", "OUTSIDE_SCOPE", 1160),
    ]
    for label, status, x in nodes:
        fill = STATUS_FILL[status]
        body.append(rect(x, 200, 200, 120, fill=PANEL, stroke=fill))
        body.append(
            '<rect x="' + str(x) + '" y="200" width="200" height="10" rx="5" fill="' + fill + '"/>'
        )
        body.append(text(x + 16, 244, status, size=18, fill=fill, weight="700"))
        for li, line_txt in enumerate(wrap(label, 22)):
            body.append(text(x + 16, 276 + li * 22, line_txt, size=14, fill=MUTED))
    body.append(text(78, 400, "Boundary", size=16, fill=INK, weight="700"))
    body.append(
        text(
            174,
            400,
            "A status is a projection of declared marker coverage at a review date; it is not mastery.",
            size=16,
            fill=MUTED,
        )
    )
    width = 1400
    height = 440
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(width) + '" height="'
        + str(height) + '" viewBox="0 0 ' + str(width) + " " + str(height)
        + '" role="img" aria-label="Green Line status flow">'
        + "".join(body)
        + "</svg>"
    )



COVER_NAME = "green_line_cover"


def green_line_cover_svg() -> str:
    """The cover plate: growth drawn with its unrealized continuation visible.

    A capacity-under-development instrument, so the dominant green stroke
    rises and then thins into a dashed ghost with hollow markers: the path
    is announced, not yet realized. The only text is the small-caps title
    top-left and the small-caps tagline bottom-right — no dates, no versions.
    """

    width, height = 1400, 1100
    body = [
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
        # Thin rule frame set inside the canvas edge.
        '<rect x="42" y="42" width="1316" height="1016" rx="0" '
        f'fill="none" stroke="{GRID}" stroke-width="2"/>',
        # Small-caps title, top-left, set in the title serif.
        text(
            92,
            148,
            "GREEN LINE",
            size=44,
            weight="700",
            family=TITLE_FONT,
            letter_spacing=10,
        ),
        # A short rule under the title, drawn in the work's own green.
        f'<line x1="94" y1="176" x2="470" y2="176" stroke="{GREEN}" stroke-width="3"/>',
    ]

    # The realized ascent: one thick stroke from the lower left, carrying
    # solid markers for each stage already walked.
    realized = "M 130 930 C 330 900 480 800 650 710 C 820 620 940 560 1060 480"
    body.append(
        f'<path d="{realized}" fill="none" stroke="{DARK_GREEN}" '
        'stroke-width="15" stroke-linecap="round"/>'
    )
    for index, (x, y) in enumerate(
        (
            (130, 930),
            (316, 880),
            (484, 800),
            (650, 710),
            (805, 628),
            (938, 555),
            (1060, 480),
        )
    ):
        body.append(
            f'<circle cx="{x}" cy="{y}" r="{15 - index}" fill="{GREEN}" '
            f'stroke="{PAPER}" stroke-width="3"/>'
        )
    # The continuation is announced but not realized: dashed, thinner, with
    # hollow markers where capacity is still under development.
    body.append(
        '<path d="M 1060 480 C 1160 404 1230 356 1298 300" fill="none" '
        f'stroke="{GREEN}" stroke-width="6" stroke-linecap="round" '
        'stroke-dasharray="5 19" opacity="0.6"/>'
    )
    for x, y in ((1136, 428), (1222, 362), (1298, 300)):
        body.append(
            f'<circle cx="{x}" cy="{y}" r="10" fill="{PAPER}" stroke="{GREEN}" '
            'stroke-width="3" opacity="0.9"/>'
        )

    # Muted companions: faint practice ticks along the base, the ground the
    # growth is recorded against.
    for index in range(14):
        x = 130 + index * 84
        tick = 26 + (index % 3) * 8
        body.append(
            f'<line x1="{x}" y1="976" x2="{x}" y2="{976 - tick}" '
            f'stroke="{GRID}" stroke-width="3" opacity="0.8"/>'
        )

    # Small-caps tagline, bottom-right.
    body.append(
        text(
            1308,
            1014,
            "CAPACITY UNDER DEVELOPMENT",
            size=25,
            weight="700",
            fill=DARK_GREEN,
            anchor="end",
            letter_spacing=6,
        )
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(width) + '" height="'
        + str(height) + '" viewBox="0 0 ' + str(width) + " " + str(height)
        + '" role="img" aria-labelledby="cover-title cover-desc">'
        + '<title id="cover-title">Green Line: capacity under development</title>'
        + '<desc id="cover-desc">On a pale green cream field inside a thin rule '
        "frame, a thick green stroke rises from the lower left through six solid "
        "markers and continues as a dashed line through three hollow markers, "
        "with faint practice ticks along the base; the small-caps title Green "
        "Line sits top-left and the small-caps tagline Capacity Under "
        'Development sits bottom-right.</desc>'
        + "".join(body)
        + "</svg>"
    )


def figure_registry() -> dict:
    """The derived figure registry, deterministic and digest-pinned."""

    return {
        "schema_version": "1.0",
        "package_version": __version__,
        "registry_digest": registry_digest(GREEN_RECORDS),
        "record_count": len(GREEN_RECORDS),
        "tag_vocabulary": sorted(TAG_VOCABULARY),
        "figures": [
            {
                "name": "growth_cards",
                "label": "Growth-record cards",
                "caption": "Green Line growth records in registry declaration order",
                "alt": "Cards for each growth record with family colour and required markers",
                "interpretive_claim": "shows what the registry declares about growth surfaces",
                "epistemic_boundary": "not a competence or mastery measure",
            },
            {
                "name": "marker_matrix",
                "label": "Growth-marker contract",
                "caption": "The registry's marker contract without implying verification",
                "alt": "Matrix of records with tags and required growth markers",
                "interpretive_claim": "shows which markers each record asks a reader to look for",
                "epistemic_boundary": "markers are declarations, not verified practice",
            },
            {
                "name": "status_flow",
                "label": "Status projection",
                "caption": "How reads project onto the Green Line status vocabulary",
                "alt": "Flow from intake conditions to status vocabulary",
                "interpretive_claim": "shows the projection rules the evaluator applies",
                "epistemic_boundary": "statuses are coverage projections, not judgments of persons",
            },
            {
                "name": COVER_NAME,
                "label": "Cover plate",
                "caption": "Cover plate showing growth drawn with its unrealized continuation left visible",
                "alt": "A thick green stroke rises through six solid markers and continues as a dashed line through three hollow markers, on a cream field inside a thin rule frame, titled Green Line and tagged Capacity Under Development",
                "interpretive_claim": "shows growth that is explicit about its own incompleteness",
                "epistemic_boundary": "the plate is a metaphor, not a measure of any person's development",
            },
        ],
    }


def _resolve_converter() -> str:
    """Resolve ``rsvg-convert`` from ``PATH`` or fail with an actionable message."""

    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise RuntimeError(
            "rsvg-convert is required to rasterize the deterministic cover SVG"
        )
    return converter


def build_figures(project_root: Path | None = None) -> list[Path]:
    """Write every deterministic SVG figure, the cover plate, and the registry.

    Figures are written as SVG: no external rasterizer dependency, so the
    build is pure standard library and fully deterministic. The cover is
    additionally rasterized to PNG through the shared ``rsvg-convert``
    binary (resolved from PATH) so the title page has an image to embed;
    that rasterization is byte-deterministic for a given SVG. The digests
    pin the registry version that produced the figures.
    """

    root = (project_root or ROOT).resolve()
    out = root / "output" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    builders = {
        "growth_cards": growth_cards_svg,
        "marker_matrix": marker_matrix_svg,
        "status_flow": status_flow_svg,
        COVER_NAME: green_line_cover_svg,
    }
    reg = figure_registry()
    generated: list[Path] = []
    entries: list = []
    for entry in reg["figures"]:
        name = entry["name"]
        svg_path = out / (name + ".svg")
        svg_path.write_text(builders[name](), encoding="utf-8")
        generated.append(svg_path)
        digest = hashlib.sha256(svg_path.read_bytes()).hexdigest()
        entry = {**entry, "sha256": digest}
        if name == COVER_NAME:
            png_path = out / (name + ".png")
            subprocess.run(
                [_resolve_converter(), str(svg_path), "--output", str(png_path)],
                check=True,
            )
            entry["png_sha256"] = hashlib.sha256(png_path.read_bytes()).hexdigest()
            generated.append(png_path)
        entries.append(entry)
    registry_out = {**reg, "figures": entries}
    (out / "figure_registry.json").write_text(
        json.dumps(registry_out, indent=2, sort_keys=True), encoding="utf-8"
    )
    return generated
