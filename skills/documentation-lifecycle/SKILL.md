---
name: documentation-lifecycle
description: "Use when engineering docs need ownership, source of truth, freshness, or lifecycle gates; not for routine editorial or mechanical edits."
---

# Engineering Documentation Lifecycle

## Overview

Engineering documentation is useful only when it is findable, owned, current, authoritative, and tied to the system it describes.

**Core principle:** make docs part of the delivery system, with audience, owner, freshness signal, source of truth, and review trigger.

## Iron Law

```
NO CRITICAL ENGINEERING DOC WITHOUT AUDIENCE, OWNER, SOURCE OF TRUTH, FRESHNESS RULE, AND REVIEW TRIGGER
```

If a doc can mislead an operator, reviewer, or maintainer, stale documentation is a production risk.

## When To Use

- The user asks to audit, design, govern, restructure, or lifecycle-manage engineering docs, runbooks, design docs, decision records, onboarding guides, operational references, or documentation standards.
- Documentation is stale, duplicated, missing owners, hard to find, or disconnected from code and operations.
- A launch, migration, incident, or deprecation needs docs that remain accurate after the change lands.
- A team needs a doc lifecycle, not just copy editing.

## When Not To Use

- The main artifact is an architecture decision; use architecture review and decision records.
- The main artifact is an incident timeline or postmortem; use incident response.
- The request is marketing, sales, or public positioning copy.
- The request is routine editorial or mechanical documentation maintenance with no source-of-truth dispute, operational guidance gap, stale-doc risk, or lifecycle decision.

## Inputs To Collect

- Doc type, audience, owner, source of truth, repo or system link, and decision authority.
- Current doc set, duplicates, stale pages, search paths, and missing operational references.
- Change triggers: code ownership, service behavior, alerts, runbooks, interfaces, migrations, and deprecations.
- Review cadence, freshness signal, archival rule, and exception path.
- Evidence that users can find and apply the doc during real work.

## Workflow

1. **Classify docs by job.** Separate tutorials, how-to guides, references, explanations, runbooks, and decisions.
2. **Name the audience.** State who uses the doc and what decision or task it supports.
3. **Assign ownership.** Give every critical doc an owner and update trigger tied to the system lifecycle.
4. **Pick the source of truth.** Remove or mark duplicates so readers know where authority lives.
5. **Add freshness signals.** Include last-reviewed state, lifecycle stage, review trigger, and archive rule.
6. **Connect docs to delivery.** Link docs to code, alerts, dashboards, runbooks, release gates, or decision records where they are used.
7. **Test usability.** Verify a new maintainer or on-call engineer can find and follow the doc under realistic conditions.
8. **Retire stale docs.** Archive misleading content rather than keeping it searchable with no owner.

## Synthesized Default

Use a lightweight documentation lifecycle: classify by user job, assign owner, define source of truth, tie updates to system changes, add freshness signals, and archive stale material. Critical runbooks and launch docs should be checked as part of delivery, not after outages prove they were wrong.

## Exceptions

- Short-lived design notes may expire after the decision is recorded elsewhere.
- Exploratory notes can remain rough if clearly marked as non-authoritative.
- Emergency docs may start minimal but need owner and cleanup immediately after the event.

## Response Quality Bar

- Lead with the doc lifecycle, inventory, rewrite plan, or freshness gate requested.
- Cover audience, owner, source of truth, doc type, update trigger, discoverability, and archival rule before optional style advice.
- Make recommendations actionable with owners, review cadence, stale-doc handling, and delivery gates where relevant.
- State required evidence such as current docs, usage paths, owner map, stale pages, runbook tests, and change triggers; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering documentation. Route architecture decisions, incident writeups, or marketing copy only when they are central.
- Be concise: prefer doc inventories and lifecycle rules over broad writing theory.

## Required Outputs

- Documentation inventory by audience and job.
- Owner, source-of-truth, freshness, and archive map.
- Required docs for launch, operations, migration, or maintenance.
- Update triggers tied to code, operations, and release events.
- Stale-doc cleanup plan.
- Usability and findability checks.

## Evidence Gates

- `audience_job`: each critical doc names its reader and supported task.
- `owner_source`: owner and source of truth are explicit.
- `freshness_rule`: review trigger, lifecycle state, and archive rule exist.
- `delivery_link`: docs required for operation or launch are tied to delivery gates.
- `usability_check`: someone can find and use the doc without tribal knowledge.

## Red Flags - Stop And Rework

- Two docs contradict each other and neither is marked authoritative.
- A runbook has no owner or last-review signal.
- A launch depends on undocumented manual knowledge.
- Stale docs remain searchable after the system changes.
- Documentation standards focus on formatting while operational gaps remain.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Writing before audience | Start with reader job and decision. |
| Keeping every page forever | Archive misleading docs aggressively. |
| Treating docs as separate from delivery | Add update triggers to code and release workflows. |
| Style as governance | Govern ownership, truth, freshness, and usability. |
