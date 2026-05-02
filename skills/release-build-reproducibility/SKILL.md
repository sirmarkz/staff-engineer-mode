---
name: release-build-reproducibility
description: "Use when the user asks about build systems, release branches, release trains, hermetic builds, reproducible builds, build cache safety, packaging, versioning, artifact promotion, flaky builds, slow builds, or cutting a release. Do not use for rollout/canary behavior after an artifact is built."
---

# Release Engineering And Build Reproducibility

## Overview

Release engineering turns source changes into trustworthy artifacts.

**Core principle:** build from pinned inputs in a controlled environment, identify the artifact precisely, and promote that artifact through validation and release.

## Iron Law

```
NO RELEASE WITHOUT PINNED INPUTS, REPRODUCIBLE BUILD, IMMUTABLE ARTIFACT, AND TRACEABLE PROMOTION
```

If a team cannot tell exactly what was built, how it was built, and where it was promoted, it does not have a reliable release.

## When To Use

- The user asks about build systems, release engineering, release trains, release branches, release candidates, packaging, versioning, or artifact promotion.
- Builds are slow, flaky, non-hermetic, non-reproducible, cache-sensitive, or dependent on local developer machines.
- A release process needs build-once promotion, release cut criteria, release branch policy, or artifact identity.
- A team needs to separate build, deploy, and release responsibilities.

## When Not To Use

- The main topic is rollout stages, canaries, feature flags, rollback, or production exposure; use progressive delivery.
- The main topic is artifact signing, provenance maturity, dependency inventory, builder trust, or deploy admission; use supply-chain security.
- The main topic is code review latency or developer workflow policy; use engineering productivity.
- The main topic is an actively vulnerable deployed artifact; use vulnerability management.

## Inputs To Collect

- Source revision, branch/release-line model, release cadence, owners, and supported versions.
- Build graph, test graph, generated code, packaging steps, and artifact outputs.
- Pinned dependencies, lockfiles, toolchains, build images, environment variables, and network access.
- Cache strategy, cache keys, invalidation rules, remote/local differences, and flaky build evidence.
- Release gates: tests, static checks, compatibility checks, security checks, and approval requirements.
- Artifact identity, metadata, storage, promotion path, deployment consumers, and rollback path.

## Workflow

1. **Separate concerns.** Distinguish developer build feedback, CI validation, artifact creation, deployment, and user-facing release.
2. **Pin every input.** Record source revision, dependencies, toolchains, build image, generators, and configuration needed to recreate the artifact.
3. **Make builds hermetic.** Remove undeclared local files, ambient credentials, network fetches, clock-sensitive output, and machine-specific behavior.
4. **Stabilize the graph.** Define build/test targets, cache keys, generated-output ownership, and invalidation rules so cache hits cannot hide missing dependencies.
5. **Build once, promote many.** Create an immutable artifact once and move the same artifact through validation, staging, and production.
6. **Define release lines.** Choose trunk release, release branch, train, or candidate flow based on support window and rollback needs.
7. **Keep main recoverable.** Prefer short-lived topic branches, protected main, and release branches with explicit cherry-pick/backport policy so hotfixes do not disappear from the next release.
8. **Gate releases deliberately.** Keep gates fast and signal-rich; quarantine flaky checks, but do not let flakes silently weaken release evidence.
9. **Record traceability.** Link artifact, source, build logs, checks, release decision, deployment, and rollback target.

## Synthesized Default

Use hermetic, reproducible, build-once promotion with pinned inputs, explicit artifact identity, fast automated checks, and traceable release metadata. Prefer trunk-compatible releases with short-lived topic branches and clearly owned release branches unless support windows require maintained release lines.

## Exceptions

- Emergency fixes may use a shortened gate path, but artifact identity, pinned inputs, and rollback target still apply.
- Long-lived support branches are appropriate when customers, platforms, or compliance commitments require maintained versions.
- Some generated artifacts cannot be byte-identical across platforms; require semantic reproducibility and record the allowed nondeterminism.
- Experimental internal tools may use lighter packaging if they do not create production artifacts.

## Response Quality Bar

- Lead with the release pipeline decision, reproducibility gap, flaky-build diagnosis, or release-cut plan requested.
- Cover pinned inputs, hermeticity, artifact identity, cache safety, release gates, promotion, and rollback traceability before optional release topics.
- Make recommendations actionable with owners, build metadata, validation commands, gates, stop criteria, and rollback artifact references where relevant.
- State required evidence such as source revision, lockfiles, toolchain versions, build images, cache keys, build logs, artifact metadata, and promotion records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside build and release engineering. Route rollout/canary behavior or supply-chain signing only when those are the central unresolved risk.
- Be concise: avoid generic release-process background and prefer compact pipeline maps, hermeticity checklists, and traceability tables.

## Required Outputs

- Build and release pipeline map.
- Pinned-input and hermeticity checklist.
- Artifact identity and metadata standard.
- Release branch/train/candidate policy.
- Build cache and invalidation policy.
- Release gate list with required versus advisory checks.
- Promotion and rollback traceability plan.

## Evidence Gates

- `input_pinning`: source, dependencies, toolchains, generated inputs, and build environment are pinned or explicitly exempted.
- `hermeticity_check`: build does not depend on undeclared local files, ambient network, machine state, or unscoped credentials.
- `artifact_identity`: artifact has immutable identifier, source revision, build metadata, and storage location.
- `cache_safety`: cache keys and invalidation rules prove stale output cannot satisfy changed inputs.
- `release_trace`: promotion and rollback path link artifact, checks, deployment, and owner.

## Red Flags - Stop And Rework

- Release artifacts are rebuilt separately for each environment.
- A build passes only on one developer machine or one CI worker.
- Cache misses are slow, but cache hits are not trusted.
- Release branches exist indefinitely with no owner, support window, or merge policy.
- Rollback target is "whatever was previously deployed" with no artifact identity.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Treating deploy as release | Build and deploy artifacts separately from user exposure. |
| Chasing speed before determinism | Make the build correct and reproducible, then optimize graph and cache. |
| Ignoring generated code | Treat generators and generated outputs as declared build inputs. |
| Letting flakes erode gates | Quarantine, own, and fix flakes with expiry. |
