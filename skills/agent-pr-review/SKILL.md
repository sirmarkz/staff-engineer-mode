---
name: agent-pr-review
description: "Use when asked to apply a senior pre-merge checklist to a diff before it merges, after narrower API, dependency, config, rollout, security, database, and test-gate surfaces are ruled out."
---

# Pre-Merge PR Review

## Iron Law

```
NO DIFF MERGES WITHOUT VERIFIED INTENT, BEHAVIOR EVIDENCE, ASSIGNED RISK, AND A FAILURE-MODE PASS
```

If the stated intent does not match the actual diff, or the diff cannot show that the changed behavior was exercised by a test that would fail without the change, the diff is not reviewable yet.

## Overview

The default pre-merge review pass. Applies whether the diff was written by a human, by an AI coding agent, or by both. Modern diffs increasingly contain AI-assisted code that looks plausible, so every review treats the diff as untrusted until intent, behavior evidence, responsibility, and common failure modes (silent assumptions, plausible-but-wrong logic, hallucinated APIs, deleted-but-used code, scope creep, missing edge cases) have been checked against the actual change set.

**Core principle:** review the diff against its originating task, not against the author's self-summary. The summary is a hypothesis; the diff is the evidence.

## When To Use

- The user asks to review a PR, branch, diff, or change set before merging — regardless of who or what produced it.
- A coding agent has just finished a multi-file change, refactor, migration, or new feature and the user is deciding whether to merge.
- The user asks "is this safe to merge," "what would a senior review catch here," "review my last commit," "review this PR," "find risks in this diff," or "did the agent miss anything."
- The author's summary may not match what actually changed.
- The change touches paths the author was not explicitly scoped to and needs an explicit intent check.

## When Not To Use

- The work is pre-design: there is no diff yet; use `architecture-decisions` or `secure-sdlc-and-threat-modeling` instead.
- A live incident is underway; use `incident-response-and-postmortems` instead first.
- The request is org-level policy for AI-assisted work, not a single diff; use `ai-coding-governance` instead.
- The request is review routing, change-size policy, responsibility policy, or DORA workflow metrics — i.e. how review works, not the review itself; use `code-review-and-workflow` instead.
- The request is launch readiness across multiple surfaces with an explicit launch event; use `production-readiness-review` instead.
- The diff is one trivial fix the human author can self-review without a structured pass.

## Inputs To Collect

- **Diff scope:** files changed, lines added/removed, public-surface changes, generated-file changes, and deleted code.
- **Authorship context:** human, AI agent, or mixed; which agent or contributor produced the diff; what prompt or task it was given; what the task summary claims it did.
- **Change type:** new feature, refactor, bug fix, dependency update, migration, generated code, or mixed.
- **Environment context:** target repo's tier, exposed surfaces, user-stated scope, local responsibility metadata or recent commits when available, and whether the change touches production paths, data, or shared libraries.
- **Test coverage state:** which tests exist for the touched paths, which were added, and which were modified or deleted.
- **Prior review state:** whether a human or other agent has already passed over the diff and what was flagged.
- **Stated intent versus diff:** the author's or agent's summary, the originating task, and the actual file-by-file delta.

## Workflow

1. **Reconstruct intent.** Restate what the change is supposed to do in one sentence, sourced from the task or PR description, not from the author's self-summary. Anchor the intent in the actual diff with at least one concrete file/function/line signal when available. Note any gap between intent and the diff's actual surface area.
2. **Map the diff.** Group changes by purpose: behavior change, refactor, test, generated/mechanical, dependency, configuration, deletion. Flag any group the stated intent does not justify as scope creep.
3. **Pin evidence anchors.** Before writing the verdict, select at least two separate changed locations from the diff and cite them as `file:line` in the final review. Prefer line-numbered changed files; if only a patch is available, cite the hunk file and added-line number from the patch. These anchors should include the most important behavior or risk locations, not just file names.
4. **Run the failure-mode pass.** For each change, check for: silent assumptions, plausible-but-wrong logic, hallucinated APIs or imports, deleted-but-still-used code, unmotivated edits, missing edge cases a careful review would consider, mismatched error handling, and copied-pattern code that does not match the local convention. These checks apply whether the diff is human, AI, or mixed; AI-assisted code raises the prior probability of each.
5. **Verify behavior is exercised.** Confirm the changed behavior has tests that fail without the change. New behavior without a failing-without-the-change test is treated as unverified.
6. **Check correctness on real inputs.** Look for boundary conditions, null/empty/large/concurrent inputs, error paths, and idempotency. Confirm the diff was not tested only against the happy path the author imagined.
7. **Check code-quality dimensions.** Compactly assess design, functionality, complexity, tests, naming, comments, and style as issue, OK, or not applicable based on the diff and surrounding code. Do not invent findings just to fill a dimension.
8. **Check responsibility and surface.** Confirm changed files fit the user's stated scope or local responsibility evidence. Files touched outside the stated scope need an explicit reason or get flagged as out-of-scope.
9. **Check public-surface and contract impact.** Identify breaking changes to APIs, schemas, configs, on-disk formats, events, or shared modules. Confirm consumer impact has been considered.
10. **Check operational artifacts.** Identify missing rollback path, missing telemetry for new behavior, missing runbook update, missing migration safety, missing SLO/error-budget consideration, missing threat consideration for new trust-boundary changes, and missing docs.
11. **Classify findings.** For each finding, record category, evidence (file:line or behavior), recommended next action, and risk level (blocker, must-fix-before-merge, follow-up, or accepted with rationale).
12. **Use specialist lenses when needed.** If security, database, rollout, observability, accessibility, or contract-evolution concerns dominate, apply that narrower skill rather than expanding this review.
13. **Produce the structured artifact.** Output a single review with the categories below, not running prose. The user can use this and can act without re-reading the diff.

## Synthesized Default

Use a structured pre-merge review pass: verify stated intent matches actual diff, check that changed behavior is exercised by a test that would fail without the change, scan for hallucinated APIs and deleted-but-used code, classify scope creep, and require evidence plus next action for every blocker. Treat any author or agent self-summary as a hypothesis, not a finding. Use narrower specialist skills only as internal lenses when their surface dominates.

## Exceptions

- Throwaway prototypes isolated from production may use a lighter pass focused on hallucinated APIs and unmotivated edits.
- Mechanical or generated changes may use sample review plus a non-regression check rather than line-by-line review, when the generator and pattern are maintained and verified.
- Emergency fixes may merge with a documented blocker list, explicit user risk acceptance, and an immediate post-merge review and rollback plan.
- Diffs already checked once may use this skill to verify failure modes a routine review would not have looked for.

## Response Quality Bar

- Lead with the structured review artifact, blocker list, or scope-creep finding requested.
- Start the artifact with an `Evidence anchors` line containing at least two changed `file:line` citations when the diff has two or more changed lines; one anchor may support intent, but blocker and must-fix findings still need separate cited evidence.
- Cover intent verification, failure-mode pass, behavior-exercise evidence, responsibility/scope evidence, public-surface impact, and missing operational artifacts before optional review breadth.
- Include a compact code-quality dimensions pass that explicitly covers design, functionality, complexity, tests, naming, comments, and style with issue, OK, or not applicable status tied to the diff.
- Make findings actionable with file/line evidence, recommended next action, and risk classification; do not produce vibes-only review.
- Include at least two concrete diff anchors when the diff has enough changed lines: file:line citations, file:function references, or short quoted code excerpts. One anchor may support intent reconstruction; blocker and must-fix findings still need separate evidence.
- State required evidence such as the diff itself, the originating task or prompt, the test results, and the author's stated summary; do not claim findings against unseen code.
- Stay technology-agnostic by default: do not introduce provider, product, framework, database, protocol, or command names unless the user supplied them or explicitly requested tool-specific guidance.
- Stay inside pre-merge review of a single diff. Route security depth, database migration depth, rollout safety, accessibility, and contract evolution to their responsible specialists rather than absorbing them here.
- Be concise: prefer a single structured artifact with categorized findings over running narrative.

## Required Outputs

- Evidence anchors: at least two changed `file:line` citations from the diff, unless the diff itself has fewer than two changed lines.
- One-sentence reconstructed intent and one-sentence assessment of whether the diff matches it, anchored to at least one changed file, function, or line when available.
- Explicit merge verdict: ready to merge, request changes, or block, with reasons tied to observed issues or their absence.
- Code-quality dimensions summary covering design, functionality, complexity, tests, naming, comments, and style, each marked issue, OK, or not applicable with brief evidence or reason.
- Categorized findings table with category, evidence (file/line or behavior), recommended next action, and risk level.
- Blocker list: changes that must not merge as-is, each with evidence and next action.
- Failure-mode findings covering silent assumptions, plausible-but-wrong logic, hallucinated APIs, deleted-but-used code, unmotivated edits, missing edge cases, and scope creep.
- Missing-artifact list across rollback path, telemetry for new behavior, runbook updates, migration safety, threat consideration for new trust boundaries, and docs.
- Behavior-exercise summary stating which changed behaviors have a failing-without-the-change test and which do not.
- Specialist follow-up routes, capped and prioritized.
- Risk classification per finding (blocker, must-fix-before-merge, follow-up, accepted with rationale and user confirmation).

## Evidence Gates

- `intent_match`: stated intent is restated and compared to the actual diff; scope creep is named when present.
- `failure_mode_pass`: silent assumptions, hallucinated APIs, deleted-but-used code, unmotivated edits, and missing edge cases have each been considered explicitly.
- `behavior_exercised`: every changed behavior is tied to a test or an explicit unverified-behavior finding.
- `quality_dimensions`: design, functionality, complexity, tests, naming, comments, and style have each been explicitly addressed or marked not applicable with a diff-based reason.
- `evidence_per_finding`: every finding has file/line or behavior evidence and a recommended next action.
- `risk_classified`: every finding has a risk level and a recommended next action.
- `surface_check`: public-surface, contract, schema, config, event, and shared-module impact has been addressed or marked not applicable with reason.
- `artifact_check`: missing rollback, telemetry, runbook, migration safety, threat consideration, and docs are listed when relevant.
- `diff_anchors`: final review includes at least two changed file:line citations, or states that the diff has fewer than two changed locations.

## Red Flags - Stop And Rework

- The review trusts the author's self-summary instead of checking the diff.
- Findings are stated as opinions without file/line or behavior evidence.
- New behavior is accepted because tests pass, without confirming any test would fail without the change.
- Deletions are accepted without checking for remaining callers, imports, or references.
- Out-of-scope file changes are merged because they "look harmless."
- Hallucinated APIs, types, or imports are not checked even though the author (human or AI) could have invented them.
- Specialist concerns (security, migration, rollout) are absorbed into this review instead of routed to the responsible specialist.
- The review produces prose only, with no categorized findings, evidence, next actions, or risk levels.
- The final verdict is given with fewer than two changed `file:line` evidence anchors when the diff contains enough changed lines.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Reviewing the author's narration | Review the diff against the originating task, not the self-summary. |
| Treating green tests as verification | Confirm a test exists that would fail without the change. |
| Reviewing line-by-line without intent | Group changes by purpose and check each group against stated intent. |
| Ignoring deletions | Search for remaining callers, imports, references, and tests of removed code. |
| Accepting plausible APIs at face value | Confirm imports, types, and external calls actually exist in the target environment. |
| Letting scope creep slide | Name out-of-scope edits and require justification or removal. |
| Skipping code-quality dimensions | Compactly cover design, functionality, complexity, tests, naming, comments, and style as part of the review artifact. |
| Doing the specialist's work here | Route security, migration, rollout, accessibility, and contract concerns to the responsible specialist. |
| Producing vibes review | Output a structured artifact with categories, evidence, next actions, and risk levels. |
| Giving a verdict before pinning evidence | Cite at least two changed `file:line` anchors first, then make the merge decision. |
