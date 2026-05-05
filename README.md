# Staff Engineer Mode

[![Release](https://img.shields.io/github/package-json/v/sirmarkz/staff-engineer-mode?label=release)](./RELEASE-NOTES.md)

**Your AI coding agent ships fast. This makes it ship careful.**

The senior reviewer your AI coding agent is missing.

## Why Now

AI coding agents now write material amounts of production code. The bottleneck is no longer how fast the agent writes — it is whether the agent reasoned about what happens when the code runs at 3am. Agents will happily ship a migration with no rollback, an endpoint with no SLO, an alert with no owner, a config change with no canary. This pack closes that gap.

## How It Works

Ask a normal engineering question. Hand the agent a task. The router reads the work, picks one specialist (occasionally one secondary), and returns concrete risks, gates, owners, evidence, and next steps. You never name a skill.

The router refuses to load every plausible skill. One reviewer at a time, by default.

See [SAMPLE-PROMPTS.md](SAMPLE-PROMPTS.md) for prompts across every specialist.

## Compared To Alternatives

> *agency-agents adds roles. Superpowers adds methodology. Staff Engineer Mode adds a senior reviewer.*

The full positioning grid lives in [COMPARISON.md](COMPARISON.md). None of these replace each other. Compose freely.

## Installation

### Claude Code

```text
/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode
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
Fetch and follow instructions from https://raw.githubusercontent.com/sirmarkz/staff-engineer-mode/main/.codex/INSTALL.md
```

### OpenCode

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/sirmarkz/staff-engineer-mode/refs/heads/main/.opencode/INSTALL.md
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add sirmarkz/staff-engineer-mode
copilot plugin install staff-engineer-mode@staff-engineer-mode
```

### Gemini CLI

```bash
gemini extensions install https://github.com/sirmarkz/staff-engineer-mode
```

## Verify

Start a fresh session inside any open repo and ask one of:

- "Review my last commit and tell me what you would catch in PR review."
- "Find risks in the diff I'm about to push."
- "What did my agent miss in this branch?"

The agent should load the router, choose a specialist, and respond with concrete risks, gates, owners, and evidence — not vibes.

## What's Inside

One router. A specialist for every engineering surface. Three to start with:

- [**`agent-pr-review`**](skills/agent-pr-review/SKILL.md) — the default pre-merge review: applies a senior reviewer's checklist to any diff, human or AI-generated, before it merges.
- [**`production-readiness-review`**](skills/production-readiness-review/SKILL.md) — when a service, feature, migration, tier change, or traffic shift needs go/no-go evidence.
- [**`code-review-and-workflow`**](skills/code-review-and-workflow/SKILL.md) — when reviewer routing, change size, ownership, or workflow quality are the bottleneck.

Examples by surface (the full catalog with prompts for every specialist is in [SAMPLE-PROMPTS.md](SAMPLE-PROMPTS.md)):

| Surface | Example specialists |
| --- | --- |
| Architecture and interfaces | [`architecture-decisions`](skills/architecture-decisions/SKILL.md), [`api-design-and-compatibility`](skills/api-design-and-compatibility/SKILL.md), [`data-contracts`](skills/data-contracts/SKILL.md), [`state-machine-correctness`](skills/state-machine-correctness/SKILL.md) |
| Reliability and resilience | [`slo-and-error-budgets`](skills/slo-and-error-budgets/SKILL.md), [`high-availability-design`](skills/high-availability-design/SKILL.md), [`dependency-resilience`](skills/dependency-resilience/SKILL.md), [`backup-and-recovery`](skills/backup-and-recovery/SKILL.md), [`resilience-experiments`](skills/resilience-experiments/SKILL.md), [`performance-and-capacity`](skills/performance-and-capacity/SKILL.md) |
| Delivery and change safety | [`agent-pr-review`](skills/agent-pr-review/SKILL.md), [`progressive-delivery`](skills/progressive-delivery/SKILL.md), [`feature-flag-lifecycle`](skills/feature-flag-lifecycle/SKILL.md), [`release-build-reproducibility`](skills/release-build-reproducibility/SKILL.md), [`testing-and-quality-gates`](skills/testing-and-quality-gates/SKILL.md), [`test-data-engineering`](skills/test-data-engineering/SKILL.md), [`dev-environment-parity`](skills/dev-environment-parity/SKILL.md), [`migration-and-deprecation`](skills/migration-and-deprecation/SKILL.md), [`code-review-and-workflow`](skills/code-review-and-workflow/SKILL.md), [`code-readability-for-agents`](skills/code-readability-for-agents/SKILL.md), [`documentation-lifecycle`](skills/documentation-lifecycle/SKILL.md), [`dependency-and-code-hygiene`](skills/dependency-and-code-hygiene/SKILL.md), [`configuration-and-automation-safety`](skills/configuration-and-automation-safety/SKILL.md), [`fleet-upgrades`](skills/fleet-upgrades/SKILL.md) |
| Operations and observability | [`observability-and-alerting`](skills/observability-and-alerting/SKILL.md), [`incident-response-and-postmortems`](skills/incident-response-and-postmortems/SKILL.md), [`oncall-health`](skills/oncall-health/SKILL.md), [`production-readiness-review`](skills/production-readiness-review/SKILL.md) |
| Security and privacy | [`secure-sdlc-and-threat-modeling`](skills/secure-sdlc-and-threat-modeling/SKILL.md), [`identity-and-secrets`](skills/identity-and-secrets/SKILL.md), [`cryptography-and-key-lifecycle`](skills/cryptography-and-key-lifecycle/SKILL.md), [`software-supply-chain-security`](skills/software-supply-chain-security/SKILL.md), [`vulnerability-management`](skills/vulnerability-management/SKILL.md), [`tenant-isolation`](skills/tenant-isolation/SKILL.md), [`privacy-and-data-lifecycle`](skills/privacy-and-data-lifecycle/SKILL.md), [`engineering-control-evidence`](skills/engineering-control-evidence/SKILL.md) |
| Data and workflow systems | [`distributed-data-and-consistency`](skills/distributed-data-and-consistency/SKILL.md), [`database-operations`](skills/database-operations/SKILL.md), [`event-workflows`](skills/event-workflows/SKILL.md), [`data-pipeline-reliability`](skills/data-pipeline-reliability/SKILL.md), [`caching-and-derived-data`](skills/caching-and-derived-data/SKILL.md) |
| Platform and edge | [`platform-golden-paths`](skills/platform-golden-paths/SKILL.md), [`infrastructure-and-policy-as-code`](skills/infrastructure-and-policy-as-code/SKILL.md), [`internal-service-networking`](skills/internal-service-networking/SKILL.md), [`edge-traffic-and-ddos-defense`](skills/edge-traffic-and-ddos-defense/SKILL.md), [`cost-aware-reliability`](skills/cost-aware-reliability/SKILL.md) |
| Client, ML/AI, and experimentation | [`web-release-gates`](skills/web-release-gates/SKILL.md), [`mobile-release-engineering`](skills/mobile-release-engineering/SKILL.md), [`accessibility-gates`](skills/accessibility-gates/SKILL.md), [`ai-coding-governance`](skills/ai-coding-governance/SKILL.md), [`llm-application-security`](skills/llm-application-security/SKILL.md), [`llm-evaluation`](skills/llm-evaluation/SKILL.md), [`llm-serving-cost-and-latency`](skills/llm-serving-cost-and-latency/SKILL.md), [`ml-reliability-and-evaluation`](skills/ml-reliability-and-evaluation/SKILL.md), [`experimentation-and-metric-guardrails`](skills/experimentation-and-metric-guardrails/SKILL.md) |

Every specialist appears in [SAMPLE-PROMPTS.md](SAMPLE-PROMPTS.md) with three representative prompts.

## Contributing

Patches welcome — especially additional practices from authoritative sources: first-party engineering publications, official documentation, standards bodies, peer-reviewed papers, or widely cited practitioner references.

New skills must be technology-agnostic, cite stable source IDs, and avoid vendor endorsement. Read [STYLE.md](STYLE.md) before opening a PR. The voice is enforced.

## Maintainers

See [MAINTAINERS.md](MAINTAINERS.md). For security issues, contact the maintainer listed there.

## Sources And Influences

Practices in this pack are synthesized from public engineering writing at large operators (Google, Amazon, Meta, Microsoft, Apple, Netflix) and from standards work cited by their teams (NIST, CISA, OWASP, OpenSSF, IETF, W3C). Specific source IDs are in `skills/_shared/references/source-index.md`. This is an independent project; nothing here is endorsed by or affiliated with those organizations.

## License

MIT — see [LICENSE](LICENSE).

## Notice

Independent. Cites primary sources. Vendor-neutral by default.

---

*Fewer vibes. More engineering.*
