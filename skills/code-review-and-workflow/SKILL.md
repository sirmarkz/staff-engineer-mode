---
name: code-review-and-workflow
description: "Use to set the system-level rules for code review — who reviews what, change-size limits, review-latency targets, and the productivity metrics paired with quality guardrails. Not for reviewing one specific PR; that is agent-pr-review."
---

# Engineering Productivity And Code Review

## Overview

Produces a code review policy, a reviewer-routing plan tied to ownership, and a metrics plan where every velocity number is paired with a quality or reliability guardrail. Catches the moment when an oversized agent-generated diff lands on a random reviewer with no decomposition plan and no defect signal behind the speed metric.

**Core principle:** optimize the review system for fast understanding, clear ownership, automated checks, and quality guardrails rather than raw activity counts.

## Iron Law

```
NO REVIEW POLICY WITHOUT OWNERS, CHANGE-SIZE LIMITS, AND METRICS PAIRED WITH QUALITY GUARDRAILS
```

The policy must say who reviews what, cap how big a single diff can grow before it must be decomposed, and pair every productivity metric with a quality or reliability guardrail. A metric that improves when the system gets worse is not a safe productivity metric. For a solo developer "owners" collapses to "you" and the policy still has to declare it; the change-size cap and guardrail-paired metrics still apply because they exist to catch sloppy diffs and misleading speed numbers.

## When To Use

- The user asks about code review standards, reviewer routing, ownership, review latency, change size, developer productivity, DORA metrics, or workflow quality.
- A team is blocked by slow reviews, unclear ownership, oversized changes, or manual review debates.
- The user asks how to keep code health high while moving faster.
- Static checks and quality gates exist, but reviewer behavior and workflow design are the main problem.

## When Not To Use

- The request is a per-diff pre-merge review pass — "review this PR before merge," "did the agent miss anything," "is this safe to merge," "find risks in this diff" — for any diff regardless of who or what produced it; use `agent-pr-review`. This skill owns the SYSTEM of code review (routing, change size, ownership, DORA metrics); `agent-pr-review` owns the ACT of reviewing a specific diff.
- The user asks which CI checks should block merge; use `testing-and-quality-gates`.
- The user asks about live incidents, on-call, or operational toil; use `incident-response-and-postmortems` or `oncall-health`.
- The request is org-level policy for AI-assisted coding (repo instructions, allowed/forbidden actions, protected paths, secret boundaries, audit trails) rather than reviewer routing or workflow metrics; use `ai-coding-governance`.
- The request is staffing, compensation, performance management, or headcount planning; out of scope.
- The question is broad architecture ownership; use `architecture-decisions` if boundaries are the issue.

## Inputs To Collect

- Current review policy, ownership metadata, reviewer assignment method, and approval requirements.
- Change size, review latency, rework rate, revert rate, escaped defects, and blocked-time data.
- Automated checks, style/format enforcement, static analysis, and pre-merge gates.
- Ownership gaps, cross-team dependencies, large-scale change patterns, and legacy hotspots.
- DORA-style metrics and reliability/quality guardrails already tracked.

## Workflow

1. **Separate workflow from gates.** Review process decides human judgment and ownership; quality gates decide automated evidence.
2. **Reduce change size.** Encourage small, coherent changes with clear intent, tests, rollout notes, and reversible steps.
3. **Route to owners.** Use code ownership, domain knowledge, and risk areas to select reviewers. Avoid broad drive-by review.
4. **Automate the mechanical.** Formatting, simple style, generated code checks, and repeatable static findings should not consume human review time.
5. **Define review priorities.** Review correctness, design, complexity, tests, security, observability, and maintainability before style preferences.
6. **Use metrics with guardrails.** Pair review latency and deployment frequency with defect, revert, incident, SLO, and code-health signals.
7. **Keep integration flow simple.** Prefer a buildable mainline, short-lived branches, protected merges, and automated owner/policy checks over long-lived branch hierarchies.
8. **Handle large changes deliberately.** Use staged codemods, ownership splits, compatibility layers, and automated verification.
9. **Turn repeated friction into platform work.** If many changes repeat setup, approval, or boilerplate, route to golden paths or automation.

## Synthesized Default

Use small changes, explicit ownership, automated mechanical checks, protected mainline integration, risk-based reviewer routing, and guarded metrics. Optimize for the reviewer quickly understanding whether the change improves the system, not for minimizing review as a ritual.

## Exceptions

- Emergency fixes can use expedited review if risk of delay is higher, but follow-up review and tests remain required.
- Large mechanical changes are acceptable when generated, scoped, reviewable by pattern, and validated automatically.
- High-risk changes may require deeper design review, security review, or staged rollout even when code diff is small.
- Experimental prototypes can use lighter review if isolated from production and clearly disposable.

## Response Quality Bar

- Lead with the review policy, workflow diagnosis, metric design, or remediation plan requested.
- Cover ownership, change size, automation, review priorities, guardrail metrics, and large-change handling before optional productivity topics.
- Make recommendations actionable with owners, policy changes, measurement definitions, gates, rollback paths, and reviewable next steps where relevant.
- State required evidence such as review latency, change size, rework, revert, defect, incident, ownership, and code-health data; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering workflow and code review. Route CI gate design, incident response, or architecture ownership only when they are the central unresolved risk.
- Be concise: avoid generic productivity advice and prefer compact policy tables, metric guardrail matrices, and remediation backlogs.

## Required Outputs

- Code review policy covering purpose, reviewer expectations, and approval rules.
- Ownership and reviewer-routing plan.
- Change-size guidance and decomposition patterns.
- Automation backlog for mechanical review work.
- Metrics plan with quality/reliability guardrails.
- Large-scale change plan when applicable.
- Review anti-patterns and remediation actions.

## Evidence Gates

- `ownership_check`: every reviewed area has owner or escalation route.
- `automation_check`: mechanical style/format/static checks are automated or listed for automation.
- `guardrail_check`: productivity metrics are paired with quality, reliability, or incident guardrails.
- `change_size_check`: oversized changes have decomposition or large-scale-change plan.
- `review_priority_check`: review policy prioritizes correctness, design, complexity, tests, and operability before style.

## Red Flags - Stop And Rework

- Review speed is optimized without tracking defects, incidents, reverts, or code health.
- Humans debate formatting or mechanical style that a tool could enforce.
- Reviewer assignment is random for high-risk or domain-owned code.
- Large risky changes are approved as one diff because splitting is inconvenient.
- Metrics reward volume of commits, comments, or approvals instead of outcomes.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating review as gatekeeping | Make review a fast correctness and maintainability check. |
| Measuring only speed | Pair speed with quality, reliability, and code-health signals. |
| Routing everyone to everything | Use ownership and domain risk to select reviewers. |
| Reviewing generated changes line by line | Review generator, pattern, sample, and validation evidence. |
