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

- Reliability target policy routes to `slo-error-budget-engineering`; telemetry construction routes to `observability-and-alerting`; page fatigue routes to `oncall-health-and-toil-reduction`.
- When a prompt mixes noisy pages and missing reliability targets, route the immediate operator pain to `oncall-health-and-toil-reduction` and use `slo-error-budget-engineering` only as a secondary policy artifact.
- Launch readiness routes to `production-readiness-review` only when launch, major traffic shift, tier upgrade, or broad readiness audit is explicit. Generic design review routes elsewhere.
- Fault-domain topology routes to `high-availability-design-and-validation`; restore capability routes to `backup-restore-and-disaster-recovery`; controlled failure tests route to `resilience-experiments-and-chaos-engineering`.
- Build and artifact creation route to `release-build-reproducibility`; production exposure and rollback route to `progressive-delivery-and-safe-change`.
- Config, feature settings, generated operations, and automation mutation route to `configuration-and-automation-safety`; production exposure still routes to `progressive-delivery-and-safe-change`.
- Engineering docs, runbooks, design docs, and freshness/source-of-truth work route to `engineering-documentation-lifecycle`; architecture decisions still route to `architecture-review-and-decision-records`.
- Normal merge/release checks route to `testing-and-quality-gates`; protocol, state-machine, or concurrency assurance routes to `systems-correctness-and-formal-validation`.
- Accessibility conformance for user-facing flows routes to `accessibility-conformance-gates`; client performance still routes to `frontend-performance-release-gates` or `mobile-release-engineering-and-crash-budgets`.
- Broad migrations, legacy retirement, and capability sunset route to `large-scale-change-and-service-deprecation`; routine cleanup routes to `dependency-hygiene-and-code-health`; exposed contract compatibility routes to `api-design-and-compatibility`.
- Fleet upgrades, support windows, and mixed-version rollout route to `fleet-upgrades-and-version-skew-management`; routine package updates stay with `dependency-hygiene-and-code-health`.
- Supply-chain trust controls route to `software-supply-chain-security`; deployed vulnerability remediation routes to `vulnerability-management-and-patch-sla`; routine dependency updates route to `dependency-hygiene-and-code-health`.
- Pre-deploy abuse-case and control reasoning routes to `secure-sdlc-and-threat-modeling`; already-deployed vulnerable code routes to `vulnerability-management-and-patch-sla`; trust in the build path routes to `software-supply-chain-security`.
- Cryptographic agility, certificate expiry, key rotation, and trust-chain lifecycle route to `crypto-agility-and-cert-lifecycle`; runtime access and secrets policy stays with `zero-trust-identity-and-secrets`.
- Data pipeline freshness, lineage, and idempotent reprocessing route to `data-pipeline-reliability`; message contracts, replay semantics, and workflow orchestration route to `event-driven-systems-and-workflows`.
- Cross-surface data contracts, producer/consumer schema evolution, and domain-interface ownership route to `data-contracts-and-domain-interfaces`; single API contract changes stay with `api-design-and-compatibility`.
- Cache invalidation, derived values, and stale cache entries route to `caching-and-derived-data`; deciding whether stale reads are allowed by the storage model routes to `distributed-data-and-consistency`.
- AI-assisted repo workflow, agent instructions, data boundaries, and generated-code acceptance route to `ai-assisted-coding-governance`; deployed LLM app security stays with `llm-application-security`.
- LLM tool, prompt-injection, retrieval-boundary, and unsafe-output risk routes to `llm-application-security`; LLM eval datasets, graders, thresholds, and regression gates route to `llm-evaluation-harness-engineering`; production ML serving and drift stay with `ml-systems-reliability-and-evaluation`.
- Experiments, holdouts, exposure logging, and metric validity route to `experimentation-and-metric-guardrails`; operational canaries stay with `progressive-delivery-and-safe-change`.
- Single-surface evidence stays with the surface owner. `engineering-control-evidence` is for cross-surface control mapping, exception records, scorecards, and evidence packs.
- Public edge traffic defense routes to `edge-traffic-and-ddos-defense`; internal service-to-service traffic policy routes to `internal-networking-and-service-mesh`.
- Retry, timeout, circuit-breaker, load-shedding, and dependency overload policy routes to `dependency-resilience-and-overload` even when implemented through internal traffic tooling; service identity, discovery, transport, and locality route to `internal-networking-and-service-mesh`.
- Client-rendered user experience performance gates route to `frontend-performance-release-gates`; backend latency and headroom route to `capacity-performance-and-tail-latency`.
- Headroom and latency without spend tradeoffs route to `capacity-performance-and-tail-latency`; cost, spend, allocation, or reliability/cost tradeoffs route to `finops-and-cost-aware-reliability`; pure billing work is out of scope.

## Scope

Product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, and broad compliance-program work are out of scope unless reframed as concrete engineering controls.
