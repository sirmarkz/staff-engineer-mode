# Specialist Slug Rename Audit

## Decision Rule

Rename a specialist only when the current slug causes realistic routing failures
and the replacement is narrower or clearer without hiding the specialist
boundary. Existing slugs are public routing contracts, so a rename requires
fixture coverage, sample-prompt updates, install docs review, and release notes.

## Candidates

| Current | Proposed | Decision | Reason |
| --- | --- | --- | --- |
| `agent-pr-review` | `pre-merge-risk-review` | defer | Diff-only scope is intentional; examples and lifecycle routing should point pre-code work to other specialists. |
| `code-review-and-workflow` | `review-system-design` | test | Natural review-system design wording should still route to the current slug before any rename is considered. |
| `engineering-control-evidence` | `engineering-evidence-mapping` | test | The current slug preserves the cross-surface control boundary; natural evidence-mapping prompts should prove whether it is too audit-shaped. |
| `dependency-and-code-hygiene` | `codebase-maintenance` | test | More natural cleanup wording may help, but the replacement risks becoming too broad. |
| `release-build-reproducibility` | `build-artifact-reproducibility` | test | Artifact wording is clearer; keep current slug if natural build-artifact prompts route correctly. |
| `configuration-and-automation-safety` | `config-automation-safety` | defer | Shorter, but not materially clearer. |
| `ml-reliability-and-evaluation` | `model-reliability-and-evaluation` | test | More natural language, but must not blur LLM application, eval, and serving boundaries. |
| `secure-sdlc-and-threat-modeling` | `secure-design-and-threat-modeling` | test | Clearer lifecycle wording; verify current slug still handles secure-design prompts. |
| `platform-golden-paths` | `platform-engineering` | defer | Replacement is broader and may attract unrelated platform work. |
| `llm-serving-cost-and-latency` | `llm-serving-performance` | defer | Current slug preserves cost and latency specificity. |

## Current Decision

No slug rename is included in this change. Add counterfactual lifecycle probes
for candidate wording first; rename only if the current slug produces repeated
live routing failures for realistic prompts.
