#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bump-version.sh"


class BumpVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / ".gitignore").write_text("docs/\ndecisions/\n", encoding="utf-8")
        (self.root / "scripts").mkdir()
        shutil.copy2(SCRIPT, self.root / "scripts" / "bump-version.sh")
        self.write_json(
            ".version-bump.json",
            {
                "files": [
                    {"path": "package.json", "field": "version"},
                    {"path": ".codex-plugin/plugin.json", "field": "version"},
                    {"path": "gemini-extension.json", "field": "version"},
                    {
                        "path": ".claude-plugin/marketplace.json",
                        "field": "plugins.0.source.ref",
                        "format": "v{version}",
                    },
                ],
                "audit": {"exclude": []},
            },
        )
        self.write_json("package.json", {"version": "1.0.0"})
        self.write_json(".codex-plugin/plugin.json", {"version": "1.0.0"})
        self.write_json("gemini-extension.json", {"version": "1.0.0"})
        self.write_json(".claude-plugin/marketplace.json", {"plugins": [{"source": {"ref": "v1.0.0"}}]})

    def write_json(self, relative: str, content: object) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content) + "\n", encoding="utf-8")

    def read_json(self, relative: str) -> object:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", "scripts/bump-version.sh", *args],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_audit_fails_when_declared_versions_drift(self) -> None:
        self.write_json(".codex-plugin/plugin.json", {"version": "9.9.9"})

        result = self.run_script("--audit")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".codex-plugin/plugin.json", result.stdout)
        self.assertIn("9.9.9", result.stdout)
        self.assertIn("1.0.0", result.stdout)
        self.assertEqual(
            self.read_json(".codex-plugin/plugin.json"), {"version": "9.9.9"}
        )
        self.assertEqual(self.read_json("package.json"), {"version": "1.0.0"})

    def test_bump_rejects_version_suffix(self) -> None:
        result = self.run_script("1.2.3oops")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.read_json("package.json"), {"version": "1.0.0"})

    def test_audit_applies_basename_exclusions_at_any_depth(self) -> None:
        config = self.read_json(".version-bump.json")
        assert isinstance(config, dict)
        config["audit"] = {"exclude": ["package-lock.json"]}
        self.write_json(".version-bump.json", config)
        lockfile = self.root / "packages" / "demo" / "package-lock.json"
        lockfile.parent.mkdir(parents=True)
        lockfile.write_text('{"version":"1.0.0"}\n', encoding="utf-8")

        result = self.run_script("--audit")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_audit_excludes_generated_evidence_subtree(self) -> None:
        config = self.read_json(".version-bump.json")
        assert isinstance(config, dict)
        config["audit"] = {"exclude": ["evals/runs"]}
        self.write_json(".version-bump.json", config)
        evidence = self.root / "evals" / "runs" / "probe.log"
        evidence.parent.mkdir(parents=True)
        evidence.write_text("generated with 1.0.0\n", encoding="utf-8")

        result = self.run_script("--audit")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_audit_honors_repository_ignore_rules(self) -> None:
        for relative in ("docs/draft.md", "decisions/choice.md"):
            path = self.root / relative
            path.parent.mkdir(exist_ok=True)
            path.write_text("scratch record for 1.0.0\n", encoding="utf-8")

        result = self.run_script("--audit")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
