---
name: llm-evaluation
description: "Use when model-backed changes need eval datasets, graders, thresholds, slices, regression history, or failure triage"
---

# LLM Evaluation Harness Engineering

## Iron Law

```
NO MODEL-BACKED CHANGE WITHOUT EVAL CASES, SCORING RULES, THRESHOLDS, REGRESSION HISTORY, AND FAILURE TRIAGE
```

If you cannot say what got better, what got worse, and which failures block release, the eval is not a gate.

## Overview

LLM behavior is production behavior when prompts, tools, retrieval, or model outputs affect users or workflows.

**Core principle:** build eval harnesses with representative cases, stable scoring, slice coverage, regression history, and release thresholds before trusting model-backed changes.

## When To Use

- The user asks about LLM evals, prompt tests, agent evals, graders, regression sets, acceptance thresholds, or model-backed workflow quality gates.
- A prompt, model, retrieval source, tool policy, or agent workflow changes and needs release evidence.
- Existing evals are flaky, too small, too easy, judge-biased, or disconnected from production failures.
- You need repeatable evidence for quality, safety, refusal, formatting, task completion, or user-impact slices.

## When Not To Use

- The main risk is prompt injection, tool misuse, data leakage, or unsafe actions; use `llm-application-security` instead.
- The main work is classical ML drift, training-serving skew, or model-serving readiness; use `ml-reliability-and-evaluation` instead.
- The request is broad AI coding-agent governance; use `ai-coding-governance` instead.
- The request is product strategy for which model to choose with no engineering gate.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Workflow, user tasks, expected outputs, unacceptable failures, and release decision to support.
- Eval cases, production examples, synthetic cases, edge cases, slices, and known regressions.
- Scoring method, graders, rubrics, deterministic checks, human review, and tie-break rules.
- Thresholds, confidence needs, flake rate, baseline result, and comparison target.
- Versioned prompts, models, retrieval inputs, tools, datasets, and harness code.
- Failure triage workflow, severity, waiver rules, and re-run policy.

## Workflow

1. **Name the decision.** State whether the eval gates merge, release, prompt change, model change, or rollback.
2. **Build representative cases.** Include production-like tasks, edge cases, regressions, adversarial examples, and important user slices.
3. **Separate scoring types.** Use exact checks for structured requirements, rubric scoring for judgment, and human review for ambiguous high-impact cases.
4. **Control grader risk.** Define rubrics, blind comparisons where useful, calibration cases, and checks for scoring drift.
5. **Set thresholds first.** Declare pass, warn, and block criteria before looking at the new result.
6. **Version inputs.** Link prompts, model, retrieval corpus, tool policy, eval cases, graders, and harness code to the result.
7. **Triage failures.** Classify blockers, acceptable regressions, flaky cases, data issues, and missing coverage.
8. **Keep history.** Track baseline, deltas, regressions, waived failures, and production incidents that should become future cases.

## Synthesized Default

Use a versioned eval harness with representative cases, slice coverage, deterministic checks where possible, calibrated rubric graders where needed, predefined thresholds, regression history, and explicit failure triage. Treat aggregate score improvements as insufficient when critical slices or known failure modes regress.



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

- Early prototypes may use exploratory evals if they are not release gates.
- Human review can supplement automated scoring for high-impact or ambiguous tasks, but should use a written rubric.
- Low-risk copy changes may use a narrow regression set if output constraints and affected journeys are limited.

## Response Quality Bar

- Lead with the eval harness design, release gate, failure triage, or threshold decision requested.
- Cover decision, cases, slices, scoring, thresholds, versioning, regression history, and failure handling before optional model discussion.
- Make recommendations actionable with dataset changes, grader rules, pass/fail criteria, and rerun policy where relevant.
- State required evidence such as eval cases, baseline runs, grader rubric, flake rate, slice results, versioned inputs, and failure log; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside model-backed evaluation gates. Route security, ML serving, or AI coding governance only when those risks dominate.
- Be concise: prefer eval matrices and release gates over generic eval theory.

## Required Outputs

- Eval harness specification.
- Case inventory with production, synthetic, edge, regression, and slice coverage.
- Scoring and grader rubric.
- Thresholds for pass, warn, block, and rollback.
- Versioned-input record.
- Failure triage table with disposition and next action.
- Regression history and case-promotion policy.

## Evidence Gates

- `decision_named`: eval result maps to a merge, release, rollback, or investigation decision.
- `case_coverage`: representative cases include critical tasks, slices, and known regressions.
- `scoring_defined`: checks, graders, rubrics, and tie-break rules are explicit.
- `thresholds_predeclared`: pass, warn, and block criteria are set before judging the change.
- `version_lineage`: prompts, model, data inputs, tools, eval cases, graders, and result are linked.

## Red Flags - Stop And Rework

- A single aggregate score hides critical slice regressions.
- The grader rubric changes between baseline and candidate.
- Eval cases are generated from the same prompt being tested with no review.
- Failures are waived without reason, and expiry.
- Production incidents do not become regression cases.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Score first, threshold later | Set pass and block criteria before running. |
| Only happy-path cases | Add edge, adversarial, and regression cases. |
| Unversioned prompts | Link every input to every result. |
| Treating judge output as truth | Calibrate rubrics and inspect failures. |
