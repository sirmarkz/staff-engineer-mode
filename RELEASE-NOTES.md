# Staff Engineer Mode Release Notes

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
