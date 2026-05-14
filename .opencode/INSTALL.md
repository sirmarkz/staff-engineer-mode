# Installing Staff Engineer Mode For OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed

## Installation

Add Staff Engineer Mode to the `plugin` array in `opencode.json`:

```json
{
  "plugin": ["staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git"]
}
```

Restart OpenCode. The plugin auto-installs, registers the router skill, and
injects the router bootstrap into the first user message of each session.

## Verify

Ask OpenCode:

```text
Review this service for production readiness.
```

The router should choose one primary specialist and at most one secondary.

## Usage

Use OpenCode's native `skill` tool:

```text
use skill tool to list skills
use skill tool to load staff-engineer-mode
```

Normal use should not require the user to name a specialist; the router
bootstrap is loaded automatically and reads routed specialist files from
`specialists/`.

## Updating

OpenCode updates Git plugins when it restarts.

To pin a specific version:

```json
{
  "plugin": ["staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git#vX.Y.Z"]
}
```

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i staff-engineer-mode`
2. Verify the plugin line in `opencode.json`
3. Make sure you are running a recent OpenCode version

### Skills not found

1. Use OpenCode's `skill` tool to list available skills
2. Check that the plugin is loading

### Router not activating

1. Confirm the plugin loaded without errors
2. Check that `.opencode/plugins/staff-engineer-mode.js` contains the chat message
   transform hook
3. Restart OpenCode after config changes
