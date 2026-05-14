# OE Phase Map

Browse by phase, route by context, artifact, surface, risk, and next decision.

Use this as a navigation aid for scanning which specialist surfaces tend to appear in each OE phase; the [staff-engineer-mode](skills/staff-engineer-mode/SKILL.md) router still selects the right specialist file from the user's context, artifact, surface, risk, and evidence. Users do not need to name a phase or an existing codebase for a specialist to guide the next engineering decision.

## Foundations

This pack does not include a general "what is OE" skill. It starts with concrete Design & Build work, so use Foundations for orientation and routing rather than specialist selection.

- [staff-engineer-mode](skills/staff-engineer-mode/SKILL.md) — Routes broad or mixed engineering requests to the best specialist file before detailed guidance.
- [source-index](skills/_shared/references/source-index.md) — Shared citation inventory for the standards and engineering references synthesized by the pack.

## Design & Build

- [api-design-and-compatibility](specialists/api-design-and-compatibility.md) — Shapes exposed API contracts so clients, SDKs, and services can evolve safely.
- [architecture-decisions](specialists/architecture-decisions.md) — Reviews system boundaries, tradeoffs, ADRs, and decisions before implementation locks them in.
- [backup-and-recovery](specialists/backup-and-recovery.md) — Designs recoverability targets and restore evidence for stateful systems.
- [caching-and-derived-data](specialists/caching-and-derived-data.md) — Designs caches and materialized views with freshness, invalidation, stampede, and stale-state behavior.
- [cost-aware-reliability](specialists/cost-aware-reliability.md) — Frames reliability headroom, capacity cost, and unit economics as explicit engineering tradeoffs.
- [cryptography-and-key-lifecycle](specialists/cryptography-and-key-lifecycle.md) — Plans key, certificate, trust-root, and algorithm lifecycle before expiry becomes an outage.
- [data-contracts](specialists/data-contracts.md) — Defines shared schemas, datasets, events, files, or streams so producers and consumers can change independently.
- [data-pipeline-reliability](specialists/data-pipeline-reliability.md) — Designs critical batch or streaming pipelines around freshness, correctness, lineage, and replay.
- [dependency-resilience](specialists/dependency-resilience.md) — Sets timeout, retry, idempotency, queue, and overload behavior for remote calls and asynchronous work.
- [distributed-data-and-consistency](specialists/distributed-data-and-consistency.md) — Chooses data ownership, consistency, sharding, conflict, and failover semantics before code or schema lands.
- [edge-traffic-and-ddos-defense](specialists/edge-traffic-and-ddos-defense.md) — Designs public-edge protection, traffic shaping, origin isolation, and reversible abuse controls.
- [event-workflows](specialists/event-workflows.md) — Designs events, queues, streams, sagas, and workflows with idempotency, ordering, DLQ, retry, and replay.
- [high-availability-design](specialists/high-availability-design.md) — Validates fault domains, static capacity, blast radius, and failover claims.
- [identity-and-secrets](specialists/identity-and-secrets.md) — Designs human and workload access, credential lifetime, secret storage, break-glass, and audit.
- [infrastructure-and-policy-as-code](specialists/infrastructure-and-policy-as-code.md) — Makes infrastructure declarative with policy checks, drift handling, promotion, and emergency paths.
- [internal-service-networking](specialists/internal-service-networking.md) — Designs internal service traffic, discovery, routing, workload identity, encrypted transport, and per-hop failure behavior.
- [llm-application-security](specialists/llm-application-security.md) — Hardens model-backed features where prompts, retrieval, tools, output, or generated actions cross boundaries.
- [llm-serving-cost-and-latency](specialists/llm-serving-cost-and-latency.md) — Sets model-backed route budgets for tokens, latency, caching, fallback, and spend attribution.
- [performance-and-capacity](specialists/performance-and-capacity.md) — Models traffic, tail latency, saturation, headroom, and load-test evidence for peak or failover.
- [platform-golden-paths](specialists/platform-golden-paths.md) — Designs reusable platform paths, templates, scorecards, and safe defaults across projects.
- [privacy-and-data-lifecycle](specialists/privacy-and-data-lifecycle.md) — Engineers data minimization, classification, retention, deletion, export, and privacy-safe telemetry.
- [secure-sdlc-and-threat-modeling](specialists/secure-sdlc-and-threat-modeling.md) — Turns trust boundaries, abuse cases, controls, and residual risks into testable secure-design evidence.
- [slo-and-error-budgets](specialists/slo-and-error-budgets.md) — Defines user-journey SLIs, SLOs, error budgets, burn alerts, and budget-based release policy.
- [software-supply-chain-security](specialists/software-supply-chain-security.md) — Hardens source, build, provenance, signing, dependency inventory, and deployment admission.
- [state-machine-correctness](specialists/state-machine-correctness.md) — Validates high-risk protocols, workflows, or concurrency boundaries with invariants and stronger-than-example tests.
- [tenant-isolation](specialists/tenant-isolation.md) — Designs tenant context, partitioning, quotas, telemetry, and cross-tenant protection for shared systems.

## Develop & Test

- [accessibility-gates](specialists/accessibility-gates.md) — Combines automated and manual evidence for keyboard, focus, contrast, semantic, and assistive-technology release checks.
- [agent-pr-review](specialists/agent-pr-review.md) — Applies a senior pre-merge risk review to a specific diff or PR.
- [ai-coding-governance](specialists/ai-coding-governance.md) — Sets repo rules for coding agents, protected paths, data boundaries, verification evidence, and auditability.
- [code-readability-for-agents](specialists/code-readability-for-agents.md) — Audits module boundaries, naming, file size, and searchability so agents can find canonical code safely.
- [data-contracts](specialists/data-contracts.md) — Adds compatibility and contract-test discipline to shared producer-consumer data surfaces.
- [data-pipeline-reliability](specialists/data-pipeline-reliability.md) — Sets validation gates and replay checks before critical data is published to consumers.
- [dependency-and-code-hygiene](specialists/dependency-and-code-hygiene.md) — Plans dependency updates, lockfile changes, static-analysis ratchets, codemods, and dead-code cleanup in reversible batches.
- [dev-environment-parity](specialists/dev-environment-parity.md) — Builds parity checks across local, CI, staging, and production-like environments so test results mean what they claim.
- [llm-application-security](specialists/llm-application-security.md) — Adds adversarial checks for prompt injection, tool misuse, output handling, and sensitive data leakage.
- [llm-evaluation](specialists/llm-evaluation.md) — Builds eval harnesses with representative cases, graders, thresholds, slices, and regression history.
- [ml-reliability-and-evaluation](specialists/ml-reliability-and-evaluation.md) — Gates model changes on data validation, eval thresholds, training-serving skew, serving checks, and rollback evidence.
- [performance-and-capacity](specialists/performance-and-capacity.md) — Plans load, stress, spike, soak, and regression tests using tail percentiles and saturation signals.
- [release-build-reproducibility](specialists/release-build-reproducibility.md) — Makes builds reproducible with pinned inputs, hermeticity checks, stable cache rules, and artifact identity.
- [resilience-experiments](specialists/resilience-experiments.md) — Designs chaos, failover, fault-injection, and game-day tests with hypothesis, blast radius, abort criteria, and learning loop.
- [secure-sdlc-and-threat-modeling](specialists/secure-sdlc-and-threat-modeling.md) — Converts threat-model controls into verification gates before sensitive implementation proceeds.
- [software-supply-chain-security](specialists/software-supply-chain-security.md) — Adds build-path integrity, dependency inventory, secret scanning, provenance, and deploy-trust checks.
- [state-machine-correctness](specialists/state-machine-correctness.md) — Uses property tests, fuzzing, simulation, or model checking when example tests cannot cover dangerous interleavings.
- [tenant-isolation](specialists/tenant-isolation.md) — Adds cross-tenant tests and telemetry safeguards for multi-tenant code paths.
- [test-data-engineering](specialists/test-data-engineering.md) — Governs fixtures, golden files, snapshots, anonymization, regeneration, and drift from production shape.
- [testing-and-quality-gates](specialists/testing-and-quality-gates.md) — Designs merge and release checks, CI budgets, flake policy, static analysis, and quality ratchets.
- [web-release-gates](specialists/web-release-gates.md) — Gates browser releases on loading, interaction readiness, visual stability, runtime errors, journey budgets, and smoke checks.

## Deploy & Operate

- [accessibility-gates](specialists/accessibility-gates.md) — Blocks user-facing releases when critical accessibility evidence is missing or regresses.
- [backup-and-recovery](specialists/backup-and-recovery.md) — Proves restore paths, recovery objectives, and disaster scenarios before relying on them.
- [caching-and-derived-data](specialists/caching-and-derived-data.md) — Operates cache and derived-view changes with explicit freshness, failure, and repair behavior.
- [configuration-and-automation-safety](specialists/configuration-and-automation-safety.md) — Adds validation, preview, blast-radius limits, confirmation, and recovery to config and automation changes.
- [cryptography-and-key-lifecycle](specialists/cryptography-and-key-lifecycle.md) — Runs rotations, renewals, replacements, and algorithm transitions with inventory and rollback evidence.
- [data-pipeline-reliability](specialists/data-pipeline-reliability.md) — Operates pipelines with freshness alerts, validation gates, backfill, replay, and consumer notification.
- [database-operations](specialists/database-operations.md) — Runs schema changes, backfills, index builds, destructive queries, and maintenance with lock, lag, throttle, abort, and verification controls.
- [dev-environment-parity](specialists/dev-environment-parity.md) — Keeps environment drift from invalidating promotion, staging, preview, and production evidence.
- [edge-traffic-and-ddos-defense](specialists/edge-traffic-and-ddos-defense.md) — Operates rate rules, traffic filters, abuse controls, edge telemetry, emergency mitigations, and rollback.
- [event-workflows](specialists/event-workflows.md) — Operates asynchronous flows with queue limits, DLQs, poison handling, replay, correction, and lag visibility.
- [fleet-upgrades](specialists/fleet-upgrades.md) — Rolls out runtime, platform, framework, client, or host upgrades across mixed-version fleets.
- [identity-and-secrets](specialists/identity-and-secrets.md) — Grants, rotates, revokes, audits, and reviews production access and secret usage.
- [infrastructure-and-policy-as-code](specialists/infrastructure-and-policy-as-code.md) — Promotes infrastructure changes through desired state, policy gates, drift detection, reconciliation, and emergency controls.
- [internal-service-networking](specialists/internal-service-networking.md) — Operates service routing, identity, encrypted transport, policy rollout, diagnostics, and internal traffic upgrades.
- [llm-serving-cost-and-latency](specialists/llm-serving-cost-and-latency.md) — Operates model-backed routes with token caps, tail-latency budgets, fallback behavior, cache rules, and cost attribution.
- [migration-and-deprecation](specialists/migration-and-deprecation.md) — Executes broad migrations, service retirements, API sunsets, no-new-usage controls, and disable-before-delete plans.
- [ml-reliability-and-evaluation](specialists/ml-reliability-and-evaluation.md) — Promotes and rolls back model artifacts with serving checks, data validation, drift signals, and rollout gates.
- [mobile-release-engineering](specialists/mobile-release-engineering.md) — Manages native mobile releases with staged rollout, stability budgets, segmentation, kill switches, and forward-fix paths.
- [privacy-and-data-lifecycle](specialists/privacy-and-data-lifecycle.md) — Operates retention, deletion propagation, export, erasure, telemetry controls, and audit paths for sensitive data.
- [production-readiness-review](specialists/production-readiness-review.md) — Aggregates launch evidence, blockers, exceptions, tier classification, and specialist follow-up routes before production exposure.
- [progressive-delivery](specialists/progressive-delivery.md) — Plans staged exposure, canary metrics, stop criteria, rollback, forward-fix, compatibility, and cleanup for production changes.
- [release-build-reproducibility](specialists/release-build-reproducibility.md) — Promotes one identifiable artifact through environments with release gates and traceable rollback targets.
- [software-supply-chain-security](specialists/software-supply-chain-security.md) — Operates source-to-deploy controls for artifact integrity, dependency evidence, builder trust, and admission.
- [tenant-isolation](specialists/tenant-isolation.md) — Enforces tenant-aware quotas, data access, logs, metrics, traces, exports, and operational workflows.
- [vulnerability-management](specialists/vulnerability-management.md) — Triages deployed vulnerabilities, sets patch urgency, rolls out fixes, verifies remediation, and tracks exceptions.
- [web-release-gates](specialists/web-release-gates.md) — Operates browser release gates around field-user experience, errors, performance budgets, deploy markers, and safe exposure.

## Monitor & Respond

- [backup-and-recovery](specialists/backup-and-recovery.md) — Supports response when data loss, corruption, destructive changes, or restore proof becomes the critical path.
- [cost-aware-reliability](specialists/cost-aware-reliability.md) — Investigates cost spikes as possible reliability, abuse, capacity, or regression signals without silently consuming headroom.
- [data-pipeline-reliability](specialists/data-pipeline-reliability.md) — Alerts on stale, missing, duplicated, or incorrect data and provides replay or backfill response paths.
- [documentation-lifecycle](specialists/documentation-lifecycle.md) — Keeps runbooks and operational references findable, current, authoritative, and tied to change triggers.
- [edge-traffic-and-ddos-defense](specialists/edge-traffic-and-ddos-defense.md) — Responds to abusive public traffic with scoped rules, telemetry, false-positive checks, expiry, and rollback.
- [experimentation-and-metric-guardrails](specialists/experimentation-and-metric-guardrails.md) — Reads out experiments and ramps using exposure logs, guardrails, validity checks, and predeclared decision rules.
- [incident-response-and-postmortems](specialists/incident-response-and-postmortems.md) — Runs active incidents, status cadence, timelines, postmortems, and verified action items.
- [llm-serving-cost-and-latency](specialists/llm-serving-cost-and-latency.md) — Monitors model-backed latency, fallback, cache hit rate, retry amplification, and spend anomalies.
- [ml-reliability-and-evaluation](specialists/ml-reliability-and-evaluation.md) — Monitors model quality, drift, serving latency, freshness, saturation, and rollback triggers.
- [mobile-release-engineering](specialists/mobile-release-engineering.md) — Tracks crash-free rates, hangs, startup, cohorts, and rollout halt or forward-fix criteria.
- [observability-and-alerting](specialists/observability-and-alerting.md) — Designs telemetry, dashboards, alerts, structured events, trace context, and runbooks tied to user journeys.
- [oncall-health](specialists/oncall-health.md) — Reduces noisy pages, repeated manual work, stale runbooks, and unactionable operational load.
- [performance-and-capacity](specialists/performance-and-capacity.md) — Investigates tail-latency regressions, saturation, queueing, hot paths, and capacity limits.
- [slo-and-error-budgets](specialists/slo-and-error-budgets.md) — Connects user-visible reliability objectives to burn alerts and budget-state response.
- [vulnerability-management](specialists/vulnerability-management.md) — Responds to vulnerable deployed artifacts with risk-based patching, rollout, verification, and expiring exceptions.
- [web-release-gates](specialists/web-release-gates.md) — Watches field-user browser metrics, runtime errors, visual stability, interaction readiness, and release markers.

## Improve

- [accessibility-gates](specialists/accessibility-gates.md) — Raises accessibility from ad hoc checks to repeatable conformance and regression gates for critical journeys.
- [ai-coding-governance](specialists/ai-coding-governance.md) — Improves agent-assisted development with repo-local boundaries, verification rules, and reviewable audit trails.
- [code-readability-for-agents](specialists/code-readability-for-agents.md) — Reduces wrong-file edits and duplicated helpers by improving codebase legibility for humans and agents.
- [cost-aware-reliability](specialists/cost-aware-reliability.md) — Improves reliability economics by preserving explicit SLO, capacity, and recovery targets while reducing waste.
- [dependency-and-code-hygiene](specialists/dependency-and-code-hygiene.md) — Turns dependency freshness, static findings, codemods, and dead-code removal into routine reversible maintenance.
- [dev-environment-parity](specialists/dev-environment-parity.md) — Reduces recurring environment drift with parity contracts, drift budgets, and action triggers.
- [documentation-lifecycle](specialists/documentation-lifecycle.md) — Improves engineering docs through source-of-truth rules, freshness signals, review triggers, and stale-doc cleanup.
- [engineering-control-evidence](specialists/engineering-control-evidence.md) — Builds cross-surface evidence packs, scorecards, and exception registers from normal engineering artifacts.
- [experimentation-and-metric-guardrails](specialists/experimentation-and-metric-guardrails.md) — Converts experiment and ramp results into trustworthy decisions with guardrails and metric-validity checks.
- [feature-flag-lifecycle](specialists/feature-flag-lifecycle.md) — Audits live flags, finds orphans, sets expiry, plans safe removal, and scores flag debt after rollout.
- [fleet-upgrades](specialists/fleet-upgrades.md) — Retires unsupported versions, closes skew windows, updates operations, and removes old fleet paths.
- [llm-evaluation](specialists/llm-evaluation.md) — Keeps model-backed quality gates current with regression history, promoted incidents, slices, thresholds, and failure triage.
- [migration-and-deprecation](specialists/migration-and-deprecation.md) — Drives large retirements and replacements with usage telemetry, migration batches, backsliding controls, and final cleanup.
- [oncall-health](specialists/oncall-health.md) — Converts recurring pages and manual operations into measured engineering backlog and toil reduction.
- [performance-and-capacity](specialists/performance-and-capacity.md) — Improves latency, saturation, headroom, overload behavior, and cost-capacity tradeoffs from evidence.
- [platform-golden-paths](specialists/platform-golden-paths.md) — Bakes recurring reliability, security, deployment, telemetry, and operations defaults into reusable developer paths.
- [privacy-and-data-lifecycle](specialists/privacy-and-data-lifecycle.md) — Improves data lifecycle control through minimization, deletion verification, copy control, and regression gates.
- [production-readiness-review](specialists/production-readiness-review.md) — Feeds launch-readiness gaps, exceptions, and evidence findings back into standards and specialist follow-ups.
- [release-build-reproducibility](specialists/release-build-reproducibility.md) — Improves release confidence by removing local-machine, cache, unpinned-input, and artifact-traceability gaps.
- [resilience-experiments](specialists/resilience-experiments.md) — Turns failover drills and fault-injection results into verified resilience fixes.
- [slo-and-error-budgets](specialists/slo-and-error-budgets.md) — Uses budget policy to guide release risk, alert tuning, and reliability improvement work.
- [software-supply-chain-security](specialists/software-supply-chain-security.md) — Strengthens source-to-deploy trust through provenance, dependency evidence, isolated builds, and least-privilege automation.
- [test-data-engineering](specialists/test-data-engineering.md) — Improves fixture reliability, anonymization, regeneration, and production-shape drift detection.
- [testing-and-quality-gates](specialists/testing-and-quality-gates.md) — Improves test strategy with faster high-signal checks, legacy ratchets, flake policy, and release-gate discipline.
- [vulnerability-management](specialists/vulnerability-management.md) — Improves security posture through remediation SLAs, exception expiry, verification evidence, and recurring-risk reduction.
- [web-release-gates](specialists/web-release-gates.md) — Improves browser release quality by turning field-user regressions into journey budgets and release gates.

Citations and source notes live in the shared [source-index](skills/_shared/references/source-index.md).
