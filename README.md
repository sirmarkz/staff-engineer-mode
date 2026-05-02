# Staff Engineer Mode

[![Release](https://img.shields.io/github/package-json/v/tnilabs/staff-engineer-mode?label=release)](./RELEASE-NOTES.md)

The checks staff engineers run before code ships at serious engineering orgs —
turned into routing skills your coding agent can use without you naming the
specific skill.

Readiness reviews. Rollback plans. Threat models. SLOs and error budgets.
Compatibility checks. Migration playbooks. Runbooks. Blast-radius math. The
forty-nine things a senior engineer walks through across design, merge, launch,
incidents, and maintenance — now your agent walks them too, on the right change,
at the right time.

Drawn from public engineering practice at Google, Amazon, Meta, Microsoft,
Apple, and Netflix, plus the standards bodies their teams cite (NIST, CISA,
OWASP, OpenSSF, IETF, W3C). Independent project. Not affiliated.

**Fewer vibes. More engineering.**

## How It Works

Ask a normal engineering question. Hand the agent a task. The router picks
the smallest useful specialist set — one primary, occasionally one secondary —
and the agent works through concrete risks, gates, owners, evidence, and
next steps. You never name a skill.

Composes with other skill packs (including Superpowers) without replacing
their workflows.

See [SAMPLE-PROMPTS.md](SAMPLE-PROMPTS.md) for examples across every skill.

## Installation

### Claude Code

```text
/plugin marketplace add https://github.com/tnilabs/staff-engineer-mode
/plugin install staff-engineer-mode@staff-engineer-mode
```

### Cursor

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

## Verify

Start a fresh session and ask:

```text
Review this checkout migration plan for production readiness.
```

The agent should load the router, choose a specialist, and respond with
concrete risks, gates, owners, and evidence — not vibes.

## What's Inside

One router. Forty-nine specialists across eight surfaces: architecture and
interfaces, reliability and resilience, delivery and change safety, operations
and observability, security and privacy, data and workflow systems, platform
and edge, and client/ML/AI/experimentation.

## Contributing

Contributions welcome — especially additional practices from authoritative
sources: first-party engineering publications, official docs, standards
bodies, peer-reviewed papers, or widely cited practitioner references.

Keep contributions focused on engineering lifecycle work. New guidance should
be technology-agnostic, cite stable source IDs, and avoid vendor endorsement.

## License

MIT — see [LICENSE](LICENSE).

## Notice

Independent project. Not endorsed by or affiliated with any company,
standards body, or open-source project it draws on.
