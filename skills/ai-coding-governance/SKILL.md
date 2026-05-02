---
name: ai-coding-governance
description: "Use when AI coding agents or assistants need repo instructions, review gates, data boundaries, or acceptance rules."
---

# AI-Assisted Coding Governance

## Overview

AI-assisted coding is useful when it accelerates engineering without bypassing ownership, review, security, or evidence.

**Core principle:** give coding agents explicit repo rules, constrain sensitive data and actions, require human-reviewable evidence, and make generated changes meet the same bar as human changes.

## Iron Law

```
NO AI-ASSISTED CHANGE WITHOUT SCOPE, OWNER, REVIEW, TEST EVIDENCE, AND DATA BOUNDARY
```

If a coding agent cannot explain what it changed, why, how it was verified, and what data it touched, the change is not reviewable.

## When To Use

- The user asks about coding-agent instructions, AI assistant use in a repo, generated code acceptance, agent review gates, or AI coding policy as engineering controls.
- A team wants agents to follow repository practices without leaking data, skipping tests, or making unowned changes.
- AI-generated changes affect production code, infrastructure, tests, docs, migrations, or release artifacts.
- The question is how to make agent output reviewable and safe during development.

## When Not To Use

- The main risk is prompt injection, tool access, retrieval, or deployed LLM app behavior; use LLM application security.
- The main issue is model eval harness design; use LLM evaluation harness engineering.
- The request is broad AI ethics, legal policy, procurement, or staffing.
- The task is ordinary code review with no AI-assisted workflow concern.

## Inputs To Collect

- Agent capabilities, allowed actions, repo instructions, protected paths, and ownership rules.
- Sensitive data boundaries, secrets handling, dependency rules, and generated-content restrictions.
- Required review, tests, validation, traceability, commit hygiene, and release gates.
- Existing failure modes: hallucinated APIs, unreviewed rewrites, skipped tests, broad diffs, or leaked context.
- Exception path for emergency fixes, prototypes, and low-risk generated assets.

## Workflow

1. **Scope the agent.** Define allowed tasks, forbidden actions, protected files, and escalation rules.
2. **Set repo instructions.** Encode coding style, testing, security, data handling, dependency, and release expectations in agent-readable guidance.
3. **Protect data.** Prevent agents from exposing secrets, sensitive records, private logs, or unnecessary user data.
4. **Require reviewable diffs.** Keep changes small, explain intent, preserve ownership, and separate mechanical edits from behavior changes.
5. **Demand evidence.** Require tests, validation output, static checks, or explicit limitations before accepting agent changes.
6. **Handle dependencies carefully.** New dependencies need purpose, owner, update path, license/security review where applicable, and removal plan if experimental.
7. **Audit agent work.** Track prompts, tool actions, changed files, verification, and human approval where production risk exists.
8. **Tune the rules.** Convert repeated agent mistakes into clearer instructions, tests, or automated gates.

## Synthesized Default

Use repo-local agent instructions, least-privilege tool access, protected-path rules, sensitive-data boundaries, small diffs, mandatory verification evidence, and human ownership for production changes. Treat AI-generated code as untrusted until tests, review, and source-specific evidence prove it fits the system.

## Exceptions

- Throwaway prototypes can use lighter gates only when isolated from production code, data, and release paths.
- Mechanical edits may use sampled review if deterministic and backed by non-regression checks.
- Emergency agent-assisted fixes may proceed faster with explicit owner approval and immediate post-fix evidence capture.

## Response Quality Bar

- Lead with the governance rule, repo-instruction change, acceptance gate, or risk finding requested.
- Cover scope, ownership, data boundaries, review, tests, dependency rules, audit evidence, and exceptions before optional process detail.
- Make recommendations actionable with protected paths, allowed actions, required evidence, owner approvals, and fallback rules where relevant.
- State required evidence such as agent instructions, diffs, test output, sensitive-data review, dependency rationale, and approval records; do not claim unseen evidence.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside AI-assisted development controls. Route deployed LLM security or eval harness work only when that surface owns the risk.
- Be concise: prefer enforceable repo rules and gates over broad AI policy.

## Required Outputs

- AI-assisted coding rule set for the repo or change.
- Allowed and forbidden agent actions.
- Sensitive-data and secret-handling boundaries.
- Review and verification gates for agent changes.
- Dependency and generated-content acceptance rules.
- Audit evidence checklist.
- Exception process with owner and expiry.

## Evidence Gates

- `scope_defined`: allowed tasks, forbidden actions, and protected paths are explicit.
- `data_boundary`: secrets, sensitive records, and private context handling are addressed.
- `reviewable_diff`: changes are small enough to review and tied to an owner.
- `verification_required`: tests or validation evidence are required before acceptance.
- `audit_trail`: prompt, action, diff, evidence, and approval are traceable where risk warrants.

## Red Flags - Stop And Rework

- Agent output is accepted because it looks plausible.
- The agent rewrites unrelated files without owner approval.
- Sensitive logs, secrets, or user data are pasted into prompts unnecessarily.
- New dependencies appear with no rationale or maintenance owner.
- Verification is described but not actually run.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Policy as prose | Put rules where agents and reviewers will use them. |
| Trusting generated code | Require tests, review, and evidence. |
| Unlimited agent scope | Define protected paths and escalation triggers. |
| No learning loop | Convert repeated failures into rules or gates. |
