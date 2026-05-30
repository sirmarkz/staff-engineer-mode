#!/usr/bin/env bash
# Real-LLM adapter for the Staff Engineer Mode router eval harness.
# Reads ONE eval prompt on stdin, asks Claude to act as the SEM router in
# eval-harness mode, and writes the model's response to stdout.
set -euo pipefail

prompt="$(cat)"
model="${CLAUDE_MODEL:-claude-opus-4-8}"
effort="${CLAUDE_EFFORT:-medium}"
instructions="You are the Staff Engineer Mode router in eval-harness mode.
Load the staff-engineer-mode router, classify the prompt below, and output ONLY
a fenced \`\`\`routing block of JSON with fields: primary, secondary, confidence,
artifact, surface, phase, rationale. Use one primary slug from the router's
Bundled Specialist Slugs. No prose outside the block. If out of scope or
low-confidence, output no routing block.

PROMPT:
${prompt}"

claude -p "${instructions}" \
  --model "${model}" \
  --effort "${effort}" \
  --output-format text \
  --no-session-persistence \
  2>/dev/null
