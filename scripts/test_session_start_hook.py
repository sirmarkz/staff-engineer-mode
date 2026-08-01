#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION_START = ROOT / "hooks" / "session-start"
RUN_HOOK = ROOT / "hooks" / "run-hook.cmd"
AGENT_EVENT_POLICY = ROOT / "hooks" / "agent-event-policy"


class SessionStartHookTests(unittest.TestCase):
    @staticmethod
    def context_fields(context: str) -> dict[str, str]:
        return {
            key: value
            for key, value in (
                (part.strip() for part in line.split("=", 1))
                for line in context.splitlines()
                if "=" in line
            )
        }

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

    def test_session_start_context_survives_linebreak_collapse(self) -> None:
        result = self.run_session_start()

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        context = output["additionalContext"]
        collapsed = context.replace("\n", "")

        fields = self.context_fields(context)
        self.assertEqual(
            set(fields),
            {"SPECIALIST_ROOT", "TEMPLATE_ROOT", "ROUTER_PATH", "EVENT_HOOK", "CURRENT_REPO"},
        )
        for key, value in fields.items():
            self.assertIn(f"{key}={value}", collapsed)
        self.assertTrue(
            all(line.endswith(" ") for line in context.splitlines()[:-1]),
            "every removed line break must leave a token separator",
        )
        self.assertNotIn("{{", context)
        self.assertNotIn("}}", context)

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
        fields = self.context_fields(context)
        self.assertEqual(fields["ROUTER_PATH"], str(router_path))
        self.assertEqual(fields["SPECIALIST_ROOT"], str(specialists_dir))
        self.assertEqual(
            fields["TEMPLATE_ROOT"],
            str(plugin_root / "skills" / "_shared" / "assets" / "templates"),
        )
        self.assertEqual(fields["ROUTER_STATUS"], "readable")
        self.assertEqual(fields["SPECIALIST_STATUS"], "readable")
        self.assertEqual(fields["BOOTSTRAP_STATUS"], "missing-or-unreadable")
        self.assertEqual(fields["TEMPLATE_STATUS"], "missing-or-unreadable")

    def test_session_start_falls_back_when_template_directory_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp)
            hooks_dir = plugin_root / "hooks"
            router_dir = plugin_root / "skills" / "staff-engineer-mode"
            specialists_dir = plugin_root / "specialists"
            bootstrap_dir = router_dir / "references"
            hooks_dir.mkdir()
            bootstrap_dir.mkdir(parents=True)
            specialists_dir.mkdir()
            script = hooks_dir / "session-start"
            shutil.copy2(SESSION_START, script)
            (router_dir / "SKILL.md").write_text("# Router\n", encoding="utf-8")
            (bootstrap_dir / "bootstrap-context.md").write_text(
                "SPECIALIST_ROOT={{SPECIALIST_ROOT}}\nTEMPLATE_ROOT={{TEMPLATE_ROOT}}\n"
                "ROUTER_PATH={{ROUTER_PATH}}\nEVENT_HOOK={{EVENT_HOOK}}\n"
                "CURRENT_REPO={{CURRENT_REPO}}\n{{TOOL_MAPPING}}\n",
                encoding="utf-8",
            )

            result = self.run_session_start(script, cwd=plugin_root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        context = json.loads(result.stdout)["additionalContext"]
        fields = self.context_fields(context)
        self.assertEqual(
            fields["TEMPLATE_ROOT"],
            str(plugin_root / "skills" / "_shared" / "assets" / "templates"),
        )
        self.assertEqual(fields["ROUTER_STATUS"], "readable")
        self.assertEqual(fields["BOOTSTRAP_STATUS"], "readable")
        self.assertEqual(fields["SPECIALIST_STATUS"], "readable")
        self.assertEqual(fields["TEMPLATE_STATUS"], "missing-or-unreadable")
        self.assertEqual(fields["EVENT_HOOK_STATUS"], "missing-or-unreadable")

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

    def test_run_hook_ignores_posix_shell_from_bash_environment(self) -> None:
        env = os.environ.copy()
        env["BASH"] = "/bin/sh"
        result = subprocess.run(
            ["/bin/sh", str(RUN_HOOK), "agent-event-policy", "pretooluse"],
            cwd=ROOT,
            env=env,
            input='{"tool_input":{"command":"echo ok"}}',
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, "")

    def test_run_hook_ignores_shell_candidates_from_bash_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hooks_dir = Path(tmp)
            wrapper = hooks_dir / "run-hook.cmd"
            probe = hooks_dir / "probe"
            non_bash = hooks_dir / "not-bash"
            shutil.copy2(RUN_HOOK, wrapper)
            probe.write_text(
                "[ -n \"${BASH_VERSION:-}\" ] || exit 70\n"
                "case \"${BASH:-}\" in \"\"|sh|*/sh) exit 71 ;; esac\n"
                "if shopt -qo posix; then exit 72; fi\n"
                "printf 'normal-bash\\n'\n",
                encoding="utf-8",
            )
            non_bash.write_text("#!/bin/sh\nexit 73\n", encoding="utf-8")
            non_bash.chmod(0o755)

            for candidate in ("/bin/sh", str(non_bash)):
                with self.subTest(candidate=candidate):
                    env = os.environ.copy()
                    env["BASH"] = candidate
                    result = subprocess.run(
                        ["/bin/sh", str(wrapper), "probe"],
                        cwd=ROOT,
                        env=env,
                        text=True,
                        capture_output=True,
                        check=False,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertEqual(result.stdout, "normal-bash\n")

    @unittest.skipUnless(sys.platform == "darwin", "requires the macOS system shell")
    def test_agent_event_policy_parses_with_macos_system_shell(self) -> None:
        result = subprocess.run(
            ["/bin/sh", "-n", str(AGENT_EVENT_POLICY)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

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
