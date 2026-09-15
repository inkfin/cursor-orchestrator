---
name: verification-planning
description: >-
  Plan evidence and a bounded parallel acceptance wave before a non-trivial
  writer under /orc, or before 验收. Skip for parent-owned trivial work.
---

# Verification planning

Use this skill **before** a dispatched writer on a non-trivial change, and before an 验收 gate.

The parent may skip this planning skill for Q&A, known-path edits, ≤3 files, and reproduced small fixes it implements itself (no `/orc`). This does not waive the always-on acceptance wave when the user asks for 验收 or a non-trivial behavior change is being declared done.

Trivial = single-file typo, comment-only edit, rename with no behavior change, or a reproduced small fix the parent is doing.

## Exemptions

Throwaway prototypes, read-only investigations, and pure environment diagnosis may skip the full plan and acceptance wave. Record one sentence explaining which exemption applies. Promotion to product code ends the exemption.

## Produce a verification plan

Output a short plan with these sections:

### 1. Claims

List each user-facing or behavioral claim the change must satisfy. One line per claim, testable wording.

### 2. Evidence paths

For each claim, name how to prove it:

| Claim | Evidence type | Command or artifact |
|---|---|---|
| … | unit test / integration / manual / diff review | exact command or file |

Prefer automated evidence. If only manual proof is possible, name the steps.

### 3. Validation owner

| Role | Owner |
|---|---|
| Implementation | parent, or `fixer` / `designer` when a writer is dispatched |
| Requirements / diff / evidence | one `verifier` |
| Focused risk review | 1–3 `explorer` / `oracle` reviewers with orthogonal claims |
| Reconciliation | parent, once all reports use the same immutable diff/commit |

Two reviewers total is the default; four is the maximum. Do not clone prompts. Partition ownership, compatibility, runtime behavior, architecture, or security claims. The writer (or parent) runs **Verification** commands; reviewers inspect the resulting evidence independently.

### 4. Acceptance strength

Choose and report the strongest status supported by actual evidence:

- `live-ui-verified` — required UI behavior was exercised in a running interface.
- `unit-test-verified` — relevant automated behavioral tests passed.
- `type-check-only` — static type checking passed, with behavior still unverified.
- `verifier-blocked` — independent verification could not run; state the blocker.
- `verifier-failed` — independent verification found a failing requirement.

A behavioral change cannot be accepted as `type-check-only`; add behavioral evidence or leave it blocked/failed.

### 5. Budget

Set limits to prevent endless loops:

- Max writer repair rounds before escalation: **2**
- Max verifier → repair → re-verify cycles: **1**
- Max acceptance reviewers per wave: **4**
- When budget is exhausted: stop and report status; use `oracle` only when unresolved judgment blocks acceptance

## Handoff

Include the verification plan in the writer task under **Verification**. Before acceptance, freeze the diff/commit and evidence locations, then launch the reviewers in one parallel wave.
