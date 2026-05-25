# Contributing

Operational rules for human contributors writing or reviewing skill prose in
this repository.

This is the human-facing companion to [AGENTS.md](AGENTS.md). `AGENTS.md`
tells coding agents how to work in the repo. This file tells people what good
skill content looks like before they open a PR.

## What This Repo Publishes

This repository publishes one native router skill and routed specialist files
that guide engineering lifecycle, DevOps, operations, reliability, security,
stability, and architecture work toward reviewable engineering practice.

It is not a generic process handbook, a role-play pack, or a catalog of famous
company habits. The router and specialist files should stay focused on
building, shipping, securing, operating, and maintaining complex software
systems.

## What A Skill Must Do

A skill is useful when it changes what the coding agent does in a concrete
engineering situation.

Each specialist file should:

- State when the router should select it.
- State when not to use it.
- Give the agent an operational workflow it can follow from local context.
- Name details to gather, required outputs, checks before moving on, red flags, and common
  mistakes.
- Produce artifacts a reviewer can inspect: risks, blockers, owners, rollout
  checks, rollback paths, exceptions, runbooks, matrices, or test results.
- Mark unknowns explicitly instead of pretending outside facts are known.
- Keep the agent responsible for the work with the user. Do not defer the core
  decision to an outside team, vendor, committee, or future confirmation.

If a draft only gives background, motivation, or a reading list, it is not a
useful specialist file yet.

## Skill Authoring Rules

- Keep each specialist file narrow enough that the router can select it with low noise.
- Keep `skills/staff-engineer-mode/SKILL.md` and `specialists/<specialist-name>.md` under 300 lines.
- Use `skills/` only for the native router entrypoint; routed specialist files live under `specialists/`.
- Frontmatter descriptions start with `Use when` and describe the trigger, not
  the feature.
- Names are lowercase and hyphenated. Prefer
  `<surface>-<action-or-artifact>` or `<artifact>-and-<scope>`.
- Do not use vendor names, tool names, emoji, or persona names in skill names.
- Final skill prose is hand-authored. Do not bulk-generate `SKILL.md` bodies
  from templates, tables, scripts, LLM batch output, or search summaries.
- Scripts may validate, package, move, or review skill files. Scripts must not be the
  source of truth for final skill prose.
- A specialist file may route to an adjacent specialist, but it must still produce useful
  guidance for the current user request.
- Do not force users to invoke specialist files by name. Router language should let normal
  engineering prompts select the right specialist.

## Required Skill Shape

Every specialist file should include:

- `## Iron Law`
- `## When To Use`
- `## When Not To Use`
- `## Info To Gather`
- `## Workflow`
- `## Required Outputs`
- `## Checks Before Moving On`
- `## Red Flags`
- `## Common Mistakes`

Additional sections are fine when they remove ambiguity. Do not add sections
that only repeat the same rule in different words.

## Writing Style

Write like an engineer leaving instructions for another careful engineer.

- Be plain, direct, and specific.
- Prefer imperatives over commentary.
- Prefer artifacts over abstract statements.
- Prefer concrete checks over confidence words.
- Prefer capabilities over products: `queue`, `cache`, `object store`,
  `load balancer`, `identity provider`, `approval system`.
- End sentences where the meaning ends.
- Use short examples only when they clarify the rule.

Avoid:

- Marketing adjectives: `powerful`, `comprehensive`, `world-class`,
  `industry-leading`, `seamless`, `cutting-edge`, `production-grade`,
  `game-changing`, `best-in-class`.
- Vague hedges: `best practices`, `industry standards`, `modern engineering`,
  `cloud-native`, unless the phrase is user-provided context being analyzed.
- Logo name-dropping in openings. Name a source only when it supports a concrete
  rule.
- Persona language. The skill is a reviewer, not a cast of characters.
- Tooling invented by the skill. Do not prescribe a cloud provider, database,
  framework, observability product, or command the user did not supply unless
  the skill is explicitly technology-bound.

## Sources And Synthesis

Use sources to support operational rules, not to borrow prestige.

- Cite stable source IDs from
  `skills/_shared/references/source-index.md`.
- Prefer authoritative sources: official documentation, standards bodies,
  peer-reviewed papers, first-party engineering publications, or widely cited
  practitioner references that originated the pattern.
- Do not cite encyclopedias, forums, scraped mirrors, SEO summaries, anonymous
  content farms, or unofficial copies when a primary source exists.
- Read the relevant source notes and reconcile tradeoffs into one blended
  default.
- Keep final prose technology-agnostic unless the skill's surface is explicitly
  technology-bound, such as frontend, mobile, ML, or LLM applications.
- Do not paste source prose into skills. Synthesize.

## Iron Laws

Every specialist file has one all-caps rule that names the central failure mode
the skill prevents.

Good Iron Laws are short, testable, and operational:

- `NO LAUNCH READINESS CALL WITHOUT CURRENT CHECK RESULTS OR A DATED EXCEPTION`
- `NO STATE MACHINE REVIEW WITHOUT EXPLICIT INVARIANTS`
- `NO SECRET ROTATION WITHOUT OVERLAP, VERIFICATION, AND ROLLBACK`

Weak Iron Laws are slogans:

- "Be careful with releases."
- "Security should be considered."
- "Use best practices."

## Documentation Rules

README, release notes, manifests, install docs, sample prompts, and source
references should match the router and specialist files.

- Update docs when setup, CLI behavior, manifests, public paths, examples, or
  skill contracts change.
- Verify command examples before presenting them as working.
- Keep public copy plain and technically accurate.
- Do not use source-owner names as hero copy or credibility decoration.
- Do not add AI assistants, automation, or tools as co-authors or attribution in
  docs, headers, release notes, or commit messages.

## Validation

Run the relevant checks before asking for review.

- Run repo-local validation for skill changes.
- Run `python3 scripts/validate_source_quality.py` after source-index or
  citation changes.
- Run `python3 scripts/validate_platform_support.py` after plugin manifest,
  install, README, LICENSE, or cross-tool packaging changes.
- Run `python3 scripts/lint_brand_voice.py` after public prose changes.

The voice linter enforces the hard subset of these rules: prestige vendor and
cloud names in H1/H2 and opening lines, marketing adjectives in headings or
descriptions, hedging phrases in headings or descriptions, specialist vendor or
framework names in `SKILL.md` prose, and `## Iron Law` presence in specialist
skills. The rest is reviewer-enforced.

## Review Bar

A style-compliant change should leave the reviewer able to answer:

1. What situation selects this skill?
2. What should the agent do first, next, and last?
3. What concrete check shows the output is safe enough to use?
4. What output artifact will the user receive?
5. What is explicitly out of scope?
6. Which sources support the rule, and where are they cited?
7. Does the prose work without vendor prestige, marketing language, or invented
   tooling?

If those answers are not clear from the file, keep editing.
