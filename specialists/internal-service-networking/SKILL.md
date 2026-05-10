---
name: internal-service-networking
description: "Use when internal service traffic needs discovery, routing, locality, identity, encrypted transport, or private access"
---

# Internal Networking And Service Mesh

## Iron Law

```
NO INTERNAL SERVICE PATH WITHOUT IDENTITY, FAILURE MODE, OBSERVABILITY, AND AN OPERATIONS PLAN FOR EVERY HOP
```

Every hop on a service-to-service path needs a workload identity, a documented failure mode, telemetry that explains what happened, and a runnable debugging and upgrade path. "We added a mesh" or "we use DNS" is not an answer to any of those four. For a solo or two-service deployment the rule still applies at a smaller scale.

> This skill assumes a multi-service deployment. A single-process app does not have internal service hops; route to `dependency-resilience` for remote-call policy or `architecture-decisions` if the question is whether to split.

## Overview

Internal networking should solve concrete traffic, identity, policy, and observability problems; mesh is not a default.

**Core principle:** choose the simplest internal networking model that provides required routing, identity, reliability, observability, and operations guarantees.

## When To Use

- The user clearly describes internal service networking, service mesh, internal load balancing, service discovery, east-west traffic policy, authenticated service-to-service transport, locality-aware routing, or cross-location network cost.
- Services need consistent traffic policy, identity, telemetry, routing, or authorization at the platform layer.
- Internal routing or failover behavior affects reliability, latency, blast radius, or cost.
- The user asks whether adopting a service mesh is justified.
- The affected path is known to be internal service-to-service or private network traffic.

## When Not To Use

- The request is public edge abuse or denial-of-service defense; use `edge-traffic-and-ddos-defense` instead.
- The request is a vague network issue without a known affected path, surface, or symptom; use the router first.
- The issue is per-call retry/timeout/backpressure policy without networking architecture; use `dependency-resilience` instead.
- The main topic is API contract design; use `api-design-and-compatibility` instead.
- The work is broad identity/secrets beyond network identity; use `identity-and-secrets` instead.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Service topology, traffic flows, protocols, locations, fault domains, partitions, dependencies, and responsibility.
- Concrete problem: service identity, encrypted transport, authorization, traffic splitting, locality, failover, observability, policy, or debugging.
- Current service discovery, load balancing, DNS/routing, ingress/egress, and network boundaries.
- Latency, cross-location egress, failure domains, retry behavior, and dependency resilience policies.
- Platform maturity: upgrade process, sidecar/proxy/data-plane operations, incident history, and local diagnostic path.
- Telemetry needs: route, upstream/downstream identity, locality, retries, connection errors, and request context.

## Workflow

1. **Name the problem.** Do not propose mesh until the repeated capability gap is explicit.
2. **Map traffic.** Identify internal routes, dependencies, locations, failover paths, identity boundaries, and policy points.
3. **Compare no-mesh alternatives.** Consider library, gateway, platform, or simple load-balancer capabilities before adding a mesh-wide data plane.
4. **Define routing policy.** Include locality, failover, traffic splitting, retries, timeouts, and circuit behavior responsibility.
5. **Define identity and policy.** State how workload identity, authenticated encrypted transport, authorization, and audit work.
6. **Model failure and upgrades.** Include proxy/control-plane failure, config error, upgrade rollout, and debug burden.
7. **Instrument paths.** Capture request IDs, route metadata, identity, upstream locality, retries, errors, and latency.
8. **Plan adoption.** Roll out by service, partition, or environment; keep rollback and exception path.

## Synthesized Default

Do not add service mesh by default. Adopt a mesh or equivalent platform traffic layer only when repeated cross-service needs justify its operational cost: identity, encrypted transport, traffic policy, telemetry, authorization, routing, or locality.



## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, gates, and evidence to collect.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness evidence.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Review: evaluate an existing diff, design, runbook, evidence, or system behavior as one mode.
- Missing evidence: state assumptions and produce the evidence plan instead of blocking lifecycle guidance.

## Exceptions

- Small systems may use simple internal load balancing and library conventions.
- High-security or multi-tenant platforms may justify centralized identity and traffic policy earlier.
- Cross-location systems may prefer explicit location boundaries and locality rules over opaque global routing.
- Emergency network changes need audit, rollback, and post-change reconciliation.

## Response Quality Bar

- Lead with the mesh/no-mesh decision, routing policy, identity model, or failure-mode blocker requested.
- For quick design-review or troubleshooting answers, still include one compact per-edge baseline: `<caller> -> <callee>` discovery/routing mechanism and stale/unavailable behavior; service-to-service authentication mechanism and scope, such as mutual-authentication transport workload identity, mesh identity, or a signed service token for that edge; per-request authorization decision criteria, such as caller identity plus method/resource/action; default-deny service policy with user-confirmed exception rule; RED metrics (request rate, error rate, latency) with dashboard and alert; and runnable debug command or procedure.
- Cover concrete repeated needs, traffic map, routing/locality/failover, identity/encrypted transport/authorization, retry responsibility, telemetry, upgrades, rollback, and cost/latency tradeoffs before optional mesh breadth.
- Make recommendations actionable with policy locations, rollout stages, config checks, failure tests, rollback steps, and operational runbooks where relevant.
- State required evidence such as dependency maps, route config, retry/timeout settings, control-plane health, proxy versions, identity claims, latency/egress data, and incident history; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside internal traffic and service mesh decisions. Route dependency resilience or zero-trust work only when it materially changes the mesh decision.
- Be concise: avoid generic mesh advocacy and prefer compact decision records and routing matrices.

## Required Outputs

- Internal traffic and dependency map.
- Mesh/no-mesh decision record with alternatives.
- Routing, locality, failover, and traffic-splitting policy.
- Workload identity, encrypted transport, and authorization model.
- Operations, upgrade, diagnostics, and rollback plan.
- Network telemetry and debugging requirements.
- Cost and latency tradeoff notes for cross-boundary traffic.

## Evidence Gates

- `problem_check`: mesh or routing layer adoption maps to concrete repeated needs.
- `failure_model`: data-plane, control-plane, config, and upgrade failure modes are addressed.
- `diagnostic_check`: debugging, upgrade, and incident-response paths are explicit and runnable or marked unknown.
- `routing_policy`: locality, failover, traffic split, and retry/timeout responsibility are defined.
- `telemetry_check`: route, identity, locality, retry, latency, and error metadata are observable.

## Red Flags - Stop And Rework

- Mesh is selected because it is fashionable.
- Proxy upgrades or data-plane incidents have no runnable diagnostic or rollback path.
- Routing retries conflict with application retry budgets.
- Cross-location routing hides latency and egress cost.
- Identity is claimed but not tied to authorization or audit.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Mesh first | Start with the capability gap and simpler options. |
| Hidden retries | Align network retries with application retry budgets. |
| No upgrade plan | Treat data-plane upgrades as production releases. |
| Blind global routing | Make locality, failover, and cost explicit. |
