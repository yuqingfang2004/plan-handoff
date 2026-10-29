# plan-clean

Recoverably remove covered inactive plan files from the working collection. Archive them under that same collection's `archive/`, not a new directory outside it. Never clean real projects merely to test this skill.

## Preview and authorize

1. Confirm the root, scope and writer ownership. Read summary.md and summary.manifest.json. If absent or stale, ask whether to run plan-summary before cleaning; do not silently summarize then clean. Explicit prior authorization for the entire chain can be reused.
2. Check the summary actually preserves each candidate's outcome, limits, important decisions and evidence. A matching hash is not a semantic check. Active, blocked, pending, unknown or dependency-bearing plans stay protected. Do not relabel them to make cleanup pass.
3. Run a read-only preview with exact candidate paths:

```sh
python <skill>/scripts/plan_store.py preview --root <collection> \
  --plan 2026-10-29-reader/plan.md
```

Use repeated `--plan` for multiple files. The helper scans Markdown references within the collection. Add `--references-root <project-docs>` for relevant external documentation roots. It detects ordinary inline and reference-style links, not every possible Markdown/HTML format or semantic dependency. It conservatively retains targets referenced by other existing plans, including selected plans: a selected source may survive a removal failure. Resolve such dependencies explicitly rather than assuming an entire batch will disappear. Inspect known dependencies and unusual references yourself; retain their sources until resolved. Do not claim a global no-broken-links guarantee from this scoped scan.

4. Show what will be archived, what remains and why, the summary location and the reference-check scope. Perform only the user's authorized concrete scope. A broad initial "clean" request needs no duplicate confirmation when that exact scope is already clear and authorized; ambiguity does. Never treat --apply as a substitute for user authorization.

## Archive then remove

```sh
python <skill>/scripts/plan_store.py archive --root <collection> \
  --plan 2026-10-29-reader/plan.md --apply
```

Without --apply, archive is only a preview. Apply rechecks eligibility, creates a uniquely named ZIP under archive/, validates CRC and source hashes, saves recovery mappings and redirects supported summary links, then rechecks original bytes before removing each selected file. It rebuilds its managed index from the actual remaining sources, including originals retained after backup. If that final navigation update fails, the error identifies actual removals and the verified backup; do not claim all originals remain. It removes only empty task directories; evidence logs and other files remain. It rejects path traversal and symlink paths and never recursively deletes a task directory.

Use a coordinated filesystem. The helper lock excludes other helper writers, not unrelated agents or hostile OS-level replacement races. Do not operate while another session is modifying the collection. It will not contact that session for you.

Unrecognized management files are protected. Unsupported summary references retain the affected sources. On interruption, a verified archive may exist alongside some originals or partial metadata updates. Retain evidence, report the actual removed/retained lists, archive and error; do not claim transaction-wide rollback. An `already archived; original retained` report requires inspection, not forced deletion or automatic re-archiving. A stale lock is also inspected before removal.

Do not alter archived blocks while summarizing new work, overwrite ZIPs, delete archive/ during routine cleaning, or repeat an archive already completed. The summary and manifest retain archived results even after original folders disappear.

## Restore and report

Restore into a new directory, never over existing work:

```sh
python <skill>/scripts/plan_store.py restore --root <collection> \
  --archive archive/2026-10-29-001.zip --destination <new-empty-path>
```

The destination must not exist. The helper validates managed ZIP content and writes only approved relative Markdown members without extractall. Recovery preserves original bytes and paths. Moving recovered plans back into an active project requires checking the current workspace and authorization; don't silently reopen a finished task.

Report archived and retained counts, archive location and recovery command. Explain errors or unsupported layouts. This mode is recoverable archiving, not permanent archive purging. If further work requires a handoff, use the explicit phase/model-role block in [SKILL.md](../SKILL.md); otherwise state that no model switch is needed.
