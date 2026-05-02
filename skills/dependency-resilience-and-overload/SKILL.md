---
name: dependency-resilience-and-overload
description: "Use when the user is changing or adding remote calls, queues, RPCs, retries, timeouts, idempotency, backpressure, circuit breakers, health checks, or load shedding. Do not use for in-process error handling or SLO definition."
---

# Dependency Resilience And Overload

## Overview

Most cascading failures are dependency failures amplified by callers.

**Core principle:** every remote interaction needs a deadline, retry budget, idempotency story, overload behavior, and observable failure mode.

## Iron Law

```
NO REMOTE CALL OR QUEUE WITHOUT TIMEOUT, RETRY, IDEMPOTENCY, AND OVERLOAD POLICY
```

If any dependency can wait forever, retry forever, queue forever, or fail ambiguously, the design is not production-safe.

## When To Use

- A change adds or modifies RPC, HTTP, database, cache, broker, stream, queue, webhook, or third-party calls.
- The user asks about retries, timeouts, backoff, jitter, circuit breakers, bulkheads, idempotency, backpressure, health checks, or load shedding.
- A service degrades when a dependency is slow, overloaded, unavailable, or returning errors.
- Queue depth, age, retries, or fanout can amplify failures.

## When Not To Use

- The request is only about in-process exceptions or validation.
- The main question is SLO target policy; use SLO engineering.
- The main issue is topology and zone/region survival; use HA.
- The problem is p99 optimization without dependency safety changes; use capacity/tail latency.

## Inputs To Collect

- Dependency matrix: caller, callee, operation, protocol, owner, tier, and criticality.
- End-to-end request deadline, per-hop timeout, connection timeout, and cancellation behavior.
- Retry count, retry locations, backoff, jitter, retryable status codes/errors, and retry budget.
- Mutation idempotency: idempotency key, dedupe window, side effects, and replay behavior.
- Queue limits: max depth, age, drain rate, consumer concurrency, poison message handling, and DLQ policy.
- Overload signals: saturation, errors, latency, admission decisions, rejected work, and load-shed responses.
- Health checks: liveness, readiness, startup, dependency probes, and failure thresholds.

## Workflow

1. **Build the dependency matrix.** Include synchronous and asynchronous dependencies, third parties, control planes, and shared infrastructure.
2. **Set the caller deadline.** Define the total time budget from the user's perspective, then allocate per-hop timeouts inside it.
3. **Bound retries.** Retry only when the operation is safe, useful, inside the deadline, jittered, and not repeated at every layer.
4. **Make mutations idempotent.** Require idempotency keys or durable dedupe for retryable writes, webhooks, and queue consumers.
5. **Control queues.** Set max depth, max age, drain-rate alerts, poison handling, and backpressure before backlogs become unrecoverable.
6. **Smooth mismatched rates.** When callers can outpace dependencies, use durable buffering, controlled workers, and rate limits instead of unbounded memory queues.
7. **Design overload response.** Prefer fail-fast, admission control, load shedding, and priority shedding before expensive work starts.
8. **Use circuit breakers carefully.** Only add them when open-state behavior is tested and better than bounded fail-fast.
9. **Keep health checks local.** Readiness may check immediate dependencies only when that cannot remove all capacity at once.

## Synthesized Default

Use bounded timeouts/retries with jitter, idempotent APIs, rate limiting, queue backpressure, and load shedding as the default. Retry only transient conditions inside the caller deadline and retry budget; do not retry permanent failures or overload signals unless the contract explicitly says to. Treat circuit breakers as an exception mechanism, not the first tool. Avoid fallback unless the fallback is simpler, isolated, capacity-tested, and observably correct under the same dependency failure.

## Exceptions

- Some read-only idempotent requests can use hedging for tail latency, but only with capacity accounting and duplicate suppression where needed.
- A circuit breaker is appropriate when repeated calls make the outage worse and the open state has a tested user behavior.
- A fallback is acceptable when it is stale, cached, local, or reduced-quality by design, and does not depend on the same failing system.
- Non-critical asynchronous work may be dropped or delayed if loss semantics are explicit.

## Response Quality Bar

- Lead with the dependency risk, timeout/retry budget, overload policy, or failure-mode plan requested.
- Cover deadlines, retry safety, idempotency, backpressure, load shedding, health checks, fallbacks, and failure tests before optional resilience breadth.
- Make recommendations actionable with owners, thresholds, budgets, queue limits, stop criteria, tests, and rollback or disablement steps where relevant.
- State required evidence such as dependency owners, p95/p99 latency, error classes, retry counts, queue age, saturation, health-check behavior, and failure-test results; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside dependency resilience and overload. Route API contract or capacity-model work only when it materially blocks the failure-mode decision.
- Be concise: avoid generic retry guidance and prefer compact dependency matrices and budget tables.

## Required Outputs

- Dependency matrix with owner, operation, protocol, criticality, and failure behavior.
- Timeout/deadline budget table for caller and each dependency.
- Retry policy with backoff, jitter, retryable conditions, and retry budget.
- Idempotency and duplicate-handling plan for mutations and consumers.
- Queue/backpressure/load-shedding policy with thresholds.
- Health-check design separating liveness, readiness, startup, and dependency checks.
- Failure-mode tests or experiments for slow, erroring, overloaded, and unavailable dependencies.

## Evidence Gates

- `dependency_matrix`: every remote dependency and queue has owner, timeout, retry, and failure behavior.
- `deadline_budget`: per-hop timeouts fit inside the end-to-end caller deadline.
- `retry_safety`: retryable mutations and consumers have idempotency or dedupe evidence.
- `overload_bound`: queues are bounded and overload behavior is observable before saturation cascades.
- `health_check_safety`: health checks cannot remove the whole fleet because a shared dependency is unhealthy.

## Red Flags - Stop And Rework

- Retrying at client, gateway, service, SDK, and worker layers with no budget.
- Timeout values are absent, default, infinite, or longer than the caller's deadline.
- A queue has max depth but no max age, drain-rate alert, DLQ, or poison-message policy.
- Health checks call a shared dependency and mark all instances unavailable at once.
- Fallback is more complex than the primary path or shares the same failing dependency.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Adding retries to fix slowness | First set deadlines and understand capacity; retries add load. |
| Treating circuit breakers as magic | Define and test the open, half-open, and recovery behavior. |
| Ignoring idempotency | Make retryable writes duplicate-safe before enabling retries. |
| Letting queues absorb everything | Bound queues and shed or defer work deliberately. |
