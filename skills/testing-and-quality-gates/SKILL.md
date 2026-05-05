---
name: testing-and-quality-gates
description: "Use to design the test strategy and decide which checks block merge or release — pre-merge gates, CI runtime budgets, static analysis, mutation testing, flake policy, and legacy ratchets."
---

# Testing And Quality Gates

## Iron Law

```
EVERY TEST PROVES A NAMED RISK; EVERY BLOCKING GATE HAS AN OWNER AND A FAILURE RESPONSE
```

Tests exist to exercise a specific risk; "we have tests" without naming the risk each test exercises is faith, not evidence. A blocking gate without an owner and a written failure response teaches people to ignore it. For a solo developer the owner is you and the failure response is a written sentence — the discipline is naming both, not creating a roster.

## Overview

Quality gates should catch real risk early without turning delivery into ritual.

**Core principle:** place fast, deterministic, high-signal checks before merge; reserve slower or broader checks for the stage where they actually prove something.

## When To Use

- The user asks for test strategy, merge gates, release gates, CI checks, quality standards, test pyramid/trophy, static analysis, coverage policy, or verification requirements.
- A team needs to decide what must pass before merge, before release, or before launch.
- A legacy codebase needs quality ratchets without stopping all work.
- Existing tests or CI are slow, flaky, low-signal, or ignored.

## When Not To Use

- The user asks about reviewer behavior, ownership routing, or review latency; defer to `code-review-and-workflow`.
- The user asks for canary or production rollout gates; defer to `progressive-delivery`.
- The request is production chaos or failover testing; defer to `resilience-experiments` or `high-availability-design`.
- The question is pure formatting/style enforcement; automate it and keep this skill focused on risk.

## Inputs To Collect

- Supported behaviors, critical journeys, system tier, risk areas, and recent defect history.
- Existing test inventory: unit/component/contract/integration/end-to-end/performance/security/accessibility/static checks.
- CI structure, runtime, flake rate, failure ownership, and required versus advisory checks.
- Coverage signal, mutation or fault-injection needs, legacy findings, and known blind spots.
- Release process and where gates can run without excessive feedback delay.

## Workflow

1. **Classify risk.** Identify correctness, compatibility, security, reliability, performance, data, and accessibility risks introduced by the change.
2. **Place tests low.** Prefer the cheapest deterministic check that proves the behavior; use broader tests only for cross-boundary confidence.
3. **Define a test taxonomy.** Group checks by dependency and runtime cost so fast in-memory/component tests protect merge, deployment tests protect release, and production probes protect rollout.
4. **Separate gate types.** Pre-merge gates should be fast and high-signal; use a default budget such as p95 under 10 minutes for the full pre-merge lane and under 5 minutes for a fast path. Pre-release gates can be broader; production gates belong to rollout.
5. **Make gates owned.** Every blocking check needs an owner, failure instructions, and a path to fix or quarantine.
6. **Handle flakes ruthlessly.** A flaky blocker teaches people to ignore gates. Fix, quarantine, or downgrade with owner and expiry.
7. **Use ratchets for legacy.** Prevent new critical findings and gradually reduce existing debt rather than requiring impossible cleanup.
8. **Place high-assurance tests deliberately.** Bounded property tests on pure logic and ordinary fuzzing can live in this skill; concurrency/protocol invariants, model checking, deterministic simulation, and counterexample-driven proof route to formal validation.
9. **Choose test data safely.** Use synthetic data for pre-merge by default, anonymized or captured production-like data in controlled release stages, and explicit privacy review for sensitive fixtures.
10. **Use mutation testing selectively.** Apply it to safety, security, financial, or dense branch logic where coverage percentage is misleading; do not make it a universal gate.
11. **Keep style mechanical.** Formatting and simple style should be automated, not debated in review.
12. **Verify the strategy.** Confirm each critical risk has a gate, test, review artifact, or explicit exception.

## Synthesized Default

Use a risk-based test strategy with fast deterministic pre-merge gates, focused integration/contract checks for boundaries, static/security analysis in the developer path, and broader release gates only where they add confidence. Push tests left when they can run reliably before merge; push tests right only when production reality is the evidence needed. Block on high-signal checks; make low-signal checks advisory until they are trustworthy.

## Exceptions

- Legacy systems may use non-regression ratchets before enforcing absolute thresholds.
- Flaky tests should not block until fixed or quarantined with clear ownership.
- Safety-critical, financial, security-sensitive, or data-destructive paths may require deeper verification, formal review, or simulation.
- Generated or third-party code may use contract and integration checks instead of unit-level ownership.

## Response Quality Bar

- Lead with the test strategy, gate matrix, blocker decision, or quality-risk map requested.
- Cover risk mapping, gate stage, failure response, flake policy, static/security checks, and legacy ratchets before optional testing breadth.
- Make recommendations actionable with owners, blocking/advisory status, validation commands, quarantine rules, stop criteria, and rollout of new gates where relevant.
- State required evidence such as defect history, critical journeys, CI runtime, flake rate, coverage gaps, static findings, and release failure data; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside verification and quality gates. Route production rollout gates, reviewer workflow, or chaos testing only when they are the central unresolved risk.
- Be concise and prefer compact risk-to-gate matrices, but always state: a flake-rate metric paired with a quarantine timer, a coverage metric+target paired with a meaningful-vs-vanity caveat, a CI runtime target paired with how it is measured, and per-layer test ratios with rationale when test composition is in scope.

## Required Outputs

- Test strategy by risk area and lifecycle stage.
- Gate matrix: pre-merge, pre-release, launch, and advisory checks.
- Runtime budget for blocking lanes with a measurement source (p95 from CI history, not aspirational), and the action when the budget is exceeded.
- Test composition by layer (unit/integration/e2e ratios or counts) with rationale when redesigning a suite.
- Failure response for each blocking gate.
- Static analysis, security scanning, and dependency check policy.
- Coverage or mutation policy where it adds useful signal — name the metric, the target, and the meaningful-vs-vanity caveat (changed-code coverage, critical-path coverage).
- Test data sourcing and privacy/sensitivity policy.
- Flake management and quarantine policy — state the flake-rate threshold (e.g. >1% rerun rate) and the quarantine timer (e.g. 24-48h to quarantine or downgrade with expiry).
- Legacy ratchet plan with owner and cadence.

## Evidence Gates

- `risk_mapping`: every critical risk maps to a test, check, review artifact, or explicit exception.
- `gate_signal`: every blocking gate has high signal, owner, and failure response.
- `flake_policy`: flaky checks have fix, quarantine, downgrade, or expiry decision.
- `stage_fit`: each gate runs at the earliest stage where it can prove the intended property.
- `legacy_ratchet`: existing debt has a non-regression rule and reduction plan.

## Red Flags - Stop And Rework

- A slow end-to-end suite is the only meaningful pre-merge gate.
- Coverage percentage is treated as quality without behavior/risk mapping.
- Flaky tests are required but failures are routinely rerun until green.
- Static analysis results are dumped on teams after merge with no owner.
- Gates block but nobody can explain what failure means.
- High-assurance protocol or concurrency validation is treated as ordinary CI without invariants or counterexamples.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Testing implementation shape | Test supported behavior and contracts. |
| Blocking on noisy tools | Start advisory, tune signal, then enforce. |
| One giant quality gate | Split by lifecycle stage and risk. |
| Demanding instant legacy perfection | Use ratchets and prevent new debt. |
