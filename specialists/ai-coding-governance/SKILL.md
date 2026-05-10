---
name: ai-coding-governance
description: "Use when setting repo rules for AI coding agents: allowed actions, protected paths, data boundaries, evidence"
---

# AI-Assisted Coding Controls

## Iron Law

```
NO AI-ASSISTED CHANGE WITHOUT SCOPE, VERIFICATION EVIDENCE, DATA BOUNDARY, AND RESPONSIBLE ACCEPTANCE
```

If a coding agent cannot explain what it changed, why, how it was verified, and what data it touched, the change is not acceptably traceable.

## Overview

Produces a repo-local rule set for coding agents: allowed and forbidden actions, protected paths, sensitive-data and secret boundaries, required verification evidence, and traceability tied to the user and local evidence. Catches the moment when an agent rewrites twelve files at 11pm with no test run, no scope statement, and no accountability for the diff.

**Core principle:** give coding agents explicit repo rules, constrain sensitive data and actions, require user-visible evidence, and make generated changes meet the same bar as human changes.

## When To Use

- The user is designing coding-agent instructions, AI assistant repo rules, generated-code acceptance gates, protected paths, or AI coding rules as engineering controls.
- You want agents to follow repository practices without leaking data, skipping tests, or making anonymous changes.
- AI-generated changes affect production code, infrastructure, tests, docs, migrations, or release artifacts.
- The question is how to make agent output traceable, bounded, and safe during development.

## When Not To Use

- The request is per-PR, per-diff, or per-change pre-merge review ("review this PR before merge," "what did my agent miss here," "is this branch safe to merge") for any diff regardless of authorship; use `agent-pr-review`. This skill covers org-level and repo-level controls: allowed and forbidden actions, protected paths, secret and data boundaries, traceability, and the rules any diff must satisfy. `agent-pr-review` covers the senior review pass on a specific diff against those rules.
- The main risk is prompt injection, tool access, retrieval, or deployed LLM app behavior; use `llm-application-security`.
- The main issue is model eval harness design, graders, or regression gates for an LLM workflow; use `llm-evaluation`.
- The request is review routing, responsibility, change-size policy, or DORA-style workflow metrics for human and agent code together; use `code-review-and-workflow`.
- The request is broad AI ethics, legal rules, procurement, or staffing; out of scope.
- The task is ordinary code review with no AI-assisted workflow concern; use `code-review-and-workflow`.

## Inputs To Collect

- Current lifecycle phase, next decision, available evidence, and assumptions when evidence is missing.
- Agent capabilities, allowed actions, repo instructions, protected paths, and responsibility rules.
- Sensitive data boundaries, secrets handling, dependency rules, and generated-content restrictions.
- Required verification, acceptance checks, traceability, commit hygiene, and release gates.
- Existing failure modes: hallucinated APIs, unbounded rewrites, skipped tests, broad diffs, or leaked context.
- Exception path for emergency fixes, prototypes, and low-risk generated assets.

## Workflow

1. **Scope the agent.** Define allowed tasks, forbidden actions, protected files, and selection rules.
2. **Set repo instructions.** Encode coding style, testing, security, data handling, dependency, and release expectations in agent-readable guidance.
3. **Protect data.** Prevent agents from exposing secrets, sensitive records, private logs, or unnecessary user data.
4. **Require small explainable diffs.** Keep changes small, explain intent, preserve responsibility, and separate mechanical edits from behavior changes.
5. **Demand evidence.** Require tests, validation output, static checks, or explicit limitations before accepting agent changes.
6. **Handle dependencies carefully.** New dependencies need purpose, update path, license/security rationale where applicable, and removal plan if experimental.
7. **Trace agent work.** Track prompts, tool actions, changed files, verification, and explicit user confirmation where production risk exists.
8. **Tune the rules.** Convert repeated agent mistakes into clearer instructions, tests, or automated gates.

## Synthesized Default

Use repo-local agent instructions, least-privilege tool access, protected-path rules, sensitive-data boundaries, small diffs, mandatory verification evidence, and human responsibility for production changes. Treat AI-generated code as untrusted until tests, checks, and source-specific evidence prove it fits the system.



## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, gates, and evidence to collect.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness evidence.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Existing artifact: use current code, docs, telemetry, incidents, or diffs as evidence for the next engineering decision; do not wait for a finished artifact before guiding design, build, release, or operation.
- Missing evidence: state assumptions and produce the evidence plan instead of blocking lifecycle guidance.

## Exceptions

- Throwaway prototypes can use lighter gates only when isolated from production code, data, and release paths.
- Mechanical edits may use sampled checks if deterministic and backed by non-regression checks.
- Emergency agent-assisted fixes may proceed faster with explicit user confirmation and immediate post-fix evidence capture.

## Response Quality Bar

- Lead with the control rule, repo-instruction change, acceptance gate, or risk finding requested.
- Cover scope, responsibility, data boundaries, verification, tests, dependency rules, traceability evidence, and exceptions before optional operational detail.
- Make recommendations actionable with protected paths, allowed actions, required evidence, user confirmations, and fallback rules where relevant.
- State required evidence such as agent instructions, diffs, test output, sensitive-data boundary checks, dependency rationale, and confirmation records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside AI-assisted development controls. Use deployed LLM security or eval-harness skills only when that surface is the central risk.
- Be concise: prefer enforceable repo rules and gates over broad AI statements.

## Required Outputs

- AI-assisted coding rule set for the repo or change.
- Allowed and forbidden agent actions.
- Sensitive-data and secret-handling boundaries.
- Verification and acceptance gates for agent changes.
- Dependency and generated-content acceptance rules.
- Traceability evidence checklist.
- Exception rule with user confirmation and expiry.

## Evidence Gates

- `scope_defined`: allowed tasks, forbidden actions, and protected paths are explicit.
- `data_boundary`: secrets, sensitive records, and private context handling are addressed.
- `small_diff`: changes are small enough to understand and tied to a user-visible evidence trail.
- `verification_required`: tests or validation evidence are required before acceptance.
- `traceability_record`: prompt, action, diff, evidence, and confirmation are traceable where risk warrants.

## Red Flags - Stop And Rework

- Agent output is accepted because it looks plausible.
- The agent rewrites unrelated files without explicit user confirmation.
- Sensitive logs, secrets, or user data are pasted into prompts unnecessarily.
- New dependencies appear with no rationale, update path, or removal plan.
- Verification is described but not actually run.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Rules as prose | Put rules where agents and acceptance checks will use them. |
| Trusting generated code | Require tests, checks, and evidence. |
| Unlimited agent scope | Define protected paths and user-confirmation triggers. |
| No learning loop | Convert repeated failures into rules or gates. |
