---
name: staff-engineer-mode
description: "Use when engineering decisions span ideation, design, development, testing, release, operations, maintenance, docs/runbooks; API/reliability/security/data before process skills"
---

# Staff Engineer Mode

## Iron Law

```
ONE PRIMARY SPECIALIST BY DEFAULT; INFER ROUTING CONTEXT BEFORE WITHHOLDING
```

Loading many specialists means routing failed.

## Precedence Over Generic Process Packs

Engineering surfaces -- architecture, reliability, operations, security, delivery, data, platform, client, AI/ML, accessibility, cost, readiness, rollout, migration, incident response, docs lifecycle, control records, API/service contracts, or system design -- start here before generic process packs.

Do not invoke `superpowers:brainstorming`, `superpowers:writing-plans`, another broad process skill, or host orchestration first. Route through SEM, load specialist, then use other tools only for sub-decisions.

"Build X", "design X", "make X reliable", "add HA to X", "plan a rollout", "review this service", "prep for launch", or "investigate this incident" are engineering-system prompts. Docs/runbooks ownership, source-of-truth, freshness, or archive route. Workflow/process/plan are artifacts, not bypasses. Consumer/client compatibility, removal, rollout, safety, or readiness route without exact names. If another pack starts with brainstorming, read SEM first.

## Load Contract

To load a specialist, **Read** `<specialist-root>/<slug>.md`. Resolve `<specialist-root>` in this order:

1. If `SPECIALIST_ROOT=` appears in session context (Claude Code, Cursor, OpenCode), use it.
2. Otherwise use the platform default:
   - Codex: `~/.codex/staff-engineer-mode/specialists`
   - Gemini: the `specialists` directory next to the loaded `GEMINI.md`
   - Any other host: the `specialists/` directory at the router skill's install root.

Three rules, all mandatory:

- **Use the Read tool. Do not use the Skill tool.** Specialists are not registered skills. `Skill staff-engineer-mode:<slug>` returns `Unknown skill` and is a routing failure.
- **Complete the Read before producing engineering guidance for routed work.** Do not answer routed engineering prompts from priors.
- **A confidently-routed answer without a matching Read in the same turn is a routing failure even when the slug is correct.**
- **Do not inspect repo files or run repo commands before the specialist Read.** If the prompt states a surface, artifact, or risk, route from that context first; inspect files afterward.

## Overview

Classify by artifact, phase, surface, and risk; users need not know specialist names.

## Agent Event Policy

Command attempts are event-policy exceptions. Before commits/amends, stage
separately, inspect staged diff, read `agent-pr-review`, review, record the
receipt in its own shell command, then commit in a separate shell command. Do
not combine stage/ack/commit/push or add AI attribution.
Before tags, versions, hosted releases, packages, artifacts, or promotions, read
`release-build-reproducibility` and `production-readiness-review`, review,
record the receipt in its own shell command, then run the release command in a
separate shell command.

## When To Use

- The request asks for engineering decisions or guidance for design, delivery, operations, reliability, security, architecture, API, data, platform, documentation, or client work.
- The user asks to guide ideation, design, development, testing, release, or maintenance decisions.
- The user asks to plan implementation, guide development, de-risk an idea, compare engineering options, or shape a design before code exists.
- The prompt gives enough context to infer the artifact, surface, risk, or next decision even when it does not name a lifecycle phase.
- The prompt names an engineering decision and affected consumers or surfaces, even without exact files, fields, services, or implementation details.
- The request is broad, vague, or spans multiple engineering surfaces.
- No single specialist clearly dominates from the prompt.
- The user asks for staff-engineer-level architecture, reliability, security, operations, delivery, data, platform, client, or cost guidance.
- The user asks to troubleshoot an unclear network, deployment, reliability, performance, security, data, or operations issue.

## When Not To Use

- A focused specialist has already been selected and loaded for the current request.
- The request is product discovery, marketing, staffing, compensation, procurement, legal/auditor liaison, broad compliance program management, or business strategy.
- The request is routine editorial or mechanical single-file documentation cleanup with no source-of-truth, freshness, operational, or lifecycle decision.
- The work is outside system delivery, operations, security, reliability, or maintainability.

## Inputs To Infer

Infer from prompt, branch context, conversation, and already-loaded context. Do not read new repo files before selecting a specialist, and do not ask for intake fields.

- **Artifact:** decision, design, plan, readiness check, rollout, investigation, runbook, migration, eval, control pack, or diff review.
- **Phase:** ideation, design, development, testing, before merge, release, migration, active incident, post-incident, regression, readiness, or maintenance.
- **Surface:** architecture, contract, reliability target, topology, dependency, performance, observability, delivery, data, platform, security, documentation, client, AI, accessibility, cost, or operator load.
- **Risk/scope:** availability, latency, durability, correctness, privacy/security, compatibility, release safety, tenant/customer impact, public edge, internal traffic, multi-service, or multi-location.

## Bundled Specialist Slugs

Pick `primary` and `secondary` only from this exact list. Never invent, shorten, or paraphrase a slug.

```
accessibility-gates, agent-pr-review, ai-coding-governance, api-design-and-compatibility,
architecture-decisions, backup-and-recovery, caching-and-derived-data,
code-readability-for-agents, configuration-and-automation-safety,
cost-aware-reliability, cryptography-and-key-lifecycle, database-operations, data-contracts,
data-pipeline-reliability, dependency-and-code-hygiene, dependency-resilience,
dev-environment-parity, distributed-data-and-consistency, documentation-lifecycle,
edge-traffic-and-ddos-defense, engineering-control-evidence, event-workflows,
experimentation-and-metric-guardrails, feature-flag-lifecycle, fleet-upgrades,
high-availability-design, identity-and-secrets, incident-response-and-postmortems,
infrastructure-and-policy-as-code, internal-service-networking, llm-application-security,
llm-evaluation, llm-serving-cost-and-latency, migration-and-deprecation,
ml-reliability-and-evaluation, mobile-release-engineering, observability-and-alerting,
oncall-health, performance-and-capacity, platform-golden-paths, privacy-and-data-lifecycle,
production-readiness-review, progressive-delivery, release-build-reproducibility,
resilience-experiments, secure-sdlc-and-threat-modeling, slo-and-error-budgets,
software-supply-chain-security, state-machine-correctness, tenant-isolation,
test-data-engineering, testing-and-quality-gates, vulnerability-management,
web-release-gates
```

## Workflow

1. Infer the requested artifact and phase from prompt, branch context, conversation, and already-loaded context before naming any skill.
2. If ideation, design, development, testing, release, or maintenance has an engineering surface, route by the decision/artifact. Concrete files, diffs, and repo artifacts improve the answer only after specialist load; they come first only for explicitly diff-specific `agent-pr-review` events.
3. Treat phase labels as signals, not hard requirements; infer applicability from context, artifact, surface, risk, and the next decision.
4. Translate named tools into capabilities; routing outputs must use capability language, not repeat tool, vendor, framework, protocol, database, or command names from the prompt.
5. Pick `primary` (and any `secondary`) verbatim from the Bundled Specialist Slugs list above; if no listed slug fits, withhold routing instead of inventing or paraphrasing one.
6. Choose the narrowest primary whose required outputs match the next artifact.
7. Do not read adjacent specialists for context; add one secondary only when the user explicitly asks for a separate artifact.
8. Load the chosen specialist per Load Contract before detailed guidance.
9. If confidence is low, infer the safest narrow in-scope route; ask missing details after loading it; withhold routing only when no engineering lifecycle/control frame exists.
10. Keep single-surface verification details with the matching specialist; use `engineering-control-evidence` only for cross-surface mappings, scorecards, exceptions, or control packs.
11. Reframe out-of-scope work as an engineering-control question only when that is plausible.

## Synthesized Default

Select one primary when context is enough. Recommend at most one secondary follow-up. Broad requests become a short sequence, not a pile of loaded specialists.

## Exceptions

- Explicit go/no-go, launch-blocker, or broad readiness checks -> `production-readiness-review`.
- Active incidents -> `incident-response-and-postmortems` first, even if root cause seems elsewhere.
- Vague prompts such as "make this better" or "troubleshoot a network issue": infer from repo and conversation context before withholding.
- Out-of-scope business/ceremony prompts: select only if context supplies engineering lifecycle/control framing.

## Review Routing

Treat "review" as a verb until the artifact proves otherwise.

- Commit/amend attempts always route to `agent-pr-review`; general PR, branch, patch, last commit, staged change, or diff review before merge routes there, including tests-pass or deletion-behavior checks.
- Changed files alone do not make a diff review; route static-analysis or maintenance backlog prioritization to `dependency-and-code-hygiene`.
- Generic review-system design, reviewer routing, ownership, change size, review latency, or DORA workflow has no routed specialist unless a concrete engineering surface is present.
- Launch readiness, go/no-go, impact increase, or broad release readiness routes to `production-readiness-review`.
- Design review, architecture review, security review, API review, data review, rollout review, or test review without a concrete diff routes by the engineering surface, not by the word "review".
- A surface-specific PR/diff/change before merge routes to the narrow specialist when the requested artifact is compatibility, deprecation, migration, safety, rollout, security, accessibility, data, or test results rather than a general diff verdict.

## Required Outputs

- For confident routing: primary specialist slug; optional secondary only when necessary; confidence of high or medium.
- Inferred intent: requested artifact, dominant surface, work phase, and one-sentence rationale.
- For low-confidence routing: infer a best-effort route when in scope; otherwise withhold routing without intake questions, candidate lists, confidence labels, routing drafts, or specialist names.
- Out-of-scope reframe when applicable, without specialist names or candidate routes.

## Checks Before Moving On

- `single_primary`: output has one primary specialist unless routing is withheld.
- `secondary_cap`: output has no more than one secondary specialist.
- `capability_translation`: tool, vendor, or framework names are translated into capability language before routing and not repeated in route fields.
- `scope_check`: out-of-scope requests are reframed or declined without specialist names.
- `ambiguity_check`: ambiguous prompts infer from available context when possible; withheld routes expose no specialist names, candidate routes, confidence labels, drafts, or intake questions.
- `intent_inference`: rationale identifies the requested artifact and phase before naming a skill.

## Routing Tiebreakers

Load `references/routing-matrix.md` for uncertainty.

- Go/no-go/traffic shift -> `production-readiness-review`; mobile/app startup/crash/hang/offline release -> `mobile-release-engineering`; canary/rollback metrics -> `progressive-delivery`; narrow artifacts keep specialist; incidents -> `incident-response-and-postmortems`.
- Prefer narrow routes. Commit attempts or general PR/branch/patch/diff reviews -> `agent-pr-review`; surface-specific PRs route narrow.
- Service/worker ownership, even with retries -> `architecture-decisions`; AI-agent repo legibility/names/canonical paths -> `code-readability-for-agents`; retry/timeout/fallback/overload -> `dependency-resilience`.
- HA topology/static capacity -> `high-availability-design`; fault-injection -> `resilience-experiments`; telemetry/alert design -> `observability-and-alerting`; recurring alerts, manual runbook toil, suppression/noise -> `oncall-health`; reliability policy, restore, overload, and invariants stay separate.
- Cross-service database/storage correctness routes to `distributed-data-and-consistency`; in-process states/invariants route to `state-machine-correctness`.
- Keep API compatibility, data contracts, fixtures/goldens/prod samples, hygiene, fleet, events, cache, and pipeline distinct. Fixtures/goldens/prod samples -> `test-data-engineering`; stream/batch/event replay with freshness, validation, reporting trust, no-double-count recovery -> `data-pipeline-reliability`; producer/consumer schema -> `data-contracts`; runtime/client version-skew -> `fleet-upgrades`.
- Corruption/deletion recovery routes to `backup-and-recovery`; query-plan, schema-migration, and database-caused endpoint regressions route to `database-operations`; generic latency/headroom routes to `performance-and-capacity`.
- Flag owner/expiry/fallback/removal -> `feature-flag-lifecycle`; config mutation/generated ops/bulk scripts/preview/validation/caps/rollback -> `configuration-and-automation-safety`.
- Tags/versions/packages/artifact identity/promotion -> `release-build-reproducibility`; local/CI/staging/prod drift -> `dev-environment-parity`; provenance/signing/builder isolation -> `software-supply-chain-security`.
- Desired-state capture, drift detection, reconciliation, emergency infra exceptions -> `infrastructure-and-policy-as-code`.
- Retiring/replacing with no-new-usage checks -> `migration-and-deprecation`; ML promotion/eval/skew/drift/rollback -> `ml-reliability-and-evaluation`.
- Security by artifact: threat model, identity/secrets, cryptography, supply-chain trust, deployed vulnerability, tenant boundary, privacy lifecycle, LLM app risk.
- Docs/runbooks/ADRs owner/source-of-truth/freshness/archive -> `documentation-lifecycle`; AI agent repo rules/protected paths/generated-code acceptance -> `ai-coding-governance`; control maps/scorecards/exceptions -> `engineering-control-evidence`.
- Public edge, service identity/locality, dependency retry, browser release, accessibility, readability, LLM eval/serving/security stay separate; capacity/headroom benefit versus cost/savings -> `cost-aware-reliability`.

## Red Flags - Stop And Rework

- More than two specialists are selected automatically.
- The router chooses from a phrase match without identifying artifact and phase.
- A tool or vendor name drives routing without capability translation, or appears in route text.
- `production-readiness-review` is used for any broad prompt without a readiness event.
- Compliance, staffing, compensation, procurement, or marketing work is routed as engineering work.
- A low-confidence or out-of-scope answer names candidate specialists, prints a routing draft, or exposes the internal shortlist.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Keyword matching | Infer artifact, phase, surface, and risk. |
| Loading every related specialist | Choose one primary and list at most one follow-up. |
| Treating tools as domains | Translate tools to capabilities. |
| Dumping candidate specialists | Infer the narrowest route, or withhold only when no in-scope frame exists. |
| Asking intake questions too soon | Infer from prompt, repo, files, branch context, and conversation first. |
