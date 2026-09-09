# cursor-orchestrator

Cursor-native **policy pack** for specialist-lane orchestration (hub-and-spoke without a separate runtime). Version **0.3.2**.

It ships:

- **9 custom subagents** under `agents/`
- **9 workflow skills** under `skills/`
- A writer **task-contract hook** under `hooks/`
- One always-on routing rule under `rules/`

Routing lives in `rules/orchestration.mdc`. Explicit dispatch is skill `orc`. Models live in each agent's `model:` frontmatter. Context7 and other MCP servers are not bundled.

Herdr fleet management, peer mailbox files, and session hooks stay outside this plugin.

## This plugin lives in a marketplace repo

This directory is the plugin: `.cursor-plugin/plugin.json` plus `agents/`, `rules/`, `skills/`, and `hooks/`.

The **repository root** one level up is the marketplace. It holds `.cursor-plugin/marketplace.json`, which lists this plugin with `"source": "cursor-orchestrator"`.

That manifest is schema-validated with `additionalProperties: false`, so any unsupported key makes the marketplace index zero plugins without reporting an error. See the [repo README](../README.md) for the allowed keys.

## How to install

### GitHub / team marketplace

Import the repository via your team's Cursor marketplace (admin **Import from Repo**). Requires a git remote Cursor can reach (typically GitHub).

### IDE (local user plugin)

Symlink the **plugin directory**, not the repository root:

```bash
mkdir -p ~/.cursor/plugins/local
ln -sfn /path/to/cursor-orchestrator/cursor-orchestrator ~/.cursor/plugins/local/cursor-orchestrator
```

Then **Developer: Reload Window**. Confirm `cursor-orchestrator` in Customize.
Delete any leftover User Rule that still contains the old orchestration
protocol so the plugin rule is the only copy.

On Teams/Enterprise, **Allow Local Plugin Imports** must be on. A marketplace
plugin with the same `name` shadows this local copy.

### CLI

On local `agent` 2026.08.11-e8db854, `--plugin-dir` discovers the 9 agents but does **not** inject this plugin's rules or skills into the session. The official continual-learning plugin's skill shows the same gap, a current CLI/component limitation.

```bash
agent --plugin-dir /path/to/cursor-orchestrator/cursor-orchestrator ...
```

Some builds also accept `cursor-agent --plugin-dir`. Do not treat `--plugin-dir` as a full component load.

After IDE local or marketplace install, run **Developer: Reload Window** and confirm rule, skills, and hooks in Customize.

## Agents (9)

| Agent | Job |
|---|---|
| `explorer` | Local codebase recon (read-only) |
| `librarian` | External docs, APIs, web facts (read-only) |
| `operator` | Named CLI: start, stop, submit, poll/watch |
| `scout` | Patrol / 巡查 and log harvest |
| `oracle` | Last-resort architecture / hard debug / review |
| `oracle-sol` | Second verdict with `oracle` |
| `fixer` | Product-code writer (non-UI-primary) |
| `designer` | UI / layout / a11y writer |
| `verifier` | Post-implementation acceptance (read-only) |

Writers (`fixer`, `designer`) run foreground and need the four-field task contract. Parallel writers need a real `git_branch`. Cloud subagents are forbidden. See `rules/orchestration.mdc`.

## Skills (9)

| Skill | When |
|---|---|
| `verification-planning` | Auto, before non-trivial changes |
| `deepwork` | Large refactors; local worktree allocation |
| `reflect` | Explicit only, process retrospective |
| `orc` | Explicit only; 主动安排任务; user names `orc` / 编排 |
| `orc-patrol` | Explicit only, 巡查 |
| `visual-analysis` | GUI canvas for standalone analytical reports (IDE only) |
| `prototype-lite` | Throwaway local prototypes in declared scratch paths |
| `collab-debug` | Evidence-driven cross-machine or cross-team diagnosis |
| `goal-watch` | Explicit overnight experiment watching with sparse wakeups |

`goal-watch` details live in that skill. `visual-analysis` is IDE-only (`metadata.surfaces: [ide]`). Additional workflow commands may later use the `orc-` prefix; `orc` and `orc-patrol` are separate skills.

## Hooks

`hooks/hooks.json` runs `task-contract-guard.py` on two events. Both set **`failClosed: true`** (needs `python3` on PATH).

| Event | Matcher | What it gates |
|---|---|---|
| `preToolUse` | `Task` | Writer contract, parallel `git_branch`, no cloud |
| `subagentStart` | `fixer\|designer` | Same writer contract on surfaces that still emit it |

Non-writer lanes skip the writer contract and only hit the cloud checks. The hook does not store state or merge branches.

## Models

| Agent | Model |
|---|---|
| `fixer`, `designer` | `grok-4.6[effort=high,fast=false]` |
| `explorer` | `composer-2.5[fast=true]` |
| `verifier` | `composer-2.5[fast=false]` |
| `oracle` | `auto-smart[optimize_for=intelligence]` |
| `oracle-sol` | `gpt-5.6-sol[effort=high,fast=false]` |
| `librarian`, `operator`, `scout` | `auto-smart[optimize_for=cost]` |

**`auto-smart`** requires **Teams or Enterprise** with Router enabled. Without Router, Cursor falls back to the workspace default model.

## Layout

```text
<repo root>/
├── .cursor-plugin/marketplace.json   # marketplace: lists the plugin below
├── cursor-orchestrator/              # this plugin
│   ├── .cursor-plugin/plugin.json
│   ├── agents/                       # 9 subagents
│   ├── skills/                       # 9 skills
│   ├── hooks/
│   │   ├── hooks.json
│   │   └── task-contract-guard.py
│   ├── rules/orchestration.mdc
│   ├── LICENSE
│   └── README.md
├── scripts/validate_plugin.py        # repo tooling, not shipped as a component
├── tests/
├── LICENSE
└── README.md
```

## Validation

Run from the **repository root**:

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```

After install, use **Developer: Reload Window** and confirm agents/skills/hooks appear in Customize.

## Publishing

| Channel | What it needs |
|---|---|
| Local symlink | Symlink this plugin subdirectory |
| Team Marketplace | Admin Import from Repo; `marketplace.json` entry pointing at this subdirectory |
| Public Marketplace | Public git repo + [submit](https://cursor.com/marketplace/publish) + review on every update |

Public listing also wants this repo public, a clear README, and preferably a
logo referenced from `plugin.json`. Keep `name` kebab-case and unique.
