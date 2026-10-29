# plan-switch

Read this for planning, implementation, recovery, or review. Use the mandatory handoff block in [SKILL.md](../SKILL.md) whenever the next stage needs another role.

## Select the stage

Follow the current user request. The stage recorded in the task document provides recovery context, not new authorization.

| Request | Action |
| --- | --- |
| Plan first or prepare a handoff | Complete the plan and return it to the user without implementing the change |
| Implement an existing plan or continue authorized implementation | Check the workspace and continue without requesting the same approval again |
| Review delivered work | Check changes and evidence, then report findings; a review request does not authorize edits |

Ask one brief question only if the request and existing authorization do not establish the stage and the answer would determine whether project files should be modified. Do not infer the stage from a model name or claim to have switched or verified the model selected in the user's interface.

## Maintain one dedicated plan per task

Use a dedicated `plan.md`, separate from the user's existing plans, notes, and handoff documents. Treat those as reference sources: link them and extract only the confirmed constraints needed to proceed, without turning them into progress logs. An explicit user instruction to edit a particular file takes precedence.

First check for this task's existing dedicated plan. Continue it even at a legacy path; do not automatically rename or migrate it. For a new task, use the [plan template](../templates/plan.md) at the user-designated location, or `handoffs/YYYY-MM-DD-<topic>/plan.md` in the target project. The date is the creation date; keep the path stable. Distinguish tasks by their folders, never overwrite an unrelated plan, and never store project plans in this skill's installation directory. Identify a match by its goal and acceptance criteria, not just modification time. Clarify only when ownership or identity remains ambiguous.

Decide whether the work still has the same goal and completion criteria:

| Situation | Document action |
| --- | --- |
| Switch model, conversation, date, or stage; resume after a workspace change | Continue the same plan; check evidence applicability |
| Refine the same goal, fix acceptance failures, or address review findings | Update the same plan; retain the rationale and authorization for important changes |
| Add an independently deliverable goal or independently managed subtask | Create a new task folder and plan; link the dependency rather than copying the old record |
| Replace the goal so the old plan no longer applies | Create a successor plan; mark the old one superseded and link both ways, not completed |
| Discover an incorrect completion claim or missing work in the original scope | Reopen the same plan and identify invalid evidence; a separately scoped follow-up can be a linked new task |
| The plan gets long | Consolidate current state and reference detailed evidence; length alone does not create a new plan |

Track an identifier, last update, task status, and current stage. Suggested task statuses are awaiting planning, in progress, blocked, completed, cancelled, and superseded; these differ from the planning/implementation/review stage and per-item acceptance status. Mark completed only when required work and acceptance are done, including review if required. Status and document changes do not authorize new work.

Keep one current entry point per task. Update current progress and next steps in place, retaining short records of important decisions and evidence that became historical or invalid. On completion, retain results, limits, evidence, and follow-up links in place; do not automatically delete, move, or rename the plan. An explicit plan-clean request uses the separate, summary-gated archive workflow. When the collection has multiple tasks, maintain a lightweight `handoffs/index.md` (or the designated collection's equivalent) with links, goal summaries, and statuses. Reuse an existing same-purpose index; do not overwrite an unrelated file. Plans remain authoritative for details. Parent plans summarize dependencies rather than duplicating child progress.

Record only what affects the handoff: scope, key decisions and their rationale, working location, tasks and acceptance criteria, current progress, and the next step. Reference source, diffs, and logs with paths and brief summaries instead of copying whole conversations or implementations. Identify code by paths and symbols, using line numbers only as an aid. Resolve paths against the project root declared in the task document. Check path mappings across machines rather than assuming an old absolute path is valid.

Update the document at handoff, after meaningful progress, when a key decision changes, or when blocked. Read it again when resuming, after relevant changes, or when context is missing; do not inject the entire document before every tool call. Combine template sections for small tasks and omit irrelevant fields.

## Planning

1. Read the request, project rules, and relevant implementation. Distinguish verified facts, design choices, and open questions. If scope is unclear, investigate what does not depend on an answer and ask only questions that affect the plan.
2. Record the goal, edit boundaries, explicit exclusions, and important interfaces, compatibility constraints, and decision rationale that the implementer must not guess. Leave implementation details to the implementer instead of writing the whole solution in advance.
3. Divide the work into verifiable outcomes. Define a validation method and passing condition for each. Use tests, manual checks, or artifact inspection according to risk; do not add tests merely to satisfy a process.
4. Check that every requirement has a corresponding task and mark the next step. Use the explicit handoff format in SKILL.md, then end the planning stage. State whether approval is still pending; a finished plan is not implementation authorization. If the user already requested authorized implementation, continue that stage without inserting another planning approval gate.

## Implementation and recovery

1. Read the task document and applicable project rules. Check the actual directory, relevant files, and current work. For Git projects, check the branch, HEAD, and uncommitted changes; otherwise check input and artifact versions. Compare workspace differences with the task scope instead of stopping merely because a SHA differs.
2. Preserve existing work. Do not repeat completed tasks whose evidence remains applicable. Coordinate first if edit ownership is unclear or another writer could conflict with this task. The skill does not authorize automatic branch switches, cleanup, commits, or publication; follow the user's existing authorization.
3. Continue from the first unfinished task. Handle ordinary implementation choices and diagnosable failures yourself. Investigate failed tests before changing anything, and do not weaken acceptance criteria merely to pass. Rerun only checks affected by the changes or whose evidence is no longer valid.
4. If the goal, agreed public interfaces, safety constraints, or significant architecture decisions must change, record the conflict location, verified evidence, options, and impact, then use the decision handoff in SKILL.md. Continue independent authorized work where possible. If a critical issue persists without new evidence, summarize the attempts and return it to the user rather than retrying indefinitely. Do not independently switch models, dispatch subagents, or contact other sessions.
5. Update each task's status, distinguishing implementation complete from acceptance passed. Record the command or method, result, code or artifact version, and evidence path. For uncommitted code, note the workspace state and retain the relevant diff or snapshot evidence; HEAD alone does not identify the tested version. Mark checks that could not run as "not run" and explain why.

## Review and delivery

Review according to the user's request without automatically making another model call. Compare the actual changes, scope, and acceptance evidence with the plan. For each finding, identify its location, impact, and evidence. If no issues are found, state the review scope and remaining validation limits. If revisions invalidate earlier evidence, rerun the relevant checks.

Report only completed work, actual validation results, unfinished or pending decisions, and the task document's location. Keep full logs in files. If required acceptance checks are incomplete, say "implementation complete, acceptance pending" instead of claiming the entire task is done. Label local tests, remote CI, platform-specific checks, and real service calls separately; none substitutes for another.
