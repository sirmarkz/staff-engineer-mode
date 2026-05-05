---
name: progressive-delivery
description: "Use to plan a rollout — staged exposure, canary metrics, stop criteria, rollback or forward-fix path — for any change that affects production behavior, config, schema, data, or clients."
---

# Progressive Delivery And Safe Change

## Overview

Produces a staged rollout plan with named blast radius per stage, predeclared canary metrics with baseline and observation windows, stop and rollback criteria, and a cleanup owner for every temporary flag or compatibility path. Refuses rollouts whose rollback only reverts code while config, schema, data, or clients stay forward.

**Core principle:** treat code, configuration, flags, schemas, data, infrastructure, and model artifacts as production changes with the same blast-radius discipline.

## Iron Law

```
NO PRODUCTION CHANGE WITHOUT A BLAST RADIUS, STOP CRITERIA, AND RECOVERY PATH
```

If the rollout cannot be stopped or reversed when evidence degrades, it is not safe delivery.

## When To Use

- The user asks how to roll out, rollback, canary, phase, stage, gate, migrate, or release a change.
- A change involves configuration, feature flags, schema/data migration, dependency update, model change, infrastructure change, or client-visible behavior.
- The user asks how to reduce production risk from deployments or release trains.
- PRR or launch evidence needs rollout, rollback, and canary details.

## When Not To Use

- A live incident needs immediate command and mitigation; route to `incident-response-and-postmortems` first.
- The question is only code review or merge gates; defer to `testing-and-quality-gates` or `code-review-and-workflow`.
- The question is build systems, release branches, packaging, or reproducible artifacts; defer to `release-build-reproducibility`.
- The main risk is database lock/backfill execution; defer to `database-operations` for that detail and use this skill for rollout sequencing.
- The request is product launch messaging or marketing; out of scope.

## Inputs To Collect

- Change type, owner, affected users, blast radius, tier, and reversibility.
- Artifact identity and promotion path from build to environments.
- Rollout unit: ring, cohort, cell, zone, region, tenant, percentage, device group, or internal-only group.
- Canary metrics: SLO symptoms, errors, latency, saturation, correctness, business invariants, and guardrail signals.
- Rollback or forward-fix path for code, config, flags, schema, data, and clients.
- Feature-flag lifecycle, config validation, migration steps, cleanup owner, and expiry.
- Observability markers, dashboards, alerts, incident path, and communication expectations.

## Workflow

1. **Classify the change.** Separate code, config, flag, schema, data, infrastructure, dependency, model, and client components; each can fail differently.
2. **Bound the blast radius.** Pick the smallest rollout unit that still gives signal. State who or what can be affected at each stage.
3. **Promote one artifact.** Build once and promote the same artifact or immutable change set through stages.
4. **Define compatibility.** Ensure old and new versions can coexist across clients, services, data, and messages during rollout.
5. **Stage stateful changes.** Keep reader/writer compatibility across at least one-version skew; use expand/contract, dual-read/dual-write, delayed cleanup, and explicit schema/data ordering when state is involved.
6. **Choose canary gates.** Select metrics before release. Include user-visible symptoms and correctness, not only process health. Each gate needs a baseline window, minimum observation window, and enough exposed traffic or an alternate signal such as synthetic probes, extended bake time, or manual verification.
7. **Gate each exposure step.** Move through rings, cohorts, cells, stamps, zones, or regions only after health evidence says the previous step is safe.
8. **Set stop and rollback rules.** Define thresholds, who can halt, how rollback works, and when forward-fix is safer.
9. **Handle forward-fix-only surfaces.** If rollback is structurally impossible, require a server-side kill switch or disable path, staged adoption metric, hotfix lane, and explicit owner approval before first exposure.
10. **Handle non-code changes as first class.** Validate config, stage flags, throttle migrations, and delay destructive cleanup.
11. **Keep emergency flow familiar.** Hotfixes may move faster, but should use the same artifact identity, review, health gates, and traceable branch/change workflow where practical.
12. **Close the loop.** Record rollout evidence, remove temporary flags/paths, and update standards if the rollout found a new class of risk.

## Synthesized Default

Use build-once promotion, progressive exposure, predeclared health and canary metrics, automated or explicit stop criteria, reversible changes, and cleanup ownership. Prefer compatibility and expand/contract patterns over big-bang cutovers. Treat deploy, exposure, and customer-visible release as separate control points.

## Exceptions

- Emergency fixes may use a narrower or faster rollout when waiting is riskier than release, but stop criteria and owner still apply.
- Some destructive data changes cannot be rolled back; they require backup/restore evidence, delayed cleanup, and forward-fix criteria.
- Low-risk internal changes may use lighter gates if blast radius and owner acceptance are explicit.
- Client releases with slow adoption may require forward-fix and kill-switch strategy rather than true rollback.
- Temporary experiment flags should expire within about 90 days by default; long-lived operational kill switches need an owner, review cadence, and removal or renewal decision.

## Response Quality Bar

- Lead with the rollout plan, halt criteria, rollback path, or exposure decision requested.
- Cover blast radius, artifact identity, canary metrics, compatibility, feature/config lifecycle, migration safety, and cleanup before optional delivery topics.
- Make recommendations actionable with owners, stage thresholds, windows, stop criteria, rollback or forward-fix actions, and cleanup expiry where relevant.
- State required evidence such as artifact IDs, deploy markers, canary baselines, SLO/error signals, migration checks, rollback proof, and flag inventory; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside progressive exposure and safe change. Route build reproducibility, API compatibility, or data migration depth only when they materially block rollout safety.
- Be concise: avoid generic CD background and prefer compact rollout, metric, and rollback tables.

## Required Outputs

- Rollout plan with stages, blast radius, owner, and schedule.
- Canary metric set with thresholds, baseline window, observation window, minimum signal, and expected behavior.
- Stop, rollback, and forward-fix criteria.
- Compatibility plan for old/new code, clients, data, messages, config, and stateful reader/writer skew.
- Feature flag/config lifecycle plan with owner and expiry.
- Migration and cleanup plan for temporary paths or data structures.
- Verification commands or evidence links for each gate.

## Evidence Gates

- `blast_radius`: every rollout stage names affected users/systems and maximum impact.
- `artifact_identity`: the release identifies the artifact/change set and promotion path.
- `canary_criteria`: canary metrics, thresholds, windows, and stop rules are defined before rollout.
- `rollback_path`: rollback or forward-fix path is tested, rehearsed, or explicitly exempted with owner approval.
- `cleanup_owner`: temporary flags, configs, compatibility paths, and migration leftovers have owner and expiry.

## Red Flags - Stop And Rework

- Rollback means "revert the PR" while config, data, schema, or clients are not reversible.
- Canary metrics are picked after the rollout begins.
- Feature flags have no removal plan.
- Configuration changes bypass review or staged rollout.
- Destructive cleanup happens in the same step as first exposure.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating deploy and release as the same thing | Deploy safely first; expose behavior progressively. |
| Only measuring service health | Include user symptoms and correctness invariants. |
| Ignoring config | Validate, stage, and roll back config as carefully as code. |
| Forgetting cleanup | Track temporary flags and compatibility paths to removal. |
