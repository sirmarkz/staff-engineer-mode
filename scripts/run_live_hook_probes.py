#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import signal
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
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


@dataclass
class CodexProbeEnvironment:
    env: dict[str, str]
    root: Path
    sensitive_values: tuple[str, ...] = ()


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        if os.name == "posix":
            # A child may keep inherited pipes open after the session leader
            # exits, so kill the process group even when poll() reports the
            # direct process has already finished.
            os.killpg(process.pid, signal.SIGKILL)
        elif process.poll() is None:
            process.kill()
    except ProcessLookupError:
        pass


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
    process = subprocess.Popen(
        args,
        cwd=cwd,
        env=process_env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name == "posix",
    )
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_process_group(process)
        stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(
            args,
            timeout,
            output=stdout,
            stderr=stderr,
        ) from None
    except BaseException:
        terminate_process_group(process)
        process.communicate()
        raise
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def git(repo: Path, *args: str) -> str:
    completed = run(["git", *args], cwd=repo, timeout=30)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    return completed.stdout


def make_repo(root: Path, event: str) -> Path:
    root = root.expanduser().resolve()
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
        "Do not retry, repair, or run fallback commands. "
        "Run one shell tool call at a time, wait for its result before starting the next, "
        "and never issue duplicate or parallel shell tool calls.\n"
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


def codex_agent_message_block_command(text: str) -> str | None:
    lowered = text.lower()
    if "blocked" not in lowered or "command" not in lowered:
        return None
    match = re.search(r"```(?:bash|sh)?\s*\n(?P<command>.*?)\n```", text, re.DOTALL)
    if match is None:
        return None
    for line in match.group("command").splitlines():
        command = line.strip()
        if command:
            return command
    return None


def unwrap_shell_command(command: str) -> str:
    try:
        argv = shlex.split(command)
    except ValueError:
        return command
    if len(argv) >= 3 and Path(argv[0]).name in {"bash", "sh"} and argv[1] in {"-lc", "-c"}:
        return argv[2]
    return command


def command_attempts_from_log(text: str) -> list[CommandAttempt]:
    by_item_id: dict[str, CommandAttempt] = {}
    order: list[str] = []
    has_sem_marker = '"sem_hook_probe_denials"' in text
    native_denial_commands: set[str] = set()

    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        for denial in value.get("permission_denials", []):
            if not isinstance(denial, dict):
                continue
            tool_input = denial.get("tool_input")
            command = tool_input.get("command") if isinstance(tool_input, dict) else None
            if isinstance(command, str):
                native_denial_commands.add(unwrap_shell_command(command))

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
            for key in ("permission_denials", "sem_hook_probe_denials"):
                for denial in value.get(key, []):
                    if not isinstance(denial, dict):
                        continue
                    tool_input = denial.get("tool_input")
                    command = tool_input.get("command") if isinstance(tool_input, dict) else None
                    if not isinstance(command, str) or not isinstance(denial.get("tool_use_id"), str):
                        continue
                    if key == "sem_hook_probe_denials" and unwrap_shell_command(command) in native_denial_commands:
                        continue
                    ensure_attempt(denial["tool_use_id"], command)
                    mark_failed(denial["tool_use_id"], blocked=True)
            item = value.get("item")
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                if not has_sem_marker and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                    blocked_command = codex_agent_message_block_command(item["text"])
                    if blocked_command is not None:
                        ensure_attempt(item["id"], blocked_command)
                        mark_failed(item["id"], blocked=True)
                        continue
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


def is_allowed_path_arg(arg: str, allowed_paths: list[str]) -> bool:
    return any(arg == path or arg.endswith(f"/{path}") for path in allowed_paths)


def split_shell_prelude(command: str) -> list[str]:
    return [part.strip() for part in re.split(r"\s*(?:&&|;)\s*", command) if part.strip()]


def strip_safe_redirects(argv: list[str]) -> list[str] | None:
    stripped: list[str] = []
    for arg in argv:
        if ">" in arg or "<" in arg:
            if arg != "2>&1":
                return None
            continue
        stripped.append(arg)
    return stripped


def is_allowed_ls_option(arg: str) -> bool:
    return bool(re.fullmatch(r"-[adhl]+", arg))


def is_allowed_sem_file_read(argv: list[str], allowed_paths: list[str]) -> bool:
    if not argv:
        return False
    tool = Path(argv[0]).name
    if tool == "echo":
        return len(argv) == 1 or (len(argv) == 2 and argv[1] == "---")
    if tool == "cat":
        return len(argv) >= 2 and all(is_allowed_path_arg(arg, allowed_paths) for arg in argv[1:])
    if tool == "sed":
        return (
            len(argv) >= 4
            and argv[1] == "-n"
            and re.fullmatch(r"\d+(?:,(?:\d+|\$))?p", argv[2]) is not None
            and all(is_allowed_path_arg(arg, allowed_paths) for arg in argv[3:])
        )
    if tool == "wc":
        return (
            len(argv) >= 3
            and argv[1] == "-l"
            and all(is_allowed_path_arg(arg, allowed_paths) for arg in argv[2:])
        )
    if tool == "ls":
        options = [arg for arg in argv[1:] if arg.startswith("-")]
        paths = [arg for arg in argv[1:] if not arg.startswith("-")]
        return (
            bool(paths)
            and all(is_allowed_ls_option(arg) for arg in options)
            and all(is_allowed_path_arg(arg, allowed_paths) for arg in paths)
        )
    return False


def is_allowed_sem_prelude(command: str, probe: Probe) -> bool:
    command = unwrap_shell_command(command)
    syntax_check = command.replace("1,$p", "")
    if any(marker in syntax_check for marker in ("|", "`", "$", "<", "\n", "{", "}", "*", "?", "~", "[", "]")):
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
    parts = split_shell_prelude(command)
    if not parts:
        return False
    for part in parts:
        try:
            argv = shlex.split(part)
        except ValueError:
            return False
        argv = strip_safe_redirects(argv)
        if argv is None or not is_allowed_sem_file_read(argv, allowed_paths):
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
        "ERROR codex_core::tools::router",
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


def has_expected_block_reason(text: str, event: str) -> bool:
    exact = f"Do not combine the ack command with the {event} command"
    if exact in text:
        return True
    lowered = text.lower()
    return (
        "hook" in lowered
        and "block" in lowered
        and "ack" in lowered
        and event in lowered
        and "combined" in lowered
        and "separate shell command" in lowered
    )


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

    if probe.probe == "block":
        if not relevant_attempts or not relevant_attempts[0].failed:
            return False, "block probe did not produce a failed or blocked command attempt"
        if not relevant_attempts[0].blocked:
            return False, "block probe reached shell instead of a host hook denial"
        if not has_expected_block_reason(text, probe.event):
            return False, f"missing expected block reason for {probe.event}"
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


def hook_probe_marker(repo: Path) -> Path:
    return repo / ".git" / "staff-engineer-mode" / "live-hook-probe-blocks.jsonl"


def marker_denial_log(repo: Path) -> str:
    marker = hook_probe_marker(repo)
    if not marker.exists():
        return ""
    denials: list[dict[str, object]] = []
    for index, line in enumerate(marker.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        command = entry.get("command")
        reason = entry.get("reason")
        if isinstance(command, str) and isinstance(reason, str):
            denials.append(
                {
                    "tool_use_id": f"sem_hook_probe_{index}",
                    "tool_input": {"command": command},
                    "reason": reason,
                }
            )
    if not denials:
        return ""
    return json.dumps({"sem_hook_probe_denials": denials})


def codex_env(repo: Path | None = None, base: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(base or {})
    existing = env.get("RUST_LOG", os.environ.get("RUST_LOG", ""))
    router_filter = "codex_core::tools::router=off"
    if "codex_core::tools::router" in existing:
        env["RUST_LOG"] = existing
    elif existing:
        env["RUST_LOG"] = f"{existing},{router_filter}"
    else:
        env["RUST_LOG"] = router_filter
    if repo is not None:
        env["SEM_HOOK_PROBE_MARKER"] = str(hook_probe_marker(repo))
    return env


def write_codex_local_marketplace(marketplace_root: Path) -> None:
    plugin_root = marketplace_root / "plugins" / "staff-engineer-mode"
    manifest_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    plugin_root.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if plugin_root.exists() or plugin_root.is_symlink():
        if plugin_root.is_symlink() or plugin_root.is_file():
            plugin_root.unlink()
        else:
            shutil.rmtree(plugin_root)
    try:
        os.symlink(ROOT, plugin_root, target_is_directory=True)
    except OSError:
        shutil.copytree(
            ROOT,
            plugin_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".mypy_cache"),
        )

    manifest = {
        "name": "staff-engineer-mode",
        "plugins": [
            {
                "name": "staff-engineer-mode",
                "description": "Staff Engineer Mode local live probe plugin",
                "version": "0.0.0-local-probe",
                "source": {"source": "local", "path": "./plugins/staff-engineer-mode"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Coding",
            }
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def source_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def codex_probe_root(work_root: Path) -> Path:
    parent = source_codex_home() / ".tmp"
    try:
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="sem-live-hook-probes-codex.", dir=parent))
    except OSError:
        return Path(tempfile.mkdtemp(prefix="codex-home.", dir=work_root))


def app_server_request(
    method: str,
    params: dict[str, object],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> dict[str, object]:
    process_env = os.environ.copy()
    process_env.update(env)
    process = subprocess.Popen(
        ["codex", "app-server", "--stdio"],
        cwd=cwd,
        env=process_env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name == "posix",
    )
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None
    lines: queue.Queue[tuple[str, str]] = queue.Queue()

    def read_stream(name: str, stream: Any) -> None:
        for line in stream:
            lines.put((name, line))

    stdout_thread = threading.Thread(target=read_stream, args=("stdout", process.stdout), daemon=True)
    stderr_thread = threading.Thread(target=read_stream, args=("stderr", process.stderr), daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    request_id = f"request-{time.monotonic_ns()}"
    init_id = f"init-{time.monotonic_ns()}"
    stderr_lines: list[str] = []
    stdout_lines: list[str] = []

    def send(message: dict[str, object]) -> None:
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    sent_request = False
    deadline = time.monotonic() + timeout
    try:
        send(
            {
                "id": init_id,
                "method": "initialize",
                "params": {
                    "clientInfo": {
                        "name": "sem-live-hook-probes",
                        "title": "SEM Live Hook Probes",
                        "version": "0",
                    },
                    "capabilities": {
                        "experimentalApi": True,
                        "requestAttestation": False,
                        "optOutNotificationMethods": [],
                    },
                },
            }
        )
        while time.monotonic() < deadline:
            try:
                stream_name, line = lines.get(timeout=0.1)
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if stream_name == "stderr":
                stderr_lines.append(line)
                continue
            stdout_lines.append(line)
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") == init_id:
                send({"method": "initialized"})
                send({"id": request_id, "method": method, "params": params})
                sent_request = True
                continue
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(f"codex app-server {method} failed: {message['error']}")
            result = message.get("result")
            if isinstance(result, dict):
                return result
            raise RuntimeError(f"codex app-server {method} returned invalid result")
        detail = "".join(stderr_lines[-5:] + stdout_lines[-5:])
        state = "before request" if not sent_request else "waiting for response"
        raise RuntimeError(f"timed out {state} from codex app-server {method}: {detail}")
    finally:
        try:
            process.stdin.close()
        except OSError:
            pass
        terminate_process_group(process)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        process.stdout.close()
        process.stderr.close()


def codex_plugin_hooks(env: dict[str, str], *, cwd: Path, timeout: int) -> list[dict[str, object]]:
    result = app_server_request("hooks/list", {"cwds": [str(cwd)]}, cwd=cwd, env=env, timeout=timeout)
    hooks: list[dict[str, object]] = []
    for entry in result.get("data", []):
        if not isinstance(entry, dict):
            continue
        for hook in entry.get("hooks", []):
            if isinstance(hook, dict):
                hooks.append(hook)
    return hooks


def append_codex_hook_trust(config_path: Path, hooks: list[dict[str, object]]) -> list[str]:
    trusted_keys: list[str] = []
    lines = ["", "[hooks.state]"]
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    if "[hooks.state]" in existing:
        lines = [""]
    for hook in hooks:
        key = hook.get("key")
        current_hash = hook.get("currentHash")
        if (
            hook.get("source") != "plugin"
            or hook.get("pluginId") != "staff-engineer-mode@staff-engineer-mode"
            or not isinstance(key, str)
            or not isinstance(current_hash, str)
            or not current_hash.startswith("sha256:")
        ):
            continue
        section = f"[hooks.state.{json.dumps(key)}]"
        if section in existing:
            continue
        lines.extend([section, f"trusted_hash = {json.dumps(current_hash)}", ""])
        trusted_keys.append(key)
    if trusted_keys:
        with config_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines).rstrip() + "\n")
    return trusted_keys


def checked_run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    label: str,
) -> subprocess.CompletedProcess[str]:
    completed = run(command, cwd=cwd, env=env, timeout=timeout)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise RuntimeError(f"{label} failed: {detail}")
    return completed


def auth_sensitive_values(value: object) -> tuple[str, ...]:
    values: set[str] = set()

    def collect(current: object) -> None:
        if isinstance(current, str):
            if current:
                values.add(current)
        elif isinstance(current, dict):
            for child in current.values():
                collect(child)
        elif isinstance(current, list):
            for child in current:
                collect(child)

    collect(value)
    return tuple(sorted(values, key=lambda item: (-len(item), item)))


def redact_sensitive_text(text: str, sensitive_values: tuple[str, ...]) -> str:
    for value in sensitive_values:
        if value:
            text = text.replace(value, "[REDACTED]")
    return text


def remove_probe_root_without_following(root: Path) -> None:
    if not os.path.lexists(root):
        return
    if root.is_symlink() or not root.is_dir():
        root.unlink()
    else:
        shutil.rmtree(root)


def remove_copied_codex_auth(root: Path) -> None:
    """Remove copied Codex credentials without traversing a replaced symlink."""
    if not os.path.lexists(root):
        return
    home = root / "home"
    codex_home = home / ".codex"
    if root.is_symlink() or home.is_symlink() or codex_home.is_symlink():
        remove_probe_root_without_following(root)
        return

    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        root_fd = os.open(root, directory_flags)
        descriptors.append(root_fd)
        home_fd = os.open("home", directory_flags, dir_fd=root_fd)
        descriptors.append(home_fd)
        codex_fd = os.open(".codex", directory_flags, dir_fd=home_fd)
        descriptors.append(codex_fd)
        try:
            os.unlink("auth.json", dir_fd=codex_fd)
        except FileNotFoundError:
            return
    except FileNotFoundError:
        return
    except OSError as exc:
        # Diagnostics are expendable; a copied credential is not. If direct
        # removal fails, remove the entire probe home rather than retain it.
        remove_probe_root_without_following(root)
        if os.path.lexists(root):
            raise RuntimeError(f"could not remove copied Codex credential under: {root}") from exc
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def prepare_codex_probe_environment(work_root: Path, *, timeout: int) -> CodexProbeEnvironment:
    root = codex_probe_root(work_root)
    user_home = root / "home"
    codex_home = user_home / ".codex"
    marketplace_root = root / "marketplace"
    sensitive_values: tuple[str, ...] = ()
    try:
        codex_home.mkdir(parents=True, exist_ok=True)
        auth = source_codex_home() / "auth.json"
        if auth.exists():
            try:
                auth_data = json.loads(auth.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"could not safely read Codex auth data from {auth}") from exc
            sensitive_values = auth_sensitive_values(auth_data)
            shutil.copy2(auth, codex_home / "auth.json")
        fallback_install = codex_home / "staff-engineer-mode"
        try:
            os.symlink(ROOT, fallback_install, target_is_directory=True)
        except OSError:
            if not fallback_install.exists():
                shutil.copytree(
                    ROOT,
                    fallback_install,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".mypy_cache"),
                )

        write_codex_local_marketplace(marketplace_root)
        env = {"HOME": str(user_home), "CODEX_HOME": str(codex_home)}
        checked_run(
            ["codex", "plugin", "marketplace", "add", str(marketplace_root)],
            cwd=ROOT,
            env=env,
            timeout=timeout,
            label="codex local marketplace setup",
        )
        checked_run(
            ["codex", "plugin", "add", "staff-engineer-mode@staff-engineer-mode"],
            cwd=ROOT,
            env=env,
            timeout=timeout,
            label="codex local plugin install",
        )
        hooks = codex_plugin_hooks(env, cwd=ROOT, timeout=timeout)
        trusted = append_codex_hook_trust(codex_home / "config.toml", hooks)
        if not any("pre_tool_use" in key for key in trusted):
            raise RuntimeError("codex local plugin install did not expose a trusted PreToolUse hook")
        return CodexProbeEnvironment(env=env, root=root, sensitive_values=sensitive_values)
    except BaseException as exc:
        remove_copied_codex_auth(root)
        if isinstance(exc, Exception) and sensitive_values:
            sanitized = redact_sensitive_text(str(exc), sensitive_values)
            if sanitized != str(exc):
                raise RuntimeError(sanitized) from None
        raise


def run_codex(
    probe: Probe,
    repo: Path,
    prompt: str,
    args: argparse.Namespace,
    codex_base_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        "codex",
        "exec",
        "--json",
        "--dangerously-bypass-approvals-and-sandbox",
        "--enable",
        "hooks",
        "-C",
        str(repo),
    ]
    if probe.model:
        command.extend(["--model", probe.model])
    if probe.effort:
        command.extend(["--config", f"model_reasoning_effort={probe.effort!r}"])
    command.append(prompt)
    return run(command, cwd=repo, env=codex_env(repo, codex_base_env), timeout=args.timeout)


def run_probe(
    probe: Probe,
    args: argparse.Namespace,
    work_root: Path,
    codex_base_env: dict[str, str] | None = None,
    sensitive_values: tuple[str, ...] = (),
) -> ProbeResult:
    probe_root = work_root / probe.name.replace(":", "-").replace(".", "_")
    probe_root.mkdir(parents=True, exist_ok=True)
    repo = make_repo(probe_root, probe.event)
    commands = shell_for_probe(repo, probe.event, probe.probe)
    prompt = prompt_for(commands, probe, repo)
    log_path = probe_root / f"{probe.host}.log"

    try:
        if probe.host == "claude":
            completed = run_claude(probe, repo, prompt, args)
        else:
            completed = run_codex(probe, repo, prompt, args, codex_base_env)
    except subprocess.TimeoutExpired as exc:
        def timeout_text(value: str | bytes | None) -> str:
            if value is None:
                return ""
            if isinstance(value, bytes):
                return value.decode("utf-8", errors="replace")
            return value

        text = timeout_text(exc.stdout) + timeout_text(exc.stderr)
        marker_log = marker_denial_log(repo)
        if marker_log:
            text = f"{text}\n{marker_log}\n"
        log_path.write_text(
            redact_sensitive_text(text, sensitive_values),
            encoding="utf-8",
        )
        return ProbeResult(probe, False, f"host timed out after {exc.timeout} seconds", log_path)

    text = completed.stdout + completed.stderr
    marker_log = marker_denial_log(repo)
    if marker_log:
        text = f"{text}\n{marker_log}\n"
    text = redact_sensitive_text(text, sensitive_values)
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
            "Defaults: Claude Opus 4.8 and Codex gpt-5.6-terra at high effort."
        ),
    )
    parser.add_argument("--host", choices=("all", "claude", "codex"), default="all")
    parser.add_argument("--event", choices=("all", "commit", "release"), default="all")
    parser.add_argument("--probe", choices=("all", "block", "allow"), default="all")
    parser.add_argument("--claude-model", default="claude-opus-4-8")
    parser.add_argument("--claude-effort", default="high")
    parser.add_argument("--codex-model", default="gpt-5.6-terra")
    parser.add_argument("--codex-effort", default="high")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--work-dir", type=Path, default=None)
    parser.add_argument("--keep-temp", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.timeout < 1:
        print("--timeout must be positive", file=sys.stderr)
        return 2
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
        work_root = args.work_dir.expanduser().resolve()
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

    codex_probe_env: CodexProbeEnvironment | None = None
    failed = True
    try:
        if any(probe.host == "codex" for probe in probes):
            codex_probe_env = prepare_codex_probe_environment(work_root, timeout=args.timeout)

        print(f"live hook probe work dir: {work_root}")
        results = [
            run_probe(
                probe,
                args,
                work_root,
                codex_probe_env.env if codex_probe_env is not None and probe.host == "codex" else None,
                codex_probe_env.sensitive_values
                if codex_probe_env is not None and probe.host == "codex"
                else (),
            )
            for probe in probes
        ]

        failed = False
        for result in results:
            status = "PASS" if result.ok else "FAIL"
            print(f"{status} {result.probe.name}: {result.details} (log: {result.log_path})")
            failed = failed or not result.ok

        return 1 if failed else 0
    finally:
        keep_artifacts = args.keep_temp or failed
        if codex_probe_env is not None:
            remove_copied_codex_auth(codex_probe_env.root)
            if keep_artifacts and codex_probe_env.root.exists():
                print(f"kept codex probe home: {codex_probe_env.root}")
            elif not keep_artifacts:
                shutil.rmtree(codex_probe_env.root, ignore_errors=True)

        if remove_work_root and keep_artifacts:
            print(f"kept probe work dir: {work_root}")
        elif remove_work_root:
            shutil.rmtree(work_root)


if __name__ == "__main__":
    raise SystemExit(main())
