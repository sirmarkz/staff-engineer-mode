---
name: capacity-performance-and-tail-latency
description: "Use when latency, throughput, load tests, saturation, queues, capacity, or hot paths are central."
---

# Capacity Performance And Tail Latency

## Overview

Users experience tail latency, not averages.

**Core principle:** model demand, concurrency, queueing, saturation, and fanout, then test to the knee of the curve before production finds it.

## Iron Law

```
NO CAPACITY OR PERFORMANCE CLAIM WITHOUT A TRAFFIC MODEL, TAIL METRIC, SATURATION SIGNAL, AND TEST EVIDENCE
```

If the answer only says "scale horizontally" or reports averages, it is not enough.

## When To Use

- The user asks about p95, p99, p99.9, throughput, QPS, concurrency, queueing, saturation, hot paths, or scaling limits.
- A release caused latency or throughput regression.
- A launch, PRR, or migration needs capacity evidence.
- The system needs load, stress, spike, soak, or failure-condition testing.
- Cost is discussed as a capacity/headroom tradeoff rather than a billing support question.

## When Not To Use

- The main problem is retries, timeouts, or dependency failure safety; use dependency resilience.
- The main request is public edge abuse, denial-of-service defense, or application-layer filtering; use edge traffic defense.
- The user asks pure billing/procurement questions; out of scope.
- The work is SLO target selection without performance investigation; use SLO engineering.

## Inputs To Collect

- User journeys, SLOs, latency percentiles, throughput targets, and acceptable degradation behavior.
- Traffic model: current, peak, forecast, burstiness, tenant skew, payload size, and fanout.
- Resource signals: CPU, memory, IO, network, lock contention, connection pools, thread pools, queue depth, queue age, and GC.
- Load-balancing behavior, locality, shard keys, hot partitions, cache hit rate, and downstream quotas.
- Existing load tests, production incidents, profiling/flame graphs, and regression data.
- Headroom policy, autoscaling behavior, failover capacity, and unit-cost constraints.

## Workflow

1. **Define the user-visible target.** Choose p95/p99/p99.9 and throughput targets that map to SLOs or launch requirements.
2. **Build the demand model.** Capture request rate, burstiness, concurrency, fanout, payload, tenant skew, and seasonal peaks.
3. **Apply queueing sanity checks.** Use Little's Law to connect arrival rate, latency, and concurrency; identify queues that can hide saturation.
4. **Find saturation points.** Track RED for services and USE for resources. Include locks, connection pools, thread pools, caches, and downstream quotas.
5. **Test to the knee.** Run load/stress/spike/soak tests in production-like environments until latency or errors become nonlinear; stop before uncontrolled damage.
6. **Protect the system.** Define admission control, load shedding, prioritization, and graceful degradation before saturation.
7. **Investigate regressions scientifically.** Compare before/after profiles, deploy markers, dependency metrics, cache behavior, and resource saturation.
8. **Tie capacity to cost when relevant.** Preserve required headroom and failover capacity; optimize unit economics only after risk is explicit.

## Synthesized Default

Optimize around tail percentiles, saturation, queue age, and headroom rather than averages. Combine tail-at-scale design, SRE golden signals, performance baselines, load-shedding practice, and unit-cost discipline when cost is explicitly part of the reliability tradeoff.

## Exceptions

- Batch pipelines may use freshness and completion latency instead of request p99; route to data pipeline reliability when the system is mainly ETL.
- Internal low-tier tools may use lower headroom or ticket-only alerts when owners accept the SLO.
- Hedged requests can reduce tail latency only when extra load is budgeted and duplicate work is safe.
- Predictive scaling helps predictable demand, but cold-start latency must not sit on a critical synchronous path.

## Response Quality Bar

- Lead with the capacity model, tail-latency diagnosis, load-test plan, or headroom decision requested.
- Cover traffic shape, fanout, tail budgets, saturation signals, load shedding, test evidence, failure-domain headroom, and cost tradeoffs when relevant before optional performance breadth.
- Make recommendations actionable with owners, thresholds, test scenarios, stop criteria, scaling limits, rollback actions, and regression gates where relevant.
- State required evidence such as p95/p99 metrics, peak/burst traffic, concurrency, queue age, resource saturation, downstream limits, load-test results, and unit cost; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside capacity, performance, and tail latency. Route data pipelines, dependency resilience, or FinOps only when they materially change the decision.
- Be concise: avoid generic performance advice and prefer compact capacity models, latency budgets, and test matrices.

## Required Outputs

- Capacity model covering normal, peak, burst, and failure-domain conditions.
- Latency budget by hop, including dependency fanout.
- Load/stress/spike/soak test plan with stop criteria and rollback.
- Saturation dashboard spec using RED/USE plus queue age and drain rate.
- Load-shedding and admission-control thresholds.
- Performance regression analysis plan or results.
- Cost/headroom tradeoff record when cost is part of the prompt.

## Evidence Gates

- `tail_metric`: target percentile, window, and journey are stated.
- `traffic_model`: peak, burst, concurrency, fanout, and tenant skew are modeled or marked unknown.
- `saturation_signals`: resource, queue, pool, and downstream saturation metrics are identified.
- `test_evidence`: load or regression test has scenario, stop criteria, result, and owner.
- `headroom_check`: capacity includes peak and expected failure-domain conditions.

## Red Flags - Stop And Rework

- Average latency is used as the primary user-experience metric.
- The plan scales replicas but ignores database, cache, queue, or downstream limits.
- Load tests stop at expected peak and never find the nonlinear point.
- Queue depth is monitored without queue age or drain rate.
- Cost cutting removes failover headroom without changing the SLO or accepting risk.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating CPU as capacity | Include all saturation points: queues, locks, pools, IO, network, and dependencies. |
| Testing only steady load | Add bursts, soak, failover, cold cache, and dependency-slow scenarios. |
| Hiding overload in queues | Track age and drain rate; shed work before recovery becomes impossible. |
| Optimizing p50 | Optimize the percentile users and SLOs actually experience. |
