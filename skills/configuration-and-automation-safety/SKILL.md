---
name: configuration-and-automation-safety
description: "Use before running a config change, bulk script, or automation that touches production state — to add validation, preview, blast-radius limits, and a recovery path."
---

# Configuration And Automation Safety

## Overview

Configuration and automation can change production faster than code review can notice.

**Core principle:** treat config, generated changes, and operational automation as production code with explicit schema, preview, owner, and recovery evidence.

## Iron Law

```
NO CONFIG OR AUTOMATION CHANGE WITHOUT VALIDATION, PREVIEW, BLAST RADIUS, OWNER, AND RECOVERY PATH
```

If the change cannot be checked before execution and reversed or contained after failure, it is not safe enough.

## When To Use

- The user asks about configuration safety, generated changes, operational scripts, bulk automation, feature settings, policy defaults, or config validation.
- A non-code change can alter routing, permissions, capacity, customer experience, data handling, or operational behavior.
- Automation creates, updates, deletes, migrates, or remediates production state.
- Configuration drift, copy-paste settings, or unreviewed overrides are causing incidents.

## When Not To Use

- The main question is production rollout sequencing; defer to `progressive-delivery`.
- The main question is declarative infrastructure, admission, or drift reconciliation; defer to `infrastructure-and-policy-as-code`.
- The main question is dependency cleanup or package updates; defer to `dependency-and-code-hygiene`.
- The request is one-off local scripting with no production or shared-state risk.

## Inputs To Collect

- Config or automation surface, owner, consumers, environments, and affected production state.
- Schema, allowed values, defaults, invariants, dependency ordering, and unsafe combinations.
- Change path, review path, preview or dry-run output, execution identity, and audit record.
- Blast radius, rollback or disable path, rate limit, lock, retry, and idempotency behavior.
- Prior incidents, drift reports, manual overrides, and exception process.

## Workflow

1. **Classify the surface.** Separate static config, dynamic config, generated changes, scheduled automation, and emergency automation.
2. **Define the contract.** Specify schema, defaults, bounds, invariants, ownership, and incompatible combinations.
3. **Validate before execution.** Require parse, semantic, dependency, permission, and environment checks before production use.
4. **Preview the effect.** Show intended creates, updates, deletes, traffic impact, permission changes, and affected owners before apply.
5. **Bound execution.** Use batches, locks, rate limits, stop criteria, and idempotency for automation that touches shared state.
6. **Make recovery concrete.** Define rollback, disable, restore, or roll-forward behavior for config, generated changes, and automation side effects.
7. **Control drift.** Detect unmanaged overrides and stale settings; decide reconcile, exception, or removal.
8. **Close with evidence.** Record owner, review, validation output, preview, execution result, and cleanup for temporary settings.

## Synthesized Default

Use typed config contracts, deterministic validation, effect preview, small execution batches, explicit owner approval, audit records, drift checks, and tested recovery paths. Automation should be idempotent by default and should fail closed when it cannot prove the intended target.

## Exceptions

- Emergency automation may run with reduced review when delay is riskier, but it still needs owner, audit, stop criteria, and post-change reconciliation.
- Low-risk local config can use lighter checks if it cannot affect shared systems, sensitive data, or production users.
- Some generated changes are easier to roll forward than roll back; document the recovery decision before execution.

## Response Quality Bar

- Lead with the safety decision, config contract, automation risk, or gate matrix requested.
- Cover validation, preview, blast radius, owner, execution controls, drift handling, and recovery before optional automation detail.
- Make recommendations actionable with owners, validation checks, stop criteria, batch size, audit evidence, and cleanup where relevant.
- State required evidence such as schema, preview output, owner approval, execution logs, drift reports, and rollback proof; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside config and automation safety. Route rollout, infrastructure policy, or dependency hygiene only when that surface owns the immediate risk.
- Be concise: prefer compact contract and gate tables over generic automation advice.

## Required Outputs

- Configuration or automation safety review.
- Contract: owner, schema, defaults, invariants, unsafe combinations, and allowed overrides.
- Validation and preview gate list.
- Blast-radius and execution-control plan.
- Recovery plan for rollback, disable, restore, or roll-forward.
- Drift detection and exception policy.
- Evidence checklist for review, execution, and cleanup.

## Evidence Gates

- `contract_defined`: owner, schema, defaults, bounds, and invariants are explicit.
- `preview_checked`: intended production effect is visible before execution.
- `blast_radius`: affected users, systems, data, and owners are bounded.
- `recovery_path`: rollback, disable, restore, or roll-forward path is defined.
- `audit_record`: review, validation, execution result, and exception state are traceable.

## Red Flags - Stop And Rework

- Configuration bypasses review because it is "not code."
- Automation can delete or mutate shared state without preview.
- Defaults differ by environment without a documented reason.
- Recovery depends on remembering the previous value manually.
- Temporary overrides have no owner or expiry.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Valid syntax as safety | Add semantic, dependency, and blast-radius checks. |
| One giant automation run | Use batches, locks, stop criteria, and idempotency. |
| Silent config drift | Detect, reconcile, or exception-gate unmanaged changes. |
| Rollback by memory | Record prior state and prove recovery. |
