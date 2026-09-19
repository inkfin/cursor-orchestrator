---
name: verification-planning
description: >-
  Plan evidence and a bounded acceptance wave before a consequential writer
  package under /orc, or explicit independent 验收. Skip low-risk parent-owned
  bounded work.
---

# Verification planning

Use this skill **before** a dispatched writer on a consequential change, and before an independent 验收 gate.

Apply the always-on risk definitions to the cumulative change from the goal start state. Consequential risk or explicit independent acceptance takes priority over size and implementation owner. Skip this skill for Q&A, bounded research, and low-risk localized edits or reproduced fixes without an independent-review requirement. A behavior change alone does not require subagent acceptance.

Small file count or known paths do not establish low risk.

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
| Requirements / diff / evidence | parent, or one `verifier` for independent acceptance |
| Focused risk review | 1–2 `explorer` / `oracle` reviewers with orthogonal claims when justified |
| Reconciliation | parent, once all reports use the same immutable diff/commit |

One verifier is sufficient for explicit independent acceptance with no separate risk claim. One verifier plus one focused reviewer is the default for a consequential `/orc` acceptance wave; four reviewers is the maximum when four distinct high-risk claims exist. Do not clone prompts. Partition ownership, compatibility, runtime behavior, architecture, or security claims. The writer or parent runs **Verification** commands; reviewers inspect the resulting evidence independently.

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

Include the verification plan in the writer task under **Verification**. Before acceptance, freeze the diff/commit and evidence locations, then launch the reviewer, or one parallel wave when multiple distinct claims justify reviewers.
