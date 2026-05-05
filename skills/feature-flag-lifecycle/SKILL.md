---
name: feature-flag-lifecycle
description: "Use to audit and retire feature flags after rollout — assign owner and expiry per flag, detect orphans, plan removal with rollback, and score the flag debt. Not for in-flight rollout sequencing; that is progressive-delivery."
---

# Feature Flag Lifecycle

## Iron Law

```
EVERY LIVE FLAG HAS AN OWNER, AN EXPIRY, AND A REMOVAL PLAN
```

A flag without all three is orphan debt. Orphan flags become dead branches, contradictory defaults, and stale kill switches that nobody dares pull during an incident.

## Overview

Produces a flag inventory with category, owner, and expiry per flag, an orphan report for flags whose owners or features no longer exist, and a removal plan with rollback for each retiring flag. Refuses to count a feature as shipped while a flag still gates it.

**Core principle:** every live flag is unfinished work. After a rollout completes, the flag, its branches, and its config rows are decision debt that compounds until someone explicitly removes them.

## When To Use

- The user asks to audit, inventory, classify, retire, clean up, or sunset feature flags.
- A rollout has completed and the flag that gated it is still live.
- An incident exposed a flag whose intended behavior nobody currently owns.
- A team asks how to stop accumulating flag debt or how to set expiry policy per flag class.
- The agent is being asked to add a new flag and the existing flag inventory and removal pattern need to be checked first.
- A code search reveals branches gated by flags that were not declared in any registry or are not referenced from production config.

## When Not To Use

- A change is mid-rollout and the question is staging, exposure rings, canary metrics, stop criteria, or rollback; use `progressive-delivery`.
- A flag itself is being changed as a configuration value with safety implications; use `configuration-and-automation-safety`.
- Generic dead-code or dependency cleanup with no flag-specific gating; use `dependency-and-code-hygiene`.
- The flag is an A/B experiment treatment under active analysis; use `experimentation-and-metric-guardrails`.
- The change is an org-level policy for AI-assisted code that adds flags it never removes; use `ai-coding-governance`.
- The work is broad release readiness across multiple surfaces; use `production-readiness-review`.

## Inputs To Collect

- Flag inventory source: code search, flag-service registry, config files, environment overrides, and any per-tenant or per-region overrides.
- Per-flag metadata: name, declaration site, default value, current production value per environment, last evaluation timestamp where available, and number of branches gated.
- Stated category for each flag: release toggle, experiment, operational kill switch, or permission/entitlement.
- Owner of record per flag, owning team, escalation path, and decision authority for removal.
- Expiry policy by category and whether the flag has exceeded it.
- Rollout state: was the flag's launch completed, partially shipped, abandoned, or still ramping.
- Failure behavior: local fallback/default value used if flag evaluation fails, the behavior selected during a flag-service outage, and whether that behavior is safe for production.
- Branch coverage: which code paths execute under each value, whether both branches still have callers, and whether any tests exercise both branches.
- Tenants, regions, cohorts, or accounts pinned to non-default values and the reason for each pin.
- Incident history involving the flag, including any time the kill-switch path was exercised.

## Workflow

1. **Build the inventory.** Reconcile flags discovered in code, in the flag service or config registry, and in environment overrides. A flag that exists in only one of those sources is the first orphan signal.
2. **Classify each flag.** Assign exactly one category: release toggle (turns a shipped feature on), experiment (assigns variants for measurement), operational kill switch (disables a path under load or failure), permission or entitlement (gates access by tenant, plan, or role). A flag that resists classification is itself a finding.
3. **Assign owner and expiry by category.** Release toggles default to short expiry tied to rollout completion. Experiment flags default to short expiry tied to readout date. Operational kill switches default to longer expiry but require named owner and review cadence. Permission flags may be long-lived but still need owner and review.
4. **Check default-value safety.** Record the local default/fallback value for each flag and the behavior chosen if flag evaluation or the flag service is unavailable. The fallback should select the safest known production behavior, not an accidental SDK or config default.
5. **Check rollout completion.** For each release toggle, confirm the rollout finished, the chosen value is the production default everywhere, and no environment still pins the legacy value without a documented reason.
6. **Detect orphans.** Flag the following as orphans: declared in code but absent from the registry; present in registry but unreferenced in code; owner left the team or no owner recorded; expiry exceeded with no removal action; both branches identical or one branch unreachable; not evaluated in production within a defined freshness window where evaluation telemetry exists.
7. **Map flag-driven branches.** For each retiring flag, list the call sites, the branch each value selects, the tests that exercise each branch, and any config rows or per-tenant overrides that depend on the flag name.
8. **Plan removal.** For each flag scheduled for removal, define: target value (the branch that stays), the order of cleanup (default flip, override sweep, code removal, registry removal, config-row removal), the rollback path if removal regresses behavior, and the verification step that proves no caller still selects the removed branch.
9. **Stage the removal as a change.** Treat flag removal as a production change with its own blast radius and rollback. Hand off rollout sequencing to `progressive-delivery` when removal touches a tier-critical path.
10. **Score the flag debt.** Produce a scorecard: total flags by category, percent past expiry, percent without owner, orphan count, oldest live flag age, and removal velocity over the last review period.
11. **Set the standing rule.** Establish per-category expiry defaults, a recurring review cadence, and the rule that adding a new flag requires declaring its category, owner, expiry, and safe fallback value at creation time.

## Synthesized Default

Treat flags as time-bounded. Release toggles expire when the rollout completes. Experiment flags expire when the readout is signed off. Operational kill switches and permission flags may live longer but still require named owner and recurring review. Removal is a planned change, not a cleanup ticket. The inventory is the source of truth and is reconciled against code on a defined cadence. Every flag must also document its fallback/default value and what production behavior occurs if flag evaluation fails.

## Exceptions

- Long-lived operational kill switches may exceed standard expiry if the owner reviews them on a recorded cadence and the disabled path is rehearsed.
- Permission or entitlement flags tied to billing, plan, or regulatory access may be effectively permanent; they are not orphans but still need owner and review.
- A flag protecting an in-progress migration may stay past its initial expiry with a renewed expiry date and a named completion owner.
- Emergency kill switches added during an incident may bypass the create-time expiry rule but must be classified, owned, dated, and assigned a safe fallback value within the postmortem follow-up.

## Response Quality Bar

- Lead with the flag inventory, orphan list, removal plan, or flag-debt scorecard requested.
- Cover classification, ownership, expiry, default-value safety, branch mapping, removal sequencing, and rollback before optional flag-system breadth.
- Make recommendations actionable with per-flag owner, expiry, target value, fallback/default value, outage behavior, removal step, rollback step, and verification evidence.
- State required evidence such as code-search results, flag-registry export, environment overrides, evaluation telemetry where available, and incident history; do not claim flag state from prose alone.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside post-rollout flag lifecycle. Route in-flight rollout sequencing, generic dead-code cleanup, experiment analysis, and config-change safety to the owning specialist.
- Be concise: prefer compact inventory and removal tables over running narrative about flag philosophy.

## Required Outputs

- Flag inventory with name, category, declaration site, owner, expiry, current production value per environment, fallback/default value if evaluation fails, outage behavior, and branch count.
- Orphan report listing flags with missing owner, missing classification, exceeded expiry, unsafe or undocumented fallback, identical branches, unreachable branch, registry/code mismatch, or stale evaluation.
- Per-flag removal plan with target value, cleanup order, rollback path, and verification step for each flag scheduled for removal.
- Per-tenant, per-region, or per-cohort override list with reason and removal owner for each non-default pin.
- Branch map per retiring flag covering call sites, tests per branch, and dependent config rows.
- Flag-debt scorecard with totals by category, percent past expiry, percent without owner, orphan count, oldest live flag age, and removal velocity.
- Standing policy: per-category expiry defaults, review cadence, and the create-time owner/expiry/category/safe-fallback rule.
- Follow-up routes to progressive delivery, configuration safety, dependency hygiene, or experimentation as needed.

## Evidence Gates

- `flag_inventory_present`: a single inventory reconciles flags found in code, in the registry, and in environment overrides; mismatches are listed.
- `category_assigned`: every live flag has exactly one category from release, experiment, operational kill switch, or permission.
- `owner_and_expiry`: every live flag has a named owner and a dated expiry; any exception is recorded with renewed date and reason.
- `default_value_safety`: every live flag records the fallback/default value used when evaluation fails and the production behavior during a flag-service outage.
- `orphan_report`: orphan criteria are evaluated and the resulting flags are listed with the matching criterion per flag.
- `removal_plan_per_retiring_flag`: each flag scheduled for removal has target value, cleanup order, rollback path, and verification step.
- `branch_map`: retiring flags have a call-site list and a per-branch test list; unreachable or untested branches are flagged.
- `debt_scorecard`: scorecard covers totals by category, percent past expiry, percent without owner, orphan count, oldest live flag age, and removal velocity.

## Red Flags - Stop And Rework

- A flag has no recorded owner and no expiry, and the team treats this as normal.
- A flag has no documented fallback/default value, so a flag-service outage could silently choose the wrong behavior.
- The rollout that created a flag completed months ago but the legacy branch still has callers and the flag is still evaluated in production.
- The flag registry and the code disagree about which flags exist, and nobody owns reconciliation.
- An operational kill switch has never been exercised and no rehearsal exists, so its real behavior is unknown.
- Both branches of a flag are identical or one branch is unreachable, and the flag is still evaluated.
- A flag is removed by deleting code without sweeping per-tenant overrides, registry rows, or environment pins.
- New flags are being added by AI coding agents without recording category, owner, expiry, or safe fallback at creation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating "the rollout finished" as cleanup | Removal is a separate planned change with rollback and verification. |
| One global flag bucket | Classify by release, experiment, operational, or permission; each has a different lifecycle. |
| Owner is "the team" | Record a named individual or rotation with decision authority. |
| Counting flags only in code | Reconcile code, registry, and environment overrides; mismatches are orphans. |
| Ignoring flag-evaluation failure | Record the fallback/default value and confirm outage behavior is safe. |
| Removing the code path but leaving the flag | Sweep registry rows, overrides, and dependent config in the same change. |
| Letting kill switches drift untested | Rehearse the disabled path or downgrade the switch to documented inert. |
| Adding new flags faster than removing them | Track removal velocity in the scorecard and gate new-flag creation on declared expiry. |
---
name: feature-flag-lifecycle
description: "Use to audit and retire feature flags after rollout — assign owner and expiry per flag, detect orphans, plan removal with rollback, and score the flag debt. Not for in-flight rollout sequencing; that is progressive-delivery."
---

# Feature Flag Lifecycle

## Overview

Produces a flag inventory with category, owner, and expiry per flag, an orphan report for flags whose owners or features no longer exist, and a removal plan with rollback for each retiring flag. Refuses to count a feature as shipped while a flag still gates it.

**Core principle:** every live flag is unfinished work. After a rollout completes, the flag, its branches, and its config rows are decision debt that compounds until someone explicitly removes them.

## Iron Law

```
EVERY LIVE FLAG HAS AN OWNER, AN EXPIRY, AND A REMOVAL PLAN
```

A flag without all three is orphan debt. Orphan flags become dead branches, contradictory defaults, and stale kill switches that nobody dares pull during an incident.

## When To Use

- The user asks to audit, inventory, classify, retire, clean up, or sunset feature flags.
- A rollout has completed and the flag that gated it is still live.
- An incident exposed a flag whose intended behavior nobody currently owns.
- A team asks how to stop accumulating flag debt or how to set expiry policy per flag class.
- The agent is being asked to add a new flag and the existing flag inventory and removal pattern need to be checked first.
- A code search reveals branches gated by flags that were not declared in any registry or are not referenced from production config.

## When Not To Use

- A change is mid-rollout and the question is staging, exposure rings, canary metrics, stop criteria, or rollback; use `progressive-delivery`.
- A flag itself is being changed as a configuration value with safety implications; use `configuration-and-automation-safety`.
- Generic dead-code or dependency cleanup with no flag-specific gating; use `dependency-and-code-hygiene`.
- The flag is an A/B experiment treatment under active analysis; use `experimentation-and-metric-guardrails`.
- The change is an org-level policy for AI-assisted code that adds flags it never removes; use `ai-coding-governance`.
- The work is broad release readiness across multiple surfaces; use `production-readiness-review`.

## Inputs To Collect

- Flag inventory source: code search, flag-service registry, config files, environment overrides, and any per-tenant or per-region overrides.
- Per-flag metadata: name, declaration site, default value, current production value per environment, last evaluation timestamp where available, and number of branches gated.
- Stated category for each flag: release toggle, experiment, operational kill switch, or permission/entitlement.
- Owner of record per flag, owning team, escalation path, and decision authority for removal.
- Expiry policy by category and whether the flag has exceeded it.
- Rollout state: was the flag's launch completed, partially shipped, abandoned, or still ramping.
- Failure behavior: local fallback/default value used if flag evaluation fails, the behavior selected during a flag-service outage, and whether that behavior is safe for production.
- Branch coverage: which code paths execute under each value, whether both branches still have callers, and whether any tests exercise both branches.
- Tenants, regions, cohorts, or accounts pinned to non-default values and the reason for each pin.
- Incident history involving the flag, including any time the kill-switch path was exercised.

## Workflow

1. **Build the inventory.** Reconcile flags discovered in code, in the flag service or config registry, and in environment overrides. A flag that exists in only one of those sources is the first orphan signal.
2. **Classify each flag.** Assign exactly one category: release toggle (turns a shipped feature on), experiment (assigns variants for measurement), operational kill switch (disables a path under load or failure), permission or entitlement (gates access by tenant, plan, or role). A flag that resists classification is itself a finding.
3. **Assign owner and expiry by category.** Release toggles default to short expiry tied to rollout completion. Experiment flags default to short expiry tied to readout date. Operational kill switches default to longer expiry but require named owner and review cadence. Permission flags may be long-lived but still need owner and review.
4. **Check default-value safety.** Record the local default/fallback value for each flag and the behavior chosen if flag evaluation or the flag service is unavailable. The fallback should select the safest known production behavior, not an accidental SDK or config default.
5. **Check rollout completion.** For each release toggle, confirm the rollout finished, the chosen value is the production default everywhere, and no environment still pins the legacy value without a documented reason.
6. **Detect orphans.** Flag the following as orphans: declared in code but absent from the registry; present in registry but unreferenced in code; owner left the team or no owner recorded; expiry exceeded with no removal action; both branches identical or one branch unreachable; not evaluated in production within a defined freshness window where evaluation telemetry exists.
7. **Map flag-driven branches.** For each retiring flag, list the call sites, the branch each value selects, the tests that exercise each branch, and any config rows or per-tenant overrides that depend on the flag name.
8. **Plan removal.** For each flag scheduled for removal, define: target value (the branch that stays), the order of cleanup (default flip, override sweep, code removal, registry removal, config-row removal), the rollback path if removal regresses behavior, and the verification step that proves no caller still selects the removed branch.
9. **Stage the removal as a change.** Treat flag removal as a production change with its own blast radius and rollback. Hand off rollout sequencing to `progressive-delivery` when removal touches a tier-critical path.
10. **Score the flag debt.** Produce a scorecard: total flags by category, percent past expiry, percent without owner, orphan count, oldest live flag age, and removal velocity over the last review period.
11. **Set the standing rule.** Establish per-category expiry defaults, a recurring review cadence, and the rule that adding a new flag requires declaring its category, owner, expiry, and safe fallback value at creation time.

## Synthesized Default

Treat flags as time-bounded. Release toggles expire when the rollout completes. Experiment flags expire when the readout is signed off. Operational kill switches and permission flags may live longer but still require named owner and recurring review. Removal is a planned change, not a cleanup ticket. The inventory is the source of truth and is reconciled against code on a defined cadence. Every flag must also document its fallback/default value and what production behavior occurs if flag evaluation fails.

## Exceptions

- Long-lived operational kill switches may exceed standard expiry if the owner reviews them on a recorded cadence and the disabled path is rehearsed.
- Permission or entitlement flags tied to billing, plan, or regulatory access may be effectively permanent; they are not orphans but still need owner and review.
- A flag protecting an in-progress migration may stay past its initial expiry with a renewed expiry date and a named completion owner.
- Emergency kill switches added during an incident may bypass the create-time expiry rule but must be classified, owned, dated, and assigned a safe fallback value within the postmortem follow-up.

## Response Quality Bar

- Lead with the flag inventory, orphan list, removal plan, or flag-debt scorecard requested.
- Cover classification, ownership, expiry, default-value safety, branch mapping, removal sequencing, and rollback before optional flag-system breadth.
- Make recommendations actionable with per-flag owner, expiry, target value, fallback/default value, outage behavior, removal step, rollback step, and verification evidence.
- State required evidence such as code-search results, flag-registry export, environment overrides, evaluation telemetry where available, and incident history; do not claim flag state from prose alone.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside post-rollout flag lifecycle. Route in-flight rollout sequencing, generic dead-code cleanup, experiment analysis, and config-change safety to the owning specialist.
- Be concise: prefer compact inventory and removal tables over running narrative about flag philosophy.

## Required Outputs

- Flag inventory with name, category, declaration site, owner, expiry, current production value per environment, fallback/default value if evaluation fails, outage behavior, and branch count.
- Orphan report listing flags with missing owner, missing classification, exceeded expiry, unsafe or undocumented fallback, identical branches, unreachable branch, registry/code mismatch, or stale evaluation.
- Per-flag removal plan with target value, cleanup order, rollback path, and verification step for each flag scheduled for removal.
- Per-tenant, per-region, or per-cohort override list with reason and removal owner for each non-default pin.
- Branch map per retiring flag covering call sites, tests per branch, and dependent config rows.
- Flag-debt scorecard with totals by category, percent past expiry, percent without owner, orphan count, oldest live flag age, and removal velocity.
- Standing policy: per-category expiry defaults, review cadence, and the create-time owner/expiry/category/safe-fallback rule.
- Follow-up routes to progressive delivery, configuration safety, dependency hygiene, or experimentation as needed.

## Evidence Gates

- `flag_inventory_present`: a single inventory reconciles flags found in code, in the registry, and in environment overrides; mismatches are listed.
- `category_assigned`: every live flag has exactly one category from release, experiment, operational kill switch, or permission.
- `owner_and_expiry`: every live flag has a named owner and a dated expiry; any exception is recorded with renewed date and reason.
- `default_value_safety`: every live flag records the fallback/default value used when evaluation fails and the production behavior during a flag-service outage.
- `orphan_report`: orphan criteria are evaluated and the resulting flags are listed with the matching criterion per flag.
- `removal_plan_per_retiring_flag`: each flag scheduled for removal has target value, cleanup order, rollback path, and verification step.
- `branch_map`: retiring flags have a call-site list and a per-branch test list; unreachable or untested branches are flagged.
- `debt_scorecard`: scorecard covers totals by category, percent past expiry, percent without owner, orphan count, oldest live flag age, and removal velocity.

## Red Flags - Stop And Rework

- A flag has no recorded owner and no expiry, and the team treats this as normal.
- A flag has no documented fallback/default value, so a flag-service outage could silently choose the wrong behavior.
- The rollout that created a flag completed months ago but the legacy branch still has callers and the flag is still evaluated in production.
- The flag registry and the code disagree about which flags exist, and nobody owns reconciliation.
- An operational kill switch has never been exercised and no rehearsal exists, so its real behavior is unknown.
- Both branches of a flag are identical or one branch is unreachable, and the flag is still evaluated.
- A flag is removed by deleting code without sweeping per-tenant overrides, registry rows, or environment pins.
- New flags are being added by AI coding agents without recording category, owner, expiry, or safe fallback at creation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating "the rollout finished" as cleanup | Removal is a separate planned change with rollback and verification. |
| One global flag bucket | Classify by release, experiment, operational, or permission; each has a different lifecycle. |
| Owner is "the team" | Record a named individual or rotation with decision authority. |
| Counting flags only in code | Reconcile code, registry, and environment overrides; mismatches are orphans. |
| Ignoring flag-evaluation failure | Record the fallback/default value and confirm outage behavior is safe. |
| Removing the code path but leaving the flag | Sweep registry rows, overrides, and dependent config in the same change. |
| Letting kill switches drift untested | Rehearse the disabled path or downgrade the switch to documented inert. |
| Adding new flags faster than removing them | Track removal velocity in the scorecard and gate new-flag creation on declared expiry. |
