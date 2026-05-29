# Data Pipeline Reliability Plan

## Pipeline Scope

- Source:
- Sink:
- Freshness target:
- Correctness target:

## Pipeline SLI/SLO

| Journey/Dataset | SLI | SLO | Measurement Source | Missing-Signal Behavior |
| --- | --- | --- | --- | --- |

## Dataset Responsibility And Lineage

| Dataset | Owner | Upstream Source | Downstream Consumer | Transformation |
| --- | --- | --- | --- | --- |

## Freshness And Quality Signals

| Signal | Source | Threshold | Missing-Signal Behavior | Owner |
| --- | --- | --- | --- | --- |

## Validation And Publish Checks

| Check | Blocks Publish? | Failure Response | Evidence |
| --- | --- | --- | --- |

## Replay And Idempotency

| Stage | Idempotency Key | Replay Method | Duplicate Handling | Verification |
| --- | --- | --- | --- | --- |

## Late, Bad, Or Missing Data

| Failure | Detection | Quarantine/DLQ | Repair Path | User Impact |
| --- | --- | --- | --- | --- |

## Backfill Runbook

| Step | Throttle | Checkpoint | Abort | Validation |
| --- | --- | --- | --- | --- |

## Consumer Impact And Recovery Tests

| Consumer | Impact | Notification Path | Recovery Test Or Plan | Gap |
| --- | --- | --- | --- | --- |
