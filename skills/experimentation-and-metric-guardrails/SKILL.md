---
name: experimentation-and-metric-guardrails
description: "Use when experiments, A/B tests, holdouts, guardrail metrics, exposure logging, or metric trust are central."
---

# Experimentation And Metric Guardrails

## Overview

Experiments are only useful when assignment, exposure, metrics, and decision rules are trustworthy.

**Core principle:** design experiments with clear hypotheses, stable assignment, reliable exposure logging, predeclared metrics, guardrails, and invalidation checks.

## Iron Law

```
NO EXPERIMENT DECISION WITHOUT HYPOTHESIS, ASSIGNMENT CHECKS, EXPOSURE LOGGING, GUARDRAILS, AND READOUT RULES
```

If the experiment cannot prove who saw what and which metric decides the outcome, it should not drive the decision.

## When To Use

- The user asks about experiments, A/B tests, holdouts, ramp decisions, sample-ratio mismatch, exposure logging, guardrail metrics, or metric trust.
- A product, ranking, pricing, UI, recommendation, or workflow change needs causal evidence rather than only rollout health.
- Experiment results conflict, look too good, lack power, or may be invalid because of logging, assignment, contamination, or metric defects.
- A ramp needs outcome guardrails beyond operational canary checks.

## When Not To Use

- The main question is blast radius, rollback, canary, or operational rollout; defer to `progressive-delivery`.
- The main question is service reliability objectives or alerting policy; defer to `slo-and-error-budgets`.
- The main question is LLM evals or model release gates; defer to `llm-evaluation` or `ml-reliability-and-evaluation`.
- The request is product strategy with no engineering measurement artifact.

## Inputs To Collect

- Hypothesis, decision to make, target population, unit of assignment, treatment, control, and exposure rule.
- Primary metric, guardrail metrics, diagnostic metrics, minimum effect, runtime, and stopping rule.
- Assignment implementation, eligibility filters, ramp plan, holdout policy, and contamination risks.
- Exposure logging, event definitions, metric pipelines, missingness, delayed effects, and data-quality checks.
- Segment/slice plan, interaction with other experiments, and decision owner.

## Workflow

1. **State the decision.** Define the hypothesis and what action the readout will drive.
2. **Choose assignment unit.** Pick a stable unit that matches the effect being measured and avoids cross-contamination.
3. **Define exposure.** Log when the user or entity could actually be affected, not only when assignment occurred.
4. **Predeclare metrics.** Name primary, guardrail, diagnostic, and segment metrics before reading results.
5. **Check validity.** Test assignment balance, sample-ratio mismatch, missing telemetry, logging defects, and eligibility drift.
6. **Plan interactions.** Identify overlapping experiments, long-lived holdouts, novelty effects, and downstream metric coupling.
7. **Gate ramps.** Combine experiment outcomes with operational guardrails; do not let positive primary metrics hide safety regressions.
8. **Record decision evidence.** Capture result, caveats, decision, owner, rollback trigger, and follow-up measurement.

## Synthesized Default

Use predeclared hypotheses, stable assignment, exposure-based analysis, primary and guardrail metrics, validity checks, segment readouts, and decision records. Treat metric trust failures as experiment blockers, not as minor caveats after the decision.

## Exceptions

- Very low-risk copy or layout tests may use simpler analysis if assignment, exposure, and guardrails remain clear.
- Sequential ramps can make decisions before full power when safety or user impact requires it, but must state the weaker inference.
- Long-term effects may need holdouts or delayed readouts before irreversible changes.

## Response Quality Bar

- Lead with the experiment design, validity finding, ramp decision, or metric guardrail requested.
- Cover hypothesis, assignment, exposure, metrics, guardrails, validity checks, slices, interactions, and decision rule before optional statistics detail.
- Make recommendations actionable with owners, metric definitions, stop criteria, invalidation triggers, and readout dates where relevant.
- State required evidence such as assignment logs, exposure events, metric definitions, balance checks, missingness, segment results, and prior experiment interactions; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside experimentation and metric trust. Route rollout safety, service SLOs, or AI evals only when those own the decision.
- Be concise: prefer experiment design and readout tables over generic testing background.

## Required Outputs

- Experiment design with hypothesis, population, assignment unit, treatment, control, and exposure rule.
- Metric map: primary, guardrail, diagnostic, and segment metrics.
- Validity checks for assignment, sample ratio, telemetry, eligibility, contamination, and missingness.
- Ramp, stop, and readout decision rules.
- Interaction and holdout notes.
- Decision record with caveats and follow-up measurement.

## Evidence Gates

- `hypothesis_named`: experiment maps to a clear decision and expected effect.
- `assignment_valid`: unit, eligibility, and balance checks are defined.
- `exposure_logged`: exposure event proves who could be affected.
- `guardrails_set`: safety and quality metrics can block a positive primary result.
- `validity_checked`: metric trust failures are checked before readout.

## Red Flags - Stop And Rework

- Assignment exists but exposure is not logged.
- Metrics are chosen after the result is known.
- Sample-ratio mismatch is ignored.
- A positive primary metric hides reliability, safety, or accessibility harm.
- The ramp continues after validity checks fail.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Rollout health as causal proof | Use assignment, exposure, and readout rules. |
| Result-first metrics | Predeclare metrics and guardrails. |
| Ignoring invalidation | Treat balance and telemetry failures as blockers. |
| Average-only readouts | Check important slices and long-term effects. |
