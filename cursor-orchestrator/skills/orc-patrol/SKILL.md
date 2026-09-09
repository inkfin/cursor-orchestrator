---
name: orc-patrol
description: >-
  One-shot runtime patrol. Invoke when the user asks for 巡查, orc-patrol, or
  to check CI/jobs against acceptance criteria. Dispatch scout to harvest logs
  locally and report errors or obvious execution anomalies only.
disable-model-invocation: true
---

# Orc-patrol

**Explicit invocation only.** Apply this skill only when the user names `orc-patrol` or 巡查.

Future workflow commands may use the `orc-` prefix. This skill is just `orc-patrol`.

Do not do the patrol yourself if `scout` can run. Dispatch `scout` via `Task` with all four contract fields:

- **Owned paths:** only the log directory (`.cursor/scout-logs/` or the caller path)
- **Scope:** patrol + log harvest; no product edits; no experiment start/stop
- **Verification:** local log files exist; verdict vs criteria
- **Execution mode:** `single`

Pass through: acceptance criteria, named resources (run id, pod, URL), and log destination.

If the user gave no criteria, default: job/pipeline succeeded; no errors; no obvious crash/OOM/timeout.

After scout returns: show the verdict and log paths. Do not re-analyze the logs. Escalate to `oracle` only if the user asks why.

Scout is not a writer. Writers are `fixer` and `designer`. Include the four contract fields so dispatch stays bounded. Scout may run in background; the parent still uses `Task`.
