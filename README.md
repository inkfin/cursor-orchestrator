# cursor-orchestrator

Cursor Plugin for specialist-lane orchestration.

It provides:

- seven custom subagents under `agents/`
- one always-on routing rule under `rules/`

Models live in each agent's `model:` frontmatter. Context7 and other MCP
servers are not bundled; install them separately.

Herdr fleet management, peer mailbox files, and session hooks stay outside
this plugin.

## Install

### IDE (user scope)

```bash
mkdir -p ~/.cursor/plugins/local
ln -sfn /data/workspace/toolings/cursor-orchestrator ~/.cursor/plugins/local/cursor-orchestrator
```

Then **Developer: Reload Window**. Confirm `cursor-orchestrator` in Customize.
If a User Rule still contains the old orchestration protocol, delete it so
the plugin rule is the only copy.

On Teams/Enterprise, **Allow Local Plugin Imports** must be on.

### CLI

Point `enabled_plugins` at this directory in `~/.cursor/settings.json`:

```json
{
  "enabled_plugins": [
    "/data/workspace/toolings/cursor-orchestrator"
  ]
}
```

Alternatively pass `--plugin-dir /data/workspace/toolings/cursor-orchestrator`
on a single invocation.

## Layout

```text
cursor-orchestrator/
├── .cursor-plugin/plugin.json
├── agents/
├── rules/orchestration.mdc
└── README.md
```
