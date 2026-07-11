# Installing Staff Engineer Mode For Codex

Enable Staff Engineer Mode in OpenAI Codex through the Codex plugin system. The
plugin exposes one native router skill and keeps routed specialist files under
`specialists/`. Event-policy guidance travels through the router and specialist
files; bundled hooks provide the command-interception layer when Codex loads
plugin lifecycle hooks.

## Prerequisites

- Git
- Codex CLI

## Install From A Terminal

Run these commands in your shell, not inside a Codex chat:

```bash
codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git
codex plugin add staff-engineer-mode@staff-engineer-mode
```

Codex clones the marketplace automatically and installs the plugin selected by
the marketplace manifest.

Restart Codex after installation so skills are loaded.

## Verify

From a terminal:

```bash
codex plugin marketplace list
codex plugin list --marketplace staff-engineer-mode
```

Then start a fresh Codex session in a repository and ask:

```text
Review this service for production readiness.
```

The session should load the Staff Engineer Mode bootstrap, route the request to
one primary specialist, and read the selected file from
`specialists/<slug>.md` before giving engineering guidance.

## How It Works

Codex installs the plugin from the configured marketplace snapshot and loads the
router skill from `skills/staff-engineer-mode/SKILL.md`. The router is the only
native skill entrypoint. Specialist guidance remains in repository files:

```text
<plugin root>/specialists/<slug>.md
```

Users should not need to name individual specialists. Broad engineering
requests route through `staff-engineer-mode`, which then reads the selected
specialist file.

## Event Policy

Codex plugin installs expose the router skill and bundled hook configuration.
The router still carries the same commit and release flow for Codex builds or
surfaces where lifecycle hooks are unavailable. The host PreToolUse hook is the
command-interception layer; `hooks/agent-event-policy ack ...` records receipts
and does not self-fail when command hooks are bypassed.

Before creating or amending commits, the agent must read `agent-pr-review`,
stage separately, inspect and review the exact staged diff, record the commit
receipt, and then commit. Before tags, version bumps, hosted release
records, packages, artifact publication, or promotion, the agent must read and
apply both `release-build-reproducibility` and `production-readiness-review`,
record the release receipt, and then run the release command.

## Updating

To refresh to the latest marketplace metadata:

```bash
codex plugin marketplace upgrade staff-engineer-mode
codex plugin remove staff-engineer-mode@staff-engineer-mode
codex plugin add staff-engineer-mode@staff-engineer-mode
```

Restart Codex after updating.

## Skills-Only Fallback

Use this only when the Codex plugin system is unavailable. It exposes the router
skill through native skill discovery, but it does not install plugin metadata or
hooks.

### Linux / macOS

```bash
mkdir -p ~/.codex
git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.codex/staff-engineer-mode
mkdir -p ~/.agents/skills
ln -s ~/.codex/staff-engineer-mode/skills ~/.agents/skills/staff-engineer-mode
```

### Windows PowerShell

Use a junction instead of a symlink:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex"
git clone https://github.com/sirmarkz/staff-engineer-mode.git "$env:USERPROFILE\.codex\staff-engineer-mode"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\staff-engineer-mode" "$env:USERPROFILE\.codex\staff-engineer-mode\skills"
```

Restart Codex after fallback installation.

## Uninstalling

Plugin install:

```bash
codex plugin remove staff-engineer-mode@staff-engineer-mode
codex plugin marketplace remove staff-engineer-mode
```

Skills-only fallback:

```bash
rm ~/.agents/skills/staff-engineer-mode
rm -rf ~/.codex/staff-engineer-mode
```

Windows PowerShell fallback:

```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\staff-engineer-mode"
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\staff-engineer-mode"
```
