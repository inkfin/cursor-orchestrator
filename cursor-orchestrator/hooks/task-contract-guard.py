#!/usr/bin/env python3
"""Task-contract guard for writer subagents (fixer, designer).

Reads hook JSON from stdin and serves two events:

preToolUse (matcher: Task) — primary gate (CLI reliably fires this)
  - denies Task dispatches that request cloud execution
  - for fixer/designer, requires Owned paths, Scope, Verification, Execution mode
    in the Task prompt (same contract as subagentStart)
  - parallel/worktree prompts require a non-empty git_branch on the tool input

subagentStart (matcher: fixer|designer) — kept for surfaces that still emit it
  - same writer contract against the `task` field
  - parallel/worktree work requires a non-empty git_branch in the payload
  - cloud execution is forbidden

Exit 0 + {"permission":"allow"} on success.
Exit 2 + {"permission":"deny",...} on contract violation.
Exit 2 is reserved for a policy verdict, because Cursor reads it as an explicit
deny on a permission hook. Anything this guard cannot evaluate — unreadable or
non-JSON stdin, an unexpected payload shape — therefore allows instead, leaving
enforcement to the always-on rule. A broken install must not look like a denial:
`python3` also exits 2 when it cannot open this file, so hooks.json checks that
the interpreter and this path resolve before handing over control.

hooks.json runs this fail-open (`failClosed: false`) for the same reason. A hook
that cannot start enforces nothing either way, and the `Task` matcher covers
every lane, so failing closed would block read-only dispatch too. Denials and
malformed responses still block while the guard runs.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

# Case-insensitive labels; allow optional markdown bold around keys.
REQUIRED_FIELDS = (
    ("owned paths", re.compile(r"\bowned\s+paths\b", re.IGNORECASE)),
    ("scope", re.compile(r"\bscope\b", re.IGNORECASE)),
    ("verification", re.compile(r"\bverification\b", re.IGNORECASE)),
    ("execution mode", re.compile(r"execution\s+mode\b", re.IGNORECASE)),
)

PARALLEL_MODE = re.compile(
    r"execution\s+mode\s*[:\-]?\s*[^\n]*\b(parallel|worktree)\b"
    r"|\bparallel/worktree\b"
    r"|\bexecution\s+mode\s*[:\-]?\s*parallel\b",
    re.IGNORECASE,
)

# Deliberately narrow: only explicit cloud-execution requests, so ordinary
# tasks that merely mention cloud infrastructure are not blocked.
CLOUD_EXECUTION = re.compile(
    r"environment\s*[:=]\s*[\"']?cloud\b"
    r"|\bcloud\s+(?:subagent|worktree)s?\b"
    r"|\bexecution\s+mode\s*[:\-]?[^\n]*\bcloud\b",
    re.IGNORECASE,
)

CLOUD_BRANCH = re.compile(r"cloud", re.IGNORECASE)

WRITER_AGENTS = ("fixer", "designer")

CLOUD_DENIAL = (
    "Cloud execution is forbidden. Use a single local writer or local "
    "worktree isolation with a real git_branch."
)

CONTRACT_HINT = (
    "Include Owned paths, Scope, Verification, and Execution mode in the "
    "Task prompt, then re-dispatch."
)


def _emit(payload: dict[str, Any], code: int) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.exit(code)


def _deny(message: str, agent_message: str | None = None) -> None:
    payload: dict[str, Any] = {"permission": "deny", "user_message": message}
    if agent_message:
        payload["agent_message"] = agent_message
    _emit(payload, 2)


def _allow() -> None:
    _emit({"permission": "allow"}, 0)


def detect_event(data: dict[str, Any]) -> str:
    """Return 'preToolUse' or 'subagentStart' for the incoming payload."""
    name = str(data.get("hook_event_name") or data.get("hookEventName") or "")
    normalized = name.replace("_", "").replace("-", "").strip().lower()
    if normalized == "pretooluse":
        return "preToolUse"
    if normalized == "subagentstart":
        return "subagentStart"
    # Fall back on payload shape when the event name is absent.
    if "tool_name" in data or "tool_input" in data:
        return "preToolUse"
    return "subagentStart"


def _branch_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def validate_writer_contract(
    *,
    subagent_type: str,
    task: str,
    git_branch: Any = None,
    is_parallel_worker: Any = False,
) -> str | None:
    """Return error message if a writer dispatch violates the task contract."""
    if subagent_type not in WRITER_AGENTS:
        return None

    if not isinstance(task, str) or not task.strip():
        return (
            "Writer task is empty. Include Owned paths, Scope, Verification, "
            "and Execution mode."
        )

    for label, pattern in REQUIRED_FIELDS:
        if not pattern.search(task):
            return (
                f"Writer task missing required field: {label}. "
                "Include Owned paths, Scope, Verification, and Execution mode."
            )

    if CLOUD_EXECUTION.search(task):
        return CLOUD_DENIAL

    branch = _branch_text(git_branch)
    if branch and CLOUD_BRANCH.search(branch):
        return f"Cloud worktrees are forbidden (git_branch={branch!r})."

    is_parallel = bool(is_parallel_worker) or bool(PARALLEL_MODE.search(task))
    if is_parallel and not branch:
        return (
            "Parallel/worktree execution requires a non-empty git_branch in the "
            "dispatch payload. Task text describing a local worktree is not enough."
        )

    return None


def validate_tool_call(data: dict[str, Any]) -> str | None:
    """Validate a Task preToolUse payload (cloud + writer contract)."""
    tool_name = str(data.get("tool_name") or "").strip().lower()
    if tool_name and tool_name != "task":
        return None

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return None

    environment = tool_input.get("environment")
    if isinstance(environment, str) and environment.strip().lower() == "cloud":
        return CLOUD_DENIAL

    for key in ("prompt", "description"):
        value = tool_input.get(key)
        if isinstance(value, str) and CLOUD_EXECUTION.search(value):
            return CLOUD_DENIAL

    subagent_type = str(tool_input.get("subagent_type") or "").strip().lower()
    prompt = tool_input.get("prompt")
    task = prompt if isinstance(prompt, str) else ""
    return validate_writer_contract(
        subagent_type=subagent_type,
        task=task,
        git_branch=tool_input.get("git_branch"),
        is_parallel_worker=tool_input.get("is_parallel_worker"),
    )


def validate_payload(data: dict[str, Any]) -> str | None:
    """Validate a subagentStart payload for writer contract fields."""
    subagent_type = str(data.get("subagent_type", "")).lower()
    task = data.get("task") or ""
    if not isinstance(task, str):
        task = ""
    return validate_writer_contract(
        subagent_type=subagent_type,
        task=task,
        git_branch=data.get("git_branch"),
        is_parallel_worker=data.get("is_parallel_worker"),
    )


def _agent_message_for(error: str) -> str:
    if error == CLOUD_DENIAL or error.startswith("Cloud worktrees"):
        return (
            f"{error} Re-dispatch this Task with environment omitted or "
            "set to local, and use a non-cloud git_branch if isolating."
        )
    return f"{error} {CONTRACT_HINT}"


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        _allow()

    if not isinstance(data, dict):
        _allow()

    if detect_event(data) == "preToolUse":
        error = validate_tool_call(data)
        if error:
            _deny(error, agent_message=_agent_message_for(error))
        _allow()

    error = validate_payload(data)
    if error:
        _deny(error)
    _allow()


if __name__ == "__main__":
    main()
