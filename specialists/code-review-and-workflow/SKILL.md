---
name: code-review-and-workflow
description: "Use when designing change-flow and review systems: responsibility, change size, latency, reviewer routing"
---

# Change Flow And Review Systems

## Iron Law

```
NO ENGINEERING CHANGE FLOW WITHOUT RESPONSIBILITY, CHANGE-SIZE LIMITS, REVIEW LENS, AND QUALITY GUARDRAILS
```

The change flow must say who is responsible, how judgment enters the change, when a diff must be decomposed, and which quality or reliability guardrail pairs with every productivity metric. A metric that improves when the system gets worse is not a safe productivity metric. For a solo developer, responsibility stays with the user and agent through explicit evidence, not a separate review chain.

## Overview

Produces a change-flow design for code review, self-review, responsibility, decomposition, automation, and metrics. Catches the moment when an oversized agent-generated diff has no decomposition plan and no defect signal behind the speed metric.

**Core principle:** optimize engineering change flow for fast understanding, clear responsibility, automated checks, and quality guardrails rather than raw activity counts.

## When To Use

- The user asks about code review standards, review routing, responsibility, review latency, change size, developer productivity, DORA metrics, or change-flow quality.
- You are blocked by slow review flow, unclear responsibility, oversized changes, or disagreement about what judgment is needed.
- The user asks how to keep code health high while moving faster.
- Static checks and quality gates exist, but change-flow design and review behavior are the main problem.

## When Not To Use

- The request is a per-diff pre-merge review pass — "review this PR before merge," "did the agent miss anything," "is this safe to merge," "find risks in this diff" — for any diff regardless of who or what produced it; use `agent-pr-review`. This skill covers the SYSTEM of code review (routing, change size, responsibility, DORA metrics); `agent-pr-review` covers the ACT of reviewing a specific diff.
- The user asks which CI checks should block merge; use `testing-and-quality-gates`.
- The user asks about live incidents, on-call, or operational toil; use `incident-response-and-postmortems` or `oncall-health`.
- The request is org-level rules for AI-assisted coding (repo instructions, allowed/forbidden actions, protected paths, secret boundaries, traceability) rather than review routing or workflow metrics; use `ai-coding-governance`.
- The request is staffing, compensation, performance management, or headcount planning; out of scope.
- The question is broad architecture responsibility; use `architecture-decisions` if boundaries are the issue.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Current change-flow rules, responsibility metadata, review assignment method, and confirmation requirements.
- Change size, review latency, rework rate, revert rate, escaped defects, and blocked-time data.
- Automated checks, style/format enforcement, static analysis, and pre-merge gates.
- Responsibility gaps, cross-component dependencies, large-scale change patterns, and legacy hotspots.
- DORA-style metrics and reliability/quality guardrails already tracked.

## Workflow

1. **Separate human judgment from gates.** Review flow decides judgment and responsibility; quality gates decide automated evidence.
2. **Reduce change size.** Encourage small, coherent changes with clear intent, tests, rollout notes, and reversible steps.
3. **Select the right review lens.** Use code responsibility, domain knowledge, and risk areas to decide whether the user needs self-review, agent pre-merge review, or a narrower specialist skill.
4. **Automate the mechanical.** Formatting, simple style, generated code checks, and repeatable static findings should not consume human review time.
5. **Define review priorities.** Prioritize correctness, design, complexity, tests, security, observability, and maintainability before style preferences.
6. **Use metrics with guardrails.** Pair review latency and deployment frequency with defect, revert, incident, SLO, and code-health signals.
7. **Keep integration flow simple.** Prefer a buildable mainline, short-lived branches, protected merges, and automated checks over long-lived branch hierarchies.
8. **Handle large changes deliberately.** Use staged codemods, responsibility splits, compatibility layers, and automated verification.
9. **Turn repeated friction into platform work.** If many changes repeat setup, confirmation, or boilerplate, route to golden paths or automation.

## Synthesized Default

Use small changes, explicit responsibility, automated mechanical checks, protected mainline integration, risk-based review routing, and guarded metrics. Optimize for fast evidence that the change improves the system, not for minimizing review as a ritual.



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

- Emergency fixes can use expedited review if risk of delay is higher, but follow-up review and tests remain required.
- Large mechanical changes are acceptable when generated, scoped, reviewable by pattern, and validated automatically.
- High-risk changes may require deeper design, security, or rollout scrutiny even when the code diff is small.
- Experimental prototypes can use lighter review if isolated from production and clearly disposable.

## Response Quality Bar

- Lead with the change-flow rule, routing decision, metric design, or remediation plan requested.
- Cover responsibility, change size, automation, review priorities, guardrail metrics, and large-change handling before optional productivity topics.
- Make recommendations actionable with rule changes, measurement definitions, gates, rollback paths, and next steps where relevant.
- State required evidence such as review latency, change size, rework, revert, defect, incident, responsibility, and code-health data; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering workflow and code review. Route CI gate design, incident response, or architecture responsibility only when they are the central unresolved risk.
- Be concise: avoid generic productivity advice and prefer compact policy tables, metric guardrail matrices, and remediation backlogs.

## Required Outputs

- Change-flow rule set covering purpose, review expectations, and merge rules.
- Responsibility and review-routing plan.
- Change-size guidance and decomposition patterns.
- Automation backlog for mechanical checks.
- Metrics plan with quality/reliability guardrails.
- Large-scale change plan when applicable.
- Change-flow anti-patterns and remediation actions.

## Evidence Gates

- `responsibility_check`: every reviewed area has an explicit user/agent responsibility path or fallback path.
- `automation_check`: mechanical style/format/static checks are automated or listed for automation.
- `guardrail_check`: productivity metrics are paired with quality, reliability, or incident guardrails.
- `change_size_check`: oversized changes have decomposition or large-scale-change plan.
- `review_priority_check`: review priorities put correctness, design, complexity, tests, and operability before style.

## Red Flags - Stop And Rework

- Review speed is optimized without tracking defects, incidents, reverts, or code health.
- Humans debate formatting or mechanical style that a tool could enforce.
- High-risk or domain-critical code gets no focused review lens.
- Large risky changes are accepted as one diff because splitting is inconvenient.
- Metrics reward volume of commits, comments, or review acknowledgments instead of outcomes.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating review as gatekeeping | Make review a fast correctness and maintainability check. |
| Measuring only speed | Pair speed with quality, reliability, and code-health signals. |
| Routing everyone to everything | Use responsibility and domain risk to select review passes. |
| Reviewing generated changes line by line | Review generator, pattern, sample, and validation evidence. |
