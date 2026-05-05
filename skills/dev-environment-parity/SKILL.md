---
name: dev-environment-parity
description: "Use to diagnose 'works on my machine' failures or build a parity matrix across local, CI, staging, and production — covering dependencies, config, data shape, time, network, and secrets — with a drift budget."
---

# Dev Environment Parity

## Overview

Produces a parity matrix across local, CI, staging, and production for the dimensions that decide whether a fix carries: dependency versions, configuration, data shape, time and clock behavior, network policy, and secret handling. Produces a drift-detection plan, a defined drift budget with action triggers, and a required-parity-versus-allowed-divergence taxonomy. Refuses to call a change shipped when it works only in the environment it was written in.

**Core principle:** environments are a contract. Allowed divergence is named, bounded, and monitored; unnamed divergence is the bug that hides until the worst possible moment.

## Iron Law

```
NO FIX THAT WORKS ONLY LOCALLY COUNTS AS FIXED
```

A change that passes locally but fails in CI, passes in CI but fails in staging, or passes in staging but fails in production is unfinished work. The drift that hid the failure is the real defect.

## When To Use

- The user reports a "works on my machine" failure or a green-CI-but-broken-staging failure.
- A migration, dependency update, or configuration change behaves differently across environments and the team needs to know which differences matter.
- A new environment (preview, ephemeral, branch-per-developer) is being introduced and the team needs to define how closely it must match the others.
- A team is moving to ephemeral preview environments and needs a parity contract before relying on them as a release gate.
- An incident's root cause was a divergence (different library version, different timezone, different network egress) and the team wants to prevent the next one.
- A new contributor's local setup keeps producing diffs that fail CI for environment reasons rather than logic reasons.
- An AI coding agent is editing in an environment whose parity to CI or production is undeclared, and its diffs pass locally but break elsewhere.

## When Not To Use

- The work is producing reproducible release artifacts (pinned inputs, hermetic build, signed promotion); use `release-build-reproducibility`.
- The work is declaring infrastructure desired state, drift reconciliation against that desired state, or admission policy; use `infrastructure-and-policy-as-code`.
- The work is platform templates, golden paths, or a service catalog; use `platform-golden-paths`.
- The work is configuration safety in a single environment (validation, preview, blast radius, rollback); use `configuration-and-automation-safety`.
- The work is secret rotation, key management, or workload identity; use `identity-and-secrets`.
- The work is internal service mesh, discovery, or routing; use `internal-service-networking`.
- The work is an active production incident whose triage cannot wait for parity analysis; use `incident-response-and-postmortems`.

## Inputs To Collect

- Environment inventory: local developer machines, CI runners, ephemeral or preview environments, staging, production, and any tier in between, with owner per environment.
- Dependency manifest per environment: language runtime version, system library versions, package lockfile state, and how each environment resolves them.
- Configuration manifest per environment: feature flags, environment variables, defaults, overrides, and the rule for how production-like each non-prod environment is.
- Data-shape manifest: schema versions, sample data sources, and whether non-prod data shape (cardinality, distribution, size) resembles production for the paths under test.
- Time and clock behavior: timezone, locale, NTP configuration, and any code paths that depend on wall-clock or monotonic time.
- Network policy: egress allowlists, ingress filters, DNS resolution, internal service reachability, and outbound rate or timeout differences across environments.
- Secret handling: how secrets are injected, scoped, and rotated per environment, and whether a non-prod environment has access to production-scope secrets.
- Recent incidents whose root cause was an environment divergence and the dimension responsible.
- Existing drift signals or detectors and their false-positive rate.

## Workflow

1. **Inventory the environments.** Name every environment a developer or CI uses, its purpose, its owner, and the tier of confidence its results carry.
2. **Build the parity matrix.** For each environment pair, list the parity status across dimensions: dependency versions, configuration, data shape, time and clock, network policy, and secret handling. Mark each cell as required-parity, allowed-divergence (with reason), or unknown (a finding by itself).
3. **Define the required-parity dimensions.** Decide which dimensions must match across environments to keep test results meaningful. Dependency versions and configuration shape are usually required; production data values are usually forbidden in non-prod.
4. **Define the allowed-divergence dimensions.** Decide which dimensions are intentionally different and what the contract is: data scale, secret values, account identifiers, real third-party dependencies versus stand-ins, network egress scope.
5. **Set the drift budget.** State the acceptable size of divergence per dimension (for example, dependency-version skew within one minor version, configuration drift within a defined allowlist) and the action triggered when the budget is exceeded.
6. **Detect drift.** For each parity-required dimension, instrument a comparison: hash the dependency lock, snapshot the configuration, compare schema versions, compare clock and locale settings, compare network reachability matrices. Drift detection runs on a defined cadence, not only on incident.
7. **Set action triggers.** When drift exceeds the budget, the action is not "file a ticket." The action is named: block CI promotion, block deploy to the next environment, page the environment owner, or open an incident-grade follow-up.
8. **Handle ephemeral and preview environments.** Ephemeral environments are useful only when their parity contract is explicit. State which dimensions they replicate from production and which they intentionally diverge on, so a passing preview means something specific.
9. **Bound third-party dependencies in non-prod.** Decide per dependency whether non-prod uses a stand-in, a sandbox, or the real production endpoint. Each choice has different parity properties; document them.
10. **Reproduce the failure across environments.** When a "works here, fails there" failure appears, the first action is to reproduce in each tier and identify the dimension responsible. The fix lives in that dimension, not only in the failing tier.
11. **Update the parity contract.** After every drift-related incident, update the matrix, the drift budget, or the detection so the same divergence cannot hide again.

## Synthesized Default

Define required parity and allowed divergence per dimension. Detect drift on parity-required dimensions on a defined cadence. Bound divergence with a budget and a named action when the budget is exceeded. Treat ephemeral and preview environments as parity-explicit, not parity-by-vibes. Reproduce environment-divergent failures in every tier before declaring a fix. Update the contract after every drift-rooted incident.

## Exceptions

- A research or exploration environment may diverge intentionally; results from it cannot be used as release evidence.
- A regulated workload may forbid production-realistic data in non-prod; the parity contract then privileges shape and schema over content, and the test data lives in a different fixture class.
- Performance and load environments may run on smaller capacity by design; the parity contract specifies which signals are still meaningful at reduced scale.
- A pre-production environment that exists only to exercise the rollout machinery may waive data and traffic parity, but must hold dependency, configuration, and policy parity.
- Local laptop environments may run a reduced subset of services with a documented stand-in policy, but a fix verified only against stand-ins is not yet a fix.

## Response Quality Bar

- Lead with the parity matrix, drift budget, drift-detection plan, allowed-divergence taxonomy, or environment-failure reproduction requested.
- When diagnosing a "passes here, fails there" failure, name the anti-pattern in plain language ("the local pass is a mocked happy-path result", "the fix is environment-only and does not count as shipped") AND name the enforcement that would have caught it (CI route-coverage check, readiness gate, lint, review checklist). Do not let the structured matrix replace the verdict.
- Cover dependencies, configuration, data shape, time and clock, network policy, and secret handling before optional environment breadth.
- Make recommendations actionable with per-dimension parity status, drift budget, detection cadence, action trigger, and environment owner.
- State required evidence such as dependency-lock comparisons, configuration snapshots, schema versions, clock settings, network reachability checks, and the drift signals that fired or did not fire; do not claim parity without the comparison.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside running-environment parity. Route release-artifact reproducibility, infrastructure desired state, platform templates, single-environment configuration safety, secret lifecycle, internal mesh, and incident command to the owning specialist.
- Be concise: prefer compact parity matrices and budget tables over generic environment-management prose.

## Required Outputs

- Parity matrix across local, CI, ephemeral or preview, staging, and production for each dimension (dependencies, configuration, data shape, time and clock, network policy, secret handling) with required-parity, allowed-divergence, or unknown per cell.
- Required-parity-versus-allowed-divergence taxonomy: which dimensions must match, which may diverge with reason, and which are forbidden in non-prod.
- Drift budget per dimension with the size of acceptable divergence and the named action when exceeded.
- Drift-detection plan listing the comparison method, cadence, source of truth, and owner per dimension.
- Action-trigger table mapping each drift-budget breach to the action taken (block CI promotion, block deploy, page environment owner, open follow-up).
- Ephemeral and preview environment contract stating replicated and diverged dimensions and what a passing run in those environments proves.
- Third-party dependency stand-in policy per dependency with the parity properties of each choice.
- Reproduction protocol for "works here, fails there" failures with the order of tiers to reproduce in and the dimension-isolation steps.
- Follow-up routes to release reproducibility, infrastructure-as-code, platform paths, configuration safety, identity, internal networking, or incident response as needed.

## Evidence Gates

- `environment_inventory_present`: every environment a developer or CI uses is named with owner and tier of confidence.
- `parity_matrix_present`: parity status is recorded per dimension per environment pair; unknowns are listed as findings.
- `divergence_taxonomy`: required-parity, allowed-divergence with reason, and forbidden combinations are explicit.
- `drift_budget_set`: each parity-required dimension has a numeric or categorical budget and a named action when exceeded.
- `drift_detection_active`: each parity-required dimension has an active comparison with cadence and owner.
- `action_triggers_named`: drift-budget breaches map to specific actions, not generic ticket creation.
- `ephemeral_contract`: preview and ephemeral environments declare replicated and diverged dimensions explicitly.
- `reproduction_protocol`: a documented order and method for reproducing environment-divergent failures across tiers exists and is used.

## Red Flags - Stop And Rework

- A fix is declared shipped because it passes locally and the next environment is "probably fine."
- Dependency versions, configuration, or schema differ across environments and no comparison runs.
- Ephemeral or preview environments are treated as production-equivalent without a stated parity contract.
- Production-scope secrets are accessible from a non-prod environment with no recorded reason.
- A drift detector exists but the action on breach is "send an email."
- An incident's root cause was an environment divergence and the parity contract was not updated.
- Time, locale, or clock differences across environments are unmeasured even after a date- or timezone-related bug.
- Stand-in dependencies in non-prod produce different success contracts than the real dependency in production and nobody has documented the gap.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| "Works on my machine" closes the ticket | Reproduce across tiers; the fix lives in the diverged dimension. |
| Drift treated only as developer annoyance | Set a drift budget with a named action when exceeded. |
| Ephemeral environments trusted by default | State the parity contract; results count only for replicated dimensions. |
| Secrets shared across tiers for convenience | Scope secrets per environment; document any cross-tier exception with owner. |
| Detection without action | Map every breach to block, page, or open follow-up. |
| Divergence considered only on incident | Compare parity-required dimensions on a defined cadence. |
| Treating data shape and data values the same | Forbid production values in non-prod; require shape parity for the paths under test. |
