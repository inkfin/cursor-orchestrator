# cursor-orchestrator

Cursor-native **policy pack** for specialist-lane orchestration (hub-and-spoke without a separate runtime). Version **0.4.0**.

It ships:

- **9 custom subagents** under `agents/`
- **9 workflow skills** under `skills/`
- A writer **task-contract hook** under `hooks/`
- One thin always-on rule under `rules/` (research, parallel 验收, and artifact-first experiments)

The parent implements by default. The always-on rule does not dispatch writers to execute a plan; that protocol is the explicit `orc` skill (`/orc`). Research may fan out only across independent questions. Non-trivial acceptance uses one bounded parallel review wave. Experiment control/logs/conclusions flow through `operator` → evidence files, `scout` → log files, and `oracle` → compact decision. Models live in each agent's `model:` frontmatter. Context7 and other MCP servers are not bundled.

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
| `explorer` | Local recon when landing is unknown (read-only, foreground) |
| `librarian` | External docs, APIs, web facts (read-only, foreground) |
| `operator` | One named CLI transaction; raw receipts to evidence files |
| `scout` | One multi-resource patrol snapshot and log harvest |
| `oracle` | Architecture / hard debug / experiment conclusion |
| `oracle-sol` | Second verdict when asked or conflict is likely |
| `fixer` | Product-code writer (non-UI-primary) |
| `designer` | UI / layout / a11y writer |
| `verifier` | Independent 验收: requirements vs diff vs evidence |

Writers (`fixer`, `designer`) run foreground and need the four-field task contract. Parallel writers need a real `git_branch`. Cloud subagents are forbidden. See `rules/orchestration.mdc`.

## Skills (9)

| Skill | When |
|---|---|
| `verification-planning` | Evidence plan and bounded parallel 验收 |
| `deepwork` | Large refactors under `/orc`; local worktree allocation |
| `reflect` | Explicit only, process retrospective |
| `orc` | Explicit only (`/orc`); parent plans, specialists execute |
| `orc-patrol` | Explicit only, 巡查 |
| `visual-analysis` | GUI canvas for standalone analytical reports (IDE only) |
| `prototype-lite` | Throwaway local prototypes in declared scratch paths |
| `collab-debug` | Evidence-driven cross-machine or cross-team diagnosis |
| `goal-watch` | Explicit overnight experiment watching with sparse wakeups |

`goal-watch` details live in that skill. `visual-analysis` is IDE-only (`metadata.surfaces: [ide]`). Additional workflow commands may later use the `orc-` prefix; `orc` and `orc-patrol` are separate skills.

## Hooks

`hooks/hooks.json` runs `task-contract-guard.py` on two events (needs `python3` on PATH).

| Event | Matcher | What it gates |
|---|---|---|
| `preToolUse` | `Task` | Writer contract, parallel `git_branch`, no cloud |
| `subagentStart` | `fixer\|designer` | Same writer contract on surfaces that still emit it |

Non-writer lanes skip the writer contract and only hit the cloud checks. The hook does not store state or merge branches.

Both entries set **`failClosed: false`**, and the command checks that `python3`
and the guard path resolve before running the guard, falling back to an `allow`
verdict when they do not. Cursor reads exit 2 from a permission hook as an
explicit deny, and `python3` also exits 2 when it cannot open the script — so a
mislocated plugin root would otherwise deny **every** `Task` dispatch, read-only
lanes included. Enforcement is unchanged whenever the guard actually runs:
denials and malformed responses still block.

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
