# Standalone operation

Green Line installs, tests, and generates figures without other Line Set
repositories. Its runtime uses Python 3.11 or later and the standard library.
See [development](development.md) for the locked environment and exact gates.

Envelope tests use a frozen copy of the register's structural schema. When
an optional sibling envelope is available, the tests can also inspect it
read-only. See [envelopes](envelopes.md) for the separate report, validation,
and provenance checks.

Publication uses the [pinned template renderer](development.md#render-and-validate-the-manuscript)
in a separate checkout. It reads this project's source under
[`docs/manuscript/`](manuscript/README.md) and writes generated artifacts
under `output/`. The [publication procedure](publication.md) covers versioned
archives and DOI evidence.
