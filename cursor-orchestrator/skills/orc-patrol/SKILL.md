---
name: orc-patrol
description: >-
  Explicit delegated runtime patrol. Invoke when the user names orc-patrol or
  explicitly asks a scout to check multiple CI/jobs or harvest logs. Dispatch
  scout to save artifacts and report errors or obvious anomalies only.
disable-model-invocation: true
---

# Orc-patrol

**Explicit invocation only.** Apply this skill only when the user names `orc-patrol` or explicitly asks to delegate a multi-resource patrol or log harvest. A simple "巡查一下" or progress check may be completed directly by the parent.

Future workflow commands may use the `orc-` prefix. This skill is just `orc-patrol`.

Do not do the patrol yourself if `scout` can run. Dispatch one `scout` for all related named resources. This is not a writer task; do not pad the prompt with the writer four-field contract. Supply:

- one log directory (`.cursor/scout-logs/` or the caller path);
- named resources and stable identifiers;
- acceptance criteria;
- allowed read-only platform commands and known CLI pitfalls.

Pass through: acceptance criteria, named resources (run id, pod, URL), and log destination.

If the user gave no criteria, default: job/pipeline succeeded; no errors; no obvious crash/OOM/timeout.

Before dispatch, reuse an existing snapshot when resource state/version and criteria are unchanged. If a snapshot is unverifiable only because a selector or command was wrong, resume the same scout once with the correction; do not create another scout task. While scout runs, the parent does not issue overlapping inspect/log commands. After scout returns: show the compact verdict and log paths. Do not re-analyze or paste the logs. If the user asks why or for an experiment conclusion, apply the always-on judgment threshold: the parent answers from bounded evidence; use `oracle` for consequential or ambiguous judgment.

Scout is not a writer. It never starts, stops, retries, or creates experiments. Those follow the shared mutation safeguards and dispatch thresholds; when delegated, batch them into one complete named `operator` transaction.
