---
name: ml-reliability-and-evaluation
description: "Use to gate a production ML model promotion on data validation, eval thresholds, training-serving skew, drift monitoring, and rollback path — before a new artifact replaces the live one."
---

# ML Systems Reliability And Evaluation

## Iron Law

```
NO MODEL PROMOTION WITHOUT DATA VALIDATION, EVAL GATES, SERVING CHECKS, AND ROLLBACK
```

Offline accuracy alone is not production readiness.

## Overview

Production ML reliability is software reliability plus data reliability plus model behavior reliability.

**Core principle:** promote models only when data, features, evals, serving behavior, rollout, monitoring, and rollback are all controlled.

## When To Use

- The user asks about production ML readiness, model serving, training pipelines, eval gates, feature validation, training-serving skew, drift, model rollout, or model rollback.
- A model artifact, feature pipeline, training job, or inference path is changing.
- The user needs to monitor model quality, prediction distribution, data drift, or serving latency.
- A launch or PRR includes ML behavior.

## When Not To Use

- The work is generic warehouse/ETL reliability with no model production concern; defer to `data-pipeline-reliability`.
- The request is broad AI policy or model strategy; out of scope unless framed as production engineering.
- The system is an LLM or agent app with prompt/tool security risk; defer to `llm-application-security`.
- The work is offline experimentation only and will not affect production.

## Inputs To Collect

- Model owner, use case, user impact, failure consequence, and production tier.
- Training data, feature definitions, schemas, labels, transform code, and serving data sources.
- Offline eval metrics, acceptance thresholds, slices/cohorts, fairness/safety checks where relevant, and regression history.
- Training-serving consistency checks, feature freshness, null/default behavior, and schema drift.
- Model artifact version, data version, config, dependencies, and rollout unit.
- Serving SLOs, latency, saturation, fallback behavior, monitoring, and rollback path.
- Drift, quality, feedback, incident, and human-review signals.

## Workflow

1. **Establish a non-ML baseline.** Confirm the system needs ML and has a deterministic fallback or baseline where appropriate.
2. **Validate data and features.** Check schema, ranges, missingness, distributions, freshness, and transform consistency.
3. **Check training-serving skew.** Compare feature generation, preprocessing, defaults, and dependency versions across training and serving.
4. **Define eval gates.** Use offline metrics, slice metrics, regression tests, adversarial/security checks, safety/business constraints, and minimum deltas for promotion.
5. **Version everything.** Link model artifact, code, features, data snapshot, config, eval result, and serving environment.
6. **Roll out progressively.** Use shadow, canary, cohort, percentage, or holdback where feasible; monitor serving and model behavior.
7. **Monitor production with thresholds.** Track serving SLOs, prediction distribution, feature drift, data freshness, quality proxies, feedback loops, and capacity or quota saturation; name alert thresholds or rollback triggers for at least two of those signals.
8. **Prepare rollback.** Keep prior artifact/config available and define when to rollback, disable, or route to baseline.

## Synthesized Default

Gate ML releases on data validation, eval results, threat-informed failure-mode checks, training-serving consistency, versioned artifacts, progressive rollout, serving SLOs, thresholded drift and serving monitoring, and rollback. Treat model-only evaluation as insufficient for production readiness.

## Exceptions

- Non-production exploration may use lighter checks if isolated and clearly not used for decisions.
- Some models lack immediate ground truth; use proxy metrics, delayed labels, human review, or guardrail metrics.
- High-risk decisions may require human-in-the-loop, additional safety reviews, or stricter slice gates.
- Batch scoring may use pipeline freshness and output validation instead of synchronous serving latency.

## Response Quality Bar

- Lead with the launch decision, eval gate, or model-risk blocker.
- Cover offline/online evals, guardrails, drift/skew, rollback, and monitoring before optional ML-platform breadth.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and rollback or shadow-mode criteria where relevant.
- State required evidence such as offline metrics, online guardrails, cohort slices, drift signals, and rollback proof; do not claim unseen evidence.
- For production monitoring, give thresholded alerts or stop conditions for at least two signals, such as prediction drift, training-versus-serving feature distribution drift, serving latency, data freshness, saturation, or quota exhaustion.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside model-serving reliability and evaluation unless the prompt asks for broader product or research strategy.
- Be concise: avoid generic ML background and prefer compact eval and rollout matrices.

## Required Outputs

- ML production readiness checklist.
- Data and feature validation plan.
- Training-serving skew review.
- Offline and production eval gate plan.
- AI/ML failure-mode and adversarial/security evaluation plan where misuse or dependency manipulation can affect users.
- Versioning and artifact lineage record.
- Model rollout and rollback plan.
- Drift, quality, freshness, serving latency, and capacity/quota monitoring requirements with alert thresholds and owners.
- Owner, incident path, and residual risk notes.

## Evidence Gates

- `data_validation`: training and serving data have schema, freshness, distribution, and missingness checks.
- `eval_gate`: promotion thresholds, regression checks, and slice criteria are stated.
- `skew_check`: training-serving feature and transform differences are reviewed.
- `version_lineage`: model, code, data, features, config, and eval result are linked.
- `monitoring_thresholds`: prediction drift, feature distribution drift, latency, freshness, saturation, or quota signals have alert thresholds and owners.
- `rollback_check`: prior model or safe fallback is available with trigger criteria.

## Red Flags - Stop And Rework

- Offline aggregate accuracy is the only launch gate.
- Feature generation differs between training and serving with no skew check.
- Model artifact cannot be tied to data, code, config, and eval result.
- Rollback requires retraining under incident pressure.
- Drift is monitored without a decision rule, threshold, or owner.
- Serving latency, capacity, or quota risk is discussed without alert thresholds.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating ML as only a model file | Include data, features, serving, evals, rollout, and monitoring. |
| Ignoring slices | Evaluate important cohorts and failure-sensitive segments. |
| Waiting for labels only | Use proxy and delayed-quality signals where ground truth lags. |
| No fallback | Keep prior model, rule baseline, or disable path where impact warrants it. |
| Vague monitoring | Add alert thresholds for drift, feature distribution, latency, and capacity or quota signals. |
---
name: ml-reliability-and-evaluation
description: "Use to gate a production ML model promotion on data validation, eval thresholds, training-serving skew, drift monitoring, and rollback path — before a new artifact replaces the live one."
---

# ML Systems Reliability And Evaluation

## Iron Law

```
NO MODEL PROMOTION WITHOUT DATA VALIDATION, EVAL GATES, SERVING CHECKS, AND ROLLBACK
```

Offline accuracy alone is not production readiness.

## Overview

Production ML reliability is software reliability plus data reliability plus model behavior reliability.

**Core principle:** promote models only when data, features, evals, serving behavior, rollout, monitoring, and rollback are all controlled.

## When To Use

- The user asks about production ML readiness, model serving, training pipelines, eval gates, feature validation, training-serving skew, drift, model rollout, or model rollback.
- A model artifact, feature pipeline, training job, or inference path is changing.
- The user needs to monitor model quality, prediction distribution, data drift, or serving latency.
- A launch or PRR includes ML behavior.

## When Not To Use

- The work is generic warehouse/ETL reliability with no model production concern; defer to `data-pipeline-reliability`.
- The request is broad AI policy or model strategy; out of scope unless framed as production engineering.
- The system is an LLM or agent app with prompt/tool security risk; defer to `llm-application-security`.
- The work is offline experimentation only and will not affect production.

## Inputs To Collect

- Model owner, use case, user impact, failure consequence, and production tier.
- Training data, feature definitions, schemas, labels, transform code, and serving data sources.
- Offline eval metrics, acceptance thresholds, slices/cohorts, fairness/safety checks where relevant, and regression history.
- Training-serving consistency checks, feature freshness, null/default behavior, and schema drift.
- Model artifact version, data version, config, dependencies, and rollout unit.
- Serving SLOs, latency, saturation, fallback behavior, monitoring, and rollback path.
- Drift, quality, feedback, incident, and human-review signals.

## Workflow

1. **Establish a non-ML baseline.** Confirm the system needs ML and has a deterministic fallback or baseline where appropriate.
2. **Validate data and features.** Check schema, ranges, missingness, distributions, freshness, and transform consistency.
3. **Check training-serving skew.** Compare feature generation, preprocessing, defaults, and dependency versions across training and serving.
4. **Define eval gates.** Use offline metrics, slice metrics, regression tests, adversarial/security checks, safety/business constraints, and minimum deltas for promotion.
5. **Version everything.** Link model artifact, code, features, data snapshot, config, eval result, and serving environment.
6. **Roll out progressively.** Use shadow, canary, cohort, percentage, or holdback where feasible; monitor serving and model behavior.
7. **Monitor production with thresholds.** Track serving SLOs, prediction distribution, feature drift, data freshness, quality proxies, feedback loops, and capacity or quota saturation; name alert thresholds or rollback triggers for at least two of those signals.
8. **Prepare rollback.** Keep prior artifact/config available and define when to rollback, disable, or route to baseline.

## Synthesized Default

Gate ML releases on data validation, eval results, threat-informed failure-mode checks, training-serving consistency, versioned artifacts, progressive rollout, serving SLOs, thresholded drift and serving monitoring, and rollback. Treat model-only evaluation as insufficient for production readiness.

## Exceptions

- Non-production exploration may use lighter checks if isolated and clearly not used for decisions.
- Some models lack immediate ground truth; use proxy metrics, delayed labels, human review, or guardrail metrics.
- High-risk decisions may require human-in-the-loop, additional safety reviews, or stricter slice gates.
- Batch scoring may use pipeline freshness and output validation instead of synchronous serving latency.

## Response Quality Bar

- Lead with the launch decision, eval gate, or model-risk blocker.
- Cover offline/online evals, guardrails, drift/skew, rollback, and monitoring before optional ML-platform breadth.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and rollback or shadow-mode criteria where relevant.
- State required evidence such as offline metrics, online guardrails, cohort slices, drift signals, and rollback proof; do not claim unseen evidence.
- For production monitoring, give thresholded alerts or stop conditions for at least two signals, such as prediction drift, training-versus-serving feature distribution drift, serving latency, data freshness, saturation, or quota exhaustion.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside model-serving reliability and evaluation unless the prompt asks for broader product or research strategy.
- Be concise: avoid generic ML background and prefer compact eval and rollout matrices.

## Required Outputs

- ML production readiness checklist.
- Data and feature validation plan.
- Training-serving skew review.
- Offline and production eval gate plan.
- AI/ML failure-mode and adversarial/security evaluation plan where misuse or dependency manipulation can affect users.
- Versioning and artifact lineage record.
- Model rollout and rollback plan.
- Drift, quality, freshness, serving latency, and capacity/quota monitoring requirements with alert thresholds and owners.
- Owner, incident path, and residual risk notes.

## Evidence Gates

- `data_validation`: training and serving data have schema, freshness, distribution, and missingness checks.
- `eval_gate`: promotion thresholds, regression checks, and slice criteria are stated.
- `skew_check`: training-serving feature and transform differences are reviewed.
- `version_lineage`: model, code, data, features, config, and eval result are linked.
- `monitoring_thresholds`: prediction drift, feature distribution drift, latency, freshness, saturation, or quota signals have alert thresholds and owners.
- `rollback_check`: prior model or safe fallback is available with trigger criteria.

## Red Flags - Stop And Rework

- Offline aggregate accuracy is the only launch gate.
- Feature generation differs between training and serving with no skew check.
- Model artifact cannot be tied to data, code, config, and eval result.
- Rollback requires retraining under incident pressure.
- Drift is monitored without a decision rule, threshold, or owner.
- Serving latency, capacity, or quota risk is discussed without alert thresholds.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating ML as only a model file | Include data, features, serving, evals, rollout, and monitoring. |
| Ignoring slices | Evaluate important cohorts and failure-sensitive segments. |
| Waiting for labels only | Use proxy and delayed-quality signals where ground truth lags. |
| No fallback | Keep prior model, rule baseline, or disable path where impact warrants it. |
| Vague monitoring | Add alert thresholds for drift, feature distribution, latency, and capacity or quota signals. |
