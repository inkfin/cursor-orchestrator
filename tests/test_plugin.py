"""Tests for task-contract guard hook and plugin static validation."""

from __future__ import annotations

import json
import os
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
SKILLS_DIR = PLUGIN_DIR / "skills"


def run_guard_raw(payload: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    out = proc.stdout.strip()
    parsed = json.loads(out) if out else {}
    return proc.returncode, parsed


def run_guard(payload: dict) -> tuple[int, dict]:
    return run_guard_raw(json.dumps(payload))


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

    def test_invalid_json_allowed(self) -> None:
        """Unparseable stdin is a guard failure, not a writer policy violation."""
        code, out = run_guard_raw("not json")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

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

    def test_local_writer_with_contract_allowed(self) -> None:
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

    def test_pretooluse_enforces_writer_contract(self) -> None:
        """CLI reliably fires preToolUse; contract must be gated here."""
        code, out = run_fixture("pretooluse_task_writer_missing_contract.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("Owned paths", out.get("user_message", ""))
        self.assertIn("Owned paths", out.get("agent_message", ""))

    def test_pretooluse_non_writer_skips_contract(self) -> None:
        code, out = run_fixture("pretooluse_task_explorer_ok.json")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_pretooluse_parallel_without_branch_denied(self) -> None:
        code, out = run_fixture("pretooluse_task_parallel_no_branch.json")
        self.assertEqual(code, 2)
        self.assertEqual(out.get("permission"), "deny")
        self.assertIn("git_branch", out.get("user_message", ""))


class HooksManifestTests(unittest.TestCase):
    def test_both_events_registered_fail_open(self) -> None:
        """A hook that cannot start must not block dispatch it never inspected."""
        hooks = json.loads(HOOKS_JSON.read_text())["hooks"]
        for event, matcher in (("subagentStart", "fixer|designer"), ("preToolUse", "Task")):
            entries = hooks.get(event) or []
            self.assertTrue(entries, msg=f"{event} hook missing")
            entry = entries[0]
            self.assertEqual(entry.get("matcher"), matcher)
            self.assertFalse(entry.get("failClosed"))
            self.assertIn("task-contract-guard", entry.get("command", ""))

    def test_command_checks_interpreter_and_path_before_running(self) -> None:
        """A broken install must not reach python3, whose exit 2 reads as deny."""
        hooks = json.loads(HOOKS_JSON.read_text())["hooks"]
        for event in ("subagentStart", "preToolUse"):
            command = hooks[event][0]["command"]
            self.assertIn("command -v python3", command)
            self.assertIn('[ -f "${CURSOR_PLUGIN_ROOT:-}/hooks/task-contract-guard.py" ]', command)
            self.assertIn('printf \'{"permission":"allow"}', command)


class BrokenInstallTests(unittest.TestCase):
    """Guard-infrastructure failures must never masquerade as a policy deny.

    Cursor reads exit 2 from a permission hook as an explicit denial, so an
    unresolvable plugin root or unreadable payload would otherwise block every
    Task dispatch rather than only non-conforming writer dispatches.
    """

    WRITER_DENY = {
        "hook_event_name": "preToolUse",
        "tool_name": "Task",
        "tool_input": {"subagent_type": "fixer", "prompt": "no contract fields"},
    }

    def run_hook_command(self, plugin_root: str | None, payload: str) -> tuple[int, str]:
        command = json.loads(HOOKS_JSON.read_text())["hooks"]["preToolUse"][0]["command"]
        env = dict(os.environ)
        if plugin_root is None:
            env.pop("CURSOR_PLUGIN_ROOT", None)
        else:
            env["CURSOR_PLUGIN_ROOT"] = plugin_root
        proc = subprocess.run(
            ["/bin/sh", "-c", command],
            input=payload,
            capture_output=True,
            text=True,
            env=env,
        )
        return proc.returncode, proc.stdout.strip()

    def test_missing_plugin_root_allows(self) -> None:
        code, out = self.run_hook_command(None, json.dumps(self.WRITER_DENY))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out).get("permission"), "allow")

    def test_wrong_plugin_root_allows(self) -> None:
        code, out = self.run_hook_command("/nonexistent-plugin-root", json.dumps(self.WRITER_DENY))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out).get("permission"), "allow")

    def test_resolvable_plugin_root_still_denies(self) -> None:
        code, out = self.run_hook_command(str(PLUGIN_DIR), json.dumps(self.WRITER_DENY))
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(out).get("permission"), "deny")

    def test_malformed_stdin_allows(self) -> None:
        code, out = run_guard_raw("not json at all")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")

    def test_non_object_payload_allows(self) -> None:
        code, out = run_guard_raw("[1, 2, 3]")
        self.assertEqual(code, 0)
        self.assertEqual(out.get("permission"), "allow")


class PluginManifestTests(unittest.TestCase):
    def test_plugin_json_declares_component_paths(self) -> None:
        plugin = json.loads((PLUGIN_DIR / ".cursor-plugin" / "plugin.json").read_text())
        self.assertEqual(plugin.get("version"), "0.4.0")
        self.assertEqual(plugin.get("agents"), "./agents/")
        self.assertEqual(plugin.get("skills"), "./skills/")
        self.assertEqual(plugin.get("rules"), "./rules/")
        self.assertEqual(plugin.get("hooks"), "./hooks/hooks.json")

    def test_marketplace_source_points_at_plugin_subdirectory(self) -> None:
        marketplace = json.loads((REPO_ROOT / ".cursor-plugin" / "marketplace.json").read_text())
        sources = [p.get("source") for p in marketplace.get("plugins", [])]
        self.assertIn("cursor-orchestrator", sources)

    def test_marketplace_conforms_to_closed_schema(self) -> None:
        """One unsupported key indexes the whole marketplace to zero plugins."""
        marketplace = json.loads((REPO_ROOT / ".cursor-plugin" / "marketplace.json").read_text())
        self.assertLessEqual(set(marketplace), {"name", "owner", "metadata", "plugins"})
        self.assertLessEqual(set(marketplace.get("owner", {})), {"name", "email"})
        for entry in marketplace.get("plugins", []):
            self.assertLessEqual(
                set(entry), {"name", "source", "description", "minClientVersions"}
            )

class PstackLiteSkillTests(unittest.TestCase):
    def skill_text(self, name: str) -> str:
        path = SKILLS_DIR / name / "SKILL.md"
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"))
        self.assertIn(f"name: {name}", text)
        self.assertIn("description:", text)
        return text

    def test_new_skills_have_frontmatter(self) -> None:
        for name in ("prototype-lite", "collab-debug", "goal-watch"):
            with self.subTest(skill=name):
                self.skill_text(name)

    def test_prototype_cannot_modify_product_code(self) -> None:
        text = self.skill_text("prototype-lite")
        self.assertIn("product paths remain read-only", text)
        self.assertIn("implement as product code (parent by default, or a writer if `orc` is active)", text)

    def test_collab_debug_forbids_guessing_before_reproduction(self) -> None:
        text = self.skill_text("collab-debug")
        self.assertIn("failure is not reproduced", text)
        self.assertIn("do not ask `fixer` to guess a repair", text)

    def test_goal_watch_safety_invariants(self) -> None:
        text = self.skill_text("goal-watch")
        for phrase in (
            "persistent server-side `cursor-agent` CLI session",
            "does **not** guarantee wakeup",
            "hard stop conditions only",
            "Never run an agent polling loop",
            "never use a Ralph `stop` hook",
            "Idempotent wake",
            "One goal controls exactly one job",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_goal_watch_continue_without_retune(self) -> None:
        text = self.skill_text("goal-watch")
        self.assertIn("A non-terminal wake does **not** retune", text)
        self.assertIn("rebuild the watcher and update next wake only. Do not stop, start, or retune", text)
        self.assertIn("leave the old job running and re-arm only. Do not stop, start, or retune", text)
        self.assertIn("then — and only then — change one allowed knob", text)
        self.assertIn("wake reason, metric freshness, evaluation window, and attempt id", text)
        self.assertIn("continue/re-arm without retune", text)

    def test_parent_works_by_default(self) -> None:
        text = (PLUGIN_DIR / "rules" / "orchestration.mdc").read_text()
        self.assertIn("The parent answers and implements by default", text)
        self.assertIn("Multi-agent plan execution is opt-in", text)
        self.assertIn("## Research", text)
        self.assertIn("## Acceptance", text)
        self.assertIn("parallel acceptance wave", text)
        self.assertIn("2–4 reviewers total", text)
        self.assertIn("## Experiments and runtime", text)
        self.assertIn("Raw logs and large evidence stay in files", text)
        self.assertIn("Do not launch a recon lane and parent Read/Grep", text)
        self.assertIn("operation + resource id + expected prior generation/attempt", text)
        self.assertNotIn("Dispatch by default", text)
        self.assertIn("Do not report lane counts", text)


class OrcSkillTests(unittest.TestCase):
    def skill_text(self) -> str:
        path = SKILLS_DIR / "orc" / "SKILL.md"
        self.assertTrue(path.is_file())
        return path.read_text()

    def test_frontmatter_explicit_only(self) -> None:
        text = self.skill_text()
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: orc", text)
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("主动安排任务", text)
        self.assertNotIn("alwaysApply", text)
        self.assertNotIn("orc-orchestrate", text)

    def test_opt_in_plan_execution(self) -> None:
        text = self.skill_text()
        self.assertIn("multi-agent plan execution", text)
        self.assertIn("specialists execute the plan", text)
        self.assertIn("Dispatch to complete the plan", text)
        self.assertIn("One acceptance wave", text)
        self.assertIn("Artifact-first", text)
        self.assertNotIn("Dispatch by default", text)

    def test_mentions_scout_for_patrol(self) -> None:
        text = self.skill_text()
        self.assertIn("`scout`", text)
        self.assertIn("log harvest", text)
        self.assertIn("Patrol", text)

    def test_does_not_require_project_rule_install(self) -> None:
        text = self.skill_text()
        self.assertNotIn("init-project-rules", text)
        self.assertNotRegex(
            text,
            r"(?i)(copy|install|inject|write (this )?into).{0,80}(AGENTS\.md|\.cursor/rules)",
        )

    def test_no_leftover_old_skill_ids(self) -> None:
        self.assertFalse((SKILLS_DIR / "orc-orchestrate").exists())
        self.assertFalse((SKILLS_DIR / "orchestrate").exists())


class OrcPatrolSkillTests(unittest.TestCase):
    def test_orc_patrol_skill(self) -> None:
        path = SKILLS_DIR / "orc-patrol" / "SKILL.md"
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: orc-patrol", text)
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("scout", text)
        self.assertIn("巡查", text)
        self.assertIn("reuse an existing snapshot", text)
        self.assertIn("do not pad the prompt with the writer four-field contract", text)
        self.assertIn("resume the same scout once", text)


class ScoutAgentTests(unittest.TestCase):
    def test_scout_agent_frontmatter_and_body(self) -> None:
        path = PLUGIN_DIR / "agents" / "scout.md"
        self.assertTrue(path.is_file())
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: scout", text)
        self.assertIn("optimize_for=cost", text)
        self.assertIn("is_background: true", text)
        self.assertNotIn("readonly: true", text)
        self.assertIn(".cursor/scout-logs", text)
        self.assertIn("run an experiment", text)
        self.assertIn("use `operator`", text)
        self.assertIn("all named related", text)
        self.assertIn("Repeat an unchanged snapshot", text)


class ContextBudgetAgentTests(unittest.TestCase):
    def test_operator_batches_transaction_and_stores_receipts(self) -> None:
        text = (PLUGIN_DIR / "agents" / "operator.md").read_text()
        self.assertIn("is_background: false", text)
        self.assertIn("one transaction", text)
        self.assertIn("preflight → dry-run → create → initial inspect", text)
        self.assertIn("idempotency key", text)
        self.assertIn("operation + resource id + expected prior generation/attempt", text)
        self.assertIn("evidence paths", text)
        self.assertIn("Do not paste large command output", text)

    def test_oracle_can_conclude_experiment_from_artifacts(self) -> None:
        text = (PLUGIN_DIR / "agents" / "oracle.md").read_text()
        self.assertIn("Experiment conclusion", text)
        self.assertIn("scout artifact paths", text)
        self.assertIn("Separate platform health from hypothesis evidence", text)


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
        self.assertIn("agents: 9", proc.stdout)
        self.assertIn("skills: 9", proc.stdout)

    def test_readme_counts_nine(self) -> None:
        plugin = (PLUGIN_DIR / "README.md").read_text()
        self.assertIn("Agents (9)", plugin)
        self.assertIn("Skills (9)", plugin)
        root = (REPO_ROOT / "README.md").read_text()
        self.assertIn("9 subagents", root)
        self.assertIn("9 workflow skills", root)


if __name__ == "__main__":
    unittest.main()
