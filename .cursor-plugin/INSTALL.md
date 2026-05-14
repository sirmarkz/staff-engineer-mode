# Installing staff-engineer-mode for Cursor

Cursor's `/add-plugin` requires a published marketplace. For local installs,
symlink the cloned repository into Cursor's per-user plugins directory.

## Prerequisites

- Cursor IDE
- Git

## Installation (Linux / macOS)

```bash
git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.cursor/staff-engineer-mode-src
mkdir -p ~/.cursor/plugins
ln -s ~/.cursor/staff-engineer-mode-src ~/.cursor/plugins/staff-engineer-mode
```

Reload Cursor with `Developer: Reload Window` or restart the IDE. Cursor reads
the plugin manifest from
`~/.cursor/plugins/staff-engineer-mode/.cursor-plugin/plugin.json`, the router in
`skills/`, and routed specialist files in `specialists/`.

## Installation (Windows PowerShell)

```powershell
git clone https://github.com/sirmarkz/staff-engineer-mode.git "$env:USERPROFILE\.cursor\staff-engineer-mode-src"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\plugins"
cmd /c mklink /J "$env:USERPROFILE\.cursor\plugins\staff-engineer-mode" "$env:USERPROFILE\.cursor\staff-engineer-mode-src"
```

Reload Cursor.

## Per-Project Alternative

If the pack should be available only in one Cursor workspace, symlink the whole
repository into a workspace plugin path. A skills-only symlink will expose the
router but not the routed specialist files.

```bash
mkdir -p .cursor/plugins
ln -s /path/to/staff-engineer-mode .cursor/plugins/staff-engineer-mode
```

Reload the workspace.

## Verify

In Cursor Agent chat:

```text
Design the production readiness checks for this service.
```

The router should select the smallest useful specialist set instead of
requiring a named skill invocation.

## Updating

```bash
cd ~/.cursor/staff-engineer-mode-src && git pull
```

Reload Cursor.

## Uninstalling

```bash
rm ~/.cursor/plugins/staff-engineer-mode
```

Optionally delete the source clone: `rm -rf ~/.cursor/staff-engineer-mode-src`.
