---
name: distributed-data-and-consistency
description: "Use when storage, replication, transactions, consistency, sharding, hot keys, or distributed locks are central."
---

# Distributed Data And Consistency

## Overview

Data architecture starts with semantics, not storage brands.

**Core principle:** choose storage, replication, transactions, consistency, and sharding from the correctness guarantees each operation actually needs.

## Iron Law

```
NO DATA DESIGN WITHOUT OPERATION-LEVEL CONSISTENCY AND FAILURE SEMANTICS
```

If reads, writes, conflicts, retries, failover, and repair behavior are undefined, the data design is incomplete.

## When To Use

- The user asks about storage choice, replication, consistency, transactions, sharding, hot keys, data correctness, distributed locks, or data ownership.
- A service boundary changes who owns or mutates data.
- The design needs to choose between strong, eventual, read-your-writes, monotonic, causal, or quorum-style behavior.
- The user asks whether stale reads, duplicate writes, or conflicts are acceptable.

## When Not To Use

- The request is only cache TTL, invalidation, stampede, or materialized-view operation; use caching.
- The question is online schema/backfill execution; use database operations.
- The work is service event choreography; use event-driven systems.
- The request is warehouse/ETL freshness rather than application data correctness; use data pipeline reliability.

## Inputs To Collect

- Data classes: money, authz, user settings, content, cache, derived state, analytics, notifications, audit, or ML features.
- Operations: create, update, delete, read, list, search, reconcile, compensate, and repair.
- Correctness expectations: uniqueness, ordering, freshness, read-your-writes, conflict handling, idempotency, and durability.
- Access patterns, read/write volume, fanout, hot keys, tenant/shard routing, and growth forecast.
- Failure modes: partial writes, failover, replication lag, split brain, retries, duplicate leaders, and operator repair.
- Migration constraints, ownership, auditability, and backup/restore requirements.

## Workflow

1. **Classify data by consequence.** Financial, authorization, privacy, and audit data usually need stronger guarantees than analytics or derived views.
2. **Write operation semantics.** For each critical operation, define allowed staleness, conflict behavior, idempotency, and durability.
3. **Choose consistency deliberately.** Use the weakest guarantee that preserves correctness and user expectation; document the tradeoff.
4. **Avoid cross-service transactions.** Prefer local transactions plus outbox, sagas, reconciliation, or compensating actions over distributed two-phase commit.
5. **Plan partitioning early.** Choose shard/tenant keys, hot-key mitigations, locality needs, shard-map ownership, resharding path, and ownership boundaries.
6. **Treat locks and leaders as dangerous.** Use proven coordination primitives when necessary, and design work to be idempotent under duplicate execution.
7. **Define repair and verification.** Include reconciliation jobs, invariants, audit trails, and manual repair safety.
8. **Route operational changes.** Schema/backfill execution goes to database operations; cache mechanics go to caching.

## Synthesized Default

Default to the simplest storage and consistency model that satisfies operation semantics. Keep data ownership local where possible, co-locate data that must transact together, use idempotency and durable state transitions, and avoid custom distributed coordination. When weaker consistency is chosen, state exactly what users may observe and how repair works.

## Exceptions

- Financial, authorization, inventory, and destructive operations may require strong consistency or formal modeling.
- High-scale read paths may accept stale or derived reads when user impact and repair are explicit.
- Multi-step workflows across owners should use sagas or reconciliation rather than pretending one atomic transaction exists.
- Distributed locks are acceptable only with a proven primitive, lease semantics, fencing or idempotency, and failure tests.

## Response Quality Bar

- Lead with the consistency decision, tradeoff, or unresolved blocker.
- Cover data semantics, stale-read impact, conflicts, failure behavior, and operational cost before optional distributed-systems breadth.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and validation criteria where relevant.
- State required evidence such as invariants, latency budgets, conflict rates, replication behavior, and failure assumptions; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside the data consistency decision. Mention caches, workflows, or schema execution only when they materially change semantics.
- Be concise: avoid generic CAP/PACELC exposition and prefer decision matrices.

## Required Outputs

- Data classification table.
- Operation-level consistency matrix.
- Storage decision record with rejected alternatives.
- Replication, failover, and conflict-resolution model.
- Sharding/hot-key/tenant-routing plan.
- Transaction, outbox, saga, or reconciliation plan.
- Correctness verification and repair plan.

## Evidence Gates

- `semantics_check`: every critical operation has freshness, ordering, idempotency, conflict, and durability semantics.
- `consistency_choice`: chosen guarantees are justified by user consequence and failure behavior.
- `ownership_check`: every data class has an owner and mutation boundary.
- `partition_check`: shard/tenant key, hot-key risk, and resharding approach are addressed where scale requires it.
- `repair_check`: invariants, reconciliation, audit, or manual repair path exists for known inconsistency modes.

## Red Flags - Stop And Rework

- Storage is selected before data semantics are written.
- "Eventually consistent" is used without saying what users can observe or how conflicts repair.
- Distributed locks are hand-rolled.
- Hot keys or tenant skew are ignored for a high-scale path.
- Cross-service writes are described as atomic without a mechanism or compensation plan.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| One consistency level for everything | Decide per operation and data class. |
| Using caches to solve semantics | Decide stale-read semantics here, then route cache mechanics. |
| Ignoring repair | Define invariants, reconciliation, audit, and correction paths. |
| Treating sharding as later | At least identify shard keys and hot-key risks early. |
