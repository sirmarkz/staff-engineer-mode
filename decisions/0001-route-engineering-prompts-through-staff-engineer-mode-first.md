# ADR 0001: Route Engineering Prompts Through Staff Engineer Mode First

## Context

Staff Engineer Mode runs alongside other process packs that may claim broad
creative, build, design, or implementation prompts. For engineering-system work,
that can produce the wrong first action: a generic brainstorming or planning
workflow can run before the router selects the specialist that owns the actual
engineering surface.

The router also needs to handle underspecified but routable prompts, such as
consumer compatibility, removal, rollout, safety, or readiness checks, without
asking for exact file, field, service, or system names before loading the
specialist.

## Decision

Staff Engineer Mode takes precedence for engineering lifecycle and engineering
system prompts. When the prompt is about architecture, reliability, operations,
security, delivery, data, platform, client, AI/ML, accessibility, cost,
readiness, rollout, migration, incident response, control records, API design,
service contracts, or engineering-system design, the agent must route through
Staff Engineer Mode and read the selected specialist before invoking broad
process packs.

The router should infer a best-fit specialist from available context when the
engineering surface is clear, then gather missing details after the specialist is
loaded.

## Status

Accepted.

## Tradeoffs

Positive:

- Engineering prompts reach the narrow specialist before generic process advice
  can dilute routing.
- Users do not need to know specialist names or supply exact implementation
  identifiers before the agent can start the correct workflow.
- Router behavior becomes easier to validate with fixtures for build phrasing,
  compatibility changes, and capability-specific tiebreakers.

Negative:

- The router description and bootstrap context become more explicit and slightly
  longer.
- Some ambiguous prompts may route earlier than before, so specialist guidance
  must clearly mark assumptions and ask follow-up questions after loading.
- The skill description needs a higher character limit to express trigger
  precedence without losing discoverability.

## Revisit Conditions

Revisit this decision if:

- Router eval fixtures show repeated over-routing of non-engineering creative or
  process-only requests.
- Generic process packs gain a reliable way to defer engineering-system prompts
  back to Staff Engineer Mode before producing guidance.
- The longer skill description harms plugin discovery, marketplace display, or
  cross-tool installation behavior.
- Users report that missing implementation details should block routing for a
  specific specialist surface.

## Evidence

- `skills/staff-engineer-mode/SKILL.md` documents precedence over generic
  process packs and adds routing guidance for underspecified engineering
  decisions.
- `skills/staff-engineer-mode/references/bootstrap-context.md` carries the same
  precedence rule into bootstrap context.
- `skills/staff-engineer-mode/references/router-eval-set.yaml` adds and updates
  fixtures for build phrasing and compatibility routing.
- `scripts/validate_skill_pack.py` raises the description character limit so the
  trigger can state the precedence rule.
