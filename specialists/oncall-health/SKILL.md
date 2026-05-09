---
name: oncall-health
description: "Use when page volume, suppression rules, toil, runbook gaps, or recurring manual ops are hurting responders"
---

# Oncall Health And Toil Reduction

## Iron Law

```
NO RECURRING PAGE OR MANUAL RUNBOOK STEP WITHOUT A FIX PATH AND ELIMINATION PLAN
```

If the same alert or manual operation keeps recurring, the system is asking for engineering work.

## Overview

Repeated pages and manual operations are engineering defects.

**Core principle:** keep pages urgent and actionable, convert repeated manual work into durable fixes, and protect responders from avoidable operational load.

## When To Use

- The user asks to reduce pages, alert fatigue, toil, manual operations, repeated runbook work, or operational burden.
- On-call responders are interrupted by non-urgent, unactionable, duplicate, or noisy alerts.
- Manual mitigations are repeated often enough to automate or remove.
- Runbooks are missing, stale, unsafe, or too vague to execute under pressure.

## When Not To Use

- The user asks about staffing, compensation, rotation fairness, headcount, or HR process; out of scope unless reframed as technical toil reduction.
- The main deliverable is new telemetry or alert construction; use `observability-and-alerting` instead.
- The main work is defining SLOs or paging thresholds from scratch; use `slo-and-error-budgets` instead.
- The request is generic developer productivity with no operational pain; use `code-review-and-workflow` instead.

## Inputs To Collect

- Page history: alert name, count, time, severity, duration, action taken, user impact, and fix path.
- Toil inventory: manual, repetitive, automatable, tactical, interrupt-driven work.
- Runbooks, fallback paths, responsibility, checkpoint notes, and incident/postmortem actions.
- Alert policy: page versus ticket, SLO mapping, diagnostic alerts, dedupe, grouping, and suppression.
- Automation candidates, recurring incident classes, platform gaps, and unsafe manual steps.
- Responder load: after-hours pages, sleep interruption, unresolved alerts, and checkpoint friction.

## Workflow

1. **Classify pages.** Mark each as urgent/actionable/user-visible/novel, ticket-only, diagnostic, duplicate, stale, or false positive.
2. **Find top load sources.** Rank by interruption count, duration, user impact, recurrence, and manual effort.
3. **Separate symptom from cause.** Keep user-impact pages, but remove duplicate cause pages unless they drive distinct action.
4. **Fix runbooks.** Every remaining page needs impact check, mitigation, fallback, rollback, and verification.
5. **Eliminate toil.** Automate, self-heal, remove, or redesign repeated manual operations; do not just document them better.
6. **Create an engineering backlog.** Give every recurring class a priority, expected page reduction, and verification metric.
7. **Protect the signal.** Use SLO burn, grouping, dedupe, maintenance windows, and ticket routing to prevent alert erosion.
8. **Set a page-rate budget.** State a numeric per-shift / per-week page target (e.g., "≤2 pages/shift") AND how it will be measured (rolling 7d, after-hours weighted). Compare against current rate.
9. **Audit runbook freshness.** For every paging alert, record runbook last-reviewed date and require review cadence (e.g., 90d) alongside coverage.
10. **Review regularly.** Feed incident/postmortem findings back into alert policy, platform work, and reliability standards.

## Synthesized Default

Pages should be urgent, actionable, user-visible, and novel. Everything else should be ticketed, automated, grouped, suppressed, or removed. Toil reduction should produce engineering work with measured page or manual-effort reduction, and live-site responsibility should feed back into product engineering priorities.

## Exceptions

- Some pre-user-impact alerts may page if they are proven leading indicators with a safe, immediate mitigation.
- Low-tier internal systems may route most operational signals to tickets if user impact is limited and the user accepts the response latency.
- Temporary noisy alerts are allowed during a risky migration only with expiry, and cleanup task.
- Staffing and compensation questions remain out of scope unless translated into technical page/toil reduction.

## Response Quality Bar

- Lead with the page classification, toil inventory, alert-change decision, or automation backlog requested.
- Cover urgency, actionability, user visibility, novelty, runbook quality, repeated manual work, responsibility, and measurement before optional on-call breadth.
- Make recommendations actionable with page/ticket/remove decisions, runbook fixes, automation tasks, expiry dates, and measured reduction targets where relevant.
- State required evidence such as alert history, pages per responder, after-hours volume, runbook links, toil hours, manual steps, suppression rules, and incident outcomes; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside technical on-call health and toil. Mark staffing, compensation, and HR questions out of scope unless translated into engineering controls.
- Be concise: avoid generic on-call advice and prefer compact page inventories and remediation backlogs.

## Required Outputs

- Page inventory and classification.
- Top toil sources with frequency, effort, and removal path.
- Alert changes: page/ticket/remove/group/dedupe/suppress decisions.
- Runbook gap list and required updates.
- Automation or redesign backlog with expected page/manual-effort reduction.
- Responsibility and fallback fixes.
- Measurement plan for page volume, after-hours interruptions, and toil hours.
- Numeric page-rate / interruption budget per shift with the measurement window and source.
- Runbook coverage AND freshness check (last-reviewed date, review cadence) for each paging alert.

## Evidence Gates

- `page_classification`: each reviewed page is classified by urgency, actionability, user visibility, and novelty.
- `toil_inventory`: repeated manual work has frequency, and elimination or automation plan.
- `runbook_check`: remaining pages link to executable runbooks with mitigation and verification.
- `noise_reduction`: proposed changes state expected page or toil reduction and how it will be measured.
- `scope_check`: staffing, compensation, and HR issues are reframed or marked out of scope.
- `page_rate_budget`: a numeric per-shift or per-week page target is stated with measurement window.
- `runbook_freshness`: each paging alert has a last-reviewed date and a freshness cadence.

## Red Flags - Stop And Rework

- The solution is "make the runbook longer" for repeated manual work.
- A page has no action other than "look at dashboard".
- Responders routinely silence, ignore, or rerun alerts.
- Every cause alert pages alongside the symptom alert.
- Alert reduction removes the only user-impact signal.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating pages as inevitable | Treat avoidable pages as engineering defects. |
| Automating bad operations | Remove or redesign unsafe manual work when possible. |
| Deleting noisy alerts blindly | Preserve user-impact coverage and verify replacement signal. |
| Measuring only count | Track after-hours load, duration, recurrence, and toil hours. |
