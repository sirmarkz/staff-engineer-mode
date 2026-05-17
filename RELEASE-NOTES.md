# Staff Engineer Mode Release Notes

## 1.5.1 - 2026-05-16

Operational guidance patch.

- Tightens operational specialist guidance across release, resilience,
  observability, on-call, performance, platform, API, and data surfaces with
  more concrete checks and plainer developer wording.
- Clarifies on-call health routing so direct responder interruption, rotation
  load, escalation, and handoff work routes to `oncall-health`, while
  telemetry, SLO, and capacity alert design stays with the narrower specialist.
- Updates sample prompts and router fixtures around on-call health and adjacent
  operational surfaces so common wording continues to route correctly.

## 1.5.0 - 2026-05-15

Flattened specialist file release.

- Moves routed specialists from nested `specialists/<slug>/SKILL.md` paths to
  flat `specialists/<slug>.md` files, keeping only the router in native skill
  discovery.
- Updates Claude Code, Cursor, OpenCode, Codex, GitHub Copilot CLI, and Gemini
  packaging/docs so routed work loads the selected flat specialist file.
- Adds shared bootstrap and manifest contract checks so install surfaces,
  descriptions, and routing load paths stay aligned across supported tools.
- Refreshes routing eval terminology and reusable templates with plainer
  everyday developer language.

## 1.4.2 - 2026-05-13

Clean-machine Claude install fix.

- Changes Claude Code and GitHub Copilot CLI marketplace add examples to use
  the full HTTPS git URL with a `.git` suffix, avoiding the owner/repo
  shorthand path that can make Claude try SSH first on fresh machines.
- Keeps the Claude marketplace plugin source pinned to the HTTPS git URL and
  adds validation so future README examples do not drift back to owner/repo
  shorthand.
- Clarifies repo agent instructions so plugin source, marketplace add, and
  install paths all stay on HTTPS git URLs.

## 1.4.1 - 2026-05-13

Claude marketplace install fix.

- Changes the Claude marketplace plugin source to a pinned HTTPS git URL so a
  clean machine can install without pre-seeding GitHub SSH host keys.
- Splits two-step README install flows into separate copyable command blocks
  for Claude Code and GitHub Copilot CLI.
- Adds repo guidance and validation coverage to keep shipped plugin install
  paths on HTTPS git URLs instead of SSH-style GitHub paths.

## 1.4.0 - 2026-05-13

Specialist language simplification release.

- Rewrites specialist intake and completion sections in everyday developer
  language, replacing formal control wording with plainer "info to gather" and
  "checks before moving on" framing across the routed specialist pack.
- Tightens specialist Iron Laws and trigger descriptions so new-system design
  work and existing-system review work both route to the right specialist when
  applicable.
- Updates sample prompts to cover both new and existing systems where relevant,
  and verifies the full 216-prompt sample set live through Claude Code and
  Codex.
- Clarifies README sources and influences as the intersection of strongest
  publicly documented practices from leading software engineering
  organizations, with stable source IDs retained in the shared source index.

## 1.3.2 - 2026-05-11

Router precedence release.

- Adds a `## Precedence Over Generic Process Packs` section to the router
  skill declaring Staff Engineer Mode runs first on any engineering-system
  prompt. The section names the engineering surfaces explicitly and lists
  the natural-language phrasings (`build X`, `design X`, `make X reliable`,
  `plan a rollout`, `review this service`, `investigate this incident`,
  etc.) that must NOT be routed to `superpowers:brainstorming` or
  `superpowers:writing-plans` as the first response.
- Mirrors the same `<EXTREMELY-IMPORTANT>` precedence block at the top of
  the SessionStart hook output (Claude Code, Cursor) and the OpenCode
  plugin bootstrap so the override reaches the model before any generic
  process pack can load.
- Verified live on Claude Code and Codex with five prompts spanning HA
  design, incident response, and production readiness. All five route to
  the right specialist with zero brainstorming detours. The earlier
  symptom -- typing "i want to build a highly available system" and
  getting a `superpowers:brainstorming` intake flow instead of HA
  guidance -- no longer occurs.
- Bumps the router word budget from 1800 to 2000 to accommodate the new
  precedence section.

## 1.3.1 - 2026-05-11

Router load-contract hardening release.

- Adds a top-level `## Load Contract` block to the router skill spelling out
  three mandatory rules: use the Read tool to open the routed specialist,
  never call the Skill tool on a specialist slug, and complete the Read
  before producing routed engineering guidance.
- Drops the obsolete `../../specialists/<slug>/SKILL.md` relative path from
  the router workflow; the Load Contract now carries platform-specific
  absolute path fallbacks for Codex, Gemini, and any host that does not
  publish `SPECIALIST_ROOT` at session start.
- Front-loads `SPECIALIST_ROOT=` and an explicit `LOAD:` directive in the
  Claude Code SessionStart hook, the Cursor SessionStart hook (shared
  script), and the OpenCode plugin bootstrap so the load path is the first
  signal the model sees on those hosts.
- Documents the router-borne contract in `GEMINI.md` and `.codex/INSTALL.md`
  for hosts that have no runtime hook today.
- Adds the `no_skill_invoke` and `read_load` gates to the router eval
  scorer. The Skill-call detector catches plain, quoted, and colon-form
  invocations against any specialist slug; the Read-load detector flags
  substantive answers that lack a Read of the routed slug's `SKILL.md`.
  Every confidently-routed sample prompt now requires both gates.
- Extends the skill-pack validator with a Load Contract assertion: the
  section must sit between `## Iron Law` and `## Overview`, contain all
  three rule fragments, mention the platform fallback markers, and not
  carry the obsolete relative path.
- Bumps the router word budget from 1600 to 1800 to accommodate the new
  section.
- Verified live on Claude Code (Read of
  `specialists/high-availability-design/SKILL.md` captured via stream-json,
  zero Skill calls) and Codex (specialist file loaded via the host's native
  file-read verb, zero Skill calls) after a clean uninstall and reinstall
  from the v1.3.1 tag.

## 1.3.0 - 2026-05-10

Engineering-surface cleanup and live-routing hardening release.

- Removes the generic `code-review-and-workflow` specialist. Review-system
  design, reviewer routing, change-size policy, ownership workflow, and DORA
  process prompts no longer route unless the request names a concrete
  engineering surface; the pack now routes to 54 engineering specialists.
- Keeps the lifecycle-routing model from 1.2.0 focused on engineering decisions
  across ideation, design, development, testing, release, operation, and
  maintenance. Concrete diffs still route to `agent-pr-review`; surface-specific
  design, rollout, security, data, accessibility, migration, and test evidence
  routes to the narrow specialist that should guide the decision.
- Reorganizes the README catalog so process-adjacent specialists live in a final
  `Engineering workflow, readiness, and evidence` category, while delivery,
  operations, platform, security, client, data, and reliability categories stay
  engineering-surface first.
- Narrows `engineering-control-evidence` into a cross-surface engineering
  evidence aggregator, not a compliance or workflow-management specialist.
  Single-surface evidence stays with the matching specialist; cross-surface
  scorecards, exception registers, and evidence packs stay here.
- Hardens router and matrix boundaries from live Claude and Codex routing:
  deprecation PRs, ML model promotion, frontend field/lab release gates,
  static-analysis hygiene, cross-service database/storage correctness,
  high-availability failover evidence, and desired-state infrastructure drift
  now route to the intended engineering specialists.
- Removes paging/page wording from engineering-surface specialists where
  responder interruption is not the primary workflow, and adds validation so
  page language remains limited to workflow, readiness, and evidence
  specialists.
- Updates Claude, Codex, Cursor, OpenCode, Gemini, and package metadata to the
  1.3.0 release line.

## 1.2.0 - 2026-05-10

Lifecycle-aware specialist routing release.

- Repositions the router and specialists for ideation, design, development,
  testing, release, operation, and maintenance guidance instead of
  after-the-fact review.
- Clarifies review routing so concrete diffs, readiness decisions, and
  surface-specific design reviews route to the right specialist.
- Adds lifecycle and review-routing eval cases, plus live Claude and Codex smoke
  coverage for pre-code design routing.

## 1.1.0 - 2026-05-10

Router and marketplace refresh release.

- Compacts the native router tiebreakers while preserving detailed adjacent
  routing boundaries in the bundled routing matrix.
- Tightens router output discipline from live smoke testing: routine mechanical
  docs edits stay out of Staff Engineer Mode, out-of-scope answers do not leak
  specialist names, and eval routing blocks avoid repeating tool names from
  prompts.
- Updates Claude marketplace, Codex, Cursor, OpenCode, Gemini, and package
  metadata to the 1.1.0 release line.

## 1.0.0 - 2026-05-09

Stable release.

- Marks the router-and-specialist architecture (one native router skill, 55
  routed specialist files) as stable for downstream listings, plugin
  directories, and integrations.
- Aligns plugin and marketplace descriptions to a single capability-focused
  summary suitable for plugin directory listings.
- No skill content, routing behavior, or supported-tools changes since 0.10.1.

## 0.10.1 - 2026-05-09

Copy clarification release.

- Clarifies that Staff Engineer Mode installs one native router skill and routes
  to specialist files, not separately listed specialist skills.
- Updates root documentation to use tool-neutral language for supported
  runtimes and the router-only package shape.
- Removes local Claude memory context from `AGENTS.md` so repository
  instructions stay portable and public-safe.

## 0.10.0 - 2026-05-09

Router-only native skill release.

- Keeps only the Staff Engineer Mode router in native skill discovery while
  moving all routed specialist files under `specialists/`, reducing native
  skill-listing overhead across supported tools.
- Teaches the router to load selected specialist files by path after classification,
  so users can ask natural engineering questions without naming specialist
  files or invoking separate skills.
- Updates Claude, Codex, Cursor, OpenCode, Gemini, validation scripts, and docs
  for the router-only package shape.
- Validates live Claude and Codex routing across all 55 specialists after the
  restructure.

## 0.9.0 - 2026-05-08

Routing quality and metadata efficiency release.

- Hardens Staff Engineer Mode routing and sample prompts so natural engineering
  requests route cleanly without users naming individual skills.
- Shortens Codex skill-discovery metadata while preserving the specialist
  routing boundaries validated by the full sample-prompt suite.
- Aligns the human contributor style guide and routing reference with the
  compact, skill-focused authoring rules used by the pack.

## 0.8.0 - 2026-05-07

AWS Builders' Library guidance pass and phase-based navigation aid.

- Tightens 10 specialist skills with technical defaults sourced from the
  AWS Builders' Library: structured-log baseline fields and trace/span
  propagation contract; per-hop timeout calibration, token-bucket retry
  budget, AIMD over binary breakers, per-dependency pool sizing,
  server-side overload defaults (LIFO, deadline propagation,
  observe-before-enforce, shed-metric visibility), shallow liveness +
  health-endpoint capacity reservation; canary-slice scoping and
  two-thirds rolling-deploy capacity floor; pre-classified rollback
  safety dimensions; named expand/migrate/transition/contract phases
  with per-phase rollback safety; cache hit-rate operating-point
  alarming; constant-work-pattern guidance; dual-credential overlap
  rotation with verify-zero-old-traffic gate plus renewal-runway
  default.
- Adds `OE-PHASE-MAP.md` at the repo root: a phase-based navigation aid
  (Foundations / Design & Build / Develop & Test / Deploy & Operate /
  Monitor & Respond / Improve) with one-line descriptions per skill.
  README links to it next to `SAMPLE-PROMPTS.md`.
- Adds 7 AWS Builders' Library entries to the source index (S284-S290):
  Ensuring Rollback Safety, Instrumenting Distributed Systems, Building
  Dashboards, Going Faster with CD, Dependency Isolation, Minimizing
  Correlated Failures, Caching Challenges and Strategies.

## 0.7.0 - 2026-05-06

Self-sufficient skill guidance release.

- Refactors the skill catalog so guidance works directly for solo developers:
  skills now use local evidence, explicit user decisions, and executable
  response paths instead of external responsibility chains.
- Consolidates all specialist `SKILL.md` files under the 300-line cap while
  preserving operational sections, evidence gates, red flags, and common
  mistakes.
- Adds stronger API design, availability, dependency resilience, LLM
  application security, data lifecycle, and release-safety guidance across the
  relevant specialist skills.
- Updates shared templates, router fixtures, and routing notes to match the
  evidence-based responsibility model.
- Strengthens validation with line-count enforcement, duplicate-content checks,
  description trigger checks, frontmatter shape checks, and newline checks.

## 0.6.0 - 2026-05-05

Performance optimizations across the skill catalog.

## 0.5.0 - 2026-05-04

Repositioning and quality release.

- Repositions the pack around "the senior reviewer your AI coding agent is
  missing." New README hero, supporting line, and category framing
  (`COMPARISON.md`) against neighboring skill packs.
- Adds six specialist skills: `agent-pr-review` (default pre-merge review for
  any diff, human or AI), `feature-flag-lifecycle`, `llm-serving-cost-and-latency`,
  `code-readability-for-agents`, `test-data-engineering`, `dev-environment-parity`.
- Renames two skills for discoverability: `crypto-lifecycle` →
  `cryptography-and-key-lifecycle`; `correctness-and-formal-methods` →
  `state-machine-correctness`.
- Solo-dev usability pass across 54 specialist `SKILL.md` files. Every skill
  now scales from a single developer up; multi-team-required skills carry
  explicit enterprise-context annotations rather than being scaled past
  usefulness.
- Prescriptive frontmatter pass: 54 description fields rewritten from
  descriptive ("Use when X is central") to prescriptive ("Use to do Y") in
  plain language with concrete trigger phrases that disambiguate from neighbors.
- Sharper Iron Laws across the pack, with two-clause coverage on skills that
  bundle distinct concerns (incident response + postmortem; telemetry +
  alerting; review policy + productivity metrics).
- Adds top-level `MAINTAINERS.md` with named human attribution, `STYLE.md`
  voice principles, and `docs/screencast-script.md` recording plan.
- Adds brand-voice CI linter (`scripts/lint_brand_voice.py`) with 29 unit
  tests and a GitHub Actions workflow that fails PRs on FAANG name-drops in
  openings, marketing adjectives in headlines, hedging in headlines, vendor
  names in specialist prose, and missing Iron Laws.
- Repository moved from `tnilabs/staff-engineer-mode` to
  `sirmarkz/staff-engineer-mode`. Install URLs updated everywhere.

## 0.4.0 - 2026-05-02

Skill naming and router quality release.

- Shortens specialist skill names to plainer slugs and updates sample prompts,
  routing fixtures, and routing matrix references to match.
- Adds the router evaluation harness for scoring routing responses across
  direct, paraphrased, ambiguous, mixed-intent, and out-of-scope prompts.
- Removes wording-only validation checks while preserving behavior and contract
  gates for skill structure, evidence gates, install paths, and platform
  support.

## 0.3.0 - 2026-05-02

Skill expansion release.

- Adds nine specialist skills covering accessibility release gates, AI-assisted
  coding governance, configuration safety, certificate lifecycle, data
  contracts, documentation lifecycle, experimentation guardrails, fleet upgrade
  version skew, and LLM evaluation harnesses.
- Adds reusable templates for the new skill surfaces and expands sample prompts
  so users can exercise the added routing paths.
- Updates shared references, synthesis notes, router fixtures, and README
  positioning for the expanded skill pack.

## 0.2.0 - 2026-05-02

Documentation and metadata update.

- Adds sample prompts and compact skill metadata to make routing behavior easier
  to inspect and try.
- Improves README guidance for contribution, installation, and footer
  organization.
- Reorganizes shared source references by owner for easier maintenance.

## 0.1.0 - 2026-05-02

First public release.

- Adds the Staff Engineer Mode router and 40 specialist engineering skills across architecture, reliability, delivery, operations, security, privacy, data, platform, client, ML, LLM application, and cost-aware reliability work.
- Supports Claude Code, Codex, Cursor, OpenCode, GitHub Copilot CLI, and Gemini CLI plugin or skill installation paths.
- Includes deterministic validation for source quality, skill contracts, router fixtures, platform support, version metadata, plugin syntax, and whitespace.
- Publishes shared references, templates, and evidence-gate conventions for technology-agnostic engineering guidance.
