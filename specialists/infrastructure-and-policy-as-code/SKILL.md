---
name: infrastructure-and-policy-as-code
description: "Use when infrastructure needs declarative desired state, policy checks, drift detection, or environment promotion"
---

# Infrastructure GitOps And Policy As Code

## Iron Law

```
NO INFRASTRUCTURE CHANGE WITHOUT REVIEWABLE DESIRED STATE, POLICY CHECK, DRIFT PLAN, AND ROLLBACK STORY
```

If production infrastructure can change without traceable desired state and reconciliation, the platform is not controlled.

## Overview

Infrastructure is safer when desired state, review, policy, drift, and rollback are explicit.

**Core principle:** make infrastructure changes declarative, reviewed, enforceable, auditable, and continuously reconciled.

## When To Use

- The user asks about infrastructure as code, declarative delivery, policy as code, deployment admission, drift detection, environment promotion, or infrastructure rollback.
- A platform needs enforceable standards for deployment, networking, identity, secrets, tagging, or runtime configuration.
- Manual infrastructure changes are causing drift, outages, or audit gaps.
- The user needs to map platform policies into automated checks.

## When Not To Use

- The request is application business logic policy.
- The work is broad platform product design; use `platform-golden-paths` instead.
- The main topic is artifact provenance or signing; use `software-supply-chain-security` instead.
- The request is one-off architecture without reusable infrastructure policy.

## Inputs To Collect

- Infrastructure resources, environments, responsible change path, desired-state repositories, and change workflow.
- Policy requirements: security, reliability, identity, network, secrets, tagging, cost, and operational standards.
- Deployment/admission points, promotion model, user confirmations, and emergency-change process.
- Drift sources, detection methods, reconciliation authority, and incident history.
- Rollback/roll-forward mechanisms, state storage, locks, and blast-radius controls.
- Secret material, secret references, diff redaction, and state-store protection requirements.

## Workflow

1. **Define desired state.** Identify which infrastructure and runtime config must be represented declaratively.
2. **Keep secrets out of desired-state diffs.** Store secret references, encrypted envelopes, or external secret bindings instead of plaintext; redact plans/diffs and fail the change if secret values appear in review artifacts.
3. **Make changes reviewable in version control.** Require responsible change path, plans/diffs, checks, and user confirmations appropriate to risk.
4. **Encode and test policies.** Convert standards into automated rules with clear failure messages, fixture tests, historical dry runs where feasible, and an exception path.
5. **Separate platform and workload boundaries.** Make shared services, application environments, and responsibility explicit so policy inheritance and exceptions are understandable.
6. **Enforce at the right point.** Use pre-merge, pre-deploy, admission, or continuous audit depending on risk and feasibility.
7. **Detect drift.** Compare actual state to desired state and decide whether to alert, reconcile, or open a ticket.
8. **Plan rollback.** State when rollback is possible, when roll-forward is safer, and how state is protected.
9. **Handle emergencies.** Permit manual break-glass only with separate emergency identity, audit, maximum duration, automatic re-locking, reconciliation, and post-change review.
10. **Protect the source of truth.** Treat desired-state repositories, state stores, lock stores, and reconcilers as production control-plane dependencies with access control, backup, and recovery plans.
11. **Feed evidence.** Surface policy and drift evidence to scorecards and PRR where useful.

## Synthesized Default

Use declarative desired state, reviewed changes, automated policy checks, clear platform/workload boundaries, drift detection, controlled reconciliation, and explicit emergency paths. Policies should be technology-agnostic standards expressed as enforceable rules.

## Exceptions

- Some low-risk experiments can use temporary manual resources if isolated and expiry is enforced.
- Emergency changes may bypass normal review only with audit and reconciliation.
- Not every policy should block immediately; advisory mode helps tune signal before enforcement.
- Roll-forward may be safer than rollback for stateful infrastructure; document the decision.

## Response Quality Bar

- Lead with the infrastructure workflow, policy decision, drift finding, or emergency-change procedure requested.
- Cover desired-state scope, reviewability, plan/diff evidence, policy checks, enforcement mode, drift response, rollback or roll-forward, and emergency reconciliation before optional GitOps breadth.
- Make recommendations actionable with source-of-truth paths, policy rules, exception workflow, detection cadence, reconciliation steps, and audit gates where relevant.
- State required evidence such as repo paths, plans/diffs, user confirmations, policy outputs, drift reports, reconciliation logs, break-glass records, and deployment status; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside infrastructure workflow and policy-as-code. Route platform product work or supply-chain controls only when they are central to the decision.
- Be concise: avoid generic GitOps background and prefer compact workflow and control matrices.

## Required Outputs

- Infrastructure change workflow.
- Desired-state scope and responsibility.
- Policy-as-code control matrix.
- Enforcement point and exception model.
- Drift detection and reconciliation plan.
- Rollback/roll-forward and emergency-change procedure.
- Secret-reference and diff-redaction guardrails.
- Desired-state and state-store protection plan.
- Evidence links for review, policy, drift, and deployment.

## Evidence Gates

- `desired_state`: managed infrastructure scope and source of truth are explicit.
- `review_check`: changes are reviewable with plan/diff, responsible change path, and confirmation path.
- `secret_check`: desired state and review artifacts do not expose plaintext secrets.
- `policy_check`: policies map to engineering standards and enforcement/advisory mode.
- `drift_check`: drift detection and reconciliation response are defined.
- `emergency_check`: manual break-glass changes require separate identity, expiry, audit, reconciliation, and re-locking.

## Red Flags - Stop And Rework

- Production resources are changed manually and never reconciled.
- Policies block without clear error messages or exception path.
- Desired state is split across undocumented sources.
- Secret values appear in desired state, plan output, logs, or review diffs.
- Rollback assumes state can simply be reverted.
- Emergency changes leave permanent drift.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Policy as paperwork | Encode enforceable or auditable checks. |
| Blocking too early | Tune in advisory mode, then enforce high-signal rules. |
| Ignoring drift | Define detection, reconciliation, and the change path. |
| No emergency path | Add audited break-glass and post-change cleanup. |
