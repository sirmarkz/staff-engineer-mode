---
name: documentation-lifecycle
description: "Use when runbooks, design docs, ADRs, or onboarding docs need ownership, freshness rules, or review triggers"
---

# Engineering Documentation Lifecycle

## Iron Law

```
NO CRITICAL ENGINEERING DOC WITHOUT AUDIENCE, SOURCE OF TRUTH, FRESHNESS RULE, AND REVIEW TRIGGER
```

If a doc can mislead an operator, or stale documentation is a production risk.

## Overview

Engineering documentation is useful only when it is findable, maintained, current, authoritative, and tied to the system it describes.

**Core principle:** make docs part of the delivery system, with audience, freshness signal, source of truth, and review trigger.

## When To Use

- The user asks to audit, design, govern, restructure, or lifecycle-manage engineering docs, runbooks, design docs, decision records, onboarding guides, operational references, or documentation standards.
- Documentation is stale, duplicated, missing hard to find, or disconnected from code and operations.
- A launch, migration, incident, or deprecation needs docs that remain accurate after the change lands.
- You need a doc lifecycle, not just copy editing.

## When Not To Use

- The main artifact is an architecture decision; use `architecture-decisions`.
- The main artifact is an incident timeline or postmortem; use `incident-response-and-postmortems`.
- The request is marketing, sales, or public positioning copy.
- The request is routine editorial or mechanical documentation maintenance with no source-of-truth dispute, operational guidance gap, stale-doc risk, or lifecycle decision.

## Inputs To Collect

- Doc type, audience, source of truth, repo or system link, and user decision point.
- Current doc set, duplicates, stale pages, search paths, and missing operational references.
- Change triggers: code responsibility, service behavior, alerts, runbooks, interfaces, migrations, and deprecations.
- Review cadence, freshness signal, archival rule, and exception path.
- Evidence that users can find and apply the doc during real work.

## Workflow

1. **Classify docs by job.** Place every doc asset into exactly one quadrant: tutorial (learning-oriented), how-to (task-oriented), reference (information-oriented), or explanation (understanding-oriented). Tag runbooks and decision records separately as operational and architectural artifacts. Split or rewrite any doc that mixes quadrants until each piece sits in one.
2. **Name the audience.** State who uses the doc and what decision or task it supports.
3. **Assign responsibility.** Give every critical doc a user/agent responsibility path and an update trigger tied to the system lifecycle. Anonymous docs become stale silently.
4. **Pick the source of truth.** Remove or mark duplicates so readers know where authority lives.
5. **Add freshness signals.** Include last-reviewed state, lifecycle stage, review trigger, and archive rule.
6. **Connect docs to delivery.** Link docs to code, alerts, dashboards, runbooks, release gates, or decision records where they are used.
7. **Test usability.** Verify a fresh agent or the user from a clean clone can find and follow the doc under realistic conditions.
8. **Retire stale docs.** Archive misleading content rather than keeping it searchable with no current source of truth.

## Synthesized Default

Use a lightweight documentation lifecycle: classify by user job, assign define source of truth, tie updates to system changes, add freshness signals, and archive stale material. Critical runbooks and launch docs should be checked as part of delivery, not after outages prove they were wrong.

## Exceptions

- Short-lived design notes may expire after the decision is recorded elsewhere.
- Exploratory notes can remain rough if clearly marked as non-authoritative.
- Emergency docs may start minimal but need cleanup immediately after the event.

## Response Quality Bar

- Lead with the doc lifecycle, inventory, rewrite plan, or freshness gate requested.
- Cover audience, source of truth, doc type, update trigger, discoverability, and archival rule before optional style advice.
- Make recommendations actionable with review cadence, stale-doc handling, and delivery gates where relevant.
- State required evidence such as current docs, usage paths, responsibility paths, stale pages, runbook tests, and change triggers; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering documentation. Route architecture decisions, incident writeups, or marketing copy only when they are central.
- Be concise: prefer doc inventories and lifecycle rules over broad writing theory.

## Required Outputs

- Documentation inventory **table with explicit columns**: `Doc | Diátaxis quadrant (tutorial / how-to / reference / explanation) | Responsibility path | Source of truth | Last reviewed | Review cadence | Staleness signal`. Runbooks and decision records tagged separately as operational/architectural.
- Source-of-truth map that **states the no-duplication rule explicitly** (e.g., "one canonical location per system; duplicates are marked non-authoritative or deleted").
- Freshness policy naming **both review cadence AND staleness signal** (e.g., "review every 90 days; mark `stale` if last-verified > cadence or if linked alert/code changed without doc update").
- Docs-as-code workflow: **PR-based review for doc changes AND automated checks** (link-checker, markdown lint, CI build) running on every doc PR.
- Required docs for launch, operations, migration, or maintenance.
- Update triggers tied to code, operations, and release events.
- Stale-doc cleanup plan.
- Usability and findability checks.

## Evidence Gates

- `audience_job`: each critical doc names its reader and supported task.
- `doc_source`: responsibility path and source of truth are explicit.
- `quadrant_classification`: every doc in the inventory **table carries a visible quadrant label** (tutorial / how-to / reference / explanation); runbooks and decision records tagged separately as operational/architectural. Mixed-quadrant docs are split.
- `no_duplication_rule`: source-of-truth section states an explicit rule against duplication, not just "remove duplicates."
- `staleness_signal`: freshness policy names both a cadence and the signal that flips a doc to stale.
- `docs_as_code`: doc changes flow through PR review AND automated checks (lint, link-check, or CI).
- `freshness_rule`: review trigger, lifecycle state, and archive rule exist.
- `delivery_link`: docs required for operation or launch are tied to delivery gates.
- `usability_check`: someone can find and use the doc without tribal knowledge.

## Red Flags - Stop And Rework

- Two docs contradict each other and neither is marked authoritative.
- A runbook has no source of truth or last-review signal.
- A launch depends on undocumented manual knowledge.
- Stale docs remain searchable after the system changes.
- Documentation standards focus on formatting while operational gaps remain.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Writing before audience | Start with reader job and decision. |
| Keeping every page forever | Archive misleading docs aggressively. |
| Treating docs as separate from delivery | Add update triggers to code and release workflows. |
| Style as governance | Govern responsibility, truth, freshness, and usability. |
