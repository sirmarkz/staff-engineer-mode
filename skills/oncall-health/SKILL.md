---
name: oncall-health
description: "Use when pages, alert fatigue, toil, manual operations, runbook gaps, or operational burden are central."
---

# Oncall Health And Toil Reduction

## Overview

Repeated pages and manual operations are engineering defects.

**Core principle:** keep pages urgent and actionable, convert repeated manual work into durable fixes, and protect responders from avoidable operational load.

## Iron Law

```
NO RECURRING PAGE OR MANUAL RUNBOOK STEP WITHOUT AN OWNER AND ELIMINATION PLAN
```

If the same alert or manual operation keeps recurring, the system is asking for engineering work.

## When To Use

- The user asks to reduce pages, alert fatigue, toil, manual operations, repeated runbook work, or operational burden.
- On-call responders are interrupted by non-urgent, unactionable, duplicate, or noisy alerts.
- Manual mitigations are repeated often enough to automate or remove.
- Runbooks are missing, stale, unsafe, or too vague to execute under pressure.

## When Not To Use

- The user asks about staffing, compensation, rotation fairness, headcount, or HR process; out of scope unless reframed as technical toil reduction.
- The main deliverable is new telemetry or alert construction; defer to `observability-and-alerting`.
- The main work is defining SLOs or paging thresholds from scratch; defer to `slo-and-error-budgets`.
- The request is generic developer productivity with no operational pain; defer to `code-review-and-workflow`.

## Inputs To Collect

- Page history: alert name, count, time, severity, owner, duration, action taken, and user impact.
- Toil inventory: manual, repetitive, automatable, tactical, interrupt-driven work.
- Runbooks, escalation paths, ownership, handoff notes, and incident/postmortem actions.
- Alert policy: page versus ticket, SLO mapping, diagnostic alerts, dedupe, grouping, and suppression.
- Automation candidates, recurring incident classes, platform gaps, and unsafe manual steps.
- Responder load: after-hours pages, sleep interruption, unresolved alerts, and handoff friction.

## Workflow

1. **Classify pages.** Mark each as urgent/actionable/user-visible/novel, ticket-only, diagnostic, duplicate, stale, or false positive.
2. **Find top load sources.** Rank by interruption count, duration, user impact, recurrence, and manual effort.
3. **Separate symptom from cause.** Keep user-impact pages, but remove duplicate cause pages unless they drive distinct action.
4. **Fix runbooks.** Every remaining page needs impact check, mitigation, escalation, rollback/fallback, and verification.
5. **Eliminate toil.** Automate, self-heal, remove, or redesign repeated manual operations; do not just document them better.
6. **Create an engineering backlog.** Give every recurring class an owner, priority, expected page reduction, and verification metric.
7. **Protect the signal.** Use SLO burn, grouping, dedupe, maintenance windows, and ticket routing to prevent alert erosion.
8. **Review regularly.** Feed incident/postmortem findings back into alert policy, platform work, and reliability standards.

## Synthesized Default

Pages should be urgent, actionable, user-visible, and novel. Everything else should be ticketed, automated, grouped, suppressed, or removed. Toil reduction should produce engineering work with measured page or manual-effort reduction, and live-site ownership should feed back into product engineering priorities.

## Exceptions

- Some pre-user-impact alerts may page if they are proven leading indicators with a safe, immediate mitigation.
- Low-tier internal systems may route most operational signals to tickets if user impact is limited and owners accept latency.
- Temporary noisy alerts are allowed during a risky migration only with owner, expiry, and cleanup task.
- Staffing and compensation questions remain out of scope unless translated into technical page/toil reduction.

## Response Quality Bar

- Lead with the page classification, toil inventory, alert-change decision, or automation backlog requested.
- Cover urgency, actionability, user visibility, novelty, runbook quality, repeated manual work, ownership, and measurement before optional on-call breadth.
- Make recommendations actionable with owners, page/ticket/remove decisions, runbook fixes, automation tasks, expiry dates, and measured reduction targets where relevant.
- State required evidence such as alert history, pages per responder, after-hours volume, runbook links, toil hours, manual steps, suppression rules, and incident outcomes; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside technical on-call health and toil. Mark staffing, compensation, and HR questions out of scope unless translated into engineering controls.
- Be concise: avoid generic on-call advice and prefer compact page inventories and remediation backlogs.

## Required Outputs

- Page inventory and classification.
- Top toil sources with frequency, effort, owner, and removal path.
- Alert changes: page/ticket/remove/group/dedupe/suppress decisions.
- Runbook gap list and required updates.
- Automation or redesign backlog with expected page/manual-effort reduction.
- Ownership and escalation fixes.
- Measurement plan for page volume, after-hours interruptions, and toil hours.

## Evidence Gates

- `page_classification`: each reviewed page is classified by urgency, actionability, user visibility, and novelty.
- `toil_inventory`: repeated manual work has owner, frequency, and elimination or automation plan.
- `runbook_check`: remaining pages link to executable runbooks with mitigation and verification.
- `noise_reduction`: proposed changes state expected page or toil reduction and how it will be measured.
- `scope_check`: staffing, compensation, and HR issues are reframed or marked out of scope.

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
