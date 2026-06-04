# Router Boundary Prompts: Near Miss

Tests in-scope neighboring engineering work that is close to the target but owned by a narrower specialist.

Prompts are grouped by the specialist that must not fire. The suffix gives the correct route.

## Architecture And Interfaces

### `api-design-and-compatibility`

- "A shared event schema changes across producers and consumers, with no public API resource or generated client surface." (-> `data-contracts`)
- "Retire an old public endpoint by blocking new callers, migrating remaining consumers, and enforcing no-new-usage checks." (-> `migration-and-deprecation`)
- "Publish producer-consumer version rules for an internal domain event used by multiple services, without adding API resources or client SDK changes." (-> `data-contracts`)
- "Set compatibility windows and version skew for a shared Kafka order event while the REST API contract remains untouched." (-> `data-contracts`)
- "Coordinate a sunset plan for a legacy SDK endpoint with consumer notices, no-new-adoption checks, and rollback criteria." (-> `migration-and-deprecation`)

### `architecture-decisions`

- "Set timeout, retry, fallback, idempotency, and overload policy for an existing dependency call without changing service ownership." (-> `dependency-resilience`)
- "Set circuit-breaker thresholds and fallback behavior for a single existing payment provider call without moving service boundaries." (-> `dependency-resilience`)
- "Make repository module names and canonical entry points easier for coding agents to locate; no service ownership decision is requested." (-> `code-readability-for-agents`)
- "Assign owners, freshness cadence, and archive criteria for ADRs that already document the service split." (-> `documentation-lifecycle`)
- "Collect cross-team control evidence for architecture review checkpoints, exception records, and release signoff artifacts." (-> `engineering-control-evidence`)

### `resilience-requirements`

- "Choose service boundaries, ownership, and call direction for a feature whose failure behavior is already specified." (-> `architecture-decisions`)
- "Turn existing availability and latency targets into burn-rate alerts, error-budget policy, and follow-up ownership." (-> `slo-and-error-budgets`)
- "Map trust boundaries, abuse cases, mitigations, and residual risk for a planned feature before code ships." (-> `secure-sdlc-and-threat-modeling`)
- "Define suite-wide merge blockers and release gates for already-written failure-behavior acceptance criteria." (-> `testing-and-quality-gates`)
- "Set retries, timeout budgets, fallback behavior, and overload policy for an existing downstream call." (-> `dependency-resilience`)

### `data-contracts`

- "Change one public API response field while preserving generated-client and existing-caller behavior." (-> `api-design-and-compatibility`)
- "Add a new REST resource and generated-client behavior while preserving existing callers." (-> `api-design-and-compatibility`)
- "Define replay, ordering, idempotency, and DLQ behavior for a message workflow whose schema is already stable." (-> `event-workflows`)
- "Design a typed public API operation and generated client names for a new account export endpoint." (-> `api-design-and-compatibility`)
- "Choose DLQ replay and out-of-order handling for an existing event whose schema will not change." (-> `event-workflows`)

### `persistent-connection-systems`

- "Define broker-mediated replay, ordering, idempotency, and poison-message recovery for async delivery after disconnects." (-> `event-workflows`)
- "Set request-response timeout, retry, fallback, and circuit-breaker policy for a dependency reached over an existing route." (-> `dependency-resilience`)
- "Model concurrent-connection headroom, memory, file descriptors, and autoscaling without changing reconnect or drain semantics." (-> `performance-and-capacity`)
- "Set private service identity, locality, and load-balancer policy for east-west traffic that carries streaming requests." (-> `internal-service-networking`)
- "Plan mobile offline sync, startup, crash, and release gates for a client feature that uses a connection when online." (-> `mobile-release-engineering`)

## Reliability And Resilience

### `slo-and-error-budgets`

- "Design new telemetry, dashboards, and alert context for a user journey before launch." (-> `observability-and-alerting`)
- "Create dashboards, traces, and alert annotations for a new API before reliability targets are set." (-> `observability-and-alerting`)
- "Reduce recurring pages for a noisy alert while preserving real user-impact escalation." (-> `oncall-health`)
- "Wire traces, logs, dashboard panels, and alert annotations for checkout before defining reliability targets." (-> `observability-and-alerting`)
- "Change the on-call escalation path to suppress duplicate pages while preserving true impact paging." (-> `oncall-health`)

### `high-availability-design`

- "Test failover behavior through controlled fault injection and game-day safety, not static topology." (-> `resilience-experiments`)
- "Run a game day that injects zone loss to prove failover procedures and abort criteria." (-> `resilience-experiments`)
- "Define RTO, RPO, restore drills, and corruption recovery for the storage layer." (-> `backup-and-recovery`)
- "Prove the region-failover runbook with a scoped game day and abort criteria, not by redesigning placement." (-> `resilience-experiments`)
- "Set backup retention and restore verification for regional data loss, including RTO and RPO targets." (-> `backup-and-recovery`)

### `multi-region-and-data-residency`

- "Set static fault-domain placement, spare capacity, and quorum assumptions to survive a region loss without residency rules." (-> `high-availability-design`)
- "Run a controlled regional evacuation game day with abort criteria and evidence, after topology and residency are already defined." (-> `resilience-experiments`)
- "Define replication conflict resolution, stale-read bounds, and write failover semantics for one replicated store." (-> `distributed-data-and-consistency`)
- "Set retention, deletion, minimization, and purpose limits for regulated regional personal data." (-> `privacy-and-data-lifecycle`)
- "Protect public edge routes with abuse controls, origin shielding, and rate-limit breach behavior across regions." (-> `edge-traffic-and-ddos-defense`)

### `dependency-resilience`

- "A queue consumer retries messages and sometimes creates duplicate work after DLQ replay; define ordering, idempotency, and poison-message recovery, not downstream-call timeout policy." (-> `event-workflows`)
- "Set per-tenant quota keys, burst sharing, and noisy-neighbor limits for shared capacity, not caller retry policy." (-> `tenant-isolation`)
- "Define whether delayed webhook events are replayed, reordered, or discarded after consumer downtime." (-> `event-workflows`)
- "Set event replay windows, poison-message handling, and idempotent repair for a queue workflow." (-> `event-workflows`)
- "Choose mTLS identity, service discovery, and locality rules for private east-west calls." (-> `internal-service-networking`)

### `performance-and-capacity`

- "Choose a cheaper capacity target while preserving reliability and error-budget commitments." (-> `cost-aware-reliability`)
- "Attribute LLM token spend by feature and set per-route latency budgets for generated responses." (-> `llm-serving-cost-and-latency`)
- "Lower reserved capacity to save spend while documenting error-budget impact." (-> `cost-aware-reliability`)
- "Reduce cloud spend by lowering headroom only after recording error-budget impact and rollback triggers." (-> `cost-aware-reliability`)
- "Cap per-feature LLM tokens and response-cache behavior to control hosted model latency." (-> `llm-serving-cost-and-latency`)

### `backup-and-recovery`

- "Add isolated builder, artifact provenance, signing, and deployment admission checks; there is no restore or data-loss scenario." (-> `software-supply-chain-security`)
- "Design HA failover capacity and fault-domain placement for losing one region without a restore." (-> `high-availability-design`)
- "Execute an online schema backfill with lock limits, query-plan checks, throttling, and abort criteria." (-> `database-operations`)
- "Run a zonal failover game day with injected faults and clear abort criteria; no restore path is exercised." (-> `resilience-experiments`)
- "Place quorum and spare capacity across fault domains to survive a data-center loss without restoring backups." (-> `high-availability-design`)

### `resilience-experiments`

- "Design static fault-domain topology, failover capacity, and location-loss survivability." (-> `high-availability-design`)
- "Set multi-zone capacity, quorum placement, and steady-state failover assumptions without injecting faults." (-> `high-availability-design`)
- "Define RTO/RPO restore drills for accidental deletion and data corruption." (-> `backup-and-recovery`)
- "Set steady-state quorum placement and capacity math for a full zone outage, without planning an experiment." (-> `high-availability-design`)
- "Schedule restore drills for corrupted customer tables with data-loss measurement." (-> `backup-and-recovery`)

### `state-machine-correctness`

- "Fuzz a stateless config-file parser and set CI merge checks; there are no protocol states, concurrency interleavings, retries, leases, or state-machine invariants beyond input validation." (-> `testing-and-quality-gates`)
- "Model cross-shard write conflicts, replication lag, and failover consistency for shared account balances." (-> `distributed-data-and-consistency`)
- "Require CI smoke, contract, and rollback checks for a stateless CLI report generator with no config mutation or lifecycle states." (-> `testing-and-quality-gates`)
- "Set merge-blocking CI checks for a pure JSON parser with fixture coverage and flaky-test quarantine." (-> `testing-and-quality-gates`)
- "Resolve replication-lag conflict handling for account writes split across two stores." (-> `distributed-data-and-consistency`)

## Delivery And Quality

### `testing-and-quality-gates`

- "Define release blockers for the checkout UI based on keyboard completion, focus order, labels, contrast, and assistive-technology support; this is not a broad CI strategy." (-> `accessibility-gates`)
- "Build fixture inventories, anonymized production samples, and freshness checks for test data drift." (-> `test-data-engineering`)
- "Review a concrete PR diff for behavioral regressions and missing edge-case tests before merge." (-> `agent-pr-review`)
- "Refresh anonymized production fixtures and define drift alerts for stale test data." (-> `test-data-engineering`)
- "Review the current PR diff for missing rollback tests and changed behavior before merge." (-> `agent-pr-review`)

### `test-data-engineering`

- "Define overall merge-blocking tests, CI signals, quality gates, and release-blocking failure probes." (-> `testing-and-quality-gates`)
- "Decide CI pass/fail signals, flaky-test quarantine policy, and merge blockers across the suite." (-> `testing-and-quality-gates`)
- "Define producer-consumer schema fixtures and compatibility rules for a shared domain event." (-> `data-contracts`)
- "Set suite-wide merge blockers, quarantine policy, and release gate ownership without changing fixtures." (-> `testing-and-quality-gates`)
- "Define compatibility fixtures for producer and consumer schema versions of a shared payment event." (-> `data-contracts`)

### `configuration-and-automation-safety`

- "Capture desired infrastructure state, drift detection, reconciliation rules, and emergency exception expiry." (-> `infrastructure-and-policy-as-code`)
- "Define policy-as-code checks for manually created network rules, including drift repair and exception expiry." (-> `infrastructure-and-policy-as-code`)
- "Roll a config-backed feature exposure through canary stages with halt metrics and rollback criteria." (-> `progressive-delivery`)
- "Represent desired firewall rules as policy-as-code with drift reconciliation and expiring exceptions." (-> `infrastructure-and-policy-as-code`)
- "Canary a new config value through rings with halt metrics and automatic rollback." (-> `progressive-delivery`)

### `release-build-reproducibility`

- "Move production traffic through canary stages with halt metrics, rollback criteria, and forward-fix options." (-> `progressive-delivery`)
- "Run a release go/no-go for customer impact, dependencies, observability, and rollback readiness before launch." (-> `production-readiness-review`)
- "Assess isolated builders, signed provenance, and deployment admission for untrusted artifacts." (-> `software-supply-chain-security`)
- "Move a signed build through 5 percent, 25 percent, and 100 percent traffic stages with abort metrics." (-> `progressive-delivery`)
- "Check launch readiness for customer support, dependencies, observability, rollback, and owner signoff." (-> `production-readiness-review`)

### `dev-environment-parity`

- "Create build-once promote-many package identity evidence and release promotion records." (-> `release-build-reproducibility`)
- "Trace a failed promotion to a mismatched package digest between staging and production, not environment drift." (-> `release-build-reproducibility`)
- "Fix an endpoint regression caused by a production query plan and missing database index." (-> `database-operations`)
- "Record package digests and build-once promote-many evidence for staging and production artifacts." (-> `release-build-reproducibility`)
- "Diagnose a production-only slow query caused by a missing index and bad query plan." (-> `database-operations`)

### `progressive-delivery`

- "Cut a reproducible release candidate with version metadata, package identity, and build-once promote-many evidence." (-> `release-build-reproducibility`)
- "Create immutable release artifacts, package versions, and promotion evidence before any traffic moves." (-> `release-build-reproducibility`)
- "Set feature-flag owner, expiry, fallback behavior, and removal criteria after rollout is done." (-> `feature-flag-lifecycle`)
- "Produce the immutable release artifact, version metadata, and promotion receipt before exposure begins." (-> `release-build-reproducibility`)
- "Decide post-rollout owner, expiry date, fallback behavior, and deletion plan for a flag." (-> `feature-flag-lifecycle`)

### `feature-flag-lifecycle`

- "Use a new flag only as a rollout mechanism with staged production exposure, canary metrics, and rollback criteria." (-> `progressive-delivery`)
- "Expose a flag to five percent, watch canary halt metrics, and rollback on user-impact regression." (-> `progressive-delivery`)
- "Remove dead flagged code paths and static-analysis warnings in cleanup batches." (-> `dependency-and-code-hygiene`)
- "Use the flag as a canary switch with staged exposure, halt metrics, and rollback triggers." (-> `progressive-delivery`)
- "Clean up a retired flag's dead branches and warnings as routine code hygiene." (-> `dependency-and-code-hygiene`)

### `production-readiness-review`

- "Plan staged rollout, canary halt metrics, rollback criteria, and forward-fix options for production exposure." (-> `progressive-delivery`)
- "Tune one public edge layer for bot handling, origin shielding, and rate-limit actions." (-> `edge-traffic-and-ddos-defense`)
- "Review a concrete branch diff before merge for regressions, missing tests, and behavior changes." (-> `agent-pr-review`)
- "Define browser payload, layout-stability, runtime-error, and interaction-readiness gates for launch." (-> `web-release-gates`)
- "Run a canary rollout plan with halt metrics and rollback rules after readiness is already approved." (-> `progressive-delivery`)

### `migration-and-deprecation`

- "Clean up dead helper code and static-analysis warnings in small batches with codemod safety." (-> `dependency-and-code-hygiene`)
- "Prioritize dead-code cleanup and warning ratchets for legacy helpers before any consumer sunset plan." (-> `dependency-and-code-hygiene`)
- "Change a public API field while preserving old generated clients and caller compatibility." (-> `api-design-and-compatibility`)
- "Add generated-client compatibility checks for changing a public response field, with existing callers preserved." (-> `api-design-and-compatibility`)
- "Remove obsolete helpers and warnings in small batches with static-analysis ratchets." (-> `dependency-and-code-hygiene`)

### `service-decommission-and-sunset`

- "Sunset a deprecated API family by blocking new callers, migrating consumers, and proving no-new-usage before teardown." (-> `migration-and-deprecation`)
- "Preview a single destructive production configuration change with input validation, blast-radius cap, abort, and rollback." (-> `configuration-and-automation-safety`)
- "Delete one obsolete database table with lock limits, query-plan checks, backup point, and rollback criteria." (-> `database-operations`)
- "Revoke and rotate service certificates and trust-chain material for a still-running replacement service." (-> `cryptography-and-key-lifecycle`)
- "Prove restore capability before deleting a store by running point-in-time recovery and reconciliation checks." (-> `backup-and-recovery`)

### `fleet-upgrades`

- "Update one package lockfile in small batches with migration notes and rollback checks." (-> `dependency-and-code-hygiene`)
- "Patch a vulnerable deployed dependency with exploitability triage, SLA, and exception expiry." (-> `vulnerability-management`)
- "Bump one dependency for a bug fix and remove obsolete imports without fleet-wide support windows." (-> `dependency-and-code-hygiene`)
- "Triage a CVE in a deployed package with exposure, patch SLA, rollout, and exception expiry." (-> `vulnerability-management`)
- "Sunset a deprecated API family across services with no-new-usage checks and migration completion evidence, not mixed-version runtime rollout." (-> `migration-and-deprecation`)

### `agent-pr-review`

- "Review this removal PR only for no-new-usage enforcement, sunset backsliding checks, and migration controls; do not give a general diff verdict." (-> `migration-and-deprecation`)
- "Set org-level AI coding-agent allowed actions, protected paths, and generated-code acceptance rules." (-> `ai-coding-governance`)
- "Plan API compatibility checks for a response-field change without asking for a general diff verdict." (-> `api-design-and-compatibility`)
- "Set protected paths, allowed actions, and required verification for AI-generated changes across the repo." (-> `ai-coding-governance`)
- "Design compatibility tests for a proposed API field rename; no concrete diff review is requested." (-> `api-design-and-compatibility`)

### `code-readability-for-agents`

- "Create an ADR for splitting the billing service into API, worker, and reconciliation modules with ownership boundaries and call direction; agent-readable names can be noted, but the artifact is the architecture decision." (-> `architecture-decisions`)
- "Choose service and worker ownership boundaries for a billing split, independent of agent searchability." (-> `architecture-decisions`)
- "Set AI-agent data boundaries, protected paths, and required verification commands for generated changes." (-> `ai-coding-governance`)
- "Approve the service split ADR with ownership boundaries, call direction, and module responsibilities." (-> `architecture-decisions`)
- "Review one AI-generated branch diff for behavioral regressions and missing tests before merge." (-> `agent-pr-review`)

### `documentation-lifecycle`

- "Rewrite README paragraphs, fix install-doc wording, and clean markdown links without ownership, freshness, operational accuracy, or archive decisions." (-> `none`)
- "Create an ADR for a service boundary decision, including ownership and call direction." (-> `architecture-decisions`)
- "Fix broken links, headings, and typo-heavy install wording with no lifecycle or operational-accuracy decision." (-> `none`)
- "Collect cross-control evidence showing runbook ownership, review cadence, exception expiry, and release checks." (-> `engineering-control-evidence`)
- "Decide service ownership boundaries in an ADR; documentation freshness is not the question." (-> `architecture-decisions`)

### `dependency-and-code-hygiene`

- "Plan support windows and mixed-version exceptions for a runtime upgrade across all services." (-> `fleet-upgrades`)
- "Plan mixed-version runtime rollout, support windows, skew exceptions, and fleet rollback." (-> `fleet-upgrades`)
- "Assess exploitability and remediation SLA for a deployed vulnerable package." (-> `vulnerability-management`)
- "Plan runtime upgrade support windows, mixed-version compatibility, and rollback across all services." (-> `fleet-upgrades`)
- "Patch an exploitable deployed dependency under a remediation SLA and expiring exception." (-> `vulnerability-management`)

## Operations And Observability

### `observability-and-alerting`

- "Reduce noisy recurring pages and responder toil without hiding user impact." (-> `oncall-health`)
- "Define SLO target, burn-rate policy, and error-budget follow-up rules for the service." (-> `slo-and-error-budgets`)
- "Cut recurring alert noise, suppression rules, and responder toil without adding telemetry." (-> `oncall-health`)
- "Set the SLO target, burn-rate alert policy, and error-budget follow-up for checkout." (-> `slo-and-error-budgets`)
- "Suppress duplicate overnight pages and tune escalation rules without creating new telemetry." (-> `oncall-health`)

### `incident-response-and-postmortems`

- "Assess exploitability and patch rollout for a deployed vulnerable dependency; there is no active incident command or postmortem." (-> `vulnerability-management`)
- "Design a post-launch alerting dashboard for a new checkout journey; no incident is active." (-> `observability-and-alerting`)
- "Patch a deployed vulnerable dependency with exploitability assessment and exception expiry outside incident command." (-> `vulnerability-management`)
- "Define new dashboards and alert context for a dependency before any incident is declared." (-> `observability-and-alerting`)
- "Handle CVE exposure triage and patch rollout as routine vulnerability work, with no incident command." (-> `vulnerability-management`)

### `oncall-health`

- "Design new logs, metrics, traces, dashboards, alerts, and runbook context for a checkout flow." (-> `observability-and-alerting`)
- "Create new alert rules, dashboards, and runbook context for an unmonitored dependency." (-> `observability-and-alerting`)
- "Set SLO burn-rate thresholds and error-budget policy for paging urgency." (-> `slo-and-error-budgets`)
- "Build missing traces, logs, dashboard panels, and runbook annotations for a new checkout dependency." (-> `observability-and-alerting`)
- "Set burn-rate paging thresholds and error-budget follow-up ownership for the service." (-> `slo-and-error-budgets`)

### `operational-ownership-transfer`

- "Assign runbook owners, source-of-truth links, freshness cadence, stale-signal checks, and archive criteria." (-> `documentation-lifecycle`)
- "Reduce noisy recurring pages, suppression rules, and responder toil for the current service owner." (-> `oncall-health`)
- "Run launch readiness for a service with customer impact, dependency, observability, rollback, and support checks." (-> `production-readiness-review`)
- "Record architectural ownership boundaries, module responsibilities, and call direction in an ADR." (-> `architecture-decisions`)
- "Retire a service with zero-traffic proof, data disposition, credential revocation, and no-resurrection evidence." (-> `service-decommission-and-sunset`)

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "A deployed dependency is exploitable and needs remediation rollout, patch SLA, and exception expiry." (-> `vulnerability-management`)
- "Rotate expiring certificates and define key custody, escrow, and trust-chain lifecycle." (-> `cryptography-and-key-lifecycle`)
- "Triage a deployed CVE with exposure, patch rollout, SLA, and exception expiry." (-> `vulnerability-management`)
- "Assess deployed CVE exposure, patch SLA, rollout sequence, and exception expiry." (-> `vulnerability-management`)
- "Verify isolated builder provenance, artifact signing, and deployment admission before release." (-> `software-supply-chain-security`)

### `input-validation-and-injection-defense`

- "Threat model trust boundaries, data flows, abuse cases, and residual risk for an admin import feature before implementation." (-> `secure-sdlc-and-threat-modeling`)
- "Set API request bounds, malformed-field behavior, and generated-client compatibility for an external contract, with no query or render sink." (-> `api-design-and-compatibility`)
- "Handle prompt-injection, retrieval leakage, unsafe tool output, and least-privilege controls for an LLM assistant." (-> `llm-application-security`)
- "Triage a deployed injection flaw with exploitability, patch SLA, rollout sequence, and exception expiry." (-> `vulnerability-management`)
- "Define server-side callback egress allowlists, private-address blocking, redirect handling, and audit fields." (-> `secure-sdlc-and-threat-modeling`)

### `identity-and-secrets`

- "Design service identity, discovery, locality, and private traffic policy for east-west calls; no runtime secret read policy or emergency access is involved." (-> `internal-service-networking`)
- "Choose east-west traffic locality and discovery for a new private route; secret access stays unchanged." (-> `internal-service-networking`)
- "Define certificate rotation, key custody, and trust-chain expiry for service authentication." (-> `cryptography-and-key-lifecycle`)
- "Plan certificate rotation, trust-chain expiry, and key custody evidence for service auth." (-> `cryptography-and-key-lifecycle`)
- "Set internal service discovery, locality, and private route policy for east-west traffic." (-> `internal-service-networking`)

### `cryptography-and-key-lifecycle`

- "Add source-to-deploy checks for signed artifacts, isolated builders, provenance, and deployment admission; no certificate expiry or key rotation plan is being asked." (-> `software-supply-chain-security`)
- "Set runtime secret read policy, emergency access, and rotation evidence for application credentials." (-> `identity-and-secrets`)
- "Verify provenance and admission controls for a third-party plugin artifact before deployment." (-> `software-supply-chain-security`)
- "Set runtime secret access, break-glass approval, rotation proof, and least-privilege checks for credentials." (-> `identity-and-secrets`)
- "Require signed provenance and deployment admission for build artifacts, not key rotation." (-> `software-supply-chain-security`)

### `software-supply-chain-security`

- "Cut a release candidate with build-once promote-many artifact identity, package versions, and promotion records; no untrusted source, builder isolation, signing, or admission-control decision is involved." (-> `release-build-reproducibility`)
- "Patch an already-deployed vulnerable dependency with exploitability triage and remediation SLA." (-> `vulnerability-management`)
- "Reconcile package digest, version metadata, and promotion receipt for a release artifact." (-> `release-build-reproducibility`)
- "Cut a reproducible release candidate with package digests and promotion evidence." (-> `release-build-reproducibility`)
- "Remediate a deployed vulnerable library with exploitability triage and patch SLA." (-> `vulnerability-management`)

### `vulnerability-management`

- "Before deployment, build a threat model with trust boundaries, data flows, abuse cases, and residual risk." (-> `secure-sdlc-and-threat-modeling`)
- "Assess whether a planned admin workflow can be abused across trust boundaries before code ships." (-> `secure-sdlc-and-threat-modeling`)
- "Clean stale dependencies and warning backlogs with small-batch update policy before any CVE exists." (-> `dependency-and-code-hygiene`)
- "Threat model a planned admin feature before deployment, including trust boundaries and abuse cases." (-> `secure-sdlc-and-threat-modeling`)
- "Clear stale package warnings and update drift without any known exposure or CVE." (-> `dependency-and-code-hygiene`)

### `tenant-isolation`

- "Define retention, deletion, minimization, and privacy lifecycle controls for customer data." (-> `privacy-and-data-lifecycle`)
- "Throttle abusive public API clients with edge route limits, breach actions, and origin shielding before requests reach shared tenant workers." (-> `edge-traffic-and-ddos-defense`)
- "Handle prompt session isolation and tool-output leakage for an LLM assistant across tenants." (-> `llm-application-security`)
- "Set retention, deletion proof, and minimization rules for customer exports." (-> `privacy-and-data-lifecycle`)
- "Threat model prompt-injection and retrieval leakage for a multi-tenant LLM assistant." (-> `llm-application-security`)

### `privacy-and-data-lifecycle`

- "Prove tenant-boundary isolation with cross-tenant access tests and blast-radius checks." (-> `tenant-isolation`)
- "Test whether support tooling can read another customer's records across tenant boundaries." (-> `tenant-isolation`)
- "Set data boundary rules for coding agents so generated changes cannot access private datasets." (-> `ai-coding-governance`)
- "Prove cross-tenant access controls with isolation tests and support-tool blast-radius checks." (-> `tenant-isolation`)
- "Define AI coding-agent data boundaries and forbidden private datasets for generated changes." (-> `ai-coding-governance`)

### `engineering-control-evidence`

- "Map one runbook set for owner, source of truth, freshness cadence, stale signal, and archive criteria." (-> `documentation-lifecycle`)
- "Decide whether stale dashboards need owners, source-of-truth links, and archive dates in runbook docs." (-> `documentation-lifecycle`)
- "Define release artifact identity evidence and promotion records for a single release train." (-> `release-build-reproducibility`)
- "Assign runbook owners, source-of-truth links, freshness cadence, and archive criteria." (-> `documentation-lifecycle`)
- "Collect artifact digest and promotion receipts for one release candidate." (-> `release-build-reproducibility`)

### `llm-application-security`

- "Build an LLM eval dataset with graders, thresholds, regression history, and failure triage." (-> `llm-evaluation`)
- "Build task-run evals for a support agent with allowed-tool trace checks, final-state assertions, repeated runs, and failure triage." (-> `llm-evaluation`)
- "Set token-budget attribution, response-cache policy, and tail-latency guardrails for LLM calls." (-> `llm-serving-cost-and-latency`)
- "Create prompt eval slices, grader thresholds, and regression history for model changes." (-> `llm-evaluation`)
- "Set per-route token budgets, cache policy, and tail-latency limits for assistant calls." (-> `llm-serving-cost-and-latency`)

### `ai-coding-governance`

- "Improve repository file names so agents can find the canonical payment implementation in one search." (-> `code-readability-for-agents`)
- "Add canonical search terms and path labels for payment handlers so agents stop landing on deprecated files." (-> `code-readability-for-agents`)
- "Review one AI-generated PR diff for regressions and missing tests before merge." (-> `agent-pr-review`)
- "Rename ambiguous files and add canonical path labels so coding agents find the right implementation." (-> `code-readability-for-agents`)
- "Review a concrete AI-generated PR for behavior changes, edge cases, and test gaps." (-> `agent-pr-review`)

### `llm-evaluation`

- "Build a prompt-injection red-team eval set for an assistant that retrieves customer records and calls write tools; require least-privilege controls, audit, and retest criteria." (-> `llm-application-security`)
- "Threat model tool access, prompt-injection boundaries, retrieval leakage, and unsafe output handling." (-> `llm-application-security`)
- "Plan production model drift monitors, promotion gates, and rollback for a non-LLM classifier." (-> `ml-reliability-and-evaluation`)
- "Create a red-team eval for prompt-injection attempts that manipulate retrieval context and write-tool arguments." (-> `llm-application-security`)
- "Set drift monitors and rollback gates for a non-LLM ranking model in production." (-> `ml-reliability-and-evaluation`)

### `llm-serving-cost-and-latency`

- "A hosted model endpoint intermittently times out; define circuit breakers, retry bounds, idempotency, and overload policy for the existing remote dependency." (-> `dependency-resilience`)
- "Set generic backend capacity headroom, saturation limits, load-test targets, and p95/p99 latency targets for a non-LLM endpoint." (-> `performance-and-capacity`)
- "Define remote dependency retry, timeout, circuit-breaker, and overload policy for an existing model provider call." (-> `dependency-resilience`)
- "Set retry bounds, timeout policy, and circuit breakers for an existing model provider call." (-> `dependency-resilience`)
- "Measure CPU saturation and p95 latency for a non-LLM hot path." (-> `performance-and-capacity`)

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "Model one in-process protocol with state transitions, locks, invariants, property tests, and fuzzing." (-> `state-machine-correctness`)
- "Property-test an in-memory lease protocol with transitions and invariants, with no cross-store writes." (-> `state-machine-correctness`)
- "Execute schema backfill locks, index changes, and query-plan checks for one database." (-> `database-operations`)
- "Model an in-process lease protocol with property tests, invariants, and fuzzing." (-> `state-machine-correctness`)
- "Plan index backfill locks, query-plan validation, and schema migration execution for one database." (-> `database-operations`)

### `event-workflows`

- "Define a producer-consumer schema compatibility plan without replay, ordering, idempotency, or dead-letter behavior." (-> `data-contracts`)
- "Publish version-skew rules for producers and consumers of a shared order event, without replay decisions." (-> `data-contracts`)
- "Fix stale reporting stream freshness with lineage checks and idempotent reprocessing." (-> `data-pipeline-reliability`)
- "Define producer-consumer schema versioning rules for a shared shipment event, without replay choices." (-> `data-contracts`)
- "Restore stream freshness with lineage validation and idempotent reprocessing after pipeline lag." (-> `data-pipeline-reliability`)

### `caching-and-derived-data`

- "A reporting stream misses freshness targets and needs lineage, validation, and idempotent reprocessing." (-> `data-pipeline-reliability`)
- "Reprocess a delayed fraud-score pipeline and prove freshness with lineage checks." (-> `data-pipeline-reliability`)
- "Decide whether primary storage may serve stale reads under replication lag and failover." (-> `distributed-data-and-consistency`)
- "Resolve cross-shard conflict handling and allowed stale reads during failover." (-> `distributed-data-and-consistency`)
- "Fix delayed batch-pipeline freshness with lineage checks and idempotent replay." (-> `data-pipeline-reliability`)

### `database-operations`

- "Split mutation state across shards and stores while preserving conflict handling, replication lag behavior, and failover consistency." (-> `distributed-data-and-consistency`)
- "Choose conflict resolution for writes split between ledger storage and profile storage during failover." (-> `distributed-data-and-consistency`)
- "Restore a tenant snapshot after accidental deletion and reconcile writes made during recovery." (-> `backup-and-recovery`)
- "Choose cross-store conflict rules and replication-lag behavior for a split ledger write." (-> `distributed-data-and-consistency`)
- "Profile endpoint headroom and p95 latency where the database is not implicated." (-> `performance-and-capacity`)

### `data-pipeline-reliability`

- "A stream-processing queue is stale after a consumer rollback; decide whether delayed messages are replayed, dropped, or manually repaired across producer and consumer versions, including idempotency and DLQ policy." (-> `event-workflows`)
- "Specify DLQ replay and idempotent repair for a queue after a poison-message burst." (-> `event-workflows`)
- "Set producer-consumer schema compatibility and versioning for a shared analytics event." (-> `data-contracts`)
- "Decide message replay, ordering, and DLQ repair for a queue after consumer downtime." (-> `event-workflows`)
- "Set producer-consumer schema compatibility for an analytics event without freshness work." (-> `data-contracts`)

### `data-lineage-and-provenance`

- "Recover a stale reporting pipeline with freshness validation, replay bounds, backlog burn-down, and idempotent reprocessing." (-> `data-pipeline-reliability`)
- "Define personal-data retention, deletion proof, minimization, and consent lifecycle controls for customer exports." (-> `privacy-and-data-lifecycle`)
- "Verify source-to-deploy artifact provenance, signed attestations, isolated builders, and admission controls." (-> `software-supply-chain-security`)
- "Set producer-consumer schema versioning and compatibility rules for a shared revenue event." (-> `data-contracts`)
- "Resolve replication-lag consistency and conflict handling for writes split across operational stores." (-> `distributed-data-and-consistency`)

### `ml-reliability-and-evaluation`

- "Build an LLM prompt eval harness with datasets, graders, thresholds, and regression history." (-> `llm-evaluation`)
- "Calibrate LLM judge rubrics and failure slices for a prompt-change release gate." (-> `llm-evaluation`)
- "Set per-route token budgets, response-cache strategy, and tail-latency limits for LLM serving." (-> `llm-serving-cost-and-latency`)
- "Build agent task-run evals with tool-call trace checks, final-state assertions, repeated runs, and failure triage." (-> `llm-evaluation`)
- "Set hosted LLM token budgets, cache rules, and tail-latency objectives." (-> `llm-serving-cost-and-latency`)

### `platform-golden-paths`

- "Set AI-agent allowed actions, protected paths, data boundaries, and generated-code acceptance rules." (-> `ai-coding-governance`)
- "Set desired infrastructure state capture, drift detection, reconciliation, and exception expiry." (-> `infrastructure-and-policy-as-code`)
- "Write generated-code acceptance and protected-path rules for AI agents contributing to the repo." (-> `ai-coding-governance`)
- "Set infrastructure desired state, drift detection, policy checks, reconciliation, and exception expiry." (-> `infrastructure-and-policy-as-code`)
- "Define AI-agent allowed actions, protected paths, and generated-code acceptance checks." (-> `ai-coding-governance`)

### `infrastructure-and-policy-as-code`

- "Run a generated production config mutation with preview, input validation, blast-radius cap, abort, and rollback." (-> `configuration-and-automation-safety`)
- "Bulk-disable a production feature setting with dry-run preview, cap, abort, and rollback." (-> `configuration-and-automation-safety`)
- "Define developer golden-path templates, paved-road service defaults, and platform adoption checks." (-> `platform-golden-paths`)
- "Run a one-time generated production config change with preview, blast-radius cap, abort, and rollback." (-> `configuration-and-automation-safety`)
- "Define paved-road service templates and golden-path adoption checks for developers." (-> `platform-golden-paths`)

### `container-runtime-and-orchestration`

- "Define desired-state policy checks, drift repair, and expiring exceptions for workload runtime settings." (-> `infrastructure-and-policy-as-code`)
- "Model latency, saturation, throughput, and headroom for a workload before choosing resource bounds." (-> `performance-and-capacity`)
- "Verify image provenance, signed attestations, builder isolation, and deployment admission for runtime artifacts." (-> `software-supply-chain-security`)
- "Plan runtime version waves, mixed-version support windows, skew exceptions, and rollback across the fleet." (-> `fleet-upgrades`)
- "Design fault-domain capacity and node-as-failure-domain survivability before setting per-workload probes." (-> `high-availability-design`)

### `internal-service-networking`

- "Protect public ingress with bot handling, rate-limit actions, origin shielding, and edge load shedding." (-> `edge-traffic-and-ddos-defense`)
- "Set retry budgets, circuit breakers, fallbacks, and overload behavior for an existing dependency call." (-> `dependency-resilience`)
- "Add public ingress bot challenges and origin shielding for a traffic spike at the edge." (-> `edge-traffic-and-ddos-defense`)
- "Constrain a server-side importer that fetches user-supplied URLs with egress allowlists, private-address blocks, redirect limits, and audit fields." (-> `secure-sdlc-and-threat-modeling`)
- "Set retry budgets, fallback behavior, and circuit breakers for an existing downstream dependency." (-> `dependency-resilience`)

### `edge-traffic-and-ddos-defense`

- "Set internal service identity, locality, discovery, and private dependency routing for service-to-service calls." (-> `internal-service-networking`)
- "Set tenant-aware quotas and noisy-neighbor fairness for shared capacity after one customer saturates workers." (-> `tenant-isolation`)
- "Plan browser release checks for responsiveness, layout stability, runtime errors, and payload growth." (-> `web-release-gates`)
- "Set private service discovery, identity, locality, and east-west routing policy." (-> `internal-service-networking`)
- "Gate a web deploy on layout shift, payload size, runtime errors, and interaction readiness." (-> `web-release-gates`)

### `cost-aware-reliability`

- "The endpoint is slow and needs latency and headroom checks, with no spend or cost tradeoff requested." (-> `performance-and-capacity`)
- "Profile CPU saturation and p95 latency for a hot endpoint before any budget tradeoff." (-> `performance-and-capacity`)
- "Attribute LLM token spend and latency budgets per feature for a hosted model route." (-> `llm-serving-cost-and-latency`)
- "Measure backend latency, CPU saturation, and capacity headroom before any budget tradeoff." (-> `performance-and-capacity`)
- "Set per-feature LLM spend attribution and token limits for hosted model calls." (-> `llm-serving-cost-and-latency`)

### `mobile-release-engineering`

- "Plan browser release checks for loading, responsiveness, layout stability, runtime errors, and payload growth." (-> `web-release-gates`)
- "Gate a web deploy on client errors, layout shift, payload growth, and interaction readiness." (-> `web-release-gates`)
- "Check checkout keyboard navigation, focus order, labels, contrast, and assistive-technology support." (-> `accessibility-gates`)
- "Gate a browser release on layout shift, runtime errors, interaction readiness, and payload growth." (-> `web-release-gates`)
- "Block checkout release on focus order, labels, contrast, and screen-reader support." (-> `accessibility-gates`)

### `web-release-gates`

- "Plan a native mobile staged rollout with startup, crash, hang, offline telemetry, pause criteria, and forward fix." (-> `mobile-release-engineering`)
- "Plan a store rollout pause rule for crash spikes, cold-start regressions, and offline sync failures." (-> `mobile-release-engineering`)
- "Define accessibility release blockers for focus order, labels, contrast, and assistive-technology support." (-> `accessibility-gates`)
- "Plan native mobile staged rollout pauses for crash spikes, cold starts, hangs, and offline sync." (-> `mobile-release-engineering`)
- "Define accessibility blockers for keyboard completion, labels, focus order, contrast, and assistive tech." (-> `accessibility-gates`)

### `accessibility-gates`

- "The checkout page has a larger script bundle and slower interaction readiness, but no keyboard, focus, label, contrast, or assistive-technology concern." (-> `web-release-gates`)
- "Gate a web release on layout stability, runtime errors, payload growth, and interaction readiness." (-> `web-release-gates`)
- "Review a native mobile rollout for startup, crash, hang, and offline telemetry pause rules." (-> `mobile-release-engineering`)
- "Gate a browser release on payload growth, interaction readiness, layout shift, and client errors." (-> `web-release-gates`)
- "Review native mobile rollout pause rules for crash rate, startup regression, hangs, and offline failures." (-> `mobile-release-engineering`)

### `experimentation-and-metric-guardrails`

- "Set canary halt metrics and rollback criteria for production traffic exposure, not an A/B readout." (-> `progressive-delivery`)
- "Shift checkout traffic through operational canary rings with abort metrics, not experiment readouts." (-> `progressive-delivery`)
- "Define SLO burn-rate alerts and error-budget follow-up policy for a service journey." (-> `slo-and-error-budgets`)
- "Canary production traffic with operational halt metrics and rollback, without treatment analysis." (-> `progressive-delivery`)
- "Define service SLO burn-rate alerts and error-budget follow-up rules." (-> `slo-and-error-budgets`)
