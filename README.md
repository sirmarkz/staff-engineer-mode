# Staff Engineer Mode

[![Release](https://img.shields.io/github/package-json/v/tnilabs/staff-engineer-mode?label=release)](./RELEASE-NOTES.md)

Turn your coding agent into a staff engineer.

Staff Engineer Mode steers coding agents toward production-grade engineering
judgment as they plan, edit, review risk, migrate data, release, debug, and
leave reviewable evidence, using practices drawn from Big Tech engineering
organizations and public standards. Fewer vibes, more engineering.

It is synthesized from more than 200 authoritative public sources: Google SRE
and engineering practices, Amazon and AWS engineering writing, Microsoft and
Azure guidance, Meta and Netflix engineering publications, Apple platform
material, NIST, CISA, OWASP, OpenSSF, IETF/W3C standards, and widely adopted
practitioner patterns.
It is not affiliated with or endorsed by any company, standards body, or project
it draws on.

You should not have to memorize skill names. Ask a normal engineering question
or hand the agent a development task. The router selects the smallest useful
specialist set, then the agent works through concrete risks, gates, owners,
evidence, and next steps.

See [sample prompts](SAMPLE-PROMPTS.md) for practical examples across every
skill.

## How It Works

Everything enters through `staff-engineer-mode`.

The router classifies the request by engineering surface, event type, risk, and
scope. It picks one primary specialist by default, adds at most one secondary
when clearly needed, and asks a single clarifying question when routing would
otherwise be noisy.

It composes with other skill packs, including Superpowers, by adding
engineering-surface routing and risk checks without replacing other workflows.

Forty specialist skills push the agent toward judgment, not verbosity: ADRs,
compatibility reviews, rollout plans, SLOs, incident timelines, threat models,
readiness checks, migration plans, dependency matrices, control evidence, and
release gates that keep compatibility, safety, reliability, security,
operability, ownership, rollout, and evidence in view before changes land.

## Installation

Installation differs by platform.

### Claude Code Marketplace

Run these as separate slash commands:

```text
/plugin marketplace add https://github.com/tnilabs/staff-engineer-mode
/plugin install staff-engineer-mode@staff-engineer-mode
```

### Cursor

In Cursor Agent chat:

```text
/add-plugin staff-engineer-mode
```

Or search `staff-engineer-mode` in the plugin marketplace.

### Codex

Works with Codex CLI and Codex App. Tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/tnilabs/staff-engineer-mode/refs/heads/main/.codex/INSTALL.md
```

### OpenCode

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/tnilabs/staff-engineer-mode/refs/heads/main/.opencode/INSTALL.md
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add tnilabs/staff-engineer-mode
copilot plugin install staff-engineer-mode@staff-engineer-mode
```

### Gemini CLI

```bash
gemini extensions install https://github.com/tnilabs/staff-engineer-mode
```

## Verify Installation

Start a fresh session and ask for something that requires engineering judgment:

```text
Review this checkout migration plan for production readiness.
```

The agent should load the router, choose a specialist, and respond with
concrete risks, gates, owners, and evidence, not just vibes.

For the authoritative source list behind the skills, see the
[source index](skills/_shared/references/source-index.md).

## What's Inside

Forty specialist skills across six engineering surfaces: architecture and
interfaces (2), reliability and resilience (7), delivery and quality (7),
operations and observability (3), security and privacy (8), and data, platform,
and client systems (13).

## Contributing

Contributions are welcome, especially additional engineering practices from
highly reliable, authoritative sources: first-party engineering publications,
official documentation, standards bodies, peer-reviewed papers, or widely cited
practitioner references that originated the pattern.

Keep contributions focused on engineering lifecycle, DevOps, operations,
reliability, security, stability, architecture, and maintainability. New skills
or guidance should synthesize the source material into technology-agnostic
operational instructions, cite stable source IDs from the shared references, and
avoid vendor endorsement or process-only advice.

## License

MIT - see `LICENSE`.

## Notice

This is an independent project. It is not endorsed by or affiliated with any
company, standards body, or open-source project it draws on.
