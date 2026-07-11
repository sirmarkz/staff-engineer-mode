#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from eval_adapter_protocol import (
    AdapterSettings,
    adapter_failure_message,
    build_adapter_environment,
    open_exclusive_file_at,
    reserve_run_directory,
    resolve_adapter_settings as resolve_protocol_settings,
)

ADAPTER_PROTOCOL_PATH = SCRIPT_DIR / "eval_adapter_protocol.py"
CATALOG = ROOT / "evals" / "prompts" / "specialist-behavior.json"
SPECIALISTS = ROOT / "specialists"
TEMPLATES = ROOT / "skills" / "_shared" / "assets" / "templates"
CASE_FIELDS = {"id", "specialist", "prompt", "required", "forbidden"}
SAFE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NEGATION_RE = re.compile(
    r"\b(?:no|not|never|without|cannot|can't|won't|must\s+not|should\s+not|"
    r"do\s+not|does\s+not|did\s+not|avoid|omit|exclude|lacks?|lacking|absent)\b",
    re.IGNORECASE,
)
FENCE_RE = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<rest>.*)$")
CONTAINER_PREFIX_RE = re.compile(
    r"^(?: {0,3}>[ \t]?| {0,3}(?:[-+*]|\d{1,9}[.)])[ \t]+)"
)
TABLE_DELIMITER_CELL_RE = re.compile(r"^:?-+:?$")


def fail(message: str) -> None:
    print(f"specialist eval failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def specialist_path(slug: Any, context: str) -> Path:
    if not isinstance(slug, str) or not SAFE_SLUG_RE.fullmatch(slug):
        fail(f"{context} has unsafe specialist slug {slug!r}")
    candidate = (SPECIALISTS / f"{slug}.md").resolve()
    try:
        relative = candidate.relative_to(SPECIALISTS.resolve())
    except ValueError:
        fail(f"{context} specialist escapes specialists directory")
    if relative.parent != Path(".") or not candidate.is_file():
        fail(f"{context} references missing specialist {slug!r}")
    return candidate


def load_cases(path: Path = CATALOG) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, list) or not value:
        fail(f"{path} must contain a non-empty JSON array")
    seen: set[str] = set()
    for index, case in enumerate(value, 1):
        if not isinstance(case, dict):
            fail(f"{path} case {index} must be an object")
        if set(case) != CASE_FIELDS:
            fail(
                f"{path} case {index} fields mismatch: "
                f"missing={sorted(CASE_FIELDS - set(case))}, "
                f"extra={sorted(set(case) - CASE_FIELDS)}"
            )
        case_id = case["id"]
        if not isinstance(case_id, str) or not SAFE_SLUG_RE.fullmatch(case_id):
            fail(f"{path} case {index} has unsafe id {case_id!r}")
        if case_id in seen:
            fail(f"{path} duplicate case id {case_id!r}")
        seen.add(case_id)

        specialist_path(case["specialist"], f"{path} case {case_id!r}")

        prompt = case["prompt"]
        if not isinstance(prompt, str) or not prompt.strip():
            fail(f"{path} case {case_id!r} prompt must be a non-empty string")
        required = case["required"]
        if not isinstance(required, list) or not required:
            fail(f"{path} case {case_id!r} needs required concept groups")
        if not all(
            isinstance(group, str)
            and group.strip()
            and all(part.strip() for part in group.split("|"))
            for group in required
        ):
            fail(f"{path} case {case_id!r} required groups must contain non-empty strings")
        forbidden = case["forbidden"]
        if not isinstance(forbidden, list):
            fail(f"{path} case {case_id!r} forbidden must be a list")
        if not all(
            isinstance(claim, str)
            and claim.strip()
            and all(part.strip() for part in claim.split("|"))
            for claim in forbidden
        ):
            fail(f"{path} case {case_id!r} forbidden claims must be non-empty strings")
    return value


def owned_templates(slug: str) -> list[Path]:
    paths: list[Path] = []
    for line in (TEMPLATES / "README.md").read_text().splitlines():
        if not line.startswith("| `"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) == 4 and columns[1].strip("`") == slug:
            candidate = (TEMPLATES / columns[0].strip("`")).resolve()
            try:
                candidate.relative_to(TEMPLATES.resolve())
            except ValueError:
                fail(f"template ownership entry escapes template directory for {slug!r}")
            if not candidate.is_file():
                fail(f"template ownership entry for {slug!r} is missing {candidate.name!r}")
            paths.append(candidate)
    return paths


def build_prompt(case: dict[str, Any]) -> str:
    slug = str(case["specialist"])
    specialist_text = specialist_path(slug, f"case {case.get('id')!r}").read_text()
    template_text = "\n\n".join(
        f"TEMPLATE {path.name}:\n{path.read_text()}" for path in owned_templates(slug)
    )
    return f"""Answer the user request using only the local specialist guidance and templates below.
Produce the smallest complete operational artifact for the request. State assumptions where local facts are
missing. Do not discuss this evaluation, the rubric, or the supplied source text.

LOCAL SPECIALIST ({slug}):
{specialist_text}

LOCAL OWNED TEMPLATES:
{template_text or '(none)'}

USER REQUEST:
{case['prompt']}
"""


def concept_pattern(concept: str) -> re.Pattern[str]:
    tokens = re.findall(r"[a-z0-9]+\*?", concept.casefold())
    if not tokens:
        raise ValueError(f"concept has no searchable tokens: {concept!r}")
    token_patterns: list[str] = []
    for token in tokens:
        if token.endswith("*"):
            token_patterns.append(re.escape(token[:-1]) + r"[\w]*")
        else:
            token_patterns.append(
                re.escape(token) + r"(?:s|es|ed|ing|er|ers)?"
            )
    body = r"(?:[\s_-]+)".join(token_patterns)
    identifier_token = r"[^\W_]"
    return re.compile(
        rf"(?<!{identifier_token})" + body + rf"(?!{identifier_token})",
        re.IGNORECASE,
    )


def character_is_escaped(value: str, index: int) -> bool:
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and value[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def backtick_run_length(value: str, start: int) -> int:
    end = start
    while end < len(value) and value[end] == "`":
        end += 1
    return end - start


def matching_backtick_closer(value: str, start: int, length: int) -> int | None:
    cursor = start
    while cursor < len(value):
        candidate = value.find("`", cursor)
        if candidate < 0:
            return None
        run_length = backtick_run_length(value, candidate)
        if (
            run_length == length
            and not character_is_escaped(value, candidate)
        ):
            return candidate
        cursor = candidate + run_length
    return None


def markdown_container_content(line: str) -> tuple[str, int]:
    content = line
    prefix_length = 0
    while True:
        prefix = CONTAINER_PREFIX_RE.match(content)
        if prefix is None:
            return content, prefix_length
        prefix_length += prefix.end()
        content = content[prefix.end() :]


def is_indented_code_line(line: str) -> bool:
    return line.startswith("\t") or len(line) - len(line.lstrip(" ")) >= 4


def code_span_ranges(value: str, offset: int = 0) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(value):
        candidate = value.find("`", cursor)
        if candidate < 0:
            break
        run_length = backtick_run_length(value, candidate)
        if character_is_escaped(value, candidate):
            cursor = candidate + run_length
            continue
        closer = matching_backtick_closer(
            value, candidate + run_length, run_length
        )
        if closer is None:
            cursor = candidate + run_length
            continue
        end = closer + run_length
        ranges.append((offset + candidate, offset + end))
        cursor = end
    return ranges


def inline_code_ranges(
    response: str, lines: list[dict[str, Any]]
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    segment_start: int | None = None
    for item in lines:
        if item["block_code"]:
            if segment_start is not None:
                ranges.extend(
                    code_span_ranges(
                        response[segment_start : item["start"]], segment_start
                    )
                )
                segment_start = None
        elif segment_start is None:
            segment_start = item["start"]
    if segment_start is not None:
        ranges.extend(code_span_ranges(response[segment_start:], segment_start))
    return ranges


def noncode_pipe_positions(
    line: str,
    line_start: int,
    code_ranges: list[tuple[int, int]],
) -> list[int]:
    return [
        line_start + index
        for index, character in enumerate(line)
        if character == "|"
        and not character_is_escaped(line, index)
        and not any(
            range_start <= line_start + index < range_end
            for range_start, range_end in code_ranges
        )
    ]


def table_cells(line: str, line_start: int, pipes: list[int]) -> list[str]:
    local_pipes = [position - line_start for position in pipes]
    cells: list[str] = []
    cell_start = 0
    for position in local_pipes:
        cells.append(line[cell_start:position].strip())
        cell_start = position + 1
    cells.append(line[cell_start:].strip())
    if local_pipes and not line[: local_pipes[0]].strip():
        cells = cells[1:]
    if local_pipes and not line[local_pipes[-1] + 1 :].strip():
        cells = cells[:-1]
    return cells


def is_outer_pipe_table_row(line: str, line_start: int, pipes: list[int]) -> bool:
    if len(pipes) < 2:
        return False
    local_pipes = [position - line_start for position in pipes]
    return (
        not line[: local_pipes[0]].strip()
        and not line[local_pipes[-1] + 1 :].strip()
        and any(table_cells(line, line_start, pipes))
    )


def is_table_delimiter_row(line: str, line_start: int, pipes: list[int]) -> bool:
    cells = table_cells(line, line_start, pipes)
    return len(cells) >= 2 and all(
        TABLE_DELIMITER_CELL_RE.fullmatch(cell) is not None for cell in cells
    )


def markdown_table_pipe_positions(response: str) -> list[int]:
    lines: list[dict[str, Any]] = []
    fence_character: str | None = None
    fence_length = 0
    fence_container_indent = 0
    offset = 0
    for raw_line in response.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        container_content, container_indent = markdown_container_content(line)
        fence = FENCE_RE.match(container_content)
        if fence_character is not None:
            closing_fence = fence
            if (
                closing_fence is None
                and fence_container_indent
                and len(line) >= fence_container_indent
                and not line[:fence_container_indent].strip()
            ):
                closing_fence = FENCE_RE.match(line[fence_container_indent:])
            if closing_fence is not None:
                marker = closing_fence.group("marker")
                if (
                    marker[0] == fence_character
                    and len(marker) >= fence_length
                    and not closing_fence.group("rest").strip()
                ):
                    fence_character = None
                    fence_length = 0
                    fence_container_indent = 0
            block_code = True
        elif fence is not None and not (
            fence.group("marker")[0] == "`" and "`" in fence.group("rest")
        ):
            marker = fence.group("marker")
            fence_character = marker[0]
            fence_length = len(marker)
            fence_container_indent = container_indent
            block_code = True
        else:
            block_code = is_indented_code_line(line)
        lines.append(
            {
                "line": line,
                "start": offset,
                "end": offset + len(raw_line),
                "block_code": block_code,
                "pipes": [],
                "table": False,
            }
        )
        offset += len(raw_line)

    code_ranges = inline_code_ranges(response, lines)
    for item in lines:
        if not item["block_code"]:
            item["pipes"] = noncode_pipe_positions(
                item["line"], item["start"], code_ranges
            )

    for item in lines:
        item["table"] = is_outer_pipe_table_row(
            item["line"], item["start"], item["pipes"]
        )

    for index, item in enumerate(lines):
        if not is_table_delimiter_row(
            item["line"], item["start"], item["pipes"]
        ):
            continue
        if index == 0 or not lines[index - 1]["pipes"]:
            continue
        item["table"] = True
        lines[index - 1]["table"] = True
        body_index = index + 1
        while body_index < len(lines):
            body = lines[body_index]
            if not body["line"].strip() or not body["pipes"]:
                break
            body["table"] = True
            body_index += 1

    return sorted(
        position
        for item in lines
        if item["table"]
        for position in item["pipes"]
    )


def match_is_negated(response: str, start: int) -> bool:
    table_boundary = max(
        (
            position
            for position in markdown_table_pipe_positions(response)
            if position < start
        ),
        default=-1,
    )
    clause_start = max(
        response.rfind(".", 0, start),
        response.rfind("!", 0, start),
        response.rfind("?", 0, start),
        response.rfind(";", 0, start),
        response.rfind("\n", 0, start),
        table_boundary,
    )
    prefix = response[clause_start + 1 : start]
    words = list(re.finditer(r"[\w']+", prefix))
    if len(words) > 8:
        prefix = prefix[words[-8].start() :]
    return NEGATION_RE.search(prefix) is not None


def has_positive_concept(response: str, concept: str) -> bool:
    return any(
        not match_is_negated(response, match.start())
        for match in concept_pattern(concept).finditer(response)
    )


def score_response(case: dict[str, Any], response: str) -> list[str]:
    failures: list[str] = []
    for group in case["required"]:
        alternatives = [alternative.strip() for alternative in str(group).split("|")]
        if not any(has_positive_concept(response, alternative) for alternative in alternatives):
            failures.append(f"missing required concept: {group}")
    for group in case["forbidden"]:
        alternatives = [alternative.strip() for alternative in str(group).split("|")]
        if any(has_positive_concept(response, alternative) for alternative in alternatives):
            failures.append(f"forbidden claim present: {group}")
    return failures


def command_response(
    command: str,
    prompt: str,
    timeout: int,
    adapter_settings: AdapterSettings | None = None,
) -> str:
    settings = adapter_settings or resolve_adapter_settings(command)
    with tempfile.TemporaryDirectory(prefix="sem-eval-adapter-") as workspace_value:
        workspace = Path(workspace_value)
        workspace.chmod(0o700)
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env=build_adapter_environment(settings, workspace),
        )
        try:
            stdout, stderr = process.communicate(input=prompt, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            if hasattr(os, "killpg"):
                os.killpg(process.pid, signal.SIGKILL)
            else:  # pragma: no cover - Windows fallback
                process.kill()
            process.communicate()
            raise RuntimeError(f"case timed out after {timeout} seconds") from exc
        if process.returncode != 0:
            raise RuntimeError(
                adapter_failure_message(process.returncode, stdout, stderr)
            )
        return stdout


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def command_identity(command: str) -> dict[str, Any]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = []
    executable = next(
        (
            token
            for token in tokens
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token)
        ),
        "",
    )
    identity: dict[str, Any] = {
        "kind": "shell-command",
        "command_sha256": sha256_bytes(command.encode("utf-8")),
    }
    if not executable:
        return identity
    candidate = Path(executable)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(ROOT)
    except (OSError, ValueError):
        return identity
    if resolved.is_file():
        identity["adapter"] = str(resolved.relative_to(ROOT))
        identity["adapter_sha256"] = sha256_bytes(resolved.read_bytes())
        identity["executable"] = resolved.name
    elif "/" not in executable and executable in {
        "bash",
        "claude",
        "codex",
        "python",
        "python3",
        "sh",
    }:
        identity["executable"] = executable
    return identity


def resolve_adapter_settings(command: str) -> AdapterSettings:
    adapter = command_identity(command).get("adapter")
    return resolve_protocol_settings(
        adapter=str(adapter) if adapter is not None else None,
        command=command,
    )


def model_environment(command: str) -> tuple[str | None, str | None]:
    return resolve_adapter_settings(command)


def query_host_cli_version(command: str | None) -> tuple[str | None, str | None]:
    if command is None:
        return None, None
    lowered = command.lower()
    host = "claude" if "claude" in lowered else "codex" if "codex" in lowered else None
    if host is None:
        return None, None
    try:
        completed = subprocess.run(
            [host, "--version"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return host, None
    output = completed.stdout.strip() or completed.stderr.strip()
    version = output.splitlines()[0][:200] if completed.returncode == 0 and output else None
    return host, version


def git_state() -> dict[str, Any]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return {
        "sha": sha.stdout.strip() if sha.returncode == 0 else None,
        "dirty": bool(status.stdout) if status.returncode == 0 else None,
    }


def split_access_context(command_record: dict[str, Any]) -> str:
    if command_record.get("adapter") == "evals/adapters/codex-specialist.sh":
        return (
            "The target model receives the selected specialist and owned templates inline "
            "in an isolated, tool-disabled temporary working directory; required terms, "
            "forbidden claims, and scoring outcomes remain in the evaluator."
        )
    return (
        "The evaluator withholds required terms, forbidden claims, and scoring outcomes "
        "from the command input; command isolation and tool access are not verified."
    )


def build_run_manifest(
    *,
    cases: list[dict[str, Any]],
    catalog_path: Path,
    command: str,
    prompts: dict[str, str] | None = None,
    selection_mode: str = "catalog",
    jobs: int = 1,
    case_timeout: int = 600,
    run_controls: dict[str, Any] | None = None,
    adapter_settings: AdapterSettings | None = None,
) -> dict[str, Any]:
    prompt_sha256 = {
        str(case["id"]): sha256_bytes(
            (
                prompts[str(case["id"])]
                if prompts is not None
                else build_prompt(case)
            ).encode("utf-8")
        )
        for case in cases
    }
    prompt_set = json.dumps(prompt_sha256, sort_keys=True, separators=(",", ":"))
    settings = adapter_settings or resolve_adapter_settings(command)
    model, effort = settings
    host_cli, host_cli_version = query_host_cli_version(command)
    command_record = command_identity(command)
    return {
        "type": "manifest",
        "schema_version": 3,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "live",
        "catalog": (
            str(catalog_path.resolve().relative_to(ROOT))
            if catalog_path.resolve().is_relative_to(ROOT)
            else "external-catalog"
        ),
        "seed": None,
        "selected_case_ids": list(prompt_sha256),
        "prompt_sha256": prompt_sha256,
        "prompt_set_sha256": sha256_bytes(prompt_set.encode("utf-8")),
        "catalog_sha256": sha256_bytes(catalog_path.read_bytes()),
        "harness_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "adapter_protocol": {
            "path": str(ADAPTER_PROTOCOL_PATH.relative_to(ROOT)),
            "sha256": sha256_bytes(ADAPTER_PROTOCOL_PATH.read_bytes()),
        },
        "command": command_record,
        "model": model,
        "effort": effort,
        "host_cli": host_cli,
        "host_cli_version": host_cli_version,
        "run_controls": run_controls or {
            "selection_mode": selection_mode,
            "jobs": jobs,
            "case_timeout": case_timeout,
        },
        "git": git_state(),
        "scoring_mode": "lexical_smoke",
        "split_access_context": split_access_context(command_record),
        "evidence": {
            "manifest": "manifest.json",
            "results": "results.jsonl",
            "response_path_pattern": "{case_id}.txt",
            "response_digest": "sha256",
        },
    }


def reserve_exclusive_file(
    directory_descriptor: int,
    name: str,
    display_path: Path,
    description: str,
) -> int:
    try:
        return open_exclusive_file_at(directory_descriptor, name, mode=0o600)
    except FileExistsError:
        fail(f"refusing to overwrite {description} {display_path}")
    except (OSError, ValueError) as exc:
        fail(f"cannot reserve {description} {display_path}: {exc}")
    raise AssertionError("fail() must exit")


def specialist_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "scoring_mode": "lexical_smoke",
        "passed": sum(1 for result in results if result["passed"]),
        "total": len(results),
        "failures": [
            {key: result[key] for key in ("id", "specialist", "failures")}
            for result in results
            if not result["passed"]
        ],
    }


class SpecialistRunWriter:
    def __init__(
        self,
        results_dir: Path,
        total: int,
        manifest: dict[str, Any],
    ) -> None:
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            fail(f"invalid result total {total!r}")
        selected_case_ids = manifest.get("selected_case_ids")
        if selected_case_ids is not None:
            if not isinstance(selected_case_ids, list) or not all(
                isinstance(case_id, str) and SAFE_SLUG_RE.fullmatch(case_id)
                for case_id in selected_case_ids
            ):
                fail("manifest selected_case_ids must contain safe case IDs")
            if len(selected_case_ids) != len(set(selected_case_ids)):
                fail("manifest selected_case_ids must be unique")
            if len(selected_case_ids) != total:
                fail(
                    "manifest selected_case_ids count does not match result total"
                )

        self.results_dir = results_dir
        self.total = total
        self.expected_case_ids = (
            set(selected_case_ids) if selected_case_ids is not None else None
        )
        self.seen: set[str] = set()
        self.failed_case_ids: set[str] = set()
        self.completed = 0
        self.passed = 0
        self.failed = 0
        self.summary_written = False
        self._handle = None
        self._directory_descriptor: int | None = None
        try:
            self._directory_descriptor = reserve_run_directory(
                results_dir, mode=0o700
            )
        except FileExistsError:
            fail(f"refusing to reuse results directory {results_dir}")
        except (OSError, ValueError) as exc:
            fail(f"cannot reserve results directory {results_dir}: {exc}")

        try:
            manifest_descriptor = reserve_exclusive_file(
                self._directory_descriptor,
                "manifest.json",
                results_dir / "manifest.json",
                "manifest",
            )
            try:
                with os.fdopen(
                    manifest_descriptor, "w", encoding="utf-8", newline="\n"
                ) as handle:
                    json.dump(manifest, handle, indent=2, sort_keys=True)
                    handle.write("\n")
            except OSError as exc:
                fail(f"cannot write manifest under {results_dir}: {exc}")

            results_descriptor = reserve_exclusive_file(
                self._directory_descriptor,
                "results.jsonl",
                results_dir / "results.jsonl",
                "results JSONL",
            )
            self._handle = os.fdopen(
                results_descriptor, "w", encoding="utf-8", newline="\n"
            )
            self._append(manifest)
        except BaseException:
            self.close()
            raise

    def write_result(self, result: dict[str, Any]) -> None:
        if self.summary_written:
            fail("cannot write a case after the final summary")
        case_id = result.get("id")
        if not isinstance(case_id, str) or not SAFE_SLUG_RE.fullmatch(case_id):
            fail(f"unsafe result id {case_id!r}")
        if self.expected_case_ids is not None and case_id not in self.expected_case_ids:
            fail(f"result id {case_id!r} was not selected in the manifest")
        if case_id in self.seen:
            fail(f"duplicate result id {case_id!r}")
        specialist = result.get("specialist")
        if not isinstance(specialist, str) or not SAFE_SLUG_RE.fullmatch(specialist):
            fail(f"unsafe result specialist {specialist!r}")
        passed = result.get("passed")
        if not isinstance(passed, bool):
            fail(f"result {case_id!r} passed must be boolean")
        failures = result.get("failures")
        if not isinstance(failures, list) or not all(
            isinstance(failure, str) for failure in failures
        ):
            fail(f"result {case_id!r} failures must be strings")
        response = result.get("response")
        if not isinstance(response, str):
            fail(f"result {case_id!r} response must be text")

        response_bytes = response.encode("utf-8")
        path = self.results_dir / f"{case_id}.txt"
        if self._directory_descriptor is None:
            fail("cannot write a result after closing the run directory")
        descriptor = reserve_exclusive_file(
            self._directory_descriptor,
            path.name,
            path,
            "result file",
        )
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(response_bytes)
        except OSError as exc:
            fail(f"cannot write result file {path}: {exc}")

        self.seen.add(case_id)
        self.completed += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            self.failed_case_ids.add(case_id)
        self._append(
            {
                "type": "case",
                "case_id": case_id,
                "specialist": specialist,
                "passed": passed,
                "failures": failures,
                "response_path": path.name,
                "response_sha256": sha256_bytes(response_bytes),
                "completed": self.completed,
                "total": self.total,
                "passed_so_far": self.passed,
                "failed_so_far": self.failed,
            }
        )

    def write_summary(self, summary: dict[str, Any]) -> None:
        if self.summary_written:
            fail("refusing to write more than one final summary")
        if self.completed != self.total:
            fail(
                f"cannot finalize incomplete results: {self.completed}/{self.total} cases"
            )
        if self.expected_case_ids is not None and self.seen != self.expected_case_ids:
            fail("cannot finalize results that do not match manifest case IDs")
        if not isinstance(summary, dict):
            fail("final summary must be an object")
        if summary.get("total") != self.total or summary.get("passed") != self.passed:
            fail("final summary counts do not match scored case records")
        summary_failures = summary.get("failures")
        if not isinstance(summary_failures, list) or not all(
            isinstance(failure, dict)
            and isinstance(failure.get("id"), str)
            for failure in summary_failures
        ):
            fail("final summary failures must identify failed cases")
        if (
            len(summary_failures) != self.failed
            or {failure["id"] for failure in summary_failures}
            != self.failed_case_ids
        ):
            fail("final summary failures do not match scored case records")
        self._append(
            {
                "type": "summary",
                "completed": self.completed,
                "total": self.total,
                "passed_so_far": self.passed,
                "failed_so_far": self.failed,
                "summary": summary,
            }
        )
        self.summary_written = True

    def _append(self, record: dict[str, Any]) -> None:
        if self._handle is None or self._handle.closed:
            fail("cannot append to a closed results JSONL")
        self._handle.write(json.dumps(record, sort_keys=True) + "\n")
        self._handle.flush()

    def close(self) -> None:
        if self._handle is not None and not self._handle.closed:
            self._handle.close()
        if self._directory_descriptor is not None:
            os.close(self._directory_descriptor)
            self._directory_descriptor = None


def write_results(
    results_dir: Path,
    results: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    writer = SpecialistRunWriter(results_dir, len(results), manifest)
    try:
        for result in results:
            writer.write_result(result)
        writer.write_summary(specialist_summary(results))
    finally:
        writer.close()


def run_case(
    case: dict[str, Any],
    command: str,
    timeout: int,
    prompt: str | None = None,
    adapter_settings: AdapterSettings | None = None,
) -> dict[str, Any]:
    try:
        response = command_response(
            command,
            prompt if prompt is not None else build_prompt(case),
            timeout,
            adapter_settings=adapter_settings,
        )
        failures = score_response(case, response)
    except RuntimeError as exc:
        response = ""
        failures = [f"command failed: {exc}"]
    return {
        "id": case["id"],
        "specialist": case["specialist"],
        "passed": not failures,
        "failures": failures,
        "response": response,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run lexical-smoke specialist behavior evals."
    )
    parser.add_argument("--catalog", default=str(CATALOG))
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--case-timeout", type=int, default=600)
    parser.add_argument("--command", required=True)
    parser.add_argument("--results-dir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.case_timeout < 1:
        parser.error("--jobs and --case-timeout must be positive")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    catalog_path = Path(args.catalog)
    cases = load_cases(catalog_path)
    if args.case_id:
        if len(args.case_id) != len(set(args.case_id)):
            fail("duplicate --case-id values")
        requested = set(args.case_id)
        cases = [case for case in cases if case["id"] in requested]
        missing = requested - {case["id"] for case in cases}
        if missing:
            fail(f"unknown case ids: {', '.join(sorted(missing))}")
    if args.limit is not None:
        cases = cases[: args.limit]
    if not cases:
        fail("no cases selected")

    prompts = {str(case["id"]): build_prompt(case) for case in cases}
    adapter_settings = resolve_adapter_settings(args.command)
    selection_mode = (
        "case_ids"
        if args.case_id
        else "limit"
        if args.limit is not None
        else "catalog"
    )
    manifest = (
        build_run_manifest(
            cases=cases,
            catalog_path=catalog_path,
            command=args.command,
            prompts=prompts,
            selection_mode=selection_mode,
            jobs=args.jobs,
            case_timeout=args.case_timeout,
            adapter_settings=adapter_settings,
            run_controls={
                "selection_mode": selection_mode,
                "catalog": (
                    str(catalog_path.resolve().relative_to(ROOT))
                    if catalog_path.resolve().is_relative_to(ROOT)
                    else "external-catalog"
                ),
                "requested_case_ids": list(args.case_id),
                "limit": args.limit,
                "jobs": args.jobs,
                "case_timeout": args.case_timeout,
                "summary_format": "json" if args.json else "text",
                "evidence_sink": "run_directory",
            },
        )
        if args.results_dir
        else None
    )
    writer = (
        SpecialistRunWriter(Path(args.results_dir), len(cases), manifest)
        if args.results_dir and manifest is not None
        else None
    )

    results: list[dict[str, Any] | None] = [None] * len(cases)
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    run_case,
                    case,
                    args.command,
                    args.case_timeout,
                    prompts[str(case["id"])],
                    adapter_settings,
                ): index
                for index, case in enumerate(cases)
            }
            for future in as_completed(futures):
                result = future.result()
                results[futures[future]] = result
                if writer is not None:
                    writer.write_result(result)
        complete = [result for result in results if result is not None]
        summary = specialist_summary(complete)
        if writer is not None:
            writer.write_summary(summary)
    finally:
        if writer is not None:
            writer.close()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"specialist lexical smoke: {summary['passed']}/{summary['total']} cases passed"
        )
        for result in summary["failures"]:
            print(f"{result['id']} ({result['specialist']}):")
            for failure in result["failures"]:
                print(f"  - {failure}")
    return 0 if not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
