---
name: resilience-experiments
description: "Use when asked to design or run a chaos test, game day, failover drill, or fault-injection experiment — with hypothesis, blast-radius bound, abort criteria, and a learning loop."
---

# Resilience Experiments And Chaos Engineering

## Iron Law

```
NO FAILURE EXPERIMENT WITHOUT HYPOTHESIS, BLAST RADIUS, ABORT CRITERIA, TELEMETRY, AND LEARNING LOOP
```

Breaking things without a learning objective is not engineering.

## Overview

Resilience experiments test whether the system behaves the way the design claims it will behave.

**Core principle:** run controlled experiments with a hypothesis, bounded blast radius, observable steady state, abort criteria, and follow-up fixes.

## When To Use

- The user asks for a chaos experiment, game day, failover drill, disaster role play, fault injection, or resilience test plan.
- You want evidence that retry, failover, overload, backup, or dependency-failure behavior works.
- You need to exercise location, partition, deployment-unit, traffic-shift, startup, or recovery behavior before relying on it.
- A production-readiness review needs controlled failure validation.
- Incident follow-up requires proving that a class of failure is now handled.

## When Not To Use

- The main deliverable is fault-domain topology, static stability, or multi-location design; use `high-availability-design` instead.
- The main deliverable is backup restore testing or RTO/RPO proof; use `backup-and-recovery` instead unless broader experiments are central.
- The main deliverable is timeout, retry, queue, or overload policy; use `dependency-resilience` instead.
- The work is only unit/integration testing without runtime failure injection.

## Inputs To Collect

- System tier, SLOs, critical journeys, known failure modes, and previous incident classes.
- Existing fault-domain map, dependency matrix, capacity model, and recovery runbooks.
- Steady-state signals: availability, latency, correctness, freshness, saturation, queue age, and user-impact indicators.
- Experiment target, injected fault, blast radius, duration, traffic scope, customer exposure, and abort criteria.
- Production cadence or trigger for recurring drills, based on tier and change rate.
- Participants, on-call coverage, communication channel, user decision point, and rollback/fallback actions.
- Evidence to capture, expected outcome, safety constraints, and follow-up tracking path.

## Workflow

1. **State the hypothesis.** Use the form: "If X fails, the system will continue Y within Z because controls A and B work."
2. **Define steady state.** Pick user-visible and causal signals before injecting failure.
3. **Bound the blast radius.** Start with shift-left simulation or staging when needed, then a small partition, tenant, shard, deployment unit, or traffic slice.
4. **Set abort criteria.** Decide in advance which SLO burn, error, latency, saturation, data, or operator signal stops the experiment.
5. **Prepare responders.** Confirm on-call, runbooks, rollback, communication channel, and user decision point.
6. **Inject one failure.** Change one variable at a time unless the explicit goal is compound-failure validation.
7. **Observe and decide.** Compare actual behavior to hypothesis, abort on criteria, and record evidence while the system is still fresh.
8. **Set recurrence deliberately.** For tier-critical recovery mechanisms, define when to repeat the drill after topology, traffic, dependency, or runbook changes.
9. **Close the loop.** File fixes, update runbooks, add regression checks, and rerun only after material changes.

## Synthesized Default

Use hypothesis-driven experiments that begin small, verify user-visible steady state, and expand only after evidence supports the previous scope. Treat shift-left experiments, shift-right production drills, and game days as engineering validation, not training theater.

## Exceptions

- Tabletop or disaster role play is appropriate before risky operational drills, but it does not replace technical validation.
- Production experiments may be inappropriate for safety-critical, destructive, or unbounded failure modes; use simulation or isolated environments.
- Compound failures are valid only after single-failure behavior is understood and observability is strong.
- Low-tier internal services may use lightweight drills when the user explicitly accepts the risk.

## Response Quality Bar

- Lead with the experiment hypothesis, blast-radius boundary, abort criteria, or evidence plan requested.
- Cover steady state, fault method, scope, telemetry, participant/communication plan, rollback actions, evidence capture, and learning loop before optional chaos-program breadth.
- Make recommendations actionable with exact fault injection, thresholds, stop trigger, rollback commands, evidence to capture, and rerun criteria where relevant.
- State required evidence such as dashboards, SLO signals, deployment markers, runbooks, dependency health, experiment logs, findings, and fix paths; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside resilience experiment design and execution. Route HA redesign or DR strategy only when the experiment exposes those as central gaps.
- Be concise: avoid generic chaos-engineering background and prefer compact experiment plans and findings tables.

## Required Outputs

- Experiment hypothesis.
- Steady-state signal list and dashboard links.
- Fault injection method and blast-radius boundary.
- Abort criteria and rollback/fallback actions.
- Recurrence trigger, deadline, or cadence for critical recovery claims.
- Participant, on-call, and communication plan.
- Evidence capture checklist.
- Findings, fixes, and rerun condition.

## Evidence Gates

- `hypothesis_check`: experiment states failure, expected behavior, and resilience mechanism.
- `blast_radius`: affected users, partitions, tenants, shards, locations, or traffic percentage are bounded.
- `abort_criteria`: stop thresholds and user decision point are defined before the experiment.
- `telemetry_check`: steady-state and causal signals are visible during the test.
- `learning_loop`: findings create maintained fixes or explicit risk acceptance.
- `recurrence_rule`: critical recovery behavior has a repeat trigger, deadline, or cadence tied to tier, topology change, or incident learning.

## Red Flags - Stop And Rework

- The plan says "run chaos" but names no hypothesis.
- The failure can affect all customers before anyone can abort.
- Only infrastructure health is monitored while user impact is unknown.
- The drill depends on manual heroics that are not documented or repeatable.
- Findings are recorded but no fix path or rerun condition exists.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating chaos as random failure | Inject a specific fault to test a specific claim. |
| Starting too large | Prove behavior in the smallest useful blast radius first. |
| Ignoring correctness | Include data correctness, freshness, and side effects, not just uptime. |
| Ending at the debrief | Convert findings into fixes, tests, and runbook updates. |
