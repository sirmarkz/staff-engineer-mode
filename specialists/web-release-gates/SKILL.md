---
name: web-release-gates
description: "Use when browser releases need loading, interaction, layout stability, runtime errors, telemetry, budgets, or gates"
---

# Frontend Performance Release Gates

## Iron Law

```
NO CLIENT RELEASE GATE WITHOUT USER-CENTRIC METRICS, JOURNEY BUDGETS, FIELD/LAB SIGNALS, AND ROLLBACK CRITERIA
```

If a release can make the client experience worse without tripping a gate, the gate is incomplete.

## Overview

Client-side quality is production reliability for the user's device and network.

**Core principle:** gate client-facing releases on field-user experience, journey-level budgets, runtime errors, and accessibility smoke checks, not only build success.

## When To Use

- A browser-delivered or client-rendered change can affect user-perceived loading, interaction readiness, visual stability, runtime errors, payload weight, or client-side release safety.
- You need release thresholds for routes, screens, or user journeys.
- Field-user telemetry, lab checks, deploy markers, feature flags, or automated accessibility smoke checks are needed to stop client regressions from shipping.

## When Not To Use

- The request is product UX strategy, visual design, SEO strategy, or broad accessibility-program management.
- Backend latency is the only issue and client user experience is not central; use `performance-and-capacity` instead.
- The request is general CI gate policy; use `testing-and-quality-gates` instead.
- The issue is mobile native release stability; use `mobile-release-engineering` instead.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Critical routes, screens, journeys, user segments, devices, network classes, and supported clients.
- Field metrics: user-perceived loading, interaction readiness, visual stability, runtime errors, and journey-level latency.
- Lab metrics: payload weight, critical path work, client initialization or rendering cost, dependency weight, and synthetic checks.
- Current budgets, deploy markers, feature flags, rollout controls, and rollback path.
- Accessibility smoke checks that can be automated reliably.
- Privacy constraints for real-user monitoring and error collection.

## Workflow

1. **Pick user journeys and routes.** Gate what users actually experience, not only the application shell.
2. **Set budgets.** Define journey-level payload, dependency, critical path, rendering, and interaction budgets.
3. **Use field and lab signals.** Use lab checks for fast feedback and field data for real user impact.
4. **Segment enough to see regressions.** Track mobile/desktop, browser, device class, geography/network, and key customer segments where relevant.
5. **Gate accessibility smoke checks.** Automate high-signal checks such as missing labels, landmarks, contrast failures detectable by tooling, and keyboard traps where feasible.
6. **Mark releases.** Attach deploy, config, and feature markers to client telemetry and error reports.
7. **Define stop/rollback.** State thresholds for halting rollout, disabling flags, reverting bundles, or forward-fixing.
8. **Route backend causes.** If client experience regresses due to backend saturation, follow up with capacity/performance.

## Synthesized Default

Use user-centric journey-level budgets, field monitoring, lab checks, runtime-error tracking, deploy markers, automated accessibility smoke checks, and explicit rollback criteria. Treat client performance regressions as release blockers when they affect critical journeys.



## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, gates, and evidence to collect.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness evidence.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Existing artifact: use current code, docs, telemetry, incidents, or diffs as evidence for the next engineering decision; do not wait for a finished artifact before guiding design, build, release, or operation.
- Missing evidence: state assumptions and produce the evidence plan instead of blocking lifecycle guidance.

## Exceptions

- Low-traffic routes may rely more on lab checks until enough field data exists.
- Accessibility smoke checks do not replace a full accessibility program; they catch release regressions within engineering scope.
- Experimental internal routes can use advisory budgets if isolated from customers.
- Emergency security fixes can ship with narrower performance gates if post-release monitoring and rollback are explicit.

## Response Quality Bar

- Lead with the release gates, blocking thresholds, or rollout decision requested.
- Cover user-centric metrics, journey budgets, field/lab signals, runtime errors, and rollback criteria before optional client quality topics.
- Make recommendations actionable with evidence, gates, stop conditions, and rollback or flag actions where relevant.
- For ticketing or release-readiness prompts, separate feature implementation tickets from release-control tickets; if a critical journey already regressed, lead with the hold, flag, or rollback decision before the ticket list.
- State required evidence such as field telemetry segments, lab checks, deploy markers, error rates, and payload/journey budgets; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside client release quality. Mention accessibility smoke checks only as release regression gates unless the prompt asks for broader accessibility work.
- Be concise: avoid generic web-performance background and prefer compact gate matrices.

## Required Outputs

- Client runtime SLI/SLO table by journey, screen, or route.
- Performance budget for payload, dependency, critical path, rendering, and interaction costs.
- Field and lab measurement plan.
- Automated accessibility smoke-check list.
- CI/release gate matrix with thresholds and failure response.
- Rollout, flag, and rollback criteria.
- Telemetry privacy notes.

## Evidence Gates

- `user_experience_check`: user-centric load, interaction, and visual stability metrics have journey-level targets.
- `budget_check`: payload, dependency, critical path, rendering, and interaction budgets exist with failure response.
- `field_lab_check`: both field and lab signals are used or a low-traffic exception is recorded.
- `a11y_smoke`: automated accessibility smoke checks are defined for release regressions.
- `rollback_check`: rollout halt, flag disable, revert, or forward-fix criteria are explicit.

## Red Flags - Stop And Rework

- Build success is the only client release gate.
- Aggregate site metrics hide critical route regressions.
- Payload budgets exist but failures have no response path.
- Field monitoring collects sensitive data unnecessarily.
- Accessibility is treated as fully solved by one automated scan.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Lab-only confidence | Combine fast lab checks with field user impact. |
| Global budgets only | Set route and journey budgets. |
| No deploy markers | Tag releases, config, and feature flags in telemetry. |
| Broad accessibility scope creep | Keep release gates to automated smoke checks and route larger work separately. |
