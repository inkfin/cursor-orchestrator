# cursor-orchestrator (marketplace repo)

A Cursor plugin marketplace containing one plugin.

| Plugin | Path | What it does |
|---|---|---|
| `cursor-orchestrator` | [`cursor-orchestrator/`](./cursor-orchestrator) | Specialist-lane orchestration policy (v0.4.0): parent-owned bounded work, 9 subagents, 9 workflow skills, goal-scoped opt-in `/orc`, dispatch thresholds, and writer task-contract hooks |

Install and lane lookup: [plugin README](./cursor-orchestrator/README.md). Routing: `cursor-orchestrator/rules/orchestration.mdc`.

## Layout

The repository root is the **marketplace**; each plugin is a subdirectory.

```text
<repo root>/
├── .cursor-plugin/marketplace.json   # catalog: one entry per plugin
├── cursor-orchestrator/              # the plugin
├── scripts/validate_plugin.py        # repo tooling
└── tests/
```

`marketplace.json` is validated against Cursor's
[`marketplace.schema.json`](https://github.com/cursor/plugins/blob/main/schemas/marketplace.schema.json),
which sets `additionalProperties: false` at every level. A single unsupported
key (for example `owner.url`) fails the whole manifest and the marketplace
indexes to **zero plugins** with no error message. Allowed keys:

| Object | Keys |
|---|---|
| root | `name`, `owner`, `metadata`, `plugins` |
| `owner` | `name`, `email` |
| plugin entry | `name`, `source`, `description`, `minClientVersions` |

`scripts/validate_plugin.py` checks this, since the indexer reports the failure
only as a zero count.

## Install

Import this repository through your team's Cursor marketplace, or symlink the
plugin subdirectory for local development:

```bash
mkdir -p ~/.cursor/plugins/local
ln -sfn "$PWD/cursor-orchestrator" ~/.cursor/plugins/local/cursor-orchestrator
```

Then run **Developer: Reload Window**.

## Publishing an update

Observed on `agent` CLI 2026.10.01-e373342. After a push, refresh the existing marketplace:

```bash
agent plugin marketplace update cursor-orchestrator
agent plugin marketplace list --format json
```

`update` re-indexes through the server. A successful run reports the indexed plugin count, and `lastIndexedAt` moves. `gitRef` stays when the remote default branch has not moved; it advances when that branch has new commits. Do not `remove` and `add` just to pick up a push.

`add` still records the commit that was current when it ran. Use it for a first install, not for a routine update. There is no `plugin install` subcommand; after adding a marketplace, enable the plugin from `/plugins` in interactive mode.

`remove` deletes one user-scoped marketplace. If the name or URL matches more than one marketplace, the command stops instead of deleting every match.

The marketplace name registered by `add` comes from `marketplace.json`'s `name` field, not from the repo or owner.

## Development

`scripts/` and `tests/` are repo tooling and are not shipped as plugin
components. Run both from the repository root:

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```
