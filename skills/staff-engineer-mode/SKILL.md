---
name: staff-engineer-mode
description: "Use when asked to route broad or multi-surface engineering requests to one Staff Engineer Mode specialist before answering."
---

# Staff Engineer Mode

## Iron Law

```
ONE PRIMARY SKILL BY DEFAULT; ASK ONLY QUESTIONS WHEN CONFIDENCE IS LOW
```

Loading many plausible skills is a routing failure.

## Overview

Users are not expected to know skill names. Classify ordinary engineering language by artifact, phase, surface, and risk, then quietly select the specialist whose outputs fit the next useful artifact.

## When To Use

- The request is broad, vague, or spans multiple engineering surfaces.
- No single specialist clearly dominates from the prompt.
- The user asks for staff-engineer-level architecture, reliability, security, operations, delivery, data, platform, client, or cost guidance.
- The user asks to troubleshoot an unclear network, deployment, reliability, performance, security, data, or operations issue.

## When Not To Use

- One focused specialist clearly applies.
- The request is product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, broad compliance program management, or business strategy.
- The work is outside system delivery, operations, security, reliability, or maintainability.

## Inputs To Collect

- **Artifact:** decision, plan, gate, rollout, investigation, runbook, policy, migration, eval, evidence pack, or review.
- **Phase:** design, before merge, launch, migration, active incident, post-incident, regression, audit/evidence, or maintenance.
- **Surface:** architecture, contract, reliability target, topology, dependency, performance, observability, delivery, data, platform, security, client, AI, accessibility, cost, or operator load.
- **Risk/scope:** availability, latency, durability, correctness, privacy/security, compatibility, release safety, tenant/customer impact, public edge, internal traffic, multi-service, or multi-location.

## Loaded Specialist Slugs

Pick `primary` and `secondary` only from this exact list. Never invent, shorten, or paraphrase a slug.

```
accessibility-gates, agent-pr-review, ai-coding-governance, api-design-and-compatibility,
architecture-decisions, backup-and-recovery, caching-and-derived-data,
code-readability-for-agents, code-review-and-workflow, configuration-and-automation-safety,
cost-aware-reliability, cryptography-and-key-lifecycle, database-operations, data-contracts,
data-pipeline-reliability, dependency-and-code-hygiene, dependency-resilience,
dev-environment-parity, distributed-data-and-consistency, documentation-lifecycle,
edge-traffic-and-ddos-defense, engineering-control-evidence, event-workflows,
experimentation-and-metric-guardrails, feature-flag-lifecycle, fleet-upgrades,
high-availability-design, identity-and-secrets, incident-response-and-postmortems,
infrastructure-and-policy-as-code, internal-service-networking, llm-application-security,
llm-evaluation, llm-serving-cost-and-latency, migration-and-deprecation,
ml-reliability-and-evaluation, mobile-release-engineering, observability-and-alerting,
oncall-health, performance-and-capacity, platform-golden-paths, privacy-and-data-lifecycle,
production-readiness-review, progressive-delivery, release-build-reproducibility,
resilience-experiments, secure-sdlc-and-threat-modeling, slo-and-error-budgets,
software-supply-chain-security, state-machine-correctness, tenant-isolation,
test-data-engineering, testing-and-quality-gates, vulnerability-management,
web-release-gates
```

## Workflow

1. Identify the requested artifact and phase before naming any skill.
2. Translate named tools into capabilities; do not invent tools, vendors, frameworks, protocols, databases, or commands.
3. Pick `primary` (and any `secondary`) verbatim from the Loaded Specialist Slugs list above; if no listed slug fits, ask a clarification question instead of inventing or paraphrasing one.
4. Choose the narrowest primary whose required outputs match the next artifact.
5. Add one secondary only when the user explicitly asks for a separate artifact covered by another skill.
6. If confidence is low, ask only the missing intake questions needed to route and start useful work.
7. Keep single-surface evidence with the matching specialist skill; use control evidence only for cross-surface mappings, scorecards, exceptions, or evidence packs.
8. Reframe out-of-scope work as an engineering-control question only when that is plausible.

## Synthesized Default

Select one primary when the prompt has enough context. Recommend at most one secondary follow-up. Broad requests become a short sequence, not a pile of loaded skills.

## Exceptions

- For explicit launch/readiness audits, use `production-readiness-review` as primary.
- For active incidents, use `incident-response-and-postmortems` first even if root cause appears to belong elsewhere.
- For vague prompts such as "make this better" or "troubleshoot a network issue", ask intake questions before routing.
- For out-of-scope business/process prompts, do not select a skill unless the user confirms an engineering lifecycle/control framing.

## Required Outputs

- For confident routing: primary skill name; optional secondary only when necessary; confidence of high or medium.
- Inferred intent: requested artifact, dominant surface, work phase, and one-sentence rationale.
- For explicit eval-harness runs only: also include a fenced `routing` block containing a JSON object with `primary`, `secondary`, `confidence`, `artifact`, `surface`, `phase`, and `rationale`.
- For low-confidence routing: questions only; no primary, secondary, confidence label, routing draft, candidate list, or specialist names.
- Out-of-scope reframe when applicable.

## Evidence Gates

- `single_primary`: output has exactly one primary skill unless asking a clarification question.
- `secondary_cap`: output has no more than one secondary skill.
- `capability_translation`: tool, vendor, or framework names are translated into capability language before routing.
- `scope_check`: out-of-scope requests are reframed or declined.
- `ambiguity_check`: ambiguous prompts ask user-facing questions and expose no skill names, candidate routes, confidence labels, or drafts.
- `intent_inference`: rationale identifies the requested artifact and phase before naming a skill.

## Routing Tiebreakers

Use specialist descriptions as the primary map. Load `references/routing-matrix.md` for eval runs, exact-slug uncertainty, or adjacent surfaces.

- Launch or major traffic-shift readiness aggregates through `production-readiness-review`; ordinary design review does not.
- Active user-impacting incidents select `incident-response-and-postmortems` before root-cause specialty work.
- Reliability targets, SLIs/SLOs, error budgets, SLO-based alert review, and page-vs-ticket policy route to `slo-and-error-budgets`; telemetry construction routes to `observability-and-alerting`; page fatigue and toil route to `oncall-health`.
- Topology, restore capability, controlled failure tests, overload controls, invariants, and review workflow span separate surfaces.
- Exposed API/client compatibility routes to `api-design-and-compatibility`, even for branch, PR, before-merge, review, or response-field deprecation prompts.
- Shared dataset/schema compatibility, downstream consumers, and field removal gates route to `data-contracts`.
- Broad service/module retirement or multi-quarter caller migration routes to `migration-and-deprecation`; stale library/dead-code cleanup routes to `dependency-and-code-hygiene`.
- Asynchronous workflow semantics route to `event-workflows`.
- Build/release artifact reproducibility comes before production exposure and rollback strategy.
- Single-domain evidence stays with the matching specialist skill; cross-surface evidence packs use `engineering-control-evidence`.
- Public edge traffic, internal service traffic, backend performance, client performance, cost tradeoffs, and data freshness stay separate.
- Security routes by artifact: threat model, identity/secrets, supply-chain trust, deployed vulnerability remediation, tenant boundary, privacy lifecycle, or model/tool/retrieval app risk.
- Newer narrow routes beat broad neighbors: config/automation safety, documentation lifecycle, data contracts, accessibility gates, AI coding governance, agent PR review, LLM eval harnesses, experimentation guardrails, fleet upgrades, cryptography and key lifecycle, feature flag lifecycle, LLM serving cost and latency, code readability for agents, test data engineering, and dev environment parity.
- Generic senior pre-merge diff review routes to `agent-pr-review` only after narrower API, data, config, rollout, security, and test-gate routes are ruled out.
- Post-rollout flag life, expiry, and removal route to `feature-flag-lifecycle`; introducing the flag during rollout stays with `progressive-delivery`; generic dead-code cleanup stays with `dependency-and-code-hygiene`.
- LLM-route token budget, tail latency, prompt/response cache, and provider-failure degradation route to `llm-serving-cost-and-latency`; generic spend/reliability tradeoffs route to `cost-aware-reliability`; generic backend latency to `performance-and-capacity`; generic remote-call resilience to `dependency-resilience`.
- Service/module/worker boundary ownership routes to `architecture-decisions`, even when retries are mentioned; concrete timeout, retry, idempotency, queue, or overload policy for an existing call or queue routes to `dependency-resilience`.
- Repo-as-artifact for AI comprehension, name collisions, function/file-size budgets, and one-tool-call locatability route to `code-readability-for-agents`; macro service boundaries stay with `architecture-decisions`; per-diff pre-merge review stays with `agent-pr-review`.
- Fixture inventory, anonymization policy, fixture freshness, and production/test data drift route to `test-data-engineering`; overall test strategy and merge gates stay with `testing-and-quality-gates`.
- Local/CI/staging/production parity matrices, drift budgets, and environment-only fixes route to `dev-environment-parity`; reproducible release artifacts stay with `release-build-reproducibility`.
- Rollout and rollback plans for any production-affecting change — including config, schema, data, or client changes — route to `progressive-delivery`; one-shot config edits, bulk scripts, or automation runs without a staged exposure plan stay with `configuration-and-automation-safety`.
- Declarative infrastructure changes with policy checks, drift detection, and reconciliation route to `infrastructure-and-policy-as-code`; ad-hoc config or automation runs against production state stay with `configuration-and-automation-safety`.
- Runtime, platform, or framework version moves across many services, clients, or hosts route to `fleet-upgrades`; retiring an API family, library, or service across callers stays with `migration-and-deprecation`.
- System-level review rules, change-size limits, review-latency targets, and reviewer routing route to `code-review-and-workflow`; org-level rules for AI coding agents (allowed actions, protected paths, secret/data boundaries) stay with `ai-coding-governance`.
- Tenant-boundary audits and cross-tenant isolation proofs — even when triggered by an incident — route to `tenant-isolation`; live incident command and postmortem authorship stay with `incident-response-and-postmortems`.
- Data model splits across databases, shards, or mutation boundaries route to `distributed-data-and-consistency`, even when a migration is mentioned; executing schema, backfill, index, or destructive data changes routes to `database-operations`.
- Cross-service workflows whose correctness depends on storage, replication, sharding, or failover route to `distributed-data-and-consistency`; in-process state machines, protocols, and concurrency invariants stay with `state-machine-correctness`.
- Browser or web client release gates — loading, interaction readiness, layout stability, runtime errors, payload growth, accessibility smoke — route to `web-release-gates` even when phrased as a UI PR review; native mobile rollouts (staged release, crash-free thresholds, kill switches) route to `mobile-release-engineering`.

## Red Flags - Stop And Rework

- More than two skills are selected automatically.
- The router chooses from a phrase match without identifying artifact and phase.
- A tool or vendor name drives routing without capability translation.
- `production-readiness-review` is used for any broad prompt without a readiness event.
- Compliance, staffing, compensation, procurement, or marketing work is routed as engineering work.
- A low-confidence answer names candidate skills, prints a routing draft, or exposes the internal shortlist.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Keyword matching | Infer artifact, phase, surface, and risk. |
| Loading every related skill | Choose one primary and list at most one follow-up. |
| Treating tools as domains | Translate tools to capabilities. |
| Dumping candidate skills | Ask missing diagnostic or scoping questions without naming skills. |
| Avoiding clarification | Ask focused intake questions when confidence is low. |
