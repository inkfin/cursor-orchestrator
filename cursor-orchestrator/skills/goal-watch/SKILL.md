---
name: goal-watch
description: >-
  Watch one long-running server experiment with sparse scheduled or event
  wakeups. Invoke explicitly for overnight runs or metric-gated retuning.
---

# Goal watch

This is for a persistent server-side `cursor-agent` CLI session. The experiment runs independently of chat. The machine and agent session must stay alive: this workflow does **not** guarantee wakeup after either stops.

## Goal file

Create `.cursor/goal-watch/<run>.md`. One goal controls exactly one job and records:

- predicate: metric, one-shot read command/result path, threshold, noise rule, and minimum progress;
- clock: first check/interval (normally hours, never minute-scale idle checks);
- job handle: start, graceful stop, liveness/read commands, and pid/tmux/slurm identity;
- tuning boundary: allowed knobs and paths, forbidden paths/algorithm rewrites, one knob per attempt, rollback on miss, maximum retunes;
- hard stop conditions only: predicate met, wall clock or retunes exhausted, dead job unrecoverable by its declared handle, or a human `stop`;
- declared outcome at hard limits: leave running or stop;
- state: run id, attempt, handle, next wake, last metric, processed event/attempt id, and decision log.

Every start/stop/read command needs a timeout and meaningful exit code. `operator` may execute only those declared commands; it never invents `kill` or decides whether to stop.

## Sparse wakeups

Use `/loop` as a one-shot `sleep` + sentinel, or one event watcher for a result file/log line. A long heartbeat may recover a dead watcher, at roughly the goal's check interval. Never run an agent polling loop such as `while sleep 30; read metric`, and never use a Ralph `stop` hook to feed the same prompt back each turn.

Allow one effective watcher per goal. Cancel the old watcher before re-arming. An unexpected watcher exit is not an experiment failure.

## Idempotent wake

A non-terminal wake does **not** retune. Classify the wake by wake reason, metric freshness, evaluation window, and attempt id before any stop/start/retune. If this wake's `(wake reason, attempt id, evaluation window, metric freshness)` was already processed, do nothing except report current state.

On each wake:

1. Read the goal file and declared job handle; do not rely on chat memory.
2. Ask `operator` for one declared liveness/metric read. Record whether the metric is fresh (new since last processed evaluation of this attempt).
3. Branch:

   - **Watcher or heartbeat recovery, old job healthy:** rebuild the watcher and update next wake only. Do not stop, start, or retune.
   - **Not yet in the evaluation window, or no fresh metric:** leave the old job running and re-arm only. Do not stop, start, or retune.
   - **Fresh metric after minimum progress/noise rule, predicate miss:** then — and only then — change one allowed knob, gracefully stop the old job, start a new attempt, append one decision-log entry, atomically update state, and arm the next wake.
   - **Job died unexpectedly:** follow only the recovery action predeclared in the goal. If that action cannot restore the job, enter hard stop/`blocked`. Do not invent a restart or retune.
   - **Predicate met, or a hard stop (wall clock/retunes exhausted, unrecoverable dead job, human `stop`):** apply the goal's declared action and report.

Never duplicate kill, start, or retune for the same attempt id. Duplicate wakes with a stale metric or the same evaluation window must continue/re-arm without retune.

Write goal state and the decision log atomically after every transition. A failed graceful stop may use only a predeclared escalation action; if none exists, report `blocked` and do not guess `kill -9`. Training-code changes still require the formal `fixer` path.
