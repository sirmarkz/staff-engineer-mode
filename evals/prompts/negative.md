# Router Boundary Prompts: Negative

Tests routine, out-of-scope, or neighboring work that might falsely trigger the target specialist.

Prompts are grouped by the specialist that must not fire. The suffix gives the correct route.

## Architecture And Interfaces

### `api-design-and-compatibility`

- "Refactor an internal helper function signature that has no external callers or generated clients, then prioritize the cleanup risk." (-> `dependency-and-code-hygiene`)
- "Update the public launch checklist copy for an API feature announcement without changing the API surface or compatibility behavior." (-> `none`)
- "Define producer and consumer schema compatibility for a shared analytics event without adding or changing a service API." (-> `data-contracts`)
- "Update partner onboarding FAQ examples for API usage without changing endpoints, schemas, auth behavior, or client compatibility." (-> `none`)
- "Plan retention and deletion behavior for API logs that contain customer identifiers, without changing request or response contracts." (-> `privacy-and-data-lifecycle`)

### `architecture-decisions`

- "Find module names that collide in code search and rename them so an agent can locate the canonical implementation." (-> `code-readability-for-agents`)
- "Pick an office seating plan for the engineering team to improve informal collaboration." (-> `none`)
- "Set retry, timeout, and circuit-breaker behavior for an existing downstream service call without changing ownership boundaries." (-> `dependency-resilience`)
- "Write a quarterly roadmap memo comparing staffing options, with no system boundaries or technical decision to record." (-> `none`)
- "Define merge-blocking quality checks for a service after architecture ownership and module boundaries are already agreed." (-> `testing-and-quality-gates`)

### `data-contracts`

- "Change one exposed API response field while preserving existing client callers and generated-client behavior." (-> `api-design-and-compatibility`)
- "Write plain-language privacy policy copy for how customer records are used, without changing engineering data interfaces." (-> `none`)
- "Plan replay, idempotency, and dead-letter handling for a consumer workflow after the event schema is already stable." (-> `event-workflows`)
- "Create a glossary of business terms for analytics users without producer, consumer, schema, or compatibility work." (-> `none`)
- "Tune stale cache invalidation for derived product counts after event payload fields are already stable." (-> `caching-and-derived-data`)

## Reliability And Resilience

### `slo-and-error-budgets`

- "Design logs, metrics, traces, dashboards, and alert context for a new checkout workflow before launch." (-> `observability-and-alerting`)
- "Create a quarterly executive KPI deck with sales targets and hiring goals, with no service reliability target." (-> `none`)
- "Reduce recurring alert fatigue by tuning suppression, escalation, and responder workload without changing the reliability objective." (-> `oncall-health`)
- "Rebalance oncall rotations and escalation notes to lower burnout without changing targets or alert thresholds." (-> `oncall-health`)
- "Choose team bonus metrics for a planning offsite with no user-impact reliability objective." (-> `none`)

### `high-availability-design`

- "Prove restore capability after corruption or accidental deletion with RTO/RPO evidence and recovery drills." (-> `backup-and-recovery`)
- "Negotiate a cheaper regional hosting contract without asking about failover, capacity, or user impact." (-> `none`)
- "Run a scoped failure-injection exercise to validate assumptions in the existing topology." (-> `resilience-experiments`)
- "Increase worker pool size for expected traffic growth without adding region-loss or failover design." (-> `performance-and-capacity`)
- "Prepare an office move continuity checklist for facilities, with no production service topology or failover scope." (-> `none`)

### `dependency-resilience`

- "Design service discovery, identity, locality, and private traffic policy for internal service-to-service calls." (-> `internal-service-networking`)
- "Set per-tenant quotas and noisy-neighbor fairness for shared job capacity, not retry behavior for a downstream call." (-> `tenant-isolation`)
- "Assign service ownership and module boundaries for a new worker that may call downstream systems later." (-> `architecture-decisions`)
- "Document vendor renewal risks and account contacts without setting runtime fallback, retry, or timeout behavior." (-> `none`)
- "Define private service routing and identity for east-west calls before dependency retry policy is discussed." (-> `internal-service-networking`)

### `performance-and-capacity`

- "Choose a lower-cost capacity target while preserving availability and error-budget commitments." (-> `cost-aware-reliability`)
- "Ask finance to categorize infrastructure spend by department without changing traffic, latency, or headroom." (-> `none`)
- "Tune LLM request token budgets and prompt-cache behavior for a model route with rising tail latency." (-> `llm-serving-cost-and-latency`)
- "Define alert thresholds from a service reliability objective after traffic headroom work is already complete." (-> `slo-and-error-budgets`)
- "Write a budget variance memo for cloud spend with no throughput, latency, or headroom decision." (-> `none`)

### `backup-and-recovery`

- "Prove source-to-deploy artifact integrity with isolated builders, provenance, signing, and deployment admission." (-> `software-supply-chain-security`)
- "Buy office document archiving software for paper HR files with no production system restore requirement." (-> `none`)
- "Design static failover capacity and location-loss survivability before any restore drill is planned." (-> `high-availability-design`)
- "Set data retention and deletion windows for customer records without restore drills or recovery targets." (-> `privacy-and-data-lifecycle`)
- "Run an online index backfill with query-plan checks, lock limits, throttling, and abort criteria." (-> `database-operations`)

### `resilience-experiments`

- "Design static fault-domain topology, failover capacity, and location-loss survivability for a service." (-> `high-availability-design`)
- "Host a team game-day retrospective about communication norms without touching production systems or failure modes." (-> `none`)
- "Define backup restore evidence for accidental data deletion, including RTO and RPO measurements." (-> `backup-and-recovery`)
- "Tune alert routing after a past outage produced too many pages, without injecting failures or testing hypotheses." (-> `oncall-health`)
- "Plan a disaster recovery restore drill with RTO and RPO evidence instead of exercising live failure injection." (-> `backup-and-recovery`)

### `state-machine-correctness`

- "Design event replay, ordering, idempotency, duplicate-work prevention, and dead-letter recovery across consumers." (-> `event-workflows`)
- "Document the business approval states for a sales contract without implementing software transitions or invariants." (-> `none`)
- "Split writes across two storage systems while preserving consistency, conflict resolution, and failover behavior." (-> `distributed-data-and-consistency`)
- "Rename workflow statuses in a help article without changing code, transitions, locks, or invariants." (-> `none`)
- "Define API compatibility for a status field exposed to external clients, without changing internal transition logic." (-> `api-design-and-compatibility`)

## Delivery And Quality

### `testing-and-quality-gates`

- "Review the exact staged diff before commit for intent match, missing edge cases, and behavior verification." (-> `agent-pr-review`)
- "Ask QA to choose a team lunch schedule after the release retrospective." (-> `none`)
- "Create anonymized production-derived fixtures and define their freshness versus determinism tradeoff." (-> `test-data-engineering`)
- "Write a QA team charter and meeting cadence without defining gates, signals, or verification checks." (-> `none`)
- "Plan browser payload, layout stability, and runtime error checks for a web release." (-> `web-release-gates`)

### `test-data-engineering`

- "Define overall CI signals, merge-blocking tests, quality gates, and release-blocking failure probes." (-> `testing-and-quality-gates`)
- "Write sample sales personas for a marketing demo without using them as test fixtures or validation data." (-> `none`)
- "Review a concrete staged diff for behavior risks and missing edge cases before committing." (-> `agent-pr-review`)
- "Fix flaky CI gate ordering without changing fixture generation, masking, or data freshness." (-> `testing-and-quality-gates`)
- "Create realistic customer quotes for a demo script, not validation data." (-> `none`)

### `configuration-and-automation-safety`

- "Capture desired infrastructure state, detect drift, reconcile changes, and define emergency exception rules after manual edits." (-> `infrastructure-and-policy-as-code`)
- "Choose capitalization conventions for example environment variable names in a general writing style guide, with no repo docs, live configuration, or automation behavior." (-> `none`)
- "Plan staged exposure and rollback metrics for a production configuration change after the mutation mechanism is already validated." (-> `progressive-delivery`)
- "Write onboarding copy explaining environment variable names, with no live mutation, automation behavior, ownership, source-of-truth, freshness, or lifecycle rule." (-> `none`)
- "Model desired infrastructure state and policy drift detection for manually changed resources." (-> `infrastructure-and-policy-as-code`)

### `release-build-reproducibility`

- "Move production traffic with canary metrics, exposure stages, rollback criteria, and forward-fix options." (-> `progressive-delivery`)
- "Draft a press release announcing a new product version with no build, artifact, package, or promotion work." (-> `none`)
- "Compare local, CI, staging, and production drift after a build works only in one environment." (-> `dev-environment-parity`)
- "Audit certificate signing and artifact provenance for build inputs, with no release version promotion decision." (-> `software-supply-chain-security`)
- "Write release-note copy for customers after artifacts are already published." (-> `none`)

### `dev-environment-parity`

- "Prove release artifact identity with build-once promote-many mechanics, package versions, and promotion records." (-> `release-build-reproducibility`)
- "Pick a developer laptop wallpaper standard for onboarding docs." (-> `none`)
- "Define CI quality gates and merge-blocking tests for a service, independent of environment drift." (-> `testing-and-quality-gates`)
- "Define reproducible package identity and promotion records after parity issues are resolved." (-> `release-build-reproducibility`)
- "Choose local editor themes for the onboarding guide." (-> `none`)

### `progressive-delivery`

- "Cut a release candidate with reproducible package identity, version metadata, and build-once promote-many evidence." (-> `release-build-reproducibility`)
- "Write customer-facing release announcement copy after deployment is already complete and stable." (-> `none`)
- "Set owner, expiry, fallback behavior, and removal checks for an old rollout flag." (-> `feature-flag-lifecycle`)
- "Clean up a long-expired feature flag and prove fallback code was removed after rollout." (-> `feature-flag-lifecycle`)
- "Schedule launch-day support coverage without staged exposure, metrics, or rollback work." (-> `none`)

### `feature-flag-lifecycle`

- "Introduce a rollout flag for staged production exposure with canary metrics, abort criteria, and rollback." (-> `progressive-delivery`)
- "Rename a campaign feature in product marketing materials without touching runtime flags." (-> `none`)
- "Remove dead helper code that is not guarded by any active or retired flag." (-> `dependency-and-code-hygiene`)
- "Plan canary exposure for a risky change using health metrics and automatic halt criteria." (-> `progressive-delivery`)
- "Add a UI preference toggle stored only in local browser settings, with no endpoint, schema, auth, rollout, or operational flag." (-> `none`)

### `production-readiness-review`

- "Plan staged rollout, canary metrics, halt criteria, and rollback for a production-affecting change." (-> `progressive-delivery`)
- "Run a leadership readiness survey about team morale with no system launch or operational impact." (-> `none`)
- "Design telemetry, dashboards, and alerts for a new workflow before any launch go/no-go review." (-> `observability-and-alerting`)
- "Write a launch announcement blog post after operational checks are complete." (-> `none`)
- "Run accessibility conformance checks for a new checkout flow before release." (-> `accessibility-gates`)

### `migration-and-deprecation`

- "Remove unused helper code and static-analysis warnings in small hygiene batches with codemod safety checks." (-> `dependency-and-code-hygiene`)
- "Write a retirement party invitation for a legacy product manager." (-> `none`)
- "Change an exposed endpoint response while preserving existing clients and generated SDK behavior." (-> `api-design-and-compatibility`)
- "Define a fleet-wide runtime upgrade window with version-skew exceptions and rollback batches." (-> `fleet-upgrades`)
- "Archive old office-event wiki pages by HR request without engineering docs, users, APIs, or data paths." (-> `none`)

### `fleet-upgrades`

- "Plan a routine package update and lockfile sweep with small-batch hygiene and rollback checks." (-> `dependency-and-code-hygiene`)
- "Upgrade conference room monitors and track purchase approvals for facilities." (-> `none`)
- "Plan build-once promote-many release artifacts for a new version after all runtime upgrades are complete." (-> `release-build-reproducibility`)
- "Remove unused dependencies from one service lockfile without coordinating runtime version skew." (-> `dependency-and-code-hygiene`)
- "Retire the legacy reporting service with usage inventory, no-new-usage blocks, consumer migration batches, and decommission evidence." (-> `migration-and-deprecation`)

### `agent-pr-review`

- "Design generic reviewer assignment rules, change-size limits, and review-latency reporting without a concrete diff, branch, PR, or staged change." (-> `none`)
- "Run a design review for an API versioning decision before any diff exists." (-> `api-design-and-compatibility`)
- "Evaluate static-analysis warnings and dead-code cleanup priority from a maintenance backlog, not a staged change." (-> `dependency-and-code-hygiene`)
- "Set repository-wide coding-agent governance rules before any change is staged." (-> `ai-coding-governance`)
- "Summarize a product requirements document for stakeholders without reviewing a diff." (-> `none`)

### `code-readability-for-agents`

- "Set AI-agent allowed actions, protected paths, generated-code acceptance checks, and required verification details for the repo." (-> `ai-coding-governance`)
- "Rewrite employee handbook paragraphs so they are easier for new hires to read." (-> `none`)
- "Review a concrete PR diff for intent match and missing behavior verification before merge." (-> `agent-pr-review`)
- "Review a staged refactor for behavior change, missing tests, and unintended file edits." (-> `agent-pr-review`)
- "Rewrite marketing copy so customers understand a feature name." (-> `none`)

### `documentation-lifecycle`

- "Fix typos, headings, link text, and markdown formatting in README and install docs without changing source-of-truth, freshness, or operational guidance." (-> `none`)
- "Draft marketing FAQ copy for a conference booth with no engineering source of truth or runbook impact." (-> `none`)
- "Capture an architecture decision record for service ownership and boundary tradeoffs." (-> `architecture-decisions`)
- "Run accessibility checks on public docs navigation with keyboard and screen-reader blockers." (-> `accessibility-gates`)
- "Write a customer newsletter that links to docs but has no source-of-truth or freshness obligation." (-> `none`)

### `dependency-and-code-hygiene`

- "Plan runtime support windows, mixed-version rollout, version-skew exceptions, and unsupported service cleanup." (-> `fleet-upgrades`)
- "Inventory vendor contracts for renewal dates and account owners, with no code or runtime dependency changes." (-> `none`)
- "Plan remediation for an exploitable deployed library with patch SLA, exposure review, and expiring exceptions." (-> `vulnerability-management`)
- "Plan dependency timeout, retry, and fallback behavior for a critical downstream call." (-> `dependency-resilience`)
- "Compare vendor pricing tiers for a SaaS tool without changing code, packages, or runtime dependencies." (-> `none`)

## Operations And Observability

### `observability-and-alerting`

- "Recurring pages are noisy and manual suppression may hide user impact; reduce responder toil without losing urgent signals." (-> `oncall-health`)
- "Create a dashboard of sales pipeline health for the revenue team without production telemetry or alerts." (-> `none`)
- "Tie alert thresholds to reliability targets and urgent versus follow-up rules for an existing SLO." (-> `slo-and-error-budgets`)
- "Plan SLO definitions and error-budget policy for an existing service before changing dashboards." (-> `slo-and-error-budgets`)
- "Create a finance dashboard showing invoice totals, unrelated to production telemetry." (-> `none`)

### `incident-response-and-postmortems`

- "A deployed vulnerable dependency has exploit exposure; plan patch SLA, rollout, and expiring remediation exceptions." (-> `vulnerability-management`)
- "Write a company newsletter about a historical outage without action items or current operational risk." (-> `none`)
- "Tune noisy recurring pages and escalation policy to reduce responder load without an active incident." (-> `oncall-health`)
- "Design alert thresholds, dashboards, and runbook links before any incident exists." (-> `observability-and-alerting`)
- "Write a commemorative post about a past outage for the company blog, with no remediation tracking." (-> `none`)

### `oncall-health`

- "Design logs, metrics, traces, dashboard context, and alerts for a new payment flow before launch." (-> `observability-and-alerting`)
- "Plan a wellness survey for support staff that does not involve paging, alerts, incidents, or operations." (-> `none`)
- "Run live mitigation and communication for an ongoing production outage." (-> `incident-response-and-postmortems`)
- "Choose a wellness stipend vendor for support staff, unrelated to paging or incidents." (-> `none`)
- "Define SLO alert urgency and follow-up policy for a service objective." (-> `slo-and-error-budgets`)

## Security And Privacy

### `secure-sdlc-and-threat-modeling`

- "A deployed vulnerable package is exploitable; plan remediation rollout, patch SLA, and expiring exception handling." (-> `vulnerability-management`)
- "Ask legal to review standard contract language for a customer deal, with no system design or abuse-case work." (-> `none`)
- "Set AI-agent protected paths, allowed actions, data boundaries, and verification requirements for generated code." (-> `ai-coding-governance`)
- "Review a deployed CVE and set patch rollout deadlines with temporary exception expiry." (-> `vulnerability-management`)
- "Ask procurement to score security vendors by contract price and renewal date only." (-> `none`)

### `identity-and-secrets`

- "Plan certificate expiry handling, key rotation, trust-chain agility, and cryptographic rollback evidence." (-> `cryptography-and-key-lifecycle`)
- "Create a fictional office seating chart with placeholder initials only, with no employee data, software identity, or secret access." (-> `none`)
- "Model tenant boundary tests that prove one customer cannot access another customer's data." (-> `tenant-isolation`)
- "Define tenant-boundary tests for cross-customer read and write isolation." (-> `tenant-isolation`)
- "Create an office visitor badge policy with no software identity or secret access." (-> `none`)

### `cryptography-and-key-lifecycle`

- "Define runtime access policy for secrets, including who can read them, rotation evidence, and emergency access cleanup." (-> `identity-and-secrets`)
- "Write a puzzle about encrypted messages for a recruiting event, with no production key material or protocol choice." (-> `none`)
- "Prove source-to-deploy artifact trust with isolated builders, provenance, signing, and admission checks." (-> `software-supply-chain-security`)
- "Rotate application secrets and remove emergency access after an incident without changing algorithms or trust chains." (-> `identity-and-secrets`)
- "Write a workshop puzzle about hash functions for interns, unrelated to production cryptography." (-> `none`)

### `software-supply-chain-security`

- "A deployed dependency has known exploit exposure; plan patch rollout, exception expiry, and remediation evidence." (-> `vulnerability-management`)
- "Compare vendor logos for a partner page without evaluating build provenance or dependency trust." (-> `none`)
- "Plan certificate rotation and trust-chain agility for a production service." (-> `cryptography-and-key-lifecycle`)
- "Set runtime secret access ownership and emergency read cleanup for production operators." (-> `identity-and-secrets`)
- "Evaluate a vendor partnership announcement page without build artifacts or dependency trust concerns." (-> `none`)

### `vulnerability-management`

- "Before deployment, build a threat model with trust boundaries, data flows, abuse cases, and residual-risk register." (-> `secure-sdlc-and-threat-modeling`)
- "Write a security awareness trivia quiz for all hands, with no deployed exposure or remediation workflow." (-> `none`)
- "Update routine dependencies and lockfiles in small batches where no known exploit exposure is involved." (-> `dependency-and-code-hygiene`)
- "Model trust boundaries and abuse cases for a feature before it ships, with no known deployed exploit." (-> `secure-sdlc-and-threat-modeling`)
- "Run a routine dependency update where all packages are current and no advisory is involved." (-> `dependency-and-code-hygiene`)

### `tenant-isolation`

- "Define data retention, deletion, minimization, and privacy lifecycle controls for customer records." (-> `privacy-and-data-lifecycle`)
- "Protect a public signup endpoint from abusive clients with route rate limits, breach actions, and origin shielding." (-> `edge-traffic-and-ddos-defense`)
- "Set runtime secret access policy and emergency cleanup rules for support operators." (-> `identity-and-secrets`)
- "Write contract language promising customer data separation, with no engineering tests or controls." (-> `none`)
- "Plan retention, deletion, and minimization controls for tenant data after isolation is already proven." (-> `privacy-and-data-lifecycle`)

### `privacy-and-data-lifecycle`

- "Prove tenant-boundary isolation with cross-tenant access tests and blast-radius checks." (-> `tenant-isolation`)
- "Draft a public blog post about privacy culture without engineering retention or deletion controls." (-> `none`)
- "Define producer and consumer compatibility for a customer-profile event payload." (-> `data-contracts`)
- "Model cross-tenant access tests for support tooling, with no retention or deletion scope." (-> `tenant-isolation`)
- "Draft legal privacy-policy copy for a website update without implementing lifecycle controls." (-> `none`)

### `engineering-control-evidence`

- "Create a documentation inventory for owner, source of truth, freshness cadence, and stale-doc cleanup for one runbook set." (-> `documentation-lifecycle`)
- "Collect auditor meeting availability and travel preferences without mapping engineering controls or evidence." (-> `none`)
- "Build a threat model with trust boundaries, abuse cases, and residual-risk ownership for one feature." (-> `secure-sdlc-and-threat-modeling`)
- "Prepare audit committee travel logistics without mapping any control to system evidence." (-> `none`)
- "Define release quality gates and required verification artifacts for merge blocking." (-> `testing-and-quality-gates`)

### `llm-application-security`

- "Design an LLM eval dataset with graders, thresholds, slice coverage, regression history, and failure triage." (-> `llm-evaluation`)
- "Write social media copy about responsible AI features without changing an LLM product surface." (-> `none`)
- "Set model-serving token budgets, prompt-cache policy, and latency degradation behavior for one route." (-> `llm-serving-cost-and-latency`)
- "Create an LLM benchmark with slice coverage, graders, thresholds, and failure triage." (-> `llm-evaluation`)
- "Draft AI ethics talking points for a sales deck with no product control changes." (-> `none`)

### `ai-coding-governance`

- "Write a blog post about AI coding productivity trends for a non-technical audience." (-> `none`)
- "Improve repository module names so coding agents can locate the canonical implementation in one search." (-> `code-readability-for-agents`)
- "Review an AI-generated staged diff for behavior, missing tests, and unintended file changes before commit." (-> `agent-pr-review`)
- "Review a staged AI-generated patch for unintended files and missing test evidence." (-> `agent-pr-review`)
- "Create a policy article about AI in society for the company blog." (-> `none`)

### `llm-evaluation`

- "A retrieval tool can expose hidden customer data through prompt injection; define tool-boundary and unsafe-output controls." (-> `llm-application-security`)
- "Ask a model to draft a product tagline and pick the most appealing option, with no eval harness or threshold." (-> `none`)
- "Plan production model promotion checks with drift monitors, serving rollback, and training-serving skew review." (-> `ml-reliability-and-evaluation`)
- "Tune prompt-cache keys and max-token limits to reduce serving cost for one model route." (-> `llm-serving-cost-and-latency`)
- "Ask a chatbot for naming ideas and pick the funniest one manually." (-> `none`)

### `llm-serving-cost-and-latency`

- "The backend hot path has latency regression and needs capacity headroom checks unrelated to model serving or token budgets." (-> `performance-and-capacity`)
- "Compare subscription prices for writing assistants for the marketing team, with no production serving path." (-> `none`)
- "Design an LLM regression eval set with graders, thresholds, slice coverage, and failure triage." (-> `llm-evaluation`)
- "Define unsafe tool-output handling and prompt-injection boundaries for retrieval." (-> `llm-application-security`)
- "Estimate the marketing team's subscription budget for standalone chat tools." (-> `none`)

## Data, Platform, And Client Systems

### `distributed-data-and-consistency`

- "Model in-process state transitions, locking, concurrency invariants, and property tests for a local protocol." (-> `state-machine-correctness`)
- "Choose a shared spreadsheet naming convention for data analysts, with no storage semantics or system writes." (-> `none`)
- "Execute an index backfill and lock-risk plan for a single database schema migration." (-> `database-operations`)
- "Plan schema migration lock windows and rollback for one relational table." (-> `database-operations`)
- "Write a data team mission statement with no storage, replication, or consistency decision." (-> `none`)

### `event-workflows`

- "Define producer and consumer schema compatibility for a shared event payload without replay or ordering concerns." (-> `data-contracts`)
- "Plan an employee appreciation event agenda, unrelated to software messages or workflows." (-> `none`)
- "Analyze stale materialized-view results and cache invalidation order after inventory updates." (-> `caching-and-derived-data`)
- "Define event payload schema compatibility between producer and consumer teams." (-> `data-contracts`)
- "Schedule an employee town hall and catering plan." (-> `none`)

### `caching-and-derived-data`

- "Late-arriving events are replayed after dashboard cutoff; define pipeline freshness, validation, and no-double-count recovery." (-> `data-pipeline-reliability`)
- "Make a browser cache-clearing help article for support, with no application data correctness concern." (-> `none`)
- "Set allowed stale-read semantics across replicated storage during failover." (-> `distributed-data-and-consistency`)
- "Plan data pipeline freshness checks for late-arriving records before they reach reports." (-> `data-pipeline-reliability`)
- "Write customer support instructions for refreshing a browser tab." (-> `none`)

### `database-operations`

- "Split mutations across shards and storage systems while preserving consistency, failover behavior, and conflict handling." (-> `distributed-data-and-consistency`)
- "Recover accidentally deleted account rows, prove point-in-time restore, RTO/RPO evidence, and write reconciliation." (-> `backup-and-recovery`)
- "Define API response compatibility for a field backed by the database but exposed to generated clients." (-> `api-design-and-compatibility`)
- "Set distributed write conflict handling across two stores during failover." (-> `distributed-data-and-consistency`)
- "Collect database conference talk proposals for the team learning budget." (-> `none`)

### `data-pipeline-reliability`

- "Product cards show stale search results after inventory changes; map invalidation order and cold-cache behavior." (-> `caching-and-derived-data`)
- "Prepare a slide deck about data-driven culture without changing pipelines, freshness, or reporting trust." (-> `none`)
- "Plan event consumer ordering, idempotency, and dead-letter recovery for a queue workflow." (-> `event-workflows`)
- "Fix stale derived search results by mapping cache invalidation and cold-start behavior." (-> `caching-and-derived-data`)
- "Create an analytics team brand guide with no pipeline or report correctness scope." (-> `none`)

### `ml-reliability-and-evaluation`

- "Compare model vendors for roadmap positioning and write a purchasing recommendation; no production model promotion, serving check, drift monitor, or rollback decision is involved." (-> `none`)
- "Create a model-themed recruiting exercise that does not touch a deployed ML system or evaluation gate." (-> `none`)
- "Define LLM evaluation graders, thresholds, slice coverage, and regression history for a prompt workflow." (-> `llm-evaluation`)
- "Build LLM prompt regression graders and slice thresholds for a support assistant." (-> `llm-evaluation`)
- "Write model-themed swag copy for recruiting." (-> `none`)

### `platform-golden-paths`

- "Set AI coding-agent protected paths, allowed actions, data boundaries, and generated-code acceptance checks." (-> `ai-coding-governance`)
- "Design branded platform team stickers and swag for an internal launch." (-> `none`)
- "Compare local, CI, staging, and production drift for a service that only fails outside development." (-> `dev-environment-parity`)
- "Define CI, local, staging, and production parity checks for a service template." (-> `dev-environment-parity`)
- "Plan the platform team's internal launch party playlist." (-> `none`)

### `infrastructure-and-policy-as-code`

- "Preview a generated production configuration mutation, cap blast radius, validate inputs, and define abort and rollback." (-> `configuration-and-automation-safety`)
- "Write a policy memo about remote work reimbursement, unrelated to infrastructure state or controls." (-> `none`)
- "Plan public edge rate-limit breach handling, origin shielding, and load shedding." (-> `edge-traffic-and-ddos-defense`)
- "Preview and bound a generated config change before rollout, with abort and rollback criteria." (-> `configuration-and-automation-safety`)
- "Draft an HR policy about home internet reimbursement." (-> `none`)

### `internal-service-networking`

- "Protect the public edge with bot handling, rate-limit breach actions, origin shielding, and edge load shedding." (-> `edge-traffic-and-ddos-defense`)
- "Define server-side webhook egress allowlists, private-address blocking, redirect policy, and audit fields for user-supplied callback URLs." (-> `secure-sdlc-and-threat-modeling`)
- "Set retry, timeout, and fallback policy for a service dependency call over an existing network path." (-> `dependency-resilience`)
- "Set circuit-breaker and timeout policy for a dependency call over an existing network route." (-> `dependency-resilience`)
- "Plan a professional networking meetup for engineers outside work." (-> `none`)

### `edge-traffic-and-ddos-defense`

- "Design internal service-to-service traffic locality, service identity, and private dependency routing." (-> `internal-service-networking`)
- "Set tenant-aware quotas and noisy-neighbor fairness inside shared worker capacity; no public edge abuse is involved." (-> `tenant-isolation`)
- "Plan browser release checks for layout stability, loading, runtime errors, and payload growth." (-> `web-release-gates`)
- "Define private service identity and locality for internal calls behind the edge." (-> `internal-service-networking`)
- "Choose brand imagery for the home page without traffic or overload concerns." (-> `none`)

### `cost-aware-reliability`

- "Reduce the monthly invoice by finding cheaper vendor plans; no reliability, capacity, or system behavior tradeoff is being asked." (-> `none`)
- "Ask accounting to split cloud invoices by cost center without changing reliability or capacity decisions." (-> `none`)
- "Add headroom for a latency regression where spend is not part of the decision." (-> `performance-and-capacity`)
- "Define SLOs and error-budget burn policy where cost is not part of the tradeoff." (-> `slo-and-error-budgets`)
- "Prepare quarterly budget slides for finance with no reliability decision." (-> `none`)

### `mobile-release-engineering`

- "Plan browser release checks for loading, responsiveness, layout stability, runtime errors, and payload growth." (-> `web-release-gates`)
- "Update the company phone reimbursement policy for employees." (-> `none`)
- "Plan staged production exposure for a backend feature using canary metrics and rollback criteria." (-> `progressive-delivery`)
- "Run app accessibility checks for a sign-in flow with screen reader blockers before release." (-> `accessibility-gates`)
- "Pick phone-case colors for a developer swag order." (-> `none`)

### `web-release-gates`

- "Plan a native mobile staged rollout using startup, crash, hang, offline telemetry, pause criteria, and forward-fix options." (-> `mobile-release-engineering`)
- "Choose homepage hero artwork for a marketing refresh without release or runtime checks." (-> `none`)
- "Run an accessibility conformance gate for a checkout flow keyboard trap and screen reader issue." (-> `accessibility-gates`)
- "Plan canary exposure for a backend API using staged traffic and rollback metrics." (-> `progressive-delivery`)
- "Rewrite landing-page hero copy for tone after runtime checks are already green." (-> `none`)

### `accessibility-gates`

- "Review the brand palette and make the public page feel warmer; no accessibility conformance or user-flow blocker is involved." (-> `none`)
- "Order ergonomic keyboards for the office and document vendor pricing." (-> `none`)
- "Plan web release checks for load timing, runtime errors, layout stability, and payload growth." (-> `web-release-gates`)
- "Plan web release gates for payload growth, runtime errors, and layout stability only." (-> `web-release-gates`)
- "Write inclusive-language guidance for HR docs without user-flow conformance checks." (-> `none`)

### `experimentation-and-metric-guardrails`

- "Set canary halt metrics and rollback criteria for production traffic exposure after deployment." (-> `progressive-delivery`)
- "Brainstorm survey questions for market research with no product experiment, exposure logging, or metric validity concern." (-> `none`)
- "Define SLO-based alert thresholds and follow-up policy for an existing service objective." (-> `slo-and-error-budgets`)
- "Set production canary metrics and abort criteria for a rollout, unrelated to product experiment validity." (-> `progressive-delivery`)
- "Ask customers which logo they like in a survey with no exposure logging or metrics guardrail." (-> `none`)
