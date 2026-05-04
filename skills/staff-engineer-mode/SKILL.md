---
name: staff-engineer-mode
description: "Use to route broad or multi-surface engineering requests to one Staff Engineer Mode specialist before answering."
---

# Staff Engineer Mode

## Overview

Users are not expected to know skill names. This router classifies ordinary engineering language and selects the one specialist that owns the next useful artifact.

Do not answer as a generic expert, route by keyword, or restate specialist guidance. Infer the artifact, phase, surface, and risk, then hand off quietly.

## Iron Law

```
ONE PRIMARY SKILL BY DEFAULT; ASK ONLY QUESTIONS WHEN CONFIDENCE IS LOW
```

Loading many plausible skills is a routing failure.

## When To Use

- The request is broad, vague, or spans multiple engineering surfaces.
- No single specialist clearly dominates from the prompt.
- The user asks for staff-engineer-level production quality, architecture, reliability, security, operations, delivery, data, platform, client, or cost-aware engineering guidance.
- The user asks to troubleshoot an unclear network, deployment, reliability, performance, security, data, or operations issue.

## When Not To Use

- One focused specialist clearly applies.
- The request is product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, broad compliance program management, or business strategy.
- The work is outside system delivery, operations, security, reliability, or maintainability.

## Inputs To Collect

- **Artifact:** decision, plan, gate, rollout, investigation, runbook, policy, migration, evaluation, evidence pack, or review.
- **Phase:** design, before merge, launch, migration, active incident, post-incident, regression, audit/evidence, or maintenance.
- **Surface:** architecture, contract, reliability target, topology, dependency, performance, observability, delivery, data, platform, security, client, AI, accessibility, cost, or operator load.
- **Risk and scope:** availability, latency, durability, correctness, privacy/security, compatibility, release safety, tenant/customer impact, public edge, internal traffic, multi-service, or multi-region.

## Workflow

1. Identify the requested artifact and phase before naming any skill.
2. Translate named tools into capabilities. Do not invent tool, vendor, framework, protocol, database, or command examples when the user did not provide them.
3. Choose the narrowest primary whose required outputs match the next artifact.
4. Add one secondary only when the user explicitly asks for a separate artifact owned by another skill.
5. If confidence is low, ask only the missing intake questions needed to route and start useful work.
6. Keep single-surface evidence with the surface owner; use control evidence only for cross-surface mappings, scorecards, exceptions, or evidence packs.
7. Reframe out-of-scope work as an engineering-control question only when that is plausible.

## Synthesized Default

Select exactly one primary specialist when the prompt has enough context. Recommend at most one secondary as a follow-up. Broad requests should become a short sequence, not a pile of loaded skills.

## Exceptions

- For explicit launch/readiness audits, use `production-readiness-review` as primary.
- For active incidents, use `incident-response-and-postmortems` first even if root cause appears to belong elsewhere.
- For vague prompts such as "make this better" or "troubleshoot a network issue", ask intake questions before routing.
- For out-of-scope business/process prompts, do not select a skill unless the user confirms an engineering lifecycle/control framing.

## Required Outputs

- For confident routing: primary skill name.
- For confident routing: optional secondary skill name, only when necessary.
- For confident routing: confidence of high or medium.
- For confident routing: inferred user intent, including requested artifact, dominant surface, and work phase.
- For confident routing: routing rationale in one or two sentences.
- For explicit eval-harness runs only: also include a fenced `routing` block containing a JSON object with `primary`, `secondary`, `confidence`, `artifact`, `surface`, `phase`, and `rationale`.
- For low-confidence routing: questions only.
- Do not include a primary, secondary, confidence label, routing draft, candidate list, or any specialist skill names.
- Out-of-scope reframe when applicable.

## Evidence Gates

- `single_primary`: output has exactly one primary skill unless asking a clarification question.
- `secondary_cap`: output has no more than one secondary skill.
- `capability_translation`: tool, vendor, or framework names are translated into capability language before routing.
- `scope_check`: out-of-scope requests are reframed or declined.
- `ambiguity_check`: ambiguous prompts ask only user-facing questions and expose zero skill names, candidate routes, confidence labels, or routing drafts.
- `intent_inference`: rationale identifies the requested artifact and phase before naming a skill.

## Routing Tiebreakers

Use specialist descriptions as the primary map. Load `references/routing-matrix.md` only when adjacent surfaces compete.

- Launch or major traffic-shift readiness aggregates through `production-readiness-review`; ordinary design review does not.
- Active user-impacting incidents route to `incident-response-and-postmortems` before root-cause specialty work.
- Reliability objective policy, telemetry construction, and page fatigue are separate artifacts.
- Topology, restore capability, controlled failure tests, and overload controls have separate owners.
- Exposed contract compatibility, broad deprecation/migration, and asynchronous workflow semantics are distinct.
- Build/release artifact reproducibility comes before production exposure and rollback strategy.
- Single-domain evidence stays with the owner; cross-surface evidence packs use `engineering-control-evidence`.
- Public edge traffic, internal service traffic, backend performance, client performance, cost tradeoffs, and data movement freshness should not be collapsed into one route.
- Security routes by artifact: threat model, identity/secrets, supply-chain trust, deployed vulnerability remediation, tenant boundary, privacy lifecycle, or model/tool/retrieval app risk.
- Newer narrow routes beat broad neighbors: config/automation safety, documentation lifecycle, data contracts, accessibility gates, AI coding governance, agent PR review, LLM eval harnesses, experimentation guardrails, fleet upgrades, cryptography and key lifecycle, feature flag lifecycle, LLM serving cost and latency, code readability for agents, test data engineering, and dev environment parity.
- An AI-agent-produced diff that needs a senior pre-merge review routes to `agent-pr-review`; org-level AI-assisted coding policy still routes to `ai-coding-governance`; reviewer routing, change size, and workflow metrics stay with `code-review-and-workflow`.
- Post-rollout flag life, owners, expiry, and removal route to `feature-flag-lifecycle`; introducing the flag during rollout stays with `progressive-delivery`; generic dead-code cleanup stays with `dependency-and-code-hygiene`.
- LLM-route token budget, tail latency, prompt/response cache, and provider-failure degradation route to `llm-serving-cost-and-latency`; generic spend/reliability tradeoffs route to `cost-aware-reliability`; generic backend latency to `performance-and-capacity`; generic remote-call resilience to `dependency-resilience`.
- Repo-as-artifact for AI comprehension, name collisions, function/file-size budgets, and one-tool-call locatability route to `code-readability-for-agents`; macro service boundaries stay with `architecture-decisions`; per-diff agent review stays with `agent-pr-review`.
- Fixture inventory, anonymization policy, fixture freshness, and production/test data drift route to `test-data-engineering`; overall test strategy and merge gates stay with `testing-and-quality-gates`.
- Local/CI/staging/production parity matrices, drift budgets, and environment-only fixes route to `dev-environment-parity`; reproducible release artifacts stay with `release-build-reproducibility`.

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
