# GEMINI.md

`staff-engineer-mode` is a self-contained engineering skill pack. It routes ordinary
engineering requests to technology-agnostic practices for building, shipping,
securing, operating, and maintaining complex systems.

## Entrypoint

Start at `skills/staff-engineer-mode/SKILL.md` when the request is
broad, ambiguous, multi-surface, or asks for staff-engineer-level engineering standards,
architecture review, production readiness, reliability, resilience, DevOps,
security, privacy, operations, platform, data, mobile, frontend, or cost-aware
reliability guidance.

Do not require the user to name an individual specialist. The router must infer
intent from the request and choose the smallest useful specialist file set.
After routing, read only the selected specialist reference file from
`specialists/<specialist-name>.md`.

## Specialist Loading

Specialists are reference files, not registered skills. To load a specialist:

- **Read** `specialists/<slug>.md` relative to this `GEMINI.md` file.
- Never call a Skill tool on a specialist slug. Specialists are not registered as skills on Gemini.
- Complete the Read before producing engineering guidance for routed work. A confidently-routed answer without a matching Read in the same turn is a routing failure.

## Routing Discipline

- Pick one primary specialist file by default.
- Add at most one secondary specialist file when the request clearly includes a separate
  engineering surface.
- Before creating or amending commits, route to `agent-pr-review` for the exact
  staged diff. Before tags, version bumps, hosted release records, packages, artifact
  publication, or promotion, route to `release-build-reproducibility`.
- Review findings guide the user and agent. If the user explicitly accepts
  unresolved gaps, proceed after stating the residual risk.
- Ask only focused intake questions when confidence is low. Do not expose
  candidate specialist names, confidence labels, or routing drafts while asking.
- Translate vendor, tool, framework, or cloud names into capabilities before
  routing.
- Keep guidance technology-agnostic by default. Do not introduce provider,
  framework, database, monitoring product, protocol, or command examples unless
  the user supplied them or explicitly asks for tool-specific guidance.
- Keep non-engineering process work out of scope unless reframed as concrete
  engineering controls.

**Blend compatible large-scale engineering and standards-body practices into one
normalized default. Do not ask the user to choose between named-company
approaches to the same engineering problem unless the system context truly
demands the exception.**

## Self-Contained Use

The pack does not depend on another plugin. The only native skill entrypoint is
under `skills/`; routed specialist files live under `specialists/`. Shared
sources and assets live under `skills/_shared/`.

When citing sources, use references from
`skills/_shared/references/source-index.md`. Do not quote source text unless the
quote is short, necessary, and clearly attributed.
