---
name: testing-and-quality-gates
description: "Use when test strategy, merge/release gates, CI budgets, static analysis, mutation tests, flakes, or ratchets matter"
---

# Testing And Quality Gates

## Iron Law

```
EVERY TEST PROVES A NAMED RISK; EVERY BLOCKING GATE HAS A FAILURE RESPONSE
```

Tests exist to exercise a specific risk; "we have tests" without naming the risk each test exercises is faith, not evidence. A blocking gate without a written failure response teaches people to ignore it. For a solo developer the response can be a single sentence: what the agent should inspect, what command verifies the fix, and when to quarantine or downgrade the check.

## Overview

Quality gates should catch real risk early without turning delivery into ritual.

**Core principle:** place fast, deterministic, high-signal checks before merge; reserve slower or broader checks for the stage where they actually prove something.

## When To Use

- The user asks for test strategy, merge gates, release gates, CI checks, quality standards, test pyramid/trophy, static analysis, coverage policy, or verification requirements.
- You need to decide what must pass before merge, before release, or before launch.
- A legacy codebase needs quality ratchets without stopping all work.
- Existing tests or CI are slow, flaky, low-signal, or ignored.

## When Not To Use

- The user asks about review behavior, responsibility routing, or review latency; use `code-review-and-workflow` instead.
- The user asks for canary or production rollout gates; use `progressive-delivery` instead.
- The request is production chaos or failover testing; use `resilience-experiments` or `high-availability-design` instead.
- The question is pure formatting/style enforcement; automate it and keep this skill focused on risk.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Supported behaviors, critical journeys, system tier, risk areas, and recent defect history.
- Existing test inventory: unit/component/contract/integration/end-to-end/performance/security/accessibility/static checks.
- CI structure, runtime, flake rate, failure responsibility, and required versus advisory checks.
- Coverage signal, mutation or fault-injection needs, legacy findings, and known blind spots.
- Release process and where gates can run without excessive feedback delay.

## Workflow

1. **Classify risk.** Identify correctness, compatibility, security, reliability, performance, data, and accessibility risks introduced by the change.
2. **Place tests low.** Prefer the cheapest deterministic check that proves the behavior; use broader tests only for cross-boundary confidence.
3. **Define a test taxonomy.** Group checks by dependency and runtime cost so fast in-memory/component tests protect merge, deployment tests protect release, and production probes protect rollout.
4. **State suite composition.** For CI reduction, flake cleanup, or suite redesign, include a compact current or target layer mix such as unit/component, contract/integration, and end-to-end counts or ratios, with one rationale tied to speed, determinism, and risk coverage.
5. **Separate gate types.** Pre-merge gates should be fast and high-signal; use a default budget such as p95 under 10 minutes for the full pre-merge lane and under 5 minutes for a fast path. Pre-release gates can be broader; production gates belong to rollout.
6. **Make gates actionable.** Every blocking check needs failure instructions and a path to fix or quarantine.
7. **Handle flakes ruthlessly.** A flaky blocker teaches people to ignore gates. Fix, quarantine, or downgrade with a dated expiry.
8. **Use ratchets for legacy.** Prevent new critical findings and gradually reduce existing debt rather than requiring impossible cleanup.
9. **Place high-assurance tests deliberately.** Bounded property tests on pure logic and ordinary fuzzing can live in this skill; concurrency/protocol invariants, model checking, deterministic simulation, and counterexample-driven proof route to formal validation.
10. **Choose test data safely.** Use synthetic data for pre-merge by default, anonymized or captured production-like data in controlled release stages, and explicit privacy review for sensitive fixtures.
11. **Use mutation testing selectively.** Apply it to safety, security, financial, or dense branch logic where coverage percentage is misleading; do not make it a universal gate.
12. **Keep style mechanical.** Formatting and simple style should be automated, not debated in review.
13. **Verify the strategy.** Confirm each critical risk has a gate, test, review artifact, or explicit exception.

## Synthesized Default

Use a risk-based test strategy with fast deterministic pre-merge gates, focused integration/contract checks for boundaries, static/security analysis in the developer path, and broader release gates only where they add confidence. Push tests left when they can run reliably before merge; push tests right only when production reality is the evidence needed. Block on high-signal checks; make low-signal checks advisory until they are trustworthy.



## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, gates, and evidence to collect.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness evidence.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Review: evaluate an existing diff, design, runbook, evidence, or system behavior as one mode.
- Missing evidence: state assumptions and produce the evidence plan instead of blocking lifecycle guidance.

## Exceptions

- Legacy systems may use non-regression ratchets before enforcing absolute thresholds.
- Flaky tests should not block until fixed or quarantined with clear responsibility.
- Safety-critical, financial, security-sensitive, or data-destructive paths may require deeper verification, formal review, or simulation.
- Generated or third-party code may use contract and integration checks instead of unit-level responsibility.

## Response Quality Bar

- Lead with the test strategy, gate matrix, blocker decision, or quality-risk map requested.
- Cover risk mapping, gate stage, failure response, flake policy, static/security checks, and legacy ratchets before optional testing breadth.
- For slow-CI, bypassed-CI, flaky-suite, or suite-redesign prompts, always state the intended test-layer composition as counts or ratios and explain why that mix gives faster, more deterministic signal than the current shape.
- Make recommendations actionable with blocking/advisory status, validation commands, quarantine rules, stop criteria, and rollout of new gates where relevant.
- State required evidence such as defect history, critical journeys, CI runtime, flake rate, coverage gaps, static findings, and release failure data; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside verification and quality gates. Route production rollout gates, review workflow, or chaos testing only when they are the central unresolved risk.
- Be concise and prefer compact risk-to-gate matrices, but always state: a flake-rate metric paired with a quarantine timer, a coverage metric+target paired with a meaningful-vs-vanity caveat, a CI runtime target paired with how it is measured, and per-layer test ratios with rationale when test composition is in scope.

## Required Outputs

- Test strategy by risk area and lifecycle stage.
- Gate matrix: pre-merge, pre-release, launch, and advisory checks.
- Runtime budget for blocking lanes with a measurement source (p95 from CI history, not aspirational), and the action when the budget is exceeded.
- Test composition by layer (unit/component, contract/integration, end-to-end, and specialized checks) with counts or ratios and rationale whenever cutting CI time, handling flakes, or redesigning a suite.
- Failure response for each blocking gate.
- Static analysis, security scanning, and dependency check policy.
- Coverage or mutation policy where it adds useful signal — name the metric, the target, and the meaningful-vs-vanity caveat (changed-code coverage, critical-path coverage).
- Test data sourcing and privacy/sensitivity policy.
- Flake management and quarantine policy — state the flake-rate threshold (e.g. >1% rerun rate) and the quarantine timer (e.g. 24-48h to quarantine or downgrade with expiry).
- Legacy ratchet plan with cadence, target metric, and next reduction step.

## Evidence Gates

- `risk_mapping`: every critical risk maps to a test, check, review artifact, or explicit exception.
- `gate_signal`: every blocking gate has high signal, and failure response.
- `flake_policy`: flaky checks have fix, quarantine, downgrade, or expiry decision.
- `stage_fit`: each gate runs at the earliest stage where it can prove the intended property.
- `suite_shape`: test-layer counts or ratios match the risk profile, with most pre-merge confidence coming from cheap deterministic checks and only bounded broad tests blocking.
- `legacy_ratchet`: existing debt has a non-regression rule and reduction plan.

## Red Flags - Stop And Rework

- A slow end-to-end suite is the only meaningful pre-merge gate.
- Coverage percentage is treated as quality without behavior/risk mapping.
- Flaky tests are required but failures are routinely rerun until green.
- Static analysis results appear after merge with no local fix path or suppression rule.
- Gates block but nobody can explain what failure means.
- High-assurance protocol or concurrency validation is treated as ordinary CI without invariants or counterexamples.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Testing implementation shape | Test supported behavior and contracts. |
| Blocking on noisy tools | Start advisory, tune signal, then enforce. |
| One giant quality gate | Split by lifecycle stage and risk. |
| Demanding instant legacy perfection | Use ratchets and prevent new debt. |
