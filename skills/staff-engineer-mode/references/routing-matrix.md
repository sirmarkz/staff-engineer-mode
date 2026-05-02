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
- Launch readiness routes to `production-readiness-review` only when launch, major traffic shift, tier upgrade, or broad readiness audit is explicit. Generic design review routes elsewhere.
- Fault-domain topology routes to `high-availability-design-and-validation`; restore capability routes to `backup-restore-and-disaster-recovery`; controlled failure tests route to `resilience-experiments-and-chaos-engineering`.
- Build and artifact creation route to `release-build-reproducibility`; production exposure and rollback route to `progressive-delivery-and-safe-change`.
- Normal merge/release checks route to `testing-and-quality-gates`; protocol, state-machine, or concurrency assurance routes to `systems-correctness-and-formal-validation`.
- Broad migrations, legacy retirement, and capability sunset route to `large-scale-change-and-service-deprecation`; routine cleanup routes to `dependency-hygiene-and-code-health`; exposed contract compatibility routes to `api-design-and-compatibility`.
- Supply-chain trust controls route to `software-supply-chain-security`; deployed vulnerability remediation routes to `vulnerability-management-and-patch-sla`; routine dependency updates route to `dependency-hygiene-and-code-health`.
- Data pipeline freshness, lineage, and idempotent reprocessing route to `data-pipeline-reliability`; message contracts, replay semantics, and workflow orchestration route to `event-driven-systems-and-workflows`.
- Single-surface evidence stays with the surface owner. `engineering-control-evidence` is for cross-surface control mapping, exception records, scorecards, and evidence packs.
- Public edge traffic defense routes to `edge-traffic-and-ddos-defense`; internal service-to-service traffic policy routes to `internal-networking-and-service-mesh`.
- Client-rendered user experience performance gates route to `frontend-performance-release-gates`; backend latency and headroom route to `capacity-performance-and-tail-latency`.
- Cost reduction routes to `finops-and-cost-aware-reliability` only when cost, spend, allocation, or reliability/cost tradeoff is explicit.

## Scope

Product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, and broad compliance-program work are out of scope unless reframed as concrete engineering controls.
