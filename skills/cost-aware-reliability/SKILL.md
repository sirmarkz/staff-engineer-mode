---
name: cost-aware-reliability
description: "Use when cost spikes, unit economics, or spend cuts must preserve reliability and SLO headroom"
---

# FinOps And Cost Aware Reliability

## Iron Law

```
NO COST CUT WITHOUT SLO, HEADROOM, BLAST-RADIUS, AND REGRESSION CHECK
```

If a saving silently consumes reliability margin, it is a risk decision, not an optimization.

## Overview

Cost is an operational signal, but reliability headroom is not waste by default.

**Core principle:** optimize unit economics while preserving explicit reliability, capacity, recovery, and safety targets.

## When To Use

- The user asks about cost/reliability tradeoffs, unit economics, capacity headroom, tagging/allocation, cost regressions, reserved/committed/interruptible capacity mix, or budget-aware reliability.
- A service needs to reduce cost while maintaining an SLO or launch target.
- A cost spike may indicate traffic, inefficiency, abuse, deployment regression, or capacity misconfiguration.
- The user asks how much reliability headroom is justified.

## When Not To Use

- The user asks pure billing support, procurement, contracts, or vendor negotiation; out of scope.
- The main topic is performance/capacity with no cost tradeoff; use `performance-and-capacity` instead.
- The issue is public abuse causing cost; use `edge-traffic-and-ddos-defense` instead too.
- The request is financial reporting not tied to engineering decisions.

## Inputs To Collect

- Service tier, SLOs, traffic, capacity model, failover headroom, and degradation behavior.
- Unit metrics: request, tenant, job, dataset, device, model inference, or business transaction.
- Cost allocation: environment, tenant/customer, feature, location, and workload class.
- Scaling policies, reserved/committed/interruptible mix, idle resources, and peak patterns.
- Data transfer, cross-location replication, telemetry/log volume, managed service overhead, and external traffic costs.
- Recent deploys, traffic changes, incidents, abuse signals, and cost regressions.
- Reliability risk tolerance and confirmation path for reducing headroom.

## Workflow

1. **State the reliability constraint.** Identify SLO, capacity headroom, failover target, and recovery requirement before cutting cost.
2. **Define unit cost.** Choose a meaningful engineering unit and map cost to service, feature, tenant, or workload.
3. **Find cost drivers.** Separate traffic growth, inefficient code, overprovisioning, idle capacity, data transfer, cross-location replication, telemetry/log volume, storage growth, retries, and abuse.
4. **Protect headroom.** Distinguish waste from required peak, failover, and surge capacity.
5. **Choose optimizations.** Use right-sizing, scheduling, storage lifecycle, caching, batching, data-transfer reduction, telemetry sampling/retention controls, capacity mix, or code efficiency where risk is explicit.
6. **Model commitment risk.** For committed capacity or discounts, state forecast confidence, lock-in window, unused commitment risk, exit path, and what reliability headroom is protected.
7. **Model tradeoffs.** State expected savings, reliability impact, security/operations side effects, blast radius, rollback, and monitoring.
8. **Add guardrails.** Alert on cost regressions, unit-cost anomalies, and reliability signals after changes.
9. **Review continuously.** Treat cost anomalies like operational regressions with post-change verification.

## Synthesized Default

Optimize unit cost with allocation, anomaly detection, right-sizing, and capacity-mix decisions, while preserving SLOs, required headroom, and recovery posture. Reliability-risk tradeoffs must be explicit and user-accepted; cheapest is not automatically cost-optimized.

## Exceptions

- Non-critical batch or preemptible workloads may use cheaper interruptible capacity if retries, deadlines, and data correctness are safe.
- Emergency cost controls can temporarily degrade non-critical features if user impact and rollback are explicit.
- Regulated, safety-critical, or tier-1 systems may keep high headroom even when utilization looks inefficient.
- Public abuse cost spikes should use `edge-traffic-and-ddos-defense` instead.
- Small estates may not justify heavy allocation pipelines; use coarse unit tracking until savings exceed instrumentation cost.

## Response Quality Bar

- Lead with the unit-cost model, cost driver, reliability tradeoff, optimization plan, or anomaly diagnosis requested.
- Cover allocation, unit metrics, driver separation, SLO/headroom preservation, failure-condition capacity, rollback, anomaly monitoring, and review cadence before optional FinOps breadth.
- Make recommendations actionable with metrics, savings ranges, risk acceptance, stop criteria, rollback steps, and post-change checks where relevant.
- State required evidence such as spend by usage units, traffic, capacity headroom, SLOs, peak/failure demand, deploy markers, anomaly timeline, and retry/abuse signals; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside cost-aware reliability. Route capacity, edge defense, platform, or data work only when those are the central unresolved risk.
- Be concise: avoid generic cost advice and prefer compact unit-cost, driver, and tradeoff tables.

## Required Outputs

- Unit-cost model and allocation plan.
- Cost driver analysis.
- Data-transfer, telemetry, and cross-location cost assessment where applicable.
- Reliability/headroom tradeoff record.
- Optimization plan with savings estimate, risk, and rollback.
- Commitment-risk record for reserved, prepaid, interruptible, or long-window capacity decisions.
- Cost anomaly and unit-regression dashboard requirements.
- Review cadence for cost signals.
- Follow-up routes to capacity, edge defense, platform, or data skills as needed.

## Evidence Gates

- `unit_check`: cost metric maps to an engineering unit and response path.
- `slo_headroom`: SLO, peak, and failure-condition headroom are preserved or risk is accepted.
- `driver_check`: cost drivers are separated before recommending cuts.
- `rollback_check`: optimization has rollback or mitigation plan.
- `regression_check`: post-change cost and reliability signals are monitored.

## Red Flags - Stop And Rework

- Cost reduction removes failover capacity without changing SLO or accepting risk.
- Only total monthly spend is tracked; no unit metric or response path exists.
- Idle capacity is labeled waste without peak/failure analysis.
- Interruptible capacity is used for work that cannot safely retry.
- Cost anomaly investigation ignores deploys, retries, abuse, and data growth.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Cutting before modeling risk | State SLO, headroom, and failure scenarios first. |
| Optimizing total spend only | Use unit economics tied to engineering responsibility. |
| Treating cost as finance-only | Add operational alerts and regression reviews. |
| Hiding tradeoffs | Record reliability risk and confirmation. |
