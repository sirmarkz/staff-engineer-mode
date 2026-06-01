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
        self.assertIn("DRIFT DETECTED", result.stdout)

    def test_bump_rejects_version_suffix(self) -> None:
        result = self.run_script("1.2.3oops")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.read_json("package.json"), {"version": "1.0.0"})


if __name__ == "__main__":
    unittest.main()
