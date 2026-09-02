# cursor-orchestrator

Cursor Plugin for specialist-lane orchestration.

It provides:

- seven custom subagents under `agents/`
- one always-on routing rule under `rules/`

Models live in each agent's `model:` frontmatter. Context7 and other MCP
servers are not bundled; install them separately.

Herdr fleet management, peer mailbox files, and session hooks stay outside
this plugin.

## This is a single Cursor Plugin

The repo root **is** the plugin. Layout matches the Cursor Plugin format
(`.cursor-plugin/plugin.json` plus default `agents/` and `rules/` folders).

It is **not** a multi-plugin marketplace catalog. That would need
`.cursor-plugin/marketplace.json` listing several plugins in one git repo.

## How to install

Do **not** use Customize → Install from GitHub against this woa remote.
That UI clones **github.com** marketplace sources. `git.woa.com` is not
GitHub.

### IDE (local user plugin)

```bash
mkdir -p ~/.cursor/plugins/local
ln -sfn /path/to/cursor-orchestrator ~/.cursor/plugins/local/cursor-orchestrator
```

Then **Developer: Reload Window**. Confirm `cursor-orchestrator` in Customize.
Delete any leftover User Rule that still contains the old orchestration
protocol so the plugin rule is the only copy.

On Teams/Enterprise, **Allow Local Plugin Imports** must be on. A marketplace
plugin with the same `name` shadows this local copy.

### CLI

Pass the plugin directory on the invocation (verified):

```bash
cursor-agent --plugin-dir /path/to/cursor-orchestrator ...
```

Cursor documents `enabled_plugins` in `~/.cursor/settings.json` as a
persistent local-plugin list. Treat that as optional; this CLI build still
needs `--plugin-dir`.

## Publishing later

| Channel | What it needs |
|---|---|
| Local symlink | Current setup |
| Team Marketplace | Admin Import from Repo; docs assume GitHub |
| Public Marketplace | Public git repo + [submit](https://cursor.com/marketplace/publish) + review on every update |

Public listing also wants this repo public, a clear README, and preferably a
logo referenced from `plugin.json`. Keep `name` kebab-case and unique.

## Layout

```text
cursor-orchestrator/
├── .cursor-plugin/plugin.json
├── agents/
├── rules/orchestration.mdc
├── LICENSE
└── README.md
```
