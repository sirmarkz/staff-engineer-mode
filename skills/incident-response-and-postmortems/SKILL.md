---
name: incident-response-and-postmortems
description: "Use to run an active incident, write a postmortem, or set status-update cadence — anything from 'we have an outage right now' to 'we need a writeup with action items'."
---

# Incident Response And Postmortems

## Overview

Produces incident roles and severity, a live timeline, a status-update cadence, a handoff packet for shift changes, and a blameless postmortem whose action items have owners, due dates, and observable verification signals. Refuses "human error" as a conclusion and refuses action items that read "be more careful".

**Core principle:** coordinate clear roles, mitigate impact, preserve a timeline, communicate predictably, and convert learning into verified engineering improvements.

## Iron Law

```
NO INCIDENT WITHOUT ROLES, IMPACT, AND STATUS CADENCE; NO POSTMORTEM WITHOUT TIMELINE, CONTRIBUTING FACTORS, AND VERIFIED ACTIONS
```

The two halves are co-designed: live response is unsafe without named responders, declared impact, and a predictable next-update time; a postmortem that only names a root cause or a person has not explained the system. For a solo developer the responder roles collapse onto one person, but the role labels still have to be claimed explicitly so nothing falls between them.

## When To Use

- The user asks for outage handling, incident command, severity, status updates, response roles, timelines, postmortems, or action items.
- A customer-impacting degradation, data issue, security event, or operational emergency is active or recently resolved.
- The team needs a blameless review or follow-up tracker.
- An incident exposed gaps in alerts, runbooks, ownership, deployment safety, or architecture standards.

## When Not To Use

- The work is pre-launch readiness with no incident; defer to `production-readiness-review`.
- The request is brand, PR, legal strategy, or customer-support policy beyond operational status communication.
- The user asks only to define telemetry; defer to `observability-and-alerting`.
- The user asks only to reduce alert fatigue; defer to `oncall-health`.

## Inputs To Collect

- Impact: affected users, journeys, severity, start/end times, data loss/corruption, and business-critical periods.
- Current state: active, mitigated, resolved, monitoring, or postmortem-only.
- Responders, roles, escalation path, decision authority, and communication channels.
- Timeline events: detection, triage, mitigation, customer communication, resolution, and recurrence.
- Mitigations attempted, evidence observed, dashboards/logs/traces used, and changes during the window.
- Contributing factors, missed signals, runbook gaps, ownership gaps, and action-item candidates.

## Workflow

1. **During active impact, assign roles.** Use incident commander, operations lead, communications lead, scribe, and subject experts when coordination requires them.
2. **Classify severity.** Use impact radius and urgency: highest severity for widespread critical user or data/security impact, high severity for major but bounded customer impact, medium severity for limited degradation or internal dependency risk, low severity for low-impact anomaly requiring follow-up.
3. **Put live-site impact first.** Treat customer-visible availability, health, and security as the top priority until impact is controlled.
4. **Mitigate before explaining.** Prefer actions that reduce user impact safely; defer deep root-cause analysis until impact is controlled.
5. **Keep a live timeline.** Record timestamped facts, hypotheses, decisions, commands/actions, status updates, and ownership changes.
6. **Communicate predictably.** Set status cadence by severity; highest severity should update within 30 minutes or less, high severity within an hour, and lower severities by stated owner cadence. Say what is known, unknown, impact, mitigation, and next update time.
7. **Handoff explicitly.** At every incident-commander or shift change, hand off state, current hypothesis, customer impact, in-flight actions, decision authority, comms cadence, and next decision point.
8. **Use the normal hotfix path where possible.** Reduce context switching by keeping review, artifact, branch, and rollout mechanics traceable even under urgency.
9. **Run security incidents as a protected track.** When confidentiality, integrity, identity, abuse, or data exposure may be involved, preserve evidence, restrict sensitive details to need-to-know responders, and keep operational facts separate from legal or policy conclusions.
10. **Stabilize and verify.** Confirm recovery with user-visible metrics, not only process health.
11. **Write a blameless postmortem.** Explain contributing factors across technical, operational, detection, review, and organizational layers.
12. **Create verified actions.** Every action needs owner, due date, observable completion signal, and classification: prevent, detect, mitigate, or learn.
13. **Feed standards.** Route recurring classes to SLOs, observability, safe change, HA, dependency resilience, or platform improvements.

## Synthesized Default

Use role-based incident command during response and blameless, contributing-factor postmortems after recovery. Prefer mitigation and clear communication over premature diagnosis. Treat security incidents as evidence-sensitive operational events, keep engineering accountable for live-site outcomes, and treat action items as engineering commitments with verification, not aspirations.

## Exceptions

- Security, privacy, legal, or safety incidents may require additional confidential process outside this skill while preserving operational facts.
- Very small internal incidents can use a lightweight review if impact, timeline, and action tracking remain explicit.
- If an incident is ongoing, defer final postmortem conclusions and keep outputs focused on response.
- Customer-facing wording may need communications review, but operational status cadence and facts remain in scope.

## Response Quality Bar

- Lead with the incident command plan, current mitigation posture, timeline, postmortem finding, or action register requested.
- Cover impact, severity, roles, timeline, communications cadence, mitigation, contributing factors, missed defenses, and verified actions before optional incident-process breadth.
- Make recommendations actionable with owners, decision authority, timestamps, next-update times, verification conditions, due dates, and follow-up gates where relevant.
- State required evidence such as alerts, dashboards, logs, deploy markers, chat timeline, customer-impact data, mitigation commands, and action verification; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside incident response and postmortems. Route security/privacy confidential process or specialist reliability fixes only when they are central to the next action.
- Be concise: avoid generic blameless-postmortem theory and prefer compact timelines, status updates, and action tables.

## Required Outputs

- Incident role assignment and severity classification.
- Live or reconstructed timeline.
- Impact summary with detection, mitigation, and resolution times.
- Communications cadence and status-update skeleton.
- Handoff packet for long incidents or responder changes.
- Postmortem with contributing factors and missed defenses.
- Action-item register with owner, due date, observable verification signal, and category.
- Follow-up routes to the relevant engineering skills.

## Evidence Gates

- `impact_check`: user impact, severity, start/end or current state, and affected journeys are stated.
- `role_check`: response roles and decision authority are assigned or explicitly not needed.
- `timeline_check`: detection, triage, mitigation, communication, resolution, and key decisions are captured.
- `handoff_check`: long incidents or role changes include state, in-flight actions, comms cadence, and next decision point.
- `blameless_check`: postmortem focuses on system factors and avoids person-blame or single-root-cause simplification.
- `action_check`: every action has owner, due date, verification condition, and category.

## Red Flags - Stop And Rework

- The incident review concludes "human error" without explaining system conditions.
- Timeline is reconstructed from memory with no timestamps or evidence.
- Action items say "be more careful", "monitor better", or "improve tests" without verification.
- Status updates have no next-update time.
- Mitigation is delayed because responders are debating root cause during active impact.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Root-cause hunting during impact | Mitigate first, analyze after stabilization. |
| One action per symptom | Group by contributing factor and defense gap. |
| Blameless means consequence-free | Focus accountability on system improvements and verified actions. |
| Postmortem as paperwork | Feed findings into standards, platform, and reliability backlog. |
