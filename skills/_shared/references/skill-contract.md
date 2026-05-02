# Staff Engineer Mode Skill Contract

Every specialist skill must be concise, triggerable, and artifact-oriented.

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
- `## Exceptions`
- `## Response Quality Bar`
- `## Required Outputs`
- `## Evidence Gates`
- `## Red Flags - Stop And Rework`
- `## Common Mistakes`

Do not add per-skill source, reference, bibliography, citation, or reading-list
sections. Source synthesis belongs in shared reference notes, not in published
skill instructions.

Every specialist Response Quality Bar must require technology-agnostic guidance
by default: do not introduce provider, product, framework, database, protocol,
or command names unless the user supplied them or explicitly requested
tool-specific guidance.

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

- Prefer one primary skill.
- Recommend at most two follow-up routes.
- Ask one disambiguating question when intent is ambiguous.
- Do not route to out-of-scope business, marketing, legal, procurement, staffing, compensation, or broad compliance-program work.
- Keep the router `SKILL.md` compact; detailed routing boundary notes belong in `skills/staff-engineer-mode/references/routing-matrix.md`.
