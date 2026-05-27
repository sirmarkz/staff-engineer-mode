#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "agent-event-policy"


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

    def run_hook(self, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(HOOK), "pretooluse"],
            cwd=self.repo,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def stage_change(self, content: str) -> None:
        (self.repo / "README.md").write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.repo, check=True)

    def test_commit_command_blocks_without_review_receipt(self) -> None:
        self.stage_change("initial\nchanged\n")

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -m change"}})

        self.assertEqual(result.returncode, 2)
        response = json.loads(result.stdout)
        self.assertEqual(response["decision"], "block")
        self.assertIn("agent-pr-review", response["reason"])

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
        self.assertEqual(blocked.returncode, 2)

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

    def test_commit_all_is_blocked_so_review_binds_to_staged_diff(self) -> None:
        self.stage_change("initial\nchanged\n")
        subprocess.run([str(HOOK), "ack", "commit"], cwd=self.repo, check=True, stdout=subprocess.DEVNULL)

        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git commit -am change"}})

        self.assertEqual(result.returncode, 2)
        response = json.loads(result.stdout)
        self.assertIn("stage intended changes", response["reason"].lower())

    def test_release_command_blocks_without_release_receipt(self) -> None:
        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git tag v1.2.3"}})

        self.assertEqual(result.returncode, 2)
        response = json.loads(result.stdout)
        self.assertEqual(response["decision"], "block")
        self.assertIn("release-build-reproducibility", response["reason"])

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


if __name__ == "__main__":
    unittest.main()
