# Design and validation

## Design contract

The user controls model selection. One task document carries the goal, scope,
important decisions, current state, and verification evidence between planning,
implementation, and optional review. Both a model switch in the same conversation
and a fresh conversation can use that document.

The latest user request determines the stage. A planning-only request ends with a
handoff; an explicit request to implement an approved plan proceeds without asking
for the same approval again. The plan records context rather than granting new
permissions. Ordinary implementation choices stay with the implementer; changes
to agreed scope, public interfaces, safety constraints, or significant architecture
return to the user for a decision.

The workflow is guidance, not an enforced state machine. It neither selects models
nor starts other agents, sends messages, changes branches, or publishes artifacts
on its own authority.

## Document lifecycle and handoffs

Each task owns a dedicated `plan.md`; user-owned plans and notes are sources, not
progress logs unless the user explicitly requests that edit. New plans default to
`handoffs/YYYY-MM-DD-<topic>/plan.md`; existing dedicated plans retain their paths.
Model or conversation switches, review corrections, and workspace changes do not
by themselves create a new plan. Independent deliverables get linked plans;
replacement goals supersede the old plan. Reopen incorrect completion claims,
consolidate long documents, and retain completed plans in place. A lightweight
collection index navigates multiple tasks without duplicating their details.

At actual handoffs, update the plan and give its exact path, suggested role, and
one copyable prompt. Implementation prompts preserve pending approval; decision
prompts carry a specific question and evidence; review prompts authorize review,
not implementation edits. Use the user's model preferences without hard-coding a
required model or making an automatic call. Ordinary work does not trigger a
handoff at every step.

## Structure

- `SKILL.md`: stage selection, handoff, implementation, and reporting guidance.
- `templates/plan.md`: a dedicated plan, with source references, lifecycle state, and the next handoff prompt.
- `agents/openai.yaml`: optional Codex display metadata, not runtime requirements.
- README files, this document, and `LICENSE`: public project documentation, not
  mandatory context for every invocation.

No scripts, hooks, service dependencies, or companion skills are required.
Task files belong to the target project. The skill should reference source and
logs rather than copy them, and update progress at meaningful boundaries rather
than on every tool call.

## Validation status — 2026-10-29

The 2026-10-29 lifecycle and handoff-prompt revision passed local format,
reference, UI metadata, and relocated-core checks. Author review covered source
document preservation, continuation versus new tasks, supersession and reopening,
filename collisions, and authorization in all three handoff prompts. These are
static checks, not independent model behavior tests. The installed local symlink
points to the revised source; client reload behavior was not independently tested.

The earlier evidence below remains historical and does not validate the new
lifecycle behavior:

| Evidence | Result and limit |
| --- | --- |
| Skill metadata | Local skill-creator format validator passed; this checks structure, not behavior. |
| File references and UI fields | Local link, encoding, and display-field checks passed. |
| Relocated core | Format and reference checks passed with only SKILL.md and the task template, without Codex metadata. |
| Live handoff | One same-conversation planning-to-implementation trial, with a user-selected model change, completed a repository synchronization check. No new upstream commits existed; no unnecessary merge or new transfer artifact was created. |
| Trial invocation | The agent read the local skill by path. Installed-skill discovery was not tested. |

The live trial covered the no-change path. It did not exercise changed-code
implementation, merge conflicts, new-session recovery, or native integration in
other clients. It had no control group, independent behavioral evaluator, or
usage-cost measurement. Those outcomes remain unverified.

## Next useful evaluations

Use a small disposable project to evaluate an implementation with meaningful
acceptance checks. Then try a fresh conversation with an existing partial plan,
and a workspace whose current state differs from the plan. Record actual artifacts,
missed requirements, repeated investigation, and validation outcomes. Keep static
checks, observed model behavior, and cost measurements separate.

Additional model runs require the user's authorization. Do not infer successful
behavior from the presence of a rule in SKILL.md or require an expensive evaluation
suite for routine documentation edits.
