---
name: engineering-control-evidence
description: "Use when asked to build a cross-surface evidence pack, scorecard, or exception register that maps engineering standards to artifacts projects already produce — for audits, governance reviews, or program-level reporting that spans two or more specialist surfaces."
---

# Engineering Control Evidence

## Iron Law

```
NO CROSS-SURFACE CONTROL MAP WITHOUT REPEATABLE EVIDENCE SOURCE, CADENCE, EXCEPTION PATH, AND REVIEW TRIGGER PER CONTROL
```

If a control cannot be inspected against a maintained, repeatable artifact on a defined cadence, it is not an engineering control. Single-surface evidence belongs in the matching specialist skill.

> This skill assumes a multi-surface evidence problem. The artifacts it produces (cross-surface control maps, scorecards, exception registers) exist to coordinate evidence across different engineering surfaces. A solo developer can still use it when one project needs a combined evidence pack; single-domain evidence stays with the matching specialist skill.
> Even in a cross-project context, this skill aggregates locally available engineering evidence for the user. It does not wait for audit, legal, manager, or external sign-off.

## Overview

Engineering controls are useful when they are close to the work and produce evidence automatically.

**Core principle:** map standards to the artifacts projects already create: PRs, tests, build attestations, deployment records, runbooks, incidents, access reviews, scans, and exceptions.

## When To Use

- The request explicitly spans two or more engineering surfaces and asks for a single cross-surface control map, evidence pack, scorecard, or exception register.
- You need one normalized control inventory across SDLC, reliability, supply chain, access, vulnerability, observability, data, or operations because overlapping standards would otherwise produce duplicate paperwork.
- The user asks how to prove engineering standards are followed across the organization without per-surface manual audit theater.
- Cross-surface exceptions need expiry, compensating controls, residual risk, and re-review triggers in one register.
- A multi-surface audit-evidence pack is required and no single specialist covers the full surface set.

## When Not To Use

- The request is single-launch, single-traffic-shift, or tier-change readiness; use `production-readiness-review`.
- The request is review selection, change size, responsibility rules, or workflow metrics; use `code-review-and-workflow`.
- A single specialist covers the needed evidence directly: deployed vulnerability evidence belongs to `vulnerability-management`; build-path provenance belongs to `software-supply-chain-security`; identity, secrets, and access evidence belongs to `identity-and-secrets`; reliability target evidence belongs to `slo-and-error-budgets`; alert and telemetry evidence belongs to `observability-and-alerting`; backup and restore evidence belongs to `backup-and-recovery`; tenant boundary evidence belongs to `tenant-isolation`; data lifecycle evidence belongs to `privacy-and-data-lifecycle`; data pipeline evidence belongs to `data-pipeline-reliability`; threat-model evidence belongs to `secure-sdlc-and-threat-modeling`; AI-assisted change evidence belongs to `ai-coding-governance`.
- The user says "audit" but actually wants single-domain evidence; use the matching specialist above.
- The request is broad compliance, legal, procurement, vendor risk, auditor-liaison program management, or business governance outside engineering lifecycle and operations.

## Inputs To Collect

- Engineering standards, control objectives, systems in scope, and evidence consumers.
- Existing artifacts: PRs, CI logs, tests, scans, attestations, deployments, runbooks, incidents, access reviews, and dashboards.
- Control frequency, review cadence, exception process, and risk acceptance authority.
- Current scorecards, manual evidence burden, gaps, incidents, and recurring findings.
- Required standards, control objectives, or internal guidelines and how they map to engineering behavior.

## Workflow

1. **Gate on cross-surface scope.** Confirm the work spans at least two specialist engineering surfaces and that no single specialist covers the full evidence set. If the request is single-launch readiness, use `production-readiness-review`. If the request is single-domain evidence, use the matching specialist and stop.
2. **Map control to behavior.** Express each control as something engineers do, prevent, detect, confirm, test, or review.
3. **Locate evidence near workflow.** Prefer generated records from code review, CI, deploys, access systems, scanners, runbooks, and incidents.
4. **Assign responsibility and cadence.** Every control needs review frequency, and failure response.
5. **Define exceptions.** Require expiry, compensating control, re-review trigger, and risk-acceptance authority appropriate to severity.
6. **Build scorecards carefully.** Score capabilities and evidence state, not vanity metrics. Normalize overlapping security, reliability, supply-chain, operations, and internal controls into one engineering evidence map.
7. **Create standards backlog.** Record gaps from failed evidence pulls, expired exceptions, incidents, and recurring findings with severity, expected fix path, and target date.
8. **Feed findings back.** Use incidents, failed reviews, and recurring exceptions to update standards and platform defaults.

## Synthesized Default

Keep evidence close to engineering workflows and automate collection where possible. Use one control-to-evidence map across overlapping standards, benchmarks, and internal checklists so projects do not maintain duplicate paperwork or conflicting interpretations.

## Exceptions

- Single-surface evidence should be produced by the specialist skill, with this skill only aggregating if needed.
- Manual evidence can be temporary when automation is not yet available, but it needs expiry and a replacement path.
- Legal/auditor-facing interpretation is out of scope; this skill produces engineering evidence, not legal claims.
- Threat-detection mapping is included only when detection coverage is explicitly in scope.

## Response Quality Bar

- Lead with the control-to-evidence map, scorecard, exception register, or evidence-pack outline requested.
- Cover engineering behavior, repeatable evidence sources, cadence, pass/fail states, exceptions, and workflow fit before optional governance breadth.
- Make recommendations actionable with artifact sources, collection cadence, failure response, automation backlog, and exception expiry where relevant.
- State required evidence such as CI results, deploy records, configuration snapshots, review logs, incident records, control outputs, and source artifact links; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering evidence. Do not make legal, procurement, staffing, or audit-opinion claims.
- Be concise: avoid generic compliance language and prefer compact control-evidence matrices.

## Required Outputs

- Control-to-behavior-to-evidence map.
- Evidence inventory with source, cadence, and retention.
- Scorecard with pass/fail/exception states.
- Exception register with expiry, compensating controls, re-review trigger, residual risk, and acceptance authority.
- Evidence pack outline linked to source artifacts.
- Standards update backlog with gap source, control, severity, expected fix path, and target date.

## Evidence Gates

- `scope_check`: request explicitly spans two or more engineering surfaces, no single specialist covers the full evidence set, and non-engineering program management is excluded.
- `evidence_source`: every control maps to a repeatable artifact source.
- `control_cadence`: every control has review cadence, and failure response.
- `exception_check`: exceptions have expiry, compensating control, and review trigger.
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
| Open-ended exceptions | Add expiry, compensating control, and review trigger. |
| Using this for everything | Prefer domain skills for single-surface evidence. |
