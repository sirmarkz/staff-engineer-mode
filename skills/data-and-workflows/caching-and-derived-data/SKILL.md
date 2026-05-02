---
name: caching-and-derived-data
description: "Use when the user asks about cache mechanics, invalidation, materialized views, index refresh, freshness enforcement, thundering herds, stale cache entries, or derived-state operations. Do not use when the primary question is whether reads may be stale at all."
---

# Caching And Derived Data

## Overview

Caching is a correctness path disguised as a performance optimization.

**Core principle:** every cache or derived view needs explicit freshness, invalidation, stampede protection, failure behavior, and observability.

## Iron Law

```
NO CACHE WITHOUT FRESHNESS, INVALIDATION, AND MISS-STORM BEHAVIOR
```

If writers, invalidators, readers, and downstream systems are not modeled, the cache can become an outage or data-corruption source.

## When To Use

- The user asks about cache invalidation, TTLs, stale entries, materialized views, index refresh, cache stampedes, request coalescing, stale-while-revalidate, or derived-state operations.
- A cache miss or cache failure can overload a backing dependency.
- Derived data needs freshness or repair guarantees.
- The user has already decided stale reads are acceptable and needs operational mechanics.

## When Not To Use

- The primary question is whether stale reads are semantically acceptable; use distributed data.
- The work is primary storage choice or transaction design.
- The issue is warehouse/ETL pipeline freshness; use data pipeline reliability.
- The problem is generic dependency overload without cache mechanics; use dependency resilience.

## Inputs To Collect

- Cached objects, keys, writers, invalidators, readers, and owners.
- Freshness requirement, TTL, negative caching, versioning, and stale-read tolerance.
- Backing dependency capacity, miss amplification, hot keys, and cache population path.
- Failure behavior: cache unavailable, cache cold, invalidation delayed, stale write, partial rebuild.
- Stampede controls: request coalescing, leases, single-flight, prewarming, and rate limits.
- Repair path: reindex, rebuild, invalidate all, partial repair, and correctness checks.
- Metrics: hit/miss, stale reads, evictions, rebuild lag, invalidation lag, downstream load, and tail latency.

## Workflow

1. **Confirm stale-read semantics.** If not decided, route to distributed data before choosing cache mechanics.
2. **Map the lifecycle.** Identify write, invalidate, fill, read, expire, repair, and rebuild paths.
3. **Set freshness policy.** Define TTL, maximum staleness, validation, version checks, and user-visible behavior.
4. **Protect downstreams.** Model miss amplification and add coalescing, leases, prewarming, or load shedding.
5. **Handle invalidation as correctness.** Use explicit invalidation, versioned values, or repair scans when stale writes can occur. For cache-aside writes, define the source-of-truth update and invalidation order.
6. **Define degradation.** State behavior when cache is cold, unavailable, partitioned, or stale.
7. **Instrument correctness and load.** Track stale-read rate, invalidation lag, rebuild lag, hit/miss, and downstream saturation.
8. **Plan repair.** Include manual and automated invalidation/rebuild with verification.

## Synthesized Default

Use explicit TTLs, version-aware invalidation, request coalescing, downstream protection, stale-read observability, and repair paths. Treat cache invalidation as part of the write path and derived-state maintenance as operationally owned; never let the cache become the only proof of correctness.

## Exceptions

- Write-through or write-behind can be appropriate only when write amplification, durability, ordering, and failure semantics are explicit.
- Stale-while-revalidate is useful when stale data is acceptable and marked by freshness policy.
- Negative caching needs short TTLs and careful invalidation for newly created resources.
- Derived views may rebuild from source data instead of backing up if rebuild time fits recovery objectives.

## Response Quality Bar

- Lead with the cache correctness decision, mitigation plan, or production blockers.
- Cover freshness, invalidation, stampede behavior, fallback, source-of-truth semantics, and observability before optional cache topics.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and rollback or bypass actions where relevant.
- State required evidence such as TTLs, hit/miss rates, source update events, stale-read bounds, and dependency saturation; do not claim unseen evidence.
- Stay inside cache and derived-data behavior. Route broader storage consistency or dependency overload only when materially unresolved.
- Be concise: avoid generic caching background and prefer compact consistency and mitigation tables.

## Required Outputs

- Cache or derived-data decision record.
- Key, writer, invalidator, reader, and owner map.
- Freshness, TTL, invalidation, and versioning policy.
- Stampede and miss-amplification protection plan.
- Failure/degradation behavior.
- Metrics and alerts for freshness, stale reads, rebuilds, and downstream load.
- Repair/rebuild runbook and verification checks.

## Evidence Gates

- `freshness_check`: max staleness, TTL, and user-visible stale behavior are explicit.
- `invalidation_map`: writers, invalidators, readers, and versioning/repair paths are documented.
- `stampede_check`: miss storm and hot-key behavior are bounded.
- `downstream_check`: backing dependency capacity under cold/miss conditions is modeled.
- `repair_check`: rebuild/invalidate/repair runbook and correctness verification exist.

## Red Flags - Stop And Rework

- TTL is the only invalidation strategy for correctness-sensitive data.
- Cache miss paths can fan out enough to overload backing systems.
- Writers and invalidators are owned by different teams with no contract.
- Stale entries are possible but not observable.
- Rebuild or reindex time is longer than the business recovery expectation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Calling cache a performance-only detail | Treat it as correctness and availability behavior. |
| Hiding stale reads | Measure and expose freshness. |
| Ignoring cold starts | Model cache cold, regional failover, and bulk invalidation. |
| Invalidating globally by default | Prefer scoped, versioned, or staged repair when possible. |
