# Event Workflow Contract

## Contract

- Producer:
- Consumers:
- Workflow or topic:
- Compatibility policy:

## Producer/Consumer Responsibility

| Party | Responsibility | Failure Response | Owner |
| --- | --- | --- | --- |

## Schema And Compatibility

| Field/Event | Required | Compatibility Rule | Default | Validation |
| --- | --- | --- | --- | --- |

## Delivery Semantics

| Step | Ordering | Partitioning | Idempotency | Duplicate Handling |
| --- | --- | --- | --- | --- |

## Retry, DLQ, And Replay

| Failure | Retry/Backoff | DLQ Or Poison Path | Replay Method | Manual Repair |
| --- | --- | --- | --- | --- |

## Overload Signals

| Signal | Threshold | Response | Owner |
| --- | --- | --- | --- |

## Queue/Workflow Overload

| Queue/Workflow | Depth | Age | Drain Rate | Consumer Concurrency | Poison Path | Batched-Item Status |
| --- | --- | --- | --- | --- | --- | --- |

## Observability

| Signal | Age/Lag/Depth/Error/Replay | Source | Alert |
| --- | --- | --- | --- |
