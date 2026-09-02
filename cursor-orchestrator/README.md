# cursor-orchestrator

Cursor-native **policy pack** for specialist-lane orchestration (OMO-style hub-and-spoke without a separate runtime).

It provides:

- **8 custom subagents** under `agents/` (including independent `verifier`)
- **4 workflow skills** under `skills/`
- **Task-contract hook** under `hooks/` (writer dispatch guard)
- One always-on routing rule under `rules/`

Models live in each agent's `model:` frontmatter. Context7 and other MCP servers are not bundled; install them separately.

Herdr fleet management, peer mailbox files, and session hooks stay outside this plugin.

## What v0.2 adds

- **Single-writer default** — UI to `designer`, implementation to `fixer`; parent does not edit owned paths while a writer runs
- **Local worktree parallel** only when packages are independent, paths do not overlap, and there are no shared schema/lock/generated files, and each writer carries a real `git_branch`; **cloud subagents forbidden**
- **Independent `verifier`** lane after reconciliation
- **Hooks** enforce writer task contracts (Owned paths, Scope, Verification, Execution mode)
- **Skills** for verification planning, deep work, reflection, and GUI canvas output

## This plugin lives in a marketplace repo

This directory is the plugin: `.cursor-plugin/plugin.json` plus the default
`agents/`, `rules/`, `skills/`, and `hooks/` folders.

The **repository root** one level up is the marketplace: it holds
`.cursor-plugin/marketplace.json`, which lists this plugin with
`"source": "cursor-orchestrator"`.

That manifest is schema-validated with `additionalProperties: false`, so any
unsupported key makes the marketplace index zero plugins without reporting an
error. See the [repo README](../README.md) for the allowed keys.

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

On local `agent` 2026.08.11-e8db854, `--plugin-dir` discovers the 8 agents but does **not** inject this plugin's rules or skills into the session. The official continual-learning plugin's skill shows the same gap — a current CLI/component limitation.

```bash
agent --plugin-dir /path/to/cursor-orchestrator/cursor-orchestrator ...
```

Some builds also accept `cursor-agent --plugin-dir`. Do not treat `--plugin-dir` as a full component load.

After IDE local or marketplace install, run **Developer: Reload Window** and confirm rule, skills, and hooks in Customize.

## Orchestration model

| Role | Responsibility |
|---|---|
| Parent agent | Judge, plan, dispatch, reconcile, accept |
| `fixer` / `designer` | Sole writers (foreground); require full task contract |
| `verifier` | Independent read-only acceptance |
| Other lanes | Read-only or ops; leaf agents never delegate |

**Parallel writers** use Cursor native **local worktree** isolation only, and every parallel writer must be dispatched with a real non-empty `git_branch`. Parent integrates sequentially.

## Agents (8)

| Agent | Role |
|---|---|
| `explorer` | Codebase recon (read-only) |
| `librarian` | External docs (read-only) |
| `fixer` | Implementation writer |
| `designer` | UI writer |
| `oracle` / `oracle-sol` | Strategic judgment (read-only) |
| `operator` | Named CLI / CI / logs (no repo writes) |
| `verifier` | Post-implementation verification (read-only) |

## Skills (4)

| Skill | When |
|---|---|
| `verification-planning` | Auto — before non-trivial changes |
| `deepwork` | Large refactors; local worktree allocation |
| `reflect` | Explicit only — process retrospective |
| `visual-analysis` | GUI canvas for standalone analytical reports (IDE surface only) |

## Hooks

`hooks/hooks.json` runs `task-contract-guard.py` on two events.

**`subagentStart`** (matcher `fixer|designer`):

- Validates **Owned paths**, **Scope**, **Verification**, **Execution mode**
- Parallel/worktree work requires a real non-empty `git_branch` in the dispatch payload; task text describing a local worktree is not accepted. `is_parallel_worker: true` counts as parallel even when the text says `Execution mode: single`
- Rejects cloud execution in the task text and any `git_branch` containing `cloud`

**`preToolUse`** (matcher `Task`):

- Denies `Task` dispatches with `environment: cloud` (case-insensitive) or an explicit cloud-execution request in the prompt
- Local `Task` dispatches pass through; the writer contract itself is still enforced at `subagentStart`, not here

Both entries set **`failClosed: true`** — a hook crash or invalid JSON **denies** dispatch (safer default; requires `python3` on PATH when the hook fires).

The hook guards contracts only; it does not store state or merge branches.

## Models and Router

| Agent | Model |
|---|---|
| `fixer`, `designer` | `grok-4.6[effort=high,fast=false]` |
| `explorer` | `composer-2.5[fast=true]` |
| `verifier` | `composer-2.5[fast=false]` |
| `oracle` | `auto-smart[optimize_for=intelligence]` |
| `oracle-sol` | `gpt-5.6-sol[effort=high,fast=false]` |
| `librarian`, `operator` | `auto-smart[optimize_for=cost]` |

**`auto-smart`** routes via Cursor's model router. It requires **Teams or Enterprise** with Router enabled. Without Router, Cursor falls back to the workspace default model — behavior is less predictable; prefer explicit model slugs for critical lanes if Router is unavailable.

## GUI Canvas vs CLI

The `visual-analysis` skill produces interactive **Canvas** (`.canvas.tsx`) in the Cursor IDE using `cursor/canvas` primitives and theme tokens.

Its frontmatter declares `metadata.surfaces: [ide]`, so the skill is scoped to the IDE and should not be assumed to load in **CLI / headless** sessions. The structured-markdown equivalent described inside the skill is this plugin's general reporting policy for headless runs, not a guarantee provided by the skill itself. Canvases are never created in headless mode.

## Layout

```text
<repo root>/
├── .cursor-plugin/marketplace.json   # marketplace: lists the plugin below
├── cursor-orchestrator/              # this plugin
│   ├── .cursor-plugin/plugin.json
│   ├── agents/                       # 8 subagents
│   ├── skills/                       # 4 skills
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

**Cursor UI reload** is not automated here. After install, use **Developer: Reload Window** and confirm agents/skills/hooks appear in Customize. Hook behavior requires dispatching a `fixer` or `designer` subagent in a GUI session.

## Publishing

| Channel | What it needs |
|---|---|
| Local symlink | Symlink this plugin subdirectory |
| Team Marketplace | Admin Import from Repo; `marketplace.json` entry pointing at this subdirectory |
| Public Marketplace | Public git repo + [submit](https://cursor.com/marketplace/publish) + review on every update |

Public listing also wants this repo public, a clear README, and preferably a
logo referenced from `plugin.json`. Keep `name` kebab-case and unique.
