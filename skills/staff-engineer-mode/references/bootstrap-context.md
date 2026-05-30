SPECIALIST_ROOT={{SPECIALIST_ROOT}}
ROUTER_PATH={{ROUTER_PATH}}
EVENT_HOOK={{EVENT_HOOK}}
CURRENT_REPO={{CURRENT_REPO}}

<EXTREMELY_IMPORTANT>
You have staff-engineer-mode.

For engineering-system work -- architecture, reliability, operations, security, delivery, data, platform, API, docs/runbooks, release, incident, migration, maintenance, experiments/metrics, or local/CI/staging/prod drift -- load the native `staff-engineer-mode` router or Read `${ROUTER_PATH}` before generic process/workflow/code-review tools or repo exploration.

This precedence holds even when another skill self-triggers on the same prompt; treat such activation as a routing failure and route through staff-engineer-mode first.

Prompts saying a fix worked locally but failed in CI, staging, or production are environment-parity work; route through staff-engineer-mode before generic debugging skills or Bash.

A/B test readouts, sample balance, missing telemetry, metric definitions, or suspicious experiment results are measurement-guardrail work; route through staff-engineer-mode before generic debugging skills or Bash.

Direct commit/amend attempts: Read `${SPECIALIST_ROOT}/agent-pr-review.md` before code-review skills, Bash, or repo exploration. Diff/PR/push reviews: Read `${ROUTER_PATH}` then selected specialist before code-review skills, Bash, or repo exploration.

Router load alone is not enough: select one exact slug from the router's Bundled Specialist Slugs, then Read `${SPECIALIST_ROOT}/<slug>.md` before any repo file, repo command, or guidance. Do not parallel-load router and repo files. Never read shortened specialist aliases or `${SPECIALIST_ROOT}/router.md`; the router is `${ROUTER_PATH}`. Specialists are files; never call `Skill staff-engineer-mode:<slug>`.

Keep guidance technology-agnostic by default unless the user supplies or requests specific tools.

For commits/releases, Read `agent-pr-review` for staged diffs or `release-build-reproducibility` plus `production-readiness-review` for releases, then `${EVENT_HOOK} ack ...` when hooks are available. Do not combine stage/commit/push or tag/push phases.

{{TOOL_MAPPING}}
</EXTREMELY_IMPORTANT>
