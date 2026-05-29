# High Availability Design

## Survivability Statement

- Survive loss of:
- While continuing:
- User-visible degradation allowed:

## Fault-Domain Inventory

| Component | Fault Domain | Shared Dependency | Hidden Coupling | Mitigation |
| --- | --- | --- | --- | --- |

## Capacity Model

| Scenario | Required Capacity | Available Capacity | Quota/Limit | Gap |
| --- | --- | --- | --- | --- |

## Blast Radius And Isolation

| Fault Domain | Blast Radius | Partition/Shard/Tenant Isolation | Hidden Dependency | Exception |
| --- | --- | --- | --- | --- |

## Failover Decision Record

| Trigger | Authority | Data Behavior | Rollback | Evidence |
| --- | --- | --- | --- | --- |

## Health And Traffic Shift

| Fault Domain | Health Signal | Trigger | Traffic Action | Last Validation |
| --- | --- | --- | --- | --- |

## Validation Plan

| Test | Scope | Abort Criteria | Telemetry | Capture |
| --- | --- | --- | --- | --- |
