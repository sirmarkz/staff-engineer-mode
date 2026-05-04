---
name: backup-and-recovery
description: "Use when backups, restore tests, disaster recovery, RTO/RPO, or recovery evidence are central."
---

# Backup Restore And Disaster Recovery

## Overview

Backups do not matter until a restore works.

**Core principle:** define recoverability by RTO/RPO and prove it with restore evidence under realistic failure scenarios, including destructive operators and corrupted data.

## Iron Law

```
NO RECOVERY CLAIM WITHOUT A TESTED RESTORE AND RTO/RPO EVIDENCE
```

A successful backup job is not DR evidence. Replication is not a backup. Multi-region serving is not proof of data recovery.

## When To Use

- The user asks about backups, restores, disaster recovery, RTO, RPO, PITR, immutable backups, regional recovery, ransomware recovery, or destructive data changes.
- A stateful launch or PRR needs recovery evidence.
- The system must recover from corrupted rows, accidental deletion, bad migrations, lost keys, regional loss, or compromised operators.
- The user asks which DR strategy to use: backup/restore, pilot light, warm standby, or active-active.

## When Not To Use

- The main goal is serving through zone/cell loss without restoring data; defer to `high-availability-design`.
- The request is normal unit/integration testing.
- The issue is online schema/backfill execution before disaster occurs; defer to `database-operations`.
- A live outage needs command, communications, and mitigation; route to `incident-response-and-postmortems` alongside this skill.

## Inputs To Collect

- Critical data sets, owners, customer journeys, data classification, and deletion/corruption blast radius.
- RTO/RPO expectations by journey, tenant, data class, and regulatory/customer commitment.
- Backup method, cadence, retention, location, encryption, key ownership, immutability, and access policy.
- Replication topology, lag, consistency model, PITR capability, and regional dependencies.
- Restore procedure, last restore evidence, restore environment, validation queries, and rehearsal history.
- Destructive scenarios: operator error, ransomware, compromised credentials, bad deploy, bad migration, and key loss.

## Workflow

1. **Classify what must be recovered.** Separate serving availability, data durability, data correctness, and audit/history requirements.
2. **Set RTO/RPO.** Record maximum tolerable downtime and data loss for each critical journey and data set.
3. **Map backup coverage.** Include data, metadata, schema, config, secrets/keys, object stores, queues, indexes, and derived state.
4. **Check isolation.** Ensure backups and keys survive accidental deletion, malicious operator action, account compromise, and ransomware.
5. **Design restore paths.** Include full restore, partial restore, point-in-time recovery, regional rebuild, and corruption repair.
6. **Validate with evidence.** Restore into a controlled environment, run correctness checks, measure elapsed time and data loss, and record gaps.
7. **Choose DR posture.** Use backup/restore, pilot light, warm standby, active-passive, or active-active based on RTO/RPO, complexity, cost, data residency, and operations maturity.
8. **Feed findings back.** Create blockers for PRR, platform fixes, runbook updates, and future drills.

## Synthesized Default

Use tested restore evidence tied to RTO/RPO as the default. Protect backups and encryption keys in a separate trust and blast-radius boundary. Prefer the simplest DR strategy that meets RTO/RPO and residency constraints; do not choose active-active unless the serving requirement and team maturity justify the operational cost.

## Exceptions

- Stateless services may document dependency recovery rather than service-local backups.
- Derived indexes or caches may be rebuilt instead of backed up if rebuild time fits RTO and source data is protected.
- Active-active may be required for very low RTO, but it still needs corruption recovery and backup isolation.
- Emergency data repair during an incident may proceed before full DR analysis, but evidence and postmortem actions must follow.

## Response Quality Bar

- Lead with the restore readiness decision, DR strategy, RTO/RPO gap, or blocker list requested.
- Cover backup coverage, retention, encryption/key recovery, isolation, restore runbooks, corruption/PITR/partial restore, validation, and remediation before optional DR breadth.
- Make recommendations actionable with owners, commands, prerequisites, gates, stop criteria, measured targets, and remediation deadlines where relevant.
- State required evidence such as backup job metadata, restore logs, validation queries, key recovery proof, retention settings, immutable storage controls, and measured RTO/RPO; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside backup, restore, and DR. Route HA serving design or incident repair only when those are the central unresolved risk.
- Be concise: avoid generic DR taxonomy and prefer compact coverage matrices and restore evidence tables.

## Required Outputs

- DR strategy decision record.
- RTO/RPO table by journey and data set.
- Backup coverage, retention, encryption, key, and immutability matrix.
- Restore runbook with owner, prerequisites, commands, validation, and rollback.
- PITR, partial restore, corruption repair, and regional recovery plan.
- Restore test evidence log with measured RTO/RPO and gaps.
- Remediation backlog for missing coverage or failed restore criteria.

## Evidence Gates

- `restore_evidence`: a recent restore test exists, or missing restore evidence is marked as a blocker.
- `rto_rpo_fit`: measured restore time and data loss meet the stated targets, or exceptions are owned and dated.
- `coverage_matrix`: critical data, metadata, schema, config, and keys have backup or rebuild coverage.
- `isolation_check`: backups and keys are protected from destructive operator, compromised credential, and ransomware scenarios.
- `validation_queries`: restored data has correctness checks, not just process completion.

## Red Flags - Stop And Rework

- The only evidence is "backup job succeeded".
- Replication is treated as protection against accidental deletion or corruption.
- Backups and production data are deletable by the same credentials.
- Encryption keys needed for restore are not backed up, recoverable, or separately protected.
- RTO/RPO is copied from a platform default without measuring restore time.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Equating HA with DR | HA keeps serving; DR restores lost or corrupted state. |
| Testing full restore only | Include partial restore, PITR, corruption repair, and regional rebuild where relevant. |
| Ignoring derived state | Decide whether indexes, caches, search, and analytics are backed up or rebuilt inside RTO. |
| Treating drills as paperwork | Capture measured time, data loss, validation results, and remediation owners. |
