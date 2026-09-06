"""Repo-wide invariants: fail-closed gates, sorting discipline."""

from __future__ import annotations


from green_line import GREEN_RECORDS, TAG_VOCABULARY, registry_digest
from green_line.figures import figure_registry


def test_figure_registry_digest_pinned() -> None:
    reg = figure_registry()
    assert reg["registry_digest"] == registry_digest(GREEN_RECORDS)
    assert reg["record_count"] == len(GREEN_RECORDS)
    assert reg["tag_vocabulary"] == sorted(TAG_VOCABULARY)


def test_figure_registry_has_at_least_three_figures() -> None:
    reg = figure_registry()
    assert len(reg["figures"]) >= 3
    labels = [entry["label"] for entry in reg["figures"]]
    assert len(set(labels)) == len(labels)


def test_every_figure_has_boundary() -> None:
    reg = figure_registry()
    for entry in reg["figures"]:
        assert entry["epistemic_boundary"].strip()
        assert entry["alt"].strip()


def test_tag_vocabulary_iteration_is_sorted_before_emit() -> None:
    reg = figure_registry()
    vocab = reg["tag_vocabulary"]
    assert vocab == sorted(vocab)
