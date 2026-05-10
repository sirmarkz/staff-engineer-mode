---
name: observability-and-alerting
description: "Use when telemetry, dashboards, alert rules, or runbooks need design outside SLO or release-gate policy"
---

# Observability And Alerting

## Iron Law

```
TELEMETRY STARTS FROM USER SYMPTOMS; A PAGE NEEDS USER IMPACT, URGENCY, ACTIONABILITY, AND A RUNBOOK
```

Telemetry that does not map to a user-visible symptom is decoration. An alert that lacks impact, urgency, actionability, or a runbook should not page by default. The two halves are co-designed: signals exist so that someone can act on them, and pages fire only on signals that prove user-felt impact.

## Overview

Produces telemetry requirements tied to user journeys, a dashboard specification that answers impact and recent change, and an alert policy where every page has user impact, urgency, actionability, and a runbook. Refuses host-health pages, anonymous alerts, and dashboards built from whatever the platform happened to emit.

**Core principle:** instrument user-visible symptoms first, then add enough causal context to debug without guessing.

## When To Use

- The user asks for metrics, logs, traces, dashboards, alerting, runbooks, correlation IDs, telemetry fields, or production debugging.
- A service cannot explain incidents from existing signals.
- The user asks how to instrument a new service, dependency, queue, pipeline, or rollout.
- Alert rules are the main deliverable and the work is not asking to connect them to SLO or error-budget policy.

## When Not To Use

- The user needs reliability targets, SLO math, SLO-based page/ticket policy, or budget policy; use `slo-and-error-budgets` instead.
- The user needs to reduce existing page volume or toil; use `oncall-health` instead unless new telemetry is central.
- The user is in a live incident; route to `incident-response-and-postmortems` first.
- The work is only local development logging without production operations impact.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Critical user journeys, SLOs, service tier, and incident history.
- Request paths, dependency map, queues, data stores, batch jobs, and external integrations.
- Existing metrics, logs, traces, dashboards, alerts, runbooks, and known blind spots.
- Fault-domain labels needed for impact analysis, such as location, deployment unit, partition, shard, tenant, and deployment stage.
- Deployment markers, version identifiers, feature/config flags, tenant/customer context, and correlation identifiers.
- Privacy constraints, sensitive fields, retention requirements, and sampling limits.
- Responder workflow: where pages go, what local response path handles them, and how runbooks are used.

## Workflow

1. **Start with symptoms.** Define what users notice: failed requests, slow actions, stale data, dropped work, lost messages, or incorrect results.
2. **Add golden signals.** Capture latency, traffic, errors, and saturation for services; utilization, saturation, and errors for resources.
3. **Instrument dependencies.** Include call count, latency, errors, timeouts, retries, queue depth, queue age, and drain rate.
4. **Connect events.** Propagate trace context across every service boundary so the trace identifier is global to a request and span identifiers are local to each unit of work; attach deployment/change markers.
5. **Structure logs and events.** Require a baseline field set on every entry — UTC timestamp, severity, service identifier, trace identifier, request identifier, and message — plus stable fields for operation, tenant/customer context where safe, dependency, result, error class, and latency.
6. **Define the health model.** State healthy, degraded, unavailable, and recovering conditions at component, dependency, journey, and workload levels; distinguish transient degradation from sustained unavailability.
7. **Design dashboards for questions.** Build views around impact, scope, fault domain, recent changes, dependencies, saturation, and recovery progress.
8. **Page on symptoms.** Use SLO burn or direct user-impact alerts. Keep diagnostic and causal alerts as tickets unless urgent and actionable.
9. **Identify affected customers safely.** For customer-impacting services, define privacy-safe signals that support impact scoping and notification.
10. **Attach runbooks.** Every page needs triage steps, impact check, mitigation options, fallback path, and rollback/fallback links.

## Synthesized Default

Use SLO/user-journey symptoms, layered health models, golden signals, fault-domain labels, structured events, distributed context, deployment markers, and dependency signals as the default telemetry set. Page only when action is required now; use dashboards and tickets for investigation and slow-burn work.



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

- Early-stage services may begin with a minimal symptom dashboard and expand after real failure modes are known.
- Low-volume systems may need synthetic checks or heartbeat/freshness signals to detect user impact.
- Security and privacy constraints may require redaction, hashing, sampling, or separate audit trails.
- Some critical causal signals can page if they are proven leading indicators with a runbook.

## Response Quality Bar

- Lead with the dashboard spec, alert classification, telemetry gap, or runbook requirement requested.
- Cover user journeys, health states, golden signals, dependency context, deployment markers, privacy-safe events, paging policy, and runbooks before optional observability breadth.
- Make recommendations actionable with metric/log/trace names, thresholds, routes, runbook links, failure response, and rollout gates where relevant.
- State required evidence such as SLOs, metric sources, log fields, trace context, alert history, runbook content, deploy markers, and sensitive-data handling; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside observability and alerting. Route SLO definition, on-call policy, or incident response only when those are the central unresolved risk.
- Be concise: avoid generic telemetry lists and prefer compact journey-to-signal and alert-policy tables.

## Required Outputs

- Telemetry requirements mapped to user journeys and dependencies.
- Dashboard specification for impact, scope, dependencies, saturation, and recent changes.
- Fault-domain and affected-customer scoping signals where relevant.
- Alert policy with page/ticket/diagnostic classification.
- Structured log/event field standard and sensitive-data handling.
- Trace or context propagation requirements.
- Runbook requirements for every paging alert.
- Gaps and follow-up routes to SLO, on-call, incident, or platform work.

## Evidence Gates

- `symptom_first`: paging alerts map to SLO burn or direct user-visible impact.
- `health_model`: component and dependency signals aggregate into critical-journey and workload health states.
- `causal_context`: telemetry includes dependency, correlation, version/change, and saturation context.
- `fault_domain_context`: telemetry can separate impact by location, deployment unit, partition, shard, tenant, or deployment stage where those domains exist.
- `runbook_link`: every page has a runbook with impact check, mitigation, fallback, and verification.
- `privacy_check`: sensitive data handling is defined for logs, traces, labels, and events.
- `debug_path`: dashboards answer impact, scope, cause candidates, recent changes, and recovery state.

## Red Flags - Stop And Rework

- Dashboards start from whatever the platform emits instead of user journeys.
- Every dependency error pages even when retries hide user impact.
- Logs contain sensitive data or unbounded high-cardinality fields without controls.
- Alerts have no runbook or response path.
- Metrics show averages only and hide tail latency or saturation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Collecting everything | Collect signals that answer operational questions. |
| Paging on causes | Page on symptoms; use causes for debugging. |
| Ignoring changes | Add deployment, config, and feature markers. |
| Logging prose | Use stable structured fields. |
