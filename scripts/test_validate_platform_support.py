#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "validate_platform_support.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_platform_support", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_platform_support"] = module
    spec.loader.exec_module(module)
    return module


class PlatformDocsValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.validator = load_validator()
        self.validator.ROOT = self.root
        self.write("LICENSE", "MIT License\n\nProject Notice\n")
        self.write(
            ".codex/INSTALL.md",
            "\n".join(
                [
                    "~/.agents/skills/staff-engineer-mode",
                    "ln -s ~/.codex/staff-engineer-mode/skills ~/.agents/skills/staff-engineer-mode",
                    "specialists/<slug>.md",
                    "",
                ]
            ),
        )

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_readme_accepts_https_git_marketplace_add(self) -> None:
        self.write(
            "README.md",
            "\n".join(
                [
                    "# Staff Engineer Mode",
                    "",
                    "```text",
                    "/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git",
                    "```",
                    "",
                    "```text",
                    "/plugin install staff-engineer-mode@staff-engineer-mode",
                    "```",
                    "",
                    "```bash",
                    "copilot plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git",
                    "```",
                    "",
                    "```bash",
                    "copilot plugin install staff-engineer-mode@staff-engineer-mode",
                    "```",
                    "",
                ]
            ),
        )

        self.validator.validate_docs()

    def test_readme_rejects_claude_github_shorthand_marketplace_add(self) -> None:
        self.write(
            "README.md",
            "\n".join(
                [
                    "# Staff Engineer Mode",
                    "",
                    "```text",
                    "/plugin marketplace add sirmarkz/staff-engineer-mode",
                    "```",
                    "",
                ]
            ),
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_docs()

    def test_readme_rejects_https_marketplace_add_without_git_suffix(self) -> None:
        self.write(
            "README.md",
            "\n".join(
                [
                    "# Staff Engineer Mode",
                    "",
                    "```text",
                    "/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode",
                    "/plugin install staff-engineer-mode@staff-engineer-mode",
                    "```",
                    "",
                ]
            ),
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_docs()

    def test_plugin_install_paths_accept_https_urls(self) -> None:
        self.write(
            ".claude-plugin/marketplace.json",
            '{"plugins":[{"source":{"source":"url","url":"https://github.com/sirmarkz/staff-engineer-mode.git"}}]}',
        )
        self.write(
            ".opencode/INSTALL.md",
            '"plugin": ["staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git"]',
        )
        self.write(
            "README.md",
            "/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git\n",
        )

        self.validator.validate_https_plugin_install_paths()

    def test_plugin_install_paths_reject_ssh_urls(self) -> None:
        self.write(
            ".cursor-plugin/INSTALL.md",
            "git clone git@github.com:sirmarkz/staff-engineer-mode.git\n",
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_https_plugin_install_paths()


if __name__ == "__main__":
    unittest.main()
