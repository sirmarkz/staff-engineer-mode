---
name: architecture-decisions
description: "Use to design or review a system, write an ADR, or decide between competing service boundaries before code lands."
---

# Architecture Review And Decision Records

## Overview

Architecture review turns a design from "components and opinions" into explicit goals, tradeoffs, failure modes, and decisions future maintainers can understand. Works the same at any team size: the discipline is the forces-alternatives-reversal triple, not the org-chart artifact around it.

**Core principle:** review decisions by the forces they must satisfy: user outcomes, constraints, data, reliability, security, operability, evolvability, and cost.

## Iron Law

```
NO ARCHITECTURE DECISION WITHOUT FORCES, ALTERNATIVES, AND A REVERSAL PLAN
```

If the design lacks goals, constraints, alternatives considered, and an honest read on how hard the decision would be to undo, do not approve it as reviewed. Naming a maintainer matters too; for solo work the maintainer is you, and the rule is "no anonymous components," not "produce an org chart."

## When To Use

- The user asks for system design, architecture review, RFC/design-doc review, ADRs, service boundaries, dependency direction, or tradeoff analysis.
- A change affects data ownership, public contracts, reliability, deployment topology, security boundaries, or operational responsibility.
- The user asks whether a monolith, module, service, workflow, platform component, or integration boundary "holds up".
- A prior decision needs to be recorded or revisited with current constraints.

## When Not To Use

- The user asks for live outage handling; use `incident-response-and-postmortems`.
- The request is only code style, naming, formatting, or local implementation review; use `code-review-and-workflow`.
- The work is launch readiness aggregation; use `production-readiness-review`.
- The question is a narrow API compatibility issue; use `api-design-and-compatibility`.

## Inputs To Collect

- Problem statement, users, goals, non-goals, constraints, and success criteria.
- Current and proposed architecture, data flows, trust boundaries, interfaces, and dependencies.
- Maintainer: who decides this, who fixes it when it breaks, and (for multi-team systems) on-call, escalation, and service tier.
- Alternatives considered, including "do nothing", "keep modular", and "split later".
- Reliability, security, privacy, deploy, data consistency, migration, and operational risks.
- Existing incidents, SLOs, costs, scale limits, compliance constraints, and roadmap pressures.

## Workflow

1. **Frame the decision.** Write the decision as one clear question and list goals, non-goals, and constraints before evaluating solutions.
2. **Map the system.** Identify data flow, control flow, dependency direction, maintainer, trust boundaries, failure domains, and operational handoffs.
3. **Map bounded contexts.** Produce a bounded-context map naming each context, its maintainer (a team in larger orgs, a person in small ones), the language/model it uses, and the relationship to every adjacent context (upstream/downstream, conformist, anti-corruption layer, shared kernel, partnership, customer/supplier, separate ways). Note where a context translates a neighbor's model and where it conforms.
4. **Prefer simpler boundaries first.** Start with modular design and explicit contracts. Add distribution only for independent scaling, release cadence, ownership, isolation, or blast-radius needs.
5. **Compare alternatives.** Evaluate at least two real options plus the current state. Include consequences, rejected alternatives, and what would make the decision wrong later.
6. **Specify fitness functions.** Write the architectural invariants the system must hold as testable checks. Each fitness function names: the property under test, the metric, the threshold or rule, the measurement source, the evaluation cadence, the failure response, and the owner. Cover at minimum the dependency-direction rules, the public-contract compatibility rules, the latency or throughput budgets the boundary depends on, and any blast-radius or isolation invariant the design relies on.
7. **Review cross-cutting risks.** Cover reliability, overload, data correctness, security, observability, deployment safety, recovery, cost, and maintainability.
8. **Record the decision.** Create an ADR or design-review summary with status, context, decision, consequences, owners, evidence, fitness-function references, and follow-up routes.
9. **Route specialist gaps.** Send SLOs, HA, dependency resilience, secure design, rollout, or data consistency to the narrow skill when the design exposes that surface.

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
- Bounded-context map listing each context with fields: name, maintainer (team or person, depending on org size), model/language, upstream contexts, downstream contexts, relationship to each neighbor (conformist, anti-corruption layer, shared kernel, partnership, customer/supplier, separate ways), and the translation surface where a neighbor's model is adapted.
- Fitness-function specification listing each architectural invariant with fields: property under test, metric, threshold or rule, measurement source, evaluation cadence, failure response, and owner. Cover dependency-direction rules, public-contract compatibility, latency or throughput budgets the boundary depends on, and any blast-radius or isolation invariant.
- Risk register with likelihood, impact, mitigation, owner, and evidence.
- Decision table showing default, alternatives rejected, and exception conditions.
- Follow-up routes capped at two, each tied to a specific unresolved surface.

## Evidence Gates

- `decision_record`: the ADR states context, decision, status, owner, alternatives, and consequences.
- `goal_alignment`: every recommended architecture element maps to a goal, constraint, or risk.
- `boundary_check`: service/module boundaries have ownership, contracts, data ownership, and failure behavior.
- `context_map`: every named context has a maintainer, model, upstream and downstream neighbors, and the relationship pattern to each neighbor; translation surfaces are explicit where neighbors disagree on the model.
- `fitness_functions`: every architectural invariant the design depends on has a property, metric, threshold or rule, measurement source, evaluation cadence, failure response, and a maintainer; vague "should be fast" or "should be loosely coupled" entries are rejected as not testable.
- `risk_coverage`: reliability, security, data, deploy, observability, and operations risks are considered.
- `follow_up_cap`: no more than two follow-up skills are recommended unless the output is a sequencing plan.

## Red Flags - Stop And Rework

- The review names components but not their maintainer, contracts, data flows, or failure modes. (Solo work: maintainer is "me"; the rule is no anonymous components, not formal headcount.)
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
