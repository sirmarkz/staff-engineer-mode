#!/usr/bin/env python3
from __future__ import annotations

import configparser
import json
import io
import os
import importlib.util
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
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
        *scenario_notes: str,
    ) -> dict[str, object]:
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        response = json.loads(result.stdout)
        hook_output = response.get("hookSpecificOutput")
        self.assertIsInstance(hook_output, dict)
        assert isinstance(hook_output, dict)
        self.assertEqual(hook_output.get("hookEventName"), "PreToolUse")
        self.assertEqual(
            hook_output.get("permissionDecision"),
            "deny",
            "; ".join(scenario_notes) or None,
        )
        self.assertIsInstance(response.get("systemMessage"), str)
        self.assertEqual(hook_output.get("permissionDecisionReason"), response["systemMessage"])
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
        entries = {
            key.strip(): value.strip()
            for line in result.stdout.splitlines()
            if line.startswith("- ") and ":" in line
            for key, value in [line[2:].split(":", 1)]
        }
        self.assertGreaterEqual(len(entries), 3)
        self.assertTrue({"commit", "release", "release_remote"}.issubset(entries))
        self.assertTrue(all(entries.values()))

    def test_commit_command_blocks_without_review_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})

        self.assert_pretooluse_denies(result, "before_commit policy requires agent-pr-review")

    def test_block_response_uses_structured_deny_without_hook_failure(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})

        response = self.assert_pretooluse_denies(result, "commit without receipt")
        self.assertEqual(set(response), {"hookSpecificOutput", "systemMessage"})
        self.assertEqual(
            set(response["hookSpecificOutput"]),
            {"hookEventName", "permissionDecision", "permissionDecisionReason"},
        )
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

        response = self.assert_pretooluse_denies(result, "release without receipt")
        entries = [json.loads(line) for line in marker.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["event"], "pretooluse_block")
        self.assertEqual(entries[0]["command"], "git tag v1.2.3")
        self.assertEqual(entries[0]["reason"], response["systemMessage"])

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

    def test_existing_receipt_does_not_allow_ack_and_commit_composition(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"'
                },
            }
        )

        self.assert_pretooluse_denies(result, "preceding command", "separate shell commands")

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

        ok, _details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            [commands[0]],
        )

        self.assertFalse(ok)
        attempts = live_probes.command_attempts_from_log(log)
        self.assertGreater(len(attempts), 1)
        self.assertTrue(attempts[0].failed)

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

        ok, _details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertFalse(ok)
        self.assertTrue(live_probes.has_hook_error(log, "block"))

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

    def test_live_probe_deduplicates_native_and_marker_denials_for_one_attempt(self) -> None:
        live_probes = load_live_probes()
        command = f"{HOOK} ack release --repo {self.repo} && git tag v9.9.9"
        log = "\n".join(
            [
                json.dumps(
                    {
                        "permission_denials": [
                            {
                                "tool_use_id": "exec_1",
                                "tool_input": {"command": f"/bin/bash -lc {shlex.quote(command)}"},
                                "reason": "Do not combine the ack command with the release command",
                            }
                        ]
                    }
                ),
                json.dumps(
                    {
                        "sem_hook_probe_denials": [
                            {
                                "tool_use_id": "sem_hook_probe_1",
                                "tool_input": {"command": command},
                                "reason": "Do not combine the ack command with the release command",
                            }
                        ]
                    }
                ),
            ]
        )

        ok, details = live_probes.verify_result(
            live_probes.Probe("codex", "release", "block", "gpt-5.6-terra", "high"),
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
            config = configparser.ConfigParser()
            config.read_string(config_path.read_text(encoding="utf-8"))
            prefix = 'hooks.state."'
            state = {
                section.removeprefix(prefix).removesuffix('"'): json.loads(
                    config[section]["trusted_hash"]
                )
                for section in config.sections()
                if section.startswith(prefix)
            }

            self.assertEqual(trusted, ["plugin:a", "plugin:c"])
            self.assertEqual(set(state), {"plugin:a", "plugin:c"})
            self.assertEqual(state["plugin:a"], "sha256:" + "1" * 64)
            self.assertEqual(state["plugin:c"], "sha256:" + "3" * 64)

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

    def test_make_repo_resolves_relative_work_root_before_git_initialization(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            previous = Path.cwd()
            try:
                os.chdir(tmp)
                work_root = Path("relative-evidence")
                work_root.mkdir()

                repo = live_probes.make_repo(work_root, "commit")

                self.assertTrue(repo.is_absolute())
                self.assertTrue((repo / ".git").is_dir())
                self.assertEqual(live_probes.commit_count(repo), 1)
            finally:
                os.chdir(previous)

    @unittest.skipUnless(os.name == "posix", "process-group termination requires POSIX")
    def test_host_timeout_terminates_spawned_descendant_process_group(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            survivor = root / "descendant-survived"
            child_code = (
                "import pathlib,sys,time; "
                "time.sleep(0.8); pathlib.Path(sys.argv[1]).write_text('survived')"
            )
            parent_code = (
                "import subprocess,sys; "
                f"subprocess.Popen([sys.executable, '-c', {child_code!r}, sys.argv[1]]); "
                "print('parent-started', flush=True)"
            )

            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                live_probes.run(
                    [sys.executable, "-c", parent_code, str(survivor)],
                    cwd=root,
                    timeout=0.2,
                )

            time.sleep(1.0)
            self.assertFalse(survivor.exists())
            self.assertIn("parent-started", caught.exception.stdout or "")

    @unittest.skipUnless(os.name == "posix", "process-group termination requires POSIX")
    def test_app_server_cleanup_terminates_descendant_after_leader_exits(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            survivor = root / "app-server-descendant-survived"
            child_code = (
                "import pathlib,sys,time; "
                "time.sleep(0.8); pathlib.Path(sys.argv[1]).write_text('survived')"
            )
            fake_codex = root / "codex"
            fake_codex.write_text(
                f"#!{sys.executable}\n"
                "import os, subprocess, sys\n"
                f"subprocess.Popen([sys.executable, '-c', {child_code!r}, "
                "os.environ['SURVIVOR_MARKER']])\n"
                "print('leader-exiting', flush=True)\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            env = {
                "PATH": f"{root}{os.pathsep}{os.environ.get('PATH', '')}",
                "SURVIVOR_MARKER": str(survivor),
            }

            with self.assertRaises(RuntimeError):
                live_probes.app_server_request(
                    "hooks/list",
                    {"cwds": [str(root)]},
                    cwd=root,
                    env=env,
                    timeout=1,
                )

            time.sleep(1.0)
            self.assertFalse(survivor.exists())

    @unittest.skipUnless(os.name == "posix", "process-group termination requires POSIX")
    def test_app_server_initial_broken_pipe_still_cleans_process_group_and_streams(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ready = root / "stdin-closed"
            survivor = root / "broken-pipe-descendant-survived"
            child_code = (
                "import pathlib,sys,time; "
                "time.sleep(0.8); pathlib.Path(sys.argv[1]).write_text('survived')"
            )
            helper_code = (
                "import os,pathlib,subprocess,sys,time; "
                f"subprocess.Popen([sys.executable, '-c', {child_code!r}, sys.argv[2]], "
                "stdin=subprocess.DEVNULL); "
                "os.close(0); pathlib.Path(sys.argv[1]).write_text('ready'); time.sleep(30)"
            )
            real_popen = subprocess.Popen
            created: list[subprocess.Popen[str]] = []

            def launch(_command, **kwargs):
                process = real_popen(
                    [sys.executable, "-c", helper_code, str(ready), str(survivor)],
                    **kwargs,
                )
                created.append(process)
                deadline = time.monotonic() + 2
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                if not ready.exists():
                    raise AssertionError("fake app-server did not close stdin")
                return process

            try:
                with (
                    patch.object(live_probes.subprocess, "Popen", side_effect=launch),
                    self.assertRaises(BrokenPipeError),
                ):
                    live_probes.app_server_request(
                        "hooks/list",
                        {"cwds": [str(root)]},
                        cwd=root,
                        env={},
                        timeout=1,
                    )

                time.sleep(1.0)
                self.assertFalse(survivor.exists())
                self.assertEqual(len(created), 1)
                process = created[0]
                self.assertIsNotNone(process.poll())
                self.assertTrue(process.stdin is not None and process.stdin.closed)
                self.assertTrue(process.stdout is not None and process.stdout.closed)
                self.assertTrue(process.stderr is not None and process.stderr.closed)
            finally:
                for process in created:
                    live_probes.terminate_process_group(process)
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=2)

    def test_live_probe_rejects_nonpositive_timeout_before_environment_checks(self) -> None:
        live_probes = load_live_probes()
        args = type(
            "Args",
            (),
            {
                "host": "all",
                "event": "all",
                "probe": "all",
                "claude_model": "claude-opus-4-8",
                "claude_effort": "high",
                "codex_model": "gpt-5.5",
                "codex_effort": "high",
                "timeout": 0,
                "work_dir": None,
                "keep_temp": False,
            },
        )()

        with (
            patch.object(live_probes, "parse_args", return_value=args),
            patch.object(Path, "exists", side_effect=AssertionError("static check ran")),
            patch.object(live_probes.shutil, "which", side_effect=AssertionError("tool check ran")),
            patch.object(
                live_probes,
                "prepare_codex_probe_environment",
                side_effect=AssertionError("setup ran"),
            ),
            patch("sys.stderr", new_callable=io.StringIO) as stderr,
        ):
            status = live_probes.main()

        self.assertEqual(status, 2)
        self.assertTrue(stderr.getvalue())

    def test_codex_probe_keep_temp_removes_copied_auth_before_retaining_diagnostics(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "codex-probe"
            codex_home = root / "home" / ".codex"
            codex_home.mkdir(parents=True)
            auth_path = codex_home / "auth.json"
            auth_path.write_text('{"token":"must-not-survive"}\n', encoding="utf-8")
            work_dir = Path(tmp) / "work"
            args = type(
                "Args",
                (),
                {
                    "host": "codex",
                    "event": "commit",
                    "probe": "block",
                    "claude_model": "claude-opus-4-8",
                    "claude_effort": "high",
                    "codex_model": "gpt-5.5",
                    "codex_effort": "high",
                    "timeout": 30,
                    "work_dir": work_dir,
                    "keep_temp": True,
                },
            )()
            environment = live_probes.CodexProbeEnvironment(
                env={"HOME": str(root / "home"), "CODEX_HOME": str(codex_home)},
                root=root,
            )
            failed_result = live_probes.ProbeResult(
                live_probes.Probe("codex", "commit", "block", "gpt-5.5", "high"),
                False,
                "expected test failure",
                work_dir / "probe.log",
            )

            with (
                patch.object(live_probes, "parse_args", return_value=args),
                patch.object(live_probes.shutil, "which", return_value="/usr/bin/codex"),
                patch.object(
                    live_probes,
                    "prepare_codex_probe_environment",
                    return_value=environment,
                ),
                patch.object(live_probes, "run_probe", return_value=failed_result),
            ):
                status = live_probes.main()

            self.assertEqual(status, 1)
            self.assertTrue(root.exists())
            self.assertFalse(auth_path.exists())

    def test_codex_probe_setup_failure_removes_copied_auth(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source_home = temp_root / "source-codex"
            source_home.mkdir()
            (source_home / "auth.json").write_text(
                '{"token":"must-not-survive"}\n',
                encoding="utf-8",
            )
            probe_root = temp_root / "probe-root"
            work_root = temp_root / "work"
            work_root.mkdir()

            with (
                patch.object(live_probes, "source_codex_home", return_value=source_home),
                patch.object(live_probes, "codex_probe_root", return_value=probe_root),
                patch.object(
                    live_probes,
                    "checked_run",
                    side_effect=RuntimeError("setup failed after auth copy"),
                ),
            ):
                with self.assertRaises(RuntimeError):
                    live_probes.prepare_codex_probe_environment(work_root, timeout=30)

            self.assertFalse((probe_root / "home" / ".codex" / "auth.json").exists())

    def test_codex_probe_setup_failure_redacts_copied_auth_values(self) -> None:
        live_probes = load_live_probes()
        secret = "setup-secret-must-not-leak"

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source_home = temp_root / "source-codex"
            source_home.mkdir()
            (source_home / "auth.json").write_text(
                json.dumps({"token": secret}),
                encoding="utf-8",
            )
            probe_root = temp_root / "probe-root"
            work_root = temp_root / "work"
            work_root.mkdir()

            with (
                patch.object(live_probes, "source_codex_home", return_value=source_home),
                patch.object(live_probes, "codex_probe_root", return_value=probe_root),
                patch.object(
                    live_probes,
                    "checked_run",
                    side_effect=RuntimeError(f"setup output contained {secret}"),
                ),
            ):
                with self.assertRaises(RuntimeError) as caught:
                    live_probes.prepare_codex_probe_environment(work_root, timeout=30)

            message = str(caught.exception)
            self.assertNotIn(secret, message)
            self.assertTrue(message)
            self.assertFalse((probe_root / "home" / ".codex" / "auth.json").exists())

    def test_codex_probe_log_redacts_values_copied_from_auth(self) -> None:
        live_probes = load_live_probes()
        probe = live_probes.Probe("codex", "commit", "block", "gpt-5.5", "high")
        args = type("Args", (), {"timeout": 30})()
        secret = "codex-secret-must-not-survive"

        with tempfile.TemporaryDirectory() as tmp:
            work_root = Path(tmp)
            completed = subprocess.CompletedProcess(
                ["codex"],
                1,
                f'{{"error":"credential {secret}"}}\n',
                f"debug bearer {secret}\n",
            )
            with (
                patch.object(live_probes, "run_codex", return_value=completed),
                patch.object(live_probes, "verify_result", return_value=(False, "expected")),
            ):
                result = live_probes.run_probe(
                    probe,
                    args,
                    work_root,
                    {"HOME": "/tmp/probe-home"},
                    (secret,),
                )

            log_text = result.log_path.read_text(encoding="utf-8")
            self.assertNotIn(secret, log_text)
            self.assertTrue(log_text)

    def test_codex_probe_timeout_log_redacts_copied_auth_values(self) -> None:
        live_probes = load_live_probes()
        probe = live_probes.Probe("codex", "commit", "block", "gpt-5.5", "high")
        args = type("Args", (), {"timeout": 30})()
        secret = "timeout-secret-must-not-survive"

        with tempfile.TemporaryDirectory() as tmp:
            work_root = Path(tmp)
            timeout = subprocess.TimeoutExpired(
                ["codex"],
                30,
                output=f"partial {secret}",
                stderr=f"debug {secret}",
            )
            with patch.object(live_probes, "run_codex", side_effect=timeout):
                result = live_probes.run_probe(
                    probe,
                    args,
                    work_root,
                    {"HOME": "/tmp/probe-home"},
                    (secret,),
                )

            self.assertFalse(result.ok)
            self.assertEqual(result.probe, probe)
            self.assertTrue(result.log_path.is_file())
            log_text = result.log_path.read_text(encoding="utf-8")
            self.assertNotIn(secret, log_text)
            self.assertTrue(log_text)

    def test_codex_auth_cleanup_does_not_follow_symlinked_probe_home(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            victim_home = temp_root / "victim-home"
            victim_auth = victim_home / ".codex" / "auth.json"
            victim_auth.parent.mkdir(parents=True)
            victim_auth.write_text('{"token":"real-credential"}\n', encoding="utf-8")
            probe_root = temp_root / "probe-root"
            probe_root.mkdir()
            os.symlink(victim_home, probe_root / "home", target_is_directory=True)

            live_probes.remove_copied_codex_auth(probe_root)

            self.assertTrue(victim_auth.exists())
            self.assertFalse(probe_root.exists())

    def test_prepare_codex_probe_environment_tracks_nested_auth_values(self) -> None:
        live_probes = load_live_probes()

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source_home = temp_root / "source-codex"
            source_home.mkdir()
            (source_home / "auth.json").write_text(
                json.dumps(
                    {
                        "tokens": {
                            "access": "nested-access-secret",
                            "refresh": "nested-refresh-secret",
                        },
                        "metadata": ["account-secret-value"],
                    }
                ),
                encoding="utf-8",
            )
            probe_root = temp_root / "probe-root"
            work_root = temp_root / "work"
            work_root.mkdir()

            with (
                patch.object(live_probes, "source_codex_home", return_value=source_home),
                patch.object(live_probes, "codex_probe_root", return_value=probe_root),
                patch.object(live_probes, "checked_run"),
                patch.object(
                    live_probes,
                    "codex_plugin_hooks",
                    return_value=[
                        {
                            "key": "plugin:pre_tool_use",
                            "source": "plugin",
                            "pluginId": "staff-engineer-mode@staff-engineer-mode",
                            "currentHash": "sha256:" + "1" * 64,
                        }
                    ],
                ),
            ):
                environment = live_probes.prepare_codex_probe_environment(work_root, timeout=30)

            self.assertEqual(
                set(environment.sensitive_values),
                {"nested-access-secret", "nested-refresh-secret", "account-secret-value"},
            )
            live_probes.remove_copied_codex_auth(environment.root)

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

        probe = live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh")
        ok, _details = live_probes.verify_result(
            probe,
            self.repo,
            log,
            [commands[0]],
        )

        self.assertFalse(ok)
        attempts = live_probes.command_attempts_from_log(log)
        self.assertGreater(len(attempts), 1)
        self.assertTrue(attempts[0].failed)

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

        probe = live_probes.Probe("codex", "release", "block", "gpt-5.5", "xhigh")
        ok, _details = live_probes.verify_result(
            probe,
            self.repo,
            log,
            [command],
        )

        self.assertFalse(ok)
        attempts = live_probes.protected_attempts(
            probe,
            live_probes.command_attempts_from_log(log),
        )
        self.assertEqual(len(attempts), 1)
        self.assertTrue(attempts[0].failed)
        self.assertFalse(attempts[0].blocked)

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

        ok, _details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            [command],
        )

        self.assertFalse(ok)
        self.assertTrue(live_probes.receipt_files(self.repo, "commit"))

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
                    "sed -n '1,$p' /home/mark/.codex/plugins/cache/staff-engineer-mode/"
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
                "sed -n '1,$p$(id)' /home/mark/.codex/plugins/cache/staff-engineer-mode/"
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

        probe = live_probes.Probe("claude", "commit", "block", "claude-opus-4-8", "xhigh")
        ok, _details = live_probes.verify_result(
            probe,
            self.repo,
            log,
            [commands[0]],
        )

        self.assertFalse(ok)
        attempts = live_probes.protected_attempts(
            probe,
            live_probes.command_attempts_from_log(log),
        )
        self.assertGreater(len(attempts), 1)

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

        ok, _details = live_probes.verify_result(
            live_probes.Probe("claude", "commit", "allow", "claude-opus-4-8", "xhigh"),
            self.repo,
            log,
            commands,
        )

        self.assertFalse(ok)
        self.assertTrue(live_probes.has_hook_error(log, "allow"))

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

        ok, _details = live_probes.verify_result(
            live_probes.Probe("codex", "commit", "allow", "gpt-5.5", "xhigh"),
            self.repo,
            log,
            commands,
        )

        self.assertFalse(ok)
        self.assertTrue(live_probes.has_hook_error(log, "allow"))

    def test_git_c_commit_binds_block_to_target_repo(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": f"git -C {self.repo} commit -m change"}},
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, str(self.repo))

    def test_alternate_git_directory_cannot_use_current_repo_receipt(self) -> None:
        self.stage_change("initial\nreviewed current repo\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory() as other_tmp:
            other = Path(other_tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, stdout=subprocess.DEVNULL)
            result = self.run_hook(
                {
                    "tool_name": "Bash",
                    "tool_input": {
                        "command": (
                            f"git --git-dir={other / '.git'} --work-tree={other} "
                            'commit -m "unreviewed"'
                        )
                    },
                }
            )

        self.assert_pretooluse_denies(result, "alternate Git repository selector")

    def test_alternate_index_cannot_use_current_repo_receipt(self) -> None:
        self.stage_change("initial\nreviewed current index\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        alternate_index = self.repo / "alternate.index"

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'GIT_INDEX_FILE={alternate_index} git commit -m "unreviewed"'
                },
            }
        )

        self.assert_pretooluse_denies(result, "alternate Git index selector")

    def test_git_configuration_selector_cannot_use_current_repo_receipt(self) -> None:
        self.stage_change("initial\nreviewed current worktree\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'git -c core.worktree={self.repo.parent} commit -m "unreviewed"'
                },
            }
        )

        self.assert_pretooluse_denies(result, "configuration can redirect checkout state")

    def test_inherited_alternate_index_cannot_use_current_repo_receipt(self) -> None:
        self.stage_change("initial\nreviewed current index\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": 'git commit -m "unreviewed"'}},
            env={"GIT_INDEX_FILE": str(self.repo / "alternate.index")},
        )

        self.assert_pretooluse_denies(result, "inherited selector")

    def test_no_python_fallback_rejects_alternate_git_state(self) -> None:
        self.stage_change("initial\nreviewed current index\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        for command, environment in (
            ('git --git-dir=/tmp/other.git --work-tree=/tmp/other commit -m "unreviewed"', None),
            ('GIT_INDEX_FILE=/tmp/other.index git commit -m "unreviewed"', None),
            ('git commit -m "unreviewed"', {"GIT_INDEX_FILE": "/tmp/other.index"}),
        ):
            with self.subTest(command=command, environment=environment):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": command}},
                    extra_env=environment,
                )
                self.assert_pretooluse_denies(result, "degraded parser must fail closed")

    def test_alternate_git_directory_blocks_outside_a_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as other_tmp, tempfile.TemporaryDirectory() as outside_tmp:
            other = Path(other_tmp)
            outside = Path(outside_tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, stdout=subprocess.DEVNULL)
            result = self.run_hook(
                {
                    "tool_name": "Bash",
                    "tool_input": {
                        "command": f"git --git-dir={other / '.git'} --work-tree={other} tag v1.2.3"
                    },
                },
                cwd=outside,
            )

        self.assert_pretooluse_denies(result, "non-repository fallback")

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

    def test_commit_receipt_is_invalidated_when_head_changes(self) -> None:
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "intervening commit"],
            cwd=self.repo,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git commit --allow-empty -m unreviewed"},
            }
        )

        self.assert_pretooluse_denies(result, "before_commit policy requires")

    def test_commit_receipt_rejects_implicit_staging_and_pathspecs(self) -> None:
        second = self.repo / "SECOND.md"
        second.write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "SECOND.md"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", "add second file"],
            cwd=self.repo,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        self.stage_change("initial\nreviewed staged change\n")
        second.write_text("unreviewed implicit change\n", encoding="utf-8")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        for cmd in (
            "git commit -am mixed",
            "git commit --all -m mixed",
            "git commit --include SECOND.md -m mixed",
            "git commit --only SECOND.md -m mixed",
            "git commit -m mixed -- SECOND.md",
            "git commit -m mixed SECOND.md",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "stage intended changes separately")

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

    def test_git_tag_inspection_does_not_trigger_release_gate(self) -> None:
        for cmd in (
            "git tag",
            "git tag --list",
            "git tag --list v1.2.3",
            "git tag -l 'v*'",
            "git tag --points-at HEAD",
            "git tag -v v1.2.3",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")
                self.assertEqual(result.stdout, "")

    def test_git_commit_inspection_does_not_trigger_commit_gate(self) -> None:
        for cmd in (
            "git log --oneline",
            "git log --grep commit",
            "git show --stat HEAD",
            "git rev-list --count HEAD",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")
                self.assertEqual(result.stdout, "")

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

    def test_explicit_tag_refspec_pushes_trigger_release_gate(self) -> None:
        for cmd in (
            "git push origin refs/tags/v1.2.3",
            "git push origin refs/tags/v1.2.3:refs/tags/v1.2.3",
            "git push origin :refs/tags/v1.2.3",
            "git push origin +refs/tags/v1.2.3",
            "git push --mirror origin",
            "git push origin tag release-candidate",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_commit_and_push_composition_is_blocked_even_with_commit_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m change && git push origin main'},
            }
        )

        self.assert_pretooluse_denies(result, "commit and push", "separate shell commands")

    def test_tag_and_push_composition_is_blocked_even_with_release_receipt(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git tag v1.2.3 && git push origin v1.2.3"},
            }
        )

        self.assert_pretooluse_denies(result, "tag and push", "separate shell commands")

    def test_cross_phase_composition_is_blocked_even_with_first_event_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        for cmd in (
            "git commit -m change && git tag v1.2.3",
            "git commit -m change && ./scripts/package.sh",
            "git commit -m change && gh release create v1.2.3",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "protected operations", "separate shell commands")

    def test_release_then_commit_composition_is_blocked_with_release_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git tag v1.2.3 && git commit -m change"},
            }
        )

        self.assert_pretooluse_denies(result, "protected operations", "separate shell commands")

    def test_shell_prefixes_do_not_bypass_commit_gate(self) -> None:
        self.stage_change("initial\nchanged\n")
        for cmd in (
            "foo=bar git commit -m change",
            "env -u FOO git commit -m change",
            "if git commit -m change; then :; fi",
            "command git commit -m change",
            "{ git commit -m change; }",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_commit policy requires")

    def test_path_and_timing_wrappers_do_not_bypass_commit_gate(self) -> None:
        self.stage_change("initial\nchanged\n")
        git_path = shutil.which("git")
        self.assertIsNotNone(git_path)
        for cmd in (
            f"{git_path} commit -m change",
            "time -p git commit -m change",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_commit policy requires")

    def test_newline_separated_commit_cannot_hide_behind_read_only_git_command(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git status --short\ngit commit -m change"},
            }
        )

        self.assert_pretooluse_denies(result, "preceding command", "separate shell commands")

    def test_shell_comments_preserve_real_newline_boundaries_without_false_commands(self) -> None:
        self.stage_change("initial\nchanged\n")
        blocked = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "git status --short # harmless comment\ngit commit -m change"
                },
            }
        )
        self.assert_pretooluse_denies(blocked, "preceding command", "separate shell commands")

        for command in (
            "git status --short # ; git commit -m not-executed",
            "printf '%s\\n' '# ; git commit -m not-executed'",
        ):
            with self.subTest(command=command):
                allowed = self.run_hook(
                    {"tool_name": "Bash", "tool_input": {"command": command}}
                )
                self.assertEqual(allowed.returncode, 0, allowed.stderr)
                self.assertEqual(allowed.stdout, "")

    def test_env_chdir_binds_commit_to_effective_checkout(self) -> None:
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        other = self.repo / "other"
        other.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "other@example.com"], cwd=other, check=True)
        subprocess.run(["git", "config", "user.name", "Other User"], cwd=other, check=True)
        (other / "README.md").write_text("initial\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=other, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=other, check=True, stdout=subprocess.DEVNULL)
        (other / "README.md").write_text("initial\nunreviewed\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=other, check=True)

        for command in (
            f"env -C {shlex.quote(str(other))} git commit -m change",
            f"env --chdir={shlex.quote(str(other))} git commit -m change",
        ):
            with self.subTest(command=command):
                result = self.run_hook(
                    {"tool_name": "Bash", "tool_input": {"command": command}},
                    cwd=self.repo,
                )
                self.assert_pretooluse_denies(result, str(other))

    def test_wrapped_push_does_not_bypass_commit_push_composition_guard(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for cmd in (
            "git commit -m change && foo=bar git push origin main",
            "git commit -m change && command git push origin main",
            "git commit -m change && { git push origin main; }",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "commit and push", "separate shell commands")

    def test_non_executed_git_words_do_not_trigger_composition_guards(self) -> None:
        for cmd in (
            "echo git commit git push",
            "echo git tag v1.2.3 git push",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

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

    def test_release_receipt_is_invalidated_by_unstaged_and_untracked_inputs(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        self.modify_unstaged("initial\nunreviewed release input\n")
        unstaged = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "./scripts/package.sh"}}
        )
        self.assert_pretooluse_denies(unstaged, "before_release policy requires")

        self.modify_unstaged("initial\n")
        (self.repo / "UNTRACKED.txt").write_text("unreviewed package input\n", encoding="utf-8")
        untracked = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "./scripts/package.sh"}}
        )
        self.assert_pretooluse_denies(untracked, "before_release policy requires")

    def test_release_receipt_cannot_authorize_same_command_state_mutation(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "printf 'changed\\n' > README.md && ./scripts/package.sh"
                },
            }
        )

        self.assert_pretooluse_denies(result, "preceding command", "separate shell commands")

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

    def test_cd_then_bump_version_script_triggers_release_gate(self) -> None:
        result = self.run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": f"cd {self.repo} && ./scripts/bump-version.sh 1.0.0"},
            },
            cwd=self.repo.parent,
        )

        self.assert_pretooluse_denies(result, "before_release policy requires")

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

    def test_mutating_bump_version_script_triggers_release_gate(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh 1.0.0",
            "scripts/bump-version.sh 1.0.0",
            "bash scripts/bump-version.sh 1.0.0",
            "env FOO=bar ./scripts/bump-version.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_repo_local_release_commands_trigger_release_gate(self) -> None:
        for cmd in (
            "./scripts/version.sh 1.0.0",
            "./scripts/package.sh",
            "./scripts/release.sh 1.0.0",
            "./scripts/publish.sh 1.0.0",
            "./scripts/promote.sh production",
            "bash scripts/publish-release.sh 1.0.0",
            "sh tools/promote-artifact.sh production",
            "env TARGET=prod ./bin/cut-release 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_release_script_options_and_normalized_paths_do_not_bypass_gate(self) -> None:
        (self.repo / "docs").mkdir()
        for cmd in (
            "bash -x scripts/release.sh 1.0.0",
            "python3 -u scripts/release.py 1.0.0",
            "python3 -O scripts/release.py 1.0.0",
            "python3.12 -O scripts/release.py 1.0.0",
            "cd docs && ../scripts/release.sh 1.0.0",
            "./scripts/./publish.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_nested_shell_release_script_is_rejected_as_unresolved_composition(self) -> None:
        git_path = shutil.which("git")
        self.assertIsNotNone(git_path)
        for cmd in (
            "bash -c './scripts/release.sh 1.0.0'",
            "sh --command './scripts/package.sh'",
            f"bash -lc '{git_path} tag v1.2.3'",
            "bash -c 'command git commit -m change'",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "nested shell command", "directly")

    def test_generic_release_script_check_and_audit_are_not_assumed_read_only(self) -> None:
        for cmd in (
            "./scripts/release.sh --check",
            "./scripts/publish.sh --audit",
            "./tools/promote-artifact.sh --check",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_similarly_named_or_non_executed_paths_do_not_trigger_release_gate(self) -> None:
        for cmd in (
            "echo ./scripts/release.sh 1.0.0",
            "cat scripts/publish-release.sh",
            "./scripts/release-notes.sh 1.0.0",
            "./scripts/package-report.sh",
            "./tools/version-report.sh",
            "/tmp/release.sh 1.0.0",
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

    def test_gh_release_via_env_command_selector_is_remote(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        for cmd in (
            "env GH_REPO=owner/other gh release create v1.0.0",
            "env -- GH_HOST=enterprise.example.com gh release delete v1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "remote repository or host")

    def test_env_unset_clears_inherited_gh_selector(self) -> None:
        ack = subprocess.run(
            [str(HOOK), "ack", "release"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ack.returncode, 0, ack.stderr)

        result = self.run_hook(
            {"tool_name": "Bash", "tool_input": {"command": "env -u GH_REPO gh release create v1.0.0"}},
            env={"GH_REPO": "owner/other"},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_relative_git_c_after_cd_binds_to_effective_target_repo(self) -> None:
        self.stage_change("initial\nreviewed A\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory() as other_tmp:
            other = Path(other_tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "other@example.com"], cwd=other, check=True)
            subprocess.run(["git", "config", "user.name", "Other User"], cwd=other, check=True)
            (other / "README.md").write_text("initial\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=other, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=other, check=True, stdout=subprocess.DEVNULL)
            (other / "README.md").write_text("initial\nunreviewed B\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=other, check=True)
            (other / "sub").mkdir()

            result = self.run_hook(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": f"cd {other / 'sub'} && git -C .. commit -m change"},
                }
            )

        self.assert_pretooluse_denies(result, str(other))

    def test_dynamic_git_c_target_cannot_fall_back_to_current_repo_receipt(self) -> None:
        self.stage_change("initial\nreviewed current repo\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory() as other_tmp:
            other = Path(other_tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, stdout=subprocess.DEVNULL)
            result = self.run_hook(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": 'git -C "$TARGET_REPO" commit -m change'},
                },
                env={"TARGET_REPO": str(other)},
            )

        self.assert_pretooluse_denies(result, "cannot safely resolve")

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

    def test_no_python_fallback_allows_git_tag_inspection(self) -> None:
        for cmd in (
            "git tag",
            "git tag --list",
            "git tag --list v1.2.3",
            "git tag -l 'v*'",
            "git tag --points-at HEAD",
            "git tag -v v1.2.3",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")

    def test_no_python_fallback_allows_git_commit_inspection(self) -> None:
        for cmd in (
            "git log --oneline",
            "git log --grep commit",
            "git show --stat HEAD",
            "git rev-list --count HEAD",
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

    def test_no_python_fallback_allows_read_only_release_script_checks(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh --check",
            "./scripts/bump-version.sh --audit",
            "bash scripts/bump-version.sh --check",
            "bash scripts/bump-version.sh --audit",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")
                self.assertEqual(result.stdout, "")

    def test_no_python_fallback_does_not_assume_generic_check_modes_are_read_only(self) -> None:
        for cmd in (
            "./scripts/release.sh --check",
            "./scripts/publish.sh --audit",
            "bash -x tools/promote-artifact.sh --check",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_no_python_fallback_avoids_similarly_named_or_non_executed_paths(self) -> None:
        for cmd in (
            "echo ./scripts/release.sh 1.0.0",
            "cat scripts/publish-release.sh",
            "./scripts/release-notes.sh 1.0.0",
            "./scripts/package-report.sh",
            "./tools/version-report.sh",
            "/tmp/release.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assertEqual(result.returncode, 0, f"unexpected block for {cmd!r}: {result.stdout}")
                self.assertEqual(result.stdout, "")

    def test_no_python_fallback_classifies_mutating_bump_version_script(self) -> None:
        for cmd in (
            "./scripts/bump-version.sh 1.0.0",
            "scripts/bump-version.sh 1.0.0",
            "bash scripts/bump-version.sh 1.0.0",
            "env FOO=bar ./scripts/bump-version.sh 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_no_python_fallback_classifies_repo_local_release_commands(self) -> None:
        for cmd in (
            "./scripts/version.sh 1.0.0",
            "./scripts/package.sh",
            "./scripts/release.sh 1.0.0",
            "./scripts/publish.sh 1.0.0",
            "./scripts/promote.sh production",
            "bash scripts/publish-release.sh 1.0.0",
            "python3.12 -O scripts/release.py 1.0.0",
            "sh tools/promote-artifact.sh production",
            "env TARGET=prod ./bin/cut-release 1.0.0",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python({"tool_name": "Bash", "tool_input": {"command": cmd}})
                self.assert_pretooluse_denies(result, "before_release policy requires")

    def test_no_python_fallback_blocks_combined_commit_or_tag_and_push_with_receipts(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        for cmd, phrase in (
            ("git commit -m change && git push origin main", "commit and push"),
            ("git tag v1.2.3 && git push origin v1.2.3", "tag and push"),
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assert_pretooluse_denies(result, phrase, "separate shell commands")

    def test_no_python_fallback_blocks_cross_phase_compositions_with_receipts(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        for cmd in (
            "git commit -m change && git tag v1.2.3",
            "git commit -m change && ./scripts/package.sh",
            "git tag v1.2.3 && git commit -m change",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assert_pretooluse_denies(result, "protected operations", "separate shell commands")

    def test_no_python_fallback_blocks_state_changing_preludes_with_receipts(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        commit = self.run_hook_without_python(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f'{HOOK} ack commit --repo {self.repo} && git commit -m "change"'
                },
            }
        )
        self.assert_pretooluse_denies(commit, "preceding command", "separate shell commands")

        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        release = self.run_hook_without_python(
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "printf 'changed\\n' > README.md && ./scripts/package.sh"
                },
            }
        )
        self.assert_pretooluse_denies(release, "preceding command", "separate shell commands")

    def test_no_python_fallback_rejects_implicit_staging_and_pathspecs(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        for cmd in (
            "git commit --all -m change",
            "foo=bar git commit -m change README.md",
            "command git commit -am change",
            "if git commit --only README.md -m change; then :; fi",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assert_pretooluse_denies(result, "stage intended changes separately")

    def test_no_python_fallback_blocks_path_timing_newline_and_nested_bypasses(self) -> None:
        self.stage_change("initial\nchanged\n")
        git_path = shutil.which("git")
        self.assertIsNotNone(git_path)
        cases = (
            (f"{git_path} commit -m change", "before_commit policy requires"),
            ("time -p git commit -m change", "before_commit policy requires"),
            ("git status --short\ngit commit -m change", "before_commit policy requires"),
            ("bash -c './scripts/release.sh 1.0.0'", "nested shell command"),
            ("bash -lc './scripts/release.sh 1.0.0'", "nested shell command"),
            (f"env -C {shlex.quote(str(self.repo))} git commit -m change", "cannot safely resolve"),
        )

        for command, phrase in cases:
            with self.subTest(command=command):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": command}}
                )
                self.assert_pretooluse_denies(result, phrase)

    def test_no_python_fallback_treats_env_gh_selector_as_remote(self) -> None:
        subprocess.run([str(HOOK), "ack", "release"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook_without_python(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "env GH_REPO=owner/other gh release create v1.0.0"},
            }
        )

        self.assert_pretooluse_denies(result, "remote repository or host")

    def test_no_python_fallback_fails_closed_for_relative_git_c_after_cd(self) -> None:
        self.stage_change("initial\nreviewed A\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory() as other_tmp:
            other = Path(other_tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=other, check=True, stdout=subprocess.DEVNULL)
            (other / "sub").mkdir()
            result = self.run_hook_without_python(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": f"cd {other / 'sub'} && git -C .. commit -m change"},
                }
            )

        self.assert_pretooluse_denies(result, "cannot safely resolve")

    def test_no_python_fallback_ignores_non_executed_git_words(self) -> None:
        for cmd in (
            "echo git commit git push",
            "echo git tag v1.2.3 git push",
        ):
            with self.subTest(cmd=cmd):
                result = self.run_hook_without_python(
                    {"tool_name": "Bash", "tool_input": {"command": cmd}}
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

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
            "git push origin refs/tags/v1.2.3",
            "git push origin :refs/tags/v1.2.3",
            "git push --mirror origin",
            "git push origin tag release-candidate",
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
