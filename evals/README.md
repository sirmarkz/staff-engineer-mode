# Router Evals

This directory holds the router eval fixtures and the harness that scores a
model's routing decisions against them. The harness measures one thing: whether
Staff Engineer Mode picks the right specialist for an engineering prompt.

## How the harness treats the model

The harness contains no model. It is a deterministic scorer. It reads a response,
parses the ` ```routing ` JSON block out of it, and checks that block against the
expected outcome in the fixture. The model lives outside the harness, behind
one of two flags:

- `--command "<cmd>"` runs a shell command per case. The harness pipes the prompt
  on stdin and reads the response from stdout. Point this at a real LLM to run a
  live eval.
- `--responses-dir <dir>` reads a saved `<case-id>.txt` file per case. Use this to
  score responses you captured earlier, from any source.

Provide exactly one of the two. CI uses neither: it runs the scorer's unit tests
against canned strings (`scripts/test_run_router_eval.py`), so the published
pipeline never calls a model or the network.

## Files

| Path | Contains |
| --- | --- |
| `router/router-eval-set.yaml` | 130 curated cases: direct, paraphrased, ambiguous, mixed-intent, and out-of-scope prompts with expected primary and checks. |
| `router/router-phase-eval-set.yaml` | Phase-focused cases that exercise lifecycle-phase inference. |
| `adapters/codex-router.sh` | Real-LLM adapter that drives Codex as the router. Reads a prompt on stdin, writes a routing block on stdout. |

The sample-prompt runner reads its cases from `../SAMPLE-PROMPTS.md` rather than a
fixture in this directory.

## Run a live eval with a real LLM

The adapter wraps a prompt with router instructions, calls the model once, and
returns its routing block. `adapters/codex-router.sh` does this with Codex:

```bash
# Score the first 5 cases against Codex
python3 scripts/run_router_eval.py \
  --command evals/adapters/codex-router.sh \
  --limit 5

# Score every case and write a machine-readable summary
python3 scripts/run_router_eval.py \
  --command evals/adapters/codex-router.sh \
  --json
```

Drop `--limit` to run all 130 cases. Each case is one live model call, so a full
run takes minutes and costs tokens. Start small.

To drive a different model, copy the adapter and swap the final command. A Claude
Code adapter reads the same stdin prompt and calls `claude -p`:

```bash
#!/usr/bin/env bash
set -euo pipefail
prompt="$(cat)"
claude -p "You are the Staff Engineer Mode router in eval-harness mode. Classify
the prompt and output ONLY a fenced \`\`\`routing JSON block with fields primary,
secondary, confidence, artifact, surface, phase, rationale. One primary slug from
the Bundled Specialist Slugs. No prose outside the block. Out of scope or
low-confidence: output no routing block.

PROMPT:
${prompt}"
```

The adapter must print the model's routing block to stdout and nothing that would
confuse the parser. Send diagnostic logs to stderr.

## Score saved responses

When you already have model outputs, skip the live call:

```bash
# 1. List the stable case IDs (format: NNN-<primary-slug>)
python3 scripts/run_router_eval.py --list-cases

# 2. Save each model response as <case-id>.txt, for example:
#    runs/2026-05-30/001-architecture-decisions.txt

# 3. Score the directory
python3 scripts/run_router_eval.py --responses-dir runs/2026-05-30
```

A response file holds the model's full reply for that prompt, including its
` ```routing ` block.

## Score the sample prompts

`SAMPLE-PROMPTS.md` is the user-facing prompt catalog. Every prompt is grouped
under the specialist that should handle it, so the file doubles as an eval set.
`scripts/run_sample_prompt_router_eval.py` parses those groupings and scores each
prompt the same way, against its heading's specialist.

```bash
# One prompt per specialist (54 cases) through Codex
python3 scripts/run_sample_prompt_router_eval.py \
  --command evals/adapters/codex-router.sh

# Every sample prompt (216 cases)
python3 scripts/run_sample_prompt_router_eval.py \
  --sample all \
  --command evals/adapters/codex-router.sh

# Score saved responses instead of a live model
python3 scripts/run_sample_prompt_router_eval.py \
  --responses-dir runs/sample
```

`--sample one-per-specialist` is the default and rotates which prompt it picks per
specialist across runs. `--sample all` scores the full catalog. Both runners share
the same scorer, case-ID scheme, and `--list-cases`, `--json`, and `--warn-only`
flags.

Parsing also enforces the catalog's shape: four prompts per specialist, every
specialist covered, lifecycle phases represented, and enough context-only prompts
that carry no explicit phase word. A malformed catalog fails before any model
runs.

## What a case checks

For an in-scope prompt the scorer requires a routing block whose `primary` matches
the expected slug and whose `confidence` is `high` or `medium`. Per-case
`expected_checks` add stricter assertions:

- `single_primary`: exactly one primary slug, never a list.
- `secondary_cap`: at most one secondary, matching the expected value.
- `intent_inference`: `artifact`, `surface`, `phase`, and `rationale` are all present.
- `capability_translation`: tool names from the prompt (Datadog, Istio, GraphQL,
  and the like) do not reappear in the routing text.
- `ambiguity_check` and `scope_check`: ambiguous or out-of-scope prompts emit no
  routing block.
- `no_skill_invoke`: the response never calls the `Skill` tool on a specialist.
- `read_load`: a substantive answer includes a `Read` of the routed specialist file.

A run exits non-zero when any case fails, prints a per-category pass count, and
lists each failure with its reason. Add `--warn-only` to report failures without
failing the command.
