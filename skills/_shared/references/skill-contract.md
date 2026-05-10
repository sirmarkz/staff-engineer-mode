# Staff Engineer Mode Skill Contract

Every specialist file must be concise, triggerable, and artifact-oriented.

## Required SKILL.md Shape

- YAML frontmatter with `name` and trigger-only `description`.
- `# Skill Name`
- `## Overview`
- `## Iron Law`
- `## When To Use`
- `## When Not To Use`
- `## Inputs To Collect`
- `## Workflow`
- `## Synthesized Default`
- `## Phase Behavior`
- `## Exceptions`
- `## Response Quality Bar`
- `## Required Outputs`
- `## Evidence Gates`
- `## Red Flags - Stop And Rework`
- `## Common Mistakes`

Do not add per-specialist source, reference, bibliography, citation, or reading-list
sections. Source synthesis belongs in shared reference notes, not in published
skill instructions.

Every specialist Response Quality Bar must require technology-agnostic guidance
by default: do not introduce provider, product, framework, database, protocol,
or command names unless the user supplied them or explicitly requested
tool-specific guidance.

Every specialist must state lifecycle behavior:

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, gates, and evidence to collect.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness evidence.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Review: evaluate an existing diff, design, runbook, evidence, or system behavior as one mode.
- Missing evidence: state assumptions and produce the evidence plan instead of blocking lifecycle guidance.

Non-exception specialists must not be written as audit-only reviewers. They must
guide the next decision from context, artifact, surface, risk, and available
evidence, even when the prompt does not name a formal phase.

## Output Schema

- `context`
- `risk_register`
- `synthesized_default`
- `exceptions`
- `standard_decisions`
- `required_artifacts`
- `evidence_gates`
- `follow_up_routes`

## Routing Rules

- Prefer one primary specialist.
- Recommend at most two follow-up routes.
- Ask one disambiguating question when intent is ambiguous.
- Do not route to out-of-scope business, marketing, legal, procurement, staffing, compensation, or broad compliance-program work.
- Eval-harness routing blocks are only for confident in-scope routing; low-confidence, ambiguous, and out-of-scope prompts must not emit routing blocks.
- Keep the router `SKILL.md` compact; detailed routing boundary notes belong in `skills/staff-engineer-mode/references/routing-matrix.md`.
