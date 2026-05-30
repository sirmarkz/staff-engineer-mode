# Router Evals

This directory holds the real-LLM adapter used by the router eval harness.
`SAMPLE-PROMPTS.md` is the canonical eval catalog. Each prompt is grouped under
the specialist that should handle it, so the user-facing examples and eval cases
cannot drift apart.

## How the harness treats the model

The harness contains no model. It is a deterministic scorer. It reads a response,
parses the ` ```routing ` JSON block out of it, and checks that block against the
expected specialist from `SAMPLE-PROMPTS.md`. The model lives outside the
harness, behind one of two flags:

- `--command "<cmd>"` runs a shell command per case. The harness pipes the prompt
  on stdin and reads the response from stdout. Point this at a real LLM to run a
  live eval.
- `--responses-dir <dir>` reads a saved `<case-id>.txt` file per case. Use this
  to score responses captured earlier, from any source.

Provide exactly one of the two when scoring. CI uses neither: it runs the scorer's
unit tests against canned strings (`scripts/test_run_router_eval.py`), so the
published pipeline never calls a model or the network.

## Files

| Path | Contains |
| --- | --- |
| `../SAMPLE-PROMPTS.md` | Canonical router eval catalog: four prompts per specialist plus four out-of-scope prompts, 220 total cases. |
| `adapters/codex-router.sh` | Real-LLM adapter that drives Codex as the router. Reads a prompt on stdin, writes a routing block on stdout. |
| `adapters/claude-router.sh` | Real-LLM adapter that drives Claude as the router. Reads a prompt on stdin, writes a routing block on stdout. |

## Run a live eval with Codex

The adapter wraps a prompt with router instructions, calls the model once, and
returns its routing block. `adapters/codex-router.sh` does this with Codex:

```bash
# Score one prompt per specialist plus one out-of-scope prompt (55 cases)
python3 scripts/run_router_eval.py \
  --command evals/adapters/codex-router.sh

# Score every sample prompt (220 cases)
python3 scripts/run_router_eval.py \
  --sample all \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json

# Score only the four out-of-scope prompts
python3 scripts/run_router_eval.py \
  --sample all \
  --category out_of_scope \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json
```

Each case is one live model call, so a full run takes minutes and costs tokens.
Full live runs are manual checks for router changes, model comparisons, and
targeted failure triage. Before tagging or publishing a release, run the manual
release-blocking live gate; do not add it to GitHub Actions. The gate samples
5 seeded random specialist cases from the specialist portion of the 220-case
catalog against Claude Opus 4.8 high and Codex `gpt-5.5` high via
`scripts/run_release_live_checks.py`. `--jobs` controls bounded parallelism;
keep it small enough to avoid provider rate limits.

Use the Claude adapter with the same scorer when comparing hosts:

```bash
CLAUDE_MODEL=claude-opus-4-8 CLAUDE_EFFORT=high \
  python3 scripts/run_router_eval.py \
    --sample all \
    --random-specialists 5 \
    --command evals/adapters/claude-router.sh \
    --json
```

Any adapter must print the model's routing block to stdout and nothing that
would confuse the parser. Send diagnostic logs to stderr.

## Score saved responses

When you already have model outputs, skip the live call:

```bash
# 1. List stable case IDs (format: NNN-<primary-slug>)
python3 scripts/run_router_eval.py --sample all --list-cases

# 2. Save each model response as <case-id>.txt, for example:
#    runs/2026-05-30/001-accessibility-gates.txt

# 3. Score the directory
python3 scripts/run_router_eval.py \
  --sample all \
  --responses-dir runs/2026-05-30
```

A response file holds the model's full reply for that prompt, including its
` ```routing ` block.

## Catalog Shape

Parsing enforces the catalog's shape before any model runs:

- four prompts per specialist and four out-of-scope prompts;
- every specialist covered;
- lifecycle phases represented;
- at least four context-only prompts without explicit lifecycle phase words.

## What a case checks

For each prompt the scorer requires a routing block whose `primary` matches the
specialist heading and whose `confidence` is `high` or `medium`. Sample-prompt
cases also require:

- `single_primary`: exactly one primary slug, never a list.
- `intent_inference`: `artifact`, `surface`, `phase`, and `rationale` are all present.
- `no_skill_invoke`: the response never calls the `Skill` tool on a specialist.

`read_load` remains available for saved responses from full agent runs: when a
case opts into that check, any substantive answer must include a `Read` of the
routed specialist file. Live adapter runs stay in eval-harness mode and score
the routing block only.

A run exits non-zero when any case fails, prints a per-category pass count, and
lists each failure with its reason. Add `--warn-only` to report failures without
failing the command.
