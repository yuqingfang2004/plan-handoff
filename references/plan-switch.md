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

## Explain the work to the user

Before a handoff into implementation, explain the change in the final response body, outside and before the model-role block and copyable prompt. The user must be able to assess the approach without opening a file or expanding earlier progress messages. When implementation is directly authorized without a handoff, give the explanation before substantive edits and report the actual outcome at delivery. Cover these points with enough detail to explain the mechanism:

- Where the work stands: overall goal, delivered capabilities, what remains, and why this round is needed.
- The concrete current and intended behavior. For a bug, name the trigger and consequence; distinguish an established cause from a hypothesis.
- How the change works: trace a representative input or action through the responsible components, the checks/decisions or state changes being altered, and the resulting output. Explain the important failure/edge path and why this approach is suitable. Name functions/classes only when verified and useful, with their responsibilities; file lists, "add validation", "optimize the flow" or "fix and add tests" do not explain a mechanism. If the mechanism is still unknown, state what must be inspected and what the result would decide; do not invent implementation details.
- A concrete scenario that will demonstrate the result, plus material uncertainty or an action the user actually needs to decide.

Use descriptive task and finding names. Optional IDs belong after the description, such as "Preserve navigation after a failed deletion (R2)"; never ask the user to remember codes alone. For a small change, a few sentences may cover all relevant points; for a substantive change, use connected paragraphs or ordered steps so the mechanism is actually visible. For a complex one, a small before/after example, pseudocode or diagram can help; do not narrate every line of code or every tool call.

Keep the current explanation in the same plan, and make it visible in chat rather than saying only "read the plan". If the preceding handoff already explained unchanged scope, recap only what is needed to understand the current mechanism; do not replace the final explanation with "as discussed" or a plan link. On another review/fix round, explain only the new finding, its concrete effect, the proposed correction and the remaining work. Meaningful scope or approach changes need an updated explanation. Explaining authorized work is not an extra approval gate or a reason to force a model switch.

Before handing off, check the response itself: can the user explain what happens first, which decision changes, what happens on failure, and what concrete result will demonstrate success? If the response only answers what or why, add the missing how before the copyable prompt. This is a completeness check, not an extra user-approval step or a request to disclose private deliberation.

For example, "fix duplicate saves and add tests" is incomplete. A useful proposed approach is: "Two clicks currently start two writes. Set a saving flag before the first write and reject further submissions while it is set. On success, update the list from the returned record; on failure, keep the form values and show the error. Clear the flag in either case so retry works. Test a slow write with two clicks, then a failed write followed by retry. This prevents duplicate submissions in this UI; cross-client duplicates would need a server-side guarantee." Present this as a proposal unless verified, and do not copy its mechanism into unrelated tasks.

## Keep one usable project and environment

Identify and record the established source workspace, applicable environment/dependency manager and lockfiles, and the user's launch entry point before changing them. Task-document directories are not application directories. A new task, stage, model, conversation or review round does not justify creating another repository copy, worktree, virtual environment or dependency tree.

Continue in the existing workspace unless concrete constraints require isolation. Reuse suitable existing environments; legitimate component/platform-specific environments need not be collapsed into one. Check their actual state, then install or update dependencies only when missing, declarations changed, or a diagnosed problem requires repair. Follow the project's existing tooling and pinned dependencies; do not recreate environments or reinstall everything as a ritual for each round.

For software the user will try, record the working directory, environment selection, launch command and relevant URL/port in the plan. Check the existing entry point when resuming. At delivery, give the same usable entry point and any necessary dependency update, restart or changed command, with its reason. Distinguish verified execution from instructions that have not been run; do not claim a running process has loaded new code without checking. Service start/stop and changes to shared branches still require applicable authorization.

When isolation is justified by conflicting dependencies, destructive experiments, concurrent ownership, or explicit project/user requirements, explain the reason before creating it. Record the isolated location, the canonical user-facing project, how results return there, and the retention/cleanup conditions. Avoid copying dependency directories and build caches into temporary source copies unless that is specifically needed. Do not silently promote an experiment directory to the user's new application entry point. Preserve existing artifacts and clean only authorized temporary scope; plan-clean authorization for Markdown plans does not authorize deleting environments or application copies.

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
2. Record the goal, edit boundaries, explicit exclusions, and important interfaces, compatibility constraints, and decision rationale that the implementer must not guess. Explain the intended mechanism to the user as above, while leaving routine coding details to the implementer instead of writing the whole solution in advance.
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

Separate required corrections to agreed behavior/acceptance from optional improvements and new requirements. Required findings must explain a concrete failure or unmet criterion; preferences and speculative additions do not automatically block delivery. Routine corrections within the same scope continue the same plan without restarting full planning. Recommend another review when risk or unresolved evidence justifies it, not simply because a round ended. Once the agreed scope and required checks are satisfied, close the task; keep optional follow-ups explicit rather than growing the acceptance target. Review alone still does not authorize implementation edits.

Report only completed work, actual validation results, unfinished or pending decisions, and the task document's location. Keep full logs in files. If required acceptance checks are incomplete, say "implementation complete, acceptance pending" instead of claiming the entire task is done. Label local tests, remote CI, platform-specific checks, and real service calls separately; none substitutes for another.

Explain the delivered behavior against what was proposed, any deviation and its reason, the evidence, and how the user can try the result. Use meaningful progress descriptions instead of only filenames, test counts or finding IDs.
