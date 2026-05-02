---
name: internal-networking-and-service-mesh
description: "Use when the user clearly describes internal service-to-service networking, service mesh, internal load balancing, service discovery, internal routing, east-west traffic policy, authenticated service-to-service transport, locality-aware routing, private network connectivity, or cross-region network cost. Do not use for vague network issues until the affected path is known."
---

# Internal Networking And Service Mesh

## Overview

Internal networking should solve concrete traffic, identity, policy, and observability problems; mesh is not a default.

**Core principle:** choose the simplest internal networking model that provides required routing, identity, reliability, observability, and operations guarantees.

## Iron Law

```
NO SERVICE MESH OR ROUTING LAYER WITHOUT A SPECIFIC PROBLEM, OWNER, FAILURE MODEL, AND OPERATIONS PLAN
```

If the platform cannot debug and upgrade it, it should not sit in every request path.

## When To Use

- The user clearly describes internal service networking, service mesh, internal load balancing, service discovery, east-west traffic policy, authenticated service-to-service transport, locality-aware routing, or cross-region network cost.
- Services need consistent traffic policy, identity, telemetry, routing, or authorization at the platform layer.
- Internal routing or failover behavior affects reliability, latency, blast radius, or cost.
- The user asks whether adopting a service mesh is justified.
- The affected path is known to be internal service-to-service or private network traffic.

## When Not To Use

- The request is public edge abuse or denial-of-service defense; use edge traffic defense.
- The request is a vague network issue without a known affected path, surface, or symptom; use the router first.
- The issue is per-call retry/timeout/backpressure policy without networking architecture; use dependency resilience.
- The main topic is API contract design; use API compatibility.
- The work is broad identity/secrets beyond network identity; use zero-trust identity.

## Inputs To Collect

- Service topology, traffic flows, protocols, regions/zones/cells, dependencies, and ownership.
- Concrete problem: service identity, encrypted transport, authorization, traffic splitting, locality, failover, observability, policy, or debugging.
- Current service discovery, load balancing, DNS/routing, ingress/egress, and network boundaries.
- Latency, cross-region egress, failure domains, retry behavior, and dependency resilience policies.
- Platform maturity: upgrade process, sidecar/proxy/data-plane operations, incident history, and support model.
- Telemetry needs: route, upstream/downstream identity, locality, retries, connection errors, and request context.

## Workflow

1. **Name the problem.** Do not propose mesh until the repeated capability gap is explicit.
2. **Map traffic.** Identify internal routes, dependencies, regions, failover paths, identity boundaries, and policy points.
3. **Compare no-mesh alternatives.** Consider library, gateway, platform, or simple load-balancer capabilities before adding a mesh-wide data plane.
4. **Define routing policy.** Include locality, failover, traffic splitting, retries, timeouts, and circuit behavior ownership.
5. **Define identity and policy.** State how workload identity, authenticated encrypted transport, authorization, and audit work.
6. **Model failure and upgrades.** Include proxy/control-plane failure, config error, upgrade rollout, and debug burden.
7. **Instrument paths.** Capture request IDs, route metadata, identity, upstream locality, retries, errors, and latency.
8. **Plan adoption.** Roll out by service, cell, or environment; keep rollback and exception path.

## Synthesized Default

Do not add service mesh by default. Adopt a mesh or equivalent platform traffic layer only when repeated cross-service needs justify its operational cost: identity, encrypted transport, traffic policy, telemetry, authorization, routing, or locality.

## Exceptions

- Small systems may use simple internal load balancing and library conventions.
- High-security or multi-tenant platforms may justify centralized identity and traffic policy earlier.
- Cross-region systems may prefer explicit regional boundaries and locality rules over opaque global routing.
- Emergency network changes need audit, rollback, and post-change reconciliation.

## Response Quality Bar

- Lead with the mesh/no-mesh decision, routing policy, identity model, or failure-mode blocker requested.
- Cover concrete repeated needs, traffic map, routing/locality/failover, identity/encrypted transport/authorization, retry ownership, telemetry, upgrades, rollback, and cost/latency tradeoffs before optional mesh breadth.
- Make recommendations actionable with owners, policy locations, rollout stages, config checks, failure tests, rollback steps, and operational runbooks where relevant.
- State required evidence such as dependency maps, route config, retry/timeout settings, control-plane health, proxy versions, identity claims, latency/egress data, and incident history; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside internal traffic and service mesh decisions. Route dependency resilience or zero-trust work only when it materially changes the mesh decision.
- Be concise: avoid generic mesh advocacy and prefer compact decision records and routing matrices.

## Required Outputs

- Internal traffic and dependency map.
- Mesh/no-mesh decision record with alternatives.
- Routing, locality, failover, and traffic-splitting policy.
- Workload identity, encrypted transport, and authorization model.
- Operations, upgrade, ownership, and rollback plan.
- Network telemetry and debugging requirements.
- Cost and latency tradeoff notes for cross-boundary traffic.

## Evidence Gates

- `problem_check`: mesh or routing layer adoption maps to concrete repeated needs.
- `failure_model`: data-plane, control-plane, config, and upgrade failure modes are addressed.
- `ownership_check`: platform ownership for debugging, upgrades, and incident response is explicit.
- `routing_policy`: locality, failover, traffic split, and retry/timeout ownership are defined.
- `telemetry_check`: route, identity, locality, retry, latency, and error metadata are observable.

## Red Flags - Stop And Rework

- Mesh is selected because it is fashionable.
- No one owns proxy upgrades or data-plane incidents.
- Routing retries conflict with application retry budgets.
- Cross-region routing hides latency and egress cost.
- Identity is claimed but not tied to authorization or audit.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Mesh first | Start with the capability gap and simpler options. |
| Hidden retries | Align network retries with application retry budgets. |
| No upgrade plan | Treat data-plane upgrades as production releases. |
| Blind global routing | Make locality, failover, and cost explicit. |
