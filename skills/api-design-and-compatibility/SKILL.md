---
name: api-design-and-compatibility
description: "Use when API contracts, versioning, compatibility, deprecation, pagination, errors, or client migration are central."
---

# API Design And Compatibility

## Overview

An API is a long-lived contract with unknown clients, retries, partial failures, and migration lag.

**Core principle:** make contracts explicit, evolvable, retry-safe, observable, and compatible by default.

## Iron Law

```
NO API CHANGE WITHOUT COMPATIBILITY, ERROR, IDEMPOTENCY, AND MIGRATION RULES
```

If clients cannot tell what changed, how errors behave, whether retries are safe, or how to migrate, the API is not ready.

## When To Use

- The user asks for API design, service contract review, versioning, compatibility, deprecation, pagination, error models, idempotency, or client migration.
- A change adds, removes, renames, retypes, or changes semantics of fields, operations, events, or resources exposed to another component or client.
- The user asks whether an endpoint, schema, interface, or service contract can evolve safely.
- A retryable mutating operation needs idempotency behavior.

## When Not To Use

- The data model is purely internal and not exposed through an interface.
- The main issue is per-call timeout/retry behavior rather than API contract; defer to `dependency-resilience`.
- The request is broad secure design; defer to `secure-sdlc-and-threat-modeling` unless API contract is central.
- The request is event schema evolution inside an asynchronous workflow; defer to `event-workflows` unless the external API contract is the main surface.

## Inputs To Collect

- Consumers, owners, client release cadence, compatibility expectations, and deprecation tolerance.
- Operations/resources, request and response fields, event shapes, status/error semantics, and side effects.
- Authentication, authorization, rate limits, quotas, tenant context, audit requirements, and abuse cases.
- Retry behavior, idempotency needs, duplicate suppression, and replay windows.
- Pagination, filtering, ordering, sorting, cursor stability, and consistency expectations.
- Versioning policy, migration telemetry, usage by client/version, and existing deprecation process.

## Workflow

1. **Define the contract boundary.** State who consumes the API, whether it is public or interservice, what compatibility promise exists, and which behaviors are observable by clients.
2. **Classify the change.** Mark each field, operation, error, and semantic change as compatible, conditionally compatible, or breaking.
3. **Prefer additive evolution.** Add optional fields, new operations, new enum values with tolerant readers, and new versions only when needed.
4. **Design error semantics.** Use stable machine-readable error categories, human-readable detail, retryability, correlation identifiers, and safe redaction.
5. **Make retries safe.** For mutating operations that clients may retry, require idempotency keys, operation identifiers, or dedupe semantics.
6. **Handle collections deliberately.** Prefer stable cursor-style pagination for mutable collections; define ordering, filtering, empty results, and page-token expiration.
7. **Plan migration.** Use telemetry to identify clients, publish deprecation windows, support overlap, and define removal gates.
8. **Check security and abuse.** Include authorization, rate limits, tenant isolation, audit events, and input validation as part of the contract.

## Synthesized Default

Design APIs around domain contracts, not internal storage shape. Use additive compatibility first and explicit versions only when semantics must break. Mutations that can be retried need idempotency. Errors should be structured, stable, safe to expose, and tied to retry behavior. Deprecation requires telemetry, migration support, and a removal gate.

## Exceptions

- Internal APIs with one deployable client may use tighter migration windows, but still need compatibility during rollout.
- A breaking change is acceptable when security, correctness, or unsustainable complexity justifies it and a migration plan exists.
- Cursor pagination may be unnecessary for immutable or tiny bounded collections.
- Protocol-specific conventions may shape syntax, but the compatibility, idempotency, error, and migration rules still apply.

## Response Quality Bar

- Lead with the concrete approval decision, blocker list, or migration plan requested.
- Cover all compatibility, error, idempotency, and migration risks before optional API topics.
- Make recommendations actionable with owners, evidence, gates, stop conditions, and removal criteria where relevant.
- State required evidence such as client telemetry, version usage, retry behavior, and migration readiness; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside the changed API surface. Mention pagination, rate limits, auth, audit, or tenant controls only when the prompt or risk makes them material.
- Be concise: avoid generic API background and prefer compact compatibility matrices or checklists.
- For PR, release-note, or copy-polish requests that hide contract changes, review safety before wording. If the contract is unsafe, lead with the blocker and give corrected release-note constraints only after the compatibility and idempotency fixes.
- Keep narrow reviews bounded to one decision, the material blockers, and the minimum contract changes needed to make the rollout safe.

## Required Outputs

- API contract review with consumers, owners, compatibility class, and risks.
- Compatibility matrix for each changed operation, field, event, and error.
- Versioning and deprecation plan with telemetry and removal gates.
- Error model with retryability, correlation, redaction, and client action.
- Idempotency policy for retryable mutations.
- Pagination, filtering, ordering, and rate-limit policy.
- Security and audit requirements for the exposed surface.

## Evidence Gates

- `compatibility_class`: every contract change is classified as additive, compatible, conditionally compatible, or breaking.
- `idempotency_policy`: retryable mutations have an idempotency or dedupe design.
- `error_model`: errors define machine code, human detail, retryability, correlation, and safe disclosure.
- `migration_telemetry`: deprecation or breaking changes have client usage telemetry and removal gates.
- `abuse_boundary`: authz, rate limits, tenant context, audit, and validation are addressed where relevant.

## Red Flags - Stop And Rework

- "Only internal clients use it" is used to skip compatibility while clients deploy independently.
- A field is repurposed with new semantics instead of adding a new field or version.
- Errors are free-form strings with no retryability or client action.
- Mutating operations are retryable but not idempotent.
- Deprecation depends on guessing client usage instead of telemetry.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Versioning every change | Prefer additive compatible changes; reserve versions for semantic breaks. |
| Treating status codes as the error model | Include stable application error codes and retry guidance. |
| Offset pagination on mutable data | Use stable cursors when inserts/deletes can shift results. |
| Ignoring slow clients | Plan overlap, telemetry, and explicit removal gates. |
