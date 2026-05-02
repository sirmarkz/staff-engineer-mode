---
name: observability-and-alerting
description: "Use when the user asks for dashboards, logs, metrics, traces, telemetry instrumentation, alerting, runbooks, correlation IDs, or production debugging. Do not use for SLO policy unless alerts are the main deliverable."
---

# Observability And Alerting

## Overview

Observability is the ability to explain new failures from production evidence, not the act of collecting every metric.

**Core principle:** instrument user-visible symptoms first, then add enough causal context to debug without guessing.

## Iron Law

```
NO PAGE WITHOUT USER IMPACT, URGENCY, ACTIONABILITY, AND A RUNBOOK
```

If an alert is not urgent, actionable, user-visible, and novel, it should not page by default.

## When To Use

- The user asks for metrics, logs, traces, dashboards, alerting, runbooks, correlation IDs, telemetry fields, or production debugging.
- A service cannot explain incidents from existing signals.
- The user asks how to instrument a new service, dependency, queue, pipeline, or rollout.
- Alert rules are the main deliverable, even if SLO policy is already defined.

## When Not To Use

- The user needs reliability targets, SLO math, or budget policy; use SLO engineering.
- The user needs to reduce existing page volume or toil; use on-call health unless new telemetry is central.
- The user is in a live incident; use incident response first.
- The work is only local development logging without production operations impact.

## Inputs To Collect

- Critical user journeys, SLOs, owners, service tier, and incident history.
- Request paths, dependency map, queues, data stores, batch jobs, and external integrations.
- Existing metrics, logs, traces, dashboards, alerts, runbooks, and known blind spots.
- Deployment markers, version identifiers, feature/config flags, tenant/customer context, and correlation identifiers.
- Privacy constraints, sensitive fields, retention requirements, and sampling limits.
- Responder workflow: where pages go, who owns them, and how runbooks are used.

## Workflow

1. **Start with symptoms.** Define what users notice: failed requests, slow actions, stale data, dropped work, lost messages, or incorrect results.
2. **Add golden signals.** Capture latency, traffic, errors, and saturation for services; utilization, saturation, and errors for resources.
3. **Instrument dependencies.** Include call count, latency, errors, timeouts, retries, queue depth, queue age, and drain rate.
4. **Connect events.** Propagate correlation/context identifiers across boundaries and attach deployment/change markers.
5. **Structure logs and events.** Use stable fields for operation, owner, tenant/customer context where safe, dependency, result, error class, and latency.
6. **Define the health model.** State healthy, degraded, unavailable, and recovering conditions at component, dependency, journey, and workload levels; distinguish transient degradation from sustained unavailability.
7. **Design dashboards for questions.** Build views around impact, scope, recent changes, dependencies, saturation, and recovery progress.
8. **Page on symptoms.** Use SLO burn or direct user-impact alerts. Keep diagnostic and causal alerts as tickets unless urgent and actionable.
9. **Attach runbooks.** Every page needs triage steps, impact check, mitigation options, escalation path, and rollback/fallback links.

## Synthesized Default

Use SLO/user-journey symptoms, layered health models, golden signals, structured events, distributed context, deployment markers, and dependency signals as the default telemetry set. Page only when action is required now; use dashboards and tickets for investigation and slow-burn work.

## Exceptions

- Early-stage services may begin with a minimal symptom dashboard and expand after real failure modes are known.
- Low-volume systems may need synthetic checks or heartbeat/freshness signals to detect user impact.
- Security and privacy constraints may require redaction, hashing, sampling, or separate audit trails.
- Some critical causal signals can page if they are proven leading indicators with a runbook.

## Response Quality Bar

- Lead with the dashboard spec, alert classification, telemetry gap, or runbook requirement requested.
- Cover user journeys, health states, golden signals, dependency context, deployment markers, privacy-safe events, paging policy, and runbooks before optional observability breadth.
- Make recommendations actionable with owners, metric/log/trace names, thresholds, routes, runbook links, failure response, and rollout gates where relevant.
- State required evidence such as SLOs, metric sources, log fields, trace context, alert history, runbook content, deploy markers, and sensitive-data handling; do not claim unseen evidence.
- Stay inside observability and alerting. Route SLO definition, on-call policy, or incident response only when those are the central unresolved risk.
- Be concise: avoid generic telemetry lists and prefer compact journey-to-signal and alert-policy tables.

## Required Outputs

- Telemetry requirements mapped to user journeys and dependencies.
- Dashboard specification for impact, scope, dependencies, saturation, and recent changes.
- Alert policy with page/ticket/diagnostic classification.
- Structured log/event field standard and sensitive-data handling.
- Trace or context propagation requirements.
- Runbook requirements for every paging alert.
- Gaps and follow-up routes to SLO, on-call, incident, or platform work.

## Evidence Gates

- `symptom_first`: paging alerts map to SLO burn or direct user-visible impact.
- `health_model`: component and dependency signals aggregate into critical-journey and workload health states.
- `causal_context`: telemetry includes dependency, correlation, version/change, and saturation context.
- `runbook_link`: every page has a runbook with impact check, mitigation, escalation, and verification.
- `privacy_check`: sensitive data handling is defined for logs, traces, labels, and events.
- `debug_path`: dashboards answer impact, scope, cause candidates, recent changes, and recovery state.

## Red Flags - Stop And Rework

- Dashboards start from whatever the platform emits instead of user journeys.
- Every dependency error pages even when retries hide user impact.
- Logs contain sensitive data or unbounded high-cardinality fields without controls.
- Alerts have no owner or runbook.
- Metrics show averages only and hide tail latency or saturation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Collecting everything | Collect signals that answer operational questions. |
| Paging on causes | Page on symptoms; use causes for debugging. |
| Ignoring changes | Add deployment, config, and feature markers. |
| Logging prose | Use stable structured fields. |
