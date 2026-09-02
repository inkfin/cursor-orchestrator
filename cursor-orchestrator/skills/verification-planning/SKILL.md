---
name: verification-planning
description: >-
  Plan verification before non-trivial implementation — claims, evidence paths,
  validation owner, and budget. Apply automatically before scoped changes that
  touch behavior, APIs, data models, or multi-file refactors.
---

# Verification planning

Use this skill **before** dispatching a writer on any non-trivial change.

Trivial = single-file typo, comment-only edit, or rename with no behavior change.

## Exemptions

Throwaway prototypes, read-only investigations, and pure environment diagnosis may skip the full plan and independent verifier. Record one sentence explaining which exemption applies. Promotion to product code ends the exemption.

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
| Implementation | `fixer` or `designer` (runs verification during work) |
| Independent acceptance | `verifier` (after parent reconciliation) |

The writer runs **Verification** commands from the task contract. `verifier` re-checks requirements, diff, and evidence independently.

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
- When budget is exhausted: stop, report status, escalate to `oracle` if judgment is needed

## Handoff

Include the verification plan in the writer task under **Verification**. Do not start implementation until claims and evidence paths are explicit.
