# Design and validation

## Contract

One installed skill routes three modes. **plan-switch** preserves manual planning,
implementation, decisions and review through one dedicated plan.md. **plan-summary**
explains closed task outcomes without rewriting active execution context.
**plan-clean** recoverably archives only summary-covered inactive sources under
the same collection's archive/. The user chooses models and authorizes work.

Stage and mode are explicit. Every actual handoff displays next stage, required
model role, manual action and exact plan path; the prompt repeats stage and role.
No model call, agent dispatch, branch switch or publication follows merely from a
stored plan. Review does not authorize implementation edits. Approval already
provided is reused, not repeatedly requested.

A new task uses handoffs/YYYY-MM-DD-topic/plan.md; old dedicated paths stay valid.
Switching models, conversations, stages or days does not create a new task. New
independent goals get linked plans. Reopen incorrect completion, record important
decisions, and retain evidence without appending every conversation. User-owned
plans and notes are references unless their edit was explicitly requested.

## Summary and cleanup

Inactive means completed, cancelled or superseded, subject to evidence and
remaining work. Blocked, pending acceptance/review and ambiguous plans are
protected regardless of age. A summary can show short active-task snapshots but
never certify them for cleanup. Cancellation does not mean implementation.

A cumulative summary.md retains old results after their sources are archived.
Explicit per-task result blocks identify coverage. summary.manifest.json retains
source, block and whole-summary hashes, status, evidence and archive mappings.
Semantic accuracy remains an agent/user responsibility; the helper cannot prove it.
Overview-only updates can refresh hashes; changing a result requires re-coverage.
Old archived blocks are preserved; explicit corrections can be appended.

Cleanup starts with a scoped preview and existing user authorization. If coverage
is absent or stale, ask whether to summarize before cleaning unless the full chain
was already authorized. The helper checks status, hashes, supported scoped links
and non-symlink relative paths. It verifies a ZIP, publishes recovery mappings,
redirects supported links and rechecks bytes before each original is removed.
Only empty task directories are removed; logs and business files are preserved.
Status comes from opening metadata, excluding examples and historical sections.
LF and CRLF management markers are accepted without normalizing source hashes.
References from other selected plans conservatively retain their targets, because
a batch can partially fail. Navigation lists actual remaining sources after removal,
including changed originals that already have a backup.

This is recoverable multi-file work, not a filesystem transaction. Metadata updates
or removal may partially complete; errors must report retained files and the
verified archive. Helper locks coordinate helper writers, not unrelated sessions
or hostile path replacement. Reference detection is limited to declared roots and
supported link syntax; known semantic dependencies need agent review. ZIPs are not
automatically purged. Restore targets a new directory, checks hashes and approved
relative members, and does not use extractall.

## Files and dependencies

- SKILL.md: small router, shared protection and explicit handoff format.
- references/plan-switch.md: planning, execution, recovery and review rules.
- references/plan-summary.md and plan-clean.md: on-demand mode details and commands.
- templates/plan.md and summary.md: user-facing artifact starters.
- scripts/plan_store.py: optional Python 3.9+ standard-library helper; no network,
  model or Git operations. Ordinary switch mode has no Python requirement.
- tests/test_plan_store.py: temporary-fixture behavioral acceptance for the helper.
- agents/openai.yaml: optional display metadata. README files and this design are
  public documentation, not required context for every invocation.

Keep the complete folder when installing; moving only the old two-file core no
longer includes the mode references. Removing optional Codex metadata is supported.

## v0.2.0 validation — 2026-10-29

All 34 helper tests passed on Linux Python 3.9.21 and 3.13.13. A subsequent review
verified source/log hashes and reran the 34 tests from an isolated source snapshot
on Python 3.13.13, with no failures, errors or skips. It also checked later cleanup
of a retained dependency target, CRLF summary link redirection, and ambiguous or
unfinished metadata examples. No new blocking findings remained in that scope.

Reproduce the packaged helper tests from the repository root:

```sh
python -B -m unittest discover -s tests -v
```

Temporary-fixture helper tests cover missing/stale summaries, empty result blocks,
active/unknown statuses, reopening, path traversal/symlinks, retained references,
unrelated management files, incremental archived results, unique archives,
write/verification failures, post-backup source changes and byte-exact recovery.
Regression tests also protect archived result blocks, unsupported summary links,
and stale coverage belonging to a different plan. Review regressions cover fenced
and commented status examples, real metadata versus historical states, same-batch
dependencies in both orders, retained-source navigation, final navigation failures,
and LF/CRLF archive/restore. No real project is cleaned.

Author scenario review checks the explicit role block for pending versus confirmed
execution, decisions, review and completion. Format, local references, optional UI
metadata and relocation without Codex metadata are checked separately. These are
local checks, not hosted CI, independent model behavior, native Windows or cost evaluations.

An earlier manual model-switch trial completed a repository synchronization check
with no upstream changes. It did not exercise the new modes or installed-client
automatic discovery. Fresh-session behavior and cost savings remain unmeasured.
