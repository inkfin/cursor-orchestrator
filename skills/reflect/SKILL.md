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
2. **Repeated work** — steps that ran twice or overlapped (duplicate recon, writer + parent both editing, verifier findings ignored then re-found).
3. **Root causes** — contract gaps, missing owned paths, wrong lane, skipped verifier, parallel when single-writer was enough.
4. **Recommendations** — specific edits to `rules/orchestration.mdc`, agent contracts, or skills (file + section). Prefer one actionable change per finding.
5. **Non-goals** — do not rewrite working code; this skill improves process, not product.

Keep the report concise. Verdict first: was orchestration adequate yes/no, then findings.
