---
name: edge-traffic-and-ddos-defense
description: "Use when the user asks about public edge traffic, denial-of-service resilience, edge caching, application-layer filtering, rate-limit policy, bot or abuse throttling, origin protection, global traffic steering, or edge load shedding. Do not use for internal service retries unless public edge defense is central."
---

# Edge Traffic And Denial-Of-Service Defense

## Overview

Public traffic must be filtered and shaped before abusive load reaches expensive systems.

**Core principle:** layer volumetric, protocol, application, identity, and origin protections with telemetry and reversible rules.

## Iron Law

```
NO PUBLIC EDGE EXPOSURE WITHOUT ORIGIN PROTECTION, RATE POLICY, TELEMETRY, AND RULE ROLLBACK
```

If attackers can bypass the edge and hit origin directly, edge defense is incomplete.

## When To Use

- The user asks about public edge traffic, denial-of-service risk, edge caching, application-layer filtering, bot defense, abuse throttling, origin protection, traffic steering, or edge load shedding.
- Public traffic spikes, abusive clients, or bots threaten availability or cost.
- A service needs rate limits or request filtering before work reaches application dependencies.
- The user asks how to protect origins or global entry points.

## When Not To Use

- The issue is internal service retry/backpressure; use dependency resilience.
- The request is normal capacity growth without abusive traffic; use capacity/tail latency.
- The main topic is application authorization; use secure SDLC or identity.
- The work is internal service mesh/routing; use internal networking.

## Inputs To Collect

- Public endpoints, routes, origins, DNS/traffic steering, identity signals, and bypass paths.
- Traffic patterns, known attacks, request costs, tenant/customer priorities, and false-positive tolerance.
- Existing edge rules, rate limits, bot controls, challenges, allow/deny lists, and emergency controls.
- Origin capacity, dependency limits, caching behavior, and overload thresholds.
- Telemetry: rule ID, action, request ID, route, identity/tenant, status, latency, and origin result.
- Rule ownership, rollout mode, dry-run capability, expiry, review cadence, and rollback path.

## Workflow

1. **Map the edge.** Identify public entry points, origins, bypass paths, and expensive downstream operations.
2. **Separate attack layers.** Distinguish volumetric, protocol, application-layer, credential-stuffing, scraping, and tenant-abuse patterns.
3. **Protect origin.** Restrict direct access, require edge-origin authentication where possible, and remove bypass routes.
4. **Shape traffic early.** Apply rate limits, quotas, challenges, caching, prioritization, and load shedding before expensive work.
5. **Tune false positives.** Use dry-run or staged enforcement for new rules when possible; define review signals.
6. **Instrument decisions.** Log rule, action, identity, route, request ID, and origin outcome.
7. **Plan emergency controls.** Predefine who can apply broad blocks, how long they last, and how they are reviewed.
8. **Review and expire rules.** Temporary mitigations need owner, expiry, rollback, and post-event analysis.

## Synthesized Default

Use layered edge protection: origin isolation, traffic steering, caching where correct, rate limits, bot/abuse controls, DDoS response planning, edge telemetry, staged rule rollout, and reversible emergency mitigations.

## Exceptions

- During active denial-of-service events, temporary broad blocking may be acceptable if reviewed and expired quickly.
- Internal-only services can use lighter public-edge controls if no public route exists.
- High-value customers or critical traffic may need priority lanes or separate rate policies.
- Some rules cannot run in dry-run mode; compensate with narrow scope and fast rollback.

## Response Quality Bar

- Lead with the edge risk, denial-of-service or abuse policy, origin-bypass fix, or emergency mitigation requested.
- Cover origin isolation, route cost, identity-aware limits, bot/abuse controls, false-positive review, edge telemetry, staged enforcement, rollback, and expiry before optional edge breadth.
- Make recommendations actionable with owners, rule scopes, thresholds, dry-run/enforce stages, rollback commands, review windows, and emergency authority where relevant.
- State required evidence such as DNS/origin exposure, route inventory, request rates, tenant/user identity, rule logs, false-positive samples, origin saturation, and mitigation history; do not claim unseen evidence.
- Stay inside edge traffic and DDoS defense. Route broader capacity or abuse-product policy only when they materially block defense decisions.
- Be concise: avoid generic DDoS background and prefer compact edge maps, rule tables, and runbooks.

## Required Outputs

- Edge architecture and origin-protection map.
- Denial-of-service, abuse, and rate-limit policy.
- Origin bypass remediation plan.
- False-positive review and rollout plan.
- Edge telemetry and alert requirements.
- Emergency mitigation runbook.
- Rule ownership, expiry, and rollback plan.

## Evidence Gates

- `origin_check`: origins cannot be trivially bypassed from public networks.
- `rate_policy`: rate limits or abuse controls are tied to identity, route cost, and false-positive tolerance.
- `telemetry_check`: edge decisions include rule, action, route, identity/request context, and origin result.
- `rollback_check`: enforcement rules have owner, rollout mode, and rollback path.
- `emergency_check`: broad mitigations have authority, expiry, and review requirements.

## Red Flags - Stop And Rework

- Public clients can bypass edge controls and hit origin directly.
- Rate limits are global only and hurt good tenants before abusive traffic.
- Emergency block rules have no expiry.
- Edge logs cannot explain why a request was blocked.
- Rules are deployed broadly without owner or rollback.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| One giant block rule | Layer controls and scope them by route/identity/risk. |
| No origin isolation | Make bypass difficult or impossible. |
| Ignoring false positives | Use dry-run, staged enforcement, and review signals. |
| No edge telemetry | Log rule decisions and origin outcomes. |
