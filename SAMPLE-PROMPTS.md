# Sample Prompts

You do not need to name specialists when you use Staff Engineer Mode. These
prompts are grouped by specialist file so you can see the kinds of repository
work the router understands.

Paste them while the agent is in a repo, PR, branch, or workspace. Swap in real
paths, files, migrations, logs, alerts, runbooks, or diffs when you have them.

## Architecture And Interfaces

### `api-design-and-compatibility`

- "Inspect the API changes in this branch and tell me what could break existing clients."
- "Design the new partner API before implementation: resource names, operation shapes, errors, idempotency, and future compatibility."
- "The mobile SDK and a partner integration both read this response field; check whether changing it stays compatible and define the client rollout."
- "Several SDKs and partner clients still parse this response field; check compatibility before changing its type or semantics."

### `architecture-decisions`

- "Read the current repo structure and design docs, then decide whether this new service boundary makes sense."
- "Turn the decision in this PR into a short ADR with tradeoffs and revisit conditions."
- "Compare these two proposed service-boundary designs and tell me which is easier to operate and change later."
- "Map the current background jobs and request paths, then recommend whether the new worker boundary should own retries or leave them with callers."

### `data-contracts`

- "Design the new shared customer dataset before launch: producer, planned consumers, field meanings, compatibility rules, and consumer checks."
- "Define the producer and consumer contract for this shared schema field, including compatibility and deprecation rules."
- "Inspect this existing shared data shape and define producer/consumer compatibility rules before changing it."
- "A reporting table adds nullable columns and changes enum meanings; check producer and consumer expectations before publishing it."

## Reliability And Resilience

### `slo-and-error-budgets`

- "Design SLIs and SLOs for the new checkout API before launch using its user journeys and expected traffic."
- "Inspect this service's SLO burn-rate rules and separate urgent alerts from follow-up-only budget responses."
- "Use the service code and recent incidents to draft error-budget release rules."
- "Checkout has fast failures and slow successes; decide which user outcome should burn budget and which alerts should stay non-urgent follow-ups."

### `high-availability-design`

- "Review a deployment topology and identify what would still fail if one hosting location went down."
- "Inspect the failover code path, static capacity, and runbook, then list the availability assumptions we still need to check."
- "Trace the serving path and fault-domain map, then identify which shared dependency or control-plane loss could break high availability for the whole feature."
- "During a zone evacuation, this feature still needs reads and writes; inspect which components share a failover dependency."

### `dependency-resilience`

- "Before adding this new downstream call, define timeout, retry, duplicate-work, and overload behavior."
- "Trace this existing queue consumer and tell me how it behaves when the dependency gets slow."
- "Inspect this downstream payment dependency call and find where retries could double-charge or duplicate work."
- "This new inventory call sits in checkout; decide timeout, retry, and fallback behavior when inventory stalls."

### `performance-and-capacity`

- "Set capacity and load-test targets for a new checkout endpoint before traffic ramps."
- "Inspect this load-test script and tell me whether it shows enough headroom for the code path it exercises."
- "Trace the hot path for this endpoint and point out likely bottlenecks before traffic doubles."
- "P99 doubled only for large tenants after the merge; use traces and profiles to find the saturation point."

### `backup-and-recovery`

- "Inspect the backup jobs and restore scripts in this repo, then design an RTO/RPO restore test."
- "Inspect this migration and tell me how we would recover from production data corruption or accidental deletion."
- "Read the disaster-recovery runbook and backup files, then call out restore assumptions that still need a test."
- "Before deleting old records, verify we can restore a tenant snapshot and reconcile writes made during recovery."

### `resilience-experiments`

- "Design a safe fault-injection test for this dependency with blast-radius limits, abort criteria, telemetry, and rollback."
- "Inspect the failover script and monitoring, then plan a game day with blast-radius limits and abort criteria."
- "Look at this chaos-test PR and define stop conditions, impact limits, learning goals, and rollback steps."
- "Plan a drill where the queue broker returns errors for ten minutes, with who can abort and what blast radius is allowed."

### `state-machine-correctness`

- "Design the new payout state machine before implementation: states, transitions, must-never rules, must-eventually rules, and retry cases."
- "Inspect this existing locking code and tests for races, impossible states, or missed concurrency edges."
- "Design property tests or simulations for this high-stakes money-moving state machine."
- "The order can move from paid to canceled during retry races; enumerate invalid transitions and how to test them."

## Delivery And Quality

### `testing-and-quality-gates`

- "Design the test strategy for this payment workflow change: what blocks merge, what blocks release, and what can run later."
- "Inspect the CI config and test layout, then find weak signals that could let a bad release through."
- "Build a practical test plan for this feature using the code that changed in this branch."
- "The feature touches auth, billing, and background jobs; decide the minimal blocking test set and what can run nightly."

### `test-data-engineering`

- "Design a test-data inventory for this suite: fixture purpose, regeneration path, ownership, and unreproducible data."
- "Design fixture and golden-file rules for this new integration test suite before it starts using production samples."
- "Find where production data shape has drifted from the data the tests run on and design a drift-detection check."
- "These fixtures came from support exports; check whether they are still representative and safe to keep."

### `configuration-and-automation-safety`

- "Design validation, preview, blast-radius limits, and rollback rules for a new tenant-limit config setting before automation writes it."
- "Inspect this automation script and tell me how it can safely mutate production state with an abort path."
- "Find unsafe runtime config values and temporary overrides before the cleanup automation runs, then add owners, expiry, validation, and rollback."
- "A script will rewrite tenant limits from a CSV; add preview, validation, per-tenant caps, and rollback."

### `release-build-reproducibility`

- "Define build reproducibility checks for version consistency, artifact identity, required checks, promotion path, and rollback target."
- "Inspect the packaging config and design a build-once, promote-many release path."
- "Find why this repo's builds are flaky or cache-sensitive and rank the fixes."
- "Two CI runners produce different package hashes; trace the unpinned inputs before the release is promoted."

### `dev-environment-parity`

- "Build a parity matrix across local, CI, staging, and production for this service and find the divergences the config, docs, or runbooks do not name."
- "This fix worked locally and failed in CI; trace the environment dimensions that differ and tell me which one hid the bug."
- "Define a drift budget for these environments with action triggers, allowed divergence, and required parity."
- "Staging uses seeded tenants while local uses mocks; find which environment gap hid this serialization bug."

### `progressive-delivery`

- "Build a rollout and rollback plan for the new ranking path before production exposure."
- "Inspect this staged rollout plan before exposure and tell me what canary checks, stop criteria, and rollback path are missing."
- "Define first-rollout stop criteria from deploy workflow signals and canary metrics, including minimum signal, thresholds, owner, abort, and rollback."
- "Ramp the new ranking path by tenant cohort and define metrics that pause exposure before all users see it."

### `feature-flag-lifecycle`

- "Before adding a new feature flag, define owner, expiry, fallback behavior, and the removal plan."
- "Find orphan flags whose feature shipped or whose owner left, and propose a safe removal sequence."
- "Inspect this flag-debt scorecard and tell me which flags will become contradictory defaults if we leave them in."
- "This flag now defaults on in every environment; find remaining off-path code and plan removal safely."

### `production-readiness-review`

- "Build a production-readiness decision for the new service in this repo before launch."
- "Before this migration moves traffic tomorrow, inspect code, deploy config, dashboards, and runbooks for launch blockers."
- "Inspect the code, deploy config, dashboards, and runbooks, then say what launch details are missing."
- "Before the new importer becomes high impact, collect blockers across code, deploy, telemetry, and support docs."

### `migration-and-deprecation`

- "Find every caller of this old module and plan a safe migration across the repo."
- "Inspect the deprecation PR and tell me how to prevent new usage from being added."
- "Inspect this service retirement plan against the codebase and identify anything that could strand users or teams."
- "The legacy invoice worker still has hidden cron callers; build batches to move them and block new usage."

### `fleet-upgrades`

- "Build an upgrade plan for this runtime across all services, including support windows and allowed version skew."
- "Inspect this platform upgrade and identify mixed-version combinations we need to test before rollout."
- "Inspect the existing fleet inventory and find unsupported versions, owners, exceptions, and cleanup checks."
- "During this runtime fleet upgrade, some services cannot move until clients update; plan version-skew windows and exceptions."

### `agent-pr-review`

- "Before committing the staged changes, review the exact diff for intent match, behavior verification, and missing edge cases."
- "Find risks in the diff I'm about to push: silent assumptions, hallucinated APIs, scope creep, deleted-but-used code."
- "What did the agent (or I) miss in this branch that we'd be embarrassed to ship?"
- "The diff passes tests but changed deletion behavior; review what details are missing before merge."

### `code-readability-for-agents`

- "Design module boundaries and names for a new payment workflow so an AI agent can find the canonical implementation in one tool call."
- "Find names in this codebase that collide or mislead code search and propose renames that make the canonical version unambiguous."
- "Inspect function and file sizes against a budget and tell me which files an agent will silently misread."
- "There are three payment clients with similar names; find the canonical one and where an agent could choose wrong."

### `documentation-lifecycle`

- "Map these runbooks and design docs for owner, source of truth, freshness, and archive rules."
- "Inspect the docs touched by this release and identify stale or missing operational guidance."
- "Turn this undocumented maintenance workflow into a lifecycle-managed runbook with source of truth, owner, freshness rule, and change triggers."
- "The failover runbook points to old dashboards; set owner, expiry, and freshness trigger so it stays current."

### `dependency-and-code-hygiene`

- "Find all uses of this deprecated dependency and plan a small-batch hygiene cleanup with lockfile and codemod safety checks."
- "Plan this dependency update and lockfile sweep for migration, hygiene, and rollback risks."
- "Inspect the static-analysis backlog and changed files, then prioritize fixes that reduce real maintenance risk."
- "Triage the static-analysis warning on a deprecated helper across five packages, then plan small hygiene cleanup batches with codemod safety checks."

## Operations And Observability

### `observability-and-alerting`

- "Design logs, metrics, traces, dashboards, alerts, and runbook updates for a new payment flow before launch."
- "Inspect the alert definitions in this repo and map each one to user-journey telemetry, dashboard context, and a runbook."
- "Trace this request across services and tell me what correlation context is missing."
- "Users report missing receipts but dashboards only show worker CPU; design signals that show where work disappears."

### `incident-response-and-postmortems`

- "Use these logs, commits, and incident notes to build a clear timeline and follow-up list."
- "An incident is in progress; use these symptoms and recent commits to help set severity, roles, updates, and next decisions."
- "Inspect this postmortem draft and mark follow-up actions that are too vague to verify in the repo."
- "Checkout errors spiked after a deploy twenty minutes ago; build the timeline, owners, and next update."

### `oncall-health`

- "We get paged all night for this service; cut the noise without missing real incidents."
- "Inspect these on-call suppression rules and verify page-noise reduction is not hiding real user impact."
- "This alert fires every week and the runbook says to rerun a job manually; decide what engineering fix should replace that manual step."
- "Find which alerts should page, which should become follow-ups, and which should be deleted or grouped."

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "Threat-model this customer data export PR for abuse cases, authorization gaps, unsafe inputs, and residual risk."
- "Inspect the changed files and write trust-boundary and data-flow security requirements we should meet before implementation is done."
- "Threat-model this new endpoint using the code, routes, permissions, data flows, and controls it touches."
- "A new admin export crosses customer data and support tools; trace trust boundaries and abuse cases before implementation."

### `identity-and-secrets`

- "Inspect the service-account identity, scope, and permission changes in this PR for access that is too broad."
- "Inspect how secrets are loaded in this repo and design credential rotation that will not break production."
- "Inspect workload identities, secret scopes, credential lifetime, break-glass access, and traceability gaps in this repo."
- "The importer uses a shared token with write access everywhere; design narrower workload access and rotation."

### `cryptography-and-key-lifecycle`

- "Inventory existing certificates, keys, trust roots, owners, expiry dates, and renewal paths for this service."
- "Plan a certificate rotation that shows old and new trust paths work before the old certificate is removed."
- "Inspect this cryptographic algorithm transition for compatibility, monitoring, exceptions, and retirement checks."
- "The signing key has no owner and clients pin the old algorithm; plan compatibility and retirement checks."

### `software-supply-chain-security`

- "Inspect the existing source-to-deploy chain for places an untrusted artifact could slip in."
- "Inspect the release scripts and show how artifact provenance, signing, and builder isolation identify where artifacts came from."
- "Find secret-scanning, dependency inventory, signing, provenance, or deployment-admission checks that should block release."
- "A deploy can pull artifacts from a mutable bucket; verify source, builder, signature, and admission controls."

### `vulnerability-management`

- "Before promoting this new image, triage its vulnerable packages by exploitability, exposure, patch path, and exception expiry."
- "Inspect this PR that delays a security patch and define the vulnerability exception details, owner, and expiry it needs."
- "Map the current advisories to deployed services and propose remediation deadlines based on exploitability and impact."
- "An advisory affects a library used by two live services and one internal tool; set patch order and exception expiry."

### `tenant-isolation`

- "Design tenant-isolation checks for a new support search feature that can query customer accounts."
- "Inspect the multi-tenant quota code and tell me whether one large tenant can hurt other tenants."
- "Use the access logs and tenant-context code path to check whether support search stayed isolated to one tenant."
- "Support search can query multiple accounts; verify tenant context cannot be dropped on fallback paths."

### `privacy-and-data-lifecycle`

- "Design the personal-data flow for this new feature: minimization, storage, deletion, export, and logging controls."
- "Inspect the telemetry changes and remove personal data that is not needed for privacy-safe operations."
- "Check the retention, erasure, and deletion-propagation jobs for this workflow and identify missing privacy controls."
- "Debug logs include email and free-form notes; decide what to drop, hash, retain, and erase."

### `engineering-control-evidence`

- "Turn the release checks in this repo into a cross-surface engineering record pack we can collect every release."
- "Build a control record pack from the tests, CI, dashboards, runbooks, and change records."
- "Inspect these engineering exceptions and make sure each one has an owner, expiry, and compensating control."
- "For the release record pack, map CI, approvals, runbooks, and dashboards into one control record set with exceptions."

### `llm-application-security`

- "Threat-model a new LLM assistant before launch for prompt injection, unsafe tool access, and data leakage."
- "Inspect the LLM retrieval and tool boundary for prompt injection, unsafe document access, and data leakage."
- "Inspect the model output handling path for prompt-injected links, unsafe tool arguments, and data leakage before this feature ships."
- "The assistant can open retrieved docs and call tools; identify where a malicious document could steer actions."

### `ai-coding-governance`

- "Inspect our repo instructions for AI coding agents and add rules for protected paths, tests, and data boundaries."
- "Design repo-level verification requirements for AI-generated PRs before a human should approve them."
- "Define acceptance checks for agent-written code in this repo without replacing normal change responsibility."
- "Agents can edit generated schemas and fixtures; write repo rules for protected paths, tests, and traceability details."

### `llm-evaluation`

- "Design an eval harness for this prompt change with cases, graders, thresholds, and regression history."
- "Inspect these model-backed workflow evals and find where the scoring or slice coverage is weak."
- "Turn recent bad outputs into release-blocking eval cases with owners and failure triage."
- "A prompt tweak improved summaries but broke refund cases; build regression slices and a pass threshold."

### `llm-serving-cost-and-latency`

- "Set token and p50/p95/p99 latency budgets for a new LLM-backed route before launch."
- "Design the prompt, embedding, and response cache strategy for this feature, and define when a cache miss has to fall back to a smaller model."
- "Map existing per-call LLM spend to route, feature, and tenant, then draft a degradation path for the next provider outage."
- "The support route fans out to three model calls; set latency and token budgets plus what degrades first."

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "Inspect this data model and migration before we split it across databases."
- "Trace this workflow across two services and the database, then show where correctness can break."
- "Inspect this cross-service lock and decide whether failover or replica lag can make it unsafe."
- "A tenant move may leave reads split across old and new shards; decide acceptable consistency and repair path."

### `event-workflows`

- "Design a new refund event workflow with replay, failed-message handling, duplicate handling, ordering, and DLQ behavior."
- "Inspect this event message change and find producer or consumer replay, ordering, idempotency, or DLQ behavior that might break."
- "Trace this event-driven workflow across producers, consumers, replay, and failed-message handling; show where partial failure could lose work."
- "A refund saga sends email before payment settles; trace partial failures and replay behavior."

### `caching-and-derived-data`

- "Design a new product-card cache with TTL, invalidation, miss-storm behavior, and stale-result handling."
- "Inspect this hot cache key and design protection so too many callers do not hit the backend at once."
- "Check the derived search-index refresh path and define stale-result freshness checks we can verify."
- "Inventory updates arrive but the product card stays stale; map invalidation order and cold-cache behavior."

### `database-operations`

- "Inspect this schema migration and backfill before it runs in production."
- "Inspect this index change and tell me how to avoid table locks or replica pain."
- "Inspect the query plan, index choice, and schema migration diff, then decide whether the database change needs rollback, throttling, or a new index."
- "Use the query plan and schema migration diff to find why this endpoint got slower after the database change."

### `data-pipeline-reliability`

- "Design the new revenue pipeline before launch: freshness targets, validation checks, lineage, replay, and recovery."
- "Inspect this stream change and design data-quality checks before downstream reports trust it."
- "Use the failed warehouse load logs and jobs to build a recovery plan that avoids double-counting."
- "Late-arriving events are replayed after dashboard cutoff; define freshness, validation, and no-double-count recovery."

### `ml-reliability-and-evaluation`

- "Define eval coverage, rollback, and production-risk checks for this model-serving change."
- "Inspect the training and serving code for places the model can get stale or behave differently in production."
- "The new model will replace the live fraud endpoint; define promotion checks from evals, skew checks, drift monitors, rollback, tests, metrics, and deploy workflow."
- "The fraud model retrains weekly but features changed yesterday; compare training and serving inputs plus rollback checks."

### `platform-golden-paths`

- "Inspect this repo's service template and make it a safer golden path for new production services."
- "Inspect the service catalog and template docs for friction teams hit when starting new services."
- "Find where teams bypass the platform in this repo and identify friction we should remove."
- "New services copy old templates then delete safety checks; update the template and scorecard to make the paved path easier."

### `infrastructure-and-policy-as-code`

- "Inspect this declarative infrastructure change for unsafe manual steps, missing policy checks, drift response, and rollback gaps."
- "Inspect infrastructure environment promotion for desired-state drift, missing policy checks, and whether actual changes match what is declared in code."
- "Design policy checks and exception records for these infrastructure files."
- "A manual console change fixed staging; capture desired state, drift detection, and emergency exception rules."

### `internal-service-networking`

- "Design internal routing for a new checkout service, including discovery, identity, locality, and private dependency access."
- "Inspect this internal traffic policy for service-to-service access that is too open."
- "Inspect internal service-to-service routing config and keep this private dependency's traffic local when possible."
- "Refresh the internal networking runbook for checkout: discovery, locality, identity, and fallback when private routing fails."

### `edge-traffic-and-ddos-defense`

- "Inspect the public API rate limits and origin protection in this repo before launch."
- "Inspect the signup flow and edge rules for bot filters that will not block real users."
- "Design edge traffic shedding for this route using the current routing and deployment config."
- "Signup traffic spikes with suspicious user agents; set edge limits that protect origin without blocking real customers."

### `cost-aware-reliability`

- "Before adding a new replica set for failover, compare the reliability gain against ongoing platform cost."
- "Inspect this capacity change and explain the reliability benefit versus the cost."
- "Inspect tags, owners, and shared resources so teams can act on their platform costs."
- "Replica count grew after an incident; decide what spend can be removed without losing failover headroom."

### `mobile-release-engineering`

- "Plan staged rollout, halt criteria, and forward-fix options for this new mobile release."
- "Inspect startup, crash, hang, and offline telemetry before approving this app release."
- "Use the release notes and changed files to choose rollback or forward-fix options for this app-store bug."
- "Crash-free users dip only on older OS versions after the mobile app staged rollout; decide pause, forward fix, or rollback."

### `web-release-gates`

- "Plan browser release checks for a new checkout flow covering loading, responsiveness, layout stability, runtime errors, and payload growth."
- "Inspect field and lab performance signals before rolling out this frontend change."
- "For this browser client-side change, add release checks and telemetry for loading, interaction readiness, layout stability, runtime errors, and payload growth."
- "The checkout bundle gained a heavy dependency; set checks for interaction readiness and runtime errors."

### `accessibility-gates`

- "Inspect this checkout flow for keyboard completion, focus order, labels, contrast, and release blockers."
- "Design accessibility checks for a new checkout flow before launch."
- "Turn these accessibility bugs into journey-based regression checks with owners and retest dates."
- "A modal traps keyboard focus after payment failure; turn it into a release-blocking journey check."

### `experimentation-and-metric-guardrails`

- "Inspect this experiment design for assignment, exposure logging, guardrail metrics, and readout rules."
- "The A/B test result looks suspicious; inspect sample balance, missing telemetry, and metric definitions."
- "Decide whether this experiment ramp should continue using assignment balance, exposure logging, metric validity checks, and guardrail metrics."
- "The ramp looks positive but guardrail logging changed halfway through; decide whether the readout is trustworthy."

## Out Of Scope

### `none`

- "Write a marketing launch plan for the new checkout feature."
- "How much should we pay engineers for being on call?"
- "Rewrite this landing page headline to sound warmer."
- "Pick a company offsite venue and catering plan."
