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
| `prompts/adversarial-split.md` | Gray-box route-injection cases accepted by an independent white-box reviewer. | The injected label is suppressed and the genuine artifact wins. |
| `prompts/router-contracts.md` | Mixed-intent, ambiguity, secondary, lifecycle, capability-translation, and broad-audit routing contracts. | The router satisfies every declared check and keeps one primary. |
| `prompts/specialist-behavior.json` | High-risk lexical smoke checks after a specialist and its templates are loaded. | The answer includes required terms and omits known-bad claims; a human reviews the full response. |

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
| `prompts/adversarial-split-draft.json` | Versioned gray-box authorship record and all 24 answer-free draft cases. |
| `prompts/adversarial-split.md` | The 20 cases accepted after white-box review. |
| `prompts/adversarial-split-review.json` | Versioned review record, access separation, dispositions, rationale, and coverage. |
| `prompts/router-contracts.md` | Hand-authored contract cases for dimensions the grouped catalogs cannot express. |
| `adapters/codex-router.sh` | Live Codex adapter. Reads one prompt on stdin and writes one routing response on stdout. |
| `adapters/claude-router.sh` | Live Claude adapter. Reads one prompt on stdin and writes one routing response on stdout. |
| `adapters/codex-specialist.sh` | Live Codex adapter for response-level specialist behavior cases. |

## Local Validation

Run this before live evals or commits:

```bash
python3 scripts/validate_router_eval.py
python3 -m unittest scripts/test_run_router_eval.py scripts/test_validate_router_eval.py scripts/test_run_specialist_eval.py
```

Validation checks catalog shape before any model runs:

- expected-route catalog covers every specialist with five prompts and keeps four out-of-scope cases;
- boundary files cover every specialist with five prompts for each boundary category;
- boundary cases never expect the target specialist under their heading;
- keyword-bait and adversarial prompts name the target specialist;
- adversarial cases include the `no_skill_invoke` check;
- split-access cases match the draft verbatim, accepted and rejected dispositions reconcile, and the review version binds the gray-box and white-box records;
- contract cases cover direct, paraphrase, mixed-intent, ambiguous, and out-of-scope categories, every lifecycle phase, secondary limits, and capability translation;
- live adapters load the local router and routing matrix in clean temporary homes and working directories with host tools disabled.

The Claude adapter copies only `.credentials.json` into its temporary config,
clears simple mode so OAuth remains available, loads no user, project, or local
settings, and disables tools, slash commands, and non-explicit MCP servers.

Classifier output cannot prove that a routed runtime answer issued the required
specialist `Read`. `scripts/validate_skill_pack.py` statically protects the
router's specialist-loading instructions; runtime host probes cover behavioral
loading where their event contract requires it.

`--eval-file` accepts the same required keys, route names, checks, phase values,
and nonempty fields as the canonical case contract. It scores the full custom
catalog unless you select cases with category, ID, limit, or random controls.
The harness rejects `--sample` with a custom file because specialist sampling
belongs to the built-in catalogs. Custom-run manifests record
`selection_mode: custom_catalog` and `sample: null` when no selector applies.

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

# Independently authored and reviewed route-injection cases.
python3 scripts/run_router_eval.py --catalog adversarial-split --list-cases

# Mixed-intent and routing-contract cases.
python3 scripts/run_router_eval.py --catalog contract --list-cases
```

`--catalog sample` remains a legacy alias for `--catalog positive`.
The alias is canonicalized to `positive` in manifests and case IDs. Built-in
IDs combine the canonical catalog with a 16-character digest of the normalized
prompt, such as `positive-6ed6e86e20e78fb5`. They do not include the expected
route, category, or catalog position, so a source case keeps its ID through
sampling, reordering, insertion, and corrected expectations. Duplicate prompt
content is rejected as an ID collision.

## Targeted Reruns

Use the same catalog and sampling flags that produced the failed case IDs, then
select the failures directly:

```bash
python3 scripts/run_router_eval.py \
  --catalog all \
  --sample all \
  --case-id positive-6ed6e86e20e78fb5 \
  --case-id boundary-59c8f82115072f98 \
  --command evals/adapters/codex-router.sh \
  --json
```

For longer lists, put one case ID per line. Lines copied from failure output
such as `boundary-59c8f82115072f98 failed:` are accepted.

```bash
python3 scripts/run_router_eval.py \
  --catalog all \
  --sample all \
  --case-id-file evals/runs/full-failures.txt \
  --command evals/adapters/codex-router.sh \
  --json
```

Do not mix targeted IDs with `--limit`, `--random`,
`--random-specialists`, `--stratified-categories`, or `--check-cover`; those
change the case population. After targeted fixes pass, run the full affected
slice again before treating the eval as clean.

## Live Runs

The harness is deterministic; the model is only behind `--command`. Each case is
one live model call. Keep `--jobs` bounded to avoid provider rate limits.
For a known adapter, the harness resolves the provider override or documented
default once per run. It records that model and effort in the manifest and
passes the same values to each case. The Codex router and specialist defaults
are `gpt-5.6-terra` with `high` effort; the Claude router default is
`claude-opus-4-8` with `medium` effort.

```bash
# Make the Codex defaults explicit for the commands below.
export CODEX_MODEL=gpt-5.6-terra
export CODEX_EFFORT=high

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
CLAUDE_MODEL=claude-opus-4-8 CLAUDE_EFFORT=medium \
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --category adversarial \
  --random-specialists 5 \
  --seed adversarial-smoke \
  --command evals/adapters/claude-router.sh \
  --json

# Full split-access adversarial catalog.
python3 scripts/run_router_eval.py \
  --catalog adversarial-split \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --results-dir evals/runs/adversarial-split \
  --json

# Full boundary catalog.
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json

# One seeded case from every contract category.
python3 scripts/run_router_eval.py \
  --catalog contract \
  --stratified-categories 1 \
  --seed contract-smoke \
  --command evals/adapters/codex-router.sh \
  --json

# Small deterministic set that covers release-critical contract checks.
python3 scripts/run_router_eval.py \
  --catalog contract \
  --check-cover capability_translation \
  --check-cover ambiguity_check \
  --check-cover scope_check \
  --check-cover secondary_cap \
  --seed contract-cover \
  --command evals/adapters/codex-router.sh \
  --results-dir evals/runs/router-contract-cover \
  --json

# Positive, boundary, and contract catalogs together.
python3 scripts/run_router_eval.py \
  --catalog all \
  --sample all \
  --jobs 4 \
  --command evals/adapters/codex-router.sh \
  --json
```

Adapters must print the model response to stdout and diagnostics to stderr. A
routed response is valid only when, after trimming transport whitespace, it is
exactly one fenced `routing` JSON object with no surrounding prose, the declared
fields and types, and an allowed phase. A withheld response must be the exact
literal `WITHHOLD`; the two wire forms are exclusive. Live evals are manual
checks and should stay out of default CI. JSON
summaries include `failure_types` so triage can distinguish route mismatches,
over-routing on `none` cases, malformed or missing routing blocks, and harness
contract errors.

On a nonzero adapter exit, both harnesses persist the exit status and whether
stdout or stderr contained diagnostics, but omit the raw diagnostic text. This
keeps tokens or credentials printed by a failed host process out of evidence.

Prefer `--results-dir`. It atomically reserves a new run directory before the
first adapter call, writes the manifest and scored records to `results.jsonl`,
and saves each exact final response under `responses/<case-id>.txt`. Every case
record includes the parsed structured wire fields and response SHA-256, so the
evidence can be audited and rescored. `--results-jsonl` is an exclusive
single-file alternative that includes the raw response in each case record.
Both forms refuse existing destinations.

The versioned manifest contains selected IDs, per-prompt and per-catalog-input
hashes, harness/router/adapter hashes, safe adapter identity, host CLI version,
model and effort, every selection and execution control, seed, Git SHA and dirty
state, UTC time, and split-access context. Saved-response runs are marked
`saved`, ignore ambient model variables, and bind every input response by
SHA-256. Manifests do not copy authentication data, raw environment variables,
or command arguments. Both live harnesses also identify and hash the shared
adapter protocol module so a result detects changes to workspace or model
resolution behavior.

For each live case, the Python harness creates a mode-`0700` temporary adapter
workspace and passes its path, resolved model, and effort through the private
`SEM_EVAL_*` adapter protocol. The real adapters require that protocol and copy
the minimum host credential file only beneath the supplied workspace. The
Python harness removes the workspace after success, adapter failure, or
process-group termination on timeout. Invoke these adapters through their
harness. Treat `SEM_EVAL_*` variables as private implementation details.

Boundary and split-access manifests also record the adversarial batch ID,
review version and date, author and reviewer access levels, and disposition
counts. The manifest hashes the draft, accepted catalog, and review record. A
result can therefore identify the exact answer-free author input and the later
white-box decision record.

Slice thresholds should be set before running a release check. Do not let a high
aggregate score hide failures in `negative`, `near_miss`, `keyword_bait`, or
`adversarial`; direct override cases should pass without waivers.

The release gate reserves a new evidence directory before it starts any static
or live step. Pass `--evidence-dir` when an operator or release record requires
a known path. Without the flag, the gate creates a timestamped directory under
`evals/runs/`. The gate keeps hook-probe logs under `hook-probes/`; each host and
router slice receives its own write-once run directory.
Its release models and effort are fixed to Claude Opus 4.8 high and Codex
`gpt-5.6-terra` high. Use the lower-level probe or eval harness for diagnostic
model comparisons; those runs do not satisfy this release gate.

```bash
python3 scripts/run_release_live_checks.py \
  --evidence-dir evals/runs/release-candidate-1
```

## Specialist Behavior Runs

The response-level catalog loads the local specialist and every template owned
by that specialist, asks the model for the requested artifact, then performs
hand-authored required-term and forbidden-claim checks. The matcher recognizes
tokens with a small inflection suffix set; catalog authors must add `*` when a
term is an intentional prefix stem. A match in a nearby negated clause does not
count as positive evidence. Only real Markdown table separators make negation
cell-local: escaped pipes, ordinary prose pipes, and pipes inside same-line or
multiline code spans, indented code, and root- or list-contained fences do not
create cell boundaries. The summary and manifest label this `lexical_smoke`.
It is a manual, non-gating regression signal, not a semantic proof. Review
representative passing responses as well as every failing response before using
the run to change a rubric, specialist, or release decision.

```bash
CODEX_MODEL=gpt-5.6-terra CODEX_EFFORT=high \
python3 scripts/run_specialist_eval.py \
  --command evals/adapters/codex-specialist.sh \
  --jobs 2 \
  --results-dir evals/runs/specialist-gpt-5.6-terra \
  --json
```

The results directory is write-once for a run: the harness refuses to overwrite
an existing manifest, scored record stream, or response. `manifest.json` records
the selected case IDs, prompt/catalog/harness and adapter hashes, model and
effort, Git state, UTC time, split-access context, and the evidence layout.
`results.jsonl` begins with the same manifest, appends one scored case record per
saved response with its SHA-256 and progress counts, and ends with the validated
final summary. Auditors can reconcile the selected IDs and final count from the
record stream and detect a changed response without trusting the later contents
of its mutable text file.
Directory components are opened without following symlinks, and later writes
stay anchored to the reserved directory descriptor.

## Saved Responses

Use saved responses when you already captured model output:

```bash
# 1. List stable case IDs.
python3 scripts/run_router_eval.py --catalog boundary --list-cases

# 2. Save each response as <case-id>.txt under the ignored eval run directory.
#    Example: evals/runs/boundary/boundary-59c8f82115072f98.txt

# 3. Score the directory.
python3 scripts/run_router_eval.py \
  --catalog boundary \
  --responses-dir evals/runs/boundary \
  --results-dir evals/runs/boundary-rescore \
  --json
```

The harness opens each selected response once without following a final symlink,
captures its bytes, and hashes that snapshot before scoring. The scorer and
result writer use the captured content, so a later path replacement cannot
change the response bound to the manifest. Each response must contain one exact
router wire form. The rescore directory copies the captured responses and
records their hashes and parsed fields.
Treat `evals/runs/` as local diagnostic output: redact prompts or responses that
contain repository secrets, customer data, credentials, or private code; retain
only as long as needed to diagnose the run. The directory is ignored by Git.

## Designing Boundary Cases

Use a separate gray-box or black-box author when adding route-injection cases.
Give the author the target boundary, allowed interface, risk intent, and failure
class. Withhold expected routes, route rationales, existing cases, router
implementation, scoring code, and happy-path examples. Also withhold expected
traces, reference solutions, and implementation notes when the evaluated
boundary has those artifacts. Save the answer-free draft before a white-box
reviewer assigns expectations. The reviewer records
accepted and rejected cases, ambiguity decisions, duplication checks, and the
versioned access separation. Keep all three artifacts; rejected drafts prove
that curation happened after authorship.
