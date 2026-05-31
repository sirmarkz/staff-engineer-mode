#!/usr/bin/env bash
# Real-LLM adapter for the Staff Engineer Mode router eval harness.
# Reads ONE eval prompt on stdin, asks Codex to act as the SEM router in
# eval-harness mode, and writes the model's response (with its ```routing
# block) to stdout. Used as:  run_router_eval.py --command evals/adapters/codex-router.sh
set -euo pipefail
prompt="$(cat)"
model="${CODEX_MODEL:-gpt-5.5}"
effort="${CODEX_EFFORT:-medium}"
instructions="You are the Staff Engineer Mode router in eval-harness mode.
Load the staff-engineer-mode router, classify the prompt below, and output ONLY
a fenced \`\`\`routing block of JSON with fields: primary, secondary, confidence,
artifact, surface, phase, rationale. Use one primary slug from the router's
Bundled Specialist Slugs. No prose outside the block. If out of scope or
low-confidence, output no routing block.

PROMPT:
${prompt}"
codex exec \
  --model "${model}" \
  --config "model_reasoning_effort='${effort}'" \
  --skip-git-repo-check \
  --color never \
  "${instructions}"
