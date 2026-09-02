---
name: collab-debug
description: >-
  Diagnose integration failures using local reproduction, collaborator reports,
  and environment differences. Use for cross-machine or cross-team debugging.
---

# Collaborative debugging

Keep three evidence buckets:

- **Local reproduction** — exact command, inputs, output, and whether the failure reproduces.
- **Collaborator report** — observed symptoms and supplied logs; label unverified claims.
- **Environment differences** — versions, configuration, data, permissions, services, and timing.

Start with the smallest safe reproduction and compare the buckets. If the failure is not reproduced, remain in diagnosis: request or collect discriminating evidence and do not ask `fixer` to guess a repair. When evidence identifies a code root cause, promote it to formal implementation with fresh **Scope**, **Owned paths**, and **Verification**. Pure environment remediation may stay operational.

Keep work local-only. Leaf agents do not delegate.
