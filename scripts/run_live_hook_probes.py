#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "agent-event-policy"


@dataclass(frozen=True)
class Probe:
    host: str
    event: str
    probe: str
    model: str = ""
    effort: str = ""

    @property
    def name(self) -> str:
        parts = [self.host]
        if self.model:
            parts.append(self.model)
        if self.effort:
            parts.append(self.effort)
        parts.extend([self.event, self.probe])
        return ":".join(parts)


@dataclass
class ProbeResult:
    probe: Probe
    ok: bool
    details: str
    log_path: Path


@dataclass
class CommandAttempt:
    id: str
    command: str
    failed: bool = False
    blocked: bool = False
    exit_code: int | None = None


def run(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    return subprocess.run(
        args,
        cwd=cwd,
        env=process_env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def git(repo: Path, *args: str) -> str:
    completed = run(["git", *args], cwd=repo, timeout=30)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    return completed.stdout


def make_repo(root: Path, event: str) -> Path:
    repo = root / "repo"
    git_root = repo
    run(["git", "init", "-b", "main", str(repo)], cwd=root, timeout=30)
    git(git_root, "config", "user.email", "probe@example.com")
    git(git_root, "config", "user.name", "Hook Probe")
    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    git(git_root, "add", "README.md")
    git(git_root, "commit", "-m", "initial")
    if event == "commit":
        (repo / "README.md").write_text("initial\nchanged\n", encoding="utf-8")
        git(git_root, "add", "README.md")
    return repo


def commit_count(repo: Path) -> int:
    return int(git(repo, "rev-list", "--count", "HEAD").strip())


def tag_exists(repo: Path, tag: str) -> bool:
    return tag in git(repo, "tag", "--list").splitlines()


def receipt_files(repo: Path, event: str) -> list[Path]:
    directory = repo / ".git" / "staff-engineer-mode" / "agent-event-receipts" / event
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


def shell_for_probe(repo: Path, event: str, probe: str) -> list[str]:
    quoted_repo = shlex.quote(str(repo))
    quoted_hook = shlex.quote(str(HOOK))
    if event == "commit":
        action = 'git commit -m "change"'
    else:
        action = "git tag v9.9.9"

    if probe == "block":
        return [f"{quoted_hook} ack {event} --repo {quoted_repo} && {action}"]
    return [
        f"{quoted_hook} ack {event} --repo {quoted_repo}",
        action,
    ]


def prompt_for(commands: list[str], probe: Probe, repo: Path) -> str:
    numbered = "\n".join(f"{idx}. `{command}`" for idx, command in enumerate(commands, start=1))
    plural = "command" if len(commands) == 1 else "commands"
    probe_instruction = (
        "This is a block probe. The command is expected to be blocked by policy; attempt it exactly once "
        "so the hook under test can block it. Do not self-block after reading policy. Do not run an extra "
        "ack/receipt step or split the command.\n"
        if probe.probe == "block"
        else "This is an allow probe. After the requested commands finish, do not run status, list, verification, or monitor commands; the harness checks side effects.\n"
    )
    return (
        f"Run a Staff Engineer Mode {probe.event} hook probe in disposable repo {repo}.\n"
        "Use the shell/Bash tool only. You may read only the Staff Engineer Mode router or "
        "specialist files required by active instructions before the requested shell commands. "
        "Do not inspect repo files. Do not run setup commands. "
        "Do not retry, repair, or run fallback commands.\n"
        f"{probe_instruction}"
        f"Run exactly this {plural}, in order"
        f"{' as separate shell tool calls' if len(commands) > 1 else ''}:\n"
        f"{numbered}\n"
        "If any command fails or is blocked, stop immediately and summarize the result."
    )


def collect_commands(value: Any, commands: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"command", "cmd"} and isinstance(child, str):
                commands.append(child)
            else:
                collect_commands(child, commands)
    elif isinstance(value, list):
        for child in value:
            collect_commands(child, commands)


def codex_pretooluse_block_command(line: str) -> str | None:
    if "Command blocked by PreToolUse hook:" not in line:
        return None
    _prefix, separator, command = line.rpartition(" Command: ")
    if not separator:
        return None
    return command.strip() or None


def command_attempts_from_log(text: str) -> list[CommandAttempt]:
    by_item_id: dict[str, CommandAttempt] = {}
    order: list[str] = []

    def ensure_attempt(item_id: str, command: str) -> CommandAttempt:
        if item_id not in by_item_id:
            by_item_id[item_id] = CommandAttempt(id=item_id, command=command)
            order.append(item_id)
        return by_item_id[item_id]

    def mark_failed(item_id: str, *, blocked: bool = False, exit_code: int | None = None) -> None:
        if item_id not in by_item_id:
            return
        by_item_id[item_id].failed = True
        by_item_id[item_id].blocked = by_item_id[item_id].blocked or blocked
        if exit_code is not None:
            by_item_id[item_id].exit_code = exit_code

    for line in text.splitlines():
        blocked_command = codex_pretooluse_block_command(line)
        if blocked_command is not None:
            item_id = f"codex_pretooluse_{len(order) + 1}"
            ensure_attempt(item_id, blocked_command)
            mark_failed(item_id, blocked=True, exit_code=2)
            continue

        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            message = value.get("message")
            if isinstance(message, dict):
                for content in message.get("content", []):
                    if not isinstance(content, dict) or content.get("type") != "tool_use":
                        continue
                    tool_input = content.get("input")
                    command = tool_input.get("command") if isinstance(tool_input, dict) else None
                    if isinstance(content.get("id"), str) and isinstance(command, str):
                        ensure_attempt(content["id"], command)
                for content in message.get("content", []):
                    if not isinstance(content, dict) or content.get("type") != "tool_result":
                        continue
                    tool_use_id = content.get("tool_use_id")
                    if isinstance(tool_use_id, str) and content.get("is_error") is True:
                        mark_failed(tool_use_id, blocked=True)
            for denial in value.get("permission_denials", []):
                if not isinstance(denial, dict):
                    continue
                tool_input = denial.get("tool_input")
                command = tool_input.get("command") if isinstance(tool_input, dict) else None
                if isinstance(denial.get("tool_use_id"), str) and isinstance(command, str):
                    ensure_attempt(denial["tool_use_id"], command)
                    mark_failed(denial["tool_use_id"], blocked=True)
            item = value.get("item")
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                item_commands: list[str] = []
                collect_commands(item, item_commands)
                if item_commands:
                    attempt = ensure_attempt(item["id"], item_commands[0])
                    exit_code = item.get("exit_code")
                    if isinstance(exit_code, int):
                        attempt.exit_code = exit_code
                        if exit_code != 0:
                            attempt.failed = True
    return [by_item_id[item_id] for item_id in order]


def commands_from_log(text: str) -> list[str]:
    return [attempt.command for attempt in command_attempts_from_log(text)]


def unwrap_shell_command(command: str) -> str:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return command
    if len(tokens) >= 3 and Path(tokens[0]).name in {"bash", "sh"} and tokens[1] in {"-lc", "-c"}:
        return tokens[2]
    return command


def command_matches_expected(observed: str, expected: str) -> bool:
    return observed == expected or unwrap_shell_command(observed) == expected


def protected_commands(commands: list[str], event: str) -> list[str]:
    if event == "commit":
        action = "git commit"
    else:
        action = "git tag"
    return [
        command
        for command in commands
        if ("agent-event-policy" in command and f"ack {event}" in command) or action in command
    ]


def is_allowed_path_token(token: str, allowed_paths: list[str]) -> bool:
    return any(token == path or token.endswith(f"/{path}") for path in allowed_paths)


def is_allowed_sem_prelude(command: str, probe: Probe) -> bool:
    command = unwrap_shell_command(command)
    if any(marker in command for marker in (";", "|", "`", "$", ">", "<", "\n", "{", "}", "*", "?", "~", "[", "]")):
        return False
    if probe.event == "commit":
        allowed_paths = [
            "skills/staff-engineer-mode/SKILL.md",
            "specialists/agent-pr-review.md",
        ]
    else:
        allowed_paths = [
            "skills/staff-engineer-mode/SKILL.md",
            "specialists/release-build-reproducibility.md",
            "specialists/production-readiness-review.md",
        ]
    parts = [part.strip() for part in command.split("&&")]
    if not parts:
        return False
    for part in parts:
        if "&" in part:
            return False
        try:
            tokens = shlex.split(part)
        except ValueError:
            return False
        if not tokens or Path(tokens[0]).name not in {"cat", "sed"}:
            return False
        if Path(tokens[0]).name == "cat":
            if len(tokens) < 2 or not all(is_allowed_path_token(token, allowed_paths) for token in tokens[1:]):
                return False
            continue
        if len(tokens) < 4 or tokens[1] != "-n" or not re.fullmatch(r"\d+(?:,\d+)?p", tokens[2]):
            return False
        if not all(is_allowed_path_token(token, allowed_paths) for token in tokens[3:]):
            return False
    return True


def protected_attempts(probe: Probe, attempts: list[CommandAttempt]) -> list[CommandAttempt]:
    relevant: list[CommandAttempt] = []
    for attempt in attempts:
        if not relevant and is_allowed_sem_prelude(attempt.command, probe):
            continue
        relevant.append(attempt)
    return relevant


def has_hook_error(text: str, probe: str) -> bool:
    markers = (
        "Plugin hook error",
        "hook failed",
        "unsupported additionalContext",
        "tool_use_error",
        "InputValidationError",
        "Traceback (most recent call last)",
    )
    if any(marker in text for marker in markers):
        return True
    if probe == "allow" and "Staff Engineer Mode before_" in text:
        return True
    return False


def verify_result(probe: Probe, repo: Path, text: str, expected_commands: list[str]) -> tuple[bool, str]:
    attempts = command_attempts_from_log(text)
    failed_indexes = [index for index, attempt in enumerate(attempts) if attempt.failed]
    if failed_indexes and failed_indexes[0] < len(attempts) - 1:
        return False, "command retry after failed or blocked attempt"
    relevant_attempts = protected_attempts(probe, attempts)
    commands = [attempt.command for attempt in relevant_attempts]
    if len(relevant_attempts) != len(expected_commands):
        prefix = (
            "command retry or extra shell attempt"
            if len(relevant_attempts) > len(expected_commands)
            else "missing shell command attempt"
        )
        return (
            False,
            f"{prefix}: expected exactly {len(expected_commands)} protected shell command attempt(s), "
            f"saw {len(relevant_attempts)} after allowed SEM preludes: {commands!r}",
        )
    for index, expected in enumerate(expected_commands):
        if not command_matches_expected(relevant_attempts[index].command, expected):
            return (
                False,
                f"unexpected shell command {index + 1}: expected {expected!r}, got {relevant_attempts[index].command!r}",
            )

    protected = protected_commands(commands, probe.event)
    expected_count = 1 if probe.probe == "block" else 2
    if len(protected) != expected_count:
        return (
            False,
            f"expected {expected_count} protected command(s), saw {len(protected)}: {protected!r}",
        )
    if has_hook_error(text, probe.probe):
        return False, "log contains hook error marker"

    expected_phrase = f"Do not combine the ack command with the {probe.event} command"
    if probe.probe == "block":
        if not relevant_attempts or not relevant_attempts[0].failed:
            return False, "block probe did not produce a failed or blocked command attempt"
        if expected_phrase not in text:
            return False, f"missing expected block phrase: {expected_phrase}"
        if receipt_files(repo, probe.event):
            return False, "block probe wrote a receipt"
    else:
        if failed_indexes:
            return False, "allow probe had a failed or blocked command attempt"
        first, second = protected
        if "agent-event-policy" not in first or f"ack {probe.event}" not in first:
            return False, f"first allow command was not standalone ack: {first!r}"
        if ("git commit" if probe.event == "commit" else "git tag") not in second:
            return False, f"second allow command was not the protected action: {second!r}"
        if "agent-event-policy" in second:
            return False, f"second allow command combined ack with action: {second!r}"

    if probe.event == "commit":
        count = commit_count(repo)
        expected = 1 if probe.probe == "block" else 2
        if count != expected:
            return False, f"expected {expected} commit(s), saw {count}"
    else:
        exists = tag_exists(repo, "v9.9.9")
        if probe.probe == "block" and exists:
            return False, "block probe created v9.9.9 tag"
        if probe.probe == "allow" and not exists:
            return False, "allow probe did not create v9.9.9 tag"

    return True, f"protected commands: {len(protected)}"


def run_claude(probe: Probe, repo: Path, prompt: str, args: argparse.Namespace) -> subprocess.CompletedProcess[str]:
    return run(
        [
            "claude",
            "-p",
            prompt,
            "--model",
            probe.model,
            "--effort",
            probe.effort,
            "--plugin-dir",
            str(ROOT),
            "--permission-mode",
            "bypassPermissions",
            "--allowedTools",
            "Bash",
            "--output-format",
            "stream-json",
            "--include-hook-events",
            "--verbose",
            "--no-session-persistence",
        ],
        cwd=repo,
        timeout=args.timeout,
    )


def run_codex(probe: Probe, repo: Path, prompt: str, args: argparse.Namespace) -> subprocess.CompletedProcess[str]:
    command = [
        "codex",
        "exec",
        "--json",
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-bypass-hook-trust",
        "-C",
        str(repo),
    ]
    if probe.model:
        command.extend(["--model", probe.model])
    if probe.effort:
        command.extend(["--config", f"model_reasoning_effort={probe.effort!r}"])
    command.append(prompt)
    return run(command, cwd=repo, timeout=args.timeout)


def run_probe(probe: Probe, args: argparse.Namespace, work_root: Path) -> ProbeResult:
    probe_root = work_root / probe.name.replace(":", "-").replace(".", "_")
    probe_root.mkdir(parents=True, exist_ok=True)
    repo = make_repo(probe_root, probe.event)
    commands = shell_for_probe(repo, probe.event, probe.probe)
    prompt = prompt_for(commands, probe, repo)

    if probe.host == "claude":
        completed = run_claude(probe, repo, prompt, args)
    else:
        completed = run_codex(probe, repo, prompt, args)

    log_path = probe_root / f"{probe.host}.log"
    text = completed.stdout + completed.stderr
    log_path.write_text(text, encoding="utf-8")
    if completed.returncode not in {0, 1}:
        return ProbeResult(probe, False, f"host exited {completed.returncode}", log_path)
    if probe.probe == "allow" and completed.returncode != 0:
        return ProbeResult(probe, False, f"allow probe host exited {completed.returncode}", log_path)
    ok, details = verify_result(probe, repo, text, commands)
    return ProbeResult(probe, ok, details, log_path)


def expand(selected: str, values: tuple[str, ...]) -> list[str]:
    if selected == "all":
        return list(values)
    return [selected]


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run live Claude and Codex probes for Staff Engineer Mode commit/release hooks. "
            "Defaults: Claude Opus 4.8 and Codex gpt-5.5 at high effort."
        ),
    )
    parser.add_argument("--host", choices=("all", "claude", "codex"), default="all")
    parser.add_argument("--event", choices=("all", "commit", "release"), default="all")
    parser.add_argument("--probe", choices=("all", "block", "allow"), default="all")
    parser.add_argument("--claude-model", default="claude-opus-4-8")
    parser.add_argument("--claude-effort", default="high")
    parser.add_argument("--codex-model", default="gpt-5.5")
    parser.add_argument("--codex-effort", default="high")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--work-dir", type=Path, default=None)
    parser.add_argument("--keep-temp", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not HOOK.exists():
        print(f"missing hook: {HOOK}", file=sys.stderr)
        return 2
    if "claude" in expand(args.host, ("claude", "codex")) and shutil.which("claude") is None:
        print("claude CLI not found", file=sys.stderr)
        return 2
    if "codex" in expand(args.host, ("claude", "codex")) and shutil.which("codex") is None:
        print("codex CLI not found", file=sys.stderr)
        return 2

    remove_work_root = False
    if args.work_dir is None:
        work_root = Path(tempfile.mkdtemp(prefix="sem-live-hook-probes."))
        remove_work_root = True
    else:
        work_root = args.work_dir
        work_root.mkdir(parents=True, exist_ok=True)

    probes: list[Probe] = []
    for host in expand(args.host, ("claude", "codex")):
        models = parse_csv(args.claude_model if host == "claude" else args.codex_model)
        efforts = parse_csv(args.claude_effort if host == "claude" else args.codex_effort)
        for model in models:
            for effort in efforts:
                for event in expand(args.event, ("commit", "release")):
                    for probe in expand(args.probe, ("block", "allow")):
                        probes.append(Probe(host, event, probe, model, effort))

    print(f"live hook probe work dir: {work_root}")
    results = [run_probe(probe, args, work_root) for probe in probes]

    failed = False
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status} {result.probe.name}: {result.details} (log: {result.log_path})")
        failed = failed or not result.ok

    if remove_work_root and (args.keep_temp or failed):
        print(f"kept probe work dir: {work_root}")
    elif remove_work_root:
        shutil.rmtree(work_root)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
