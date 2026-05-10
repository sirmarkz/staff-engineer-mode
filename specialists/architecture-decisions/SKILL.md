---
name: architecture-decisions
description: "Use when system design, ADRs, service/module/worker boundaries, or architecture tradeoffs need review"
---

# Architecture Review And Decision Records

## Iron Law

```
NO ARCHITECTURE DECISION WITHOUT FORCES, ALTERNATIVES, AND A REVERSAL PLAN
```

If the design lacks goals, constraints, alternatives considered, and an honest read on how hard the decision would be to undo, do not mark it as reviewed. Naming the responsibility path matters too; for solo work it is the user and agent evidence path, not an org chart.

## Overview

Architecture review turns a design from "components and opinions" into explicit goals, tradeoffs, failure modes, and decisions future readers can understand. Works the same at any project size: the discipline is the forces-alternatives-reversal triple, not the org-chart artifact around it. Review decisions by the forces they must satisfy: user outcomes, constraints, data, reliability, security, operability, evolvability, and cost.

## When To Use

- System design, architecture review, RFC/design-doc review, ADRs, service boundaries, dependency direction, or tradeoff analysis.
- A change affects data responsibility, public contracts, reliability, deployment topology, security boundaries, or operational responsibility.
- Whether a monolith, module, service, workflow, platform component, or integration boundary "holds up".
- A prior decision needs to be recorded or revisited with current constraints.

## When Not To Use

- Live outage handling: use `incident-response-and-postmortems`.
- Code style, naming, formatting, or local implementation review: use `code-review-and-workflow`.
- Launch readiness aggregation: use `production-readiness-review`.
- Narrow API compatibility issue: use `api-design-and-compatibility`.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Problem statement, users, goals, non-goals, constraints, success criteria.
- Current and proposed architecture, data flows, trust boundaries, interfaces, dependencies, and runtime responsibility model.
- Operability evidence: how the user or agent debugs, replaces, or degrades around the design, what the fallback path is, and where that path is tested or documented.
- Alternatives considered, including "do nothing", "keep modular", "split later".
- Reliability, security, privacy, deploy, data consistency, migration, operational risks.
- Existing incidents, SLOs, costs, scale limits, compliance constraints, roadmap pressures.

## When Inputs Are Referenced But Not Visible

If the user references an artifact (sketch, RFC, diff, diagram) that is not in
the workspace or thread, do not stop at "please paste it." Produce a
strawman ADR draft from the prompt's named subject (e.g., "split search
service") with: (a) a Forces table listing ≥2 likely forces with rationale,
(b) an Alternatives table with ≥2 named options and rejection reasons,
(c) an explicit Decision line plus a Consequences table split into Positive /
Negative columns, (d) a Reversibility row with cost-to-undo and the trigger
that would force reconsideration, and (e) a responsibility field. Mark every
inferred field as ASSUMED so the user can correct it.

## Workflow

1. **Frame the decision.** Write the decision as one clear question and list goals, non-goals, and constraints before evaluating solutions.
2. **Emit a compact ADR-shaped first answer.** Before asking for more artifacts, give the user a usable review skeleton containing: decision question, context/forces with rationale, explicit decision status or decision, at least two rejected alternatives with reasons, positive and negative consequences, reversibility cost and reconsideration trigger, and responsibility path. Mark unknowns as `ASSUMED` or `NEEDS EVIDENCE` instead of omitting the section.
3. **Map the system.** Identify data flow, control flow, dependency direction, trust boundaries, failure domains, and operational checkpoints.
4. **Map bounded contexts.** Produce a bounded-context map naming each context, its responsibility path, the language/model it uses, and the relationship to every adjacent context (upstream/downstream, conformist, anti-corruption layer, shared kernel, partnership, customer/supplier, separate ways). Note where a context translates a neighbor's model and where it conforms.
5. **Prefer simpler boundaries first.** Start with modular design and explicit contracts. Add distribution only for independent scaling, release cadence, responsibility, isolation, or blast-radius needs.
6. **Compare alternatives.** Evaluate at least two real options plus the current state. Include consequences, rejected alternatives, and what would make the decision wrong later.
7. **Specify fitness functions.** Write the architectural invariants the system must hold as testable checks. Each fitness function names: the property under test, the metric, the threshold or rule, the measurement source, the evaluation cadence, the failure response, and the local evidence path. Cover at minimum the dependency-direction rules, the public-contract compatibility rules, the latency or throughput budgets the boundary depends on, and any blast-radius or isolation invariant the design relies on.
8. **Review runtime dependency responsibility.** For any critical runtime dependency, state how the user or agent can debug it, patch or change it, work around issues, and exit or degrade if it fails. Keep this at design-time adoption criteria; timeout/retry policy goes to `dependency-resilience`, and launch evidence goes to `production-readiness-review`.
9. **Review cross-cutting risks.** Cover reliability, overload, data correctness, security, observability, deployment safety, recovery, cost, and maintainability.
10. **Record the decision.** Create an ADR or design-review summary with status, context (≥2 forces with rationale), decision, consequences (split positive and negative), reversibility (cost + reconsideration trigger), evidence, fitness-function references, and follow-up checks.
11. **Use specialist checks internally.** Apply the SLO, HA, dependency resilience, secure design, rollout, or data consistency skill when the design exposes that surface.

## Synthesized Default

Use a compact design review plus ADR. Keep the system modular and technology-agnostic until the design proves it needs distribution. When distribution is justified, make responsibility, contracts, failure modes, observability, and deployability explicit before endorsing the split.



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

- Exploratory prototypes can use a lightweight decision note if explicitly non-production and disposable.
- Regulated, security-sensitive, or tier-1 systems need a fuller risk register and evidence trail.
- Reversible local implementation choices may be documented in code or PR context instead of an ADR.
- If the system is already failing operationally, incident or reliability work may precede full architecture cleanup.

## Response Quality Bar

- Lead with the architecture decision, decision status, or highest-severity blockers.
- Cover goals, alternatives, responsibility, boundaries, data flow, and failure modes before optional architecture breadth.
- Make recommendations actionable with evidence, gates, stop conditions, and follow-up decisions.
- State required evidence such as SLOs, traffic, incidents, data contracts, threat boundaries, and migration proof; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside the design under review. Add at most two specialist follow-ups, only for material unresolved surfaces.
- Be concise: prefer compact ADRs, decision tables, and risk registers over generic architecture theory.
- For pre-build, ticketing, or milestone-readiness requests, distinguish implementation tasks from unresolved architecture decisions. Use compact decision, risk/tradeoff, alternative, responsibility, and gate tables; do not expand into a full narrative ADR unless asked.

## Required Outputs

- Architecture review summary with context, goals, non-goals, and constraints.
- ADR with status, decision, alternatives, consequences, and a concrete responsibility value (user, agent evidence path, or supplied project role; if unknown, use `ASSUMED: <component> responsibility path` rather than a blank or `TBD`).
- System map covering data flow, dependencies, trust boundaries, and responsibility.
- Runtime dependency adoption criteria covering supportability, changeability, fallback, and exit/degradation path.
- Bounded-context map listing each context with fields: name, responsibility path, model/language, upstream contexts, downstream contexts, relationship to each neighbor (conformist, anti-corruption layer, shared kernel, partnership, customer/supplier, separate ways), and the translation surface where a neighbor's model is adapted.
- Fitness-function specification listing each architectural invariant with fields: property under test, metric, threshold or rule, measurement source, evaluation cadence, failure response, and local evidence path. Cover dependency-direction rules, public-contract compatibility, latency or throughput budgets the boundary depends on, and any blast-radius or isolation invariant.
- Risk register with likelihood, impact, mitigation, and evidence.
- Decision table showing default, alternatives rejected, and exception conditions.
- Follow-up checks capped at two, each tied to a specific unresolved surface.

## Evidence Gates

- `decision_record`: the ADR states context, decision, status, alternatives, and consequences.
- `goal_alignment`: every recommended architecture element maps to a goal, constraint, or risk.
- `boundary_check`: service/module boundaries have responsibility, contracts, data responsibility, and failure behavior.
- `context_map`: every named context has a model, upstream and downstream neighbors, and the relationship pattern to each neighbor; translation surfaces are explicit where neighbors disagree on the model.
- `fitness_functions`: every architectural invariant the design depends on has a property, metric, threshold or rule, measurement source, evaluation cadence, failure response, and local evidence path; vague "should be fast" or "should be loosely coupled" entries are rejected as not testable.
- `risk_coverage`: reliability, security, data, deploy, observability, and operations risks are considered.
- `dependency_responsibility`: critical runtime dependencies have supportability, change path, fallback path, and exit or degradation plan.
- `follow_up_cap`: no more than two follow-up skills are recommended unless the output is a sequencing plan.

## Red Flags - Stop And Rework

- Components are named without their contracts, data flows, or failure modes. (Solo work: the responsibility path is "user + local evidence"; the rule is no anonymous components, not formal headcount.)
- A distributed design is chosen because it is fashionable, not because constraints require it.
- Alternatives are missing or all alternatives are strawmen.
- The design pushes complexity into operations without on-call responsibility or runbooks.
- A critical runtime dependency is accepted even though the user or agent has no path to debug, change, replace, or degrade around it from local tools and evidence.
- Security, observability, migration, and rollback are left as "implementation details" for a high-risk decision.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating diagrams as decisions | Record the decision, forces, consequences, and responsibility path. |
| Approving distribution too early | Prefer modular boundaries until scale, responsibility, release, or blast-radius needs justify it. |
| Hiding rejected options | State what was rejected and why, so future readers do not repeat the debate. |
