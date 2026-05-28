# Staff Engineer Mode

@./skills/staff-engineer-mode/SKILL.md

## Bash Preflight

For any user request that includes commit, amend, push, tag, release, version,
package, artifact, or promotion work, plan the Staff Engineer Mode sequence
before the first mutating Bash command.

- Receipt `--repo` means the local checkout root from `git rev-parse
  --show-toplevel`; never use `origin`, a remote URL, or a bare remote path.
- Commit or amend: run staging as its own Bash command, inspect
  `git diff --cached`, read `specialists/agent-pr-review.md`, produce the
  review, run the installed `hooks/agent-event-policy ack commit --repo <repo>`
  command, then run `git commit`. Push only in a later Bash command if
  requested.
- Tag or release: read `specialists/release-build-reproducibility.md` and
  `specialists/production-readiness-review.md`, produce both reviews, run
  the installed `hooks/agent-event-policy ack release --repo <repo>` command,
  then run the tag or release command. Push a tag only in a later Bash command
  if requested.
- Never run bare `ack`; use the installed hook path shown in SessionStart or in
  hook block messages.
- Never run `git add && git commit`, `git commit && git push`,
  `git tag && git push`, or any command that combines those phases.
- Never add `Co-Authored-By`, generated-by, assisted-by, or other AI assistant
  attribution to commit messages.

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

Before creating or amending commits, read `specialists/agent-pr-review.md` and
run `agent-pr-review` on the exact staged diff. Inspecting `git diff --cached`,
reading this file, or reading `SKILL.md` is not enough. Stage changes in a
separate shell action before review. Do not combine staging, committing, or
pushing in one shell command. The successful order is: stage changes, inspect
`git diff --cached`, read `specialists/agent-pr-review.md`, produce the review,
run the hook's `ack commit --repo <repo>` command, run `git commit`, then run
`git push` if requested.
Before tags, version bumps, hosted release records, packages, artifact
publication, or promotion, read `specialists/release-build-reproducibility.md`
and `specialists/production-readiness-review.md`, run both reviews, then run
`ack release --repo <repo>` before the first release command. Reading this file
or `SKILL.md` is not enough. Do not offer or use `--override` because a change
looks personal, small, or low risk; use an override only after unresolved
findings are shown and the user explicitly accepts them.
A review message alone is not a receipt. Do not add AI assistants, automation,
or tools as `Co-Authored-By` trailers or attribution in commit messages.

Keep the pack boundary tight: building, shipping, securing, operating, and
maintaining complex software systems.
