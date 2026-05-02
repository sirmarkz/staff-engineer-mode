---
name: architecture-review-and-decision-records
description: "Use when system design, architecture review, ADRs, tradeoffs, or service boundaries are central."
---

# Architecture Review And Decision Records

## Overview

Architecture review turns a design from "components and opinions" into explicit goals, tradeoffs, ownership, failure modes, and decisions future maintainers can understand.

**Core principle:** review decisions by the forces they must satisfy: user outcomes, constraints, data, reliability, security, operability, evolvability, cost, and ownership.

## Iron Law

```
NO ARCHITECTURE DECISION WITHOUT CONTEXT, ALTERNATIVES, CONSEQUENCES, AND OWNERS
```

If the design lacks goals, non-goals, constraints, alternatives, risk, and ownership, do not approve it as reviewed.

## When To Use

- The user asks for system design, architecture review, RFC/design-doc review, ADRs, service boundaries, dependency direction, or tradeoff analysis.
- A change affects data ownership, public contracts, reliability, deployment topology, security boundaries, or operational responsibility.
- The user asks whether a monolith, module, service, workflow, platform component, or integration boundary "holds up".
- A prior decision needs to be recorded or revisited with current constraints.

## When Not To Use

- The user asks for live outage handling; use incident response.
- The request is only code style, naming, formatting, or local implementation review.
- The work is launch readiness aggregation; use production readiness review.
- The question is a narrow API compatibility issue; use API design and compatibility.

## Inputs To Collect

- Problem statement, users, goals, non-goals, constraints, and success criteria.
- Current and proposed architecture, data flows, trust boundaries, interfaces, and dependencies.
- Ownership model: teams, on-call, escalation, service tier, and decision owner.
- Alternatives considered, including "do nothing", "keep modular", and "split later".
- Reliability, security, privacy, deploy, data consistency, migration, and operational risks.
- Existing incidents, SLOs, costs, scale limits, compliance constraints, and roadmap pressures.

## Workflow

1. **Frame the decision.** Write the decision as one clear question and list goals, non-goals, and constraints before evaluating solutions.
2. **Map the system.** Identify data flow, control flow, dependency direction, ownership, trust boundaries, failure domains, and operational handoffs.
3. **Prefer simpler boundaries first.** Start with modular design and explicit contracts. Add distribution only for independent scaling, release cadence, ownership, isolation, or blast-radius needs.
4. **Compare alternatives.** Evaluate at least two real options plus the current state. Include consequences, rejected alternatives, and what would make the decision wrong later.
5. **Review cross-cutting risks.** Cover reliability, overload, data correctness, security, observability, deployment safety, recovery, cost, and maintainability.
6. **Record the decision.** Create an ADR or design-review summary with status, context, decision, consequences, owners, evidence, and follow-up routes.
7. **Route specialist gaps.** Send SLOs, HA, dependency resilience, secure design, rollout, or data consistency to the narrow skill when the design exposes that surface.

## Synthesized Default

Use a compact design review plus ADR. Keep the system modular and technology-agnostic until the design proves it needs distribution. When distribution is justified, make ownership, contracts, failure modes, observability, and deployability explicit before endorsing the split.

## Exceptions

- Exploratory prototypes can use a lightweight decision note if they are explicitly non-production and disposable.
- Regulated, security-sensitive, or tier-1 systems need a fuller risk register and evidence trail.
- Reversible local implementation choices may be documented in code or PR context instead of an ADR.
- If the system is already failing operationally, incident or reliability work may precede full architecture cleanup.

## Response Quality Bar

- Lead with the architecture decision, approval status, or highest-severity blockers.
- Cover goals, alternatives, ownership, boundaries, data flow, and failure modes before optional architecture breadth.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and follow-up decisions where relevant.
- State required evidence such as SLOs, traffic, incidents, data contracts, threat boundaries, and migration proof; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside the design under review. Add at most two specialist follow-ups, and only for material unresolved surfaces.
- Be concise: avoid generic architecture theory and prefer compact ADRs, decision tables, and risk registers.
- For pre-build, ticketing, or milestone-readiness requests, distinguish implementation tasks from unresolved architecture decisions. Use compact decision, risk/tradeoff, alternative, ownership, and gate tables; do not expand into a full narrative ADR unless the user asks for one.

## Required Outputs

- Architecture review summary with context, goals, non-goals, and constraints.
- ADR with status, decision, alternatives, consequences, and owner.
- System map covering data flow, dependencies, trust boundaries, and ownership.
- Risk register with likelihood, impact, mitigation, owner, and evidence.
- Decision table showing default, alternatives rejected, and exception conditions.
- Follow-up routes capped at two, each tied to a specific unresolved surface.

## Evidence Gates

- `decision_record`: the ADR states context, decision, status, owner, alternatives, and consequences.
- `goal_alignment`: every recommended architecture element maps to a goal, constraint, or risk.
- `boundary_check`: service/module boundaries have ownership, contracts, data ownership, and failure behavior.
- `risk_coverage`: reliability, security, data, deploy, observability, and operations risks are considered.
- `follow_up_cap`: no more than two follow-up skills are recommended unless the output is a sequencing plan.

## Red Flags - Stop And Rework

- The review names components but not owners, contracts, data flows, or failure modes.
- A distributed design is chosen because it is fashionable, not because constraints require it.
- Alternatives are missing or all alternatives are strawmen.
- The design pushes complexity into operations without on-call ownership or runbooks.
- Security, observability, migration, and rollback are deferred as "implementation details" for a high-risk decision.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating diagrams as decisions | Record the decision, forces, consequences, and owner. |
| Approving distribution too early | Prefer modular boundaries until scale, ownership, release, or blast-radius needs justify distribution. |
| Hiding rejected options | State what was rejected and why, so future maintainers do not repeat the debate. |
| Making architecture review a checklist | Tie every finding to a concrete risk, tradeoff, or decision. |
