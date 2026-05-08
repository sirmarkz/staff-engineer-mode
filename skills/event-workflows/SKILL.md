---
name: event-workflows
description: "Use when events, messages, queues, streams, sagas, or workflows need idempotency, retry, DLQ, ordering, or replay"
---

# Event Driven Systems And Workflows

## Iron Law

```
NO EVENT OR WORKFLOW WITHOUT CONTRACT, IDEMPOTENCY, RETRY, DLQ, AND REPLAY POLICY
```

If consumers cannot safely see a message twice or late, the workflow is not production-ready.

## Overview

Asynchronous systems trade call-time coupling for delivery, ordering, replay, and correction obligations.

**Core principle:** assume duplicate, delayed, reordered, and replayed messages unless the design proves otherwise.

## When To Use

- The user asks about events, queues, streams, change capture, transactional outbox, sagas, retries, DLQs, replay, message schemas, or workflow orchestration.
- A design replaces synchronous calls with asynchronous processing.
- A multi-step business process spans services or responsibility boundaries.
- The user asks how to publish state changes reliably.

## When Not To Use

- The design is only synchronous RPC or HTTP call policy; use `dependency-resilience` instead.
- The main question is storage consistency or transaction semantics; use `distributed-data-and-consistency` instead.
- The work is batch/warehouse freshness and lineage; use `data-pipeline-reliability` instead.
- The issue is cache invalidation only; use `caching-and-derived-data` instead.

## Inputs To Collect

- Producers, consumers, topics/queues/streams, and event purpose.
- Event type: notification, state transfer, event-sourced fact, command, reply, or workflow step.
- Schema, compatibility rules, required fields, versioning, and responsibility.
- Delivery semantics, ordering needs, partition key, idempotency key, and dedupe window.
- Retry policy, backoff, max attempts, DLQ handling, poison message behavior, and manual repair.
- Replay needs, retention, correction process, and consumer side effects.
- Backlog metrics, processing latency, freshness, consumer lag, and alert thresholds.

## Workflow

1. **Classify the pattern.** Distinguish notification, event-carried state, event sourcing, command, CQRS read model, saga, and workflow orchestration.
2. **Define the contract.** Write schema, meaning, responsibility, compatibility, and versioning rules before implementation.
3. **Publish atomically.** Use a durable local transaction plus outbox or equivalent when state change and message publication must agree.
4. **Make consumers idempotent.** Design dedupe, commutative updates, durable processing markers, or safe side effects.
5. **Control retries.** Bound attempts, add backoff/jitter, isolate poison messages, and define DLQ responsibility.
6. **Plan ordering and partitioning.** Order only where necessary; choose partition keys that avoid hot partitions and preserve required entity order.
7. **Design replay and correction.** Ensure reprocessing is safe, observable, and can repair bad events or bad consumers.
8. **Instrument the flow.** Track enqueue time, age, depth, lag, drain rate, processing errors, DLQ volume, and replay progress.

## Synthesized Default

Use at-least-once delivery with idempotent consumers as the default mental model. Use outbox or equivalent for atomic publish, sagas or workflow state for multi-step processes, schema compatibility for evolution, durable queueing for rate mismatch, and explicit replay/correction for recovery. Treat event sourcing as a high-complexity pattern, not a default persistence style.

## Exceptions

- Broker-level exactly-once guarantees may reduce duplicates inside one boundary, but consumers still need duplicate-safe business outcomes.
- Ordering should be scoped to the smallest entity needed; global ordering is rarely worth the throughput and availability cost.
- Fire-and-forget notifications are acceptable only when loss, duplication, and delay are explicitly harmless.
- Human confirmation workflows may prefer explicit workflow state over event choreography.

## Response Quality Bar

- Lead with the workflow state model, failure handling plan, or blockers.
- Cover idempotency, ordering, retries, DLQ/poison handling, compensation, and reconciliation before optional event-system topics.
- Make recommendations actionable with evidence, gates, stop conditions, and replay controls where relevant.
- State required evidence such as event keys, retry counts, duplicate rates, DLQ age, consumer lag, and replay proof; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside the workflow and event contract. Route broad API or data consistency issues only when material.
- Be concise: avoid generic event-driven background and prefer compact state/retry/DLQ tables.

## Required Outputs

- Event/workflow contract and schema compatibility policy.
- Producer/consumer responsibility matrix.
- Idempotency and duplicate-handling plan.
- Retry, backoff, DLQ, and poison-message policy.
- Ordering, partitioning, and hot-key plan.
- Replay, correction, and manual repair plan.
- Observability requirements for age, lag, depth, errors, and replay.

## Evidence Gates

- `contract_check`: event meaning, schema, and compatibility rules are documented.
- `idempotency_check`: every consumer side effect is duplicate-safe or explicitly non-retryable.
- `retry_dlq_check`: retry attempts, backoff, DLQ responsibility, and poison handling are defined.
- `ordering_check`: ordering and partition key choices match the entity semantics.
- `replay_check`: replay/correction path is safe and observable.

## Red Flags - Stop And Rework

- Consumers assume exactly-once delivery without dedupe or idempotent side effects.
- DLQ exists but draining, replay, or correction has no runbook.
- Events are named after implementation steps rather than durable business facts.
- Schema changes have no compatibility rules.
- Replay would send emails, charge cards, or trigger irreversible actions again.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Using events to hide coupling | Make responsibility and contract explicit. |
| Treating DLQ as storage | Define triage, replay, and discard policy. |
| Requiring global order | Order only per entity or workflow where needed. |
| Forgetting correction | Plan bad-event and bad-consumer repair from the start. |
