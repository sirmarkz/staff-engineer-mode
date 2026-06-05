# Router Evals

This directory contains the router eval catalogs, live-model adapters, and
operator instructions. These files are eval inputs, not runtime skill guidance.

## What Is Tested

| File | What it tests | Expected result |
| --- | --- | --- |
| `prompts/expected-routes.md` | Normal in-scope engineering prompts grouped by the specialist that should handle them. | The router selects the grouped specialist. |
| `prompts/negative.md` | Routine, out-of-scope, or neighboring work that could falsely trigger the grouped specialist. | The grouped specialist does not fire. |
| `prompts/near-miss.md` | In-scope work close to the grouped specialist but owned by another specialist. | The narrower or more correct neighboring specialist fires. |
| `prompts/keyword-bait.md` | Prompts that name the grouped specialist or label while asking for another artifact. | Keyword matching does not win. |
| `prompts/adversarial.md` | Prompts that explicitly try to force the wrong grouped specialist. | The override is ignored. |

Correct-routing prompts use the same shape as the public examples: specialist
headings with quoted prompt bullets. Boundary files use the same grouped shape;
the suffix on each bullet gives the correct route:

```markdown
### `documentation-lifecycle`

- "Fix README typos without ownership or freshness decisions." (-> `none`)
```

## Files

| Path | Contains |
| --- | --- |
| `prompts/expected-routes.md` | Expected-route catalog: five prompts per specialist plus four out-of-scope prompts. |
| `prompts/negative.md` | Negative false-positive cases by target specialist, five prompts per specialist. |
| `prompts/near-miss.md` | Near-miss neighboring-specialist cases by target specialist, five prompts per specialist. |
| `prompts/keyword-bait.md` | Target-name and label bait cases by target specialist, five prompts per specialist. |
| `prompts/adversarial.md` | Explicit wrong-route override cases by target specialist, five prompts per specialist. |
| `adapters/codex-router.sh` | Live Codex adapter. Reads one prompt on stdin and writes one routing response on stdout. |
| `adapters/claude-router.sh` | Live Claude adapter. Reads one prompt on stdin and writes one routing response on stdout. |

## Local Validation

Run this before live evals or commits:

```bash
python3 scripts/validate_router_eval.py
python3 -m unittest scripts/test_run_router_eval.py scripts/test_validate_router_eval.py
```

Validation checks catalog shape before any model runs:

- expected-route catalog covers every specialist with five prompts and keeps four out-of-scope cases;
- boundary files cover every specialist with five prompts for each boundary category;
- boundary cases never expect the target specialist under their heading;
- keyword-bait and adversarial prompts name the target specialist;
- adversarial cases include the `no_skill_invoke` check;
- live adapters load the local router and routing matrix.

## Listing Cases

```bash
# One expected-route case per specialist plus one out-of-scope case.
python3 scripts/run_router_eval.py --catalog positive --list-cases

# Every expected-route case.
python3 scripts/run_router_eval.py --catalog positive --sample all --list-cases

# Every boundary case from all boundary files.
python3 scripts/run_router_eval.py --catalog boundary --list-cases

# One boundary category.
python3 scripts/run_router_eval.py --catalog boundary --category adversarial --list-cases
```

`--catalog sample` remains a legacy alias for `--catalog positive`.

## Targeted Reruns

Use the same catalog and sampling flags that produced the failed case IDs, then
select the failures directly:

```bash
python3 scripts/run_router_eval.py \
  --catalog all \
  --sample all \
  --case-id 068-release-build-reproducibility \
  --case-id 748-data-contracts \
  --command evals/adapters/codex-router.sh \
  --json
```

For longer lists, put one case ID per line. Lines copied from failure output
such as `748-data-contracts failed:` are accepted.

```bash
python3 scripts/run_router_eval.py \
  --catalog all \
  --sample all \
  --case-id-file runs/full-failures.txt \
  --command evals/adapters/codex-router.sh \
  --json
```

Do not mix targeted IDs with `--limit`, `--random`, or
`--random-specialists`; those change the case population. After targeted fixes
pass, run the full affected slice again before treating the eval as clean.

## Live Runs

The harness is deterministic; the model is only behind `--command`. Each case is
one live model call. Keep `--jobs` bounded to avoid provider rate limits.

```bash
# Expected-route smoke: one case per specialist plus one out-of-scope case.
python3 scripts/run_router_eval.py \
  --catalog positive \
  --command evals/adapters/codex-router.sh \
  --json

# Full expected-route catalog.
python3 scripts/run_router_eval.py \
  --catalog positive \
  --sample all \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json

# Seeded boundary smoke, one random case per selected target specialist.
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --random-specialists 5 \
  --seed boundary-smoke \
  --command evals/adapters/codex-router.sh \
  --json

# One boundary category with Claude.
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --category adversarial \
  --random-specialists 5 \
  --seed adversarial-smoke \
  --command evals/adapters/claude-router.sh \
  --json

# Full boundary catalog.
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json

# Expected-route and boundary catalogs together.
python3 scripts/run_router_eval.py \
  --catalog all \
  --sample all \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json
```

Adapters must print the model response to stdout and diagnostics to stderr. Live
evals are manual checks and should stay out of default CI. JSON summaries include
`failure_types` so triage can distinguish route mismatches, over-routing on
`none` cases, malformed or missing routing blocks, and harness contract errors.

Slice thresholds should be set before running a release check. Do not let a high
aggregate score hide failures in `negative`, `near_miss`, `keyword_bait`, or
`adversarial`; direct override cases should pass without waivers.

## Saved Responses

Use saved responses when you already captured model output:

```bash
# 1. List stable case IDs.
python3 scripts/run_router_eval.py --catalog boundary --list-cases

# 2. Save each response as <case-id>.txt under a run directory.
#    Example: runs/boundary/001-none.txt

# 3. Score the directory.
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --responses-dir runs/boundary \
  --json
```

The response file should include the model's fenced `routing` JSON block.

## Designing Boundary Cases

Use adversarial subagents when adding or refreshing boundary cases. Give each
subagent a bounded file or specialist slice, the target boundary, the allowed
interface, the risk intent, and the failure class. Do not give the case author
expected traces, reference solutions, implementation notes, happy-path examples,
or route rationales. A white-box reviewer may use that context afterward to
curate drafts, remove duplicates, confirm the expected route is not the heading
specialist, and run local validation.
