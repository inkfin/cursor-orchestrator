---
name: orc
description: >-
  Explicit-only 主动安排任务: specialist-lane orchestration. Invoke only
  when the user names orc, orchestrate, 编排, or 主动安排任务. Follow
  dispatch-by-default for the rest of the session; do not write AGENTS.md
  or project `.cursor/rules/`.
disable-model-invocation: true
---

# Orc

**Explicit invocation only.** This skill is 主动安排任务 (active task arrangement / dispatch). Apply this protocol only when the user asks for `orc`, 编排, or 主动安排任务. Once invoked, the parent follows it for the rest of the session.

This is a skill, not a project rule. Do not create or edit AGENTS.md or project `.cursor/rules/`.

Future workflow commands may use the `orc-` prefix. This skill is just `orc`.

This skill overrides Cursor's default "do the work yourself / skip Task for narrow questions" whenever a named specialist lane matches.

The parent agent judges, plans, dispatches, reconciles, and accepts. It does not substitute its own tools for a matching lane.

## Dispatch by default

| Work | Lane |
|---|---|
| Local codebase recon, call paths, how-X-works | `explorer` |
| External docs, APIs, changelogs, web facts | `librarian` |
| Named CLI: start, stop, submit, poll/watch experiments, PRs, deploys | `operator` |
| Patrol / 巡查 vs criteria; log harvest to local files | `scout` |
| Architecture, hard debug, consequential review | `oracle` |
| Hard-to-reverse second verdict (with `oracle`) | `oracle-sol` |
| Product-code implementation (non-UI-primary) | `fixer` |
| UI / layout / visual / a11y | `designer` |
| Post-implementation acceptance | `verifier` |

Dispatch by name via `Task`. **Leaf agents never delegate.** One-click patrol is skill `orc-patrol`; `orc` may still dispatch `scout` for log harvest mid-session.

`operator` is named CLI control (including poll/watch). `scout` is patrol/巡查 and log harvest. Do not swap them.

Parent may act directly only when:

- The answer is already in this session's context
- The user @-mentioned or attached specific files (those files only; broader recon still goes to `explorer`)
- The change is a single-file comment, typo, or rename with no behavior change
- The user explicitly forbids subagents
- Scratch paths declared under `prototype-lite`

Do not Grep/Read the tree to answer a recon question. Do not edit product files that belong to `fixer` or `designer`.

## Route by task shape

Use the lightest **lane path** that fits, not the lightest excuse to skip dispatch:

1. **Read-only investigation.** `explorer` / `librarian`. No writer or verifier.
2. **Scratch prototype.** Follow `prototype-lite`. The parent may write only to explicitly declared scratch or temporary paths. Product code is off-limits.
3. **Collaborative debugging.** Follow `collab-debug`. Do not dispatch a writer to guess a fix before reproduction identifies a code cause.
4. **Formal implementation.** `fixer` / `designer`, the task contract, verification planning, and independent verification. Use `deepwork` only for genuinely large or coordinated work.

If a prototype is promoted to product code, stop the scratch path and rewrite **Scope**, **Owned paths**, and **Verification** before dispatching the appropriate writer. Scratch permission never authorizes the parent to edit product code.

## Single-writer model

Default: **one writer at a time**.

Writers run **foreground** (`is_background: false`). While a writer is active, the parent **must not edit that writer's owned paths**.

Every writer task **must** include all four contract fields (enforced by hook):

- **Owned paths:** exclusive file/directory globs this writer may touch
- **Scope:** what to change and what to leave alone
- **Verification:** exact commands or evidence to produce
- **Execution mode:** `single` (default) or `parallel/worktree`

Hand `fixer` and `designer` bounded instructions only. Open-ended work does not go to a cheap lane.

## Parallel execution (local worktree only)

Use Cursor **native local worktree** isolation only when **all** are true:

1. At least **two independent work packages** with no ordering dependency during implementation
2. **Non-overlapping owned paths** per writer
3. **No shared** schema, lock, or generated files across packages

When parallel:

- Set **Execution mode** to `parallel/worktree` in each writer task
- Provide a real non-empty **`git_branch`** per writer. Task text describing a local worktree is not accepted
- Parent defines owned paths, integration order, and merge sequence
- Apply results **sequentially**, then verify after each integration step

**Cloud subagents are forbidden.** Do not dispatch `environment: cloud` or cloud worktrees for implementation writers. A `preToolUse` hook on the `Task` tool denies cloud execution and incomplete writer contracts. A `git_branch` containing `cloud` is denied as well. `subagentStart` repeats the same writer checks when that event fires.

For large refactors, follow the `deepwork` skill (phase gates, worktree allocation, repair budget).

## Dispatch discipline

1. **Recon before plan.** For **formal non-trivial implementation** only, dispatch `explorer` before planning. Do not plan that path from guesses. This does not override lighter routes: read-only investigation, scratch prototype, and collab diagnosis skip full recon.
2. **Read-only lanes in background.** `explorer`, `librarian`, `oracle`, `oracle-sol`, `operator`, and `scout` may run in background. Writers and `verifier` run foreground.
3. **Reconcile before proceed.** When specialist reports return, reconcile them against the plan. Conflicts get resolved (re-dispatch or judge), never averaged away.
4. **Dual-oracle rule.** For hard-to-reverse decisions, dispatch `oracle` and `oracle-sol` together, then synthesize. If they disagree, surface the disagreement explicitly.
5. **Plan → execute split.** Parent writes the concrete plan; writers execute bounded slices.
6. **Independent verification.** After writers finish and the parent reconciles, dispatch **`verifier`** (not the writer) to check requirements, final diff, test/build evidence, and edge cases. Escalate hard findings to `oracle`.
7. **Non-trivial changes.** Before implementation, apply the `verification-planning` skill (claims, evidence paths, validation owner, budget).

## Status vocabulary

Report progress as: *recon in flight*, *plan ready*, *dispatched (N lanes)*, *reconciled*, *verified*.
