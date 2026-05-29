# Installing Staff Engineer Mode For Cursor

Cursor installs marketplace plugins from inside Cursor, not from a separate
terminal plugin installer for this pack.

## Prerequisites

- Cursor IDE or Cursor Agent

## Install From Cursor Agent Chat

Type this inside Cursor Agent chat:

```text
/add-plugin staff-engineer-mode
```

You can also open the Cursor Plugin Marketplace in the IDE, search for
`Staff Engineer Mode`, and install it when published.

## Local Development Fallback

Use this only for local plugin development or before marketplace publication.
It symlinks the full repository so Cursor can read the plugin manifest, router
skill, hooks, and routed specialist files.
Do not skip the detached checkout step. Without it, the fallback install uses
the repository's default branch.

### Linux / macOS

```bash
mkdir -p ~/.cursor
git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.cursor/staff-engineer-mode-src
git -C ~/.cursor/staff-engineer-mode-src checkout --detach c4901a4bb832608fe6d59d9f9d054c705d11cc0f
mkdir -p ~/.cursor/plugins
ln -s ~/.cursor/staff-engineer-mode-src ~/.cursor/plugins/staff-engineer-mode
```

Reload Cursor with `Developer: Reload Window` or restart the IDE. Cursor reads
the plugin manifest from
`~/.cursor/plugins/staff-engineer-mode/.cursor-plugin/plugin.json`, the router in
`skills/`, and routed specialist files in `specialists/`.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor"
git clone https://github.com/sirmarkz/staff-engineer-mode.git "$env:USERPROFILE\.cursor\staff-engineer-mode-src"
git -C "$env:USERPROFILE\.cursor\staff-engineer-mode-src" checkout --detach c4901a4bb832608fe6d59d9f9d054c705d11cc0f
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\plugins"
cmd /c mklink /J "$env:USERPROFILE\.cursor\plugins\staff-engineer-mode" "$env:USERPROFILE\.cursor\staff-engineer-mode-src"
```

Reload Cursor.

## Per-Project Development Fallback

If the pack should be available only in one Cursor workspace, symlink the whole
repository into a workspace plugin path. A skills-only symlink will expose the
router but not the routed specialist files or hooks.

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

Cursor receives the same router-borne commit and release policy. Before
creating or amending commits, route to `agent-pr-review` for the exact staged
diff. Before tags, version bumps, hosted release records, packages, artifact publication,
or promotion, route to both `release-build-reproducibility` and
`production-readiness-review`.
If the user explicitly accepts unresolved review gaps, state the residual risk
and proceed.

## Updating The Local Development Fallback

Replace the local clone with the target plugin artifact commit and reload
Cursor:

```bash
rm -rf ~/.cursor/staff-engineer-mode-src
mkdir -p ~/.cursor
git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.cursor/staff-engineer-mode-src
git -C ~/.cursor/staff-engineer-mode-src checkout --detach <plugin-artifact-commit>
```

## Uninstalling The Local Development Fallback

```bash
rm ~/.cursor/plugins/staff-engineer-mode
rm -rf ~/.cursor/staff-engineer-mode-src
```
