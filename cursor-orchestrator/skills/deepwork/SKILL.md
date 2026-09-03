---
name: deepwork
description: >-
  Orchestrate large refactors and multi-package implementation — phase gates,
  writer ownership, local worktree allocation, sequential integration, and
  bounded repair. Use for changes spanning many files, modules, or coordinated
  workstreams. Cloud execution is forbidden.
---

# Deep work

Use for **large** implementation: multi-module refactors, new subsystems, coordinated API + client changes, or any work that might tempt unsafe parallel writes.

## Do not use

Do not use deepwork for small demos, throwaway research spikes, typo/comment edits, or a bounded single-session slice. Route those through the lighter workflow instead; do not add pilot or phase-gate ceremony.

## Phase gates

Work proceeds in order; do not skip gates.

1. **Recon** — `explorer` maps touch points, shared files, and risks.
2. **Plan** — parent defines packages, owned paths, integration order, verification per package.
3. **Allocate** — decide single-writer vs local worktree parallel (see below).
4. **Execute** — dispatch writer(s) with full task contracts.
5. **Integrate** — parent applies worktree results **one package at a time** in declared order.
6. **Verify** — `verifier` after each integration step (or once at end if packages are truly independent and evidence is per-package).

## Single writer (default)

When in doubt, use one `fixer` (or `designer` for UI-only) with a single **Owned paths** list and **Execution mode: single**.

## Local worktree parallel (strict)

Enable only when **all** hold:

- ≥2 independent work packages with no write-order dependency during implementation
- Non-overlapping **Owned paths** per writer
- No shared schema, lock, or generated files across packages

Before broad parallel dispatch, pilot the contract and evidence path on one representative, non-trivial work package. Fix ownership or verification gaps first. Do not require a pilot for demos, typos, or other trivial work.

For each parallel writer:

- **Execution mode:** `parallel/worktree`
- A real non-empty **`git_branch`** in the dispatch — describing a local worktree in the task text does not satisfy the hook
- Full contract: Owned paths, Scope, Verification

Parent responsibilities:

- Name integration order before dispatch
- Merge or apply results sequentially — never auto-merge
- Re-run targeted verification after each integration

## Forbidden

- **Cloud subagents** (`environment: cloud`, cloud worktrees) for implementation — the `preToolUse` hook on `Task` denies these before dispatch, and also denies writer Tasks that omit the four contract fields
- Overlapping owned paths across parallel writers
- Writers dispatching further subagents

## Repair budget

| Stage | Max rounds |
|---|---|
| Per-writer self-repair | 2 |
| Post-integration fix | 1 |
| Verifier fail → repair → re-verify | 1 |

Exhausted budget → stop, report, escalate to `oracle` / `oracle-sol` if needed.

## Status reporting

Use orchestration vocabulary: *plan ready* → *dispatched (N lanes)* → *reconciled* → *verified*.
