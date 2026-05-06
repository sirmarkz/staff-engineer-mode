---
name: secure-sdlc-and-threat-modeling
description: "Use when asked to threat-model a feature or system — trust boundaries, data flows, abuse cases, controls mapped to tests, residual risk register — before implementation crosses a sensitive boundary."
---

# Secure SDLC And Threat Modeling

## Iron Law

```
NO SECURITY REVIEW WITHOUT TRUST BOUNDARIES, DATA FLOWS, THREATS, CONTROLS, AND TESTS
```

If threats do not map to controls and verification, the review is not actionable.

## Overview

Produces a trust-boundary and data-flow map, an abuse-case table, a control mapping with verification for each high-risk control, and a residual-risk register with explicit user acceptance and expiry. Refuses to accept controls that cannot be tested, gated, or observed.

**Core principle:** model trust boundaries and abuse cases early, then turn threats into testable controls, explicit evidence, and user-accepted residual risk.

## When To Use

- The user asks for threat modeling, secure design, abuse cases, secure SDLC, input validation, authorization review, or application security requirements.
- A change crosses trust boundaries, handles sensitive data, exposes an interface, adds privileged operations, or changes operational access.
- A design needs security acceptance criteria before implementation or launch.
- The user asks what attackers can abuse or what controls must exist.

## When Not To Use

- The main topic is build provenance, artifact signing, dependency inventory, or deployment admission; use `software-supply-chain-security` instead.
- The main topic is identity, secrets, cryptography lifecycle, or access lifecycle; use `identity-and-secrets` or `cryptography-and-key-lifecycle` instead.
- The main topic is LLM prompt, tool, or retrieval abuse; use `llm-application-security` instead.
- The request is broad legal/compliance program management; out of scope unless reframed as engineering controls.

## Inputs To Collect

- Actors, identities, roles, trust boundaries, data flows, assets, and deployment surfaces.
- Data classification, sensitive fields, privacy constraints, logging/telemetry handling, and retention.
- Entry points, APIs, background jobs, admin paths, operational access, and third-party integrations.
- Abuse cases, attacker goals, known vulnerability classes, dependency assumptions, and misuse paths.
- Existing controls, tests, self-review gates, scanning results, incidents, and residual risks.

## Workflow

1. **Map the system.** Identify actors, assets, trust boundaries, data flows, privileged paths, and externally reachable surfaces.
2. **Classify data and operations.** Mark sensitive data, destructive operations, admin actions, and integrity-critical decisions.
3. **List abuse cases.** Write what an attacker or malicious/buggy client tries to accomplish, not only what component might fail.
4. **Apply a threat frame.** Use spoofing, tampering, repudiation, disclosure, denial, privilege elevation, or equivalent categories to avoid blind spots.
5. **Map controls.** Assign authentication, authorization, validation, output handling, rate limits, audit, secrets handling, encryption, and isolation controls.
6. **Make controls testable.** Define unit/integration/security tests, self-review gates, runtime monitors, or operational evidence for each high-risk control.
7. **Record residual risk.** State compensating control, expiry, acceptance condition, and explicit user risk acceptance.
8. **Route specialized surfaces.** Identity/secrets, supply chain, LLM, tenant isolation, and vulnerability remediation go to their specialist skills when central.

## Synthesized Default

Use lightweight threat modeling tied to secure SDLC gates: trust-boundary map, abuse cases, control mapping, test plan, and residual-risk register. Prefer controls that are enforced in code, configuration, self-review gates, runtime evidence, or deployment checks over prose-only policy.

## Exceptions

- Low-risk internal changes can use a small abuse-case checklist if no trust boundary, data sensitivity, or privileged operation changes.
- High-risk financial, privacy, safety, or admin paths need deeper evidence and explicit user risk acceptance.
- Emergency fixes may document the minimal threat review first and complete residual-risk review immediately after mitigation.
- Legal/compliance requirements can constrain controls, but this skill remains focused on engineering implementation and evidence.

## Response Quality Bar

- Lead with the threat-model decision, abuse-case table, control gap, or residual-risk register requested.
- Cover trust boundaries, actors, data flows, privileged paths, abuse cases, control mapping, verification, and residual responsibility before optional security breadth.
- Make recommendations actionable with control points, tests or self-review gates, stop criteria, compensating controls, and expiry where relevant.
- State required evidence such as architecture/data-flow diagrams, auth paths, sensitive data stores, logs, deployment gates, security tests, and runtime checks; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside secure design and threat modeling. Use identity, supply-chain, tenant, LLM, or vulnerability skills only when the prompt makes that specialist surface central.
- Be concise: avoid generic vulnerability category lists and prefer system-specific abuse-case and control tables.

## Required Outputs

- Trust-boundary and data-flow map.
- Threat and abuse-case table.
- Security requirements and control mapping.
- Verification plan for controls.
- Residual-risk register with explicit user acceptance and expiry.
- Sensitive-data and logging review.
- Follow-up checks for identity, supply-chain, tenant, LLM, or vulnerability work.

## Evidence Gates

- `boundary_check`: actors, trust boundaries, data flows, and privileged paths are explicit.
- `threat_coverage`: high-risk abuse cases map to controls.
- `verification_check`: every high-risk control has a test, self-review gate, runtime check, or evidence source.
- `data_handling`: sensitive data storage, transmission, logging, and retention behavior is addressed.
- `risk_responsibility`: residual risks have explicit user acceptance, expiry, and compensating control.

## Red Flags - Stop And Rework

- The threat model lists generic vulnerability categories without system-specific abuse cases.
- Controls are stated but not testable.
- Admin or operational access is ignored.
- Sensitive data appears in logs, traces, errors, or analytics without controls.
- Residual risks have no user acceptance or expiry.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Starting from checklists | Start from trust boundaries and abuse cases. |
| Treating security as final review | Add controls to requirements, code, tests, release, and operations. |
| Focusing only on external attackers | Include insider, compromised credential, confused deputy, and abusive tenant paths. |
| Leaving controls as prose | Tie controls to tests, gates, or evidence. |
