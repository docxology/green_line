from __future__ import annotations

from pathlib import Path
import json
import re

from .records import CultivationAttempt, Observation
from .evaluator import read_cultivation
from .envelope import canonical_envelope, reading_envelope, provenance_digest
from .serialization import canonical_reading
from .evidence import content_digest

ROOT = Path(__file__).resolve().parents[2]
WORKED_ATTEMPT = CultivationAttempt(
    "Practising formal proof review under a named mentor, with session logs kept",
    frozenset({"research", "teaching"}),
    dated_observations=(Observation("mentor", "2026-08-15"),
                        Observation("session_log", "2026-08-20")),
)
SAME_SUBJECT_ATTEMPT = CultivationAttempt(
    "witness_register 0.1.0 as a growing instrument: review practices, recorded limits, and handoff habits still under development",
    frozenset({"research", "teaching", "writing"}),
    dated_observations=(Observation("mentor", "2026-07-29"),
                        Observation("session_log", "2026-07-29"),
                        Observation("review_note", "2026-07-29"),
                        Observation("uncertainty", "2026-07-29")),
)
SUBJECT_ID = (
    "witness_register 0.1.0 (docxology/witness_register, commits 56962fe + 49ebea4, "
    "2026-07-29); registrar: the operator's assistant, filing growth observations "
    "from the repository's own records"
)
REFERENCE_ONLY = (
    "reference-only: gap_list: docs/manuscript/03_limits.md names unresolved work; not a scored declaration",
)
SUBJECT_REFS = (
    "declared: mentor: docs/correspondence.md external review",
    "declared: session_log: CHANGELOG.md hardening entries, 2026-07-29",
    "declared: review_note: docs/correspondence.md review attribution",
    "declared: uncertainty: docs/manuscript/03_limits.md",
    *REFERENCE_ONLY,
)


def source_hashes(root: Path = ROOT) -> dict[str, str]:
    paths = sorted((root / "src" / "green_line").rglob("*.py"))
    paths.append(root / "scripts" / "gen_envelopes.py")
    if len(paths) < 2 or any(not p.is_file() for p in paths):
        raise ValueError("empty or incomplete source scan")
    return {p.relative_to(root).as_posix(): content_digest(p.read_text(encoding="utf-8"))
            for p in paths}


def worked_prose() -> str:
    reading = read_cultivation(WORKED_ATTEMPT, as_of="2026-08-29")
    lines = ["A learner declares research and teaching, with mentor and",
             "session_log dated before the pinned review date. The following",
             "findings are generated from that declaration, without verifying practice:", "",
             "| Record | Native finding |", "| --- | --- |"]
    lines.extend(f"| {f.record_id} | {f.status.value} |" for f in reading.findings)
    lines.extend(["", f"Overall status: **{reading.status.value}** under [@def:aggregation].",
                  "This describes declared marker coverage, never competence or permission.", ""])
    return "\n".join(lines)


def build_examples(out: Path, *, source_commit: str,
                   same_subject_attempt: CultivationAttempt = SAME_SUBJECT_ATTEMPT) -> list[Path]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source_commit must be an immutable full commit SHA")
    out.mkdir(parents=True, exist_ok=True)
    specs = (
        ("green_line_worked", WORKED_ATTEMPT, "2026-08-29", "Green worked proof-review declaration",
         ("scenario: docs/manuscript/04_examples.md",)),
        ("green_line_same_subject", same_subject_attempt, "2026-07-29", SUBJECT_ID, SUBJECT_REFS),
    )
    rows: list[dict[str, object]] = []
    paths: list[Path] = []
    for name, attempt, day, subject, refs in specs:
        reading = read_cultivation(attempt, as_of=day, max_observation_age_days=None,
                                   episode_policy="combine_declared")
        envelope = reading_envelope(reading, subject, refs, strict=True)
        report_text = canonical_reading(reading)
        envelope_text = canonical_envelope(envelope)
        report_path, envelope_path = out / f"{name}.report.json", out / f"{name}.json"
        report_path.write_text(report_text, encoding="utf-8")
        envelope_path.write_text(envelope_text + "\n", encoding="utf-8")
        paths.extend((report_path, envelope_path))
        rows.append({"report": report_path.name, "envelope": envelope_path.name,
                     "report_sha256": content_digest(report_text),
                     "envelope_sha256": content_digest(envelope_text + "\n"),
                     "provenance_digest": provenance_digest(envelope, reading),
                     "context": json.loads(report_text)["context"], "review_date": day})
    manifest = out / "manifest.json"
    manifest.write_text(json.dumps({"schema_version": "green.example-bundle/1.0",
                                    "source_commit": source_commit, "source_hashes": source_hashes(),
                                    "invocation": "scripts/gen_envelopes.py --source-commit <source_commit>",
                                    "examples": rows}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    paths.append(manifest)
    return paths
