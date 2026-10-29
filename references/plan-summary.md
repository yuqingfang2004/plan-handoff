# plan-summary

Make the project's past work understandable to its user. Produce a compact results overview, not a condensed execution transcript. Use the existing collection root; skip archive/ and do not rewrite active plan.md files.

## Select and explain

1. Read the existing index, summary and coverage manifest if present. Scan current plans with `python <skill>/scripts/plan_store.py scan --root <collection>`. Scan discovers plan.md; inspect user-designated legacy paths separately. Do not scan the entire archive by default.
2. Confirm closed candidates from their stated status, remaining acceptance work and known dependencies. Completed, cancelled and superseded are eligible for summarization. Pending tests/review or a blocked task is protected even if old. Unknown or contradictory status stays protected; do not relabel it solely to enable cleanup. A user-authorized abandonment can be recorded explicitly.
3. Group results by capability or deliverable. Explain the original problem, what was delivered, key code/artifact locations, verification scope, limits and follow-up. Separate implemented results from rejected proposals. Label claims as reported in the old plan or actually checked this time; do not turn historical tests into current acceptance or start unrelated tests/model calls.
4. Show active tasks only as short goal/stage/next-step snapshots with their original links. Their full execution context stays in their plans. They receive no cleanup coverage entry.

## One cumulative overview

Maintain one `summary.md`, using [the template](../templates/summary.md). Preserve earlier results and archived entries when adding new ones. Do not erase results just because original files no longer appear in the scan. Keep it concise; plans and evidence carry details. Do not create timestamped summary copies on every run.

The helper recognizes `<!-- plan-handoff:summary:v1 -->` as the first line. Each closed task uses a stable ASCII entry ID with one substantive block:

```markdown
<!-- plan-handoff:entry:bounded-reader -->
## Bounded reader

Delivered range reads without changing legacy full reads. Evidence: reported local
acceptance at commit abc123; Windows was not evaluated. See src/reader.py.
Remaining limitation: the original file must fit the configured access policy.
<!-- /plan-handoff:entry:bounded-reader -->
```

These markers identify coverage, not permission or proof of semantic correctness. Do not mark a heading-only block or filename list as a result summary. Do not overwrite unrelated files called summary.md, index.md or summary.manifest.json. Adopt existing files only with clear ownership/authorization, otherwise ask for a non-conflicting location.

After reviewing each actual result block, record that source's version:

```sh
python <skill>/scripts/plan_store.py cover --root <collection> \
  --plan 2026-10-29-reader/plan.md --entry bounded-reader --evidence "commit abc123; local report"
```

The manifest records source and entry hashes, closed status, evidence references and archive locations. Cover every summarized source explicitly; paths use forward slashes relative to the collection root. The helper rejects active/unknown status. It recognizes an unindented `- Task status: completed` (also cancelled/superseded), or the Chinese `任务状态` equivalents, in the opening metadata before the first section heading. Code fences, comments, indented/quoted examples and later historical sections do not supply metadata. Unsupported legacy layouts remain protected until their status is explicitly clarified, not guessed. Managed first-line markers accept LF or CRLF; hashes still cover the original bytes.

For overview-only edits that leave result blocks intact, `refresh --root <collection>` updates the summary fingerprint. Changing a result block requires a renewed targeted `cover`; refresh cannot certify new claims. Preserve old archived blocks when merging new results; corrections can be appended with a clear reference to the historical claim rather than silently overwriting it. Re-read source bytes before covering; don't certify a version that changed while drafting.

Maintain a lightweight index pointing to summary, active plans and archives. A helper-managed index starts with `<!-- plan-handoff:index:v1 -->`; never add that marker to a user-owned index just to overwrite it. Summary alone retains originals. Offer cleanup separately unless the user already authorized summary→clean. Report summarized/protected task counts and remaining ambiguity. Any next handoff uses the explicit stage/model block in [SKILL.md](../SKILL.md).
