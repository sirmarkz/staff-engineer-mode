#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import contextlib
import io
import json
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
                    "codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git --ref b658229b384d79227f7dd93d59cd3bdad22c75cd",
                    "codex plugin add staff-engineer-mode@staff-engineer-mode",
                    "Do not omit the `--ref` value",
                    "Skills-Only Fallback",
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
                    "```bash",
                    "git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.claude/staff-engineer-mode-marketplace",
                    "git -C ~/.claude/staff-engineer-mode-marketplace checkout --detach b658229b384d79227f7dd93d59cd3bdad22c75cd",
                    "claude plugin marketplace add ~/.claude/staff-engineer-mode-marketplace",
                    "claude plugin install staff-engineer-mode@staff-engineer-mode",
                    "```",
                    "",
                    "```text",
                    "/plugin marketplace add ~/.claude/staff-engineer-mode-marketplace",
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

    def write_minimal_claude_files(self, marketplace_sha: str) -> None:
        self.write("package.json", '{"name":"staff-engineer-mode","version":"9.9.9"}')
        self.write(
            ".claude-plugin/plugin.json",
            '{"name":"staff-engineer-mode","version":"9.9.9","description":"x","homepage":"https://github.com/sirmarkz/staff-engineer-mode"}',
        )
        self.write("skills/staff-engineer-mode/SKILL.md", "---\nname: staff-engineer-mode\n---\n")
        self.write(
            "CLAUDE.md",
            "\n".join(
                [
                    "@./skills/staff-engineer-mode/SKILL.md",
                    "Keep guidance technology-agnostic by default",
                    "specialists/<specialist-name>.md",
                    "specialists/agent-pr-review.md",
                    "specialists/release-build-reproducibility.md",
                    "specialists/production-readiness-review.md",
                    "## Bash Preflight",
                    "Do not combine staging, committing, or",
                    "Never run `git add && git commit`",
                    "reading this file, or reading `SKILL.md` is not enough",
                    "Co-Authored-By",
                    "",
                ]
            ),
        )
        self.write(
            ".claude-plugin/marketplace.json",
            json.dumps(
                {
                    "name": "staff-engineer-mode",
                    "plugins": [
                        {
                            "name": "staff-engineer-mode",
                            "version": "9.9.9",
                            "source": {
                                "source": "url",
                                "url": "https://github.com/sirmarkz/staff-engineer-mode.git",
                                "ref": "v9.9.9",
                                "sha": marketplace_sha,
                            },
                        }
                    ],
                }
            ),
        )

    def test_claude_marketplace_sha_must_match_release_tag_commit(self) -> None:
        sha = "a" * 40
        self.write_minimal_claude_files(sha)
        self.validator.git_commit = lambda ref: sha

        self.validator.validate_claude()

    def test_claude_marketplace_sha_rejects_mismatched_release_tag_commit(self) -> None:
        self.write_minimal_claude_files("b" * 40)
        self.validator.git_commit = lambda ref: "a" * 40

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_claude()

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

    def test_hooks_require_agent_event_policy_wiring(self) -> None:
        self.write(
            "skills/staff-engineer-mode/references/bootstrap-context.md",
            "\n".join(
                [
                    "SPECIALIST_ROOT={{SPECIALIST_ROOT}}",
                    "EVENT_HOOK={{EVENT_HOOK}}",
                    "CURRENT_REPO={{CURRENT_REPO}}",
                    "Read ${SPECIALIST_ROOT}/<slug>.md",
                    "Keep guidance technology-agnostic by default",
                    "agent-pr-review",
                    "release-build-reproducibility",
                    "production-readiness-review",
                    "Bash preflight",
                    "Receipt `--repo` means the local checkout root",
                    "Do not combine staging, committing, or pushing",
                    "Never run bare `ack`",
                    "Never run `git add && git commit`",
                    "reading CLAUDE.md, or reading SKILL.md is not enough",
                    "Co-Authored-By",
                    "",
                ]
            ),
        )
        self.write(
            "hooks/session-start",
            "CURSOR_PLUGIN_ROOT CLAUDE_PLUGIN_ROOT COPILOT_CLI additionalContext additional_context staff-engineer-mode skills/staff-engineer-mode/SKILL.md specialists EVENT_HOOK CURRENT_REPO\n",
        )
        self.write("hooks/run-hook.cmd", "exec bash hook\n")
        self.write("hooks/hooks-cursor.json", "{}\n")
        self.write("hooks/hooks.json", '{"hooks":{"SessionStart":[]}}\n')

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_hooks()

        self.write(
            "hooks/agent-event-policy",
            "before_commit before_release agent-pr-review release-build-reproducibility production-readiness-review\n",
        )
        self.write(
            "hooks/hooks.json",
            '{"hooks":{"SessionStart":[],"PreToolUse":[{"matcher":"Bash","hooks":[{"command":"agent-event-policy pretooluse"}]}]}}\n',
        )

        self.validator.validate_hooks()


if __name__ == "__main__":
    unittest.main()
