#!/usr/bin/env python3
"""Static validation for cursor-orchestrator plugin layout (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN_SOURCE = "cursor-orchestrator"
PLUGIN_DIR = REPO / PLUGIN_SOURCE
MARKETPLACE_JSON = REPO / ".cursor-plugin" / "marketplace.json"
PLUGIN_JSON = PLUGIN_DIR / ".cursor-plugin" / "plugin.json"
HOOKS_JSON = PLUGIN_DIR / "hooks" / "hooks.json"
AGENTS_DIR = PLUGIN_DIR / "agents"
SKILLS_DIR = PLUGIN_DIR / "skills"
RULES_DIR = PLUGIN_DIR / "rules"
GUARD = PLUGIN_DIR / "hooks" / "task-contract-guard.py"

EXPECTED_AGENTS = {
    "designer",
    "explorer",
    "fixer",
    "librarian",
    "operator",
    "oracle",
    "oracle-sol",
    "scout",
    "verifier",
}

# Mirrors cursor/plugins schemas/marketplace.schema.json (additionalProperties: false).
MARKETPLACE_KEYS = {"name", "owner", "metadata", "plugins"}
OWNER_KEYS = {"name", "email"}
PLUGIN_ENTRY_KEYS = {"name", "source", "description", "minClientVersions"}

EXPECTED_SKILLS = {
    "collab-debug",
    "deepwork",
    "goal-watch",
    "orc",
    "orc-patrol",
    "prototype-lite",
    "reflect",
    "verification-planning",
    "visual-analysis",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    if "name" not in fields:
        raise ValueError(f"{path}: frontmatter missing name")
    return fields


def check_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    errors: list[str] = []

    # Manifests
    for path in (PLUGIN_JSON, MARKETPLACE_JSON, HOOKS_JSON):
        if not path.is_file():
            errors.append(f"Missing {path.relative_to(REPO)}")
            continue
        try:
            check_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON {path}: {exc}")

    plugin = check_json(PLUGIN_JSON)
    if plugin.get("version") != "0.4.0":
        errors.append(f"plugin.json version expected 0.4.0, got {plugin.get('version')}")
    if not plugin.get("hooks"):
        errors.append("plugin.json missing hooks path")
    if not plugin.get("skills"):
        errors.append("plugin.json missing skills path")
    if not plugin.get("rules"):
        errors.append("plugin.json missing rules path")
    if not plugin.get("agents"):
        errors.append("plugin.json missing agents path")

    # marketplace.schema.json sets additionalProperties: false at every level,
    # so one stray key silently indexes the whole marketplace to zero plugins.
    marketplace = check_json(MARKETPLACE_JSON)
    extra_top = set(marketplace) - MARKETPLACE_KEYS
    if extra_top:
        errors.append(f"marketplace.json has unsupported top-level keys: {sorted(extra_top)}")
    for required in ("name", "plugins"):
        if required not in marketplace:
            errors.append(f"marketplace.json missing required key {required!r}")

    owner = marketplace.get("owner", {})
    extra_owner = set(owner) - OWNER_KEYS
    if extra_owner:
        errors.append(f"marketplace.json owner has unsupported keys: {sorted(extra_owner)} (only name, email)")

    plugins = marketplace.get("plugins") or []
    for entry in plugins:
        extra_entry = set(entry) - PLUGIN_ENTRY_KEYS
        if extra_entry:
            errors.append(f"marketplace.json plugin entry has unsupported keys: {sorted(extra_entry)}")
    sources = [p.get("source") for p in plugins]
    if PLUGIN_SOURCE not in sources:
        errors.append(f"marketplace.json needs a plugin entry with source {PLUGIN_SOURCE!r}, got {sources}")

    # The marketplace manifest belongs to the repo, not the plugin.
    if (PLUGIN_DIR / ".cursor-plugin" / "marketplace.json").exists():
        errors.append("marketplace.json must not live inside the plugin directory")
    if not RULES_DIR.is_dir():
        errors.append(f"Missing {PLUGIN_SOURCE}/rules/")

    # Agents
    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    found_agents = set()
    for path in agent_files:
        try:
            meta = parse_frontmatter(path)
            found_agents.add(meta["name"])
        except ValueError as exc:
            errors.append(str(exc))

    missing_agents = EXPECTED_AGENTS - found_agents
    extra_agents = found_agents - EXPECTED_AGENTS
    if missing_agents:
        errors.append(f"Missing agents: {sorted(missing_agents)}")
    if extra_agents:
        errors.append(f"Unexpected agents: {sorted(extra_agents)}")

    # Writers, mutating control, and default-sync read-only lanes stay foreground
    for name in ("fixer", "designer", "operator", "explorer", "librarian", "oracle", "oracle-sol"):
        meta = parse_frontmatter(AGENTS_DIR / f"{name}.md")
        if meta.get("is_background") != "false":
            errors.append(f"{name}: is_background must be false")

    # Verifier
    verifier_meta = parse_frontmatter(AGENTS_DIR / "verifier.md")
    if verifier_meta.get("readonly") != "true":
        errors.append("verifier: readonly must be true")
    if verifier_meta.get("is_background") != "false":
        errors.append("verifier: is_background must be false")

    # oracle-sol model syntax
    sol_meta = parse_frontmatter(AGENTS_DIR / "oracle-sol.md")
    model = sol_meta.get("model", "")
    if "effort=high" not in model or "context=" in model or "reasoning=" in model:
        errors.append(f"oracle-sol model must use effort=high syntax, got {model!r}")

    # scout: background, cheap; must write log files so not readonly
    scout_meta = parse_frontmatter(AGENTS_DIR / "scout.md")
    if scout_meta.get("is_background") != "true":
        errors.append("scout: is_background must be true")
    if scout_meta.get("readonly") == "true":
        errors.append("scout: must not set readonly: true")
    scout_model = scout_meta.get("model", "")
    if "optimize_for=cost" not in scout_model:
        errors.append(f"scout model must use optimize_for=cost, got {scout_model!r}")

    # Skills
    if not SKILLS_DIR.is_dir():
        errors.append("skills/ directory missing")
    else:
        found_skills = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
        missing_skills = EXPECTED_SKILLS - found_skills
        if missing_skills:
            errors.append(f"Missing skills: {sorted(missing_skills)}")
        for skill in EXPECTED_SKILLS:
            skill_md = SKILLS_DIR / skill / "SKILL.md"
            if not skill_md.is_file():
                errors.append(f"Missing {skill_md.relative_to(REPO)}")
                continue
            try:
                parse_frontmatter(skill_md)
            except ValueError as exc:
                errors.append(str(exc))
            line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
            if line_count >= 500:
                errors.append(f"{skill_md}: exceeds 500 lines ({line_count})")

        reflect_meta = parse_frontmatter(SKILLS_DIR / "reflect" / "SKILL.md")
        if reflect_meta.get("disable-model-invocation") != "true":
            errors.append("reflect skill must set disable-model-invocation: true")

        orc_meta = parse_frontmatter(SKILLS_DIR / "orc" / "SKILL.md")
        if orc_meta.get("disable-model-invocation") != "true":
            errors.append("orc skill must set disable-model-invocation: true")

        patrol_meta = parse_frontmatter(SKILLS_DIR / "orc-patrol" / "SKILL.md")
        if patrol_meta.get("disable-model-invocation") != "true":
            errors.append("orc-patrol skill must set disable-model-invocation: true")

    # Hook script executable
    if not GUARD.is_file():
        errors.append("hooks/task-contract-guard.py missing")
    elif not (GUARD.stat().st_mode & 0o111):
        errors.append("hooks/task-contract-guard.py must be executable")

    hooks = check_json(HOOKS_JSON).get("hooks", {})
    for event in ("subagentStart", "preToolUse"):
        entries = hooks.get(event, [])
        if not entries:
            errors.append(f"hooks.json missing {event} hook")
            continue
        entry = entries[0]
        if not entry.get("failClosed"):
            errors.append(f"{event} hook should set failClosed: true")
        cmd = entry.get("command", "")
        if "task-contract-guard" not in cmd:
            errors.append(f"{event} command must invoke task-contract-guard")

    pre_tool_entries = hooks.get("preToolUse", [])
    if pre_tool_entries and pre_tool_entries[0].get("matcher") != "Task":
        errors.append("preToolUse hook must match the Task tool")

    if errors:
        print("validate_plugin: FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("validate_plugin: OK")
    print(f"  agents: {len(EXPECTED_AGENTS)}")
    print(f"  skills: {len(EXPECTED_SKILLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
