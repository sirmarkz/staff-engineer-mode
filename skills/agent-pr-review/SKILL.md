---
name: agent-pr-review
description: "Use when an AI coding agent has produced a non-trivial diff and a senior reviewer's pre-merge checklist must be applied to that AI-generated code before it merges."
---

# Agent PR Review

## Overview

AI coding agents produce diffs that look plausible and often pass shallow review. The risk is not bad syntax; it is silent assumptions, missing edge cases, hallucinated APIs, deleted-but-used code, and quiet scope creep that a senior teammate would catch.

**Core principle:** treat an agent diff as untrusted until intent, evidence, and AI-specific failure modes have been checked against the actual change set, not against the agent's narration of it.

## Iron Law

```
NO AGENT DIFF MERGES WITHOUT VERIFIED INTENT, EVIDENCE, OWNED RISK, AND AI-FAILURE-MODE CHECK
```

If the agent's stated intent does not match its actual diff, or the diff cannot show that the changed behavior was exercised, the change is not reviewable.

## When To Use

- The user asks to review a PR, branch, diff, or change set produced by an AI coding agent.
- A coding agent has just finished a multi-file change, refactor, migration, or new feature and the user is deciding whether to merge.
- The user asks "did the agent miss anything," "is this safe to merge," "what would a senior reviewer catch here," or "review this AI-generated code."
- The reviewer suspects the agent's summary may not match what actually changed.
- The change touches paths the agent was not explicitly scoped to and the user wants to confirm intent.

## When Not To Use

- The work is pre-design: there is no diff yet; defer to `architecture-decisions` or `secure-sdlc-and-threat-modeling`.
- A live incident is underway; defer to `incident-response-and-postmortems` first.
- The request is org-level policy for AI-assisted work, not a single diff; defer to `ai-coding-governance`.
- The request is reviewer routing, ownership, change-size policy, or DORA work; defer to `code-review-and-workflow`.
- The request is launch readiness across multiple surfaces with an explicit launch event; defer to `production-readiness-review`.
- The diff is one trivial fix that humans can review without a structured pass.

## Inputs To Collect

- **Diff scope:** files changed, lines added/removed, public-surface changes, generated-file changes, and deleted code.
- **Agent context:** which agent produced the diff, what prompt or task it was given, and what its own summary claims it did.
- **Change type:** new feature, refactor, bug fix, dependency update, migration, generated code, or mixed.
- **Environment context:** target repo's tier, exposed surfaces, ownership, and whether the change touches production paths, data, or shared libraries.
- **Test coverage state:** which tests exist for the touched paths, which the agent added, and which were modified or deleted.
- **Prior review state:** whether a human or other agent has already passed over the diff and what was flagged.
- **Stated intent versus diff:** the agent's narration, the originating task, and the actual file-by-file delta.

## Workflow

1. **Reconstruct intent.** Restate what the change is supposed to do in one sentence, sourced from the task or PR description, not from the agent's self-summary. Note any gap between intent and the diff's actual surface area.
2. **Map the diff.** Group changes by purpose: behavior change, refactor, test, generated/mechanical, dependency, configuration, deletion. Flag any group the stated intent does not justify as scope creep.
3. **Run the AI-specific failure-mode pass.** For each change, check for: silent assumptions, plausible-but-wrong logic, hallucinated APIs or imports, deleted-but-still-used code, unmotivated edits, missing edge cases a human would consider, mismatched error handling, and copied-pattern code that does not match the local convention.
4. **Verify behavior is exercised.** Confirm the changed behavior has tests that fail without the change. New behavior without a failing-without-the-change test is treated as unverified.
5. **Check correctness on real inputs.** Look for boundary conditions, null/empty/large/concurrent inputs, error paths, and idempotency. Confirm the agent did not test only the happy path it imagined.
6. **Check ownership and surface.** Confirm changed files have an owner who would expect this change. Files touched outside the agent's stated scope need an explicit reason or get flagged as out-of-scope.
7. **Check public-surface and contract impact.** Identify breaking changes to APIs, schemas, configs, on-disk formats, events, or shared modules. Confirm consumer impact has been considered.
8. **Check operational artifacts.** Identify missing rollback path, missing telemetry for new behavior, missing runbook update, missing migration safety, missing SLO/error-budget consideration, missing threat consideration for new trust-boundary changes, and missing docs.
9. **Classify findings.** For each finding, record category, evidence (file:line or behavior), owner, recommended next action, and risk level (blocker, must-fix-before-merge, follow-up, or accepted with rationale).
10. **Route specialist work.** Hand off security, database, rollout, observability, accessibility, or contract-evolution concerns to the right specialist instead of expanding scope here.
11. **Produce the structured artifact.** Output a single review with the categories below, not running prose. Reviewer reads this and can act without re-reading the diff.

## Synthesized Default

Use a structured pre-merge review pass focused on AI-generated failure modes: verify stated intent matches actual diff, check that changed behavior is exercised by a test that would fail without the change, scan for hallucinated APIs and deleted-but-used code, classify scope creep, and require an owner plus evidence for every blocker. Treat the agent's self-summary as a hypothesis, not a finding. Defer specialist depth to the owning specialist skill rather than re-doing it here.

## Exceptions

- Throwaway prototypes isolated from production may use a lighter pass focused on hallucinated APIs and unmotivated edits.
- Mechanical or generated changes may use sample review plus a non-regression check rather than line-by-line review, when the generator and pattern are owned and verified.
- Emergency agent-assisted fixes may merge with a documented blocker list and an immediate post-merge review and rollback plan owned by a named human.
- Diffs already reviewed by a human owner may use this skill only to verify AI-specific failure modes the human would not have looked for.

## Response Quality Bar

- Lead with the structured review artifact, blocker list, or scope-creep finding requested.
- Cover intent verification, AI-specific failure modes, behavior-exercise evidence, ownership, public-surface impact, and missing operational artifacts before optional review breadth.
- Make findings actionable with file/line evidence, owner, recommended next action, and risk classification; do not produce vibes-only review.
- State required evidence such as the diff itself, the originating task or prompt, the test results, and the agent's stated summary; do not claim findings against unseen code.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside pre-merge review of agent-generated diffs. Route security depth, database migration depth, rollout safety, accessibility, and contract evolution to their owning specialists rather than absorbing them here.
- Be concise: prefer a single structured artifact with categorized findings over running narrative.

## Required Outputs

- One-sentence reconstructed intent and one-sentence assessment of whether the diff matches it.
- Categorized findings table with category, evidence (file/line or behavior), owner, recommended next action, and risk level.
- Blocker list: changes that must not merge as-is, each with evidence and owner.
- AI-specific failure-mode findings covering silent assumptions, plausible-but-wrong logic, hallucinated APIs, deleted-but-used code, unmotivated edits, missing edge cases, and scope creep.
- Missing-artifact list across rollback path, telemetry for new behavior, runbook updates, migration safety, threat consideration for new trust boundaries, and docs.
- Behavior-exercise summary stating which changed behaviors have a failing-without-the-change test and which do not.
- Specialist follow-up routes, capped and prioritized.
- Risk classification per finding (blocker, must-fix-before-merge, follow-up, accepted with rationale and owner).

## Evidence Gates

- `intent_match`: stated intent is restated and compared to the actual diff; scope creep is named when present.
- `ai_failure_pass`: silent assumptions, hallucinated APIs, deleted-but-used code, unmotivated edits, and missing edge cases have each been considered explicitly.
- `behavior_exercised`: every changed behavior is tied to a test or an explicit unverified-behavior finding.
- `evidence_per_finding`: every finding has file/line or behavior evidence and an owner.
- `risk_classified`: every finding has a risk level and a recommended next action.
- `surface_check`: public-surface, contract, schema, config, event, and shared-module impact has been addressed or marked not applicable with reason.
- `artifact_check`: missing rollback, telemetry, runbook, migration safety, threat consideration, and docs are listed when relevant.

## Red Flags - Stop And Rework

- The review trusts the agent's self-summary instead of checking the diff.
- Findings are stated as opinions without file/line or behavior evidence.
- New behavior is accepted because tests pass, without confirming any test would fail without the change.
- Deletions are accepted without checking for remaining callers, imports, or references.
- Out-of-scope file changes are merged because they "look harmless."
- Hallucinated APIs, types, or imports are not checked even though the agent could have invented them.
- Specialist concerns (security, migration, rollout) are absorbed into this review instead of routed to the owning specialist.
- The review produces prose only, with no categorized findings, owners, or risk levels.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Reviewing the agent's narration | Review the diff against the originating task, not the self-summary. |
| Treating green tests as verification | Confirm a test exists that would fail without the change. |
| Reviewing line-by-line without intent | Group changes by purpose and check each group against stated intent. |
| Ignoring deletions | Search for remaining callers, imports, references, and tests of removed code. |
| Accepting plausible APIs at face value | Confirm imports, types, and external calls actually exist in the target environment. |
| Letting scope creep slide | Name out-of-scope edits and require justification or removal. |
| Doing the specialist's work here | Route security, migration, rollout, accessibility, and contract concerns to the owning specialist. |
| Producing vibes review | Output a structured artifact with categories, owners, evidence, and risk levels. |
