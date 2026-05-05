---
name: platform-golden-paths
description: "Use to design or evolve a developer platform — golden paths, service templates, scorecards, paved roads — when many teams need the same safe defaults baked in. Assumes a multi-team or platform-team context."
---

# Platform Engineering And Golden Paths

## Iron Law

```
NO GOLDEN PATH WITHOUT OWNERSHIP, SECURITY, OBSERVABILITY, DEPLOYMENT, AND OPERATIONS DEFAULTS
```

If a template creates a service but not an operable service, it is not a golden path.

> This skill assumes a multi-team or platform-team context. Golden paths exist to remove repeated setup across many teams; for a solo developer or single team the same patterns apply but live as repo templates, not as a platform product. Route single-service architecture to `architecture-decisions`.

## Overview

A good platform makes the safe path the easy path.

**Core principle:** encode standards as reusable workflows, templates, scorecards, and self-service capabilities that teams actually use.

## When To Use

- The user asks about internal developer platforms, golden paths, paved roads, service catalogs, templates, scorecards, or standardized service creation.
- Multiple teams need repeatable service setup, deployment, ownership, telemetry, security, or compliance evidence.
- The same operational or security gaps recur across services.
- A platform should reduce toil or make standards easier to satisfy.

## When Not To Use

- The work is one-off architecture for one service; defer to `architecture-decisions`.
- The request is only infrastructure policy mechanics; defer to `infrastructure-and-policy-as-code`.
- The request is compliance program management rather than engineering controls; defer to `engineering-control-evidence` only when in scope.
- The work is vendor selection or procurement; out of scope.

## Inputs To Collect

- Target users, service types, common workflows, pain points, and current failure modes.
- Required defaults: ownership, SLOs, telemetry, deployment, rollback, runbooks, security, secrets, cost tags, and recovery.
- Existing templates, catalogs, scorecards, CI/CD, infrastructure modules, and exception process.
- Migration needs for existing services and adoption blockers.
- Platform team ownership, support model, upgrade cadence, and feedback channels.

## Workflow

1. **Start from repeated pain.** Choose platform capabilities that remove recurring setup, safety, security, or operations work.
2. **Define the golden path.** Specify the service lifecycle from create, build, test, deploy, observe, operate, secure, recover, and retire.
3. **Bake in defaults.** Include ownership, SLO hooks, telemetry, safe deploys, secret handling, access boundaries, runbooks, and evidence.
4. **Make start-right templates.** Bootstrap repositories, delivery, infrastructure, observability, security, and policy defaults together so teams do not assemble safety by hand.
5. **Expose self-service with guardrails.** Make the path usable without bespoke platform-team intervention for normal cases while policy, security, cost, and operations controls stay automatic.
6. **Design scorecards.** Measure capability maturity across investment, adoption, governance, provisioning and management, interfaces, and feedback; use evidence for meaningful capabilities, not vanity checkboxes.
7. **Support exceptions.** Require owner, expiry, compensating control, and migration plan.
8. **Plan adoption.** Prioritize new services, high-risk services, and repeated incident classes; avoid big-bang migrations.
9. **Close feedback loops.** Use incidents, developer friction, and scorecard gaps to improve the platform.

## Synthesized Default

Build golden paths around capabilities rather than tools: service creation, build, test, release, telemetry, security, ownership, recovery, governance, and evidence. Provide self-service with guardrails, start-right templates, and escape hatches, but make exceptions visible and temporary.

## Exceptions

- Specialized services can deviate when golden-path assumptions do not fit, but the exception must preserve equivalent evidence and operations standards.
- Early platform phases may cover a narrow service type first; state non-goals clearly.
- Strict scorecards should start advisory until platform capabilities make compliance achievable.
- Existing services may need incremental migration instead of template replacement.

## Response Quality Bar

- Lead with the platform capability map, golden-path design, scorecard, migration plan, or exception workflow requested.
- Cover lifecycle defaults, service ownership, build/test/release, telemetry, security, recovery, evidence hooks, self-service, exceptions, adoption, and feedback before optional platform breadth.
- Make recommendations actionable with owners, templates, required defaults, scorecard checks, migration batches, support model, and exception expiry where relevant.
- State required evidence such as current service inventory, onboarding steps, platform friction, incident gaps, template outputs, scorecard results, adoption metrics, and support queues; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside platform engineering and golden paths. Route infrastructure policy, release engineering, or observability only when those specialist gaps block the platform decision.
- Be concise: avoid generic platform-product language and prefer compact capability maps, lifecycle defaults, and adoption tables.

## Required Outputs

- Platform capability map.
- Golden-path lifecycle and template requirements.
- Required service defaults and evidence hooks.
- Service catalog and ownership model.
- Capability scorecard with meaningful checks, adoption feedback, and exception workflow.
- Migration/adoption plan.
- Feedback and support model.

## Evidence Gates

- `template_defaults`: golden path includes ownership, SLO/telemetry, deploy/rollback, runbook, security, and secrets defaults.
- `self_service`: normal workflow can be completed without bespoke platform-team work.
- `exception_model`: exceptions have owner, expiry, compensating control, and migration path.
- `adoption_plan`: target services, migration order, and support model are stated.
- `feedback_loop`: incidents, friction, and scorecard gaps feed platform backlog.

## Red Flags - Stop And Rework

- Template creates code but no owner, runbook, alerts, or rollout path.
- Platform mandates standards teams cannot satisfy with available tools.
- Scorecards reward fields existing instead of capabilities working.
- Exceptions are permanent.
- Golden path is a vendor product wrapper rather than an engineering workflow.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Building a portal first | Start with repeatable workflows and defaults. |
| No escape hatch | Allow exceptions with owner, expiry, and equivalent controls. |
| Platform as ticket queue | Prefer self-service for normal paths. |
| Measuring adoption only | Measure operational and security outcomes too. |
