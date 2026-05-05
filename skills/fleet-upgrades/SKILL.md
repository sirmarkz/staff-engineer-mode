---
name: fleet-upgrades
description: "Use to plan a runtime, platform, or framework upgrade across many services, clients, or hosts — version skew, support windows, mixed-version compatibility, and rollback path."
---

# Fleet Upgrades And Version Skew Management

## Overview

Fleet upgrades are compatibility projects spread across runtimes, control planes, clients, services, and operators.

**Core principle:** inventory support windows, define allowed skew, prove mixed-version compatibility, stage rollout, and keep rollback or roll-forward paths ready.

## Iron Law

```
NO FLEET UPGRADE WITHOUT INVENTORY, SUPPORT WINDOW, SKEW POLICY, COMPATIBILITY TESTS, AND ROLLOUT OWNER
```

If the team cannot see what versions exist and what combinations are supported, the upgrade plan is guessing.

## When To Use

- The user asks about fleet upgrades, runtime upgrades, platform upgrades, support windows, version skew, end-of-support, or mixed-version rollout.
- Many services, clients, jobs, workers, agents, nodes, or control-plane components must move over time.
- Old and new versions need to coexist safely during rollout.
- A vendor, community, or internal platform support deadline creates production risk.

## When Not To Use

- The work is a routine library update inside one repo; defer to `dependency-and-code-hygiene`.
- The main risk is build artifact reproducibility; defer to `release-build-reproducibility`.
- The main risk is exposed API compatibility; defer to `api-design-and-compatibility`.
- The main task is broad service retirement; defer to `migration-and-deprecation`.

## Inputs To Collect

- Fleet inventory: components, owners, versions, environments, criticality, and support status.
- Version-skew policy, compatibility matrix, upgrade order, and blocked combinations.
- Tests for mixed versions, client/server compatibility, data compatibility, and operational tooling.
- Rollout batches, maintenance windows, traffic exposure, rollback or roll-forward path, and freeze dates.
- Known deprecated features, removed behavior, config changes, and operator runbooks.
- Support-window communication plan: affected consumers, deadline, required consumer action, reminder cadence, and escalation or enforcement path.
- Exception list, owner, expiry, and compensating controls.

## Workflow

1. **Inventory the fleet.** List versions, owners, support windows, criticality, and unknowns.
2. **Define allowed skew.** State which old/new combinations are supported during rollout and for how long.
3. **Communicate support deadlines.** Tell affected consumers when old versions leave support, what action they must take, and when reminders, escalation, or enforcement start.
4. **Find breaking changes.** Review behavior, config, interfaces, data formats, tooling, and operational assumptions.
5. **Prove compatibility.** Test mixed-version paths, upgrade order, downgrade or roll-forward behavior, and representative workloads.
6. **Batch rollout.** Move low-risk cohorts first, then critical paths with gates, owner signoff, and monitoring.
7. **Manage exceptions.** Track blockers with owner, expiry, risk, and compensating control.
8. **Update operations.** Refresh runbooks, alerts, dashboards, and support procedures for the new version.
9. **Close old paths.** Remove compatibility shims, stale versions, and exceptions after adoption is proven.

## Synthesized Default

Use a support-window inventory, explicit version-skew policy, compatibility matrix, staged rollout, support-deadline communication plan, exception register, operational runbook update, and retirement gate for old versions. Prefer proving mixed-version behavior before the first production batch.

## Exceptions

- Emergency security upgrades may compress rollout stages, but still need owner, compatibility risk review, consumer notice if deadlines change, and rollback or roll-forward decision.
- Low-risk internal tools can use lighter gates if they are not production dependencies.
- Some upgrades cannot roll back safely; require stronger preflight tests and roll-forward criteria.

## Response Quality Bar

- Lead with the upgrade plan, skew decision, support-window risk, or blocker list requested.
- Cover inventory, support status, skew policy, compatibility tests, rollout batches, rollback or roll-forward, exceptions, consumer communication, and operations updates before optional detail.
- Make recommendations actionable with owners, dates, gates, batch order, test evidence, consumer action requirements, and exception expiry where relevant.
- For end-of-support or support-window risk, include a short consumer communication timeline: announcement, deadline, required action from affected owners, reminder cadence, and escalation or enforcement date.
- State required evidence such as version inventory, support deadlines, compatibility matrix, test output, rollout status, communication status, and runbook changes; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside fleet upgrade and version-skew management. Route dependency hygiene, API compatibility, or deprecation work only when that surface dominates.
- Be concise: prefer upgrade matrices and batch plans over broad migration prose.
- Emit upgrade order as a discrete labeled tier list before the time-phased rollout, not buried inside a weekly schedule.

## Required Outputs

- Fleet inventory with owner, version, criticality, and support status.
- Version-skew and compatibility matrix.
- Upgrade order as an explicit tier list (e.g., control plane → data plane / nodes → clients/operators), with one-line rationale per tier and the allowed skew range between tiers stated as a numeric window with breakage criteria.
- End-of-support / support-window communication plan with announcement date, final support date, affected consumers, required consumer action, reminder cadence, and escalation or enforcement path.
- Rollout batches (waves) with progression criteria per wave.
- Mixed-version test plan and evidence requirements.
- Rollback or roll-forward plan stating both the procedure and the state-compatibility note (which prior state is restorable, which is not).
- Exception register with owner, expiry, and compensating control.
- Operations update checklist.
- Old-version retirement gate.

## Evidence Gates

- `inventory_complete`: supported, unsupported, unknown, and critical versions are visible.
- `skew_policy`: allowed mixed-version combinations and duration are explicit.
- `support_comms`: affected consumers, support deadline, required action, reminder cadence, and escalation or enforcement owner are visible.
- `compatibility_test`: representative old/new paths are tested before broad rollout.
- `rollout_owner`: every batch has owner, gate, and halt criteria.
- `exception_expiry`: blocked components have owner, risk, compensating control, and expiry.

## Red Flags - Stop And Rework

- The fleet inventory is based on guesses or stale spreadsheets.
- Old and new versions are assumed compatible without tests.
- Upgrade order ignores clients, jobs, agents, or operational tooling.
- Unsupported versions have no exception owner or consumer communication deadline.
- Rollback is impossible but roll-forward criteria are not defined.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Version bump as task | Treat it as a compatibility and rollout project. |
| No skew policy | Define supported old/new combinations. |
| Silent support deadline | Announce the deadline, required consumer action, reminders, and enforcement path. |
| Ignoring operators | Update runbooks, alerts, and tooling. |
| Leaving old versions | Add retirement gates and cleanup. |
---
name: fleet-upgrades
description: "Use to plan a runtime, platform, or framework upgrade across many services, clients, or hosts — version skew, support windows, mixed-version compatibility, and rollback path."
---

# Fleet Upgrades And Version Skew Management

## Overview

Fleet upgrades are compatibility projects spread across runtimes, control planes, clients, services, and operators.

**Core principle:** inventory support windows, define allowed skew, prove mixed-version compatibility, stage rollout, and keep rollback or roll-forward paths ready.

## Iron Law

```
NO FLEET UPGRADE WITHOUT INVENTORY, SUPPORT WINDOW, SKEW POLICY, COMPATIBILITY TESTS, AND ROLLOUT OWNER
```

If the team cannot see what versions exist and what combinations are supported, the upgrade plan is guessing.

## When To Use

- The user asks about fleet upgrades, runtime upgrades, platform upgrades, support windows, version skew, end-of-support, or mixed-version rollout.
- Many services, clients, jobs, workers, agents, nodes, or control-plane components must move over time.
- Old and new versions need to coexist safely during rollout.
- A vendor, community, or internal platform support deadline creates production risk.

## When Not To Use

- The work is a routine library update inside one repo; defer to `dependency-and-code-hygiene`.
- The main risk is build artifact reproducibility; defer to `release-build-reproducibility`.
- The main risk is exposed API compatibility; defer to `api-design-and-compatibility`.
- The main task is broad service retirement; defer to `migration-and-deprecation`.

## Inputs To Collect

- Fleet inventory: components, owners, versions, environments, criticality, and support status.
- Version-skew policy, compatibility matrix, upgrade order, and blocked combinations.
- Tests for mixed versions, client/server compatibility, data compatibility, and operational tooling.
- Rollout batches, maintenance windows, traffic exposure, rollback or roll-forward path, and freeze dates.
- Known deprecated features, removed behavior, config changes, and operator runbooks.
- Support-window communication plan: affected consumers, deadline, required consumer action, reminder cadence, and escalation or enforcement path.
- Exception list, owner, expiry, and compensating controls.

## Workflow

1. **Inventory the fleet.** List versions, owners, support windows, criticality, and unknowns.
2. **Define allowed skew.** State which old/new combinations are supported during rollout and for how long.
3. **Communicate support deadlines.** Tell affected consumers when old versions leave support, what action they must take, and when reminders, escalation, or enforcement start.
4. **Find breaking changes.** Review behavior, config, interfaces, data formats, tooling, and operational assumptions.
5. **Prove compatibility.** Test mixed-version paths, upgrade order, downgrade or roll-forward behavior, and representative workloads.
6. **Batch rollout.** Move low-risk cohorts first, then critical paths with gates, owner signoff, and monitoring.
7. **Manage exceptions.** Track blockers with owner, expiry, risk, and compensating control.
8. **Update operations.** Refresh runbooks, alerts, dashboards, and support procedures for the new version.
9. **Close old paths.** Remove compatibility shims, stale versions, and exceptions after adoption is proven.

## Synthesized Default

Use a support-window inventory, explicit version-skew policy, compatibility matrix, staged rollout, support-deadline communication plan, exception register, operational runbook update, and retirement gate for old versions. Prefer proving mixed-version behavior before the first production batch.

## Exceptions

- Emergency security upgrades may compress rollout stages, but still need owner, compatibility risk review, consumer notice if deadlines change, and rollback or roll-forward decision.
- Low-risk internal tools can use lighter gates if they are not production dependencies.
- Some upgrades cannot roll back safely; require stronger preflight tests and roll-forward criteria.

## Response Quality Bar

- Lead with the upgrade plan, skew decision, support-window risk, or blocker list requested.
- Cover inventory, support status, skew policy, compatibility tests, rollout batches, rollback or roll-forward, exceptions, consumer communication, and operations updates before optional detail.
- Make recommendations actionable with owners, dates, gates, batch order, test evidence, consumer action requirements, and exception expiry where relevant.
- For end-of-support or support-window risk, include a short consumer communication timeline: announcement, deadline, required action from affected owners, reminder cadence, and escalation or enforcement date.
- State required evidence such as version inventory, support deadlines, compatibility matrix, test output, rollout status, communication status, and runbook changes; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside fleet upgrade and version-skew management. Route dependency hygiene, API compatibility, or deprecation work only when that surface dominates.
- Be concise: prefer upgrade matrices and batch plans over broad migration prose.
- Emit upgrade order as a discrete labeled tier list before the time-phased rollout, not buried inside a weekly schedule.

## Required Outputs

- Fleet inventory with owner, version, criticality, and support status.
- Version-skew and compatibility matrix.
- Upgrade order as an explicit tier list (e.g., control plane → data plane / nodes → clients/operators), with one-line rationale per tier and the allowed skew range between tiers stated as a numeric window with breakage criteria.
- End-of-support / support-window communication plan with announcement date, final support date, affected consumers, required consumer action, reminder cadence, and escalation or enforcement path.
- Rollout batches (waves) with progression criteria per wave.
- Mixed-version test plan and evidence requirements.
- Rollback or roll-forward plan stating both the procedure and the state-compatibility note (which prior state is restorable, which is not).
- Exception register with owner, expiry, and compensating control.
- Operations update checklist.
- Old-version retirement gate.

## Evidence Gates

- `inventory_complete`: supported, unsupported, unknown, and critical versions are visible.
- `skew_policy`: allowed mixed-version combinations and duration are explicit.
- `support_comms`: affected consumers, support deadline, required action, reminder cadence, and escalation or enforcement owner are visible.
- `compatibility_test`: representative old/new paths are tested before broad rollout.
- `rollout_owner`: every batch has owner, gate, and halt criteria.
- `exception_expiry`: blocked components have owner, risk, compensating control, and expiry.

## Red Flags - Stop And Rework

- The fleet inventory is based on guesses or stale spreadsheets.
- Old and new versions are assumed compatible without tests.
- Upgrade order ignores clients, jobs, agents, or operational tooling.
- Unsupported versions have no exception owner or consumer communication deadline.
- Rollback is impossible but roll-forward criteria are not defined.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Version bump as task | Treat it as a compatibility and rollout project. |
| No skew policy | Define supported old/new combinations. |
| Silent support deadline | Announce the deadline, required consumer action, reminders, and enforcement path. |
| Ignoring operators | Update runbooks, alerts, and tooling. |
| Leaving old versions | Add retirement gates and cleanup. |
