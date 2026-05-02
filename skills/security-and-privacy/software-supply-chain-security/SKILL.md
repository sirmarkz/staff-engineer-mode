---
name: software-supply-chain-security
description: "Use when the user asks about build/deploy security, provenance, dependency inventory, artifact signing, artifact supply chain, builder isolation, secret scanning, or build/deploy integrity. Do not use for routine dependency updates or runtime app authorization."
---

# Software Supply Chain Security

## Overview

Production should run artifacts whose source, build, dependencies, and approval path can be proven.

**Core principle:** protect the source-to-deploy chain with reviewed changes, isolated builds, provenance, artifact integrity, least-privilege automation, and deployment verification.

## Iron Law

```
NO PRODUCTION ARTIFACT WITHOUT SOURCE, BUILD, PROVENANCE, INTEGRITY, AND ADMISSION EVIDENCE
```

If an artifact cannot be traced back to reviewed source and a trusted build path, it should not be trusted for production.

## When To Use

- The user asks about build/deploy security, builder isolation, artifact signing, provenance, dependency inventories, deployment admission, secret scanning, or build/deploy integrity.
- A production path lacks proof of what source and build produced an artifact.
- Automation credentials can modify source, build, registry, deployment, or infrastructure.
- The team needs supply-chain controls or evidence for release integrity.

## When Not To Use

- The work is routine package updates or dead-code cleanup; use dependency hygiene.
- The issue is a deployed vulnerability with patch SLA; use vulnerability management.
- The question is runtime authorization or service access; use zero-trust identity.
- The request is broad compliance program management; out of scope unless framed as engineering evidence.

## Inputs To Collect

- Repositories, branches, code review rules, merge rights, and source protection.
- Build system, workers, isolation, inputs, dependencies, environment, and reproducibility needs.
- Artifact types, registries, signing, checksums, provenance, dependency inventories, and retention.
- Deployment path, admission controls, environment promotion, and rollback.
- Automation credentials, token scopes, secret exposure, and third-party integrations.
- Scanning coverage, vulnerability handoff, and incident/exception process.

## Workflow

1. **Map source to deploy.** Draw every step from code change through build, artifact, registry, deployment, and runtime admission.
2. **Protect source.** Require reviewed changes, branch protections, ownership, and tamper-evident history for production paths.
3. **Harden builders.** Use isolated or ephemeral build environments for production artifacts; minimize mutable state and privileged credentials.
4. **Record provenance.** Produce metadata linking artifact identity, source revision, reviewed change, build steps, builder identity, dependency inputs, build time, and approval path. Tier-critical paths should make this metadata verifiable at deployment.
5. **Protect artifacts.** Sign or otherwise verify integrity; store artifacts in controlled registries with retention and rollback.
6. **Generate inventories.** Produce structured, machine-readable dependency inventories when they support vulnerability response, customer evidence, or audit workflows; name the consumer so the artifact is not theater.
7. **Decide reproducibility level.** State whether the path needs byte-identical, declared-nondeterminism, or content-equivalent rebuild evidence, and record any expected differences.
8. **Standardize secure pipelines.** Use governed templates or reusable pipeline modules for production paths so scanning, integrity checks, dependency inventories, approvals, and secure compute are not optional per repository.
9. **Control deployment.** Verify artifact integrity/provenance at admission and keep environment promotion auditable.
10. **Constrain automation.** Use least-privilege, short-lived credentials and secret scanning across source/build paths.
11. **Screen common attack classes.** Check for dependency confusion, typo or name-squatting, malicious maintainer takeover, build-cache poisoning, unreviewed install hooks, and compromised automation credentials.

## Synthesized Default

Use reviewed source, governed production pipelines, isolated builds, provenance, signed or integrity-verified artifacts, dependency inventory, least-privilege automation, secret scanning, and deployment admission checks for production paths. Keep routine dependency hygiene and deployed vulnerability remediation as adjacent but separate workflows.

## Exceptions

- Low-risk prototypes may use lighter controls if isolated from production data and deployment.
- Legacy build systems may need staged improvements; record missing provenance/signing as exceptions with owners.
- Dependency inventories are useful when consumed for vulnerability, customer, or audit workflows; do not generate unused artifacts as theater.
- Emergency patches can use expedited paths only with post-facto provenance and review evidence.
- Release engineering owns reproducible build mechanics; this skill owns the trust boundary, provenance expectations, artifact integrity, and admission policy.

## Response Quality Bar

- Lead with the source-to-deploy risk, control gap, provenance plan, or exception register requested.
- Cover source review, builder trust, artifact integrity, provenance, dependency inventory, deployment admission, automation credentials, and secret scanning before optional supply-chain breadth.
- Make recommendations actionable with owners, control locations, validation commands, admission gates, exception expiry, and remediation steps where relevant.
- State required evidence such as protected branch settings, build identity, isolation model, artifact metadata, signatures or digests, dependency-inventory consumers, deploy policy, and credential scopes; do not claim unseen evidence.
- Stay inside supply-chain integrity. Route routine dependency hygiene or deployed vulnerability remediation only when those are the central unresolved risk.
- Be concise: avoid generic framework background and prefer compact control matrices and evidence maps.

## Required Outputs

- Source-to-deploy supply-chain map.
- Control matrix for source, build, artifact, registry, deployment, and automation.
- Provenance and artifact integrity plan with minimum fields: artifact identity, source revision, reviewed change, builder identity, dependency inputs, build time, approval path, and verification location.
- Structured dependency inventory policy with producer, consumer, retention, and vulnerability handoff.
- Build and deployment credential hardening plan.
- Secret scanning and exposure response plan.
- Exceptions with owner, expiry, and compensating controls.

## Evidence Gates

- `source_review`: production source changes require review and protected merge path.
- `builder_trust`: build environment identity, isolation, and credential scope are documented.
- `provenance_check`: production artifacts have source/build provenance or a tracked exception.
- `integrity_check`: deployment path verifies artifact integrity before promotion/admission.
- `credential_check`: automation credentials are least privilege, short lived where possible, and secret-scanned.

## Red Flags - Stop And Rework

- Anyone with build access can deploy unreviewed code.
- Production artifacts are rebuilt differently per environment without traceability.
- Long-lived automation tokens can modify source, artifacts, and deployment.
- Dependency inventories are generated but never used for vulnerability response or evidence.
- Artifact signing exists but deployment never verifies it.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Scanning as the only control | Add provenance, integrity, least privilege, and admission. |
| Trusting the registry blindly | Verify artifact identity and provenance at deployment. |
| Mixing routine updates with supply-chain trust | Route routine dependency hygiene separately. |
| Ignoring build credentials | Treat automation credentials as production access. |
