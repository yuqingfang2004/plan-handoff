# Changelog

## v0.2.0 — 2026-10-29

- Keep one installed skill with three modes: plan-switch, plan-summary and plan-clean.
- Require explicit next-stage and model-role fields in both handoff blocks and copyable prompts.
- Summarize closed plans into one cumulative overview while protecting active or ambiguous tasks.
- Add an optional Python 3.9+ standard-library helper for coverage hashes, preview, verified ZIP archiving under the collection's archive/ and restoration into a new directory.
- Protect real task metadata from examples, preserve references and navigation after partial removals, and support LF/CRLF management markers with byte-exact source restoration.
- Update English/Chinese instructions and upgrade guidance. Existing task paths remain valid; install the complete skill folder.

Validation: 34 temporary-fixture tests passed on Linux Python 3.9 and 3.13; review reran the fixed snapshot and checked three additional boundary scenarios. Native Windows and client/model behavior are not established by these checks. See [DESIGN.md](DESIGN.md).

## v0.1.0 — 2026-10-29

- Give each task one dedicated plan.md, with explicit rules for continuing, reopening and creating successor tasks.
- Preserve existing user documents as references and provide manual planning, implementation and review handoff prompts.
