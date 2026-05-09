---
name: dependency-and-code-hygiene
description: "Use when dependency updates, dead-code removal, lockfile sweeps, codemods, or static-analysis ratchets need planning"
---

# Dependency Hygiene And Code Health

## Iron Law

```
NO MAINTENANCE CHANGE WITHOUT SCOPE, REVERSIBILITY, AND NON-REGRESSION CHECKS
```

If a cleanup cannot be reviewed, tested, rolled back, or bounded, it is not hygiene; it is uncontrolled refactoring.

## Overview

Code health is maintained by routine, reversible, low-drama maintenance, not by occasional heroic cleanup.

**Core principle:** keep dependencies, static findings, dead code, and refactors in small maintained batches with rollback, verification, and non-regression rules.

## When To Use

- The user asks about dependency updates, lockfiles, package deprecations, stale libraries, dead code, static-analysis backlog, codemods, or cleanup.
- You need a recurring maintenance policy that does not block feature delivery.
- Existing warnings or findings need a ratchet so new debt is prevented while old debt is reduced.
- A mechanical refactor or dead-code removal needs safe execution.

## When Not To Use

- The main topic is build provenance, artifact signing, dependency inventory, builder isolation, or deployment admission; use `software-supply-chain-security` instead.
- The issue is an actively exploitable deployed vulnerability with SLA; use `vulnerability-management` instead.
- The refactor changes architecture boundaries; use `architecture-decisions` instead.
- The question is broad CI gate strategy (test selection, coverage, mutation); use `testing-and-quality-gates` instead. Dependency-vulnerability scanning at PR/release time with a severity-blocking threshold remains in scope here.

## Inputs To Collect

- Dependency inventory, direct/transitive responsibility, lockfiles, update cadence, and deprecated packages.
- Current vulnerable or outdated dependencies, runtime exposure, and patch urgency.
- Static-analysis findings, warning budgets, suppression policy, and existing baseline.
- Dead code candidates, usage telemetry, responsibility, and rollback plan.
- Codemod/refactor scope, generated changes, test coverage, and review strategy.
- Release process, canary options, and rollback capability for maintenance changes.

## Workflow

1. **Classify the work.** Separate routine updates, urgent patches, deprecations, static findings, dead code, codemods, and architecture-changing refactors.
2. **Batch conservatively.** Keep updates small enough to review and roll back; separate risky runtime dependencies from safe dev-only updates.
3. **Preserve reproducibility.** Update lockfiles or equivalent pinned inputs intentionally and review transitive changes.
4. **Use risk-aware cadence.** Apply routine updates regularly; keep enough dependency inventory to identify affected deployed artifacts; treat active vulnerabilities as vulnerability-management work.
5. **Ratchet legacy findings.** Prevent new high-severity findings while gradually reducing the baseline.
6. **Prove dead code is dead.** Use references, telemetry, responsibility confirmation, and staged deletion where risk is real.
7. **Execute codemods safely.** Review the pattern, sample output, affected responsibility, and validation evidence before broad application.
8. **Route trust controls.** If provenance, signing, or build trust becomes central, switch to supply-chain security.

## Synthesized Default

Use continuous small-batch maintenance with pinned inputs, dependency inventory, automated update proposals, reviewable diffs, static-analysis ratchets, and reversible codemods. Treat routine hygiene separately from supply-chain integrity and deployed vulnerability remediation.

## Exceptions

- Emergency security updates can bypass normal batching when active exploitation risk dominates; record follow-up cleanup.
- Large mechanical codemods are acceptable when the pattern is reviewed, output is sampled, and validation is automated.
- Abandoned packages may require migration planning rather than direct update.
- Dead-code deletion in rarely used paths may require staged disablement before removal.

## Response Quality Bar

- Lead with the maintenance plan, risk classification, or rollback-safe execution path requested.
- Cover scope, reversibility, pinned inputs, ratchets, dead-code evidence, codemod validation, and scope boundaries before optional hygiene topics.
- Make recommendations actionable with batches, validation commands, non-regression gates, stop criteria, and rollback or staged-disable steps where relevant.
- State required evidence such as dependency inventory, lockfile diffs, transitive changes, static baselines, usage telemetry, and sample codemod output; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside dependency hygiene and code health. Route provenance/signing or actively exploited vulnerabilities only when they are the primary issue.
- Be concise: avoid generic cleanup advice and prefer compact batch plans, ratchet tables, and validation checklists.

## Required Outputs

- Dependency update policy and cadence.
- Dependency-vulnerability scan integrated into PR/release CI, with the severity threshold that blocks merge or promotion.
- Lockfile or pinned-input review policy.
- Deprecated package and migration plan.
- Static-analysis backlog ratchet and suppression policy.
- Dead-code cleanup plan with evidence and rollback.
- Codemod/refactor plan with scope, validation, and responsibility.
- Selection rules to vulnerability management or supply-chain security.

## Evidence Gates

- `scope_check`: maintenance work is classified and bounded.
- `reversibility_check`: update, cleanup, or codemod has rollback or staged disablement plan.
- `lockfile_check`: pinned input changes are reviewed intentionally.
- `ratchet_check`: legacy findings have non-regression rule and reduction step.
- `route_check`: provenance/signing/dependency-inventory and deployed vulnerability work are routed to the correct specialist.

## Red Flags - Stop And Rework

- A huge dependency bump mixes runtime libraries, toolchain changes, and unrelated refactors.
- Lockfile changes are treated as noise.
- Static-analysis warnings are either all ignored or all made blocking overnight.
- Dead code is removed without checking dynamic use, responsibility, or rollback.
- Routine dependency hygiene is confused with artifact provenance or signing.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Big-bang cleanup | Use small batches and ratchets. |
| Treating all dependencies alike | Separate runtime, build-time, test-only, and transitive risk. |
| Blind codemods | Review the transform, sample output, responsibility, and validation. |
| Suppression sprawl | Require reason, expiry, or baseline rule. |
