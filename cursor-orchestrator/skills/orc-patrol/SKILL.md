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

Do not do the patrol yourself if `scout` can run. Dispatch one `scout` for all related named resources. This is not a writer task; do not pad the prompt with the writer four-field contract. Supply:

- one log directory (`.cursor/scout-logs/` or the caller path);
- named resources and stable identifiers;
- acceptance criteria;
- allowed read-only platform commands and known CLI pitfalls.

Pass through: acceptance criteria, named resources (run id, pod, URL), and log destination.

If the user gave no criteria, default: job/pipeline succeeded; no errors; no obvious crash/OOM/timeout.

Before dispatch, reuse an existing snapshot when resource state/version and criteria are unchanged. If a snapshot is unverifiable only because a selector or command was wrong, resume the same scout once with the correction; do not create another scout task. While scout runs, the parent does not issue overlapping inspect/log commands. After scout returns: show the compact verdict and log paths. Do not re-analyze or paste the logs. Escalate to `oracle` only if the user asks why or asks for an experiment conclusion.

Scout is not a writer. It never starts, stops, retries, or creates experiments. Those are one complete named `operator` transaction.
