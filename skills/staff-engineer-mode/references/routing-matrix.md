# Routing Matrix Notes

The router skill body must stay compact enough for Codex and Claude to load without warning. Keep detailed boundary notes here, and load this file only when adjacent surfaces compete.

This file records the highest-risk routing boundaries to preserve during future edits. Do not duplicate every skill description here; duplication creates drift.

## Decision Frame

1. Identify the requested artifact: decision, plan, gate, rollout, investigation, runbook, policy, migration, evidence pack, or review.
2. Identify the work phase: design, pre-merge, launch, migration, active incident, post-incident, regression, audit, or steady-state maintenance.
3. Identify the dominant risk: availability, latency, durability, correctness, security, privacy, compatibility, operator load, cost, release safety, or customer experience.
4. Route to one primary. Add a secondary only when the user explicitly asks for a separate artifact.
5. Ask only the missing intake questions when the artifact or phase is unclear. Do not expose skill names, confidence labels, candidate lists, or routing drafts while asking.

## High-Risk Boundaries

- Reliability target policy routes to `slo-and-error-budgets`; telemetry construction routes to `observability-and-alerting`; page fatigue routes to `oncall-health`.
- When a prompt mixes noisy pages and missing reliability targets, route the immediate operator pain to `oncall-health` and use `slo-and-error-budgets` only as a secondary policy artifact.
- Launch readiness routes to `production-readiness-review` only when launch, major traffic shift, tier upgrade, or broad readiness audit is explicit. Generic design review routes elsewhere.
- Fault-domain topology routes to `high-availability-design`; restore capability routes to `backup-and-recovery`; controlled failure tests route to `resilience-experiments`.
- Build and artifact creation route to `release-build-reproducibility`; production exposure and rollback route to `progressive-delivery`.
- Config, feature settings, generated operations, and automation mutation route to `configuration-and-automation-safety`; production exposure still routes to `progressive-delivery`.
- Engineering docs route to `documentation-lifecycle` only when ownership, source of truth, freshness, operational accuracy, lifecycle gates, or stale/missing guidance are the artifact. Routine editorial or mechanical documentation maintenance should be handled directly without a Staff Engineer Mode specialist. Architecture decisions still route to `architecture-decisions`.
- Normal merge/release checks route to `testing-and-quality-gates`; protocol, state-machine, or concurrency assurance routes to `state-machine-correctness`.
- Accessibility conformance for user-facing flows routes to `accessibility-gates`; client performance still routes to `web-release-gates` or `mobile-release-engineering`.
- Broad migrations, legacy retirement, and capability sunset route to `migration-and-deprecation`; routine cleanup routes to `dependency-and-code-hygiene`; exposed contract compatibility routes to `api-design-and-compatibility`.
- Fleet upgrades, support windows, and mixed-version rollout route to `fleet-upgrades`; routine package updates stay with `dependency-and-code-hygiene`.
- Supply-chain trust controls route to `software-supply-chain-security`; deployed vulnerability remediation routes to `vulnerability-management`; routine dependency updates route to `dependency-and-code-hygiene`.
- Pre-deploy abuse-case and control reasoning routes to `secure-sdlc-and-threat-modeling`; already-deployed vulnerable code routes to `vulnerability-management`; trust in the build path routes to `software-supply-chain-security`.
- Cryptographic agility, certificate expiry, key rotation, and trust-chain lifecycle route to `cryptography-and-key-lifecycle`; runtime access and secrets policy stays with `identity-and-secrets`.
- Post-rollout feature-flag inventory, owners, expiry, removal plans, and orphan flag debt route to `feature-flag-lifecycle`; introducing the flag during rollout stays with `progressive-delivery`; generic dead-code cleanup stays with `dependency-and-code-hygiene`.
- Per-route LLM token budgets, tail-latency budgets, prompt and response caches, provider-failure degradation paths, and per-feature LLM cost attribution route to `llm-serving-cost-and-latency`; generic backend latency and capacity stays with `performance-and-capacity`; generic spend/reliability tradeoffs stay with `cost-aware-reliability`; generic remote-call retries, timeouts, and circuit breakers stay with `dependency-resilience`.
- Repository legibility for AI comprehension, module-boundary maps, code-search-collision audits, function and file-size budgets, and one-tool-call locatability route to `code-readability-for-agents`; macro service boundaries stay with `architecture-decisions`; per-diff agent pre-merge review stays with `agent-pr-review`.
- Fixture inventory, anonymization of production-derived test data, fixture freshness-versus-determinism choices, and production/test data drift route to `test-data-engineering`; overall test strategy, CI gates, and merge-blocking checks stay with `testing-and-quality-gates`.
- Local, CI, staging, and production parity matrices, drift budgets, allowed-versus-required divergence, and "works only in one environment" failures route to `dev-environment-parity`; reproducible release artifacts and build-once/promote-many remain with `release-build-reproducibility`.
- Data pipeline freshness, lineage, and idempotent reprocessing route to `data-pipeline-reliability`; message contracts, replay semantics, and workflow orchestration route to `event-workflows`.
- Cross-surface data contracts, producer/consumer schema evolution, and domain-interface ownership route to `data-contracts`; single API contract changes stay with `api-design-and-compatibility`.
- Cache invalidation, derived values, and stale cache entries route to `caching-and-derived-data`; deciding whether stale reads are allowed by the storage model routes to `distributed-data-and-consistency`.
- AI-assisted repo workflow, agent instructions, data boundaries, and generated-code acceptance route to `ai-coding-governance`; deployed LLM app security stays with `llm-application-security`.
- A specific agent-produced diff that needs a senior pre-merge review routes to `agent-pr-review`; org-level AI policy still routes to `ai-coding-governance`; reviewer routing, ownership, change size, and DORA workflow stay with `code-review-and-workflow`; explicit launch readiness still routes to `production-readiness-review`; an active incident still routes to `incident-response-and-postmortems` first.
- LLM tool, prompt-injection, retrieval-boundary, and unsafe-output risk routes to `llm-application-security`; LLM eval datasets, graders, thresholds, and regression gates route to `llm-evaluation`; production ML serving and drift stay with `ml-reliability-and-evaluation`.
- Experiments, holdouts, exposure logging, and metric validity route to `experimentation-and-metric-guardrails`; operational canaries stay with `progressive-delivery`.
- Single-surface evidence stays with the surface owner. `engineering-control-evidence` is for cross-surface control mapping, exception records, scorecards, and evidence packs.
- Public edge traffic defense routes to `edge-traffic-and-ddos-defense`; internal service-to-service traffic policy routes to `internal-service-networking`.
- Retry, timeout, circuit-breaker, load-shedding, and dependency overload policy routes to `dependency-resilience` even when implemented through internal traffic tooling; service identity, discovery, transport, and locality route to `internal-service-networking`.
- Client-rendered user experience performance gates route to `web-release-gates`; backend latency and headroom route to `performance-and-capacity`.
- Headroom and latency without spend tradeoffs route to `performance-and-capacity`; cost, spend, allocation, or reliability/cost tradeoffs route to `cost-aware-reliability`; pure billing work is out of scope.

## Scope

Product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, and broad compliance-program work are out of scope unless reframed as concrete engineering controls.
