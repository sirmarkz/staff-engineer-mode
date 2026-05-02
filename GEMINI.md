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

Do not require the user to name an individual specialist skill. The router must
infer intent from the request and choose the smallest useful skill set.

## Routing Discipline

- Pick one primary skill by default.
- Add at most one secondary skill when the request clearly includes a separate
  engineering surface.
- Ask only focused intake questions when confidence is low. Do not expose
  candidate skill names, confidence labels, or routing drafts while asking.
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

The pack does not depend on another plugin. Any specialist guidance it needs is
inside this repository under `skills/`. Shared sources and assets live under
`skills/_shared/`.

When citing sources, use source IDs from
`skills/_shared/references/source-index.md`. Do not quote source text unless the
quote is short, necessary, and clearly attributed.
