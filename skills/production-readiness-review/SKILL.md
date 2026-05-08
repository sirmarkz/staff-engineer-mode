---
name: production-readiness-review
description: "Use when launch, migration, tier change, major traffic shift, or release needs go/no-go readiness evidence"
---

# Production Readiness Review

## Iron Law

```
NO LAUNCH READINESS CLAIM WITHOUT EVIDENCE OR A DATED EXCEPTION
```

Unknown is not green. Missing evidence is a blocker, a recorded follow-up with evidence path and due date, or explicit user risk acceptance.

## Overview

Produces a tier-classified launch posture with an evidence matrix, a blocker list, and an exception register with expiry dates. Stops launches that confuse intentions for evidence. Unknown is not green.

**Core principle:** before launch or major traffic shift, prove — with artifacts, not intentions — that responsibility, reliability, observability, safe change, security, capacity, recovery, and incident paths are good enough for the declared tier.

## When To Use

- The user asks whether a service, feature, migration, tier upgrade, major traffic shift, or system is ready for production.
- A launch touches multiple engineering surfaces and needs one readiness posture.
- The user asks for production audit across responsibility, SLOs, rollout, security, capacity, recovery, and operations.
- You need blockers, exceptions, and follow-up routes before go/no-go.

## When Not To Use

- A small code change has no production responsibility, operational, security, or reliability impact.
- The user needs one narrow artifact, such as only an SLO table (use `slo-and-error-budgets` instead) or only a threat model (use `secure-sdlc-and-threat-modeling` instead).
- A live incident is underway; route to `incident-response-and-postmortems` first.
- The question is business confirmation, marketing launch, legal release decision, or procurement; out of scope.

## Inputs To Collect

- Launch scope, tier, customer/user impact, production dependencies, and user decision point.
- Architecture artifact: component diagram or textual component map, request/data flow, upstream and downstream dependencies, and fault-domain boundaries.
- Operability: who can run the launch, fallback path, diagnostics, incident path, and user decision point.
- SLOs/error budgets, dashboards, alerts, runbooks, and incident communication path.
- Availability posture: location independence, partition survivability, static failover capacity, and recovery drill evidence.
- Rollout plan, rollback path, canary metrics, migration plan, and feature/config lifecycle.
- Security posture: threat model, data classification, access controls, secrets, supply-chain controls, and vulnerability status.
- Capacity, load-test evidence, overload behavior, failover target, and dependency quotas.
- Backup/restore, DR evidence, data migration validation, and destructive-change safeguards.
- Open risks, exceptions, compensating controls, expiry dates, and follow-up actions.

## Workflow

1. **Classify launch tier and scope.** State what is launching, who is affected, and which standard applies.
2. **Apply the default tier rubric.** Tier 1 means externally committed, customer-critical, sensitive-data, stateful, or safety-critical impact; Tier 2 means user-visible degradation with bounded blast radius; Tier 3 means internal or shared-service impact; Tier 4 means isolated prototype or experiment.
3. **Collect artifacts.** Gather evidence from specialist domains instead of rewriting all domain work inside PRR.
4. **Review architecture shape.** Identify the component diagram or textual map, production dependencies, and fault-domain map for the launch path; if these are missing for a customer-impacting launch, mark the architecture evidence gap explicitly.
5. **Mark each domain.** Use Pass, Blocker, Exception, Follow-up, or Not Applicable. A gap is a Blocker when it can violate the tier's user, data, security, recovery, or rollback requirement before launch; it is a Follow-up only when launch risk remains bounded and the follow-up action, evidence path, and due date are explicit.
6. **Check runtime readiness.** Require SLOs, journey health model, telemetry, alerts, runbooks, fallback path, diagnostics, and incident path for customer-impacting launches.
7. **Check change readiness.** Require rollout, rollback, canary, compatibility, migration, and cleanup evidence.
8. **Check resilience and recovery.** Require location or partition independence, static failover capacity, overload behavior, failover claims, recovery drills, and restore evidence when relevant.
9. **Check security and integrity.** Require threat model, access controls, secret handling, build integrity, and unresolved vulnerability posture.
10. **Check cross-pillar tradeoffs.** Identify reliability, security, cost, operational, and performance decisions that improve one quality while weakening another.
11. **Summarize advisory posture.** Produce blockers, exceptions, and follow-up routes. The skill identifies objective blockers and readiness gaps; the user decides whether to proceed.

## Synthesized Default

Use PRR as a cross-domain evidence review for launches and major changes. It should inspect available evidence, identify missing artifacts, expose cross-pillar tradeoffs, and route only the highest-risk gaps. It should not auto-load every specialist skill.

## Exceptions

- Internal prototypes may use advisory PRR if they cannot affect customers, production data, or shared infrastructure.
- Tier-1, regulated, stateful, or externally committed systems require stricter evidence and dated risk acceptance.
- Emergency launches can proceed with documented risk when delaying is worse, but follow-up evidence and post-launch review are mandatory.
- A domain can be Not Applicable only with the disqualifying property, evidence, and reason, not by omission.

## Response Quality Bar

- Lead with the launch posture, blocker list, exception register, or readiness decision boundary requested.
- Cover architecture, responsibility, runtime readiness, safe change, recovery, security, and capacity evidence before optional PRR breadth.
- Include an architecture evidence row for customer-impacting launches: component diagram or textual map, dependencies, and fault-domain map.
- Make recommendations actionable with missing evidence, gates, due dates, stop criteria, user risk acceptance, and exception expiry where relevant.
- State required evidence such as dashboards, SLOs, rollout plans, runbooks, load tests, restore proof, threat models, and vulnerability status; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside launch readiness. Route only the highest-risk specialist follow-ups and cap them at two unless the user asks for a full audit.
- Be concise: avoid generic checklist prose and prefer compact evidence matrices, blocker tables, and exception registers.

## Required Outputs

- PRR evidence matrix by domain and status.
- Architecture review entry with component diagram or textual map, production dependencies, and fault-domain map.
- Availability evidence row covering fault-domain independence, static capacity under loss, recovery mechanism, and drill evidence.
- Launch blocker list with required evidence, file/path or artifact reference, and due date.
- Exception register with user risk acceptance, expiry, compensating control, and review trigger.
- Advisory launch posture and risk summary.
- Specialist follow-up routes, capped and prioritized.
- Tier classification and advisory boundaries: what the skill can mark as blocker, exception, follow-up, or not applicable versus who decides launch.

## Evidence Gates

- `tier_check`: tier classification states impact radius, data sensitivity, statefulness, external commitment, and user decision point.
- `architecture_check`: architecture evidence includes component diagram or textual component map, production dependencies, and fault-domain map for the affected launch path.
- `operability_check`: every production component has fallback path, diagnostics, tier, and user decision point.
- `runtime_check`: customer-impacting paths have SLOs, health states, telemetry, alerts, runbooks, and incident path.
- `change_check`: rollout, rollback, canary metrics, compatibility, and cleanup are documented.
- `availability_check`: customer-impacting systems have location/partition independence, static failed-domain capacity, recovery path, and validation evidence or an explicit exception.
- `recovery_check`: stateful or tier-critical systems have restore/DR evidence or an explicit exception.
- `exception_check`: every accepted risk has explicit user acceptance, expiry, compensating control, and review trigger.

## Red Flags - Stop And Rework

- The checklist is green but has no links, commands, artifact references, or explicit user decision point.
- PRR gives go/no-go authority to the agent instead of presenting evidence for the user decision.
- Exceptions never expire.
- The launch can roll forward but cannot roll back or stop safely.
- "Not applicable" is used to avoid security, recovery, or incident evidence without rationale.
- A missing blocker is downgraded to follow-up without stating why the launch risk remains bounded.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating PRR as a mega-skill | Aggregate evidence and route gaps to specialists. |
| Counting intentions as evidence | Require artifacts, commands, dashboards, runbooks, or dated exceptions. |
| Making all risks equal | Separate blockers from accepted exceptions and follow-ups. |
| Forgetting responsibility | Every blocker and exception needs evidence, expiry, and user decision point. |
