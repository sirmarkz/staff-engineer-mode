#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_release_live_checks.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_release_live_checks", RUNNER)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load run_release_live_checks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command_options(command: list[str]) -> dict[str, list[str | None]]:
    options: dict[str, list[str | None]] = {}
    index = 0
    while index < len(command):
        token = command[index]
        if not token.startswith("--"):
            index += 1
            continue
        value: str | None = None
        if index + 1 < len(command) and not command[index + 1].startswith("--"):
            value = command[index + 1]
            index += 1
        options.setdefault(token, []).append(value)
        index += 1
    return options


class ReleaseLiveChecksTests(unittest.TestCase):
    def test_release_gate_rejects_model_and_effort_overrides(self) -> None:
        runner = load_runner()

        for flag, value in (
            ("--codex-model", "alternate-codex-model"),
            ("--claude-model", "alternate-claude-model"),
            ("--hook-effort", "medium"),
            ("--eval-effort", "medium"),
        ):
            with self.subTest(flag=flag), patch.object(
                sys,
                "argv",
                ["run_release_live_checks.py", flag, value],
            ):
                with self.assertRaises(SystemExit):
                    runner.parse_args()

    def test_main_runs_hook_and_eval_steps_without_warn_only(self) -> None:
        runner = load_runner()
        calls = []
        random_specialists = 3

        def fake_run_step(name, command, env=None):
            calls.append((name, command, env))

        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"
            with patch.object(
                sys,
                "argv",
                [
                    "run_release_live_checks.py",
                    "--evidence-dir",
                    str(evidence),
                    "--random-specialists",
                    str(random_specialists),
                ],
            ), patch.object(runner, "run_step", fake_run_step):
                self.assertEqual(runner.main(), 0)

        self.assertEqual(
            [command[1] for _, command, _ in calls],
            [
                "scripts/validate_platform_support.py",
                "scripts/validate_router_eval.py",
                "scripts/test_agent_event_policy_hook.py",
                "scripts/run_live_hook_probes.py",
                *(["scripts/run_router_eval.py"] * 6),
            ],
        )
        for _, command, _ in calls:
            self.assertNotIn("--warn-only", command_options(command))

        hook_options = command_options(calls[3][1])
        self.assertNotIn("--timeout", hook_options)
        self.assertEqual(hook_options["--codex-model"], ["gpt-5.6-terra"])
        self.assertEqual(hook_options["--claude-model"], ["claude-opus-4-8"])
        self.assertEqual(hook_options["--codex-effort"], ["high"])
        self.assertEqual(hook_options["--claude-effort"], ["high"])
        self.assertEqual(
            Path(hook_options["--work-dir"][0]).parent,
            evidence,
        )

        eval_calls = calls[4:]
        catalogs = [
            command_options(command)["--catalog"][0]
            for _, command, _ in eval_calls
        ]
        self.assertEqual(catalogs, ["positive", "boundary", "contract"] * 2)
        positive_options = command_options(eval_calls[0][1])
        self.assertEqual(
            positive_options["--random-specialists"],
            [str(random_specialists)],
        )
        contract_options = command_options(eval_calls[2][1])
        self.assertNotIn("--stratified-categories", contract_options)
        self.assertEqual(
            set(contract_options["--check-cover"]),
            {
                "capability_translation",
                "ambiguity_check",
                "scope_check",
                "secondary_cap",
            },
        )
        self.assertEqual(
            eval_calls[0][2],
            {"CODEX_MODEL": "gpt-5.6-terra", "CODEX_EFFORT": "high"},
        )
        self.assertEqual(
            eval_calls[3][2],
            {"CLAUDE_MODEL": "claude-opus-4-8", "CLAUDE_EFFORT": "high"},
        )
        result_dirs = [
            Path(command_options(command)["--results-dir"][0])
            for _name, command, _env in eval_calls
        ]
        self.assertEqual(len(set(result_dirs)), len(result_dirs))
        self.assertTrue(all(path.parent == evidence for path in result_dirs))

    def test_main_aborts_on_first_failing_step(self) -> None:
        runner = load_runner()
        calls = []
        failure_code = 7

        def failing_run_step(name, command, env=None):
            calls.append((name, command, env))
            raise SystemExit(failure_code)

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sys,
            "argv",
            ["run_release_live_checks.py", "--evidence-dir", str(Path(tmp) / "evidence")],
        ), patch.object(
            runner,
            "run_step",
            failing_run_step,
        ):
            with self.assertRaises(SystemExit) as raised:
                runner.main()

        self.assertEqual(raised.exception.code, failure_code)
        self.assertEqual(
            [command[1] for _name, command, _env in calls],
            ["scripts/validate_platform_support.py"],
        )

    def test_explicit_timeout_is_forwarded_to_hook_probe(self) -> None:
        runner = load_runner()
        calls = []
        timeout = 15

        def fake_run_step(name, command, env=None):
            calls.append((name, command, env))

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sys,
            "argv",
            [
                "run_release_live_checks.py",
                "--timeout",
                str(timeout),
                "--evidence-dir",
                str(Path(tmp) / "evidence"),
            ],
        ), patch.object(runner, "run_step", fake_run_step):
            self.assertEqual(runner.main(), 0)

        hook_call = next(
            command
            for _name, command, _env in calls
            if command[1] == "scripts/run_live_hook_probes.py"
        )
        self.assertEqual(command_options(hook_call)["--timeout"], [str(timeout)])

    def test_eval_case_timeout_is_forwarded_to_every_router_run(self) -> None:
        runner = load_runner()
        calls = []
        timeout = 37

        def fake_run_step(name, command, env=None):
            calls.append((name, command, env))

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sys,
            "argv",
            [
                "run_release_live_checks.py",
                "--eval-case-timeout",
                str(timeout),
                "--evidence-dir",
                str(Path(tmp) / "evidence"),
            ],
        ), patch.object(runner, "run_step", fake_run_step):
            self.assertEqual(runner.main(), 0)

        router_commands = [
            command
            for _name, command, _env in calls
            if command[1] == "scripts/run_router_eval.py"
        ]
        self.assertTrue(router_commands)
        for command in router_commands:
            self.assertEqual(
                command_options(command)["--case-timeout"],
                [str(timeout)],
            )

    def test_evidence_directory_is_reserved_before_any_live_step(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "evidence"
            evidence.mkdir()
            with patch.object(
                sys,
                "argv",
                ["run_release_live_checks.py", "--evidence-dir", str(evidence)],
            ), patch.object(runner, "run_step") as run_step:
                with self.assertRaises(SystemExit):
                    runner.main()

            run_step.assert_not_called()

    def test_invalid_selection_controls_fail_before_evidence_or_live_steps(self) -> None:
        runner = load_runner()

        for flag in (
            "--jobs",
            "--random-specialists",
            "--eval-case-timeout",
            "--timeout",
        ):
            with self.subTest(flag=flag), patch.object(
                sys,
                "argv",
                ["run_release_live_checks.py", flag, "0"],
            ), patch.object(runner, "reserve_evidence_dir") as reserve, patch.object(
                runner, "run_step"
            ) as run_step:
                with self.assertRaises(SystemExit):
                    runner.main()
                reserve.assert_not_called()
                run_step.assert_not_called()


if __name__ == "__main__":
    unittest.main()
