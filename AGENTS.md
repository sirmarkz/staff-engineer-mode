# AGENTS.md

Operational rules for AI coding agents working in this repository.

## What This Repo Is

This repository publishes one native router skill and routed specialist files
that guide engineering lifecycle, DevOps, operations, reliability, security,
stability, and architecture work toward high-quality practices drawn from
large-scale engineering organizations and public standards.

The repository is not a generic process handbook. The router and specialist
files should stay focused on building, shipping, securing, operating, and
maintaining complex software systems.

## Layout

| Path | Contains |
| --- | --- |
| `skills/staff-engineer-mode/SKILL.md` | The only native skill entrypoint exposed to plugin discovery. |
| `specialists/<specialist-name>.md` | Routed specialist reference files loaded only after the router selects one. |
| `skills/_shared/references/` | Shared source index, contract, synthesis notes, and other reusable reference material. |
| `skills/_shared/assets/` | Reusable templates, checklists, and scaffolds used by skills. |
| `evals/` | Router eval adapter docs. `SAMPLE-PROMPTS.md` is the canonical eval catalog; neither path is runtime skill guidance. |
| `scripts/` | Deterministic validation and packaging helpers. No scripts may generate final skill prose. |
| `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, `.codex/`, `.opencode/`, `gemini-extension.json`, `GEMINI.md` | Cross-tool plugin manifests and install docs. |

## Skill Rules

- Keep each specialist file narrow enough that the router can select it with low noise.
- The router `SKILL.md` and specialist markdown files must not exceed 300 lines.
- Specialist files must be self-sufficient for solo developers. The agent must produce
  complete guidance from local facts and work directly with the user.
  Confirmation means explicit user confirmation or local facts from the work,
  not an outside approval step or waiting point. Adjacent-skill routing is internal skill
  selection, not a delegation of responsibility away from the agent and user.
- When a router or specialist file needs facts about a vendor, upstream project, legal constraint, or
  outside dependency, proceed from user-provided requirements and locally
  available details, marking unknowns explicitly. Do not make the skill depend
  on contacting or waiting for that third party.
- Skill descriptions must be trigger-focused and start with `Use when` unless a
  specialized router format justifies otherwise.
- Final skill prose must be hand-authored. Do not bulk-generate `SKILL.md`
  bodies from templates, tables, scripts, LLM batch output, or search summaries.
  Scripts may validate, move, package, or review skills, but must not be the
  source of truth for skill content.
- Each specialist file must synthesize the relevant references. Read the source notes
  and theme guidance, reconcile the tradeoffs, and write unambiguous operational
  instructions a future agent can follow without guessing.
- Keep only the router in the native `skills/` discovery namespace. Specialist
  guidance lives under `specialists/<specialist-name>.md` and is loaded by
  router instruction, not by plugin registry auto-discovery. Preserve thematic
  grouping through names, router language, and shared references rather than
  nested directories.
- Keep root tool context files thin. `CLAUDE.md` and `GEMINI.md` should
  reference this file and `skills/staff-engineer-mode/SKILL.md`, not duplicate
  routing, specialist-loading, or event-policy rules.
- Keep specialist files technology-agnostic unless the file is explicitly for a
  technology-bound surface such as frontend, mobile, ML, or LLM applications.
  Write guidance in terms of capabilities, contracts, failure modes, checks,
  and artifacts. Do not prescribe a cloud provider, orchestration platform,
  database, framework, vendor product, or tool as the default.
- Individual specialist files should state when not to use them, info to gather, workflow,
  synthesized defaults, exceptions, required outputs, checks before moving on, red flags,
  and common mistakes.
- Normalize competing large-scale engineering practices into one blended default
  unless the context requires a named exception.
- Do not force users to invoke individual specialists by name. The router must
  choose automatically from user intent, with conservative fallback behavior.
- Avoid process-only guidance unless it directly supports engineering lifecycle,
  DevOps, operations, reliability, security, stability, architecture, or
  maintainability work.
- Keep compliance, legal, procurement, staffing, compensation, product strategy,
  and broad governance out of scope unless framed as engineering checks or
  controls for system delivery and operations.

## Documentation

- Write docs for someone who has never seen the repository.
- Keep documentation plain, direct, and technically accurate.
- Cite source-index references from `skills/_shared/references/source-index.md`.
- Use authoritative sources: first-party engineering publications, official
  documentation, standards bodies, peer-reviewed papers, or widely cited
  practitioner references that originated the named pattern. Do not cite
  encyclopedias, Q&A/forum threads, scraped mirrors, SEO summaries, anonymous
  content farms, or unofficial copies when a primary source exists.
- Update references, templates, router fixtures, and validation scripts when
  skill contracts or routing behavior changes.

## Tests And Validation

- Validation protects supported skill contracts, routing behavior, references,
  source-index citations, templates, and artifact shape.
- Avoid tests that only pin incidental wording, heading prose, or implementation
  churn with no supported contract.
- Run repo-local validation scripts before committing skill changes.
- Run `python3 scripts/validate_source_quality.py` before committing source-index
  or citation changes.
- Run `python3 scripts/validate_platform_support.py` before committing plugin
  manifest, install, README, LICENSE, or cross-tool packaging changes.
- Router eval cases come from `SAMPLE-PROMPTS.md`, outside runtime skill paths.
  Keep prompts representative across direct, paraphrased, ambiguous,
  mixed-intent, out-of-scope, and lifecycle-phase routing behavior. Runtime
  router guidance stays in `skills/staff-engineer-mode/references/routing-matrix.md`.
- Do not make live model evals a default CI or routine merge gate. Run them
  manually only when a change needs model-backed evidence, the user explicitly
  asks for them, or the release gate below applies.
- Any change to `hooks/`, hook manifests, event-policy guidance, or specialists
  that control commit/release behavior must clear live Claude and Codex hook
  probes before release. Test commit and release block paths plus
  standalone-receipt allow paths in both hosts, and confirm the model completes
  each probe without command retry loops or hook errors. Run the probes through
  the shared harness so every agent uses the same setup and prompts:

  ```bash
  python3 scripts/run_live_hook_probes.py --host all --event all --probe all
  ```

  The default harness matrix is Claude Opus 4.8 and Codex `gpt-5.5`, both at
  medium and xhigh effort.
- Before tagging or publishing a release, run the one-command live release gate
  manually from the release checkout. Do not add this live gate to GitHub
  Actions. It runs the hook probes and 10 seeded random specialist cases from
  the specialist portion of the 220-case router catalog for Claude Opus 4.8
  xhigh and Codex `gpt-5.5` xhigh. Any hook failure or random-specialist eval
  failure aborts the release:

  ```bash
  python3 scripts/run_release_live_checks.py
  ```

## Code Quality

- Do not use deterministic scripts or LLM batches to author final skill prose.
- Keep scripts focused, readable, and repo-relative.
- Validate inputs and fail with clear errors.
- Do not log sensitive data.
- Prefer simple standard-library tooling unless a dependency improves the
  repository contract.

## Git And Commit Rules

- Keep `main` buildable. Every commit is public history.
- Prefer small, reviewable, production-safe commits.
- Commit subjects use `type(scope): summary`.
- Do not publish release notes, tags, or marketplace releases until the user
  explicitly asks to start releasing.
- Versioned metadata may stay at the pre-release placeholder before public
  release. When the user asks to release, use `scripts/bump-version.sh --check`,
  `scripts/bump-version.sh --audit`, then `scripts/bump-version.sh <new-version>`.
- Release install references are part of the release artifact. Before a release
  is considered complete, update `.claude-plugin/marketplace.json`
  `plugins.0.source.sha` to the plugin artifact commit and keep README/install
  docs on the normal marketplace or Git URL install paths. Claude's marketplace
  entry must pin the plugin artifact with matching `ref` and `sha`. Do not leave
  marketplace metadata pointing at the previous release.
- Plugin manifests and install docs must use HTTPS git URLs for plugin source,
  marketplace add, and install paths. Do not publish SSH `git@github.com` or
  `ssh://` install paths, and do not use Claude marketplace `source: github` or
  owner/repo shorthand for this plugin when an HTTPS git URL can be used.
- Only when the user directly asks to make a release, update
  `RELEASE-NOTES.md` with a concise summary of the user-facing delta since the
  last release. Do not list every commit.
- When completing a user-requested release, do not stop after creating the
  tag. After the tag exists, create the hosted release page for that tag from
  the release notes summary, commit and push the marketplace SHA/docs refresh,
  and verify that fresh Claude, Codex, OpenCode, and fallback install checks
  resolve the intended version from clean temporary config/cache directories.
- Do not add AI assistants, automation, or tools as co-authors or attribution in
  commit messages, file headers, docs, or release notes.
- Do not commit secrets, local `.env` files, private keys, machine-specific
  config, editor state, caches, local Claude review outputs, or unintended
  generated output.
- Run a staged secret scan before committing when the hook is available:

  ```bash
  git diff --cached --name-only --diff-filter=ACMRTUXB -z | xargs -0r detect-secrets-hook --
  ```

- If `detect-secrets-hook` is not installed, run an explicit fallback scan over
  staged content for obvious secret patterns and record the limitation in the
  final response.
- After pushing, check GitHub Actions when available and fix failures with
  follow-up commits.

## Bar A Change Must Clear

1. Repo-local validation scripts pass.
2. Skills, source-index citations, templates, and router fixtures are internally consistent.
3. Cross-tool manifests still support Claude Code, Codex, Cursor, OpenCode, and
   Gemini CLI when packaging artifacts change.
4. Relevant docs, references, templates, and router fixtures are updated.
5. Staged secret scan passes before each commit, or a fallback scan is run when
   the hook is unavailable.
6. `git status` shows only intentional tracked changes before pushing.
