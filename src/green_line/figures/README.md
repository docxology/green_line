# figures

Deterministic SVG builders: `growth_cards_svg`, `marker_matrix_svg`,
`status_flow_svg`, `green_line_cover_svg`, the derived `figure_registry()`, and
`build_figures(project_root)`, which writes the figures plus
`output/figures/figure_registry.json`.

The SVG build path is pure standard library. The cover plate is additionally
rasterized to PNG through `rsvg-convert` resolved from `PATH`; a missing
converter fails loudly instead of reporting a cover that does not exist
(`tests/test_figures.py`).
