# Sample Prompts

You do not need to name skills when you use Staff Engineer Mode. These prompts
are grouped by skill so you can see the kinds of repository work the router
understands.

Paste them while the agent is in a repo, PR, branch, or workspace. Swap in real
paths, files, migrations, logs, alerts, runbooks, or diffs when you have them.

## Architecture And Interfaces

### `api-design-and-compatibility`

- "Review the API changes in this branch and tell me what could break existing clients."
- "Inspect the endpoint code and API schema docs for this new pagination behavior before we merge."
- "The mobile SDK and a partner integration both read this response field; check whether changing it stays compatible and define the client rollout."
- "Several SDKs and partner clients still read this response field; check compatibility and removal gates before changing it."

### `architecture-decisions`

- "Read the current repo structure and design docs, then review whether this new service boundary makes sense."
- "Turn the decision in this PR into a short ADR with tradeoffs and revisit conditions."
- "Compare these two implementation branches and tell me which design is easier to operate and change later."
- "Map the current background jobs and request paths, then recommend whether the new worker boundary should own retries or leave them with callers."

### `data-contracts`

- "Review this shared dataset change for producer and consumer compatibility before we merge."
- "Inspect the schema and downstream usage, then define the contract and removal gates for this field."
- "Find where teams depend on this data shape and build a migration plan that will not break consumers."
- "A reporting table adds nullable columns and changes enum meanings; check producer and consumer expectations before publishing it."

## Reliability And Resilience

### `slo-and-error-budgets`

- "Look at this service's routes, dashboards, and alerts, then propose user-centered SLIs and SLOs."
- "Review the alert rules against this service's SLOs and separate paging alerts from ticket-only alerts."
- "Use the service code and recent incidents to draft an error-budget policy for releases."
- "Checkout has fast failures and slow successes; decide which user outcome should burn budget and which alerts should stay tickets."

### `high-availability-design`

- "Inspect this deployment config and fault-domain topology for what still fails if one hosting location goes down."
- "Review the failover code path, static capacity, and runbook, then list the availability assumptions we still need to prove."
- "Trace the dependencies in this repo and identify which single dependency loss could break high availability for the whole feature."
- "During a zone evacuation, this feature still needs reads and writes; inspect which components share a failover dependency."

### `dependency-resilience`

- "Review this PR's new downstream call for timeout, retry, duplicate-work, and overload risks."
- "Trace this queue consumer and tell me how it behaves when the dependency gets slow."
- "Inspect this downstream payment dependency call and find where retries could double-charge or duplicate work."
- "This new inventory call sits in checkout; decide timeout, retry, and fallback behavior when inventory stalls."

### `performance-and-capacity`

- "Use the changed files and benchmark output to explain why the slowest requests got worse."
- "Review this load-test script and tell me whether it proves enough headroom for the code path it exercises."
- "Trace the hot path for this endpoint and point out likely bottlenecks before traffic doubles."
- "P99 doubled only for large tenants after the merge; use traces and profiles to find the saturation point."

### `backup-and-recovery`

- "Inspect the backup jobs and restore scripts in this repo, then design an RTO/RPO restore test."
- "Review this migration and tell me how we would recover from production data corruption or accidental deletion."
- "Read the disaster-recovery runbook and backup files, then call out restore assumptions that are not proven."
- "Before deleting old records, prove we can restore a tenant snapshot and reconcile writes made during recovery."

### `resilience-experiments`

- "Design a safe fault-injection test for this dependency using the current service code and runbook."
- "Review the failover script and monitoring, then plan a game day with blast-radius limits and abort criteria."
- "Look at this chaos-test PR and define stop conditions, impact limits, learning goals, and rollback steps."
- "Plan a drill where the queue broker returns errors for ten minutes, with who can abort and what blast radius is allowed."

### `state-machine-correctness`

- "Trace this state machine and write the invariants it must never break."
- "Review this locking code and tests for races, impossible states, or missed concurrency edges."
- "Design property tests or simulations for this high-stakes money-moving state machine."
- "The order can move from paid to canceled during retry races; enumerate invalid transitions and how to test them."

## Delivery And Quality

### `testing-and-quality-gates`

- "Review this PR and tell me which tests should block merge and which can run after merge."
- "Inspect the CI config and test layout, then find weak signals that could let a bad release through."
- "Build a practical test plan for this feature using the code that changed in this branch."
- "The feature touches auth, billing, and background jobs; decide the minimal blocking test set and what can run nightly."

### `test-data-engineering`

- "Inventory the fixtures this suite depends on and tell me which ones cannot be regenerated."
- "Review this golden file and the production sample it came from, then prove the anonymization actually holds."
- "Find where production data shape has drifted from the data the tests run on and design a drift-detection check."
- "These fixtures came from support exports; check whether they are still representative and safe to keep."

### `configuration-and-automation-safety`

- "Review this production config change for validation, preview, blast radius, and rollback before it runs."
- "Inspect this automation script and tell me how it can safely mutate production state with an abort path."
- "Find configuration drift and temporary overrides before the cleanup automation runs, then add owners, expiry, validation, and rollback."
- "A script will rewrite tenant limits from a CSV; add preview, validation, per-tenant caps, and rollback."

### `release-build-reproducibility`

- "Review the build scripts and release workflow to see whether we can rebuild last week's artifact."
- "Inspect the packaging config and design a build-once, promote-many release path."
- "Find why this repo's builds are flaky or cache-sensitive and rank the fixes."
- "Two CI runners produce different package hashes; trace the unpinned inputs before the release is promoted."

### `dev-environment-parity`

- "Build a parity matrix across local, CI, staging, and production for this service and find the divergences nobody named."
- "This fix worked locally and failed in CI; trace the environment dimensions that differ and tell me which one hid the bug."
- "Define a drift budget for these environments with action triggers, allowed divergence, and required parity."
- "Staging uses seeded tenants while local uses mocks; find which environment gap hid this serialization bug."

### `progressive-delivery`

- "Build a rollout and rollback plan for the config change in this PR."
- "Review this feature-toggle implementation before rollout and tell me what canary checks, stop criteria, and rollback path are missing."
- "Use the deploy workflow and metrics files to define when we should stop a small first rollout."
- "Ramp the new ranking path by tenant cohort and define metrics that pause exposure before all users see it."

### `feature-flag-lifecycle`

- "The rollout is done; now build me an inventory of every live flag with owner, expiry, and removal plan."
- "Find orphan flags whose feature shipped or whose owner left, and propose a safe removal sequence."
- "Review this flag-debt scorecard and tell me which flags will become contradictory defaults if we leave them in."
- "This flag now defaults on in every environment; find remaining off-path code and plan removal safely."

### `production-readiness-review`

- "Run a production-readiness review for the service in this repo before launch."
- "Before this migration moves traffic tomorrow, inspect code, deploy config, dashboards, and runbooks for launch blockers."
- "Inspect the code, deploy config, dashboards, and runbooks, then say what evidence is missing for launch."
- "Before the new importer becomes tier 1, collect blockers across code, deploy, telemetry, and support docs."

### `migration-and-deprecation`

- "Find every caller of this old module and plan a safe migration across the repo."
- "Review the deprecation PR and tell me how to prevent new usage from being added."
- "Inspect this service retirement plan against the codebase and identify anything that could strand users or teams."
- "The legacy invoice worker still has hidden cron callers; build batches to move them and block new usage."

### `fleet-upgrades`

- "Build an upgrade plan for this runtime across all services, including support windows and allowed version skew."
- "Review this platform upgrade and identify mixed-version combinations we need to prove before rollout."
- "Inspect the fleet inventory and find unsupported versions, owners, exceptions, and cleanup gates."
- "Some services cannot move runtime versions until clients update; plan compatibility windows and exceptions."

### `code-review-and-workflow`

- "Review this large PR workflow and suggest change-size limits for splitting it without losing review context."
- "Inspect ownership files and recent changes to find why code reviews are slow and what latency targets should change."
- "Look at this shared repo and propose code-review ownership boundaries that match how the code actually changes."
- "A team keeps rubber-stamping risky generated diffs; propose review rules and size limits that reduce latency without hiding risk."

### `agent-pr-review`

- "Review this PR before merge and tell me what a senior reviewer would catch — intent match, behavior evidence, missing edge cases."
- "Find risks in the diff I'm about to push — silent assumptions, hallucinated APIs, scope creep, deleted-but-used code."
- "What did the agent (or I) miss in this branch that we'd be embarrassed to ship?"
- "The diff passes tests but changed deletion behavior; review what evidence is missing before merge."

### `code-readability-for-agents`

- "Audit this repo's module boundaries, names, and file sizes for whether an AI agent can find the canonical implementation in one tool call."
- "Find names in this codebase that collide or mislead code search and propose renames that make the canonical version unambiguous."
- "Review function and file sizes against a budget and tell me which files an agent will silently misread."
- "There are three payment clients with similar names; find the canonical one and where an agent could choose wrong."

### `documentation-lifecycle`

- "Audit these runbooks and design docs for owner, source of truth, freshness, and archive rules."
- "Inspect the docs touched by this release and identify stale or missing operational guidance."
- "Turn this undocumented maintenance workflow into a lifecycle-managed runbook with source of truth, owner, freshness rule, and review triggers."
- "The failover runbook points to old dashboards; set owner, expiry, and review trigger so it stays current."

### `dependency-and-code-hygiene`

- "Find all uses of this deprecated dependency and plan a small-batch hygiene cleanup with lockfile and codemod safety checks."
- "Review this dependency update and lockfile sweep for migration, hygiene, and rollback risks."
- "Inspect the static-analysis backlog and changed files, then prioritize fixes that reduce real maintenance risk."
- "The static analyzer warns on a deprecated helper across five packages; plan the smallest cleanup batches."

## Operations And Observability

### `observability-and-alerting`

- "Inspect this payment flow and propose the logs, metrics, traces, dashboards, alerts, and runbook updates it needs."
- "Review the alert definitions in this repo and map each one to user-journey telemetry, dashboard context, and a runbook."
- "Trace this request across services and tell me what correlation context is missing."
- "Users report missing receipts but dashboards only show worker CPU; design signals that show where work disappears."

### `incident-response-and-postmortems`

- "Use these logs, commits, and incident notes to build a clear timeline and follow-up list."
- "An incident is in progress; use these symptoms and recent commits to help set severity, roles, updates, and next decisions."
- "Review this postmortem draft and mark follow-up actions that are too vague to verify in the repo."
- "Checkout errors spiked after a deploy twenty minutes ago; build the timeline, owners, and next update."

### `oncall-health`

- "Review the alert history and runbooks in this repo, then find the noisiest safe pages to remove."
- "Inspect these weekly operations notes and identify toil that can be automated or eliminated."
- "Review these on-call suppression rules and prove we are reducing page noise without hiding real user impact."
- "The same job wakes primary every morning and gets manually retried; decide what to automate or downgrade."

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "Threat-model this customer data export PR for abuse cases, authorization gaps, unsafe inputs, and residual risk."
- "Inspect the changed files and write trust-boundary and data-flow security requirements we should meet before implementation is done."
- "Threat-model this new endpoint using the code, routes, permissions, data flows, and controls it touches."
- "A new admin export crosses customer data and support tools; trace trust boundaries and abuse cases before implementation."

### `identity-and-secrets`

- "Review the service-account identity, scope, and permission changes in this PR for access that is too broad."
- "Inspect how secrets are loaded in this repo and design credential rotation that will not break production."
- "Review workload identities, secret scopes, credential lifetime, break-glass access, and audit gaps in this repo."
- "The importer uses a shared token with write access everywhere; design narrower workload access and rotation."

### `cryptography-and-key-lifecycle`

- "Inventory certificates, keys, trust roots, owners, expiry dates, and renewal paths for this service."
- "Plan a certificate rotation that proves old and new trust paths work before the old certificate is removed."
- "Review this cryptographic algorithm transition for compatibility, monitoring, exceptions, and retirement gates."
- "The signing key has no owner and clients pin the old algorithm; plan compatibility and retirement gates."

### `software-supply-chain-security`

- "Review this repo's source-to-deploy chain for places an untrusted artifact could slip in."
- "Inspect the release scripts and show how artifact provenance, signing, and builder isolation prove where artifacts came from."
- "Find secret-scanning, dependency inventory, signing, provenance, or deployment-admission checks that should block release."
- "A deploy can pull artifacts from a mutable bucket; prove source, builder, signature, and admission controls."

### `vulnerability-management`

- "Triage the vulnerable dependencies in deployed artifacts and tell me what needs patching first by exploitability and exposure."
- "Review this PR that delays a security patch and define the vulnerability exception evidence, owner, and expiry it needs."
- "Map the current advisories to deployed services and propose remediation deadlines based on exploitability and impact."
- "An advisory affects a library used by two live services and one internal tool; set patch order and exception expiry."

### `tenant-isolation`

- "Review this multi-tenant customer data model and find ways one tenant could see another tenant's data."
- "Inspect the multi-tenant quota code and tell me whether one large tenant can hurt everyone else."
- "Use the access logs and tenant-context code path to prove whether this customer-impact incident stayed isolated to one tenant."
- "Support search can query multiple accounts; prove tenant context cannot be dropped on fallback paths."

### `privacy-and-data-lifecycle`

- "Review this feature's code for personal-data minimization, storage, deletion, export, and logging controls."
- "Inspect the telemetry changes and remove personal data that is not needed for privacy-safe operations."
- "Check the retention, erasure, and deletion-propagation jobs for this workflow and identify missing privacy controls."
- "Debug logs include email and free-form notes; decide what to drop, hash, retain, and erase."

### `engineering-control-evidence`

- "Turn the release checks in this repo into a cross-surface engineering evidence pack we can collect every release."
- "Build an evidence pack from the tests, CI, dashboards, runbooks, and review records."
- "Review these engineering exceptions and make sure each one has an owner, expiry, and compensating control."
- "For the release review, map CI, approvals, runbooks, and dashboards into one evidence pack with exceptions."

### `llm-application-security`

- "Review this LLM feature PR for prompt injection, unsafe tool access, and data leakage."
- "Inspect the LLM retrieval code and prove users cannot access documents they should not see."
- "Review the model output handling path for prompt-injected links, unsafe tool arguments, and data leakage before this feature ships."
- "The assistant can open retrieved docs and call tools; review where a malicious document could steer actions."

### `ai-coding-governance`

- "Review our repo instructions for AI coding agents and add rules for protected paths, tests, and data boundaries."
- "Define repo-level evidence requirements for AI-generated PRs before a human should approve them."
- "Define acceptance gates for agent-written code in this repo without replacing normal review."
- "Agents can edit generated schemas and fixtures; write repo rules for protected paths, tests, and review evidence."

### `llm-evaluation`

- "Design an eval harness for this prompt change with cases, graders, thresholds, and regression history."
- "Inspect these model-backed workflow evals and find where the scoring or slice coverage is weak."
- "Turn recent bad outputs into release-blocking eval cases with owners and failure triage."
- "A prompt tweak improved summaries but broke refund cases; build regression slices and a pass threshold."

### `llm-serving-cost-and-latency`

- "Set token and p50/p95/p99 latency budgets for this LLM-backed route and tell me which calls already blow them."
- "Design the prompt, embedding, and response cache strategy for this feature, and define when a cache miss has to fall back to a smaller model."
- "Map per-call LLM spend to route, feature, and tenant, then draft a degradation path for the next provider outage."
- "The support route fans out to three model calls; set latency and token budgets plus what degrades first."

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "Review this data model and migration before we split it across databases."
- "Trace this workflow across two services and the database, then show where correctness can break."
- "Inspect this cross-service lock and decide whether failover or replica lag can make it unsafe."
- "A tenant move may leave reads split across old and new shards; decide acceptable consistency and repair path."

### `event-workflows`

- "Review this event producer and consumer change for replay, failed messages, and duplicate events."
- "Inspect this event message change and find producer or consumer replay, ordering, idempotency, or DLQ behavior that might break."
- "Trace this multi-step workflow and show how partial failure could lose work."
- "A refund saga sends email before payment settles; trace partial failures and replay behavior."

### `caching-and-derived-data`

- "Review this cache invalidation code and tell me when users could see stale data."
- "Inspect this hot cache key and design protection so too many callers do not hit the backend at once."
- "Check the derived search-index refresh path and define stale-result freshness checks we can verify."
- "Inventory updates arrive but the product card stays stale; map invalidation order and cold-cache behavior."

### `database-operations`

- "Review this schema migration and backfill before it runs in production."
- "Inspect this index change and tell me how to avoid table locks or replica pain."
- "Review the query plan, index choice, and schema migration diff, then decide whether the database change needs rollback, throttling, or a new index."
- "Use the query plan and schema migration diff to find why this endpoint got slower after the database change."

### `data-pipeline-reliability`

- "Review this pipeline code for missed runs, freshness gaps, and unsafe reprocessing."
- "Inspect this stream change and design data-quality gates before downstream reports trust it."
- "Use the failed warehouse load logs and jobs to build a recovery plan that avoids double-counting."
- "Late-arriving events are replayed after dashboard cutoff; define freshness, validation, and no-double-count recovery."

### `ml-reliability-and-evaluation`

- "Review this model-serving PR for eval coverage, rollback, and production risk."
- "Inspect the training and serving code for places the model can get stale or behave differently in production."
- "The new model will replace the live fraud endpoint; define promotion evidence from evals, skew checks, drift monitors, rollback, tests, metrics, and deploy workflow."
- "The fraud model retrains weekly but features changed yesterday; compare training and serving inputs plus rollback evidence."

### `platform-golden-paths`

- "Inspect this repo's service template and make it a safer golden path for new production services."
- "Review the service catalog and scorecard files for what developers will actually use."
- "Find where teams bypass the platform in this repo and identify friction we should remove."
- "New services copy old templates then delete safety checks; update the template and scorecard to make the paved path easier."

### `infrastructure-and-policy-as-code`

- "Review this infrastructure change for unsafe manual steps, missing policy checks, and rollback gaps."
- "Inspect the environment promotion workflow and prove it matches what is declared in code."
- "Design policy checks and exception records for these infrastructure files."
- "A manual console change fixed staging; capture desired state, drift detection, and emergency exception rules."

### `internal-service-networking`

- "An internal service cannot reach one of its dependencies; inspect the repo config and help narrow down the path."
- "Review this internal traffic policy for service-to-service access that is too open."
- "Inspect internal service-to-service routing config and keep this private dependency's traffic local when possible."
- "Checkout sometimes exits the private network to reach payment; inspect discovery and locality rules."

### `edge-traffic-and-ddos-defense`

- "Review the public API rate limits and origin protection in this repo before launch."
- "Inspect the signup flow and edge rules for bot filters that will not block real users."
- "Design edge traffic shedding for this route using the current routing and deployment config."
- "Signup traffic spikes with suspicious user agents; set edge limits that protect origin without blocking real customers."

### `cost-aware-reliability`

- "Use the infra and service changes in this branch to find likely cost increases."
- "Review this capacity change and explain the reliability benefit versus the cost."
- "Inspect tags, owners, and shared resources so teams can act on their platform costs."
- "Replica count grew after an incident; decide what spend can be removed without losing failover headroom."

### `mobile-release-engineering`

- "Review this mobile release branch and define when staged rollout should pause."
- "Inspect startup, crash, hang, and offline telemetry before approving this app release."
- "Use the release notes and changed files to choose rollback or forward-fix options for this app-store bug."
- "Crash-free users dip only on older OS versions after staged rollout; decide pause, forward fix, or rollback."

### `web-release-gates`

- "Review this UI PR for loading, responsiveness, layout stability, runtime errors, and payload growth."
- "Inspect field and lab performance signals before rolling out this frontend change."
- "Add release gates and telemetry for this client-side change using the files in this repo."
- "The checkout bundle gained a heavy dependency; set gates for interaction readiness and runtime errors."

### `accessibility-gates`

- "Review this checkout flow for keyboard completion, focus order, labels, contrast, and release blockers."
- "Inspect this UI change and build the accessibility gate we need before launch."
- "Turn these accessibility bugs into journey-based regression checks with owners and retest dates."
- "A modal traps keyboard focus after payment failure; turn it into a release-blocking journey check."

### `experimentation-and-metric-guardrails`

- "Review this experiment design for assignment, exposure logging, guardrail metrics, and readout rules."
- "The A/B test result looks suspicious; inspect sample balance, missing telemetry, and metric definitions."
- "Decide whether this ramp should continue using experiment validity checks and operational guardrails."
- "The ramp looks positive but guardrail logging changed halfway through; decide whether the readout is trustworthy."
