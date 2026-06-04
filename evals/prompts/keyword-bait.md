# Router Boundary Prompts: Keyword Bait

Tests prompts that name the target specialist or label while the requested artifact belongs elsewhere.

Prompts are grouped by the specialist that must not fire. The suffix gives the correct route.

## Architecture And Interfaces

### `api-design-and-compatibility`

- "The notes say api-design-and-compatibility, but the work is replay ordering and dead-letter recovery for event consumers." (-> `event-workflows`)
- "The Jira component is api-design-and-compatibility, but the artifact is a build-once promotion record with package identity, version pins, and rollback target." (-> `release-build-reproducibility`)
- "The README section is named api-design-and-compatibility, but the task is to define owner, expiry, fallback behavior, and removal criteria for a stale runtime flag." (-> `feature-flag-lifecycle`)
- "The branch name includes api-design-and-compatibility, but the review is about service account scope, secret rotation, and emergency access cleanup." (-> `identity-and-secrets`)
- "The comment tag says api-design-and-compatibility, but the requested check is whether local, CI, staging, and production configs drift in ways that hide bugs." (-> `dev-environment-parity`)

### `architecture-decisions`

- "The doc title includes architecture-decisions, but the task is to rename confusing modules so agents find the canonical code path." (-> `code-readability-for-agents`)
- "The ticket name starts with architecture-decisions, but the requested artifact is a public endpoint compatibility review for SDK and partner clients." (-> `api-design-and-compatibility`)
- "The folder is called architecture-decisions, but the problem is unsafe automation mutating production state without preview, validation, caps, or rollback." (-> `configuration-and-automation-safety`)
- "The design note header says architecture-decisions, but the work is SLI selection, SLO target setting, burn alerts, and budget policy." (-> `slo-and-error-budgets`)
- "The meeting agenda says architecture-decisions, but the task is incident timeline, severity, owner updates, and follow-up quality." (-> `incident-response-and-postmortems`)

### `data-contracts`

- "The fixture catalog is labeled data-contracts and mentions schema drift, but the work is to refresh production-derived contract-test snapshots with anonymization, restore steps, and freshness-versus-determinism rules." (-> `test-data-engineering`)
- "The spreadsheet tab is data-contracts, but the request is lineage, freshness SLIs, validation, replay, and late-arriving metric handling for a pipeline." (-> `data-pipeline-reliability`)
- "The doc title says data-contracts, but the concrete issue is replicated reads, stale data after failover, and cross-store consistency assumptions." (-> `distributed-data-and-consistency`)
- "The PR label says data-contracts, but the work is package provenance, signature verification, and deploy admission trust." (-> `software-supply-chain-security`)
- "The comment says data-contracts, but the task is route-specific LLM grader slices, thresholds, prompt versions, and regression history." (-> `llm-evaluation`)

### `resilience-requirements`

- "The feature brief is labeled resilience-requirements, but the requested artifact is an ADR choosing service boundaries, call direction, and ownership tradeoffs." (-> `architecture-decisions`)
- "The acceptance-criteria section says resilience-requirements, but the work is SLO target math, burn-rate alerts, and budget response policy." (-> `slo-and-error-budgets`)
- "The backlog item says resilience-requirements, but the task is trust-boundary mapping, abuse cases, and control selection for a new endpoint." (-> `secure-sdlc-and-threat-modeling`)
- "The spec tag says resilience-requirements, but the concrete ask is merge-blocking checks, flaky-test quarantine, release gates, and nightly coverage." (-> `testing-and-quality-gates`)
- "The roadmap note says resilience-requirements, but the request is market prioritization and feature value ranking with no engineering failure behavior." (-> `none`)

### `persistent-connection-systems`

- "The ticket title says persistent-connection-systems, but the work is message ordering, idempotent consumers, dead-letter replay, and compensation." (-> `event-workflows`)
- "The design note says persistent-connection-systems, but the concrete ask is retry, timeout, fallback, idempotency, and overload behavior for one request-reply dependency." (-> `dependency-resilience`)
- "The capacity doc is labeled persistent-connection-systems, but the task is load-test saturation, headroom, queue depth, and autoscaling targets for an API." (-> `performance-and-capacity`)
- "The route map says persistent-connection-systems, but the work is internal service discovery, identity, locality, and private traffic policy." (-> `internal-service-networking`)
- "The rollout card says persistent-connection-systems, but the ask is canary stages, stop metrics, rollback target, and production exposure sequencing." (-> `progressive-delivery`)

## Reliability And Resilience

### `slo-and-error-budgets`

- "The planning doc says slo-and-error-budgets, but the decision is whether to reduce reserved capacity spend while preserving availability and current error-budget commitments." (-> `cost-aware-reliability`)
- "The dashboard folder is slo-and-error-budgets, but the request is to add logs, traces, correlation IDs, dashboards, alerts, and runbook links for a new flow." (-> `observability-and-alerting`)
- "The ticket tag says slo-and-error-budgets, but the artifact is a load-test plan with saturation points, queue depth limits, and capacity headroom." (-> `performance-and-capacity`)
- "The doc name includes slo-and-error-budgets, but the work is on-call page noise triage, suppression safety, and engineering fixes for recurring alerts." (-> `oncall-health`)
- "The label says slo-and-error-budgets, but the task is a launch go/no-go packet across code, deploy config, telemetry, runbooks, and support readiness." (-> `production-readiness-review`)

### `high-availability-design`

- "The doc heading says high-availability-design, but the work is corruption restore testing with RTO and RPO evidence." (-> `backup-and-recovery`)
- "The topology diagram is named high-availability-design, but the ask is timeout, retry, circuit-breaker, duplicate-work, and overload behavior for one downstream call." (-> `dependency-resilience`)
- "The runbook file says high-availability-design, but the concrete task is a safe fault-injection drill with blast radius, abort criteria, telemetry, and rollback." (-> `resilience-experiments`)
- "The release card says high-availability-design, but the issue is runtime fleet version skew, support windows, temporary exceptions, and rollback compatibility." (-> `fleet-upgrades`)
- "The architecture note says high-availability-design, but the task is private service discovery, identity, locality, and internal routing policy." (-> `internal-service-networking`)

### `multi-region-and-data-residency`

- "The regional plan says multi-region-and-data-residency, but the work is static failover capacity, fault-domain placement, and location-loss survivability." (-> `high-availability-design`)
- "The DR checklist says multi-region-and-data-residency, but the task is restore testing, corruption recovery, RTO, RPO, and rebuild evidence." (-> `backup-and-recovery`)
- "The replication note says multi-region-and-data-residency, but the concrete issue is stale reads, conflicts, and consistency semantics for one store." (-> `distributed-data-and-consistency`)
- "The routing diagram says multi-region-and-data-residency, but the ask is internal service discovery, identity, locality, and private east-west traffic policy." (-> `internal-service-networking`)
- "The residency spreadsheet says multi-region-and-data-residency, but the task is retention, deletion, minimization, and lifecycle controls for personal data." (-> `privacy-and-data-lifecycle`)

### `dependency-resilience`

- "The design doc says dependency-resilience, but the decision is ownership boundaries between service, worker, and module." (-> `architecture-decisions`)
- "The label says dependency-resilience, but the concrete ask is package upgrade hygiene, deprecated helper cleanup, lockfile risk, and codemod safety." (-> `dependency-and-code-hygiene`)
- "The runbook heading says dependency-resilience, but the work is restoring a tenant snapshot after accidental deletion and reconciling writes made during recovery." (-> `backup-and-recovery`)
- "The comment prefix is dependency-resilience, but the issue is SLO burn policy and separating urgent paging from follow-up work." (-> `slo-and-error-budgets`)
- "The ticket title says dependency-resilience, but the requested artifact is message idempotency, ordering guarantees, DLQ replay, and compensation logic." (-> `event-workflows`)

### `performance-and-capacity`

- "The graph says performance-and-capacity, but query-plan changes after schema migration caused the latency spike." (-> `database-operations`)
- "The dashboard name says performance-and-capacity, but the blocker is browser bundle growth, interaction latency, layout shifts, and client runtime errors." (-> `web-release-gates`)
- "The issue tag says performance-and-capacity, but the concrete hosted-model route task is per-route token budgets, p99 latency budgets, cache policy, and degraded provider fallback." (-> `llm-serving-cost-and-latency`)
- "The profile file says performance-and-capacity, but the real question is whether stale derived data invalidation can corrupt cached reads." (-> `caching-and-derived-data`)
- "The planning note says performance-and-capacity, but the work is reserved-capacity spend versus availability commitments and reliability tradeoffs." (-> `cost-aware-reliability`)

### `backup-and-recovery`

- "The DR doc says backup-and-recovery, but the task is to prove a zone can fail without data restore by checking fault-domain topology, preallocated failover capacity, and location-loss survivability." (-> `high-availability-design`)
- "The filename says backup-and-recovery, but the request is backup job telemetry, failed-run alerts, dashboard context, and runbook links." (-> `observability-and-alerting`)
- "The plan title says backup-and-recovery, but the task is online schema backfill safety with query-plan checks, lock limits, throttling, and abort criteria." (-> `database-operations`)
- "The ticket label says backup-and-recovery, but the concrete issue is tenant data minimization, retention, deletion, and lifecycle enforcement." (-> `privacy-and-data-lifecycle`)
- "The checklist section says backup-and-recovery, but the work is production readiness across code, deploy config, dashboards, runbooks, and launch blockers." (-> `production-readiness-review`)

### `resilience-experiments`

- "The test plan calls this resilience-experiments, but the task is a traffic replay/load test to find saturation points, queue depth limits, and capacity headroom; no fault injection or failover drill." (-> `performance-and-capacity`)
- "The experiment calendar says resilience-experiments, but the current ask is SLO burn alert thresholds and deciding which failures page immediately." (-> `slo-and-error-budgets`)
- "The doc comment says resilience-experiments, but the artifact is a recoverability test for corrupted records with RTO and RPO evidence." (-> `backup-and-recovery`)
- "The label says resilience-experiments, but the work is canary stop criteria, rollback target, signal minimums, and staged exposure for a new path." (-> `progressive-delivery`)
- "The test file says resilience-experiments, but the issue is state transitions, impossible states, retry races, and property-test coverage." (-> `state-machine-correctness`)

### `state-machine-correctness`

- "The design note says state-machine-correctness, but the issue is consistency across databases, replication lag, and failover." (-> `distributed-data-and-consistency`)
- "The ticket label is state-machine-correctness, but the requested plan is event ordering, idempotent consumers, compensating actions, and DLQ replay." (-> `event-workflows`)
- "The diagram says state-machine-correctness, but the work is public API status-field compatibility for generated clients during rollout." (-> `api-design-and-compatibility`)
- "The comment says state-machine-correctness, but the task is to inspect locking, permissions, secret scopes, and credential traceability." (-> `identity-and-secrets`)
- "The test name includes state-machine-correctness, but the request is to decide merge-blocking, release-blocking, and nightly quality gates for a checkout change." (-> `testing-and-quality-gates`)

## Delivery And Quality

### `testing-and-quality-gates`

- "The test plan says testing-and-quality-gates, but the task is fixture anonymization, freshness, and determinism." (-> `test-data-engineering`)
- "The CI job is named testing-and-quality-gates, but the artifact is release package identity, version consistency, promotion path, and rollback target." (-> `release-build-reproducibility`)
- "The ticket label says testing-and-quality-gates, but the concrete work is browser accessibility checks for focus order, labels, contrast, and keyboard traps." (-> `accessibility-gates`)
- "The checklist header says testing-and-quality-gates, but the request is LLM evaluation dataset slices, grader thresholds, prompt versions, and regression trend evidence." (-> `llm-evaluation`)
- "The branch name says testing-and-quality-gates, but the work is static-analysis backlog triage, deprecated dependency cleanup, and lockfile rollback notes." (-> `dependency-and-code-hygiene`)

### `test-data-engineering`

- "The eval dataset is labeled test-data-engineering, but the work is prompt-versioned LLM grader datasets, thresholds, slice coverage, and regression history." (-> `llm-evaluation`)
- "The fixture folder says test-data-engineering, but the task is producer and consumer compatibility rules for a shared reporting schema field." (-> `data-contracts`)
- "The test file name says test-data-engineering, but the work is deciding what blocks merge, what blocks release, and what can run later." (-> `testing-and-quality-gates`)
- "The doc title says test-data-engineering, but the concrete request is data retention, deletion, minimization, and privacy lifecycle controls for support exports." (-> `privacy-and-data-lifecycle`)
- "The Jira label says test-data-engineering, but the ask is to replay metric table inputs, validate lineage, and detect late or missing pipeline batches." (-> `data-pipeline-reliability`)

### `configuration-and-automation-safety`

- "The request mentions configuration-and-automation-safety, but the real work is orphan feature-flag inventory, expiry, fallback, and removal." (-> `feature-flag-lifecycle`)
- "The script comment says configuration-and-automation-safety, but the task is declarative infrastructure policy checks, drift detection, and emergency reconciliation." (-> `infrastructure-and-policy-as-code`)
- "The ticket tag says configuration-and-automation-safety, but the work is access scope, service-account credentials, secret lifetime, and break-glass traceability." (-> `identity-and-secrets`)
- "The config file path says configuration-and-automation-safety, but the concrete issue is environment drift between local, CI, staging, and production." (-> `dev-environment-parity`)
- "The dashboard note says configuration-and-automation-safety, but the request is a static-analysis warning ratchet and dead-code cleanup plan." (-> `dependency-and-code-hygiene`)

### `release-build-reproducibility`

- "The release checklist says release-build-reproducibility, but the issue is local, CI, staging, and production drift." (-> `dev-environment-parity`)
- "The artifact manifest says release-build-reproducibility, but the work is software provenance, signature verification, SBOM gaps, and deploy admission trust." (-> `software-supply-chain-security`)
- "The release note says release-build-reproducibility, but the task is staged exposure, canary signals, pause thresholds, and rollback for a ranking path." (-> `progressive-delivery`)
- "The build log label says release-build-reproducibility, but the concrete request is a mobile app rollout with store tracks, phased rollout, crash thresholds, and rollback options." (-> `mobile-release-engineering`)
- "The checklist says release-build-reproducibility, but the issue is stale runbook ownership, source of truth, freshness triggers, and archive rules." (-> `documentation-lifecycle`)

### `dev-environment-parity`

- "The checklist says dev-environment-parity, but the issue is builder provenance, signing, and deployment admission trust." (-> `software-supply-chain-security`)
- "The parity matrix row says dev-environment-parity, but the work is build-once artifact identity, version pinning, promotion records, and rollback package selection." (-> `release-build-reproducibility`)
- "The ticket title says dev-environment-parity, but the concrete issue is test fixture drift, anonymization, regeneration, and determinism." (-> `test-data-engineering`)
- "The README section says dev-environment-parity, but the ask is to copy-edit install wording and markdown tables only." (-> `none`)
- "The label says dev-environment-parity, but the task is new-service production readiness across deployment, telemetry, runbooks, and support paths." (-> `production-readiness-review`)

### `progressive-delivery`

- "The plan says progressive-delivery, but the request is a broad go/no-go readiness decision for launch." (-> `production-readiness-review`)
- "The canary card says progressive-delivery, but the work is owner, expiry, fallback, stale-flag inventory, and eventual flag removal." (-> `feature-flag-lifecycle`)
- "The rollout doc says progressive-delivery, but the issue is mobile store rollout tracks, crash guardrails, app version support, and rollback constraints." (-> `mobile-release-engineering`)
- "The ticket says progressive-delivery, but the request is one PR diff review for intent match, missing edge cases, and hallucinated APIs." (-> `agent-pr-review`)
- "The dashboard title says progressive-delivery, but the concrete ask is an experiment guardrail review with treatment assignment, metric validity, and stop rules." (-> `experimentation-and-metric-guardrails`)

### `feature-flag-lifecycle`

- "The label says feature-flag-lifecycle, but the request is unsafe runtime config validation, generated preview, blast-radius cap, and rollback." (-> `configuration-and-automation-safety`)
- "The flag description includes feature-flag-lifecycle, but the work is staged exposure with canary metrics, minimum signal, pause criteria, and rollback target." (-> `progressive-delivery`)
- "The ticket name says feature-flag-lifecycle, but the artifact is a public API client compatibility plan for changing a response field." (-> `api-design-and-compatibility`)
- "The cleanup note says feature-flag-lifecycle, but the request is dead-code and dependency hygiene triage after a flag was removed." (-> `dependency-and-code-hygiene`)
- "The PR label says feature-flag-lifecycle, but the concrete issue is production readiness for launch evidence, support docs, telemetry, and deployment blockers." (-> `production-readiness-review`)

### `production-readiness-review`

- "The packet says production-readiness-review, but the request is release artifact identity, package versioning, and promotion evidence." (-> `release-build-reproducibility`)
- "The launch checklist says production-readiness-review, but the work is SLO definitions, burn-rate paging, and budget response policy." (-> `slo-and-error-budgets`)
- "The go-live doc says production-readiness-review, but the issue is public endpoint resource shape, error semantics, idempotency, and client compatibility." (-> `api-design-and-compatibility`)
- "The readiness folder says production-readiness-review, but the task is runbook ownership, freshness cadence, source of truth, and stale doc cleanup." (-> `documentation-lifecycle`)
- "The meeting notes say production-readiness-review, but the request is mobile phased rollout guardrails, store package identity, and crash thresholds." (-> `mobile-release-engineering`)

### `migration-and-deprecation`

- "The migration plan title says migration-and-deprecation, but the work is a runtime fleet upgrade with mixed-version windows, support policy, temporary exceptions, and rollback compatibility." (-> `fleet-upgrades`)
- "The deprecation card says migration-and-deprecation, but the work is public API sunset communication, compatible response behavior, client rollout, and generated SDK changes." (-> `api-design-and-compatibility`)
- "The folder says migration-and-deprecation, but the concrete task is dependency cleanup, lockfile migration, codemod safety, and rollback risk." (-> `dependency-and-code-hygiene`)
- "The ticket label says migration-and-deprecation, but the ask is to review the current diff for behavior regressions and missing tests before merge." (-> `agent-pr-review`)
- "The doc title says migration-and-deprecation, but the work is stale runbook archival, source-of-truth selection, owner assignment, and freshness rules." (-> `documentation-lifecycle`)

### `service-decommission-and-sunset`

- "The retirement board says service-decommission-and-sunset, but the work is still consumer migration, replacement adoption, no-new-usage checks, and backsliding prevention." (-> `migration-and-deprecation`)
- "The delete ticket says service-decommission-and-sunset, but the requested artifact is a previewed runtime mutation with validation, blast-radius cap, and rollback." (-> `configuration-and-automation-safety`)
- "The teardown folder says service-decommission-and-sunset, but the task is desired-state deletion policy, drift detection, reconciliation, and exception expiry." (-> `infrastructure-and-policy-as-code`)
- "The certificate cleanup note says service-decommission-and-sunset, but the work is key and certificate revocation lifecycle, expiry, trust-chain rotation, and evidence." (-> `cryptography-and-key-lifecycle`)
- "The database section says service-decommission-and-sunset, but the concrete issue is destructive schema-change execution, lock limits, query plans, and rollback." (-> `database-operations`)

### `fleet-upgrades`

- "The plan says fleet-upgrades, but the concrete issue is backwards-compatible public API field behavior during client rollout." (-> `api-design-and-compatibility`)
- "The runtime inventory says fleet-upgrades, but the task is package provenance, trusted builders, signatures, and deployment admission checks." (-> `software-supply-chain-security`)
- "The upgrade ticket says fleet-upgrades, but the work is environment drift across local, CI, staging, and production that hides runtime bugs." (-> `dev-environment-parity`)
- "The rollout doc says fleet-upgrades, but the ask is canary metrics, pause thresholds, rollback target, and staged exposure." (-> `progressive-delivery`)
- "The checklist label says fleet-upgrades, but the concrete issue is retiring a legacy API family with replacement, consumer inventory, no-new-usage blocks, and decommission evidence." (-> `migration-and-deprecation`)

### `agent-pr-review`

- "The ticket label is agent-pr-review and changed files are attached, but the task is to prioritize a static-analysis warning ratchet and dead-code cleanup backlog, not review a mergeable diff." (-> `dependency-and-code-hygiene`)
- "The PR title says agent-pr-review, but the requested artifact is an ADR comparing service boundaries and ownership tradeoffs." (-> `architecture-decisions`)
- "The comment mentions agent-pr-review, but the ask is to define route-specific test gates, release blockers, and nightly coverage for a feature." (-> `testing-and-quality-gates`)
- "The branch label says agent-pr-review, but the real work is module naming, canonical path discovery, and reducing code-search ambiguity for agents." (-> `code-readability-for-agents`)
- "The review queue says agent-pr-review, but the ticket is a production incident timeline with severity, roles, updates, and follow-up owners." (-> `incident-response-and-postmortems`)

### `code-readability-for-agents`

- "The prompt names code-readability-for-agents, but the artifact is a public API resource shape and generated-client compatibility plan." (-> `api-design-and-compatibility`)
- "The file comment says code-readability-for-agents, but the task is broader service-boundary ownership and ADR tradeoffs." (-> `architecture-decisions`)
- "The issue label says code-readability-for-agents, but the work is deprecated dependency removal, dead-code cleanup, static-analysis warnings, and lockfile safety." (-> `dependency-and-code-hygiene`)
- "The README title says code-readability-for-agents, but the request is copy-editing section wording and link labels only." (-> `none`)
- "The ticket name says code-readability-for-agents, but the concrete issue is agent-generated code governance, allowed use, review controls, and traceability." (-> `ai-coding-governance`)

### `documentation-lifecycle`

- "The ticket label says documentation-lifecycle, but the task is only to copy-edit README and install-doc wording, fix markdown table alignment, and rename link text; do not decide ownership, source of truth, freshness, operational accuracy, or archive rules." (-> `none`)
- "The runbook title says documentation-lifecycle, but the task is incident command support: severity, timeline, next update, and follow-up quality." (-> `incident-response-and-postmortems`)
- "The docs folder says documentation-lifecycle, but the concrete work is release artifact versioning, build provenance, promotion path, and rollback target." (-> `release-build-reproducibility`)
- "The style guide issue says documentation-lifecycle, but the request is a public privacy notice wording review with no engineering controls." (-> `none`)
- "The markdown heading says documentation-lifecycle, but the task is to map logs, metrics, traces, dashboards, alerts, and runbook links for a flow." (-> `observability-and-alerting`)

### `dependency-and-code-hygiene`

- "The PR label says dependency-and-code-hygiene, but a deployed dependency is exploitable; assess exposure, patch SLA, remediation rollout, and expiring exception evidence." (-> `vulnerability-management`)
- "The cleanup ticket says dependency-and-code-hygiene, but the issue is a trusted-build gap in provenance, signatures, SBOM, and deploy admission." (-> `software-supply-chain-security`)
- "The static-analysis report says dependency-and-code-hygiene, but the task is to review the current diff for behavior mismatch and missing edge cases before merge." (-> `agent-pr-review`)
- "The dependency dashboard says dependency-and-code-hygiene, but the request is production exploit triage with exposure, compensating controls, patch rollout, and evidence." (-> `vulnerability-management`)
- "The branch name says dependency-and-code-hygiene, but the work is runtime fleet upgrade inventory, supported version windows, exceptions, and rollback compatibility." (-> `fleet-upgrades`)

## Operations And Observability

### `observability-and-alerting`

- "The dashboard says observability-and-alerting, but the request is SLO burn alert policy and urgent versus follow-up response." (-> `slo-and-error-budgets`)
- "The alert title says observability-and-alerting, but the work is on-call health: page-noise reduction, suppression safety, and engineering fixes for recurring alerts." (-> `oncall-health`)
- "The metrics folder says observability-and-alerting, but the current issue is data-pipeline freshness, lineage, validation, replay, and late batch handling." (-> `data-pipeline-reliability`)
- "The log query note says observability-and-alerting, but the task is incident timeline reconstruction, severity, roles, stakeholder updates, and follow-up owners." (-> `incident-response-and-postmortems`)
- "The dashboard tab says observability-and-alerting, but the concrete request is LLM serving token budgets, p99 latency targets, response caching, and provider fallback." (-> `llm-serving-cost-and-latency`)

### `incident-response-and-postmortems`

- "The incident-response-and-postmortems action item is not incident command; inventory the runbook owner, source of truth, freshness cadence, and stale-operational guidance cleanup." (-> `documentation-lifecycle`)
- "The ticket title says incident-response-and-postmortems, but the task is SLO burn-rate rule cleanup and separating page-worthy alerts from follow-up-only budget responses." (-> `slo-and-error-budgets`)
- "The postmortem tag says incident-response-and-postmortems, but the requested artifact is dependency timeout, retry, idempotency, overload, and fallback design." (-> `dependency-resilience`)
- "The notes say incident-response-and-postmortems, but the concrete work is phased rollout stop criteria, canary signals, and rollback target." (-> `progressive-delivery`)
- "The incident label says incident-response-and-postmortems, but the task is deployed vulnerability exposure, patch SLA, remediation rollout, and exception expiry." (-> `vulnerability-management`)

### `oncall-health`

- "The incident note says oncall-health, but the current task is live mitigation timeline and incident command." (-> `incident-response-and-postmortems`)
- "The rotation report says oncall-health, but the ask is SLO burn alert thresholds and budget policy, not schedule or page load." (-> `slo-and-error-budgets`)
- "The pager ticket says oncall-health, but the task is dashboard, log, trace, alert, and runbook instrumentation for missing receipts." (-> `observability-and-alerting`)
- "The action item says oncall-health, but the real work is recurring runbook owner, freshness cadence, source of truth, and stale guidance cleanup." (-> `documentation-lifecycle`)
- "The alert label says oncall-health, but the concrete issue is fault-injection drill planning with impact limits, abort criteria, telemetry, and rollback." (-> `resilience-experiments`)

### `operational-ownership-transfer`

- "The handoff doc says operational-ownership-transfer, but the task is runbook source of truth, owner, freshness cadence, and stale guidance cleanup." (-> `documentation-lifecycle`)
- "The rotation review says operational-ownership-transfer, but the work is steady-state page noise, suppression safety, responder toil, and recurring alert fixes." (-> `oncall-health`)
- "The acceptance packet says operational-ownership-transfer, but the concrete ask is launch readiness across deploy config, telemetry, runbooks, support, and rollback blockers." (-> `production-readiness-review`)
- "The ownership note says operational-ownership-transfer, but the artifact is an ADR for component responsibility, service boundaries, and call-direction tradeoffs." (-> `architecture-decisions`)
- "The team-transfer label says operational-ownership-transfer, but the system is being retired with zero-traffic proof, data disposition, and no-resurrection evidence." (-> `service-decommission-and-sunset`)

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "The questionnaire says secure-sdlc-and-threat-modeling, but the task is a broad compliance response with no system design, threat model, control implementation, or engineering evidence artifact." (-> `none`)
- "The ticket label says secure-sdlc-and-threat-modeling, but the concrete issue is service-account scope, secret rotation, credential lifetime, and break-glass traceability." (-> `identity-and-secrets`)
- "The checklist says secure-sdlc-and-threat-modeling, but the task is a deployed vulnerable dependency needing exposure analysis, patch SLA, rollout, and exception expiry." (-> `vulnerability-management`)
- "The review template says secure-sdlc-and-threat-modeling, but the requested artifact is package provenance, signing, SBOM completeness, and deployment admission trust." (-> `software-supply-chain-security`)
- "The doc heading says secure-sdlc-and-threat-modeling, but the ask is legal policy wording for a public security FAQ with no engineering control decision." (-> `none`)

### `input-validation-and-injection-defense`

- "The bug label says input-validation-and-injection-defense, but the issue is prompt injection, retrieved-data leakage, and unsafe tool output in a model-backed assistant." (-> `llm-application-security`)
- "The endpoint review says input-validation-and-injection-defense, but the task is API request bounds, malformed-request behavior, response compatibility, and client error semantics." (-> `api-design-and-compatibility`)
- "The security brief says input-validation-and-injection-defense, but the work is trust-boundary mapping, abuse cases, data flows, and residual risk for a new workflow." (-> `secure-sdlc-and-threat-modeling`)
- "The CVE ticket says input-validation-and-injection-defense, but the deployed system needs exposure triage, remediation SLA, rollout, and expiring exception evidence." (-> `vulnerability-management`)
- "The upload folder says input-validation-and-injection-defense, but the request is retention, deletion, minimization, and lifecycle controls for stored customer files." (-> `privacy-and-data-lifecycle`)

### `identity-and-secrets`

- "The access review says identity-and-secrets, but the task is retention, deletion, minimization, and data lifecycle checks." (-> `privacy-and-data-lifecycle`)
- "The secret-rotation ticket says identity-and-secrets, but the concrete work is key material generation, certificate expiry, algorithm lifecycle, and rotation windows." (-> `cryptography-and-key-lifecycle`)
- "The IAM review label says identity-and-secrets, but the issue is cross-tenant boundary enforcement in shared storage and request routing." (-> `tenant-isolation`)
- "The credentials doc says identity-and-secrets, but the task is a broad compliance questionnaire response with no engineering evidence or control implementation." (-> `none`)
- "The runbook section says identity-and-secrets, but the request is prompt injection and unsafe tool-output containment in a retrieval assistant." (-> `llm-application-security`)

### `cryptography-and-key-lifecycle`

- "The ticket label is cryptography-and-key-lifecycle, but the concrete issue is a deployed exploitable dependency needing patch rollout." (-> `vulnerability-management`)
- "The certificate dashboard says cryptography-and-key-lifecycle, but the task is general secret scope, service-account identity, emergency access, and credential traceability." (-> `identity-and-secrets`)
- "The encryption note says cryptography-and-key-lifecycle, but the request is privacy retention, deletion, minimization, and data lifecycle checks." (-> `privacy-and-data-lifecycle`)
- "The crypto review says cryptography-and-key-lifecycle, but the work is package signing provenance, trusted build inputs, and deploy admission trust." (-> `software-supply-chain-security`)
- "The doc title says cryptography-and-key-lifecycle, but the ask is copy-editing terminology in public docs with no key, certificate, or control change." (-> `none`)

### `software-supply-chain-security`

- "The dependency note says software-supply-chain-security, but the request is routine lockfile cleanup with rollback notes." (-> `dependency-and-code-hygiene`)
- "The SBOM card says software-supply-chain-security, but the task is build reproducibility, artifact identity, version consistency, and promotion records." (-> `release-build-reproducibility`)
- "The package issue says software-supply-chain-security, but a known CVE is already deployed and needs exposure triage, patch rollout, and exception expiry." (-> `vulnerability-management`)
- "The provenance folder says software-supply-chain-security, but the concrete work is CI, staging, local, and production environment drift that changes behavior." (-> `dev-environment-parity`)
- "The supplier questionnaire says software-supply-chain-security, but the answer is only a procurement summary with no code, artifact, or deploy control." (-> `none`)

### `vulnerability-management`

- "The security ticket says vulnerability-management, but the concrete issue is key rotation and certificate expiry lifecycle." (-> `cryptography-and-key-lifecycle`)
- "The CVE label says vulnerability-management, but the task is threat modeling a new endpoint's trust boundaries, data flows, authorization gaps, and abuse cases." (-> `secure-sdlc-and-threat-modeling`)
- "The vuln dashboard says vulnerability-management, but the request is routine dependency cleanup with no exploitable deployed exposure." (-> `dependency-and-code-hygiene`)
- "The report title says vulnerability-management, but the concrete issue is prompt injection through an LLM retrieval tool boundary." (-> `llm-application-security`)
- "The ticket tag says vulnerability-management, but the ask is source-of-truth ownership, freshness cadence, and stale remediation-runbook cleanup." (-> `documentation-lifecycle`)

### `tenant-isolation`

- "The access review is labeled tenant-isolation, but the task is general service-account secret rotation and emergency access cleanup with no tenant data path or cross-tenant boundary." (-> `identity-and-secrets`)
- "The architecture note says tenant-isolation, but the concrete work is public API tenant field compatibility for SDK clients during rollout." (-> `api-design-and-compatibility`)
- "The privacy ticket says tenant-isolation, but the ask is retention, deletion, minimization, and lifecycle controls for one tenant's exported data." (-> `privacy-and-data-lifecycle`)
- "The security review says tenant-isolation, but the issue is prompt injection leaking retrieved data through an assistant tool boundary." (-> `llm-application-security`)
- "The doc title says tenant-isolation, but the task is public edge rate limits, breach actions, bot handling, and origin shielding for abusive clients." (-> `edge-traffic-and-ddos-defense`)

### `privacy-and-data-lifecycle`

- "The privacy review says privacy-and-data-lifecycle, but the work is legal policy wording for a public privacy notice with no engineering data controls." (-> `none`)
- "The data lifecycle label says privacy-and-data-lifecycle, but the task is production-derived fixture anonymization, regeneration, freshness, and determinism." (-> `test-data-engineering`)
- "The retention ticket says privacy-and-data-lifecycle, but the concrete issue is cross-tenant access boundaries in shared storage and routing." (-> `tenant-isolation`)
- "The deletion request says privacy-and-data-lifecycle, but the work is backup restore proof with RTO and RPO evidence after accidental deletion." (-> `backup-and-recovery`)
- "The review comment says privacy-and-data-lifecycle, but the requested artifact is prompt and response retention controls for an LLM assistant that also needs injection-boundary review." (-> `llm-application-security`)

### `engineering-control-evidence`

- "The packet says engineering-control-evidence, but the requested artifact is one checkout merge gate: CI signals, release-blocking failures, and test-result acceptance for that surface only." (-> `testing-and-quality-gates`)
- "The audit folder says engineering-control-evidence, but the task is a broad compliance answer with no repository evidence, system control, or delivery artifact." (-> `none`)
- "The evidence template says engineering-control-evidence, but the concrete work is release artifact identity, version pins, promotion proof, and rollback target." (-> `release-build-reproducibility`)
- "The control packet says engineering-control-evidence, but the ask is vulnerability exposure, patch SLA, remediation rollout, and expiring exception evidence." (-> `vulnerability-management`)
- "The ticket says engineering-control-evidence, but the work is source-of-truth runbook owner, freshness cadence, stale dashboard links, and archive rules." (-> `documentation-lifecycle`)

### `llm-application-security`

- "The issue says llm-application-security, but the task is prompt and response retention, deletion, minimization, and data lifecycle checks with no prompt-injection, retrieval, tool, or unsafe-output boundary." (-> `privacy-and-data-lifecycle`)
- "The assistant review says llm-application-security, but the work is prompt-versioned eval datasets, grader thresholds, slice coverage, and regression history." (-> `llm-evaluation`)
- "The prompt-injection ticket says llm-application-security, but the ask is per-route token budgets, response-cache policy, p99 latency, and provider fallback." (-> `llm-serving-cost-and-latency`)
- "The model gateway doc says llm-application-security, but the concrete task is general secure SDLC threat modeling for a non-LLM admin export endpoint." (-> `secure-sdlc-and-threat-modeling`)
- "The label says llm-application-security, but the work is AI coding use policy, review controls, traceability, and allowed automation boundaries." (-> `ai-coding-governance`)

### `ai-coding-governance`

- "The user mentions ai-coding-governance, but the concrete risk is a production LLM tool boundary leaking retrieved data." (-> `llm-application-security`)
- "The policy doc says ai-coding-governance, but the request is to review the exact PR diff for intent match, behavior regressions, and missing tests." (-> `agent-pr-review`)
- "The assistant ticket says ai-coding-governance, but the work is module names, canonical code paths, and search ambiguity that cause agents to edit the wrong file." (-> `code-readability-for-agents`)
- "The checklist says ai-coding-governance, but the concrete issue is LLM grader datasets, prompt versions, slice coverage, and regression thresholds." (-> `llm-evaluation`)
- "The governance label says ai-coding-governance, but the task is legal policy wording about internal tool use with no engineering controls." (-> `none`)

### `llm-evaluation`

- "The file says llm-evaluation, but the acceptance criteria are per-route token caps, cache scopes, p99 latency targets, and provider-failure fallback." (-> `llm-serving-cost-and-latency`)
- "The eval report says llm-evaluation, but the issue is prompt injection, retrieved-data leakage, unsafe tool output, and containment boundaries." (-> `llm-application-security`)
- "The dataset folder says llm-evaluation, but the task is production-derived fixture anonymization, refresh cadence, determinism, and drift checks." (-> `test-data-engineering`)
- "The scorecard title says llm-evaluation, but the concrete request is experiment guardrails, treatment assignment, metric validity, and stop rules." (-> `experimentation-and-metric-guardrails`)
- "The benchmark note says llm-evaluation, but the work is model serving spend, latency, caching, and provider outage degradation." (-> `llm-serving-cost-and-latency`)

### `llm-serving-cost-and-latency`

- "The route label says llm-serving-cost-and-latency, but the request is a spend-versus-availability tradeoff for reserved capacity across the service." (-> `cost-aware-reliability`)
- "The gateway dashboard says llm-serving-cost-and-latency, but the task is prompt injection and retrieved-context leakage through tools." (-> `llm-application-security`)
- "The token budget ticket says llm-serving-cost-and-latency, but the ask is LLM evaluation slice coverage, grader thresholds, and regression history." (-> `llm-evaluation`)
- "The cost report says llm-serving-cost-and-latency, but the work is SLO burn rates and user-impact alert policy for the whole checkout journey." (-> `slo-and-error-budgets`)
- "The latency issue says llm-serving-cost-and-latency, but the blocker is browser payload growth, interaction delay, layout shifts, and runtime errors." (-> `web-release-gates`)

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "The design note asks for distributed-data-and-consistency for a saga, but the concrete decision is message ordering, idempotent consumers, compensation, and DLQ replay; storage semantics are already fixed." (-> `event-workflows`)
- "The replication doc says distributed-data-and-consistency, but the concrete work is cache invalidation, derived view refresh, stale reads, and rebuild safety." (-> `caching-and-derived-data`)
- "The issue label says distributed-data-and-consistency, but the task is database migration planning, query-plan regression, index safety, and operational rollback." (-> `database-operations`)
- "The design diagram says distributed-data-and-consistency, but the ask is state transitions, impossible states, retry races, and property tests." (-> `state-machine-correctness`)
- "The ticket title says distributed-data-and-consistency, but the request is producer and consumer compatibility rules for a shared data shape." (-> `data-contracts`)

### `event-workflows`

- "The team calls this event-workflows, but it is a synchronous downstream call needing timeouts, retries, circuit breakers, idempotent request handling, and overload behavior; no messages, queues, or replay are involved." (-> `dependency-resilience`)
- "The queue runbook says event-workflows, but the issue is metric table lineage, freshness SLIs, validation, replay, and late batches." (-> `data-pipeline-reliability`)
- "The worker ticket says event-workflows, but the concrete task is state-machine transition invariants, race tests, and must-never rules." (-> `state-machine-correctness`)
- "The message doc says event-workflows, but the work is replicated storage consistency, read-after-write expectations, and failover staleness." (-> `distributed-data-and-consistency`)
- "The label says event-workflows, but the ask is traffic replay load testing to find saturation, queue depth limits, and capacity headroom." (-> `performance-and-capacity`)

### `caching-and-derived-data`

- "The dashboard tab says caching-and-derived-data, but the question is whether replicated storage may serve stale reads after failover." (-> `distributed-data-and-consistency`)
- "The cache ticket says caching-and-derived-data, but the work is query-plan regression after schema migration and index rollback safety." (-> `database-operations`)
- "The derived-view doc says caching-and-derived-data, but the task is metric pipeline freshness, lineage, validation, replay, and late data handling." (-> `data-pipeline-reliability`)
- "The invalidation comment says caching-and-derived-data, but the concrete issue is browser payload size, interaction latency, layout shifts, and runtime errors." (-> `web-release-gates`)
- "The tag says caching-and-derived-data, but the request is public API response-field compatibility while clients roll out." (-> `api-design-and-compatibility`)

### `database-operations`

- "The alert name says database-operations, but the task is proving restore after accidental deletion with RTO and RPO evidence." (-> `backup-and-recovery`)
- "The migration folder says database-operations, but the question is cross-store consistency, replication lag, and failover semantics." (-> `distributed-data-and-consistency`)
- "The query ticket says database-operations, but the work is load-test target setting, saturation analysis, capacity headroom, and traffic ramp limits." (-> `performance-and-capacity`)
- "The schema file says database-operations, but the requested artifact is producer and consumer contract compatibility for a shared field." (-> `data-contracts`)
- "The admin note says database-operations, but the task is tenant isolation across shared storage, request routing, and authorization boundaries." (-> `tenant-isolation`)

### `data-pipeline-reliability`

- "The runbook mentions data-pipeline-reliability, but the work is anonymized fixture inventory and production-test drift." (-> `test-data-engineering`)
- "The pipeline alert says data-pipeline-reliability, but the task is SLO burn policy and user-journey alert urgency." (-> `slo-and-error-budgets`)
- "The DAG doc says data-pipeline-reliability, but the concrete issue is cached derived data invalidation and stale read protection." (-> `caching-and-derived-data`)
- "The metric table label says data-pipeline-reliability, but the request is experiment treatment assignment, metric guardrails, and stop rules." (-> `experimentation-and-metric-guardrails`)
- "The ingestion ticket says data-pipeline-reliability, but the work is consumer schema compatibility and deprecation rules for shared data." (-> `data-contracts`)

### `data-lineage-and-provenance`

- "The report catalog says data-lineage-and-provenance, but the immediate issue is pipeline freshness, late-batch replay, validation checks, and backlog recovery." (-> `data-pipeline-reliability`)
- "The consent inventory says data-lineage-and-provenance, but the task is personal-data retention, erasure, minimization, and privacy lifecycle enforcement." (-> `privacy-and-data-lifecycle`)
- "The provenance dashboard says data-lineage-and-provenance, but the work is build artifact signing, builder isolation, SBOM integrity, and deployment admission." (-> `software-supply-chain-security`)
- "The schema registry note says data-lineage-and-provenance, but the request is producer and consumer compatibility rules for a shared data field." (-> `data-contracts`)
- "The store diagram says data-lineage-and-provenance, but the concrete issue is replication lag, stale reads, conflict handling, and failover consistency." (-> `distributed-data-and-consistency`)

### `ml-reliability-and-evaluation`

- "The model card says ml-reliability-and-evaluation, but the concrete risk is prompt injection leaking retrieved tenant data through a deployed assistant's tool output." (-> `llm-application-security`)
- "The training report says ml-reliability-and-evaluation, but the work is LLM prompt-versioned grader datasets, thresholds, slices, and regression history." (-> `llm-evaluation`)
- "The model ticket says ml-reliability-and-evaluation, but the task is data-pipeline freshness, lineage, validation, replay, and late batch handling." (-> `data-pipeline-reliability`)
- "The evaluation doc says ml-reliability-and-evaluation, but the request is privacy retention, deletion, minimization, and lifecycle controls for training exports." (-> `privacy-and-data-lifecycle`)
- "The label says ml-reliability-and-evaluation, but the concrete issue is model-serving spend, token budgets, p99 latency, caching, and provider fallback." (-> `llm-serving-cost-and-latency`)

### `platform-golden-paths`

- "The service template is branded as platform-golden-paths, but the requested artifact is only declarative infrastructure policy checks, drift detection, and emergency reconciliation." (-> `infrastructure-and-policy-as-code`)
- "The scaffold repo says platform-golden-paths, but the task is private service discovery, identity, locality, and internal routing." (-> `internal-service-networking`)
- "The onboarding doc says platform-golden-paths, but the issue is environment parity across local, CI, staging, and production." (-> `dev-environment-parity`)
- "The template comment says platform-golden-paths, but the request is service-boundary ADR tradeoffs and ownership decisions." (-> `architecture-decisions`)
- "The platform issue says platform-golden-paths, but the concrete work is package provenance, trusted build inputs, signatures, and deploy admission." (-> `software-supply-chain-security`)

### `container-runtime-and-orchestration`

- "The workload note says container-runtime-and-orchestration, but the task is desired-state policy checks, drift detection, reconciliation, and exception expiry for runtime settings." (-> `infrastructure-and-policy-as-code`)
- "The pod sizing spreadsheet says container-runtime-and-orchestration, but the work is demand modeling, tail latency, saturation tests, and capacity headroom for the service." (-> `performance-and-capacity`)
- "The image checklist says container-runtime-and-orchestration, but the concrete issue is provenance, signatures, builder isolation, SBOM gaps, and deploy admission trust." (-> `software-supply-chain-security`)
- "The node rollout card says container-runtime-and-orchestration, but the request is runtime version waves, mixed-version support windows, exceptions, and rollback compatibility." (-> `fleet-upgrades`)
- "The placement diagram says container-runtime-and-orchestration, but the task is fault-domain topology, spare capacity, and surviving location loss." (-> `high-availability-design`)

### `infrastructure-and-policy-as-code`

- "The repo path says infrastructure-and-policy-as-code, but the task is internal service discovery, identity, locality, and private routing." (-> `internal-service-networking`)
- "The policy file says infrastructure-and-policy-as-code, but the work is unsafe runtime configuration validation, preview, blast-radius cap, and rollback." (-> `configuration-and-automation-safety`)
- "The IaC ticket says infrastructure-and-policy-as-code, but the task is high-availability topology and survivability when one location fails." (-> `high-availability-design`)
- "The plan heading says infrastructure-and-policy-as-code, but the concrete issue is release build artifact identity and promotion records." (-> `release-build-reproducibility`)
- "The repo label says infrastructure-and-policy-as-code, but the request is platform service template standards and adoption guidance." (-> `platform-golden-paths`)

### `internal-service-networking`

- "The dependency map says internal-service-networking, but the request is retry, timeout, circuit-breaker, and idempotency behavior." (-> `dependency-resilience`)
- "The network diagram says internal-service-networking, but the task is edge traffic filtering, abusive traffic mitigation, and DDoS defense." (-> `edge-traffic-and-ddos-defense`)
- "The service discovery ticket says internal-service-networking, but the ask is tenant isolation across shared request routing and authorization boundaries." (-> `tenant-isolation`)
- "The route table says internal-service-networking, but the concrete work is egress controls for user-supplied webhook URLs: allowlists, private-address blocking, redirect policy, and audit fields." (-> `secure-sdlc-and-threat-modeling`)
- "The mesh note says internal-service-networking, but the task is observability signals, dashboard context, alert routing, and runbook links." (-> `observability-and-alerting`)

### `edge-traffic-and-ddos-defense`

- "The edge-traffic-and-ddos-defense dashboard headline says DDoS, but the release blocker is a browser bundle that increased payload, interaction latency, layout shifts, and runtime errors for checkout." (-> `web-release-gates`)
- "The WAF ticket says edge-traffic-and-ddos-defense, but the concrete task is private service routing, internal discovery, identity, and locality." (-> `internal-service-networking`)
- "The edge alert says edge-traffic-and-ddos-defense, but the request is SLO burn-rate policy for user-impacting errors and slow successes." (-> `slo-and-error-budgets`)
- "The traffic note says edge-traffic-and-ddos-defense, but the work is load-test saturation, queue depth, and capacity headroom for checkout." (-> `performance-and-capacity`)
- "The traffic label says edge-traffic-and-ddos-defense, but the task is tenant-aware quotas, burst sharing, and noisy-neighbor fairness inside shared workers." (-> `tenant-isolation`)

### `cost-aware-reliability`

- "The FinOps note says cost-aware-reliability, but the concrete task is setting per-route LLM token budgets, tail-latency budgets, response-cache policy, and provider-failure degradation." (-> `llm-serving-cost-and-latency`)
- "The budget doc says cost-aware-reliability, but the work is SLO and error-budget policy for availability commitments, not spend allocation." (-> `slo-and-error-budgets`)
- "The savings ticket says cost-aware-reliability, but the concrete issue is load testing to find capacity headroom and saturation points." (-> `performance-and-capacity`)
- "The capacity plan says cost-aware-reliability, but the ask is high-availability topology, failover capacity, and location-loss survivability." (-> `high-availability-design`)
- "The finance label says cost-aware-reliability, but the request is a procurement cost summary with no engineering tradeoff or reliability control." (-> `none`)

### `mobile-release-engineering`

- "The release note says mobile-release-engineering, but the work is build artifact identity, package versioning, and promotion records." (-> `release-build-reproducibility`)
- "The app rollout card says mobile-release-engineering, but the task is public API compatibility for SDK clients during a response-field change." (-> `api-design-and-compatibility`)
- "The store checklist says mobile-release-engineering, but the concrete issue is feature flag owner, expiry, fallback, and removal after rollout." (-> `feature-flag-lifecycle`)
- "The crash report says mobile-release-engineering, but the work is progressive canary stop criteria and staged exposure for a backend path." (-> `progressive-delivery`)
- "The mobile ticket says mobile-release-engineering, but the blocker is browser accessibility focus, labels, contrast, and keyboard navigation." (-> `accessibility-gates`)

### `web-release-gates`

- "The browser checklist says web-release-gates, but the concrete issue is keyboard focus, labels, contrast, and accessibility blockers." (-> `accessibility-gates`)
- "The frontend release card says web-release-gates, but the task is build artifact identity, version consistency, promotion path, and rollback target." (-> `release-build-reproducibility`)
- "The Lighthouse note says web-release-gates, but the issue is edge traffic filtering, bot mitigation, rate limits, and DDoS response." (-> `edge-traffic-and-ddos-defense`)
- "The web dashboard says web-release-gates, but the ask is load-test capacity headroom and p99 saturation for an API endpoint." (-> `performance-and-capacity`)
- "The browser ticket says web-release-gates, but the work is release readiness across backend deploy config, telemetry, runbooks, and support paths." (-> `production-readiness-review`)

### `accessibility-gates`

- "The filename says accessibility-gates, but the task is only to rewrite a brand-color rationale for marketing copy with no conformance check." (-> `none`)
- "The audit label says accessibility-gates, but the release blocker is browser payload growth, interaction latency, layout shifts, and runtime errors." (-> `web-release-gates`)
- "The checklist says accessibility-gates, but the task is public docs copy-editing with no product surface, conformance, or implementation check." (-> `none`)
- "The design note says accessibility-gates, but the concrete issue is mobile store rollout guardrails, crash thresholds, and rollback constraints." (-> `mobile-release-engineering`)
- "The UI ticket says accessibility-gates, but the request is an experiment guardrail decision for metric validity and stop rules." (-> `experimentation-and-metric-guardrails`)

### `experimentation-and-metric-guardrails`

- "The reporting dashboard says experimentation-and-metric-guardrails, but there is no experiment or treatment assignment; set freshness SLIs, lineage, validation, and replay for metric tables." (-> `data-pipeline-reliability`)
- "The experiment doc says experimentation-and-metric-guardrails, but the task is canary rollout stop criteria and rollback for a production exposure ramp." (-> `progressive-delivery`)
- "The metrics ticket says experimentation-and-metric-guardrails, but the concrete ask is LLM evaluation prompt versions, grader thresholds, slices, and regression history." (-> `llm-evaluation`)
- "The A/B test label says experimentation-and-metric-guardrails, but the work is SLO alert urgency and error-budget policy for checkout." (-> `slo-and-error-budgets`)
- "The analysis note says experimentation-and-metric-guardrails, but the request is dashboard instrumentation, log fields, traces, alert routing, and runbook links." (-> `observability-and-alerting`)
