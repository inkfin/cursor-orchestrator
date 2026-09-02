# cursor-orchestrator (marketplace repo)

A Cursor plugin marketplace containing one plugin.

| Plugin | Path | What it does |
|---|---|---|
| `cursor-orchestrator` | [`cursor-orchestrator/`](./cursor-orchestrator) | Specialist-lane orchestration policy: 8 subagents, 7 workflow skills, four task routes, and a writer task-contract hook |

Full documentation lives in the [plugin README](./cursor-orchestrator/README.md).

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

Observed on `agent` CLI 2026.08.11-e8db854:

- `agent plugin marketplace add` pins the marketplace to the **commit** that
  was current when it ran, recorded as `gitRef`. Later pushes are not picked up.
- `agent plugin marketplace update <name>` prints `✓ Updated ... 0 plugins
  indexed` but does **not** re-index: `lastIndexedAt` stays unchanged. Do not
  trust its output.
- `agent plugin marketplace remove <url>` matches by URL and removes **every**
  marketplace sharing that URL, not just the named one.

So a push only reaches installs after re-adding:

```bash
agent plugin marketplace remove <marketplace-name>
agent plugin marketplace add https://github.com/inkfin/cursor-orchestrator
agent plugin marketplace list --format json   # confirm gitRef and lastIndexedAt moved
```

The marketplace name registered by `add` comes from `marketplace.json`'s `name`
field, not from the repo or owner.

## Development

`scripts/` and `tests/` are repo tooling and are not shipped as plugin
components. Run both from the repository root:

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -v
```
