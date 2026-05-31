#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import importlib.util
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "agent-event-policy"
LIVE_PROBES = ROOT / "scripts" / "run_live_hook_probes.py"


def load_live_probes():
    spec = importlib.util.spec_from_file_location("run_live_hook_probes", LIVE_PROBES)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load run_live_hook_probes.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AgentEventPolicyHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.repo, check=True)
        (self.repo / "README.md").write_text("initial\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

    def run_hook(
        self,
        payload: dict[str, object],
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        process_env = os.environ.copy()
        process_env.pop("GH_REPO", None)
        process_env.pop("GH_HOST", None)
        if env is not None:
            process_env.update(env)
        return subprocess.run(
            [str(HOOK), "pretooluse"],
            cwd=cwd or self.repo,
            env=process_env,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def run_hook_without_python(
        self,
        payload: dict[str, object],
        cwd: Path | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as bin_dir:
            path_dir = Path(bin_dir)
            for tool in ("awk", "bash", "cat", "dirname", "git", "grep", "jq", "sha256sum"):
                target = shutil.which(tool)
                if target is None:
                    raise AssertionError(f"required test tool not found: {tool}")
                os.symlink(target, path_dir / tool)
            process_env = os.environ.copy()
            process_env.pop("GH_REPO", None)
            process_env.pop("GH_HOST", None)
            if extra_env is not None:
                process_env.update(extra_env)
            process_env["PATH"] = str(path_dir)
            return subprocess.run(
                [str(HOOK), "pretooluse"],
                cwd=cwd or self.repo,
                env=process_env,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=False,
            )

    def run_hook_without_python_or_jq(
        self,
        payload: dict[str, object],
        cwd: Path | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as bin_dir:
            path_dir = Path(bin_dir)
            for tool in ("awk", "bash", "cat", "dirname", "git", "grep"):
                target = shutil.which(tool)
                if target is None:
                    raise AssertionError(f"required test tool not found: {tool}")
                os.symlink(target, path_dir / tool)
            process_env = os.environ.copy()
            process_env.pop("GH_REPO", None)
            process_env.pop("GH_HOST", None)
            if extra_env is not None:
                process_env.update(extra_env)
            process_env["PATH"] = str(path_dir)
            return subprocess.run(
                [str(HOOK), "pretooluse"],
                cwd=cwd or self.repo,
                env=process_env,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=False,
            )

    def stage_change(self, content: str) -> None:
        (self.repo / "README.md").write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.repo, check=True)

    def modify_unstaged(self, content: str) -> None:
        (self.repo / "README.md").write_text(content, encoding="utf-8")

    def commit_count(self) -> int:
        return int(
            subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.repo,
                text=True,
            ).strip()
        )

    def receipt_files(self, event: str) -> list[Path]:
        receipt_dir = self.repo / ".git" / "staff-engineer-mode" / "agent-event-receipts" / event
        if not receipt_dir.exists():
            return []
        return list(receipt_dir.glob("*.json"))

    def assert_pretooluse_denies(
        self,
        result: subprocess.CompletedProcess[str],
        *expected_phrases: str,
    ) -> dict[str, object]:
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        response = json.loads(result.stdout)
        hook_output = response.get("hookSpecificOutput")
        self.assertIsInstance(hook_output, dict)
        assert isinstance(hook_output, dict)
        self.assertEqual(hook_output.get("hookEventName"), "PreToolUse")
        self.assertEqual(hook_output.get("permissionDecision"), "deny")
        self.assertIsInstance(response.get("systemMessage"), str)
        self.assertEqual(hook_output.get("permissionDecisionReason"), response["systemMessage"])
        for phrase in expected_phrases:
            self.assertIn(phrase, response["systemMessage"])
        return response

    def test_list_protected_documents_explicit_policy_surface(self) -> None:
        result = subprocess.run(
            [str(HOOK), "list-protected"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("git commit", result.stdout)
        self.assertIn("git tag", result.stdout)
        self.assertIn("git push tags", result.stdout)
        self.assertIn("gh release create|edit|upload|delete|delete-asset", result.stdout)
        self.assertNotIn("repo-local scripts", result.stdout)

    def test_commit_command_blocks_without_review_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})

        self.assert_pretooluse_denies(result, "before_commit policy requires agent-pr-review")

    def test_block_response_uses_structured_deny_without_hook_failure(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})

        response = self.assert_pretooluse_denies(result, "before_commit policy requires agent-pr-review")
        self.assertIn("triggered accidentally", response["systemMessage"])
        self.assertIn("ask the user to confirm", response["systemMessage"])
        self.assertNotIn("decision", response)
        self.assertNotIn("reason", response)

    def test_malformed_pretooluse_payload_exits_cleanly(self) -> None:
        result = subprocess.run(
            [str(HOOK), "pretooluse"],
            cwd=self.repo,
            input="{not-json",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_protected_command_outside_repo_exits_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as non_repo:
            result = self.run_hook(
                {"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}},
                cwd=Path(non_repo),
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_block_response_writes_probe_marker_when_requested(self) -> None:
        marker = self.repo / "probe-marker.jsonl"

        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "git tag v1.2.3"}},
            env={"SEM_HOOK_PROBE_MARKER": str(marker)},
        )

        self.assert_pretooluse_denies(result, "before_release policy requires")
        entries = [json.loads(line) for line in marker.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["event"], "pretooluse_block")
        self.assertEqual(entries[0]["command"], "git tag v1.2.3")
        self.assertIn("before_release policy requires", entries[0]["reason"])

    def test_ack_and_commit_same_shell_command_explains_separate_invocation(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"'
                },
            }
        )

        self.assert_pretooluse_denies(
            result,
            "own shell command",
            "Do not combine the ack command with the commit command",
        )

    def test_ack_and_commit_same_shell_command_does_not_make_hook_error_without_host_hook(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    f"cd {shlex.quote(str(self.repo))} && "
                    f"{shlex.quote(str(HOOK))} ack commit --repo {shlex.quote(str(self.repo))} && "
                    'git commit -m "change"'
                ),
            ],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commit_count(), 2)
        self.assertGreater(len(self.receipt_files("commit")), 0)

    def test_standalone_ack_then_commit_succeeds_without_host_hook(self) -> None:
        self.stage_change("initial\nchanged\n")

        ack = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    f"cd {shlex.quote(str(self.repo))} && "
                    f"{shlex.quote(str(HOOK))} ack commit --repo {shlex.quote(str(self.repo))}"
                ),
            ],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)
        self.assertGreater(len(self.receipt_files("commit")), 0)

        commit = subprocess.run(
            ["bash", "-lc", f"cd {shlex.quote(str(self.repo))} && git commit -m change"],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)
        self.assertEqual(self.commit_count(), 2)

    def test_live_probe_rejects_retry_after_block_even_when_later_commit_succeeds(self) -> None:
        live_probes = load_live_probes()
        self.stage_change("initial\nchanged\n")
        commands = [
            f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"',
            f"{HOOK} ack commit --repo {self.repo}",
            'git commit -m "change"',
        ]
        log = "\n".join(
            [
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_1",
                                    "name": "Bash",
                                    "input": {"command": commands[0]},
                                }
                            ]
                        }
                    }
                ),
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": "toolu_1",
                                    "is_error": True,
                                    "content": "Do not combine the ack command with the commit command",
                                }
                            ]
                        }
                    }
                ),
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_2",
                                    "name": "Bash",
                                    "input": {"command": commands[1]},
                                }
                            ]
                        }
                    }
                ),
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_3",
                                    "name": "Bash",
                                    "input": {"command": commands[2]},
                                }
                            ]
                        }
                    }
                ),
            ]
        )
        ack = subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)
        commit = subprocess.run(
            ["git", "commit", "-m", "change"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)

        ok, details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            [commands[0]],
        )

        self.assertFalse(ok)
        self.assertIn("retry after failed or blocked attempt", details)

    def test_live_probe_accepts_clean_block_transcript(self) -> None:
        live_probes = load_live_probes()
        command = f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"'
        log = "\n".join(
            [
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_1",
                                    "name": "Bash",
                                    "input": {"command": command},
                                }
                            ]
                        }
                    }
                ),
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": "toolu_1",
                                    "is_error": True,
                                    "content": "Do not combine the ack command with the commit command",
                                }
                            ]
                        }
                    }
                ),
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertTrue(ok, details)

    def test_live_probe_rejects_codex_pretooluse_router_error_line(self) -> None:
        live_probes = load_live_probes()
        command = f"{HOOK} ack release --repo {self.repo} && git tag v9.9.9"
        log = (
            "ERROR codex_core::tools::router: "
            "error=Command blocked by PreToolUse hook: "
            "Do not combine the ack command with the release command. "
            f"Command: {command}"
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertFalse(ok)
        self.assertIn("hook error marker", details)

    def test_live_probe_accepts_clean_codex_permission_denial_transcript(self) -> None:
        live_probes = load_live_probes()
        command = f"{HOOK} ack release --repo {self.repo} && git tag v9.9.9"
        log = "\n".join(
            [
                json.dumps(
                    {
                        "permission_denials": [
                            {
                                "tool_use_id": "exec_1",
                                "tool_input": {"command": command},
                                "reason": "Do not combine the ack command with the release command",
                            }
                        ]
                    }
                ),
                "Do not combine the ack command with the release command",
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertTrue(ok, details)

    def test_live_probe_accepts_sem_hook_probe_marker_transcript(self) -> None:
        live_probes = load_live_probes()
        command = f"{HOOK} ack release --repo {self.repo} && git tag v9.9.9"
        log = json.dumps(
            {
                "sem_hook_probe_denials": [
                    {
                        "tool_use_id": "sem_hook_probe_1",
                        "tool_input": {"command": command},
                        "reason": "Do not combine the ack command with the release command",
                    }
                ]
            }
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertTrue(ok, details)

    def test_live_probe_accepts_codex_agent_message_block_transcript(self) -> None:
        live_probes = load_live_probes()
        command = f"{HOOK} ack release --repo {self.repo} && git tag v9.9.9"
        log = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "id": "item_1",
                    "type": "agent_message",
                    "text": "\n".join(
                        [
                            "The requested command was blocked by the Staff Engineer Mode PreToolUse hook.",
                            "",
                            "Blocked command:",
                            "",
                            "```bash",
                            command,
                            "```",
                            "",
                            "The hook blocked it because the ack and release/tag command were combined.",
                            "Policy requires the release ack and tag creation to be separate shell commands.",
                        ]
                    ),
                },
            }
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertTrue(ok, details)

    def test_codex_env_suppresses_router_deny_log_without_overwriting_other_logs(self) -> None:
        live_probes = load_live_probes()

        with patch.dict(os.environ, {"RUST_LOG": "info"}, clear=True):
            env = live_probes.codex_env()

        self.assertEqual(env["RUST_LOG"], "info,codex_core::tools::router=off")

    def test_codex_local_marketplace_points_at_current_checkout(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            marketplace_root = Path(tmp) / "marketplace"
            live_probes.write_codex_local_marketplace(marketplace_root)

            manifest_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            plugin_path = marketplace_root / "plugins" / "staff-engineer-mode"

            self.assertTrue(plugin_path.exists())
            self.assertEqual(manifest["plugins"][0]["source"]["source"], "local")
            self.assertEqual(
                (plugin_path / "hooks" / "hooks.json").read_text(encoding="utf-8"),
                (ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"),
            )

    def test_codex_hook_trust_uses_current_hashes_from_plugin_hooks(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.toml"
            config_path.write_text("[plugins.test]\nenabled = true\n", encoding="utf-8")
            hooks = [
                {
                    "key": "plugin:a",
                    "source": "plugin",
                    "pluginId": "staff-engineer-mode@staff-engineer-mode",
                    "currentHash": "sha256:" + "1" * 64,
                },
                {
                    "key": "user:b",
                    "source": "user",
                    "pluginId": None,
                    "currentHash": "sha256:" + "2" * 64,
                },
                {
                    "key": "plugin:c",
                    "source": "plugin",
                    "pluginId": "staff-engineer-mode@staff-engineer-mode",
                    "currentHash": "sha256:" + "3" * 64,
                },
            ]

            trusted = live_probes.append_codex_hook_trust(config_path, hooks)
            text = config_path.read_text(encoding="utf-8")

            self.assertEqual(trusted, ["plugin:a", "plugin:c"])
            self.assertIn("[hooks.state.\"plugin:a\"]", text)
            self.assertIn("[hooks.state.\"plugin:c\"]", text)
            self.assertNotIn("user:b", text)
            self.assertIn("sha256:" + "1" * 64, text)
            self.assertIn("sha256:" + "3" * 64, text)

    def test_run_codex_uses_prepared_plugin_environment_without_inline_hook_config(self) -> None:
        live_probes = load_live_probes()
        probe = live_probes.Probe("codex", "commit", "block", "gpt-5.5", "high")
        args = type("Args", (), {"timeout": 123})()
        base_env = {"HOME": "/tmp/sem-home", "CODEX_HOME": "/tmp/sem-home/.codex"}
        captured: dict[str, object] = {}

        def fake_run(command, *, cwd, env=None, input_text=None, timeout):
            captured["command"] = command
            captured["env"] = env
            captured["timeout"] = timeout
            return subprocess.CompletedProcess(command, 0, "", "")

        with patch.object(live_probes, "run", fake_run):
            live_probes.run_codex(probe, self.repo, "prompt", args, base_env)

        command = captured["command"]
        self.assertIsInstance(command, list)
        joined_command = "\n".join(command)
        self.assertNotIn("hooks.PreToolUse", joined_command)
        self.assertNotIn("--dangerously-bypass-hook-trust", command)
        env = captured["env"]
        self.assertIsInstance(env, dict)
        self.assertEqual(env["HOME"], base_env["HOME"])
        self.assertEqual(env["CODEX_HOME"], base_env["CODEX_HOME"])
        self.assertIn("SEM_HOOK_PROBE_MARKER", env)

    def test_live_probe_accepts_clean_allow_transcript(self) -> None:
        live_probes = load_live_probes()
        self.stage_change("initial\nchanged\n")
        commands = [
            f"{HOOK} ack commit --repo {self.repo}",
            'git commit -m "change"',
        ]
        ack = subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)
        commit = subprocess.run(
            ["git", "commit", "-m", "change"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)
        log = "\n".join(
            json.dumps(
                {
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": f"toolu_{index}",
                                "name": "Bash",
                                "input": {"command": command},
                            }
                        ]
                    }
                }
            )
            for index, command in enumerate(commands, 1)
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "allow", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            commands,
        )

        self.assertTrue(ok, details)

    def test_live_probe_parses_codex_command_failures_and_retries(self) -> None:
        live_probes = load_live_probes()
        commands = [
            f"{HOOK} ack release --repo {self.repo} && git tag v1.2.3",
            f"{HOOK} ack release --repo {self.repo}",
        ]
        log = "\n".join(
            [
                json.dumps(
                    {
                        "item": {
                            "id": "exec_1",
                            "type": "command_execution",
                            "command": commands[0],
                            "exit_code": 2,
                        }
                    }
                ),
                json.dumps(
                    {
                        "item": {
                            "id": "exec_2",
                            "type": "command_execution",
                            "command": commands[1],
                            "exit_code": 0,
                        }
                    }
                ),
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [commands[0]],
        )

        self.assertFalse(ok)
        self.assertIn("retry after failed or blocked attempt", details)

    def test_live_probe_rejects_shell_exit_as_block_without_host_hook_denial(self) -> None:
        live_probes = load_live_probes()
        command = f"{HOOK} ack release --repo {self.repo} && git tag v9.9.9"
        log = "\n".join(
            [
                json.dumps(
                    {
                        "item": {
                            "id": "exec_1",
                            "type": "command_execution",
                            "command": command,
                            "exit_code": 2,
                        }
                    }
                ),
                "Do not combine the ack command with the release command",
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertFalse(ok)
        self.assertIn("reached shell instead of a host hook denial", details)

    def test_live_probe_rejects_block_probe_that_writes_receipt(self) -> None:
        live_probes = load_live_probes()
        self.stage_change("initial\nchanged\n")
        receipt_dir = self.repo / ".git" / "staff-engineer-mode" / "agent-event-receipts" / "commit"
        receipt_dir.mkdir(parents=True)
        (receipt_dir / "leaked.json").write_text("{}", encoding="utf-8")
        command = f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"'
        log = "\n".join(
            [
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_1",
                                    "name": "Bash",
                                    "input": {"command": command},
                                }
                            ]
                        }
                    }
                ),
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": "toolu_1",
                                    "is_error": True,
                                    "content": "Do not combine the ack command with the commit command",
                                }
                            ]
                        }
                    }
                ),
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertFalse(ok)
        self.assertIn("wrote a receipt", details)

    def test_live_probe_allows_sem_read_preludes_before_protected_commands(self) -> None:
        live_probes = load_live_probes()
        self.stage_change("initial\nchanged\n")
        commands = [
            f"{HOOK} ack commit --repo {self.repo}",
            'git commit -m "change"',
        ]
        log = "\n".join(
            [
                json.dumps(
                    {
                        "item": {
                            "id": "exec_1",
                            "type": "command_execution",
                            "command": (
                                "/bin/bash -lc 'cat "
                                "/home/mark/.codex/plugins/cache/staff-engineer-mode/"
                                "staff-engineer-mode/current/specialists/agent-pr-review.md'"
                            ),
                            "exit_code": 0,
                        }
                    }
                ),
                json.dumps(
                    {
                        "item": {
                            "id": "exec_2",
                            "type": "command_execution",
                            "command": f"/bin/bash -lc '{commands[0]}'",
                            "exit_code": 0,
                        }
                    }
                ),
                json.dumps(
                    {
                        "item": {
                            "id": "exec_3",
                            "type": "command_execution",
                            "command": f"/bin/bash -lc '{commands[1]}'",
                            "exit_code": 0,
                        }
                    }
                ),
            ]
        )
        subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        subprocess.run(["git", "commit", "-m", "change"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            commands,
        )

        self.assertTrue(ok, details)

    def test_live_probe_rejects_compound_or_trailing_junk_commands(self) -> None:
        live_probes = load_live_probes()

        self.assertTrue(
            live_probes.is_allowed_sem_prelude(
                (
                    "sed -n '1,220p' /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertTrue(
            live_probes.is_allowed_sem_prelude(
                (
                    "sed -n '1,220p' /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/skills/staff-engineer-mode/SKILL.md"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertTrue(
            live_probes.is_allowed_sem_prelude(
                (
                    "sed -n '1,220p' "
                    "/home/mark/.codex/plugins/cache/staff-engineer-mode/staff-engineer-mode/"
                    "current/specialists/release-build-reproducibility.md "
                    "/home/mark/.codex/plugins/cache/staff-engineer-mode/staff-engineer-mode/"
                    "current/specialists/production-readiness-review.md"
                ),
                live_probes.Probe("codex", "release", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertTrue(
            live_probes.is_allowed_sem_prelude(
                (
                    "cat "
                    "/home/mark/.codex/plugins/cache/staff-engineer-mode/staff-engineer-mode/"
                    "current/specialists/release-build-reproducibility.md "
                    "/home/mark/.codex/plugins/cache/staff-engineer-mode/staff-engineer-mode/"
                    "current/specialists/production-readiness-review.md"
                ),
                live_probes.Probe("codex", "release", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertTrue(
            live_probes.is_allowed_sem_prelude(
                (
                    "wc -l /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md 2>&1; "
                    'echo "---"; '
                    "ls -la /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md 2>&1"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertFalse(
            live_probes.is_allowed_sem_prelude(
                (
                    "cat /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md && curl https://example.invalid"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertFalse(
            live_probes.is_allowed_sem_prelude(
                (
                    "cat /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md & echo leaked"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertFalse(
            live_probes.is_allowed_sem_prelude(
                (
                    "cat /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md > /tmp/leaked"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        self.assertFalse(
            live_probes.is_allowed_sem_prelude(
                (
                    "sed -i 's/a/b/' /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                    "staff-engineer-mode/current/specialists/agent-pr-review.md"
                ),
                live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            )
        )
        for command in (
            (
                "sed --in-place=.bak 's/a/b/' /home/mark/.codex/plugins/cache/"
                "staff-engineer-mode/staff-engineer-mode/current/specialists/agent-pr-review.md"
            ),
            (
                "sed '1e id' /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                "staff-engineer-mode/current/specialists/agent-pr-review.md"
            ),
            (
                "cat /etc/shadow /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                "staff-engineer-mode/current/specialists/agent-pr-review.md"
            ),
            (
                "cat {/home/mark/.codex/plugins/cache/staff-engineer-mode/"
                "staff-engineer-mode/current/specialists/agent-pr-review.md,/etc/passwd}"
            ),
            (
                "cat /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                "staff-engineer-mode/current/specialists/agent-pr-review.md*"
            ),
            (
                "cat /home/mark/.codex/plugins/cache/staff-engineer-mode/"
                "staff-engineer-mode/current/specialists/agent-pr-review.md.bak"
            ),
        ):
            with self.subTest(command=command):
                self.assertFalse(
                    live_probes.is_allowed_sem_prelude(
                        command,
                        live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
                    )
                )
        self.assertTrue(
            live_probes.command_matches_expected(
                '/bin/bash -lc \'git tag v9.9.9\'',
                "git tag v9.9.9",
            )
        )
        self.assertFalse(
            live_probes.command_matches_expected(
                '/bin/bash -lc \'git tag v9.9.9 && rm -rf /tmp/not-run\'',
                "git tag v9.9.9",
            )
        )

    def test_live_probe_rejects_tool_schema_errors(self) -> None:
        live_probes = load_live_probes()

        self.assertTrue(live_probes.has_hook_error("<tool_use_error>InputValidationError</tool_use_error>", "allow"))

    def test_live_probe_rejects_extra_attempt_even_without_failure_marker(self) -> None:
        live_probes = load_live_probes()
        commands = [
            f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"',
            "git status --short",
        ]
        log = "\n".join(
            json.dumps(
                {
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": f"toolu_{index}",
                                "name": "Bash",
                                "input": {"command": command},
                            }
                        ]
                    }
                }
            )
            for index, command in enumerate(commands, 1)
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            [commands[0]],
        )

        self.assertFalse(ok)
        self.assertIn("extra shell attempt", details)

    def test_live_probe_rejects_hook_error_marker_even_when_side_effects_pass(self) -> None:
        live_probes = load_live_probes()
        self.stage_change("initial\nchanged\n")
        commands = [
            f"{HOOK} ack commit --repo {self.repo}",
            'git commit -m "change"',
        ]
        ack = subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)
        commit = subprocess.run(
            ["git", "commit", "-m", "change"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)
        log = "\n".join(
            [
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_1",
                                    "name": "Bash",
                                    "input": {"command": commands[0]},
                                }
                            ]
                        }
                    }
                ),
                json.dumps(
                    {
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "toolu_2",
                                    "name": "Bash",
                                    "input": {"command": commands[1]},
                                }
                            ]
                        }
                    }
                ),
                "Plugin hook error: unsupported additionalContext",
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "allow", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            commands,
        )

        self.assertFalse(ok)
        self.assertIn("hook error marker", details)

    def test_live_probe_rejects_codex_hook_error_marker(self) -> None:
        live_probes = load_live_probes()
        self.stage_change("initial\nchanged\n")
        commands = [
            f"{HOOK} ack commit --repo {self.repo}",
            'git commit -m "change"',
        ]
        ack = subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)
        commit = subprocess.run(
            ["git", "commit", "-m", "change"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)
        log = "\n".join(
            [
                json.dumps(
                    {
                        "item": {
                            "id": "exec_1",
                            "type": "command_execution",
                            "command": commands[0],
                            "exit_code": 0,
                        }
                    }
                ),
                json.dumps(
                    {
                        "item": {
                            "id": "exec_2",
                            "type": "command_execution",
                            "command": commands[1],
                            "exit_code": 0,
                        }
                    }
                ),
                "hook failed: stderr contained a plugin lifecycle error",
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            commands,
        )

        self.assertFalse(ok)
        self.assertIn("hook error marker", details)

    def test_git_c_commit_binds_block_to_target_repo(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"git -C {self.repo} commit -m change"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_cd_then_commit_binds_block_to_target_repo(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"cd {self.repo} && git commit -m change"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_stage_and_commit_uses_single_git_commit_gate(self) -> None:
        # Ack the current (empty-staged) state so the commit branch would allow.
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        self.modify_unstaged("initial\nchanged\n")

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": 'git add README.md && git commit -m "change"'},
            }
        )

        self.assert_pretooluse_denies(result)
        cached = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=self.repo, text=True)
        self.assertEqual(cached, "")

    def test_cd_then_stage_and_commit_uses_single_git_commit_gate_for_target_repo(self) -> None:
        subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo.parent,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        self.modify_unstaged("initial\nchanged\n")

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'cd {self.repo} && git add README.md && git commit -m "change"'
                },
            },
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_commit_ack_repo_allows_target_repo_command(self) -> None:
        self.stage_change("initial\nchanged\n")
        ack = subprocess.run(
            [str(HOOK), "ack", "commit", "--repo", str(self.repo)],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)

        allowed = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"cd {self.repo} && git commit -m change"}},
            cwd=self.repo.parent,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")

    def test_commit_receipt_allows_same_staged_diff_only(self) -> None:
        self.stage_change("initial\nchanged\n")
        ack = subprocess.run(
            [str(HOOK), "ack", "commit"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)

        allowed = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")

        self.stage_change("initial\nchanged again\n")
        blocked = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})
        self.assert_pretooluse_denies(blocked)

    def test_commit_override_receipt_allows_user_accepted_gaps(self) -> None:
        self.stage_change("initial\nchanged\n")
        ack = subprocess.run(
            [str(HOOK), "ack", "commit", "--override", "user accepts missing behavior test"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)

        receipts = list((self.repo / ".git" / "staff-engineer-mode" / "agent-event-receipts" / "commit").glob("*.json"))
        self.assertEqual(len(receipts), 1)
        receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
        self.assertTrue(receipt["override"])
        self.assertEqual(receipt["rationale"], "user accepts missing behavior test")

        allowed = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_commit_all_uses_single_git_commit_gate(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -am change"}})

        self.assert_pretooluse_denies(result, "before_commit policy requires agent-pr-review")

    def test_commit_with_ai_coauthor_is_blocked_even_with_matching_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        'git commit -m "Add MIT license\n\n'
                        'Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"'
                    )
                },
            }
        )

        self.assert_pretooluse_denies(result, "blocks AI assistant co-author")

    def test_commit_with_human_named_claude_coauthor_is_allowed_with_matching_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        'git commit -m "Update docs\n\n'
                        'Co-Authored-By: Claude Martin <claude.martin@example.com>"'
                    )
                },
            }
        )

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_commit_all_with_ai_coauthor_uses_single_git_commit_gate(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": (
                        'git commit -am "Update docs\n\n'
                        'Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"'
                    )
                },
            }
        )

        self.assert_pretooluse_denies(result, "blocks AI assistant co-author")

    def test_release_command_blocks_without_release_receipt(self) -> None:
        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git tag v1.2.3"}})

        self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_git_push_branch_does_not_trigger_release_gate(self) -> None:
        for cmd in (
            "git push origin main",
            "git push --force-with-lease origin feature/work",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_git_push_tags_triggers_release_gate(self) -> None:
        for cmd in (
            "git push --tags",
            "git push --follow-tags origin main",
            "git push origin v1.2.3",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_release_block_response_uses_structured_deny_without_hook_failure(self) -> None:
        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git tag v1.2.3"}})

        self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_ack_and_release_same_shell_command_explains_separate_invocation(self) -> None:
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'{HOOK} ack release --repo {self.repo} && git tag v1.2.3'
                },
            }
        )

        self.assert_pretooluse_denies(
            result,
            "own shell command",
            "Do not combine the ack command with the release command",
        )

    def test_ack_and_release_same_shell_command_does_not_make_hook_error_without_host_hook(self) -> None:
        result = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    f"cd {shlex.quote(str(self.repo))} && "
                    f"{shlex.quote(str(HOOK))} ack release --repo {shlex.quote(str(self.repo))} && "
                    "git tag v1.2.3"
                ),
            ],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        tags = subprocess.check_output(["git", "tag", "--list"], cwd=self.repo, text=True)
        self.assertEqual(tags, "v1.2.3\n")
        self.assertGreater(len(self.receipt_files("release")), 0)

    def test_standalone_ack_then_release_succeeds_without_host_hook(self) -> None:
        ack = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    f"cd {shlex.quote(str(self.repo))} && "
                    f"{shlex.quote(str(HOOK))} ack release --repo {shlex.quote(str(self.repo))}"
                ),
            ],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)
        self.assertGreater(len(self.receipt_files("release")), 0)

        tag = subprocess.run(
            ["bash", "-lc", f"cd {shlex.quote(str(self.repo))} && git tag v1.2.3"],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(tag.returncode, 0, tag.stderr)
        tags = subprocess.check_output(["git", "tag", "--list"], cwd=self.repo, text=True)
        self.assertEqual(tags, "v1.2.3\n")

    def test_git_c_release_binds_block_to_target_repo(self) -> None:
        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"git -C {self.repo} tag v1.2.3"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_cd_then_release_binds_block_to_target_repo(self) -> None:
        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"cd {self.repo} && git tag v1.2.3"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_release_ack_repo_allows_target_repo_command(self) -> None:
        ack = subprocess.run(
            [str(HOOK), "ack", "release", "--repo", str(self.repo)],
            cwd=self.repo.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)

        allowed = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"cd {self.repo} && git tag v1.2.3"}},
            cwd=self.repo.parent,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")

    def test_release_receipt_allows_release_command(self) -> None:
        ack = subprocess.run(
            [str(HOOK), "ack", "release"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git tag v1.2.3"}})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_non_policy_command_is_allowed(self) -> None:
        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git status --short"}})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cd_then_gh_release_create_binds_block_to_target_repo(self) -> None:
        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"cd {self.repo} && gh release create v1.0.0"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_cd_then_gh_release_delete_binds_block_to_target_repo(self) -> None:
        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"cd {self.repo} && gh release delete v1.0.0"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_cd_then_bump_version_script_does_not_trigger_release_gate(self) -> None:
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": f"cd {self.repo} && ./scripts/bump-version.sh 1.0.0"},
            },
            cwd=self.repo.parent,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_reading_bump_version_script_does_not_trigger_release_gate(self) -> None:
        for cmd in (
            "sed -n '1,220p' scripts/bump-version.sh",
            "cat scripts/bump-version.sh",
            "rg bump-version.sh scripts",
            "grep -n bump-version.sh AGENTS.md",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_bump_version_check_and_audit_do_not_trigger_release_gate(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh --check",
            "./scripts/bump-version.sh --audit",
            "bash scripts/bump-version.sh --check",
            "bash scripts/bump-version.sh --audit",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_bump_version_script_does_not_trigger_release_gate_by_name(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh 1.0.0",
            "scripts/bump-version.sh 1.0.0",
            "bash scripts/bump-version.sh 1.0.0",
            "env FOO=bar ./scripts/bump-version.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_repo_local_scripts_do_not_trigger_release_gate_by_name(self) -> None:
        for cmd in (
            "./scripts/release.sh 1.0.0",
            "bash scripts/publish-release.sh 1.0.0",
            "sh tools/promote-artifact.sh production",
            "env TARGET=prod ./bin/cut-release 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_cd_chain_returning_to_repo_does_not_bypass_release_gate(self) -> None:
        (self.repo / "docs").mkdir()
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "cd docs && cd .. && gh release create v1.0.0"},
            },
        )

        self.assert_pretooluse_denies(result)

    def test_cd_into_subdir_does_not_bypass_release_gate(self) -> None:
        (self.repo / "docs").mkdir()
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "cd docs && gh release create v1.0.0"},
            },
        )

        self.assert_pretooluse_denies(result)

    def test_cd_to_missing_dir_does_not_bypass_release_gate(self) -> None:
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "cd missing-dir; gh release create v1.0.0"},
            },
        )

        self.assert_pretooluse_denies(result)

    def test_cd_to_non_repo_path_does_not_bypass_release_gate(self) -> None:
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "cd /tmp && gh release create v1.0.0 --repo owner/other"},
            },
        )

        self.assert_pretooluse_denies(result)

    def test_gh_release_with_leading_global_flags_does_not_bypass(self) -> None:
        for cmd in (
            "gh --repo owner/project release delete v1.0.0",
            "gh -R owner/project release create v1.0.0",
            "gh --hostname github.example.com release edit v1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result)

    def test_gh_remote_repo_release_blocks_even_with_local_release_receipt(self) -> None:
        # A local release receipt must NOT authorize a cross-repo gh release.
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "gh --repo owner/other release create v1.0.0"},
            }
        )

        self.assert_pretooluse_denies(result)

    def test_gh_remote_release_blocks_after_authorized_local_release_event(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "git tag v1.0.0 && gh --repo owner/other release create v1.0.0"
                },
            }
        )

        self.assert_pretooluse_denies(result)

    def test_gh_release_via_env_var_repo_selector_is_remote(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for cmd in (
            "GH_REPO=owner/other gh release create v1.0.0",
            "GH_HOST=enterprise.example.com gh release delete v1.0.0",
            "FOO=bar GH_REPO=owner/other gh release create v1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result)

    def test_gh_release_via_inherited_env_var_repo_selector_is_remote(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for env in ({"GH_REPO": "owner/other"}, {"GH_HOST": "enterprise.example.com"}):
            with self.subTest(env=env):
                result = self.run_hook(
                    {"tool_name": "Bash", "tool_input": {"command": "gh release create v1.0.0"}},
                    env=env,
                )
                self.assert_pretooluse_denies(result)

    def test_gh_release_via_hostname_selector_is_remote(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for cmd in (
            "gh --hostname enterprise.example.com release create v1.0.0",
            "gh release --hostname enterprise.example.com delete v1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result)

    def test_gh_release_delete_asset_blocks_without_release_receipt(self) -> None:
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "gh release delete-asset v1.0.0 artifact.tgz"},
            }
        )

        self.assert_pretooluse_denies(result)

    def test_gh_repo_flag_in_any_position_classifies_as_remote(self) -> None:
        # gh accepts --repo / -R before "release", between "release" and the action,
        # after the action, or with values attached to the short flag. All must be
        # classified as cross-repo and blocked, even with a local release receipt.
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for cmd in (
            "gh release --repo owner/other create v1.0.0",
            "gh release create v1.0.0 --repo owner/other",
            "gh release create --repo=owner/other v1.0.0",
            "gh release -R owner/other delete v1.0.0",
            "gh release create v1.0.0 -Rowner/other",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result)

    def test_gh_remote_release_blocks_from_non_repo_directory(self) -> None:
        # Hook must block cross-repo gh releases even when the invoking shell
        # is not inside any git repository.
        with tempfile.TemporaryDirectory() as non_repo:
            result = self.run_hook(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "gh --repo owner/other release create v1.0.0"},
                },
                cwd=Path(non_repo),
            )

            self.assert_pretooluse_denies(result)

    def test_gh_non_release_subcommand_is_not_classified(self) -> None:
        # Action keywords appearing as flag values inside a different gh
        # subcommand must not trigger the release gate.
        for cmd in (
            "gh issue create --title release --body delete",
            "gh pr create --title 'release notes' --body 'delete me'",
            "gh release list",
            "gh release view v1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_no_python_fallback_does_not_block_non_mutating_gh_release_actions(self) -> None:
        for cmd in (
            "gh release view delete",
            "gh release list create",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_no_python_fallback_inherited_env_selector_is_remote(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for env in ({"GH_REPO": "owner/other"}, {"GH_HOST": "enterprise.example.com"}):
            with self.subTest(env=env):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": "gh release create v1.0.0"}},
                    extra_env=env,
                )
                self.assert_pretooluse_denies(result)

    def test_no_python_fallback_remote_gh_release_blocks_with_local_receipt(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for cmd in (
            "gh --repo owner/other release create v1.0.0",
            "gh release --repo owner/other create v1.0.0",
            "gh release create v1.0.0 --repo owner/other",
            "gh release create v1.0.0 -Rowner/other",
            "gh release create v1.0.0 --hostname enterprise.example.com",
            "GH_REPO=owner/other gh release create v1.0.0",
            "GH_HOST=enterprise.example.com gh release delete v1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result)

    def test_no_python_fallback_allows_reading_bump_version_script(self) -> None:
        for cmd in (
            "sed -n '1,220p' scripts/bump-version.sh",
            "cat scripts/bump-version.sh",
            "rg bump-version.sh scripts",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_no_python_fallback_does_not_classify_bump_version_script_by_name(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh 1.0.0",
            "scripts/bump-version.sh 1.0.0",
            "bash scripts/bump-version.sh 1.0.0",
            "env FOO=bar ./scripts/bump-version.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_no_python_fallback_does_not_classify_repo_local_scripts_by_name(self) -> None:
        for cmd in (
            "./scripts/release.sh 1.0.0",
            "bash scripts/publish-release.sh 1.0.0",
            "sh tools/promote-artifact.sh production",
            "env TARGET=prod ./bin/cut-release 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_minimal_shell_fallback_blocks_commit_without_python_or_jq(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook_without_python_or_jq(
            {"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}}
        )

        self.assert_pretooluse_denies(result, "before_commit policy requires agent-pr-review")

    def test_no_python_fallback_allows_branch_pushes(self) -> None:
        for cmd in (
            "git push origin main",
            "git push --force-with-lease origin feature/work",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")
                self.assertEqual(result.stdout, "")

    def test_no_python_fallback_blocks_tag_pushes(self) -> None:
        for cmd in (
            "git push --tags",
            "git push --follow-tags origin main",
            "git push origin v1.2.3",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_minimal_shell_fallback_allows_branch_pushes_without_python_or_jq(self) -> None:
        for cmd in (
            "git push origin main",
            "git push --force-with-lease origin feature/work",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python_or_jq(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")
                self.assertEqual(result.stdout, "")

    def test_minimal_shell_fallback_blocks_tag_pushes_without_python_or_jq(self) -> None:
        for cmd in (
            "git push --tags",
            "git push --follow-tags origin main",
            "git push origin v1.2.3",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python_or_jq(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_minimal_shell_fallback_malformed_payload_exits_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as bin_dir:
            path_dir = Path(bin_dir)
            for tool in ("awk", "bash", "cat", "dirname", "git", "grep"):
                target = shutil.which(tool)
                if target is None:
                    raise AssertionError(f"required test tool not found: {tool}")
                os.symlink(target, path_dir / tool)
            process_env = os.environ.copy()
            process_env["PATH"] = str(path_dir)
            result = subprocess.run(
                [str(HOOK), "pretooluse"],
                cwd=self.repo,
                env=process_env,
                input="{not-json",
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_minimal_shell_fallback_protected_command_outside_repo_exits_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as non_repo:
            path_dir = Path(bin_dir)
            for tool in ("awk", "bash", "cat", "dirname", "git", "grep"):
                target = shutil.which(tool)
                if target is None:
                    raise AssertionError(f"required test tool not found: {tool}")
                os.symlink(target, path_dir / tool)
            process_env = os.environ.copy()
            process_env["PATH"] = str(path_dir)
            result = subprocess.run(
                [str(HOOK), "pretooluse"],
                cwd=Path(non_repo),
                env=process_env,
                input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}}),
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_minimal_shell_fallback_allows_reading_bump_version_script_without_python_or_jq(self) -> None:
        for cmd in (
            "sed -n '1,220p' scripts/bump-version.sh",
            "cat scripts/bump-version.sh",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python_or_jq(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_minimal_shell_fallback_does_not_classify_bump_version_script_by_name(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh 1.0.0",
            "bash scripts/bump-version.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python_or_jq(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")


if __name__ == "__main__":
    unittest.main()
