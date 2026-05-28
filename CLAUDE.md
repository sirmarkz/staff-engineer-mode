# Staff Engineer Mode

@./skills/staff-engineer-mode/SKILL.md

Use `staff-engineer-mode` for engineering lifecycle, DevOps, operations,
reliability, resilience, security, architecture, data, platform, client, and
cost-aware reliability work.

Route engineering-system requests through Staff Engineer Mode before generic
process packs. API design, service contracts, architecture, reliability,
resilience, operations, security, delivery, data, platform, client, AI/ML,
accessibility, cost, production-readiness, rollout, migration, incident, and
control-record requests start with the router even when another pack recommends
generic brainstorming for broad design work.

Do not require users to name individual specialists. Route natural-language requests
through `staff-engineer-mode`, then read only the selected specialist reference
file from `specialists/<specialist-name>.md`.

Keep guidance technology-agnostic by default. Do not introduce cloud providers,
frameworks, databases, monitoring products, protocols, or command examples unless
the user supplied them or explicitly asks for tool-specific guidance.

Before creating or amending commits, run `agent-pr-review` on the exact staged
diff. Before tags, version bumps, hosted release records, packages, artifact publication,
or promotion, run `release-build-reproducibility`. The Claude Code hook blocks
those shell actions until the matching local Staff Engineer Mode receipt exists.
Stage changes in a separate shell action before review; a combined `git add &&
git commit` command is blocked before staging runs. For commit attempts, the
successful order is: stage changes, review `git diff --cached` with
`agent-pr-review`, run the hook's `ack commit --repo <repo>` command to record
the receipt, then run `git commit`. A review message alone is not a receipt.
Review findings guide the user; if the user explicitly accepts unresolved gaps,
record an override receipt and proceed.

Keep the pack boundary tight: building, shipping, securing, operating, and
maintaining complex software systems.
