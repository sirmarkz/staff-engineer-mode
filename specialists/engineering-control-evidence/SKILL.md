---
name: engineering-control-evidence
description: "Use when cross-surface engineering evidence packs, scorecards, exceptions, or control maps support delivery decisions"
---

# Engineering Control Evidence

## Iron Law

```
NO CROSS-SURFACE CONTROL MAP WITHOUT REPEATABLE EVIDENCE SOURCE, CADENCE, EXCEPTION PATH, AND REFRESH TRIGGER PER CONTROL
```

If a control cannot be inspected against a maintained, repeatable engineering artifact on a defined cadence, it is not part of this skill. Single-surface evidence belongs in the matching specialist skill.

> This skill assumes a multi-surface engineering evidence problem. The artifacts it produces (cross-surface control maps, engineering scorecards, exception registers) exist to coordinate evidence across different engineering surfaces. A solo developer can still use it when one project needs a combined evidence pack; single-domain evidence stays with the matching specialist skill.
> Even in a cross-project context, this skill aggregates locally available engineering evidence for the user. It does not wait for legal, manager, or external sign-off.

## Overview

Engineering controls are useful only when they are close to the work and produce evidence from engineering systems.

**Core principle:** aggregate evidence from artifacts projects already create: diffs, tests, build attestations, deployment records, runbooks, incidents, access-change records, scans, and exceptions.

## When To Use

- The request explicitly spans two or more engineering surfaces and asks for one evidence pack, scorecard, control-to-artifact map, or exception register.
- You need one normalized evidence inventory across SDLC, reliability, supply chain, access, vulnerability, observability, data, or operations because separate engineering surfaces otherwise duplicate tracking.
- The user asks how to prove engineering standards are followed across delivery and operations using artifacts from normal engineering work.
- Cross-surface engineering exceptions need expiry, compensating controls, residual risk, and revisit triggers in one register.
- A multi-surface engineering evidence pack is required and no single specialist covers the full surface set.

## When Not To Use

- The request is single-launch, single-traffic-shift, or tier-change readiness; use `production-readiness-review`.
- A single specialist covers the needed evidence directly: deployed vulnerability evidence belongs to `vulnerability-management`; build-path provenance belongs to `software-supply-chain-security`; identity, secrets, and access evidence belongs to `identity-and-secrets`; reliability target evidence belongs to `slo-and-error-budgets`; alert and telemetry evidence belongs to `observability-and-alerting`; backup and restore evidence belongs to `backup-and-recovery`; tenant boundary evidence belongs to `tenant-isolation`; data lifecycle evidence belongs to `privacy-and-data-lifecycle`; data pipeline evidence belongs to `data-pipeline-reliability`; threat-model evidence belongs to `secure-sdlc-and-threat-modeling`; AI-assisted change evidence belongs to `ai-coding-governance`.
- The user asks for evidence but actually wants a single-domain answer; use the matching specialist above.
- The request is broad compliance, legal, procurement, vendor risk, auditor-liaison program management, or business program management outside engineering lifecycle and operations.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Engineering standards, systems in scope, delivery decisions, and evidence consumers.
- Existing artifacts: PRs, CI logs, tests, scans, attestations, deployments, runbooks, incidents, access reviews, and dashboards.
- Evidence refresh cadence, exception rules, and risk acceptance authority.
- Current scorecards, manual collection burden, gaps, incidents, and recurring findings.
- Required engineering expectations or internal guidelines and how they map to engineering behavior.

## Workflow

1. **Gate on cross-surface scope.** Confirm the work spans at least two specialist engineering surfaces and that no single specialist covers the full evidence set. If the request is single-launch readiness, use `production-readiness-review`. If the request is single-domain evidence, use the matching specialist and stop.
2. **Map expectations to behavior.** Express each expectation as something engineers do, prevent, detect, confirm, test, or verify.
3. **Locate evidence near engineering work.** Prefer generated records from changes, CI, deploys, access systems, scanners, runbooks, and incidents.
4. **Assign responsibility and cadence.** Every evidence source needs an owner, refresh cadence, and failure response.
5. **Define exceptions.** Require expiry, compensating control, refresh trigger, and risk-acceptance authority appropriate to severity.
6. **Build scorecards carefully.** Score capabilities and evidence state, not vanity metrics. Normalize overlapping security, reliability, supply-chain, operations, and internal engineering expectations into one evidence map.
7. **Create standards backlog.** Record gaps from failed evidence pulls, expired exceptions, incidents, and recurring findings with severity, expected fix path, and target date.
8. **Feed findings back.** Use incidents, failed reviews, and recurring exceptions to update standards and platform defaults.

## Synthesized Default

Keep evidence close to engineering workflows and automate collection where possible. Use one expectation-to-evidence map across overlapping engineering standards, benchmarks, and internal checklists so projects do not maintain duplicate tracking or conflicting interpretations.



## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, gates, and evidence to collect.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness evidence.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Existing artifact: use current code, docs, telemetry, incidents, or diffs as evidence for the next engineering decision; do not wait for a finished artifact before guiding design, build, release, or operation.
- Missing evidence: state assumptions and produce the evidence plan instead of blocking lifecycle guidance.

## Exceptions

- Single-surface evidence should be produced by the specialist skill, with this skill only aggregating if needed.
- Manual evidence can be temporary when automation is not yet available, but it needs expiry and a replacement path.
- Legal/auditor-facing interpretation is out of scope; this skill produces engineering evidence, not legal claims.
- Threat-detection mapping is included only when detection coverage is explicitly in scope.

## Response Quality Bar

- Lead with the expectation-to-evidence map, scorecard, exception register, or evidence-pack outline requested.
- Cover engineering behavior, repeatable evidence sources, cadence, pass/fail states, exceptions, and workflow fit before optional program breadth.
- Make recommendations actionable with artifact sources, collection cadence, failure response, automation backlog, and exception expiry where relevant.
- State required evidence such as CI results, deploy records, configuration snapshots, change records, incident records, control outputs, and source artifact links; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering evidence. Do not make legal, procurement, staffing, or external-assurance claims.
- Be concise: avoid generic compliance language and prefer compact engineering evidence matrices.

## Required Outputs

- Engineering expectation-to-behavior-to-evidence map.
- Evidence inventory with source, cadence, and retention.
- Scorecard with pass/fail/exception states.
- Exception register with expiry, compensating controls, refresh trigger, residual risk, and acceptance authority.
- Evidence pack outline linked to source artifacts.
- Standards update backlog with gap source, engineering expectation, severity, expected fix path, and target date.

## Evidence Gates

- `scope_check`: request explicitly spans two or more engineering surfaces, no single specialist covers the full evidence set, and non-engineering program management is excluded.
- `evidence_source`: every expectation maps to a repeatable engineering artifact source.
- `cadence_check`: every evidence source has refresh cadence and failure response.
- `exception_check`: exceptions have expiry, compensating control, and refresh trigger.
- `workflow_fit`: evidence is collected from normal engineering workflows where possible.

## Red Flags - Stop And Rework

- Expectations are copied from standards without mapping to engineering behavior.
- Evidence is a screenshot someone must manually collect every quarter.
- Exceptions never expire.
- Scorecards reward document presence rather than control effectiveness.
- The skill is being used as lawyer, procurement owner, staffing owner, or compliance-program manager.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Central evidence chores | Put evidence in the workflow that creates it. |
| Duplicate maps per standard | Normalize overlapping expectations into one evidence map. |
| Open-ended exceptions | Add expiry, compensating control, and refresh trigger. |
| Using this for everything | Prefer domain skills for single-surface evidence. |
