---
name: incident-response-and-postmortems
description: "Use when running active incidents, writing postmortems, or setting status cadence and action items"
---

# Incident Response And Postmortems

## Iron Law

```
NO INCIDENT WITHOUT ROLES, IMPACT, AND STATUS CADENCE; NO POSTMORTEM WITHOUT TIMELINE, CONTRIBUTING FACTORS, AND VERIFIED ACTIONS
```

The two halves are co-designed: live response is unsafe without named responders, declared impact, and a predictable next-update time; a postmortem that only names a root cause or a person has not explained the system. For a solo developer the responder roles collapse onto one person, but the role labels still have to be claimed explicitly so nothing falls between them.

## Overview

Produces incident roles and severity, a live timeline, a status-update cadence, a checkpoint packet for shift changes, and a blameless postmortem whose action items have due dates, and observable verification signals. Refuses "human error" as a conclusion and refuses action items that read "be more careful".

**Core principle:** coordinate clear roles, mitigate impact, preserve a timeline, communicate predictably, and convert learning into verified engineering improvements.

## When To Use

- The user asks for outage handling, incident command, severity, status updates, response roles, timelines, postmortems, or action items.
- A customer-impacting degradation, data issue, security event, or operational emergency is active or recently resolved.
- You need a blameless review or follow-up tracker.
- An incident exposed gaps in alerts, runbooks, responsibility, deployment safety, or architecture standards.

## When Not To Use

- The work is pre-launch readiness with no incident; use `production-readiness-review` instead.
- The request is brand, PR, legal strategy, or customer-support policy beyond operational status communication.
- The user asks only to define telemetry; use `observability-and-alerting` instead.
- The user asks only to reduce alert fatigue; use `oncall-health` instead.

## Inputs To Collect

- Impact: affected users, journeys, severity, start/end times, data loss/corruption, and business-critical periods.
- Current state: active, mitigated, resolved, monitoring, or postmortem-only.
- Responders, roles, fallback path, user decision point, and communication channels.
- Available docs, dependency status, and user-provided contacts that can inform mitigation without blocking on an outside party.
- Timeline events: detection, triage, mitigation, customer communication, resolution, and recurrence.
- Mitigations attempted, evidence observed, dashboards/logs/traces used, and changes during the window.
- Contributing factors, missed signals, runbook gaps, responsibility gaps, and action-item candidates.

## Workflow

1. **During active impact, assign roles.** Use incident commander, operations lead, communications lead, and scribe when coordination requires them; for solo work, explicitly claim each role yourself.
2. **Classify ticket severity.** Use impact radius and urgency: highest severity for widespread critical user or data/security impact, high severity for major but bounded customer impact, medium severity for limited degradation or internal dependency risk, and low severity for a low-impact anomaly requiring follow-up.
3. **Put live-site impact first.** Treat customer-visible availability, health, and security as the top priority until impact is controlled.
4. **Mitigate before explaining.** Prefer actions that reduce user impact safely; postpone deep root-cause analysis until impact is controlled.
5. **Keep a live timeline.** Record timestamped facts, hypotheses, decisions, commands/actions, status updates, and responsibility changes.
6. **Communicate predictably.** Set status cadence by ticket severity; highest-severity incidents should update within 30 minutes or less, high-severity incidents within an hour, and lower severities by the user-confirmed cadence. Say what is known, unknown, impact, mitigation, and next update time.
7. **Change strategy when stuck.** Use the user, available documentation, dependency status, or a narrower diagnostic skill when impact persists, mitigation authority is unclear, or a latent risk is not getting traction. Do not wait for a vendor or outside group before taking the safest available mitigation.
8. **Checkpoint explicitly.** At every incident-commander or shift change, record state, current hypothesis, customer impact, in-flight actions, user decision point, comms cadence, and next decision point.
9. **Use the normal hotfix path where possible.** Reduce context switching by keeping review, artifact, branch, and rollout mechanics traceable even under urgency.
10. **Run security incidents as a protected track.** When confidentiality, integrity, identity, abuse, or data exposure may be involved, preserve evidence, restrict sensitive details to need-to-know responders, and keep operational facts separate from legal or policy conclusions.
11. **Stabilize and verify.** Confirm recovery with user-visible metrics, not only process health.
12. **Write a blameless postmortem.** Explain contributing factors across technical, operational, detection, review, and organizational layers.
13. **Replace single-root-cause wording with layered factors.** If the user supplies "root cause: X", treat X as one technical trigger, then add process, detection, rollout, responsibility, or organizational defenses that allowed impact; mark inferred factors as candidates to verify.
14. **Create verified actions.** Every action needs due date, observable completion signal, and classification: prevent, detect, mitigate, or learn.
15. **Feed standards.** Turn recurring classes into SLO, observability, safe-change, HA, dependency-resilience, or platform-improvement work.

## Synthesized Default

Use role-based incident command during response and blameless, contributing-factor postmortems after recovery. Prefer mitigation and clear communication over premature diagnosis. Treat security incidents as evidence-sensitive operational events, keep engineering accountable for live-site outcomes, and treat action items as engineering commitments with verification, not aspirations.



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

- Security, privacy, legal, or safety incidents may have confidentiality constraints; keep operating from verified facts and user-provided requirements.
- Very small internal incidents can use a lightweight review if impact, timeline, and action tracking remain explicit.
- If an incident is ongoing, delay final postmortem conclusions and keep outputs focused on response.
- Customer-facing wording may need user confirmation, but operational status cadence and facts remain in scope.

## Response Quality Bar

- Lead with the incident command plan, current mitigation posture, timeline, postmortem finding, or action register requested.
- Cover impact, severity, roles, timeline, communications cadence, mitigation, contributing factors, missed defenses, and verified actions before optional incident-process breadth.
- For postmortems, include a **Contributing Factors** section with at least three factors across at least two layers such as technical trigger, detection gap, rollout/process gap, responsibility/runbook gap, or organizational tradeoff; avoid presenting one root cause as the whole explanation.
- Make recommendations actionable with user decision point, timestamps, next-update times, verification conditions, due dates, and follow-up gates where relevant.
- State required evidence such as alerts, dashboards, logs, deploy markers, chat timeline, customer-impact data, mitigation commands, and action verification; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside incident response and postmortems. Use security/privacy constraints or specialist reliability checks only when they are central to the next action.
- Be concise: avoid generic blameless-postmortem theory and prefer compact timelines, status updates, and action tables.

## Required Outputs

- Incident role assignment and severity classification.
- Live or reconstructed timeline.
- Impact summary with detection, mitigation, and resolution times.
- Communications cadence and status-update skeleton.
- User-confirmed strategy-change trigger when mitigation stalls.
- Checkpoint packet for long incidents or responder changes.
- Postmortem with layered contributing factors and missed defenses, not only a root-cause statement.
- Action-item register with due date, observable verification signal, and category.
- Follow-up engineering checks for the relevant skill surfaces.

## Evidence Gates

- `impact_check`: user impact, severity, start/end or current state, and affected journeys are stated.
- `role_check`: response roles and user decision point are assigned or explicitly not needed.
- `timeline_check`: detection, triage, mitigation, communication, resolution, and key decisions are captured.
- `checkpoint_check`: long incidents or role changes include state, in-flight actions, comms cadence, and next decision point.
- `blameless_check`: postmortem focuses on system factors and avoids person-blame or single-root-cause simplification.
- `action_check`: every action has due date, verification condition, and category.

## Red Flags - Stop And Rework

- The incident review concludes "human error" without explaining system conditions.
- Timeline is reconstructed from memory with no timestamps or evidence.
- Action items say "be more careful", "monitor better", or "improve tests" without verification.
- Status updates have no next-update time.
- Responders keep investigating without changing mitigation strategy when mitigation is stalled or authority is unclear.
- Mitigation is delayed because responders are debating root cause during active impact.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Root-cause hunting during impact | Mitigate first, analyze after stabilization. |
| One action per symptom | Group by contributing factor and defense gap. |
| Blameless means consequence-free | Focus accountability on system improvements and verified actions. |
| Postmortem as paperwork | Feed findings into standards, platform, and reliability backlog. |
