---
name: high-availability-design
description: "Use to claim or validate that a system survives zone, region, cell, shard, or dependency loss — fault domains, static capacity, blast radius, and failover behavior."
---

# High Availability Design And Validation

## Iron Law

```
NO HA CLAIM WITHOUT A FAULT DOMAIN, SURVIVABILITY TARGET, CAPACITY MODEL, AND TEST PLAN
```

"Multi-region", "multi-zone", and "redundant" are labels. They are not evidence.

## Overview

High availability is the ability to keep serving through expected failures without inventing new operations during the failure.

**Core principle:** identify fault domains, bound blast radius, provision enough steady-state capacity, and validate the failure mode before relying on it.

## When To Use

- The user asks whether a system can survive zone, region, cell, host, shard, tenant, or dependency loss.
- A design claims active-active, active-passive, cell-based, shuffle-sharded, or multi-region availability.
- A launch or PRR needs HA evidence.
- The work changes topology, failover, load balancing, placement, or blast radius.

## When Not To Use

- The main question is per-call retries, timeouts, backpressure, or circuit breaking; defer to `dependency-resilience`.
- The main question is restoring corrupted or lost data; defer to `backup-and-recovery`.
- The main question is planning a chaos experiment, game day, or fault injection drill; defer to `resilience-experiments`.
- The work is only unit, integration, or CI testing.
- The request is about generic uptime targets; define SLOs first via `slo-and-error-budgets`.

## Inputs To Collect

- Service tier, SLOs, critical user journeys, and maximum tolerable interruption.
- Current topology: hosts, zones, regions, cells, shards, queues, load balancers, stores, and control planes.
- Fault domains: process, node, rack, zone, region, administrative boundary, cluster, deployment ring, tenant, data partition, dependency, and operator action.
- Capacity by domain, peak traffic, failover headroom, and dependency quotas.
- Data replication model, consistency needs, and any hidden global dependencies.
- Existing failover tests, incidents, game days, chaos experiments, and rollback procedures.

## Workflow

1. **State the survival claim.** Use the form: "survive loss of X while continuing Y, with no manual Z, within SLO W."
2. **Draw the fault-domain map.** Include serving path, data path, control plane, deployment system, identity, config, DNS, observability, and operator access.
3. **Check static stability.** Confirm remaining domains already have enough capacity and quotas during the failure. Do not count emergency scaling that depends on the failed domain.
4. **Choose topology deliberately.** Decide whether a zonal, zone-redundant, multi-zone, multi-region, active-passive, active-active, or stamp/cell model is justified by the survival claim.
5. **Bound blast radius.** Use cells, stamps, shards, shuffle sharding, tenant isolation, or regional boundaries when one failure could otherwise affect the whole fleet.
6. **Remove hidden coupling.** Find global locks, shared queues, shared caches, control-plane calls, cross-region synchronous writes, and central config dependencies in the serving path.
7. **Define failover behavior.** Specify automatic/manual trigger, traffic drain, data consistency, split-brain prevention, client behavior, and rollback to normal.
8. **Validate safely.** Define the validation objective, then route detailed fault-injection or game-day planning to resilience experiments when that is the main work.

## Synthesized Default

Use static stability and explicit fault-domain isolation as the default. Prefer designs that continue in steady state after a domain loss over designs that require emergency scaling, global control-plane calls, or complex operator choreography. Add cells, stamps, or shuffle sharding when tenant, shard, or workload blast radius is the real risk.

## Exceptions

- Active-active multi-region is justified only when serving requirements exceed the complexity cost and data semantics can tolerate the replication model.
- Active-passive, warm standby, or pilot light may be better when RTO/RPO and operational maturity are the true constraints.
- Some internal or low-tier services can document a lower survival target if the SLO and owner accept it.
- Chaos experiments must be scoped down or simulated when blast radius cannot be ethically bounded.

## Response Quality Bar

- Lead with the availability decision, survivability claim, fault-domain gap, or validation plan requested.
- Cover serving paths, fault domains, static capacity, blast radius, hidden dependencies, failover behavior, data semantics, and validation before optional HA breadth.
- Make recommendations actionable with owners, survival targets, capacity calculations, trigger/authority rules, abort criteria, and validation evidence where relevant.
- State required evidence such as topology, traffic split, quotas, shared dependencies, failover drills, capacity under loss, replication behavior, and SLO/RTO/RPO targets; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside HA design and validation. Route backup/restore, chaos execution, or distributed consistency only when they are central to the decision.
- Be concise: avoid generic active-active discussion and prefer compact fault-domain maps and survivability tables.

## Required Outputs

- Fault-domain inventory and serving-path map.
- Survivability statement using "survive loss of X while continuing Y".
- Capacity and quota model under normal, peak, and failed-domain conditions.
- Blast-radius analysis and cell/shard/tenant isolation recommendation.
- Hidden dependency and control-plane risk list.
- Failover decision record with trigger, authority, data behavior, and rollback.
- Validation plan with scope, abort criteria, telemetry, and evidence to capture.

## Evidence Gates

- `fault_domain_map`: expected failure domains and hidden shared dependencies are enumerated.
- `static_capacity`: remaining domains can serve target traffic after the claimed failure without emergency scaling.
- `blast_radius_bound`: a single fault cannot exceed the documented cell, tenant, shard, or regional impact boundary.
- `failover_behavior`: trigger, authority, data consistency, traffic behavior, and rollback are written down.
- `validation_plan`: failover, game day, or chaos test has scope, abort criteria, telemetry, and owner.

## Red Flags - Stop And Rework

- "We run in two zones" is treated as proof of zone resilience.
- Failover depends on humans discovering the issue and manually changing many systems under pressure.
- Remaining capacity after failure is assumed but not calculated.
- Critical serving calls depend synchronously on a global control plane, config service, or cross-region dependency.
- Chaos testing is proposed without blast-radius limits or abort criteria.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Confusing HA with DR | HA keeps serving through expected faults; DR restores after loss or corruption. |
| Counting autoscaling as static capacity | Model capacity already available when the domain fails. |
| Testing only the happy failover path | Test detection, partial failure, rollback, and return-to-normal. |
| Ignoring operator dependencies | Include identity, access, dashboards, deploy, and config systems in the map. |
