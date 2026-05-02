---
name: staff-engineer-mode
description: "Use to classify a natural-language engineering request into the smallest useful Staff Engineer Mode skill set when the request spans multiple engineering facets or no specialist skill matches with high confidence. Do not use when one focused specialist skill clearly applies."
---

# Staff Engineer Mode

## Overview

Users are not expected to know skill names. The router must infer intent from ordinary engineering language and select the smallest useful skill set with low noise.

The router is a classifier: from realistic user prose, identify the next engineering artifact and hand off to the one specialist that owns it. Do not route by vendor vocabulary, keyword coincidence, or a restatement of specialist guidance.

## Iron Law

```
ONE PRIMARY SKILL BY DEFAULT; ASK ONE QUESTION WHEN CONFIDENCE IS LOW
```

Loading many plausible skills is a routing failure. The router should be conservative, explicit, and quiet.

## When To Use

- The request spans multiple engineering surfaces and needs sequencing.
- No single specialist skill is obviously dominant.
- The user asks for broad staff-engineer-level engineering standards, production quality, architecture review, launch readiness, reliability, security, operations, or DevOps guidance.
- The prompt is ambiguous and needs one clarifying question before a specialist can act.

## When Not To Use

- One focused specialist clearly applies with high confidence.
- The request is product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, broad compliance program management, or business strategy.
- The user explicitly asks for non-engineering process work outside system delivery, operations, security, reliability, or maintainability.

## Inputs To Collect

- **Surface:** architecture, API, reliability target, topology, dependency, performance, observability, delivery, incident, data, platform, security, client, or cost.
- **Deliverable:** decision record, compatibility plan, SLO policy, topology review, overload plan, performance investigation, release gate, rollout plan, incident timeline, migration plan, control evidence, or platform standard.
- **Phase:** design, before merge, before production exposure, launch, migration, active incident, post-incident, regression, audit/evidence, or steady-state maintenance.
- **Risk:** availability, latency, durability, correctness, privacy/security, cost, operator load, compatibility, or release safety.
- **Scope:** single component, multi-service, platform, tenant/customer, public edge, multi-region, standard, or launch.
- **Ambiguity:** whether the user means target policy, implementation mechanics, existing pain reduction, or broad review.

## Workflow

1. **Name the artifact and phase.** Identify what the user is asking the agent to produce now and where the work sits: design, merge, launch, migration, incident, regression, audit, or maintenance.
2. **Translate named tools into capabilities.** Convert provider, framework, database, queue, observability, identity, build, or edge product names into the underlying engineering capability before routing.
3. **Choose the narrowest primary.** Prefer the specialist whose required outputs match the next artifact and dominant surface, not nouns that merely appear in the prompt.
4. **Add one secondary only for a separate artifact.** A secondary is valid only when the user explicitly asks for another deliverable owned by another skill.
5. **Ask one question when needed.** If two or three skills are plausible and no primary dominates, ask one disambiguating question about the deliverable or phase.
6. **Use production readiness only as an aggregator.** Route to production readiness only for launch, major migration, traffic shift, tier change, or broad readiness audit.
7. **Keep single-surface evidence with the owner.** Use engineering control evidence only when the user asks for cross-surface mappings, scorecards, exceptions, or evidence packs.
8. **Reframe out-of-scope work.** State the pack boundary and ask whether the user wants the adjacent engineering-control version.
9. **Return routing, not content.** Provide primary skill, optional secondary, rationale, and next action. The specialist owns the detailed guidance.

## Synthesized Default

Select exactly one primary specialist. Recommend at most one secondary as a follow-up when a separate engineering surface is explicit. Broad requests should become a short sequence, not a pile of loaded skills.

## Exceptions

- For explicit launch/readiness audits, use `production-readiness-review` as primary because it aggregates evidence.
- For active incidents, use `incident-response-and-postmortems` first even if root cause appears architectural, security-related, or deployment-related.
- For vague prompts such as "make this better", ask one question before routing.
- For out-of-scope business/process prompts, do not select a skill unless the user confirms an engineering lifecycle/control framing.

## Required Outputs

- Primary skill name.
- Optional secondary skill name, only when necessary.
- Confidence: high, medium, or ask.
- Inferred user intent: the requested artifact, dominant surface, and work phase.
- Routing rationale in one or two sentences.
- One disambiguating question when confidence is low.
- Out-of-scope reframe when applicable.

## Evidence Gates

- `single_primary`: output has exactly one primary skill unless asking a clarification question.
- `secondary_cap`: output has no more than one secondary skill.
- `capability_translation`: tool, vendor, or framework names are translated into capability language before routing.
- `scope_check`: out-of-scope requests are reframed or declined.
- `ambiguity_check`: ambiguous prompts get one question, not multiple speculative skills.
- `intent_inference`: rationale identifies the user's requested artifact and phase from prose before naming a skill.

## Routing Tiebreakers

Use this as a context map, not a keyword list. Each row describes the situation that must be true before selecting the skill.

| Situation that owns the next artifact | Primary skill | Choose instead when |
| --- | --- | --- |
| The user needs a system design review, tradeoff analysis, service boundary, RFC, ADR, or decision record before work proceeds. | `architecture-review-and-decision-records` | Use `production-readiness-review` only when the question is launch readiness; use a data, reliability, security, or platform specialist when that surface owns the artifact. |
| The user is changing an exposed contract, compatibility promise, versioning policy, error semantics, pagination, idempotent endpoint behavior, or client migration path. | `api-design-and-compatibility` | Use `large-scale-change-and-service-deprecation` for broad multi-owner migrations or capability sunset; use `event-driven-systems-and-workflows` for asynchronous message contracts. |
| The user needs user-visible reliability objectives, service level indicators, error budgets, paging thresholds, burn-rate policy, or reliability acceptance criteria. | `slo-error-budget-engineering` | Use `observability-and-alerting` when instrumentation or dashboards are the deliverable; use `oncall-health-and-toil-reduction` when reducing page burden is the deliverable. |
| The user needs topology, redundancy, failover, fault-domain, cell, static-stability, or blast-radius design. | `high-availability-design-and-validation` | Use `backup-restore-and-disaster-recovery` when the artifact is restore capability; use `resilience-experiments-and-chaos-engineering` when the artifact is a controlled failure test. |
| The user is designing or fixing remote dependency calls, queues, retries, timeouts, backpressure, circuit breaking, health checks, load shedding, or overload behavior. | `dependency-resilience-and-overload` | Use `capacity-performance-and-tail-latency` when saturation or latency measurement is the main artifact; use `event-driven-systems-and-workflows` when message workflow semantics are central. |
| The user needs latency, throughput, load, saturation, headroom, hot-path, queue-depth, or performance regression analysis. | `capacity-performance-and-tail-latency` | Use `finops-and-cost-aware-reliability` when spend/reliability tradeoff is explicit; use `frontend-performance-release-gates` when client user experience is central. |
| The user needs backups, restore tests, disaster recovery, recovery time/objective evidence, point-in-time recovery, corruption recovery, or regional recovery proof. | `backup-restore-and-disaster-recovery` | Use `high-availability-design-and-validation` for live failover topology without restore semantics; use `incident-response-and-postmortems` first if impact is active. |
| The user needs controlled failure experiments, game days, failover drills, fault injection scope, blast-radius limits, or validation of failure-mode assumptions. | `resilience-experiments-and-chaos-engineering` | Use `high-availability-design-and-validation` when the requested artifact is the topology itself; use `testing-and-quality-gates` for ordinary pre-merge verification. |
| The user needs invariants, state-machine reasoning, model checking, property tests, fuzzing, deterministic simulation, concurrency correctness, protocol correctness, or high-assurance counterexample search. | `systems-correctness-and-formal-validation` | Use `testing-and-quality-gates` for normal CI, static analysis, and release-blocking checks. |
| The user needs telemetry design, dashboards, logs, metrics, traces, alert implementation, runbooks, correlation strategy, or production debugging visibility. | `observability-and-alerting` | Use `slo-error-budget-engineering` when defining objectives or page policy; use `incident-response-and-postmortems` during an active incident. |
| The user needs incident command, severity handling, status cadence, operational communications, timeline reconstruction, postmortem, or follow-up action quality. | `incident-response-and-postmortems` | Use another specialist after the incident only when the user asks for a specific corrective design artifact. |
| The user needs to reduce page volume, alert fatigue, manual operations, toil, runbook gaps, or recurring operational burden. | `oncall-health-and-toil-reduction` | Do not route staffing, compensation, or rotation policy unless reframed as technical page/toil reduction. |
| The user needs merge checks, test strategy, quality gates, static analysis, mutation testing, release-blocking verification, or CI signal design. | `testing-and-quality-gates` | Use `systems-correctness-and-formal-validation` for high-assurance state/protocol validation; use `engineering-productivity-and-code-review` for review workflow latency. |
| The user needs deterministic builds, release branch discipline, release trains, build cache safety, packaging, versioning, artifact promotion, flaky builds, slow builds, or cutting a release artifact. | `release-engineering-and-build-reproducibility` | Use `progressive-delivery-and-safe-change` after the artifact exists and the concern is production exposure. |
| The user needs rollout, rollback, canarying, feature flagging, config-change safety, migration exposure strategy, or production change containment. | `progressive-delivery-and-safe-change` | Use `database-operations-and-schema-changes` when the main hazard is production database execution; use `incident-response-and-postmortems` after a bad deploy causes active impact. |
| The user needs launch readiness, major traffic-shift readiness, tier upgrade review, production ownership evidence, or a broad readiness audit across several surfaces. | `production-readiness-review` | Do not use it for generic architecture review, small changes, or single-domain questions that another skill owns. |
| The user needs a broad migration, service retirement, legacy replacement, deprecation window, caller migration, backsliding prevention, or capability sunset plan. | `large-scale-change-and-service-deprecation` | Use `api-design-and-compatibility` for one exposed contract change; use `dependency-hygiene-and-code-health` for routine cleanup. |
| The user needs review process quality, ownership, change size, review latency, engineering workflow metrics, or developer productivity tied to delivery quality. | `engineering-productivity-and-code-review` | Use `testing-and-quality-gates` when the artifact is merge/release verification rather than review workflow. |
| The user needs dependency updates, lockfile hygiene, package deprecations, code cleanup, refactoring discipline, static-analysis backlog cleanup, codemods, or dead-code removal. | `dependency-hygiene-and-code-health` | Use `software-supply-chain-security` when trust, provenance, signing, builder isolation, or dependency inventory is central. |
| The user needs threat modeling, secure design review, abuse cases, application security requirements, input/output handling, authorization design, or secure SDLC checks. | `secure-sdlc-and-threat-modeling` | Use `zero-trust-identity-and-secrets` when identity, secrets, keys, or encryption owns the artifact; use `llm-application-security` for model/tool/retrieval-specific app risks. |
| The user needs identity, access control, service accounts, workload identity, federation, privileged access, secrets, key management, encryption, or cryptographic control design. | `zero-trust-identity-and-secrets` | Use `secure-sdlc-and-threat-modeling` for broader application security design without identity or secret ownership. |
| The user needs build/deploy trust controls, provenance, dependency inventory, artifact signing, builder isolation, secret scanning, or release integrity. | `software-supply-chain-security` | Use `dependency-hygiene-and-code-health` for routine dependency updates; use `vulnerability-management-and-patch-sla` for deployed vulnerability triage and remediation. |
| The user needs deployed vulnerability triage, exploitability prioritization, patch SLA, remediation exceptions, vulnerable artifact rollout, or time-to-fix measurement. | `vulnerability-management-and-patch-sla` | Use `software-supply-chain-security` when the missing artifact is provenance or inventory rather than remediation. |
| The user needs tenant boundaries, cross-tenant access prevention, noisy-neighbor isolation, tenant quotas, per-tenant blast radius, or multi-tenant data protection. | `tenant-isolation-and-data-protection` | Use `privacy-engineering-and-data-lifecycle` for retention, deletion, minimization, export, or erasure without tenant-boundary concerns. |
| The user needs data minimization, retention, deletion, purpose limitation, consent enforcement as an engineering control, anonymization, pseudonymization, export, erasure, or privacy-safe telemetry. | `privacy-engineering-and-data-lifecycle` | Use `tenant-isolation-and-data-protection` when the primary risk is cross-tenant boundary failure. |
| The user explicitly asks to map engineering standards or controls to repeatable evidence, exception records, scorecards, or multi-surface control artifacts. | `engineering-control-evidence` | Do not use it for broad legal/compliance program work; route single-domain evidence to the specialist that owns the control. |
| The user needs storage choice, replication, transactions, consistency, sharding, migration strategy, hot-key handling, data correctness, or distributed lock design. | `distributed-data-and-consistency` | Use `database-operations-and-schema-changes` for production execution of schema/backfill work; use `caching-and-derived-data` for cache invalidation mechanics. |
| The user needs events, queues, streams, change feeds, transactional outbox, sagas, retries, dead-letter handling, message schema evolution, replay, or workflow orchestration. | `event-driven-systems-and-workflows` | Use `dependency-resilience-and-overload` for synchronous dependency calls and overload controls; use `data-pipeline-reliability` when freshness, lineage, and idempotent reprocessing of data movement own the artifact. |
| The user needs cache mechanics, invalidation, materialized views, derived state, index refresh, freshness enforcement, thundering-herd prevention, or stale-entry operations. | `caching-and-derived-data` | Use `distributed-data-and-consistency` when the question is whether staleness is acceptable at all. |
| The user needs online schema changes, production database migrations, backfills, query-plan regression handling, index changes, lock avoidance, replica safety, compaction, or database maintenance risk. | `database-operations-and-schema-changes` | Use `distributed-data-and-consistency` for abstract storage or consistency design; use `progressive-delivery-and-safe-change` for non-database rollout strategy. |
| The user needs batch or streaming pipeline freshness, correctness, lineage, idempotent reprocessing, missed run handling, data-quality gates, or pipeline service objectives. | `data-pipeline-reliability` | Use `event-driven-systems-and-workflows` when message contracts, replay semantics, or orchestration own the artifact; use `ml-systems-reliability-and-evaluation` when model production is central. |
| The user needs production ML serving, model release gates, model rollback, training pipeline reliability, eval gates, data validation, drift handling, or training-serving skew controls. | `ml-systems-reliability-and-evaluation` | Use `data-pipeline-reliability` for non-ML data movement and freshness. |
| The user needs internal developer platform design, service catalog, golden path, paved road, templates, scorecards, or standardized service creation. | `platform-engineering-and-golden-paths` | Use `infrastructure-gitops-and-policy-as-code` when the artifact is declarative infrastructure enforcement or environment promotion. |
| The user needs declarative infrastructure delivery, admission policy, drift detection, reconciliation, environment promotion, or policy-as-code controls. | `infrastructure-gitops-and-policy-as-code` | Use `platform-engineering-and-golden-paths` for developer experience standards and reusable service creation paths. |
| The user needs public edge traffic defense, denial-of-service resilience, edge caching policy, application-layer filtering, rate limits, bot or abuse throttling, origin protection, global traffic steering, or edge load shedding. | `edge-traffic-and-ddos-defense` | Use `internal-networking-and-service-mesh` for private service-to-service traffic; use `capacity-performance-and-tail-latency` for general headroom analysis. |
| The user needs internal service networking, private service discovery, internal load balancing, east-west traffic policy, authenticated service-to-service transport, locality-aware routing, private connectivity, or cross-region network cost. | `internal-networking-and-service-mesh` | Use `edge-traffic-and-ddos-defense` for public traffic abuse or origin protection. |
| The user needs cost reduction, unit economics, tagging, capacity headroom economics, cost regressions, allocation strategy, or explicit reliability/cost tradeoff. | `finops-and-cost-aware-reliability` | Do not use for pure billing or procurement questions; use `capacity-performance-and-tail-latency` when the request is scale/headroom without cost tradeoff. |
| The user needs LLM application security, prompt injection defenses, tool permission boundaries, retrieval data boundaries, unsafe model-output handling, eval regression gates, or prompt/model supply-chain controls. | `llm-application-security` | Use `secure-sdlc-and-threat-modeling` for general application security; do not route broad AI strategy here. |
| The user needs native mobile release trains, staged rollout, crash-free user budgets, hang-rate handling, startup regression gates, offline behavior, app-store release risk, or mobile telemetry. | `mobile-release-engineering-and-crash-budgets` | Use `frontend-performance-release-gates` for browser-delivered or client-rendered web changes. |
| The user needs browser-delivered or client-rendered release gates for user-perceived loading, interaction readiness, visual stability, runtime errors, payload weight, client telemetry, or accessibility smoke checks. | `frontend-performance-release-gates` | Use `capacity-performance-and-tail-latency` for backend latency/headroom; do not hardcode a specific metric family or framework as the route. |

## Red Flags - Stop And Rework

- More than two skills are selected automatically.
- The router chooses from a phrase match without identifying the requested deliverable and phase.
- A tool or vendor name drives routing without translating the underlying engineering capability.
- `production-readiness-review` is used for any broad prompt even when no launch/readiness event exists.
- Compliance, staffing, compensation, procurement, or marketing work is routed as if it were engineering work.
- The router repeats detailed specialist guidance instead of selecting the skill.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Keyword matching | Infer surface, event, risk, and scope. |
| Loading every related skill | Choose one primary and list follow-up only when needed. |
| Treating tools as domains | Translate tools to capabilities. |
| Avoiding clarification | Ask one focused question when confidence is low. |
