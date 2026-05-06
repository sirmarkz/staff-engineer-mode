# AGENTS.md

Operational rules for AI coding agents working in this repository.

## What This Repo Is

This repository publishes a set of Codex skills that route engineering lifecycle,
DevOps, operations, reliability, security, stability, and architecture work toward
high-quality practices drawn from large-scale engineering organizations and
public standards.

The repository is not a generic process handbook. Skills should stay focused on
building, shipping, securing, operating, and maintaining complex software
systems.

## Layout

| Path | Contains |
| --- | --- |
| `skills/<skill-name>/SKILL.md` | One hand-authored skill in the flat plugin discovery namespace. |
| `skills/_shared/references/` | Shared source index, contract, synthesis notes, and other reusable reference material. |
| `skills/_shared/assets/` | Reusable templates, checklists, and scaffolds used by skills. |
| `scripts/` | Deterministic validation and packaging helpers. No scripts may generate final skill prose. |
| `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, `.codex/`, `.opencode/`, `gemini-extension.json`, `GEMINI.md` | Cross-tool plugin manifests and install docs. |

## Skill Rules

- Keep each skill narrow enough that the router can select it with low noise.
- `skills/<skill-name>/SKILL.md` files must not exceed 300 lines.
- Skills must be self-sufficient for solo developers. The agent must produce
  complete guidance from local evidence and work directly with the user.
  Confirmation means explicit user confirmation or recorded evidence, not an
  outside gate or waiting point. Adjacent-skill routing is internal skill
  selection, not a delegation of responsibility away from the agent and user.
- When a skill needs facts about a vendor, upstream project, legal constraint, or
  outside dependency, proceed from user-provided requirements and locally
  available evidence, marking unknowns explicitly. Do not make the skill depend
  on contacting or waiting for that third party.
- Skill descriptions must be trigger-focused and start with `Use when` unless a
  specialized router format justifies otherwise.
- Final skill prose must be hand-authored. Do not bulk-generate `SKILL.md`
  bodies from templates, tables, scripts, LLM batch output, or search summaries.
  Scripts may validate, move, package, or review skills, but must not be the
  source of truth for skill content.
- Each skill must synthesize the relevant references. Read the source notes
  and theme guidance, reconcile the tradeoffs, and write unambiguous operational
  instructions a future agent can follow without guessing.
- Keep skills in a flat `skills/<skill-name>/SKILL.md` namespace so plugin
  registries can discover them directly. Preserve thematic grouping through
  names, router language, and shared references rather than nested directories.
- Keep skills technology-agnostic unless the skill is explicitly for a
  technology-bound surface such as frontend, mobile, ML, or LLM applications.
  Write guidance in terms of capabilities, contracts, failure modes, evidence,
  and artifacts. Do not prescribe a cloud provider, orchestration platform,
  database, framework, vendor product, or tool as the default.
- Individual skills should state when not to use them, required inputs, workflow,
  synthesized defaults, exceptions, required outputs, evidence gates, red flags,
  and common mistakes.
- Normalize competing large-scale engineering practices into one blended default
  unless the context clearly requires a named exception.
- Do not force users to invoke individual skills by name. The router must choose
  automatically from user intent, with conservative fallback behavior.
- Avoid process-only guidance unless it directly supports engineering lifecycle,
  DevOps, operations, reliability, security, stability, architecture, or
  maintainability work.
- Keep compliance, legal, procurement, staffing, compensation, product strategy,
  and broad governance out of scope unless framed as engineering evidence or
  controls for system delivery and operations.

## Documentation

- Write docs for someone who has never seen the repository.
- Keep documentation plain, direct, and technically accurate.
- Cite sources by stable source IDs from `skills/_shared/references/source-index.md`.
- Use authoritative sources: first-party engineering publications, official
  documentation, standards bodies, peer-reviewed papers, or widely cited
  practitioner references that originated the named pattern. Do not cite
  encyclopedias, Q&A/forum threads, scraped mirrors, SEO summaries, anonymous
  content farms, or unofficial copies when a primary source exists.
- Update references, templates, router fixtures, and validation scripts when
  skill contracts or routing behavior changes.

## Tests And Validation

- Validation protects supported skill contracts, routing behavior, references,
  source IDs, templates, and artifact shape.
- Avoid tests that only pin incidental wording, heading prose, or implementation
  churn with no supported contract.
- Run repo-local validation scripts before committing skill changes.
- Run `python3 scripts/validate_source_quality.py` before committing source-index
  or citation changes.
- Run `python3 scripts/validate_platform_support.py` before committing plugin
  manifest, install, README, NOTICE, or cross-tool packaging changes.
- Router fixtures live with the router skill and should include direct,
  paraphrased, ambiguous, mixed-intent, and out-of-scope prompts.

## Code Quality

- Do not use deterministic scripts or LLM batches to author final skill prose.
- Keep scripts focused, readable, and repo-relative.
- Validate inputs and fail with clear errors.
- Do not log sensitive data.
- Prefer simple standard-library tooling unless a dependency clearly improves the
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
- Only when the user directly asks to make a release, update
  `RELEASE-NOTES.md` with a concise summary of the user-facing delta since the
  last release. Do not list every commit.
- When completing a user-requested release, do not stop after creating the
  tag. After the tag exists, create the hosted release page for that tag from
  the release notes summary and verify that the page links to the tag/artifacts.
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
2. Skills, source IDs, templates, and router fixtures are internally consistent.
3. Cross-tool manifests still support Claude Code, Codex, Cursor, OpenCode, and
   Gemini CLI when packaging artifacts change.
4. Relevant docs, references, templates, and router fixtures are updated.
5. Staged secret scan passes before each commit, or a fallback scan is run when
   the hook is unavailable.
6. `git status` shows only intentional tracked changes before pushing.


<claude-mem-context>
# Memory Context

# [staff-engineer-mode] recent context, 2026-05-06 12:57pm PDT

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (19,690t read) | 351,247t work | 94% savings

### May 6, 2026
S685 Review and provide feedback on whether a comprehensive API design standards document should be integrated into the skill pack, what should be added, and what should be avoided before implementation begins. (May 6, 11:01 AM)
S684 Review whether a comprehensive API design standards document (covering operation naming, attributes, pagination, filtering, batch operations, idempotency, exceptions, and backward compatibility) should be added as a new skill or integrated into existing structures; provide feedback before proceeding with implementation. (May 6, 11:01 AM)
S686 Review comprehensive API design standards for integration into staff-engineer-mode skill pack; provide recommendations before proceeding with implementation. (May 6, 11:02 AM)
S687 API design standards document integration into skill framework—review applicability, identify additions needed, implement with approval, and validate all changes (May 6, 11:02 AM)
S688 Comprehensive exploration and understanding of the existing skill framework structure, validation patterns, and architectural design across multiple reliability and operations domains (May 6, 11:03 AM)
S689 Integrate availability-principles content into existing skills rather than creating a new skill; distribute guidance across 11 target skills with focused router eval cases and targeted enhancements (May 6, 11:08 AM)
S690 Continue patching availability-principles content into target skills; enhance progressive-delivery with bake-time patterns, fault-domain sequencing, and post-deploy mitigation guidance (May 6, 11:11 AM)
S691 Enhance dependency-resilience/SKILL.md with adaptive retry budget patterns, overload signal handling, and partial batch outcome guidance (May 6, 11:11 AM)
S692 Plan LLM application security skill content and scope; decide between adding to existing skill vs. creating new skill; identify adjacent skills and content boundaries (May 6, 11:11 AM)
457 11:55a ✅ Staff-engineer-mode router skill refactored to use "select" and "covers"
458 11:56a 🔵 Grep confirms ownership refactoring complete; remaining uses are legitimate
459 " ✅ Final refactoring pass: 5 skills updated for ownership-to-maintenance shift and routing-to-use
460 12:02p ✅ Refactored operational skills terminology from maintainer/approval language to change-path/responsibility language
461 12:03p ✅ Extended terminology refactoring across 10 additional skills from owner/approval language to responsibility/confirmation language
462 " ✅ Completed comprehensive terminology refactoring across 14 core skills from ownership/approval to responsibility/confirmation language
463 12:04p ✅ Skill pack validation confirms successful completion of terminology refactoring across all 56 skills
464 " 🔵 Post-refactoring quality validation initiated to verify skills prose supports autonomous operation
465 12:07p 🔵 Comprehensive deep-dive review initiated to validate self-sufficiency of refactored skills
466 12:17p ⚖️ Skill pack review process for solo-developer self-sufficiency
467 12:19p 🔵 Skill pack review findings: responsibility deferrals, documentation style, content duplication
468 12:20p 🔵 Skill descriptions violating trigger-focused format requirement
469 12:21p 🔵 Pattern: "Use to" description violations and bounded-context map duplication
470 12:22p 🔵 Continued description format violations and responsibility deferral pattern
471 12:23p 🔵 Systemic MAINTAINER role embedding in Iron Laws creates responsibility deferral
472 12:24p 🔵 MAINTAINER deferral embedded in data models and continued description format violations
473 12:25p 🔵 Continued "Use to" description format violations
474 12:27p 🔵 MAINTAINER deferrals in input data collection and Iron Laws; continued format violations
475 12:28p 🔵 MAINTAINER embedded throughout Iron Laws and workflow steps as required actor
476 12:29p 🔵 Description format violation and Iron Law/Core principle duplication
477 12:30p 🔵 Multiple "Use to" format violations and MAINTAINER deferrals in LLM/incident skills
478 12:31p 🔵 More description format violations and Response Quality Bar MAINTAINER deferral
479 12:32p 🔵 Continued description format violations and oncall-health MAINTAINER assignment pattern
480 12:33p 🔵 MAINTAINER in Red Flags anti-pattern and another description format violation
481 12:34p 🔵 Critical deferral: production-readiness-review strips decision authority; format violation
482 12:35p 🔵 Iron Law with MAINTAINER requirement; two more description format violations
483 12:36p 🔵 MAINTAINER deferrals in Iron Laws and workflows; multiple format violations
484 12:37p 🔵 Two more description format violations
485 12:38p 🔵 Final batch: MAINTAINER Iron Laws, format violation, and grammatical error evidence of mechanical replacement
486 " ⚖️ Skill pack remediation plan established with four systematic phases
487 " 🔵 Comprehensive skill pack audit report generated: full remediation scope identified
488 " ✅ Bulk description format fix applied to all 56 skills
489 12:39p 🔵 Comprehensive MAINTAINER deferral inventory across skill pack: 300 lines of instances
490 " ✅ Bulk MAINTAINER removal from Response Quality Bars and enumerated sections
491 " 🔵 Remaining MAINTAINER references after bulk removal: ~150 instances across 7287 lines
492 12:40p ⚖️ Phase 3 updated: shift from bulk fixes to targeted scanning and patching
493 " 🔵 Scanning complete: remaining MAINTAINER references (~120 instances) plus approval/ownership in metadata
494 12:41p ✅ Targeted responsibility reframing patches applied to 5 files
495 12:44p ✅ Shift skill governance from human maintainers to documented procedures and executable processes
496 12:45p ✅ Extended maintainer-to-procedure refactoring to four additional staff-engineer-mode skills
497 12:50p 🔵 Brand voice linting violations found in README.md
498 " 🔵 Skill pack validation confirms 56 skills with line-length constraints enforced
499 " 🔵 Self-review validation confirms 56 skills meet line-length and content constraints
500 " 🔄 Comprehensive skill pack refactoring reduces all skills to meet 300-line constraint
501 12:51p ✅ Skill pack refactored with systematic terminology shift from organizational ownership to user/evidence-based responsibility
502 " 🔵 Router evaluation suite validates 102 test cases across routing decision patterns and intent inference
503 " ✅ Template artifacts updated to replace Maintainer columns with Responsibility/Response Path terminology
504 12:52p ✅ Core reference materials and router evaluation set updated with unified terminology shift
505 " ✅ Final terminology cleanup removes last organizational role reference from router test cases
506 " 🔵 Refactoring validation confirms complete removal of organizational terminology and fault-domain language
S693 Enforce 300-line skill constraint and refactor entire skill pack from organizational ownership models to evidence-based responsibility models (May 6, 12:53 PM)
**Investigated**: User's initial request to add skills must not exceed 300 lines constraint; validation revealed it was already partially in place but needed enforcement across all 56 skills and supporting documentation. Comprehensive audit of organizational terminology (maintainer, owner, team, reviewer, approval, defer, escalate, handoff, load-bearing) across skills, templates, routing infrastructure, and governance documents.

**Learned**: The constraint existed but was not systematically enforced. All 56 skills required refactoring to remove organizational role-based language and replace with responsibility/evidence-based language suited for solo developers and agent-driven workflows. Architectural terminology shift required updates across: skill bodies, artifact templates, routing matrices, synthesis guidelines, 102 router test cases, and validation infrastructure.

**Completed**: Comprehensive refactoring completed: 56 skill files refactored with 3,085 net line deletions ensuring all skills ≤300 lines; 12 artifact templates updated replacing Maintainer columns with Responsibility/Response Path terminology; AGENTS.md expanded with explicit rules for self-sufficient skills and third-party independence; validation infrastructure enhanced with line-count checks, duplicate fragment detection, description format validation, and frontmatter shape checking; all organizational/ownership terminology removed from skill bodies and core documents; all grep validations confirm zero deprecated terminology in skill guidance; all 76 modified files staged in git; complete validation suite passing (56 skills pass validation, 102 router test cases pass, 254 sources pass quality, 7 platforms confirmed, 60 files pass brand voice linting, 33 unit tests pass, 0 whitespace issues).

**Next Steps**: Session work is complete. All refactoring changes are staged and ready for commit. No active development underway. Repository is in valid state with all constraint enforcement in place and all terminology reterminology finished.


Access 351k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>