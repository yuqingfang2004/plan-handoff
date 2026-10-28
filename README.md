# plan-handoff

[中文说明](README.zh-CN.md)

A lightweight Agent Skill for **planning, manually switching models, and resuming implementation from one task document**.

This project started with a practical frustration: running an entire development workflow with Astra and Superpowers made even a Pro allowance feel tight. We wanted to reserve the higher-cost model for important decisions and let a more economical model handle the implementation work.

plan-handoff turns that division into a resumable plan. For example, let Astra plan, then manually switch to 6.1 Sol for implementation. If implementation calls for a significant design deviation or encounters a hard-to-diagnose problem, record the evidence and open questions, then manually switch back to Astra for a decision. For high-risk changes, return to Astra for a final review after implementation and verification. You can still use Superpowers for planning or debugging; this independent skill handles the handoff.

A manual relay needs no automatic subagent dispatch, avoiding the extra agent contexts, task distribution, and report aggregation that such orchestration would introduce. The task document carries scope, key decisions, progress, and verification evidence; source files and logs are read as needed. You choose the models and when to switch.

**Put the reasoning where it matters. Make the budget count.**

This example uses Astra and 6.1 Sol. You make every model switch manually:

```mermaid
flowchart TD
    A["Astra: planning and key design decisions"] --> B["You review the plan and switch models"]
    B --> C["6.1 Sol: implement, verify, and update the task document"]
    C --> D{"Significant design deviation or hard-to-diagnose problem?"}
    D -->|Yes| E["Record evidence and open questions; return to Astra"]
    E --> F["You approve the revised plan and switch back to Sol"]
    F --> C
    D -->|No, implementation and verification complete| G{"High-risk change?"}
    G -->|Yes| H["Astra: final review of the diff and verification evidence"]
    G -->|No| I["Review as needed and deliver"]
    H --> J{"Revisions needed?"}
    J -->|Yes, record revision items| C
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
plans/csv-export.md. Plan only; I will switch models before implementation.

[After switching models]
Use $plan-handoff to implement plans/csv-export.md.
```

The same conversation and a fresh conversation can both use the task file. New sessions need access to the project, plan, and applicable instructions. Invocation syntax depends on the host.

## Installation

Put this folder in your client's skill directory under the name `plan-handoff`. Keep [SKILL.md](SKILL.md) and [templates/task.md](templates/task.md) together. The runtime content is currently written in Chinese, with a bilingual discovery description.

For Codex, a user-level location is `~/.agents/skills/plan-handoff`. Once you have downloaded or cloned the repository, you can copy its files there. For a development checkout on Linux or macOS, an alternative is a symbolic link:

```sh
# Replace the source path with your actual checkout. The target must not exist.
mkdir -p "$HOME/.agents/skills"
ln -s /absolute/path/to/plan-handoff "$HOME/.agents/skills/plan-handoff"
```

Restart or refresh the client if it does not discover the skill. For other clients, follow their skill installation instructions. You can also explicitly ask an agent to read `SKILL.md` from your checkout without installing it.

[agents/openai.yaml](agents/openai.yaml) supplies optional Codex display metadata. The workflow does not depend on it. Other hosts may ignore or omit it; format portability does not establish tested integration with every client.

## What belongs in the task document

Use the project's existing plan, or start with the [task template](templates/task.md). Record the goal, boundaries, workspace baseline, important decisions, tasks, acceptance conditions, current state, and next step. Reference source files and logs instead of copying entire transcripts or implementations.

Task documents live in the target project, not in this skill's installation folder. Adjust the detail to the task; a small change does not need a large plan.

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
