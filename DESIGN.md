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

## Structure

- `SKILL.md`: stage selection, handoff, implementation, and reporting guidance.
- `templates/task.md`: adaptable task document; existing project plans take priority.
- `agents/openai.yaml`: optional Codex display metadata, not runtime requirements.
- README files, this document, and `LICENSE`: public project documentation, not
  mandatory context for every invocation.

No scripts, hooks, service dependencies, or companion skills are required.
Task files belong to the target project. The skill should reference source and
logs rather than copy them, and update progress at meaningful boundaries rather
than on every tool call.

## Validation status — 2026-10-28

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
