# Expected Route Demo Prompts

These are demo prompts for Staff Engineer Mode's expected-route eval catalog.
They are grouped by specialist file to show the kinds of repository work the
router should understand.

Use them as examples when adapting prompts to a real repo, PR, branch, or
workspace with concrete paths, files, migrations, logs, alerts, runbooks, or
diffs.

## Architecture And Interfaces

### `api-design-and-compatibility`

- "Inspect the API changes in this branch and tell me what could break existing clients."
- "Design the new partner API before implementation: resource names, operation shapes, errors, idempotency, and future compatibility."
- "The mobile SDK and a partner integration both read this response field; check whether changing it stays compatible and define the client rollout."
- "Several SDKs and partner clients still parse this response field; check compatibility before changing its type or semantics."
- "A generated client treats missing fields differently from null fields; review the response change and define how old clients keep working."

### `architecture-decisions`

- "Read the current repo structure and design docs, then decide whether this new service boundary makes sense."
- "Turn the decision in this PR into a short ADR with tradeoffs and revisit conditions."
- "Compare these two proposed service-boundary designs and tell me which is easier to operate and change later."
- "Map the current background jobs and request paths, then recommend whether the new worker boundary should own retries or leave them with callers."
- "The team wants one owner for checkout reconciliation; compare keeping it in the API service versus a separate worker with decision criteria."

### `data-contracts`

- "Design the new shared customer dataset before launch: producer, planned consumers, field meanings, compatibility rules, and consumer checks."
- "Define the producer and consumer contract for this shared schema field, including compatibility and deprecation rules."
- "Inspect this existing shared data shape and define producer/consumer compatibility rules before changing it."
- "A reporting table adds nullable columns and changes enum meanings; check producer and consumer expectations before publishing it."
- "A domain event gains a nested address payload; define producer guarantees, consumer rollout checks, and what values may be omitted."

### `resilience-requirements`

- "Before we build the new payouts feature, write its resiliency contract: failure behavior per dependency, non-functional targets, and testable acceptance criteria."
- "Inspect this feature spec and tell me which failure behaviors and non-functional targets it leaves undefined."
- "Trace this design back to its requirements and find the dependency failures and malformed-input cases nobody specified."
- "The spec covers the happy path only; define what the feature should do when the inventory service is down or returns garbage."
- "We keep shipping features that break on edge cases; turn this request into acceptance criteria a test can check for partial failure and bad input."

### `persistent-connection-systems`

- "Design the connection protocol for this new live-updates feature: heartbeat, reconnect with resume, slow-consumer backpressure, and drain on deploy."
- "Inspect this streaming endpoint for reconnect storms after deploy and unbounded buffers on slow clients."
- "Test what happens to live sessions during a rolling release, then define the connection-drain and reconnect-rate plan."
- "A network blip reconnects every client at once and overwhelms the backend; add backoff with jitter and a resume cursor."
- "Slow mobile clients grow server memory until workers restart; define per-connection backpressure and overflow behavior before launch."

## Reliability And Resilience

### `slo-and-error-budgets`

- "Design SLIs and SLOs for the new checkout API before launch using its user journeys and expected traffic."
- "Inspect this service's SLO burn-rate rules and separate urgent alerts from follow-up-only budget responses."
- "Use the service code and recent incidents to draft error-budget release rules."
- "Checkout has fast failures and slow successes; decide which user outcome should burn budget and which alerts should stay non-urgent follow-ups."
- "A service is meeting latency charts but users abandon retries; define the reliability target and release policy around that outcome."

### `high-availability-design`

- "Review a deployment topology and identify what would still fail if one hosting location went down."
- "Inspect the failover code path, static capacity, and runbook, then list the availability assumptions we still need to check."
- "Trace the serving path and fault-domain map, then identify which shared dependency or control-plane loss could break high availability for the whole feature."
- "During a zone evacuation, this feature still needs reads and writes; inspect which components share a failover dependency."
- "The control plane can only run in one location; map whether steady-state capacity survives losing that location."

### `dependency-resilience`

- "Before adding this new downstream call, define timeout, retry, duplicate-work, and overload behavior."
- "Trace this existing queue consumer and tell me how it behaves when the dependency gets slow."
- "Inspect this downstream payment dependency call and find where retries could double-charge or duplicate work."
- "A checkout worker has retries, a queue, and a fallback; verify overload behavior when its dependency stalls."
- "A fraud check sometimes takes five seconds; set caller behavior for timeout, fallback, duplicate requests, and overload."

### `performance-and-capacity`

- "Set capacity and load-test targets for a new checkout endpoint before traffic ramps."
- "Inspect this load-test script and tell me whether it shows enough headroom for the code path it exercises."
- "Trace the hot path for this endpoint and point out likely bottlenecks before traffic doubles."
- "P99 doubled only for large tenants after the merge; use traces and profiles to find the saturation point."
- "Traffic will triple during enrollment week; choose load scenarios, headroom targets, and bottleneck probes before the event."

### `backup-and-recovery`

- "Inspect the backup jobs and restore scripts in this repo, then design an RTO/RPO restore test."
- "Inspect this migration and tell me how we would recover from production data corruption or accidental deletion."
- "Read the disaster-recovery runbook and backup files, then call out restore assumptions that still need a test."
- "Before deleting old records, verify we can restore a tenant snapshot and reconcile writes made during recovery."
- "A bulk import may overwrite historical records; define the restore rehearsal and reconciliation evidence before it runs."

### `resilience-experiments`

- "Design a safe fault-injection test for this dependency with blast-radius limits, abort criteria, telemetry, and rollback."
- "Inspect the failover script and monitoring, then plan a game day with blast-radius limits and abort criteria."
- "Look at this chaos-test PR and define stop conditions, impact limits, learning goals, and rollback steps."
- "Plan a drill where the queue broker returns errors for ten minutes, with who can abort and what blast radius is allowed."
- "Inject packet loss into one internal dependency during a limited window and define abort signals, observers, and learning goals."

### `state-machine-correctness`

- "Design the new payout state machine before implementation: states, transitions, must-never rules, must-eventually rules, and retry cases."
- "Inspect this existing locking code and tests for races, impossible states, or missed concurrency edges."
- "Design property tests or simulations for this high-stakes money-moving state machine."
- "The order can move from paid to canceled during retry races; enumerate invalid transitions and how to test them."
- "Subscriptions can pause, resume, cancel, and renew on the same invoice cycle; enumerate forbidden transitions and eventual outcomes."

### `scheduled-job-reliability`

- "Design the nightly invoice job before launch: idempotent run windows, overlap control, missed-run detection, deadline, and catch-up behavior."
- "Inspect this cron worker and run history for skipped windows, double-fires, stuck runs, and missing completion evidence."
- "The hourly entitlement sync can run longer than its interval; define singleton locking, overrun behavior, and rate-bounded catch-up."
- "Test the billing export through daylight-saving transitions so the scheduled run cannot skip or double-process a window."
- "A monthly settlement job silently missed one run and the next retry may duplicate payouts; set the completion signal, alert, and recovery plan."

### `multi-region-and-data-residency`

- "Design the multi-region program for this service: topology, residency placement, replication-aware routing, and an evacuation runbook, before we expand to a second region."
- "Inspect this two-region setup for residency rules that are documented but not enforced in placement or routing."
- "Trace how a user request pins to a region and what happens to reads and writes during a region evacuation."
- "Regulated records can land in either region during failover; map data classes to permitted geographies and define the compliant fallback."
- "We claim active-active without region-loss rehearsal evidence; write the drain, traffic-shift, and cutover runbook and the abort signals."

## Delivery And Quality

### `testing-and-quality-gates`

- "Design the test strategy for this payment workflow change: what blocks merge, what blocks release, and what can run later."
- "Inspect the CI config and test layout, then find weak signals that could let a bad release through."
- "Build a practical test plan for this feature area: name the merge blockers, release blockers, nightly checks, and weak signals."
- "The feature touches auth, billing, and background jobs; decide the minimal blocking test set and what can run nightly."
- "A hotfix skipped two suites last time; decide which checks must block merge versus release for this risky path."

### `test-data-engineering`

- "Design a test-data inventory for this suite: fixture purpose, regeneration path, ownership, and unreproducible data."
- "Design fixture and golden-file rules for this new integration test suite before it starts using production samples."
- "Find where production data shape has drifted from the data the tests run on and design a drift-detection check."
- "These fixtures came from support exports; check whether they are still representative and safe to keep."
- "The contract tests use hand-written orders that never match holiday traffic; plan representative fixtures and regeneration rules."

### `configuration-and-automation-safety`

- "Design validation, preview, blast-radius limits, and rollback rules for a new tenant-limit config setting before automation writes it."
- "Inspect this automation script and tell me how it can safely mutate production state with an abort path."
- "Find unsafe runtime config values and temporary overrides before the cleanup automation runs, then add owners, expiry, validation, and rollback."
- "A script will rewrite tenant limits from a CSV; add preview, validation, per-tenant caps, and rollback."
- "An ops job will disable dormant accounts from a query result; require dry run output, approval thresholds, rollback, and audit trail."

### `release-build-reproducibility`

- "Define build reproducibility checks for version consistency, artifact identity, required checks, promotion path, and rollback target."
- "Inspect the packaging config and design a build-once, promote-many release path."
- "Trace why identical release-tag inputs produce cache-sensitive package hashes and rank the artifact reproducibility fixes."
- "Two CI runners produce different package hashes; trace the unpinned inputs before the release is promoted."
- "The tag, package metadata, and deployed artifact disagree; trace the version line and define promotion evidence."

### `dev-environment-parity`

- "Build a parity matrix across local, CI, staging, and production for this service and find the divergences the config, docs, or runbooks do not name."
- "This fix worked locally and failed in CI; trace the environment dimensions that differ and tell me which one hid the bug."
- "Define a drift budget for these environments with action triggers, allowed divergence, and required parity."
- "Staging uses seeded tenants while local uses mocks; find which environment gap hid this serialization bug."
- "Only production has the compression setting that triggers this bug; map the drift across environments and close the gap."

### `progressive-delivery`

- "Build a rollout and rollback plan for the new ranking path before production exposure."
- "This rollout plan has canary metrics but no rollback target; review the stop criteria before exposure."
- "Define first-rollout stop criteria from deploy workflow signals and canary metrics, including minimum signal, thresholds, owner, abort, and rollback."
- "Ramp the new ranking path by tenant cohort and define metrics that pause exposure before all users see it."
- "The search rewrite should reach only low-risk cohorts first; define ramp steps, stop metrics, and rollback ownership."

### `feature-flag-lifecycle`

- "Before adding a new feature flag, define owner, expiry, fallback behavior, and the removal plan."
- "Find orphan flags whose feature shipped or whose owner left, and propose a safe removal sequence."
- "Inspect this flag-debt scorecard and tell me which flags will become contradictory defaults if we leave them in."
- "This flag now defaults on in every environment; find remaining off-path code and plan removal safely."
- "A temporary kill switch now controls three code paths; set ownership, default state, expiry, and cleanup after launch."

### `production-readiness-review`

- "Build a production-readiness decision for the new service in this repo before launch."
- "Before this migration moves traffic tomorrow, inspect code, deploy config, dashboards, and runbooks for launch blockers."
- "Review this production-readiness packet and identify stale launch evidence before the go/no-go call."
- "Before the new importer becomes high impact, collect blockers across code, deploy, telemetry, and support docs."
- "Leadership wants to launch Friday; inspect the readiness packet for blockers across dependencies, support handoff, telemetry, and rollback."

### `migration-and-deprecation`

- "Find every caller of this old module and plan a safe migration across the repo."
- "Inspect the deprecation PR and tell me how to prevent new usage from being added."
- "Inspect this consumer migration plan before teardown and identify hidden callers, no-new-usage gaps, or teams that could be stranded."
- "The legacy invoice worker still has hidden cron callers; build batches to move them and block new usage."
- "A replacement library exists, but new code still imports the old one; plan batches, no-new-usage checks, and final removal."

### `fleet-upgrades`

- "Build an upgrade plan for this runtime across all services, including support windows and allowed version skew."
- "Inspect this platform upgrade and identify mixed-version combinations we need to test before rollout."
- "Inspect the existing fleet inventory and find unsupported versions, owners, exceptions, and cleanup checks."
- "During this runtime fleet upgrade, some services cannot move until clients update; plan version-skew windows and exceptions."
- "Some workers will run the new runtime while callers stay old for weeks; define skew tests, support windows, and exception handling."

### `service-decommission-and-sunset`

- "Plan the full teardown of this retired service: zero-traffic proof, data disposition under retention and legal hold, credential and DNS reclamation, and a no-resurrection record."
- "Inspect this retirement plan for dangling DNS names, orphaned credentials, and data deleted while under legal hold."
- "Trace what this service still owns: names, certs, credentials, alarms, and held data, then order the teardown so nothing is stranded."
- "Before release of the teardown automation, verify the old service has zero traffic and no remaining consumers."
- "As part of terminal service teardown, retirement wants to purge all records, but some are under a legal hold; define disposition per data class with hold-driven suspension."

### `agent-pr-review`

- "Before committing the staged changes, review the exact diff for intent match, behavior verification, and missing edge cases."
- "Find risks in the diff I'm about to push: silent assumptions, hallucinated APIs, scope creep, deleted-but-used code."
- "What did the agent (or I) miss in this branch that we'd be embarrassed to ship?"
- "The diff passes tests but changed deletion behavior; review what details are missing before merge."
- "Before I merge this branch, check whether the diff still matches the request and whether test evidence covers the changed behavior."

### `code-readability-for-agents`

- "Design module boundaries and names for a new payment workflow so an AI agent can find the canonical implementation in one tool call."
- "Find names in this codebase that collide or mislead code search and propose renames that make the canonical version unambiguous."
- "Inspect function and file sizes against a budget and tell me which files an agent will silently misread."
- "There are three payment clients with similar names; find the canonical one and where an agent could choose wrong."
- "An agent keeps editing the legacy billing helper; rename or restructure paths so the intended implementation is obvious from search."

### `documentation-lifecycle`

- "Map these runbooks and dashboard definitions for owner, source of truth, freshness, and staleness."
- "Inspect the docs touched by this release and identify stale or missing operational guidance."
- "Turn this undocumented maintenance workflow into a lifecycle-managed runbook with source of truth, owner, freshness rule, and change triggers."
- "The failover runbook points to old dashboards; set owner, expiry, and freshness trigger so it stays current."
- "A maintenance guide is accurate today but lacks an owner or stale-signal; set source-of-truth and refresh triggers."

### `dependency-and-code-hygiene`

- "Find all uses of this deprecated dependency and plan a small-batch hygiene cleanup with lockfile and codemod safety checks."
- "Plan this dependency update and lockfile sweep for migration, hygiene, and rollback risks."
- "Inspect the static-analysis backlog and changed files, then prioritize fixes that reduce real maintenance risk."
- "Triage the static-analysis warning on a deprecated helper across five packages, then plan small hygiene cleanup batches with codemod safety checks."
- "A dead utility remains in three packages after the refactor; plan a small cleanup with usage checks and rollback notes."

## Operations And Observability

### `observability-and-alerting`

- "Design logs, metrics, traces, dashboards, alerts, and runbook updates for a new payment flow before launch."
- "Inspect the alert definitions in this repo and map each one to user-journey telemetry, dashboard context, and a runbook."
- "Trace this request across services and tell me what correlation context is missing."
- "Users report missing receipts but dashboards only show worker CPU; design signals that show where work disappears."
- "A background job silently skips invoices; design the signal, dashboard context, alert route, and runbook link that would expose it."

### `incident-response-and-postmortems`

- "Use these logs, commits, and incident notes to build a clear timeline and follow-up list."
- "An incident is in progress; use these symptoms and recent commits to help set severity, roles, updates, and next decisions."
- "Inspect this postmortem draft and mark follow-up actions that are too vague to verify in the repo."
- "Checkout errors spiked after a deploy twenty minutes ago; build the timeline, owners, and next update."
- "Mitigation is underway and symptoms keep changing; build the current timeline, decision log, roles, and next update."

### `oncall-health`

- "We get paged all night for this service; cut the noise without missing real incidents."
- "Inspect these on-call suppression rules and verify page-noise reduction is not hiding real user impact."
- "This alert fires every week and the runbook says to rerun a job manually; decide what engineering fix should replace that manual step."
- "Find which alerts should page, which should become follow-ups, and which should be deleted or grouped."
- "Responders page themselves on a warning every morning; decide whether to automate, downgrade, group, or delete the alert."

### `operational-ownership-transfer`

- "Design the ownership-transfer gate for moving this service to another team: bus-factor inventory, runbook executability, deploy and rollback dry-run, and paging transfer."
- "Inspect this handoff plan and tell me whether the receiving team can run and change the system or only inherits the docs."
- "Trace what only one engineer knows about operating this system and turn it into runbooks the receiving team can execute."
- "Test the receiving team's failover and rollback dry-run before the transfer is accepted."
- "After the transfer, pages still route to the old team and the new team has no failover dry-run; define the verification that fixes both."

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "Threat-model this customer data export PR for abuse cases, authorization gaps, unsafe inputs, and residual risk."
- "Inspect the changed files and write trust-boundary and data-flow security requirements we should meet before implementation is done."
- "Threat-model this new endpoint using the code, routes, permissions, data flows, and controls it touches."
- "A new admin export crosses customer data and support tools; trace trust boundaries and abuse cases before implementation."
- "Before the partner upload feature ships, map trust boundaries, abuse cases, unsafe inputs, and required controls."

### `input-validation-and-injection-defense`

- "Design the input-handling defense for this new search endpoint before implementation: which untrusted fields reach which sinks, boundary validation, and the parameterization or encoding each sink needs."
- "Inspect this branch for sinks that build queries, commands, markup, file paths, or deserialized objects from request data, and tell me which ones are not parameterized or context-encoded."
- "Trace how the uploaded-document import flows into the template renderer and the report query, then define the per-sink controls and a negative test for each."
- "Search results render user-submitted names that show up unescaped in the page; map the output contexts and define the encoding each one needs."
- "A reporting filter concatenates a request parameter into the database query; rewrite the data path to parameterize it and add a malicious-input test that proves it is neutralized."

### `client-application-security`

- "Inspect this mobile client for secrets in the binary, plaintext token storage, unsafe deep links, web-view bridges, and server-side enforcement gaps."
- "Design client-side security for a browser checkout flow: trusted sinks, local storage classification, transport trust, and tamper assumptions."
- "A custom URL scheme opens account pages from external apps; define validation, authorization, and negative tests for malicious deep-link parameters."
- "Before release, check whether the client can enforce pricing or limits locally and prove the server rejects tampered requests."
- "Test a browser route that renders partner content into the DOM and caches customer data locally; set sink defenses and storage rules."

### `identity-and-secrets`

- "Inspect the service-account identity, scope, and permission changes in this PR for access that is too broad."
- "Inspect how secrets are loaded in this repo and design credential rotation that will not break production."
- "Inspect workload identities, secret scopes, credential lifetime, break-glass access, and traceability gaps in this repo."
- "The importer uses a shared token with write access everywhere; design narrower workload access and rotation."
- "A batch job needs temporary write access for launch; define scoped identity, rotation, traceability, and emergency access cleanup."

### `cryptography-and-key-lifecycle`

- "Inventory existing certificates, keys, trust roots, owners, expiry dates, and renewal paths for this service."
- "Plan a certificate rotation that shows old and new trust paths work before the old certificate is removed."
- "Inspect this cryptographic algorithm transition for compatibility, monitoring, exceptions, and retirement checks."
- "The signing key has no owner and clients pin the old algorithm; plan compatibility and retirement checks."
- "The certificate chain will change for old clients; plan trust validation, overlap, expiry ownership, and rollback."

### `software-supply-chain-security`

- "Inspect the existing source-to-deploy chain for places an untrusted artifact could slip in."
- "Inspect the release scripts and show how artifact provenance, signing, and builder isolation identify where artifacts came from."
- "Find secret-scanning, dependency inventory, signing, provenance, or deployment-admission checks that should block release."
- "A deploy can pull artifacts from a mutable bucket; verify source, builder, signature, and admission controls."
- "A release uses third-party generated artifacts; verify source lineage, isolated build path, signatures, and admission checks."

### `vulnerability-management`

- "Before promoting this new image, triage its vulnerable packages by exploitability, exposure, patch path, and exception expiry."
- "Inspect this PR that delays a security patch and define the vulnerability exception details, owner, and expiry it needs."
- "Map the current advisories to deployed services and propose remediation deadlines based on exploitability and impact."
- "An advisory affects a library used by two live services and one internal tool; set patch order and exception expiry."
- "A patched package is available but production exposure differs by service; rank remediation, exceptions, and verification evidence."

### `tenant-isolation`

- "Design tenant-isolation checks for a new support search feature that can query customer accounts."
- "Inspect the multi-tenant quota code and tell me whether one large tenant can hurt other tenants."
- "Use the access logs and tenant-context code path to check whether support search stayed isolated to one tenant."
- "Support search can query multiple accounts; verify tenant context cannot be dropped on fallback paths."
- "A shared export queue can process records from several customers; prove context cannot bleed between jobs or retries."

### `privacy-and-data-lifecycle`

- "Design the personal-data flow for this new feature: minimization, storage, deletion, export, and logging controls."
- "Inspect the telemetry changes and remove personal data that is not needed for privacy-safe operations."
- "Check the retention, erasure, and deletion-propagation jobs for this workflow and identify missing privacy controls."
- "Debug logs include email and free-form notes; decide what to drop, hash, retain, and erase."
- "Support transcripts are now searchable; decide retention, deletion propagation, minimization, and logging controls."

### `engineering-control-evidence`

- "Turn the release checks in this repo into a cross-surface engineering record pack we can collect every release."
- "Build a control record pack from the tests, CI, dashboards, runbooks, and change records."
- "Inspect these engineering exceptions and make sure each one has an owner, expiry, and compensating control."
- "For the release record pack, map CI, approvals, runbooks, and dashboards into one control record set with exceptions."
- "Create one release evidence set that ties tests, approvals, dashboards, exceptions, and runbook checks to owners."

### `llm-application-security`

- "Threat-model a new LLM assistant before launch for prompt injection, unsafe tool access, and data leakage."
- "Inspect the LLM retrieval and tool boundary for prompt injection, unsafe document access, and data leakage."
- "Inspect the model output handling path for prompt-injected links, unsafe tool arguments, and data leakage before this feature ships."
- "The assistant can open retrieved docs and call tools; identify where a malicious document could steer actions."
- "A retrieved policy page can tell the assistant to call tools; test injection paths, data leakage, and unsafe arguments."

### `ai-coding-governance`

- "Inspect our repo instructions for AI coding agents and add rules for protected paths, tests, and data boundaries."
- "Design repo-level verification requirements for AI-generated PRs before a human should approve them."
- "Define acceptance checks for agent-written code in this repo without replacing normal change responsibility."
- "Agents can edit generated schemas and fixtures; write repo rules for protected paths, tests, and traceability details."
- "Define what generated code may change in protected schema files and which verification receipts reviewers must see."

### `llm-evaluation`

- "Design an eval harness for this prompt change with cases, graders, thresholds, and regression history."
- "For this retrieval-grounded answer flow, design eval cases for retrieval fit, cited-context use, answer correctness, slice thresholds, and regression history."
- "Design agentic adversarial evals: white-box architect defines risk slices; black-box/gray-box author gets no expected traces, reference solutions, implementation notes, happy-path examples, or route rationales; white-box reviewer validates coverage."
- "A prompt tweak improved summaries but broke refund cases; build regression slices and a pass threshold."
- "The support agent now reads order status and proposes cancellations; add task-run evals with tool-call trace checks, final-state assertions, repeated runs, and failure triage."

### `llm-serving-cost-and-latency`

- "Set token and p50/p95/p99 latency budgets for a new LLM-backed route before launch."
- "Design the prompt, embedding, and response cache strategy for this feature, and define when a cache miss has to fall back to a smaller model."
- "Map existing per-call LLM spend to route, feature, and tenant, then draft a degradation path for the next provider outage."
- "The support route fans out to three model calls; set latency and token budgets plus what degrades first."
- "A chat endpoint streams slowly during peak usage; set per-call budget, cache rules, tail-latency threshold, and degradation order."

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "Inspect this data model and migration before we split it across databases."
- "Trace this workflow across two services and the database, then show where correctness can break."
- "Inspect this cross-service lock and decide whether failover or replica lag can make it unsafe."
- "A tenant move may leave reads split across old and new shards; decide acceptable consistency and repair path."
- "Writes move from one shard to another while reads can hit either side; define conflict handling and repair checks."

### `event-workflows`

- "Design a new refund event workflow with replay, failed-message handling, duplicate handling, ordering, and DLQ behavior."
- "Inspect this event message change and find producer or consumer replay, ordering, idempotency, or DLQ behavior that might break."
- "Trace this event-driven workflow across producers, consumers, replay, and failed-message handling; show where partial failure could lose work."
- "A refund saga sends email before payment settles; trace partial failures and replay behavior."
- "A shipment event can be redelivered after the email consumer has already sent mail; define idempotency, replay, and poison-message handling."

### `caching-and-derived-data`

- "Design a new product-card cache with TTL, invalidation, miss-storm behavior, and stale-result handling."
- "Inspect this hot cache key and design protection so too many callers do not hit the backend at once."
- "Check the derived search-index refresh path and define stale-result freshness checks we can verify."
- "Inventory updates arrive but the product card stays stale; map invalidation order and cold-cache behavior."
- "The recommendation index lags source updates by minutes; set freshness checks, invalidation order, and stale-result behavior."

### `database-operations`

- "Inspect this schema migration and backfill before it runs in production."
- "Inspect this index change and tell me how to avoid table locks or replica pain."
- "Inspect the query plan, index choice, and schema migration diff, then decide whether the database change needs rollback, throttling, or a new index."
- "Use the query plan and schema migration diff to find why this endpoint got slower after the database change."
- "A backfill touches every account row while live writes continue; define lock limits, throttling, query-plan checks, and rollback."

### `data-pipeline-reliability`

- "Design the new revenue pipeline before launch: freshness targets, validation checks, lineage, replay, and recovery."
- "Inspect this stream change and design data-quality checks before downstream reports trust it."
- "Use the failed warehouse load logs and jobs to build a recovery plan that avoids double-counting."
- "Late-arriving events are replayed after dashboard cutoff; define freshness, validation, and no-double-count recovery."
- "The monthly metrics job missed a partition and rerun may double-count; define lineage, validation, replay, and freshness evidence."

### `data-lineage-and-provenance`

- "Design the lineage spine for our regulated revenue figures: source-of-record, derivation chain, downstream dependency graph, and recompute impact analysis."
- "Inspect this reporting pipeline for figures with no designated authoritative source and lineage that stops at a system boundary."
- "Trace where this dashboard number comes from end to end and tell me what must be recomputed if the upstream source was wrong."
- "An auditor asks how this regulated metric was produced; build the lineage record from the figure back to its authoritative source."
- "Test the restatement path after a bad upstream feed corrupted a source table; map the blast radius across the derived datasets, reports, and models."

### `ml-reliability-and-evaluation`

- "Define eval coverage, rollback, and production-risk checks for this model-serving change."
- "Inspect the training and serving code for places the model can get stale or behave differently in production."
- "The new model will replace the live fraud endpoint; define promotion checks from evals, skew checks, drift monitors, rollback, tests, metrics, and deploy workflow."
- "The fraud model retrains weekly but features changed yesterday; compare training and serving inputs plus rollback checks."
- "A ranking model trained on old labels is ready for promotion; check skew, drift, offline evals, live monitors, and rollback."

### `platform-golden-paths`

- "Inspect this repo's service template and make it a safer golden path for new production services."
- "Inspect the service catalog and template docs for friction teams hit when starting new services."
- "Find where teams bypass the platform in this repo and identify friction we should remove."
- "New services copy old templates then delete safety checks; update the template and scorecard to make the paved path easier."
- "Teams keep deleting health checks from the service template; remove friction and update the template so the safer path is easier."

### `infrastructure-and-policy-as-code`

- "Inspect this declarative infrastructure change for unsafe manual steps, missing policy checks, drift response, and rollback gaps."
- "Inspect infrastructure environment promotion for desired-state drift, missing policy checks, and whether actual changes match what is declared in code."
- "Design policy checks and exception records for these infrastructure files."
- "A manual console change fixed staging; capture desired state, drift detection, and emergency exception rules."
- "A production firewall exception was made manually; capture desired state, policy checks, drift response, and expiry."

### `container-runtime-and-orchestration`

- "Set the runtime posture for this new service before rollout: resource requests and limits, drain contract, probe thresholds, and image hardening."
- "Inspect this workload manifest and probe config for missing limits, restart-loop risk, and a shutdown path that drops in-flight requests."
- "Trace what happens to in-flight requests when this deployment rolls or a host drains, then define the grace period and readiness gating that prevent drops."
- "Test peak load where workers get OOM-killed and restart-loop on a slow dependency; set memory bounds and fix the probe semantics."
- "Every deploy sheds a few hundred ordinary HTTP requests; define the workload shutdown/drain contract and capacity floor that take that to zero before launch."

### `internal-service-networking`

- "Design internal routing for a new checkout service, including discovery, identity, locality, and private dependency access."
- "Inspect this internal traffic policy for service-to-service access that is too open."
- "Inspect internal service-to-service routing config and keep this private dependency's traffic local when possible."
- "Refresh the internal networking runbook for checkout: discovery, locality, identity, and fallback when private routing fails."
- "A private service calls a regional dependency across regions during failover; set discovery, locality, identity, and fallback rules."

### `edge-traffic-and-ddos-defense`

- "Inspect the public API rate limits and origin protection in this repo before launch."
- "Inspect the signup flow and edge rules for bot filters that will not block real users."
- "Design edge traffic shedding for this route using the current routing and deployment config."
- "Signup traffic spikes with suspicious user agents; set edge limits that protect origin without blocking real customers."
- "A public login endpoint gets bursty traffic from new IP ranges; tune edge filtering without blocking real users."

### `cost-aware-reliability`

- "Before adding a new replica set for failover, compare the reliability gain against ongoing platform cost."
- "Inspect this capacity change and explain the reliability benefit versus the cost."
- "Inspect tags, owners, and shared resources so teams can act on their platform costs."
- "Replica count grew after an incident; decide what spend can be removed without losing failover headroom."
- "A second hot standby reduces outage risk but doubles monthly spend; compare the reliability gain with cheaper safeguards."

### `mobile-release-engineering`

- "Plan staged rollout, halt criteria, and forward-fix options for this new mobile release."
- "Inspect startup, crash, hang, and offline telemetry before approving this app release."
- "Use the release notes and changed files to choose rollback or forward-fix options for this app-store bug."
- "Crash-free users dip only on older OS versions after the mobile app staged rollout; decide pause, forward fix, or rollback."
- "A store release cannot be rolled back instantly; define staged exposure, halt signals, crash slices, and forward-fix plan."

### `web-release-gates`

- "Plan browser release checks for a new checkout flow covering loading, responsiveness, layout stability, runtime errors, and payload growth."
- "Inspect field and lab performance signals before rolling out this frontend change."
- "For this browser client-side change, add release checks and telemetry for loading, interaction readiness, layout stability, runtime errors, and payload growth."
- "The checkout bundle gained a heavy dependency; set checks for interaction readiness and runtime errors."
- "A new client route hydrates late on slow devices; define checks for load, interaction, layout stability, errors, and payload size."

### `accessibility-gates`

- "Inspect this checkout flow for keyboard completion, focus order, labels, contrast, and release blockers."
- "Design accessibility checks for a new checkout flow before launch."
- "Turn these accessibility bugs into journey-based regression checks with owners and retest dates."
- "A modal traps keyboard focus after payment failure; turn it into a release-blocking journey check."
- "A form works with a mouse but screen-reader users miss validation errors; make that journey block release until retested."

### `experimentation-and-metric-guardrails`

- "Inspect this experiment design for assignment, exposure logging, guardrail metrics, and readout rules."
- "The A/B test result looks suspicious; inspect sample balance, missing telemetry, and metric definitions."
- "Decide whether this experiment ramp should continue using assignment balance, exposure logging, metric validity checks, and guardrail metrics."
- "The ramp looks positive but guardrail logging changed halfway through; decide whether the readout is trustworthy."
- "The experiment ramps by account size and revenue changed early; verify assignment balance, exposure logging, and guardrail validity."

## Out Of Scope

### `none`

- "Write a marketing launch plan for the new checkout feature."
- "How much should we pay engineers for being on call?"
- "Rewrite this landing page headline to sound warmer."
- "Pick a company offsite venue and catering plan."
