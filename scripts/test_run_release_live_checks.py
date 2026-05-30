#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
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


class ReleaseLiveChecksTests(unittest.TestCase):
    def test_main_runs_hook_and_eval_steps_without_warn_only(self) -> None:
        runner = load_runner()
        calls = []

        def fake_run_step(name, command, env=None):
            calls.append((name, command, env))

        with patch.object(sys, "argv", ["run_release_live_checks.py"]), patch.object(
            runner,
            "run_step",
            fake_run_step,
        ):
            self.assertEqual(runner.main(), 0)

        self.assertEqual([name for name, _, _ in calls], [
            "live hook probes",
            "Codex gpt-5.5 xhigh random router eval",
            "Claude claude-opus-4-8 xhigh random router eval",
        ])
        for _, command, _ in calls:
            self.assertNotIn("--warn-only", command)
        self.assertIn("--random-specialists", calls[1][1])
        self.assertIn("10", calls[1][1])
        self.assertEqual(calls[1][2], {"CODEX_MODEL": "gpt-5.5", "CODEX_EFFORT": "xhigh"})
        self.assertEqual(
            calls[2][2],
            {"CLAUDE_MODEL": "claude-opus-4-8", "CLAUDE_EFFORT": "xhigh"},
        )

    def test_main_aborts_on_first_failing_step(self) -> None:
        runner = load_runner()
        calls = []

        def failing_run_step(name, command, env=None):
            calls.append((name, command, env))
            raise SystemExit(7)

        with patch.object(sys, "argv", ["run_release_live_checks.py"]), patch.object(
            runner,
            "run_step",
            failing_run_step,
        ):
            with self.assertRaises(SystemExit) as raised:
                runner.main()

        self.assertEqual(raised.exception.code, 7)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "live hook probes")


if __name__ == "__main__":
    unittest.main()
