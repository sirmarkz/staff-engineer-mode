---
name: cryptography-and-key-lifecycle
description: "Use to plan certificate rotation, key replacement, or algorithm migration before expiry — anything from a single TLS cert to a fleet-wide signing key transition."
---

# Crypto Agility And Cert Lifecycle

## Iron Law

```
EVERY KEY, CERT, AND ALGORITHM HAS AN OWNER, AN EXPIRY DATE, AND A TESTED REPLACEMENT PATH
```

If a certificate, key, algorithm, or trust root cannot be replaced safely on demand, the system is brittle. "Owner" is a named person or rotation, not "the team"; for solo work the owner is you. "Tested" means the replacement path has been exercised at least once outside an emergency, not just documented.

## Overview

Cryptography fails operationally when keys, certificates, algorithms, and trust roots cannot be inventoried or changed before a deadline.

**Core principle:** keep cryptographic dependencies discoverable, owned, renewable, replaceable, monitored, and tested before expiry or algorithm transition becomes an incident.

## When To Use

- The user asks about certificate expiry, key rotation, cryptographic algorithm transition, trust-chain changes, renewal automation, or cryptographic agility.
- A service depends on certificates, keys, signing, encryption, trust roots, or cryptographic policies that can expire or become deprecated.
- Rotation, revocation, renewal, or algorithm migration could break clients, jobs, devices, or partner integrations.
- The team needs evidence that cryptographic material is owned and replaceable.

## When Not To Use

- The main topic is identity authorization, secret storage, or service access policy; defer to `identity-and-secrets`.
- The main topic is artifact provenance or release signing; defer to `software-supply-chain-security`.
- The main topic is secure design broadly; defer to `secure-sdlc-and-threat-modeling`.
- The request is abstract cryptographic research with no engineering lifecycle decision.

## Inputs To Collect

- Inventory of certificates, keys, algorithms, trust roots, owners, consumers, expiry dates, and renewal paths.
- Usage context: authentication, encryption, signing, verification, storage, transport, or partner integration.
- Rotation process, automation, manual steps, approval, audit, and emergency revocation path.
- Client and dependency compatibility, trust-store update path, fallback behavior, and rollback or roll-forward limits.
- Monitoring, alert thresholds, test environment coverage, and prior expiry or rotation incidents.
- Deprecation deadline, transition target, exception owners, and compensating controls.

## Workflow

1. **Inventory dependencies.** Find cryptographic material, algorithms, trust roots, owners, consumers, and expiry or deprecation dates.
2. **Classify use.** Separate authentication, confidentiality, integrity, signing, verification, and storage use cases.
3. **Assess agility.** Determine whether each dependency can be renewed, rotated, revoked, or replaced without coordinated outage.
4. **Prove compatibility.** Test old/new material and algorithm combinations with representative clients and workloads.
5. **Automate renewal carefully.** Use monitored renewal paths with owner, alerting, audit, and failed-renewal response.
6. **Plan transitions.** Define overlap, dual support, rollout order, client migration, and retirement gates for deprecated algorithms or trust roots.
7. **Prepare emergency response.** Document revocation, compromise response, rollback or roll-forward, and communication path.
8. **Close exceptions.** Track unsupported material with owner, expiry, risk, and compensating controls.

## Synthesized Default

Use a cryptographic inventory, expiry monitoring, owner mapping, tested rotation, dual-support transition windows, compatibility gates, emergency revocation plan, and exception register. Prefer designs where cryptographic material can be replaced independently of full application redeploys.

## Exceptions

- Emergency compromise response may skip ordinary rollout windows, but must preserve audit, owner, and recovery evidence.
- Legacy clients may require overlap windows; keep them time-bound with usage telemetry and migration gates.
- Low-risk development material can use lighter monitoring if isolated from production trust paths.

## Response Quality Bar

- Lead with the lifecycle risk, rotation plan, transition decision, or expiry blocker requested.
- Cover inventory, ownership, expiry, rotation, compatibility, monitoring, emergency revocation, transition windows, and exceptions before optional cryptographic detail.
- Make recommendations actionable with owners, dates, gates, alert thresholds, compatibility tests, and retirement criteria where relevant.
- State required evidence such as inventory, expiry data, consumer list, rotation test output, renewal logs, alert rules, and exception records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside cryptographic lifecycle. Route identity, supply-chain, or secure-design work only when those own the main decision.
- Be concise: prefer inventory and transition matrices over broad cryptography explanation.

## Required Outputs

- Cryptographic dependency inventory.
- Owner, consumer, expiry, and renewal map.
- Rotation and renewal plan.
- Compatibility and dual-support test plan.
- Algorithm or trust-root transition plan.
- Monitoring and alert policy for expiry and failed renewal.
- Emergency revocation and compromise response.
- Exception register with owner, expiry, and compensating control.

## Evidence Gates

- `inventory_owned`: cryptographic material, algorithms, trust roots, owners, consumers, and expiry dates are visible.
- `rotation_test`: renewal, rotation, or replacement is tested for representative consumers.
- `compatibility_window`: old/new compatibility and overlap duration are explicit.
- `expiry_monitoring`: expiry and failed-renewal alerts have owner and response path.
- `transition_gate`: deprecated algorithms or trust roots have migration and retirement criteria.

## Red Flags - Stop And Rework

- Certificates are discovered only when expiry alerts fire.
- A key can be created but not rotated or revoked safely.
- Old and new trust paths are never tested together.
- Manual renewal depends on one person remembering a calendar date.
- Deprecated algorithms remain because clients are unknown.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Inventory only at issuance | Continuously track owner, consumers, and expiry. |
| Rotation without compatibility | Test old/new overlap before rollout. |
| Renewal without alerting | Monitor expiry and failed automation. |
| Permanent exceptions | Require owner, risk, and retirement gate. |