# Installing Staff Engineer Mode For Codex

Enable Staff Engineer Mode in OpenAI Codex through the Codex plugin system. The
plugin exposes one native router skill, keeps routed specialist files under
`specialists/`, and installs the session and command hooks that carry routing,
commit, and release policy.

## Prerequisites

- Git
- Codex CLI, or Codex App with plugin support

## Install From A Terminal

Run these commands in your shell, not inside a Codex chat:

```bash
codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git --ref b658229b384d79227f7dd93d59cd3bdad22c75cd
codex plugin add staff-engineer-mode@staff-engineer-mode
```

This pins the marketplace checkout to commit
`b658229b384d79227f7dd93d59cd3bdad22c75cd`; that marketplace entry installs
plugin artifact commit `c4901a4bb832608fe6d59d9f9d054c705d11cc0f`.
Do not omit the `--ref` value. Without it, Codex resolves the repository's
default branch at install time.

Restart Codex after installation so skills and hooks are loaded.

## Install From Codex App

Open Plugins in the Codex App sidebar, search for `Staff Engineer Mode`, and
install it from the Coding category when published.

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

## Hooks And Policy

The plugin includes a `SessionStart` hook that adds `SPECIALIST_ROOT`,
`EVENT_HOOK`, and the Staff Engineer Mode routing contract to each Codex
session. It also includes a command policy hook for commit and release events
when the host runs plugin hooks.

Before creating or amending commits, the agent must stage separately, inspect
the exact staged diff, read `agent-pr-review`, review the staged change, record
the commit receipt, and then commit. Before tags, version bumps, hosted release
records, packages, artifact publication, or promotion, the agent must read and
apply both `release-build-reproducibility` and `production-readiness-review`,
record the release receipt, and then run the release command.

## Updating

To move to a newer release:

1. Find the plugin artifact commit for the release.
2. Find the later marketplace metadata commit whose
   `.claude-plugin/marketplace.json` points at that artifact commit.
3. Replace the marketplace ref below with that marketplace metadata commit.

```bash
codex plugin remove staff-engineer-mode@staff-engineer-mode
codex plugin marketplace remove staff-engineer-mode
codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git --ref <marketplace-metadata-commit>
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
git -C ~/.codex/staff-engineer-mode checkout --detach c4901a4bb832608fe6d59d9f9d054c705d11cc0f
mkdir -p ~/.agents/skills
ln -s ~/.codex/staff-engineer-mode/skills ~/.agents/skills/staff-engineer-mode
```

### Windows PowerShell

Use a junction instead of a symlink:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex"
git clone https://github.com/sirmarkz/staff-engineer-mode.git "$env:USERPROFILE\.codex\staff-engineer-mode"
git -C "$env:USERPROFILE\.codex\staff-engineer-mode" checkout --detach c4901a4bb832608fe6d59d9f9d054c705d11cc0f
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
