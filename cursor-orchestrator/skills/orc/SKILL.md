---
name: orc
description: >-
  Explicit-only 主动安排任务: parent plans, specialists execute. Invoke only
  when the user invokes orc, orchestrate, 编排, 主动安排任务, or explicitly
  requests specialist execution of a plan. Do not write
  AGENTS.md or project `.cursor/rules/`.
disable-model-invocation: true
---

# Orc

**Explicit invocation only.** Apply only when the user invokes `orc`, `orchestrate`, 编排, or 主动安排任务 (including `/orc`), or explicitly asks specialists to execute a large plan. Mentioning or reviewing these instructions is not invocation. Scope it to one declared goal; do not carry it into later goals.

This skill is how the user opts into **multi-agent plan execution** for a large task with a clear start and finish. The always-on rule does not do that. Do not create or edit AGENTS.md or project `.cursor/rules/`.

Future workflow commands may use the `orc-` prefix. This skill is just `orc`.

Before dispatch, state the goal's **Scope**, **Deliverables**, **Start state**, **Terminal condition**, **Verification**, and **Mutation boundaries**. If these are not clear enough to allocate work safely, clarify or inspect first. `orc` ends when the terminal condition is met, the user cancels it, or explicitly replaces it with another goal. Status questions, clarifications, and corrections within scope do not end it.

On completion, cancellation, or replacement, stop new dispatch for the old goal and record unfinished packages, unintegrated worktrees, evidence paths, and running agents/jobs. Stop or hand off active agents before releasing their owned paths; do not assume cancellation ended their writes. Preserve unintegrated work. Stop external jobs only under existing authorization or the declared terminal action; otherwise report their continuing state. A new goal needs its own opt-in.

The parent judges, plans, dispatches, reconciles, and accepts. Specialists execute the packages that benefit from delegation. Keep dispatch in bounded waves so the goal does not accumulate one task per file, command, or follow-up.

## Dispatch to complete the plan

Use this table only after applying the always-on dispatch and risk gates. Explicit role requests override simple-work defaults, not role boundaries or mutation safeguards.

| Work | Lane |
|---|---|
| Broad cross-subsystem recon or independent hypotheses | `explorer` |
| External docs, APIs, changelogs, web facts | `librarian` |
| Multi-step named control transaction | `operator` |
| Patrol / 巡查 across resources; large log harvest | `scout` |
| Architecture, hard debug, consequential review | `oracle` |
| Second verdict when requested or conflict is likely | `oracle-sol` |
| Product-code implementation (non-UI-primary) | `fixer` |
| UI / layout / visual / a11y | `designer` |
| Post-implementation acceptance | `verifier` |

Dispatch by name via `Task`. **Leaf agents never delegate.** Do not split one question by file cluster.

`operator` is named CLI control (including poll/watch). `scout` is patrol/巡查 and log harvest. Do not swap them. One-click patrol is skill `orc-patrol`.

For automatic dispatch, use only lanes that materially reduce latency, main-context size, independent-risk uncertainty, or transaction coupling. The parent may directly complete small connective work, bounded lookups, and short commands inside an `orc` goal.

## Route by task shape

1. **Read-only investigation.** The parent handles bounded lookup. Use one lane for a broad search space; 2–3 parallel lanes only for independent hypotheses or separate sources. No writer.
2. **Scratch prototype.** Follow `prototype-lite`.
3. **Collaborative debugging.** Follow `collab-debug`. Do not dispatch a writer to guess a fix before reproduction identifies a code cause.
4. **Plan execution.** Parent writes the plan. `fixer` / `designer` execute bounded slices with the task contract. Use `deepwork` for genuinely large or coordinated work. Close consequential changes with one acceptance wave; only a low-risk cumulative change may close with parent review and tests.

If a prototype is promoted to product code, rewrite **Scope**, **Owned paths**, and **Verification**, then dispatch the writer. Scratch permission never authorizes product-code edits by the parent.

## Single-writer model

Default: **one writer at a time**.

Writers run **foreground** (`is_background: false`). While a writer is active, the parent **must not edit that writer's owned paths**.

Every writer task **must** include all four contract fields (enforced by hook):

- **Owned paths:** exclusive file/directory globs this writer may touch
- **Scope:** what to change and what to leave alone
- **Verification:** exact commands or evidence to produce
- **Execution mode:** `single` (default) or `parallel/worktree`

Hand `fixer` and `designer` bounded instructions only.

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

**Cloud subagents are forbidden.** Do not dispatch `environment: cloud` or cloud worktrees for implementation writers. The `preToolUse` hook on `Task` denies cloud execution and incomplete writer contracts. A `git_branch` containing `cloud` is denied as well.

## Dispatch discipline

1. **At most one recon wave.** Skip it when the parent can map the task with bounded lookup. Otherwise use one lane for a broad search space, or 2–3 parallel lanes for independent hypotheses. Give each a distinct question. Do not combine a lane with parent Read/Grep over the same scope in the dispatch turn. While lanes run, the parent does not repeat their searches. Resume the same lane for a follow-up instead of opening another.
2. **One implementation wave.** Default to one foreground writer. Parallel local-worktree writers require independent packages and non-overlapping ownership. Mutating `operator` transactions also run foreground; long observation belongs to `goal-watch`.
3. **One acceptance wave for consequential changes.** Run one `verifier` plus one focused reviewer by default; add reviewers only for distinct high-risk claims, up to four reviewers total. Only a low-risk cumulative change may close with parent review and tests; a small diff never waives consequential-risk or explicit independent-review requirements. Reviewers work in parallel against the same immutable diff/commit with orthogonal claims. Do not clone the same review prompt.
4. **Reconcile once.** Conflicts get resolved, never averaged away. One repair → re-review cycle is allowed.
5. **Oracle.** Apply the always-on judgment threshold before choosing `oracle` for architecture, hard debug, experiment conclusions, or public-contract review. `oracle-sol` only if the user asks or conflict is likely.
6. **Experiment transactions.** Apply the shared mutation safeguards even for parent-owned commands. When dispatch is justified, one `operator` task covers a complete named transaction (for example preflight → dry-run → create → initial inspect). Derive its idempotency key from operation + resource + expected prior generation. One `scout` task snapshots all related runs into files; resume that scout once if only its selector/command was wrong. Do not create a task per CLI command or unchanged patrol.
7. **Artifact-first.** Raw platform JSON, logs, and long test output go to declared paths. Specialist reports return compact conclusions and paths, not dumps.
8. **Plan → execute.** Apply `verification-planning` before consequential writer packages or independent acceptance.

## Status

Report progress in one ordinary sentence. Do not report `dispatched (N lanes)`.
