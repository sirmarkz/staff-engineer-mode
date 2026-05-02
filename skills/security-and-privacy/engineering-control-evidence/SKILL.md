---
name: engineering-control-evidence
description: "Use when the user explicitly asks to map engineering standards or controls to repeatable artifacts, exception records, evidence packs, or scorecards across multiple engineering surfaces. Do not use for broad compliance program management, legal policy, vendor risk, procurement, auditor liaison work, or single-domain evidence that another skill should produce."
---

# Engineering Control Evidence

## Overview

Engineering controls are useful when they are close to the work and produce evidence automatically.

**Core principle:** map standards to the artifacts teams already create: PRs, tests, build attestations, deployment records, runbooks, incidents, access reviews, scans, and exceptions.

## Iron Law

```
NO CONTROL WITHOUT OWNER, EVIDENCE SOURCES, CADENCE, EXCEPTION PATH, AND REVIEW TRIGGER
```

If evidence is not repeatable and owned, it is not an engineering control.

## When To Use

- The user explicitly asks to map engineering standards or controls to evidence, scorecards, exception records, or repeatable artifacts across multiple engineering surfaces.
- A team needs one control map spanning SDLC, reliability, supply chain, access, vulnerability, observability, or operations.
- The user asks how to prove standards are followed without manual audit theater.
- Exceptions need owner, expiry, compensating controls, and re-review triggers.

## When Not To Use

- The request is broad compliance, legal, procurement, vendor risk, or auditor-liaison program management.
- A single domain skill can produce the needed evidence directly.
- The user only says "audit" but actually needs identity, supply-chain, vulnerability, or PRR evidence.
- The request is business governance outside engineering lifecycle and operations.

## Inputs To Collect

- Engineering standards, control objectives, systems in scope, owners, and evidence consumers.
- Existing artifacts: PRs, CI logs, tests, scans, attestations, deployments, runbooks, incidents, access reviews, and dashboards.
- Control frequency, review cadence, exception process, and risk acceptance authority.
- Current scorecards, manual evidence burden, gaps, incidents, and recurring findings.
- Required standards, control objectives, or internal guidelines and how they map to engineering behavior.

## Workflow

1. **Scope engineering controls.** Confirm the work spans at least two specialist engineering surfaces and is not broader compliance program management.
2. **Map control to behavior.** Express each control as something engineers do, prevent, detect, approve, test, or review.
3. **Locate evidence near workflow.** Prefer generated records from code review, CI, deploys, access systems, scanners, runbooks, and incidents.
4. **Assign ownership and cadence.** Every control needs owner, review frequency, and failure response.
5. **Define exceptions.** Require owner, expiry, compensating control, re-review trigger, and risk-acceptance authority appropriate to severity.
6. **Build scorecards carefully.** Score capabilities and evidence state, not vanity metrics. Normalize overlapping security, reliability, supply-chain, operations, and internal controls into one engineering evidence map.
7. **Create standards backlog.** Record gaps from failed evidence pulls, expired exceptions, incidents, and recurring findings with owner, severity, expected fix path, and target date.
8. **Feed findings back.** Use incidents, failed reviews, and recurring exceptions to update standards and platform defaults.

## Synthesized Default

Keep evidence close to engineering workflows and automate collection where possible. Use one control-to-evidence-to-owner map across overlapping standards, benchmarks, and internal checklists so teams do not maintain duplicate paperwork or conflicting interpretations.

## Exceptions

- Single-surface evidence should be produced by the specialist skill, with this skill only aggregating if needed.
- Manual evidence can be temporary when automation is not yet available, but it needs owner and expiry.
- Legal/auditor-facing interpretation is out of scope; this skill produces engineering evidence, not legal claims.
- Threat-detection mapping is included only when detection coverage is explicitly in scope.

## Response Quality Bar

- Lead with the control-to-evidence map, scorecard, exception register, or evidence-pack outline requested.
- Cover engineering behavior, repeatable evidence sources, owners, cadence, pass/fail states, exceptions, and workflow fit before optional governance breadth.
- Make recommendations actionable with owners, artifact sources, collection cadence, failure response, automation backlog, and exception expiry where relevant.
- State required evidence such as CI results, deploy records, configuration snapshots, review logs, incident records, control outputs, and source artifact links; do not claim unseen evidence.
- Stay inside engineering evidence. Do not make legal, procurement, staffing, or audit-opinion claims.
- Be concise: avoid generic compliance language and prefer compact control-evidence-owner matrices.

## Required Outputs

- Control-to-behavior-to-evidence map.
- Evidence inventory with owner, source, cadence, and retention.
- Scorecard with pass/fail/exception states.
- Exception register with owner, expiry, compensating controls, re-review trigger, residual risk, and acceptance authority.
- Evidence pack outline linked to source artifacts.
- Standards update backlog with gap source, control, owner, severity, expected fix path, and target date.

## Evidence Gates

- `scope_check`: request spans multiple engineering controls and excludes non-engineering program management.
- `evidence_source`: every control maps to a repeatable artifact source.
- `owner_cadence`: every control has owner, review cadence, and failure response.
- `exception_check`: exceptions have owner, expiry, compensating control, and review trigger.
- `workflow_fit`: evidence is collected from normal engineering workflows where possible.

## Red Flags - Stop And Rework

- Controls are copied from standards without mapping to engineering behavior.
- Evidence is a screenshot someone must manually collect every quarter.
- Exceptions never expire.
- Scorecards reward document presence rather than control effectiveness.
- The skill is being used as auditor, lawyer, procurement, or compliance-program manager.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Central paperwork | Put evidence in the workflow that creates it. |
| Duplicate maps per standard | Normalize overlapping controls into one evidence map. |
| Open-ended exceptions | Add owner, expiry, compensating control, and review trigger. |
| Using this for everything | Prefer domain skills for single-surface evidence. |
