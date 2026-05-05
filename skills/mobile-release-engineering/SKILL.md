---
name: mobile-release-engineering
description: "Use to plan a native mobile rollout — staged release, crash-free thresholds, startup, hang and offline behavior, segmented telemetry, kill switches, and forward-fix path."
---

# Mobile Release Engineering And Crash Budgets

## Iron Law

```
NO BROAD MOBILE ROLLOUT WITHOUT STABILITY BUDGETS, SEGMENTED TELEMETRY, HALT CRITERIA, AND FORWARD-FIX PLAN
```

If the release cannot be halted or repaired under app-store/client constraints, do not widen exposure.

## Overview

Mobile releases are hard to roll back, so stability gates must be conservative before broad rollout.

**Core principle:** use staged rollout, crash/hang budgets, device/OS segmentation, startup/offline checks, privacy-safe telemetry, and forward-fix plans.

## When To Use

- The user asks about native mobile release trains, staged rollout, phased release, crash-free users/sessions, hang rates, startup, offline behavior, mobile telemetry, or app-store release risk.
- A mobile app release could affect stability across devices, OS versions, networks, or app versions.
- A mobile rollout needs thresholds to continue, halt, or forward-fix.
- Client upgrade lag or rollback limits change release strategy.

## When Not To Use

- The request is responsive web or browser performance; defer to `web-release-gates`.
- The issue is backend-only latency or availability; defer to `performance-and-capacity` or `slo-and-error-budgets`.
- The work is mobile product strategy, acquisition, store listing optimization, or UX roadmap.
- The question is general CI gate policy without mobile release constraints; defer to `testing-and-quality-gates`.

## Inputs To Collect

- Platforms, release train, app versions, staged rollout percentages, and store review constraints.
- Stability metrics: crash-free users/sessions, hang rate, startup failures, fatal/non-fatal error rate, and watchdog events.
- Device/OS/app-version/network segmentation and known high-risk cohorts.
- Critical journeys, offline behavior, sync/data-loss risk, and backend compatibility.
- Telemetry fields, privacy controls, symbolication/deobfuscation, and alerting thresholds.
- Rollback, halt, kill switch, remote config, and forward-fix options.

## Workflow

1. **Define mobile SLIs.** Use crash-free users/sessions, hang rate, startup success, and critical journey success.
2. **Segment the rollout.** Gate by platform, app version, device class, OS version, geography/network, or cohort where risk warrants it.
3. **Set staged thresholds.** Define metrics and sample-size requirements for each widening step.
4. **Check compatibility.** Verify backend, API, schema, feature flag, and config compatibility with old and new app versions.
5. **Plan offline and sync behavior.** Test intermittent network, stale config, retry, conflict, and data-loss scenarios.
6. **Protect privacy.** Avoid sensitive data in crash reports, logs, breadcrumbs, and custom keys.
7. **Define halt/repair.** Decide when to halt rollout, disable features, revert server flags, or submit a forward fix.
8. **Monitor long tail.** Track old versions and slow adoption after the main rollout completes.

## Synthesized Default

Use staged mobile rollout with crash-free, hang, startup, and critical-journey budgets as release gates. Account for slow upgrade curves and limited rollback by keeping kill switches, compatibility windows, and forward-fix paths ready.

## Exceptions

- Emergency security or compliance fixes may move faster, but staged telemetry and rollback/forward-fix criteria still apply.
- Very small internal distributions can use lighter gates if users and devices are known.
- Some app-store constraints force forward-fix rather than rollback; document this before broad rollout.
- Privacy constraints may limit telemetry detail; preserve enough aggregate signal to detect regressions.

## Response Quality Bar

- Lead with the staged rollout decision, halt criteria, or stability budget requested.
- Cover crash-free, hangs, startup, critical journey, segmentation, and repair path before optional mobile release topics.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and forward-fix or kill-switch actions where relevant.
- State required evidence such as crash-free sessions/users, OS/device cohorts, sample sizes, app versions, and telemetry readiness; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside mobile release risk. Mention backend/API/config compatibility only where it affects client rollout safety.
- Be concise: avoid generic mobile-release background and prefer compact rollout tables.

## Required Outputs

- Mobile release train and staged rollout plan.
- Crash-free, hang, startup, and critical-journey budgets.
- Device/OS/app-version segmentation plan.
- Backend/API/config compatibility plan.
- Offline/sync test and telemetry plan.
- Halt, rollback, kill-switch, and forward-fix criteria.
- Privacy-safe mobile telemetry checklist.

## Evidence Gates

- `stability_budget`: crash-free, hang, startup, and critical journey thresholds are defined.
- `segment_check`: device, OS, app version, and network/cohort segmentation is considered.
- `compatibility_check`: backend, API, config, and old-version compatibility are addressed.
- `halt_fix_check`: rollout halt, kill switch, rollback, or forward-fix path is explicit.
- `privacy_check`: crash/log telemetry avoids sensitive data and has symbolication/debuggability path.

## Red Flags - Stop And Rework

- Release goes to 100 percent before stability metrics have sample size.
- Only aggregate crash rate is watched; device/OS cohorts are ignored.
- Backend changes break older app versions.
- Crash reports include sensitive data.
- Rollback is assumed even though client distribution cannot force downgrade.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating mobile like web deploys | Account for store review, upgrade lag, and rollback limits. |
| Aggregate stability only | Segment by platform, device, OS, app version, and cohort. |
| Ignoring offline | Test sync, retry, stale config, and conflict behavior. |
| No forward-fix plan | Prepare kill switches, server flags, and patched release path. |
