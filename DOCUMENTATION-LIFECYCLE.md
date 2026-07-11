# Documentation Lifecycle

This register is for repository maintainers and coding agents deciding whether
critical engineering guidance is current, authoritative, and ready to publish.

## Documentation Inventory

| Doc | Primary Mode | Operational/Architectural Tag | Responsibility Path | Source Of Truth | Last Verified | Verification Cadence | Staleness Signal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Router and routing matrix | Reference | Operational | Router maintainer | `skills/staff-engineer-mode/SKILL.md`; detailed boundaries in `skills/staff-engineer-mode/references/routing-matrix.md` | 2026-07-10 | Every routing change and release | Slug mismatch, uncovered intent, or canonical eval disagreement |
| Specialist corpus | How-to | Operational | Owning specialist maintainer | `specialists/<slug>.md` | 2026-07-10 | Every specialist change; full review each major release | Unsafe absolute, factual contradiction, boundary drift, or template mismatch |
| Documentation lifecycle register | Reference | Operational | Repository maintainer | `DOCUMENTATION-LIFECYCLE.md` | 2026-07-10 | Every documentation-contract change and major release | Inventory omits a supported surface or names a non-authoritative source |
| Templates and ownership index | Reference | Operational | Owning specialist maintainer | `skills/_shared/assets/templates/README.md` and its listed template | 2026-07-10 | Every Required Outputs change | Required field absent, unindexed template, or unknown owner |
| Source index | Reference | Architectural | Content maintainer | `skills/_shared/references/source-index.md` | 2026-07-10 | Quarterly and before major releases | Superseded standard, failed link check, or obsolete version label |
| Router eval catalogs and harness | Reference | Operational | Router/eval maintainer | `evals/prompts/` and `scripts/run_router_eval.py` | 2026-07-10 | Every routing change | Declared check with zero cases, duplicate case, unbound adversarial provenance, or live route regression |
| Specialist response smoke harness | Reference | Operational | Specialist/eval maintainer | `evals/prompts/specialist-behavior.json` and `scripts/run_specialist_eval.py` | 2026-07-10 | Every specialist response-contract or harness change | Lexical check drift, unsafe catalog path, unreviewed failure, or lexical score presented as semantic evidence |
| Hook and event policy | How-to | Operational | Hook maintainer | `hooks/agent-event-policy` plus `skills/staff-engineer-mode/references/agent-event-policy.md` | 2026-07-10 | Every hook or event-policy change | Documented command is not intercepted or a protected composition bypasses review |
| Install documentation | How-to | Operational | Platform/package maintainer | `README.md`, `.codex/INSTALL.md`, `.cursor-plugin/INSTALL.md`, and `.opencode/INSTALL.md`; README owns Claude, Copilot, and Gemini instructions where no separate install doc exists | 2026-07-10 | Every release and supported-CLI change | Command help changes or clean install fails |
| Manifests and version metadata | Reference | Operational | Package maintainer | Platform manifests plus `package.json` | 2026-07-10 | Every release | Version, ref, SHA, description, or path mismatch |
| Contributor and release rules | Reference | Operational | Repository maintainer | `AGENTS.md`, `CONTRIBUTING.md`, and `scripts/bump-version.sh` | 2026-07-10 | Every repository-contract change | Two documents prescribe incompatible behavior |

## Source-Of-Truth Rule

One canonical location owns each contract. Summaries link to the canonical
location and must not silently redefine it. Duplicates are generated, marked
non-authoritative, or removed.

## Current-State Verification

| Surface | Claimed State | Verification Source | Current/Future | Last Verified |
| --- | --- | --- | --- | --- |
| Topology | One native router and 64 routed specialists | Skill-pack validator and filesystem inventory | Current | 2026-07-10 |
| Template ownership | Every specialist owns at least one indexed artifact template | Skill-pack template contract validation | Current | 2026-07-10 |
| Routing | Positive, boundary, split-access adversarial, and mixed-intent contract catalogs are canonical | Router-eval validator | Current | 2026-07-10 |
| Specialist response evidence | Manual, non-gating `lexical_smoke`; review representative passes and every failure, and never treat lexical scores as semantic or release-gate evidence | Specialist harness unit tests and saved manual run artifacts | Current; model-backed evidence is manual | 2026-07-10 |
| Recovery and protected commands | Commit and release command classes use receipt-gated hooks where supported | Hook regression tests and manual live probes | Current; live host evidence required after hook changes | 2026-07-10 |
| Platform support | Claude Code, Codex, Cursor, OpenCode, Copilot CLI, and Gemini CLI have package surfaces | Platform validator and per-platform clean-install checks | Current; Windows Cursor remains a release smoke target | 2026-07-10 |

## Freshness Rules

| Doc Class | Verification Cadence | Staleness Signal | Required Action |
| --- | --- | --- | --- |
| Router/specialist guidance | On every behavior change | Eval failure, contradiction, unsafe claim, or changed engineering contract | Correct prose, template, ownership notes, and evals together |
| Operational hooks and release procedure | On every change and before release | Hook retry loop, unprotected command class, retained credential, or order mismatch | Block release until regression and live probes pass |
| Install docs and manifests | Every release | CLI help or manifest schema changes; clean install fails | Update docs, validator, and clean-install evidence |
| Source index | Quarterly and before major release | Replacement publication, redirect, failed link, or historical source presented as current | Add current source and mark retained predecessor historical |

## Docs-As-Code Workflow

1. Change the canonical contract and its directly affected docs together.
2. Update specialist templates and ownership notes with Required Outputs.
3. Update positive, boundary, split-access adversarial, and contract evals when routing behavior changes.
4. Run Markdown/local-link checks, repository validators, and relevant tests on
   every pull request.
5. Run external link/version checks on a schedule so network instability does
   not make ordinary pull requests flaky.
6. Record live hook and model-eval evidence only when repository policy requires it.

## Operational Document Freshness

| Operational Document | Source Of Truth | Freshness Trigger | Last Verified |
| --- | --- | --- | --- |
| Commit/release event policy | Hook implementation and event-policy reference | Protected command or receipt behavior changes | 2026-07-10 |
| Release procedure | `AGENTS.md` and `scripts/bump-version.sh` | Version, tag, marketplace, hosted-release, or install-verification order changes | 2026-07-10 |
| Live hook probes | `scripts/run_live_hook_probes.py` | Host CLI, hook schema, authentication, or probe contract changes | 2026-07-10 |
| Live router release gate | `scripts/run_release_live_checks.py` | Model, eval catalog, sampling, or threshold changes | 2026-07-10 |
| Specialist response smoke harness | `scripts/run_specialist_eval.py` and `evals/prompts/specialist-behavior.json` | Specialist contract, adapter isolation, catalog, or scoring changes | 2026-07-10 |

## Findability Check

| Reader Task | Search Path | Expected Doc | Gap Signal |
| --- | --- | --- | --- |
| Change a specialist artifact | Specialist Required Outputs → template ownership index | Owning template | No exact owner row or template path |
| Change routing | Router → routing matrix → eval catalog | Boundary and contract cases | No case represents the changed intent |
| Change release behavior | `AGENTS.md` → bump script → live gate | One ordered release flow | Sequence differs between documents |
| Update a named standard | Source index freshness contract | Current and historical entries | Superseded entry is unmarked or replacement absent |
