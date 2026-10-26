# AGENTS.md — `green_line/src/green_line/figures`

## Scope
- Deterministic figure builders for the registry cards, marker matrix, status
  flow and cover plate. Part of the package, but not re-exported publicly.
- Pure standard library for SVG; `rsvg-convert` is used only for the cover PNG.

## Layout
- `__init__.py` — SVG builders, `figure_registry()`, `build_figures()`,
  `_resolve_converter()`.

## Gotchas
- Output must be byte-identical across runs: no timestamps, no dict-order
  iteration, no floating-point formatting drift.
- A missing `rsvg-convert` must raise rather than skip the cover;
  `tests/test_figures.py` asserts no cover is claimed when the converter is
  absent.
- `build_figures()` writes under git-ignored `output/`; never commit figures.
