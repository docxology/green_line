# Envelopes and native-report provenance

The green_line 0.2.0 producer uses its own public API; no sibling is imported
or modified. The shared line.report-envelope/1.0 shape is retained.

Each envelope has an adjacent canonical native file named *.report.json.
Its exact bytes, without a trailing newline, hash to the envelope's report_ref.
The envelope itself is canonical JSON with a trailing newline.

manifest.json records source_commit, exact source hashes, explicit evaluation
context, report/envelope file hashes and the declared provenance bundle digest.
The source commit pins the producer; the historical same-subject declaration
does not become a fresh audit of the referenced witness release. References
remain caller assertions and gap_list remains explicitly reference-only.

Regenerate into an empty directory using the manifest's full source SHA:

```bash
uv run python scripts/gen_envelopes.py --output-dir <empty-directory> --source-commit <manifest-source-sha>
```

For the committed bundle, omit --output-dir. Use the pinned commit rather than
today's HEAD when checking historical byte identity. Native reports carry
their own policy/context and reject unsupported identities rather than
guessing. Exported native_status remains uninterpreted across lines.
