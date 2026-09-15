---
name: reflect
description: >-
  Retrospective on repeated work — identify patterns, wasted effort, and
  concrete improvements to rules or skills. Invoke only when the user explicitly
  asks for reflection or a post-mortem on orchestration quality.
disable-model-invocation: true
---

# Reflect

**Explicit invocation only.** Do not apply during normal implementation or verification.

Use when the user asks for a retrospective, post-mortem, or "why did we repeat this work?"

## Steps

1. **Timeline** — what was attempted, in order (recon → plan → dispatch → verify).
2. **Repeated work** — steps that ran twice or overlapped (background recon plus parent reading the same files, unchanged patrols, one operator task per CLI command, writer + parent both editing, verifier findings ignored then re-found).
3. **Useful fan-out** — distinguish duplicate tasks from orthogonal parallel research or acceptance reviewers that found different risks.
4. **Context load** — identify raw logs/JSON pasted into the parent, reports that should have been artifact paths, and ledger rereads that merely restated a specialist result.
5. **Root causes** — contract gaps, missing owned paths, wrong lane, unstable patrol criteria, skipped verifier, parallel when single-writer was enough.
6. **Recommendations** — specific edits to `rules/orchestration.mdc`, agent contracts, or skills (file + section). Prefer one actionable change per finding.
7. **Non-goals** — do not rewrite working code; this skill improves process, not product.

Keep the report concise. Verdict first: was orchestration adequate yes/no, then findings.
