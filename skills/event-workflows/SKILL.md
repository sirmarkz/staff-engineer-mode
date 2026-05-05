---
name: event-workflows
description: "Use to design an event, queue, stream, saga, or workflow — and define idempotency, retry, DLQ, ordering, and replay before async messages start landing twice or out of order."
---

# Event Driven Systems And Workflows

## Overview

Asynchronous systems trade call-time coupling for delivery, ordering, replay, and correction obligations.

**Core principle:** assume duplicate, delayed, reordered, and replayed messages unless the design proves otherwise.

## Iron Law

```
NO EVENT OR WORKFLOW WITHOUT CONTRACT, IDEMPOTENCY, RETRY, DLQ, AND REPLAY POLICY
```

If consumers cannot safely see a message twice or late, the workflow is not production-ready.

## When To Use

- The user asks about events, queues, streams, change capture, transactional outbox, sagas, retries, DLQs, replay, message schemas, or workflow orchestration.
- A design replaces synchronous calls with asynchronous processing.
- A multi-step business process spans services or ownership boundaries.
- The user asks how to publish state changes reliably.

## When Not To Use

- The design is only synchronous RPC or HTTP call policy; defer to `dependency-resilience`.
- The main question is storage consistency or transaction semantics; defer to `distributed-data-and-consistency`.
- The work is batch/warehouse freshness and lineage; defer to `data-pipeline-reliability`.
- The issue is cache invalidation only; defer to `caching-and-derived-data`.

## Inputs To Collect

- Producers, consumers, owners, topics/queues/streams, and event purpose.
- Event type: notification, state transfer, event-sourced fact, command, reply, or workflow step.
- Schema, compatibility rules, required fields, versioning, and ownership.
- Delivery semantics, ordering needs, partition key, idempotency key, and dedupe window.
- Retry policy, backoff, max attempts, DLQ handling, poison message behavior, and manual repair.
- Replay needs, retention, correction process, and consumer side effects.
- Backlog metrics, processing latency, freshness, consumer lag, and alert thresholds.

## Workflow

1. **Classify the pattern.** Distinguish notification, event-carried state, event sourcing, command, CQRS read model, saga, and workflow orchestration.
2. **Define the contract.** Write schema, meaning, ownership, compatibility, and versioning rules before implementation.
3. **Publish atomically.** Use a durable local transaction plus outbox or equivalent when state change and message publication must agree.
4. **Make consumers idempotent.** Design dedupe, commutative updates, durable processing markers, or safe side effects.
5. **Control retries.** Bound attempts, add backoff/jitter, isolate poison messages, and define DLQ ownership.
6. **Plan ordering and partitioning.** Order only where necessary; choose partition keys that avoid hot partitions and preserve required entity order.
7. **Design replay and correction.** Ensure reprocessing is safe, observable, and can repair bad events or bad consumers.
8. **Instrument the flow.** Track enqueue time, age, depth, lag, drain rate, processing errors, DLQ volume, and replay progress.

## Synthesized Default

Use at-least-once delivery with idempotent consumers as the default mental model. Use outbox or equivalent for atomic publish, sagas or workflow state for multi-step processes, schema compatibility for evolution, durable queueing for rate mismatch, and explicit replay/correction for recovery. Treat event sourcing as a high-complexity pattern, not a default persistence style.

## Exceptions

- Broker-level exactly-once guarantees may reduce duplicates inside one boundary, but consumers still need duplicate-safe business outcomes.
- Ordering should be scoped to the smallest entity needed; global ordering is rarely worth the throughput and availability cost.
- Fire-and-forget notifications are acceptable only when loss, duplication, and delay are explicitly harmless.
- Human approval workflows may prefer explicit workflow state over event choreography.

## Response Quality Bar

- Lead with the workflow state model, failure handling plan, or blockers.
- Cover idempotency, ordering, retries, DLQ/poison handling, compensation, and reconciliation before optional event-system topics.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and replay controls where relevant.
- State required evidence such as event keys, retry counts, duplicate rates, DLQ age, consumer lag, and replay proof; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside the workflow and event contract. Route broad API or data consistency issues only when material.
- Be concise: avoid generic event-driven background and prefer compact state/retry/DLQ tables.

## Required Outputs

- Event/workflow contract and schema compatibility policy.
- Producer/consumer ownership matrix.
- Idempotency and duplicate-handling plan.
- Retry, backoff, DLQ, and poison-message policy.
- Ordering, partitioning, and hot-key plan.
- Replay, correction, and manual repair plan.
- Observability requirements for age, lag, depth, errors, and replay.

## Evidence Gates

- `contract_check`: event meaning, schema, owner, and compatibility rules are documented.
- `idempotency_check`: every consumer side effect is duplicate-safe or explicitly non-retryable.
- `retry_dlq_check`: retry attempts, backoff, DLQ ownership, and poison handling are defined.
- `ordering_check`: ordering and partition key choices match the entity semantics.
- `replay_check`: replay/correction path is safe and observable.

## Red Flags - Stop And Rework

- Consumers assume exactly-once delivery without dedupe or idempotent side effects.
- DLQ exists but nobody owns draining, replay, or correction.
- Events are named after implementation steps rather than durable business facts.
- Schema changes have no compatibility rules.
- Replay would send emails, charge cards, or trigger irreversible actions again.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Using events to hide coupling | Make ownership and contract explicit. |
| Treating DLQ as storage | Define owner, triage, replay, and discard policy. |
| Requiring global order | Order only per entity or workflow where needed. |
| Forgetting correction | Plan bad-event and bad-consumer repair from the start. |
