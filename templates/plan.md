# Task name

> Save as plan.md in this task's folder, or continue its existing dedicated plan at its current path. User-owned plans and notes are reference sources, not this progress log unless explicitly requested. Combine sections for small tasks and remove inapplicable fields. Paths are relative to the project root below unless stated otherwise. Do not paste entire source files or logs.

- Task ID and last updated:
- Task status: awaiting planning / in progress / blocked / completed / cancelled / superseded.
- Current stage: planning / implementation / review.
- Related plans (parent, dependency, predecessor, or successor), if any:

## Goal and scope

- Goal and observable completion outcome:
- Included and excluded work:
- Existing authorization and actions requiring separate confirmation:

## Explain this round

> Keep a concise explanation the user can understand, and present it in the final handoff response body before the model-role block and prompt; earlier progress messages and this file are not substitutes. For directly authorized work, explain before editing. Prefer descriptive names to codes. On subsequent rounds, update the new difference rather than repeating the whole history.

- Overall goal, delivered capabilities and what remains; why this round is needed:
- Current behavior/problem and intended outcome; established facts versus hypotheses:
- Implementation walkthrough: representative input/action → responsible components and changed checks/state → output; important failure/edge path and why this approach fits (mark unknowns):
- Concrete validation scenario and any unresolved decision:

## Workspace

- Project root and cross-machine path mappings, if applicable:
- Branch and baseline commit, or input artifact version:
- Existing uncommitted changes, their ownership, and anything uncertain:
- Applicable project rules and relevant files or symbols:
- Source plans or handoff notes and the confirmed constraints taken from them:
- Existing environment(s), dependency manager and lockfiles; reuse/update needs (record locations, not secrets):
- Stable user entry point, when applicable: working directory, environment selection, launch command, URL/port; what was actually verified:
- If isolation is necessary: reason, canonical/temporary locations, integration path and authorized cleanup conditions. Otherwise continue in the existing project; do not copy it into the task-document folder.

## Decisions and open questions

| Item | Decision or question | Evidence or path | Effect on implementation |
| --- | --- | --- | --- |
| Record necessary items | Distinguish confirmed decisions, proposals, and unknowns | Reference only relevant evidence | Whether it affects implementation and why |

## Implementation and acceptance

Suggested statuses: not started, in progress, implementation complete / acceptance pending, acceptance passed, blocked, or not applicable with a reason. Each item should describe a verifiable outcome. Add rows as needed.

| Item | Affected files or artifacts | Validation method and passing condition | Current status | Evidence location |
| --- | --- | --- | --- | --- |
| Describe the deliverable | Location and necessary interface constraints | Observable behavior and how to check it | Not started | Not run |

## Current progress and next step

- Current completed work (replace stale summaries rather than appending every session):
- In progress, awaiting acceptance, or blocked; write "none" if empty:
- Actual behavior versus the proposed change, any deviation and reason; how the user can try it and any required restart/dependency update:
- Next stage: planning/decision / implementation / review / finished.
- Required model role: planning model / implementation model / review model / none; preferred model if known:
- Manual action: select the required role's model; if already selected, no switch is needed.
- Exact plan path and project root for the next conversation:
- Copyable next prompt: explicitly repeat the NEXT STAGE and MODEL ROLE, this plan's path, stage-specific action, and authorization limits:
- Changes affecting the plan and their authorization or evidence, if any:

## Validation record

Include only evidence relevant to this task. Note when new changes invalidate earlier results; do not present historical results as current acceptance.

| Tested version or snapshot, including relevant uncommitted changes | Environment and scope | Command or inspection method | Result and exit code, if applicable | Log or artifact path |
| --- | --- | --- | --- | --- |
| Record the actual version | Local or remote, platform, and other relevant context | What was actually executed | Not run | None |

Incomplete acceptance checks and reasons:

Review conclusion and scope, only when the user requests a review: distinguish required acceptance fixes from optional improvements and new requirements; explain findings with descriptive names and concrete consequences.

Completion or closure summary, when applicable: outcome, remaining limits, evidence, and follow-up link. Reopening or superseding the task must retain the reason and identify any invalid prior acceptance.
