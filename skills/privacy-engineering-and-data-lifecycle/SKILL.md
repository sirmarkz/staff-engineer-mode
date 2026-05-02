---
name: privacy-engineering-and-data-lifecycle
description: "Use when the user asks about data minimization, retention, deletion, privacy-safe telemetry, sensitive-data lifecycle, purpose limitation, consent enforcement as an engineering control, anonymization, pseudonymization, data export, or erasure workflows. Do not use for broad legal privacy policy or tenant isolation."
---

# Privacy Engineering And Data Lifecycle

## Overview

Privacy controls fail when personal data is collected, copied, logged, retained, or derived without a lifecycle.

**Core principle:** collect the least sensitive data that satisfies the purpose, propagate classification through every copy, and make retention, deletion, export, and audit behavior testable.

## Iron Law

```
NO PERSONAL DATA FLOW WITHOUT PURPOSE, CLASSIFICATION, MINIMIZATION, RETENTION, DELETION, AND AUDIT
```

If a team cannot find and delete or justify every copy, it does not control the data lifecycle.

## When To Use

- The user asks about data minimization, retention, deletion, privacy-safe telemetry, sensitive-data lifecycle, anonymization, pseudonymization, or privacy engineering controls.
- A service copies personal or sensitive data into logs, traces, metrics, caches, search indexes, analytics, ML features, exports, backups, or support tools.
- A system needs engineering support for erasure, export, data subject requests, consent/purpose enforcement, or retention schedules.
- A design needs to prevent privacy regressions in release, observability, or data pipelines.

## When Not To Use

- The main issue is tenant boundary enforcement or noisy-neighbor isolation; use tenant isolation.
- The main issue is authentication, authorization, secrets, or cryptography; use zero-trust identity.
- The request is broad legal privacy policy, notice drafting, or regulator/auditor liaison; out of scope unless converted to concrete engineering controls.
- The work is only control mapping; use engineering control evidence.

## Inputs To Collect

- Data inventory: fields, classifications, purpose, source, owner, users, and downstream copies.
- Collection points, transformations, derived data, logs, telemetry, exports, backups, caches, and support views.
- Retention requirements, deletion triggers, legal holds if any, archival behavior, and backup expiration model.
- Data residency, cross-border transfer constraints, third-party processors, and subprocessors that store or receive personal data.
- Consent or purpose constraints that must be enforced by code, configuration, policy, or workflow.
- Access paths, audit events, break-glass behavior, and privacy incident history.
- Validation approach for minimization, redaction, deletion, export correctness, and regression prevention.

## Workflow

1. **Inventory the flow.** Map personal data from collection through storage, processing, telemetry, derived data, export, support, backup, and deletion.
2. **Classify fields.** Mark sensitivity, purpose, owner, allowed uses, residency, retention, and whether the field can be tokenized, redacted, aggregated, or omitted.
3. **Minimize collection.** Remove fields that are not needed; prefer derived, aggregated, tokenized, or on-device/local processing when it satisfies the purpose.
4. **Constrain use.** Enforce purpose, consent, and access constraints in code, data jobs, schemas, policy, or workflow gates.
5. **Control copies.** Apply privacy rules to logs, traces, metrics labels, crash reports, caches, search indexes, analytics, ML features, support tools, and third-party processors.
6. **Engineer deletion and retention.** Define retention classes, delete propagation, deletion markers for asynchronous cleanup, derived-copy repair, backup expiry, audit trail, holds/exclusions, and failure handling.
7. **Assess anonymization claims.** Do not call data anonymized unless reidentification risk has been assessed with an explicit method such as equivalence-class thresholds, diversity checks, noise-based aggregation, motivated-intruder review, or equivalent domain review; otherwise call it pseudonymized, aggregated, or tokenized.
8. **Verify export and erasure.** Test that subject, tenant, or account-scoped export/deletion finds expected copies, includes required third-party paths, uses a defined output format, and reports known exclusions.
9. **Prevent regressions.** Add review gates, schema checks, telemetry redaction tests, and data-lineage alerts for new sensitive fields.

## Synthesized Default

Use privacy-by-design as engineering controls: data inventory, classification, minimization, purpose enforcement, privacy-safe telemetry, retention/deletion automation, export/erasure verification, and audit. Make user/control-plane deletion and retention behavior explicit across primary, derived, and archived copies. Keep legal interpretation outside the skill; make the agreed control enforceable and testable.

## Exceptions

- Legal hold, fraud, security investigation, or financial record retention may override normal deletion; record owner, scope, and expiry.
- Some backup media cannot delete individual records immediately; require bounded expiry, restore-time deletion, and documented risk.
- Aggregated or anonymized data can have different retention only when reidentification risk is assessed.
- Low-risk internal telemetry may use lighter controls if it contains no personal or sensitive data by classification.

## Response Quality Bar

- Lead with the data-flow finding, privacy control design, retention/deletion plan, or blocker list requested.
- Cover inventory, classification, minimization, purpose/access enforcement, telemetry/support controls, retention/deletion propagation, and verification before optional privacy breadth.
- Make recommendations actionable with owners, field-level decisions, control points, test gates, failure handling, and retention or exception expiry where relevant.
- State required evidence such as field inventories, data stores, logs, caches, derived copies, consent/purpose rules, deletion traces, export tests, and backup behavior; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside engineering controls for data lifecycle. Leave legal interpretation out unless the user supplies a requirement to implement.
- Be concise: avoid generic privacy principles and prefer compact field inventories, flow maps, and verification plans.

## Required Outputs

- Personal-data flow inventory.
- Field classification and minimization plan.
- Purpose/consent/access enforcement plan.
- Privacy-safe telemetry and support-tool controls.
- Retention, deletion, backup, and derived-data propagation design.
- Anonymization or pseudonymization risk assessment when those claims are made.
- Export/erasure verification plan with store coverage, third-party coverage, output format, exclusion list, and completeness evidence.
- Regression gates and audit events.

## Evidence Gates

- `data_inventory`: personal and sensitive fields are mapped through primary and derived copies.
- `minimization_check`: every collected field has purpose, owner, and keep/remove/tokenize decision.
- `copy_control`: logs, metrics, traces, caches, exports, support tools, and analytics have privacy handling.
- `deletion_path`: retention, deletion trigger, propagation, backup behavior, and failure handling are defined.
- `anonymization_check`: anonymized or pseudonymized outputs state reidentification-risk method and residual limits.
- `verification_plan`: export, erasure, redaction, or minimization controls have tests or audit evidence.

## Red Flags - Stop And Rework

- Sensitive fields appear in logs or metric labels because they are useful for debugging.
- Retention is "forever" because no one owns deletion.
- Delete requests remove primary rows but leave caches, search indexes, analytics, or ML features.
- Consent or purpose is documented but not enforced by the system.
- Anonymization is claimed without reidentification risk review.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating privacy as policy text | Convert policy decisions into code, config, checks, and audit. |
| Mapping only primary storage | Include telemetry, derived data, backups, exports, and support tools. |
| Redacting after collection | Minimize or tokenize before broad propagation. |
| Trusting manual deletion | Automate propagation and verify with evidence. |
