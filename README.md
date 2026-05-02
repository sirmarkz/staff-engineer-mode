# Staff Engineer Mode

[![Release](https://img.shields.io/github/package-json/v/tnilabs/staff-engineer-mode?label=release)](./RELEASE-NOTES.md)

Turn your coding agent into a staff engineer.

Your agent is already fast at writing code. It is less fast at noticing that
the migration will lock production, the endpoint breaks an old client, the
rollout has no rollback, the dashboard has no alert, and the postmortem is
about to start with "we should have caught this in review."

Staff Engineer Mode makes agents think where it matters: compatibility, failure
modes, rollout risk, ownership, observability, security, recovery, and evidence
before they touch the keyboard.

It is synthesized from more than 200 authoritative public sources: Google SRE
and engineering practices, Amazon and AWS engineering writing, Microsoft and
Azure guidance, Meta and Netflix engineering publications, Apple platform
material, NIST, CISA, OWASP, OpenSSF, IETF/W3C standards, and widely adopted
practitioner patterns.
It is not affiliated with or endorsed by any company, standards body, or project
it draws on.

You should not have to memorize skill names. Ask a normal engineering question.
The router selects the smallest useful specialist set, then the agent answers
with concrete risks, gates, owners, evidence, and next steps. Ideally fewer
vibes, more engineering.

See [sample prompts](SAMPLE-PROMPTS.md) for practical examples across every
skill.

## Why Use It During Development

Staff Engineer Mode keeps production engineering habits active across the whole
development loop while the agent plans, edits, reviews, migrates, releases, and
debugs.

Base models can generate working code, but they do not reliably sustain those
habits through every step.

Use it when you want your agent to follow practices drawn from Big Tech
engineering organizations and public standards: protect compatibility, check
failure modes, make production changes reversible, instrument what matters,
preserve recovery paths, and leave reviewable evidence behind.

## How It Works

Everything enters through `staff-engineer-mode`.

The router classifies the request by engineering surface, event type, risk, and
scope. It picks one primary specialist by default, adds at most one secondary
when clearly needed, and asks a single clarifying question when routing would
otherwise be noisy.

Forty specialist skills then push the agent toward useful artifacts: ADRs, API
compatibility reviews, rollout plans, SLOs, incident timelines, threat models,
production-readiness checks, migration plans, dependency matrices, control
evidence, and client or model release gates.

The goal is judgment, not verbosity. Skills move the agent toward compatibility,
safety, reliability, security, operability, ownership, rollout, and evidence
before it changes anything.

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

Forty specialist skills, grouped by engineering surface.

**Architecture and interfaces**
- `api-design-and-compatibility`
- `architecture-review-and-decision-records`

**Reliability and resilience**
- `slo-error-budget-engineering`
- `high-availability-design-and-validation`
- `dependency-resilience-and-overload`
- `capacity-performance-and-tail-latency`
- `backup-restore-and-disaster-recovery`
- `resilience-experiments-and-chaos-engineering`
- `systems-correctness-and-formal-validation`

**Delivery and quality**
- `testing-and-quality-gates`
- `release-build-reproducibility`
- `progressive-delivery-and-safe-change`
- `production-readiness-review`
- `large-scale-change-and-service-deprecation`
- `engineering-productivity-and-code-review`
- `dependency-hygiene-and-code-health`

**Operations and observability**
- `observability-and-alerting`
- `incident-response-and-postmortems`
- `oncall-health-and-toil-reduction`

**Security and privacy**
- `secure-sdlc-and-threat-modeling`
- `zero-trust-identity-and-secrets`
- `software-supply-chain-security`
- `vulnerability-management-and-patch-sla`
- `tenant-isolation-and-data-protection`
- `privacy-engineering-and-data-lifecycle`
- `engineering-control-evidence`
- `llm-application-security`

**Data, platform, and client systems**
- `distributed-data-and-consistency`
- `event-driven-systems-and-workflows`
- `caching-and-derived-data`
- `database-operations-and-schema-changes`
- `data-pipeline-reliability`
- `ml-systems-reliability-and-evaluation`
- `platform-engineering-and-golden-paths`
- `infrastructure-gitops-and-policy-as-code`
- `internal-networking-and-service-mesh`
- `edge-traffic-and-ddos-defense`
- `finops-and-cost-aware-reliability`
- `mobile-release-engineering-and-crash-budgets`
- `frontend-performance-release-gates`

Marketplace installs update through the target platform's plugin or extension
update flow.

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

This is an independent TNI Labs project. It is not endorsed by or affiliated
with any company, standards body, or open-source project it draws on. Read
`NOTICE.md` before publishing, redistributing, quoting, or adding source
material.
