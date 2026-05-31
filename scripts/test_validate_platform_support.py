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
        self.write_valid_install_docs()

    def write_valid_install_docs(self) -> None:
        self.write(
            ".codex/INSTALL.md",
            "\n".join(
                [
                    "~/.agents/skills/staff-engineer-mode",
                    "ln -s ~/.codex/staff-engineer-mode/skills ~/.agents/skills/staff-engineer-mode",
                    "codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git",
                    "codex plugin add staff-engineer-mode@staff-engineer-mode",
                    "Skills-Only Fallback",
                    "specialists/<slug>.md",
                    "",
                ]
            ),
        )
        self.write(
            ".opencode/INSTALL.md",
            "\n".join(
                [
                    "opencode plugin 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git'",
                    "",
                ]
            ),
        )
        self.write(".cursor-plugin/INSTALL.md", "Cursor local installation\n")

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_valid_readme(self) -> None:
        self.write(
            "README.md",
            "\n".join(
                [
                    "# Staff Engineer Mode",
                    "",
                    "```bash",
                    "claude plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git",
                    "claude plugin install staff-engineer-mode@staff-engineer-mode",
                    "```",
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
                    "codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git",
                    "```",
                    "",
                    "```bash",
                    "opencode plugin 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git'",
                    "```",
                    "",
                    "```bash",
                    "git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.cursor/staff-engineer-mode-src",
                    "mkdir -p ~/.cursor/plugins",
                    "ln -s ~/.cursor/staff-engineer-mode-src ~/.cursor/plugins/staff-engineer-mode",
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

    def test_readme_accepts_https_git_marketplace_add(self) -> None:
        self.write_valid_readme()

        self.validator.validate_docs()

    def test_docs_reject_removed_install_paths(self) -> None:
        cases = [
            (
                "manual Claude marketplace checkout",
                lambda: self.write(
                    "README.md",
                    (self.root / "README.md").read_text() + "staff-engineer-mode-marketplace\n",
                ),
            ),
            (
                "Cursor marketplace slash command in README",
                lambda: self.write(
                    "README.md",
                    (self.root / "README.md").read_text() + "/add-plugin staff-engineer-mode\n",
                ),
            ),
            (
                "Cursor marketplace claim",
                lambda: self.write(
                    ".cursor-plugin/INSTALL.md",
                    (self.root / ".cursor-plugin" / "INSTALL.md").read_text() + "Cursor Plugin Marketplace\n",
                ),
            ),
            (
                "Codex marketplace ref pin",
                lambda: self.write(
                    ".codex/INSTALL.md",
                    (self.root / ".codex" / "INSTALL.md").read_text().replace(
                        "codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git",
                        "codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git --ref abc",
                        1,
                    ),
                ),
            ),
            (
                "OpenCode commit pin",
                lambda: self.write(
                    ".opencode/INSTALL.md",
                    (self.root / ".opencode" / "INSTALL.md").read_text()
                    + "opencode plugin 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git#abc'\n",
                ),
            ),
        ]

        for name, mutate in cases:
            with self.subTest(name=name):
                self.write_valid_readme()
                self.write_valid_install_docs()
                mutate()
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
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
                    "# Staff Engineer Mode",
                    "",
                    "@AGENTS.md",
                    "@./skills/staff-engineer-mode/SKILL.md",
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

    def test_agents_requires_release_version_format_rule(self) -> None:
        self.write("AGENTS.md", "## Git And Commit Rules\n")

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_agents_release_policy()

        self.write(
            "AGENTS.md",
            "\n".join(
                [
                    "## Git And Commit Rules",
                    "- Release tags and hosted GitHub release titles must both be exactly `vX.Y.Z`.",
                    "- `RELEASE-NOTES.md` headings keep the plain `X.Y.Z - YYYY-MM-DD` format.",
                    "- Do not commit local memory exports such as `<claude-mem-context>`.",
                    "",
                ]
            ),
        )

        self.validator.validate_agents_release_policy()

    def test_hooks_require_agent_event_policy_wiring(self) -> None:
        self.write(
            "skills/staff-engineer-mode/references/bootstrap-context.md",
            "\n".join(
                [
                    "SPECIALIST_ROOT={{SPECIALIST_ROOT}}",
                    "ROUTER_PATH={{ROUTER_PATH}}",
                    "EVENT_HOOK={{EVENT_HOOK}}",
                    "CURRENT_REPO={{CURRENT_REPO}}",
                    "load the native `staff-engineer-mode` router",
                    "Read `${ROUTER_PATH}`",
                    "Router load alone is not enough",
                    "Read `${SPECIALIST_ROOT}/<slug>.md`",
                    "before any repo file",
                    "Do not parallel-load router and repo files",
                    "never call `Skill staff-engineer-mode:<slug>`",
                    "Read `${SPECIALIST_ROOT}/agent-pr-review.md` before code-review",
                    "Keep guidance technology-agnostic by default",
                    "agent-pr-review",
                    "release-build-reproducibility",
                    "production-readiness-review",
                    "Do not combine stage/commit/push",
                    "",
                ]
            ),
        )
        self.write(
            "hooks/session-start",
            "CURSOR_PLUGIN_ROOT CLAUDE_PLUGIN_ROOT COPILOT_CLI additionalContext additional_context staff-engineer-mode skills/staff-engineer-mode/SKILL.md specialists ROUTER_PATH EVENT_HOOK CURRENT_REPO\n",
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
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {
                                "hooks": [
                                    {
                                        "command": '"${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/hooks/run-hook.cmd" session-start',
                                    }
                                ]
                            }
                        ],
                        "PreToolUse": [
                            {
                                "matcher": "Bash",
                                "hooks": [
                                    {
                                        "command": '"${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/hooks/run-hook.cmd" agent-event-policy pretooluse',
                                    }
                                ],
                            }
                        ],
                    }
                }
            ),
        )

        self.validator.validate_hooks()

    def test_hooks_require_codex_plugin_root_fallback(self) -> None:
        self.write(
            "skills/staff-engineer-mode/references/bootstrap-context.md",
            "\n".join(
                [
                    "SPECIALIST_ROOT={{SPECIALIST_ROOT}}",
                    "ROUTER_PATH={{ROUTER_PATH}}",
                    "EVENT_HOOK={{EVENT_HOOK}}",
                    "CURRENT_REPO={{CURRENT_REPO}}",
                    "load the native `staff-engineer-mode` router",
                    "Read `${ROUTER_PATH}`",
                    "Router load alone is not enough",
                    "Read `${SPECIALIST_ROOT}/<slug>.md`",
                    "before any repo file",
                    "Do not parallel-load router and repo files",
                    "never call `Skill staff-engineer-mode:<slug>`",
                    "Read `${SPECIALIST_ROOT}/agent-pr-review.md` before code-review",
                    "Keep guidance technology-agnostic by default",
                    "agent-pr-review",
                    "release-build-reproducibility",
                    "production-readiness-review",
                    "Do not combine stage/commit/push",
                    "",
                ]
            ),
        )
        self.write(
            "hooks/session-start",
            "CURSOR_PLUGIN_ROOT CLAUDE_PLUGIN_ROOT COPILOT_CLI additionalContext additional_context staff-engineer-mode skills/staff-engineer-mode/SKILL.md specialists ROUTER_PATH EVENT_HOOK CURRENT_REPO\n",
        )
        self.write("hooks/run-hook.cmd", "exec bash hook\n")
        self.write("hooks/hooks-cursor.json", "{}\n")
        self.write(
            "hooks/agent-event-policy",
            "before_commit before_release agent-pr-review release-build-reproducibility production-readiness-review\n",
        )
        self.write(
            "hooks/hooks.json",
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {
                                "hooks": [
                                    {
                                        "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start',
                                    }
                                ]
                            }
                        ],
                        "PreToolUse": [
                            {
                                "matcher": "Bash",
                                "hooks": [
                                    {
                                        "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" agent-event-policy pretooluse',
                                    }
                                ],
                            }
                        ],
                    }
                }
            ),
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_hooks()

        self.write(
            "hooks/hooks.json",
            json.dumps(
                {
                    "hooks": {
                        "SessionStart": [
                            {
                                "hooks": [
                                    {
                                        "command": '"${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/hooks/run-hook.cmd" session-start',
                                    }
                                ]
                            }
                        ],
                        "PreToolUse": [
                            {
                                "matcher": "Bash",
                                "hooks": [
                                    {
                                        "command": '"${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/hooks/run-hook.cmd" agent-event-policy pretooluse',
                                    }
                                ],
                            }
                        ],
                    }
                }
            ),
        )

        self.validator.validate_hooks()


if __name__ == "__main__":
    unittest.main()
