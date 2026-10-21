"""Package version authority: pyproject and version.py agree."""

from __future__ import annotations

import tomllib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_version_matches_package() -> None:
    from green_line import __version__

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == __version__


def test_citation_cff_version_matches() -> None:
    from green_line import __version__

    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert f"version: {__version__}" in text


def test_changelog_names_current_version() -> None:
    from green_line import __version__

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {__version__}" in changelog


def test_publication_versions_and_verified_doi_agree():
    from green_line import __version__
    zenodo = json.loads((ROOT / ".zenodo.json").read_text())
    config = (ROOT / "docs" / "manuscript" / "config.yaml").read_text()
    citation = (ROOT / "CITATION.cff").read_text()
    assert zenodo["version"] == __version__
    assert f'version: "{__version__}"' in config
    doi = re.search(r'value: "(10\.[^"]+)"', citation).group(1)
    assert f'doi: "{doi}"' in config
    assert doi in zenodo["notes"]
    assert "Apache-2.0" == zenodo["license"]
