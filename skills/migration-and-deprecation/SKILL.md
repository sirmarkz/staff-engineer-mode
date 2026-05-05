---
name: migration-and-deprecation
description: "Use to retire a service, sunset an API family, replace a legacy library, or run a broad migration across many call sites — usage telemetry, replacement readiness, batched migration, and no-new-usage controls."
---

# Large-Scale Change And Service Deprecation

## Overview

Removing or replacing a widely used system is a production change spread across many dependents.

**Core principle:** discover real usage, provide a safe replacement, migrate incrementally, prevent new usage, and remove only after evidence shows dependents are gone.

## Iron Law

```
NO DEPRECATION WITHOUT OWNER, REPLACEMENT, USAGE TELEMETRY, MIGRATION PATH, AND BACKSLIDING CONTROL
```

Warnings without migration machinery are just noise.

## When To Use

- The user asks to deprecate, sunset, retire, decommission, replace, or remove a service, API family, library, platform, data product, or capability.
- A broad migration crosses many teams, repositories, services, clients, tenants, or runtime dependents.
- A large mechanical change needs staged execution, generated edits, ownership routing, and non-regression controls.
- New usage must be blocked while old usage is migrated away.

## When Not To Use

- The work is a routine dependency update, package bump, or small codemod; defer to `dependency-and-code-hygiene`.
- The work is API versioning for one service contract; defer to `api-design-and-compatibility` unless cross-system migration dominates.
- The work is database schema/backfill execution; defer to `database-operations`.
- The work is rollout sequencing for an already built change; defer to `progressive-delivery`.

## Inputs To Collect

- Deprecated thing, replacement, reason, owner, deadline, risk, and support window.
- Static references, runtime calls, traffic, tenants, clients, jobs, dashboards, alerts, docs, and third-party dependents.
- Migration path, compatibility layer, dual-read/write needs, validation checks, and rollback/escape hatch.
- Advisory versus compulsory policy, enforcement gates, exception process, and communication channel.
- Backsliding prevention: build rules, lint/static checks, visibility controls, review warnings, templates, and docs.
- Disable and removal checklist: feature gates, traffic cutoffs, dark traffic, jobs, support tools, snapshots/exports, code, config, data, credentials, alerts, dashboards, runbooks, costs, and access paths.

## Workflow

1. **Define the end state.** State what is being removed, what replaces it, what remains supported, and why the change is worth doing.
2. **Discover usage.** Combine code search, dependency graph, runtime telemetry, logs, ownership metadata, and consumer outreach.
3. **Classify dependents.** Separate easy mechanical users, risky dynamic users, abandoned owners, critical paths, and external clients.
4. **Choose migration mode.** Use advisory deprecation for low-risk nudges; use compulsory deadlines when ownership and enforcement exist.
5. **Provide paved migration.** Supply examples, compatibility shims, codemods, validation commands, and rollback/escape hatches.
6. **Prevent backsliding.** Block or warn on new usage through review-time checks, build visibility, templates, docs, and policy gates.
7. **Migrate incrementally.** Move dependents in batches small enough to review, test, and roll back; track progress with objective metrics.
8. **Disable before delete.** Stop or quarantine old runtime paths, watch for at least one representative business cycle, check dark traffic, jobs, support tools, and alerts, and keep an escape hatch until silence is proven.
9. **Retire completely.** Remove runtime paths, data, config, credentials, dashboards, alerts, runbooks, docs, and cost artifacts after usage reaches the removal gate; preserve required snapshots/exports with owner, retention, and disposal date.

## Synthesized Default

Treat deprecation as an engineered migration, not an announcement. Use centralized expertise for broad changes, automate repetitive edits, preserve compatibility while dependents move, enforce no-new-usage, and treat final decommissioning as a high-risk production deployment.

## Exceptions

- Emergency removal may skip normal windows when security or data-loss risk dominates, but needs explicit impact review and repair plan.
- External public clients may require longer overlap, stronger telemetry, and contractual support windows.
- Advisory deprecation is acceptable for low-risk cleanup when maintenance cost is small and no deadline is required.
- Abandoned dependents may require ownership escalation or replacement before removal.

## Response Quality Bar

- Lead with the migration plan, deprecation decision, usage inventory, or retirement blocker requested.
- Cover replacement readiness, usage measurement, dependent batching, no-new-usage controls, exception policy, disable-before-delete, and final cleanup before optional change-management breadth.
- Make recommendations actionable with owners, migration batches, validation checks, deadlines, stop criteria, escape hatches, and retirement evidence where relevant.
- State required evidence such as static references, runtime telemetry, dependent owners, replacement examples, block/warn controls, dark-traffic checks, and disposal records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineered migration and deprecation. Route architecture redesign or vulnerability emergency handling only when those are the central unresolved risk.
- Be concise: avoid generic program-management language and prefer compact inventories, migration batch tables, and retirement checklists.

## Required Outputs

- Deprecation decision record with owner, replacement, reason, and end state.
- Usage inventory with static and runtime evidence.
- Dependent classification and migration batches.
- Migration guide, examples, validation, and escape hatch.
- Backsliding prevention controls.
- Enforcement, exception, and deadline policy.
- Disable-before-delete plan with watch-window evidence and disposal handling.
- Final retirement checklist.

## Evidence Gates

- `usage_inventory`: static and runtime usage are measured, or blind spots are named.
- `replacement_ready`: replacement path is documented, supported, and validated for representative dependents.
- `migration_batches`: dependents are grouped into owned, reviewable, reversible batches.
- `backsliding_control`: new usage is blocked, warned, or explicitly exception-gated.
- `retirement_check`: disable-before-delete, watch-window, code, config, data, credentials, alerts, runbooks, docs, and cost artifacts are removed or retained with owner.

## Red Flags - Stop And Rework

- A deprecation warning has no replacement, owner, deadline, or telemetry.
- New users can still copy old examples and add fresh dependencies.
- Migration success is counted by emails sent rather than usage removed.
- Removal happens before dark traffic, jobs, support tools, and external clients are checked.
- The old system keeps alerts, credentials, and costs after "retirement".

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Announcing instead of migrating | Provide tooling, examples, and owned batches. |
| Relying only on static search | Add runtime telemetry for dynamic dependents. |
| Ignoring backsliding | Block new usage while old usage is removed. |
| Stopping at code deletion | Retire operational, data, access, and cost surfaces too. |
