# plan-handoff

[Chinese README](README.zh-CN.md)

A lightweight Agent Skill for **planning, manually switching models, and resuming implementation from one task document**.

This project started with a practical frustration: running an entire development workflow with Astra and Superpowers made even a Pro allowance feel tight. We wanted to reserve the higher-cost model for important decisions and let a more economical model handle the implementation work.

plan-handoff turns that division into a resumable plan. For example, let Astra plan, then manually switch to 6.1 Sol for implementation. If implementation calls for a significant design deviation or encounters a hard-to-diagnose problem, record the evidence and open questions, then manually switch back to Astra for a decision. For high-risk changes, return to Astra for a final review after implementation and verification. You can still use Superpowers for planning or debugging; this independent skill handles the handoff.

A manual relay needs no automatic subagent dispatch, avoiding the extra agent contexts, task distribution, and report aggregation that such orchestration would introduce. The task document carries scope, key decisions, progress, and verification evidence; source files and logs are read as needed. You choose the models and when to switch.

**Put the reasoning where it matters. Make the budget count.**

This example uses Astra and 6.1 Sol. You make every model switch manually:

```mermaid
---
config:
  htmlLabels: false
---
flowchart TD
    A["Astra<br/>Plan and design"] --> B["You review the plan<br/>and switch models"]
    B --> C["6.1 Sol<br/>Implement and verify<br/>Update the task document"]
    C --> D{"Design deviation<br/>or difficult bug?"}
    D -->|Yes| E["Record evidence<br/>and open questions<br/>Ask Astra to assess"]
    E --> F["You approve the plan<br/>and switch back to Sol"]
    F --> C
    D -->|No| K["Implementation and<br/>verification complete"]
    K --> G{"High-risk change?"}
    G -->|Yes| H["Astra: final review<br/>Check diff and evidence"]
    G -->|No| I["Review as needed<br/>Deliver the result"]
    H --> J{"Revisions needed?"}
    J -->|Yes| L["Record revision items<br/>Switch back to Sol"]
    L --> C
    J -->|No| I
```

## How to use

1. Ask the agent to use `plan-handoff` to plan a task. It examines the relevant project context and writes a concise plan, without implementing the change.
2. Review the plan and manually select the implementation model.
3. Ask the agent to read that plan and implement it. It checks the workspace, continues authorized work, and records verification results.
4. For significant design deviations or hard-to-diagnose problems, update the task document with evidence and open questions, then manually return to the planning model for a decision before continuing.
5. For high-risk changes, manually return to the planning model for a final review after implementation and verification. The reviewer checks changes and evidence against the plan; review other changes as needed.

Example prompts in Codex after installation:

```text
Use $plan-handoff to plan adding CSV export. Save the task document to
handoffs/2026-10-29-csv-export/plan.md. Plan only; I will switch models before implementation.

[After switching models]
Use $plan-handoff to implement handoffs/2026-10-29-csv-export/plan.md.
```

The same conversation and a fresh conversation can both use the task file. New sessions need access to the project, plan, and applicable instructions. Invocation syntax depends on the host.

## Installation

Put this folder in your client's skill directory under the name `plan-handoff`. Keep [SKILL.md](SKILL.md) and [templates/plan.md](templates/plan.md) together. Skill instructions, discovery and display metadata, and the task template are in English. A Chinese README is available separately.

For Codex, a user-level location is `~/.agents/skills/plan-handoff`. Once you have downloaded or cloned the repository, you can copy its files there. For a development checkout on Linux or macOS, an alternative is a symbolic link:

```sh
# Replace the source path with your actual checkout. The target must not exist.
mkdir -p "$HOME/.agents/skills"
ln -s /absolute/path/to/plan-handoff "$HOME/.agents/skills/plan-handoff"
```

Restart or refresh the client if it does not discover the skill. For other clients, follow their skill installation instructions. You can also explicitly ask an agent to read `SKILL.md` from your checkout without installing it.

[agents/openai.yaml](agents/openai.yaml) supplies optional Codex display metadata. The workflow does not depend on it. Other hosts may ignore or omit it; format portability does not establish tested integration with every client.

## What belongs in the task document

Each task gets one dedicated `plan.md`, using the [plan template](templates/plan.md). Existing user plans, notes, and handoffs are reference sources; the skill does not rewrite them as progress logs unless explicitly asked. Record scope, baseline, decisions, acceptance criteria, current state, and the next handoff. Reference source and logs instead of copying them.

By default, create `handoffs/YYYY-MM-DD-<topic>/plan.md` in the target project. Different tasks use different folders; the filename stays `plan.md`. Honor a user-designated location and keep existing dedicated plans at their current paths, including legacy paths.

| Situation | What happens |
| --- | --- |
| Switch model or conversation, resume another day, implement, or review | Update the same plan |
| Revise the approach or fix acceptance failures within the same goal | Update the same plan and preserve important decision changes |
| Add an independently deliverable goal or subtask | Create a linked plan in a new task folder |
| Replace the goal entirely | Create a successor and mark the old plan superseded, not completed |
| Discover incomplete work behind a completion claim | Reopen the original plan and mark invalid evidence |
| The document becomes long | Consolidate current state; do not create another version just for length |

Update progress in place and keep concise decision history. Completed plans stay at stable paths. With multiple tasks, use one lightweight collection index (normally `handoffs/index.md`) for links, goal summaries, and statuses; detailed state stays in each plan. Small tasks can combine template sections.

## Handoff prompts

At each actual handoff, the agent updates the plan and supplies its exact path, a suggested role, and a copyable prompt. It uses your model preferences, or generic role names if none are known. These are manual switches, not automatic dispatch:

- **Ready to implement:** suggest a more economical implementation model; the prompt asks it to check the workspace, implement the confirmed scope, verify it, and update the same plan. Any pending approval is stated explicitly.
- **Decision needed:** suggest returning to the planning model; the prompt points to the specific question, evidence, attempted approaches, and options. It asks for a decision, not unauthorized implementation.
- **Review requested or recommended for high risk:** suggest a review model; the prompt asks it to inspect changes and evidence and record findings without editing implementation files.

Planning completion does not grant execution permission. Ordinary implementation steps do not repeatedly ask you to switch, and a review recommendation does not start another model call.

## Scope and validation

This repository contains instructions and a template. It has no runtime scripts, hooks, API calls, automatic model routing, or required companion skills. Instructions guide the agent; they are not a sandbox or an enforced permission system.

Current validation covers metadata and local links, relocation of the core without Codex metadata, and one live manual planning-to-implementation handoff that correctly concluded no repository update was needed. That trial used file-based invocation rather than installed-skill discovery.

Changed-code execution, conflicting workspaces, fresh-session handoffs, other clients, and cost savings have not yet been independently evaluated. No token or cost reduction is claimed. See [design and validation notes](DESIGN.md).

## Contributing

Report a concrete situation, expected behavior, and observed behavior. Prefer a small example and redact private project data. Changes should keep the core short, preserve user authorization, and avoid adding dependencies without a demonstrated need.

## Related work

The design discussion considered [Planning with Files](https://github.com/OthmanAdi/planning-with-files), [handoff-skill](https://github.com/ToolMonsters/handoff-skill), [OpenSpec](https://github.com/Fission-AI/OpenSpec), and [Spec Kit](https://github.com/github/spec-kit). They are references, not bundled dependencies.

## License

[MIT](LICENSE).
