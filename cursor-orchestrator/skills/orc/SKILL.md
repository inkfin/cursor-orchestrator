---
name: orc
description: >-
  Explicit-only 主动安排任务: parent plans, specialists execute. Invoke only
  when the user names orc, orchestrate, 编排, or 主动安排任务. Do not write
  AGENTS.md or project `.cursor/rules/`.
disable-model-invocation: true
---

# Orc

**Explicit invocation only.** Apply only when the user asks for `orc`, 编排, or 主动安排任务 (including `/orc`). Once invoked, follow this protocol for the rest of the session.

This skill is how the user opts into **multi-agent plan execution**. The always-on rule does not do that. Do not create or edit AGENTS.md or project `.cursor/rules/`.

Future workflow commands may use the `orc-` prefix. This skill is just `orc`.

The parent judges, plans, dispatches, reconciles, and accepts. After this skill is invoked, specialists execute the plan. Keep dispatch in bounded waves so the session does not accumulate one task per file, command, or follow-up.

## Dispatch to complete the plan

| Work | Lane |
|---|---|
| Local codebase recon (unknown landing or independent hypotheses) | `explorer` |
| External docs, APIs, changelogs, web facts | `librarian` |
| Named CLI: start, stop, submit, poll/watch | `operator` |
| Patrol / 巡查; log harvest | `scout` |
| Architecture, hard debug, consequential review | `oracle` |
| Second verdict when requested or conflict is likely | `oracle-sol` |
| Product-code implementation (non-UI-primary) | `fixer` |
| UI / layout / visual / a11y | `designer` |
| Post-implementation acceptance | `verifier` |

Dispatch by name via `Task`. **Leaf agents never delegate.** Do not split one question by file cluster.

`operator` is named CLI control (including poll/watch). `scout` is patrol/巡查 and log harvest. Do not swap them. One-click patrol is skill `orc-patrol`.

Parent may skip a lane only when the answer is already in this session, the user forbade subagents, or the work is a declared `prototype-lite` scratch path.

## Route by task shape

1. **Read-only investigation.** One lane for one search space; 2–3 parallel lanes only for independent hypotheses or separate sources. No writer.
2. **Scratch prototype.** Follow `prototype-lite`.
3. **Collaborative debugging.** Follow `collab-debug`. Do not dispatch a writer to guess a fix before reproduction identifies a code cause.
4. **Plan execution.** Parent writes the plan. `fixer` / `designer` execute bounded slices with the task contract. Use `deepwork` for genuinely large or coordinated work. Close with one parallel acceptance wave.

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

1. **One recon wave.** Use one lane for one search space, or 2–3 parallel lanes for independent hypotheses. Give each a distinct question. Do not combine a lane with parent Read/Grep over the same scope in the dispatch turn. While lanes run, the parent does not repeat their searches. Resume the same lane for a follow-up instead of opening another.
2. **One implementation wave.** Default to one foreground writer. Parallel local-worktree writers require independent packages and non-overlapping ownership. Mutating `operator` transactions also run foreground; long observation belongs to `goal-watch`.
3. **One acceptance wave.** Run one `verifier` plus one focused reviewer by default, or up to three focused reviewers for 2–4 reviewers total. They work in parallel against the same immutable diff/commit with orthogonal claims. Do not clone the same review prompt.
4. **Reconcile once.** Conflicts get resolved, never averaged away. One repair → re-review cycle is allowed.
5. **Oracle.** Use `oracle` for architecture, hard debug, experiment conclusions, or public-contract review. `oracle-sol` only if the user asks or conflict is likely.
6. **Experiment transactions.** One `operator` task covers a complete named transaction (for example preflight → dry-run → create → initial inspect). Derive its idempotency key from operation + resource + expected prior generation. One `scout` task snapshots all related runs into files; resume that scout once if only its selector/command was wrong. Do not create a task per CLI command or unchanged patrol.
7. **Artifact-first.** Raw platform JSON, logs, and long test output go to declared paths. Specialist reports return compact conclusions and paths, not dumps.
8. **Plan → execute.** Apply `verification-planning` before non-trivial writers.

## Status

Report progress in one ordinary sentence. Do not report `dispatched (N lanes)`.
