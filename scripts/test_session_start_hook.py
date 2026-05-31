#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION_START = ROOT / "hooks" / "session-start"
RUN_HOOK = ROOT / "hooks" / "run-hook.cmd"


class SessionStartHookTests(unittest.TestCase):
    def run_session_start(
        self,
        script: Path = SESSION_START,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.pop("CLAUDE_PLUGIN_ROOT", None)
        env.pop("CURSOR_PLUGIN_ROOT", None)
        env.pop("COPILOT_CLI", None)
        return subprocess.run(
            [str(script)],
            cwd=cwd or ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_session_start_outputs_bootstrap_context(self) -> None:
        result = self.run_session_start()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertIn("additionalContext", output)
        self.assertIsInstance(output["additionalContext"], str)
        self.assertGreater(len(output["additionalContext"]), 0)

    def test_session_start_missing_template_exits_cleanly_with_fallback_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp)
            hooks_dir = plugin_root / "hooks"
            hooks_dir.mkdir()
            script = hooks_dir / "session-start"
            shutil.copy2(SESSION_START, script)

            result = self.run_session_start(script, cwd=plugin_root)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertIn("additionalContext", output)
        self.assertIsInstance(output["additionalContext"], str)
        self.assertGreater(len(output["additionalContext"]), 0)

    def test_session_start_missing_template_reports_routed_file_availability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp)
            hooks_dir = plugin_root / "hooks"
            router_dir = plugin_root / "skills" / "staff-engineer-mode"
            specialists_dir = plugin_root / "specialists"
            hooks_dir.mkdir()
            router_dir.mkdir(parents=True)
            specialists_dir.mkdir()
            script = hooks_dir / "session-start"
            router_path = router_dir / "SKILL.md"
            shutil.copy2(SESSION_START, script)
            router_path.write_text("# Router\n", encoding="utf-8")

            result = self.run_session_start(script, cwd=plugin_root)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        context = output["additionalContext"]
        fields = {
            key: value
            for key, value in (
                line.split("=", 1)
                for line in context.splitlines()
                if "=" in line
            )
        }
        self.assertEqual(fields["ROUTER_PATH"], str(router_path))
        self.assertEqual(fields["SPECIALIST_ROOT"], str(specialists_dir))
        self.assertEqual(fields["ROUTER_STATUS"], "readable")
        self.assertEqual(fields["SPECIALIST_STATUS"], "readable")
        self.assertEqual(fields["BOOTSTRAP_STATUS"], "missing-or-unreadable")

    def test_run_hook_missing_script_exits_cleanly(self) -> None:
        result = subprocess.run(
            ["bash", str(RUN_HOOK), "does-not-exist"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_run_hook_exits_cleanly_when_path_cannot_find_shell_helpers(self) -> None:
        result = subprocess.run(
            ["/bin/sh", str(RUN_HOOK), "agent-event-policy", "pretooluse"],
            cwd=ROOT,
            env={"PATH": "/no/such"},
            input='{"tool_input":{"command":"echo ok"}}',
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_run_hook_session_start_exits_cleanly_when_path_cannot_find_shell_helpers(self) -> None:
        result = subprocess.run(
            ["/bin/sh", str(RUN_HOOK), "session-start"],
            cwd=ROOT,
            env={"PATH": "/no/such"},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertIn("additionalContext", output)
        self.assertGreater(len(output["additionalContext"]), 0)


if __name__ == "__main__":
    unittest.main()
