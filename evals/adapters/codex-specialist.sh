#!/usr/bin/env bash
# Real-LLM adapter for response-level specialist behavior evals.
set -euo pipefail
instructions="$(cat)"
tmp_dir="${SEM_EVAL_ADAPTER_WORKSPACE:?run this adapter through scripts/run_specialist_eval.py}"
model="${SEM_EVAL_MODEL:?run this adapter through scripts/run_specialist_eval.py}"
effort="${SEM_EVAL_EFFORT:?run this adapter through scripts/run_specialist_eval.py}"
if [[ ! -d "${tmp_dir}" || -L "${tmp_dir}" ]]; then
  printf 'eval adapter workspace must be a real directory\n' >&2
  exit 2
fi
source_codex_home="${CODEX_HOME:-${HOME}/.codex}"
isolated_home="${tmp_dir}/home"
isolated_codex_home="${tmp_dir}/codex-home"
work_dir="${tmp_dir}/work"
mkdir -p "${isolated_home}" "${isolated_codex_home}" "${work_dir}"
if [[ -f "${source_codex_home}/auth.json" ]]; then
  cp "${source_codex_home}/auth.json" "${isolated_codex_home}/auth.json"
  chmod 600 "${isolated_codex_home}/auth.json"
fi
last_message="${tmp_dir}/last-message.txt"

HOME="${isolated_home}" CODEX_HOME="${isolated_codex_home}" codex exec \
  --model "${model}" \
  --config "model_reasoning_effort='${effort}'" \
  --ignore-user-config \
  --ignore-rules \
  --ephemeral \
  --strict-config \
  --sandbox read-only \
  -C "${work_dir}" \
  --disable shell_tool \
  --disable unified_exec \
  --disable code_mode_host \
  --disable browser_use \
  --disable browser_use_external \
  --disable browser_use_full_cdp_access \
  --disable computer_use \
  --disable in_app_browser \
  --disable apps \
  --disable image_generation \
  --disable multi_agent \
  --disable goals \
  --disable hooks \
  --disable plugins \
  --disable remote_plugin \
  --disable skill_mcp_dependency_install \
  --disable tool_call_mcp_elicitation \
  --disable request_permissions_tool \
  --disable standalone_web_search \
  --skip-git-repo-check \
  --output-last-message "${last_message}" \
  --color never \
  "${instructions}" >&2

cat "${last_message}"
