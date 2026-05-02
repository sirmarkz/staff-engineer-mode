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
- "Find every caller of this response field and help me plan a safe deprecation."

### `architecture-decisions`

- "Read the current repo structure and design docs, then review whether this new service boundary makes sense."
- "Turn the decision in this PR into a short ADR with tradeoffs and revisit conditions."
- "Compare these two implementation branches and tell me which design is easier to operate and change later."

### `data-contracts`

- "Review this shared dataset change for producer and consumer compatibility before we merge."
- "Inspect the schema and downstream usage, then define the contract and removal gates for this field."
- "Find where teams depend on this data shape and build a migration plan that will not break consumers."

## Reliability And Resilience

### `slo-and-error-budgets`

- "Look at this service's routes, dashboards, and alerts, then propose user-centered SLIs and SLOs."
- "Review the alert rules in this repo and separate paging alerts from ticket-only alerts."
- "Use the service code and recent incidents to draft an error-budget policy for releases."

### `high-availability-design`

- "Inspect this deployment config and service topology for what still fails if one hosting location goes down."
- "Review the failover code path and runbook, then list the assumptions we still need to prove."
- "Trace the dependencies in this repo and identify where one failing component could take down the whole feature."

### `dependency-resilience`

- "Review this PR's new downstream call for timeout, retry, duplicate-work, and overload risks."
- "Trace this queue consumer and tell me how it behaves when the dependency gets slow."
- "Inspect the payment workflow code and find where retries could double-charge or duplicate work."

### `performance-and-capacity`

- "Use the changed files and benchmark output to explain why the slowest requests got worse."
- "Review this load-test script and tell me whether it proves enough headroom for the code path it exercises."
- "Trace the hot path for this endpoint and point out likely bottlenecks before traffic doubles."

### `backup-and-recovery`

- "Inspect the backup jobs and restore scripts in this repo and design a real restore test."
- "Review this migration and tell me how we would recover if it corrupts production data."
- "Read the DR runbook and deployment files, then call out assumptions that are not proven."

### `resilience-experiments`

- "Design a safe failure test for this dependency using the current service code and runbook."
- "Review the failover script and monitoring, then plan a game day that proves it works."
- "Look at this experiment PR and define stop conditions, impact limits, and rollback steps."

### `correctness-and-formal-methods`

- "Trace this stateful workflow and write the rules it must never break."
- "Review this locking code and tests for races, impossible states, or missed edge cases."
- "Design property tests or simulations for this money-moving code path."

## Delivery And Quality

### `testing-and-quality-gates`

- "Review this PR and tell me which tests should block merge and which can run after merge."
- "Inspect the CI config and test layout, then find weak signals that could let a bad release through."
- "Build a practical test plan for this feature using the code that changed in this branch."

### `configuration-and-automation-safety`

- "Review this config change for validation, preview, blast radius, and rollback before it runs."
- "Inspect this automation script and tell me how it can safely mutate production state."
- "Find configuration drift and temporary overrides that need owners, expiry, or removal."

### `release-build-reproducibility`

- "Review the build scripts and release workflow to see whether we can rebuild last week's artifact."
- "Inspect the packaging config and design a build-once, promote-many release path."
- "Find why this repo's builds are flaky or cache-sensitive and rank the fixes."

### `progressive-delivery`

- "Build a rollout and rollback plan for the config change in this PR."
- "Review this feature-toggle implementation and tell me what safety checks and cleanup are missing."
- "Use the deploy workflow and metrics files to define when we should stop a small first rollout."

### `production-readiness-review`

- "Run a production-readiness review for the service in this repo before launch."
- "Review this migration PR and identify blockers before we move traffic tomorrow."
- "Inspect the code, deploy config, dashboards, and runbooks, then say what evidence is missing for launch."

### `migration-and-deprecation`

- "Find every caller of this old module and plan a safe migration across the repo."
- "Review the deprecation PR and tell me how to prevent new usage from being added."
- "Inspect this service retirement plan against the codebase and identify anything that could strand users or teams."

### `fleet-upgrades`

- "Build an upgrade plan for this runtime across all services, including support windows and allowed version skew."
- "Review this platform upgrade and identify mixed-version combinations we need to prove before rollout."
- "Inspect the fleet inventory and find unsupported versions, owners, exceptions, and cleanup gates."

### `code-review-and-workflow`

- "Review this large PR and suggest how to split it without losing review context."
- "Inspect ownership files and recent changes to find why reviews are slow."
- "Look at this shared repo and propose ownership boundaries that match how the code actually changes."

### `documentation-lifecycle`

- "Audit these runbooks and design docs for owner, source of truth, freshness, and archive rules."
- "Inspect the docs touched by this release and identify stale or missing operational guidance."
- "Turn this undocumented maintenance workflow into a lifecycle-managed runbook with review triggers."

### `dependency-and-code-hygiene`

- "Find all uses of this deprecated library and plan a safe removal across the repo."
- "Review the dependency update PR for lockfile, migration, and rollback risks."
- "Inspect the static-analysis backlog and changed files, then prioritize fixes that reduce real maintenance risk."

## Operations And Observability

### `observability-and-alerting`

- "Inspect this payment flow and propose the logs, metrics, traces, dashboards, alerts, and runbook updates it needs."
- "Review the alert definitions in this repo and find alerts that wake people up without user impact."
- "Trace this request across services and tell me what correlation context is missing."

### `incident-response-and-postmortems`

- "Use these logs, commits, and incident notes to build a clear timeline and follow-up list."
- "An incident is in progress; use these symptoms and recent commits to help set severity, roles, updates, and next decisions."
- "Review this postmortem draft and mark follow-up actions that are too vague to verify in the repo."

### `oncall-health`

- "Review the alert history and runbooks in this repo, then find the noisiest safe pages to remove."
- "Inspect these weekly operations notes and identify toil that can be automated or eliminated."
- "Review these suppression rules and prove we are not hiding real user impact."

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "Review this customer data export PR for abuse cases, authorization gaps, and unsafe inputs."
- "Inspect the changed files and write security requirements we should meet before implementation is done."
- "Threat-model this new endpoint using the code, routes, permissions, and data it touches."

### `identity-and-secrets`

- "Review the service-account and permission changes in this PR for access that is too broad."
- "Inspect how secrets are loaded in this repo and design rotation that will not break production."
- "Review the encryption and key-management code path and call out risky assumptions."

### `crypto-lifecycle`

- "Inventory certificates, keys, trust roots, owners, expiry dates, and renewal paths for this service."
- "Plan a certificate rotation that proves old and new clients work before the old path is removed."
- "Review this algorithm transition for compatibility, monitoring, exceptions, and retirement gates."

### `software-supply-chain-security`

- "Review this repo's build and deploy workflow for places an untrusted artifact could slip in."
- "Inspect the release scripts and show how we can prove where artifacts came from."
- "Find secret-scanning, dependency, signing, or provenance checks that should block release."

### `vulnerability-management`

- "Triage the vulnerable dependencies in this repo and tell me what needs patching first."
- "Review this PR that delays a security patch and define the evidence, owner, and expiry it needs."
- "Map the current advisories to deployed services and propose patch deadlines based on exploitability and impact."

### `tenant-isolation`

- "Review this shared customer data model and find ways one customer could see another customer's data."
- "Inspect the quota code and tell me whether one large customer can hurt everyone else."
- "Use the access logs and code path to prove whether this customer-impact incident stayed isolated."

### `privacy-and-data-lifecycle`

- "Review this feature's code for how it stores, deletes, exports, and logs user data."
- "Inspect the telemetry changes and remove personal data that is not needed."
- "Check the retention and deletion jobs for this workflow and identify missing controls."

### `engineering-control-evidence`

- "Turn the release checks in this repo into evidence we can collect every release."
- "Build an evidence pack from the tests, CI, dashboards, runbooks, and review records."
- "Review these engineering exceptions and make sure each one has an owner, expiry, and compensating control."

### `llm-application-security`

- "Review this LLM feature PR for prompt injection, unsafe tool access, and data leakage."
- "Inspect the retrieval code and prove users cannot access documents they should not see."
- "Design evals that would catch insecure model output before this feature ships."

### `ai-coding-governance`

- "Review our repo instructions for coding agents and add rules for protected paths, tests, and data boundaries."
- "Inspect this AI-generated PR and tell me what evidence is missing before a human should approve it."
- "Define acceptance gates for agent-written code in this repo without replacing normal review."

### `llm-evaluation`

- "Design an eval harness for this prompt change with cases, graders, thresholds, and regression history."
- "Inspect these model-backed workflow evals and find where the scoring or slice coverage is weak."
- "Turn recent bad outputs into release-blocking eval cases with owners and failure triage."

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "Review this data model and migration before we split it across databases."
- "Trace this workflow across two services and the database, then show where correctness can break."
- "Inspect this cross-service lock and decide whether it is safe enough for this code path."

### `event-workflows`

- "Review this event producer and consumer change for replay, failed messages, and duplicate events."
- "Inspect this message schema change and find consumers that might break."
- "Trace this multi-step workflow and show how partial failure could lose work."

### `caching-and-derived-data`

- "Review this cache invalidation code and tell me when users could see stale data."
- "Inspect this hot cache key and design protection so too many callers do not hit the backend at once."
- "Check the search-index refresh path and define freshness checks we can verify."

### `database-operations`

- "Review this schema migration and backfill before it runs in production."
- "Inspect this index change and tell me how to avoid table locks or replica pain."
- "Use the query and migration diff to find why this endpoint got slower after the database change."

### `data-pipeline-reliability`

- "Review this pipeline code for missed runs, freshness gaps, and unsafe reprocessing."
- "Inspect this stream change and design data-quality gates before downstream reports trust it."
- "Use the failed warehouse load logs and jobs to build a recovery plan that avoids double-counting."

### `ml-reliability-and-evaluation`

- "Review this model-serving PR for eval coverage, rollback, and production risk."
- "Inspect the training and serving code for places the model can get stale or behave differently in production."
- "Define production-readiness evidence for this ML endpoint using the repo's tests, metrics, and deploy workflow."

### `platform-golden-paths`

- "Inspect this repo's service template and make it a safer golden path for new production services."
- "Review the service catalog and scorecard files for what developers will actually use."
- "Find where teams bypass the platform in this repo and identify friction we should remove."

### `infrastructure-and-policy-as-code`

- "Review this infrastructure change for unsafe manual steps, missing policy checks, and rollback gaps."
- "Inspect the environment promotion workflow and prove it matches what is declared in code."
- "Design policy checks and exception records for these infrastructure files."

### `internal-service-networking`

- "An internal service cannot reach one of its dependencies; inspect the repo config and help narrow down the path."
- "Review this internal traffic policy for service-to-service access that is too open."
- "Inspect routing config and keep this private dependency local when possible."

### `edge-traffic-and-ddos-defense`

- "Review the public API rate limits and origin protection in this repo before launch."
- "Inspect the signup flow and edge rules for bot filters that will not block real users."
- "Design edge traffic shedding for this route using the current routing and deployment config."

### `cost-aware-reliability`

- "Use the infra and service changes in this branch to find likely cost increases."
- "Review this capacity change and explain the reliability benefit versus the cost."
- "Inspect tags, owners, and shared resources so teams can act on their platform costs."

### `mobile-release-engineering`

- "Review this mobile release branch and define when staged rollout should pause."
- "Inspect startup, crash, hang, and offline telemetry before approving this app release."
- "Use the release notes and changed files to choose rollback or forward-fix options for this app-store bug."

### `web-release-gates`

- "Review this UI PR for loading, responsiveness, layout stability, runtime errors, and payload growth."
- "Inspect field and lab performance signals before rolling out this frontend change."
- "Add release gates and telemetry for this client-side change using the files in this repo."

### `accessibility-gates`

- "Review this checkout flow for keyboard completion, focus order, labels, contrast, and release blockers."
- "Inspect this UI change and build the accessibility gate we need before launch."
- "Turn these accessibility bugs into journey-based regression checks with owners and retest dates."

### `experimentation-and-metric-guardrails`

- "Review this experiment design for assignment, exposure logging, guardrail metrics, and readout rules."
- "The A/B test result looks suspicious; inspect sample balance, missing telemetry, and metric definitions."
- "Decide whether this ramp should continue using experiment validity checks and operational guardrails."
