# Installing Staff Engineer Mode For Codex

Enable Staff Engineer Mode in OpenAI Codex through native skill discovery. The
native skill tree exposes only the router; specialist guidance stays in the
repository under `specialists/` and is read only after routing.

## Prerequisites

- Git
- OpenAI Codex CLI or Codex App

## Plugin Marketplace

In Codex CLI, open the plugin search interface:

```text
/plugins
```

Search for `staff-engineer-mode`, then select `Install Plugin` when it is available.

In the Codex App, open Plugins in the sidebar, search for `Staff Engineer Mode`, and
install it from the Coding category when published.

## Manual Installation

### Linux / macOS

```bash
git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.codex/staff-engineer-mode
mkdir -p ~/.agents/skills
ln -s ~/.codex/staff-engineer-mode/skills ~/.agents/skills/staff-engineer-mode
```

### Windows PowerShell

Use a junction instead of a symlink:

```powershell
git clone https://github.com/sirmarkz/staff-engineer-mode.git "$env:USERPROFILE\.codex\staff-engineer-mode"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\staff-engineer-mode" "$env:USERPROFILE\.codex\staff-engineer-mode\skills"
```

Restart Codex after installation.

## How It Works

Codex scans `~/.agents/skills/` at startup, parses `SKILL.md` frontmatter, and
loads skills on demand. Staff Engineer Mode is exposed as one router skill:

```text
~/.agents/skills/staff-engineer-mode/ -> ~/.codex/staff-engineer-mode/skills/
```

Users should not need to name individual specialists. Broad engineering
requests route through `staff-engineer-mode`, which then reads the selected
specialist file from `~/.codex/staff-engineer-mode/specialists/<slug>/SKILL.md`.

## Specialist Loading

Codex does not currently fire a SessionStart hook for this pack, so no
`SPECIALIST_ROOT` environment variable is published at session start. The
**Load Contract** in `skills/staff-engineer-mode/SKILL.md` is the source of
truth: it tells the model to `Read` from
`~/.codex/staff-engineer-mode/specialists/<slug>/SKILL.md` whenever
`SPECIALIST_ROOT` is unavailable. Never call the Skill tool on a specialist
slug -- specialists are files, not registered Codex skills, and a `Skill`
invocation will fail with `Unknown skill`. No per-user wiring is required;
the contract is router-borne.

## Verify

```bash
ls -la ~/.agents/skills/staff-engineer-mode
```

Then ask Codex:

```text
Review this service for production readiness.
```

The router should choose `production-readiness-review` as the primary skill, or
ask one clarifying question if the request lacks a concrete engineering surface.

## When Other Skill Packs Are Installed

Codex native skills do not currently give this pack a session-start bootstrap
hook. If another installed pack has very broad process skills, it can preempt
vague prompts such as "troubleshoot a network issue." Add this project
instruction when you want Staff Engineer Mode to route engineering-system work
first:

```markdown
For engineering lifecycle, architecture, reliability, resilience, operations,
security, delivery, data, platform, client, or cost-aware reliability requests,
use Staff Engineer Mode before generic debugging or process skills. When the
request is ambiguous, ask only the intake questions needed to route it; do not
print specialist names, routing drafts, confidence labels, or candidate lists.
```

## Updating

```bash
cd ~/.codex/staff-engineer-mode && git pull
```

Skills update instantly through the symlink. Restart Codex if metadata does not
refresh.

## Uninstalling

```bash
rm ~/.agents/skills/staff-engineer-mode
```

Windows PowerShell:

```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\staff-engineer-mode"
```

Optionally delete the clone: `rm -rf ~/.codex/staff-engineer-mode`.
