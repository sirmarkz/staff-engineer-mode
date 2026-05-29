# Installing Staff Engineer Mode For OpenCode

## Prerequisites

- OpenCode 1.14.50 or newer
- Git

## Install From A Terminal

Run this command in your shell from the project that should use the plugin:

```bash
opencode plugin 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git'
```

OpenCode installs the Git package and updates the local project config under
`.opencode/opencode.json`. Restart OpenCode after installation. The plugin
registers the router skill and injects the router bootstrap into the first user
message of each session.

To install globally, add `--global`:

```bash
opencode plugin --global 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git'
```

## Manual Config Alternative

If you prefer editing config directly, add the plugin package to
`.opencode/opencode.json`:

```json
{
  "plugin": ["staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git"]
}
```

Restart OpenCode after editing config.

## Verify

Ask OpenCode:

```text
Review this service for production readiness.
```

The router should choose one primary specialist and at most one secondary.

## Usage

Normal use should not require the user to name a specialist; the router
bootstrap is loaded automatically and reads routed specialist files from
`specialists/`.

If you need to inspect skills manually, use OpenCode's native `skill` tool:

```text
use skill tool to list skills
use skill tool to load staff-engineer-mode
```

The bootstrap also carries the commit and release policy. Before creating or
amending commits, route to `agent-pr-review` for the exact staged diff. Before
tags, version bumps, hosted release records, packages, artifact publication, or
promotion, route to both `release-build-reproducibility` and
`production-readiness-review`.
If the user explicitly accepts unresolved review gaps, state the residual risk
and proceed.

## Updating

To refresh the Git plugin, run the install command with `--force`:

```bash
opencode plugin --force 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git'
```

Restart OpenCode after updating.

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i staff-engineer-mode`
2. Verify the plugin entry in `.opencode/opencode.json`
3. Make sure you are running a recent OpenCode version

### Skills not found

1. Use OpenCode's `skill` tool to list available skills
2. Check that the plugin is loading

### Router not activating

1. Confirm the plugin loaded without errors
2. Check that `.opencode/plugins/staff-engineer-mode.js` contains the chat message
   transform hook
3. Restart OpenCode after config changes
