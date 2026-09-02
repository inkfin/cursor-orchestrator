"""Tests for task-contract guard hook and plugin static validation."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = REPO_ROOT / "cursor-orchestrator"
GUARD = PLUGIN_DIR / "hooks" / "task-contract-guard.py"
HOOKS_JSON = PLUGIN_DIR / "hooks" / "hooks.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
VALIDATE = REPO_ROOT / "scripts" / "validate_plugin.py"


def run_guard(payload: dict) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    out = proc.stdout.strip()
    parsed = json.loads(out) if out else {}
    return proc.returncode, parsed


def run_fixture(name: str) -> tuple[int, dict]:
    return run_guard(json.loads((FIXTURES / name).read_text()))


class SubagentStartContractTests(unittest.TestCase):
    def test_valid_single_writer(self) -> None:
        code, out = run_fixture("subagent_valid_single.json")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_valid_parallel_with_branch(self) -> None:
        code, out = run_fixture("subagent_valid_parallel.json")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_missing_owned_paths_denied(self) -> None:
        code, out = run_fixture("subagent_missing_owned_paths.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("Owned paths", out.get("user_message", ""))

    def test_missing_scope_denied(self) -> None:
        code, out = run_fixture("subagent_missing_scope.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("scope", out.get("user_message", "").lower())

    def test_missing_verification_denied(self) -> None:
        code, out = run_fixture("subagent_missing_verification.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("verification", out.get("user_message", "").lower())

    def test_missing_execution_mode_denied(self) -> None:
        code, out = run_fixture("subagent_missing_execution_mode.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("execution mode", out.get("user_message", "").lower())

    def test_parallel_without_branch_denied(self) -> None:
        code, out = run_fixture("subagent_parallel_no_isolation.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("git_branch", out.get("user_message", ""))

    def test_parallel_with_local_worktree_text_only_denied(self) -> None:
        """Task text claiming local worktree isolation is no longer sufficient."""
        code, out = run_fixture("subagent_parallel_text_only_worktree.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("git_branch", out.get("user_message", ""))

    def test_single_mode_flagged_parallel_worker_denied(self) -> None:
        """is_parallel_worker overrides 'Execution mode: single' in the text."""
        code, out = run_fixture("subagent_single_flagged_parallel.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("git_branch", out.get("user_message", ""))

    def test_cloud_execution_mode_denied(self) -> None:
        code, out = run_fixture("subagent_cloud_forbidden.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("Cloud", out.get("user_message", ""))

    def test_cloud_git_branch_denied(self) -> None:
        code, out = run_fixture("subagent_cloud_branch.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("Cloud", out.get("user_message", ""))

    def test_invalid_json_denied(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(GUARD)],
            input="not json",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertEqual(out.get("permission"), "deny")

    def test_non_writer_passes_through(self) -> None:
        code, out = run_guard({"subagent_type": "explorer", "task": "look around"})
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_subagent_deny_omits_agent_message(self) -> None:
        _, out = run_fixture("subagent_missing_owned_paths.json")
        self.assertNotIn("agent_message", out)
        self.assertEqual(set(out), {"permission", "user_message"})


class PreToolUseTaskTests(unittest.TestCase):
    def test_cloud_environment_denied(self) -> None:
        code, out = run_fixture("pretooluse_task_cloud.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("Cloud", out.get("user_message", ""))
        self.assertIn("Cloud", out.get("agent_message", ""))

    def test_cloud_in_prompt_denied(self) -> None:
        code, out = run_fixture("pretooluse_task_cloud_prompt.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")

    def test_local_task_allowed(self) -> None:
        code, out = run_fixture("pretooluse_task_local.json")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_non_task_tool_allowed(self) -> None:
        code, out = run_guard(
            {
                "hook_event_name": "preToolUse",
                "tool_name": "Shell",
                "tool_input": {"command": "gcloud auth login"},
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_pretooluse_does_not_enforce_writer_contract(self) -> None:
        """Contract enforcement belongs to subagentStart, not the tool gate."""
        code, out = run_guard(
            {
                "hook_event_name": "preToolUse",
                "tool_name": "Task",
                "tool_input": {"subagent_type": "fixer", "prompt": "just do it"},
            }
        )
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")


class HooksManifestTests(unittest.TestCase):
    def test_both_events_registered_fail_closed(self) -> None:
        hooks = json.loads(HOOKS_JSON.read_text())["hooks"]
        for event, matcher in (("subagentStart", "fixer|designer"), ("preToolUse", "Task")):
            entries = hooks.get(event) or []
            self.assertTrue(entries, msg=f"{event} hook missing")
            entry = entries[0]
            self.assertEqual(entry.get("matcher"), matcher)
            self.assertTrue(entry.get("failClosed"))
            self.assertIn("task-contract-guard", entry.get("command", ""))


class PluginManifestTests(unittest.TestCase):
    def test_plugin_json_declares_component_paths(self) -> None:
        plugin = json.loads((PLUGIN_DIR / ".cursor-plugin" / "plugin.json").read_text())
        self.assertEqual(plugin.get("agents"), "./agents/")
        self.assertEqual(plugin.get("skills"), "./skills/")
        self.assertEqual(plugin.get("rules"), "./rules/")
        self.assertEqual(plugin.get("hooks"), "./hooks/hooks.json")

    def test_marketplace_source_points_at_plugin_subdirectory(self) -> None:
        marketplace = json.loads((REPO_ROOT / ".cursor-plugin" / "marketplace.json").read_text())
        sources = [p.get("source") for p in marketplace.get("plugins", [])]
        self.assertIn("cursor-orchestrator", sources)
        for source in sources:
            self.assertNotIn(source, ("./", ".", ""))


class ValidatePluginScriptTests(unittest.TestCase):
    def test_validate_plugin_exits_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(VALIDATE)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=proc.stdout + proc.stderr,
        )


if __name__ == "__main__":
    unittest.main()
