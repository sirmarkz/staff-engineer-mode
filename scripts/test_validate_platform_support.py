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

    def repository_text(self, relative: str) -> str:
        return (SCRIPT.parents[1] / relative).read_text(encoding="utf-8")

    def write_valid_bootstrap_context(self) -> None:
        relative = str(self.validator.BOOTSTRAP_TEMPLATE_RELATIVE)
        self.write(relative, self.repository_text(relative))

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

    def test_agents_release_policy_requires_stable_format_tokens(self) -> None:
        self.write("AGENTS.md", "## Git And Commit Rules\n")

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_agents_release_policy()

        policy = self.repository_text("AGENTS.md")
        self.write("AGENTS.md", policy)
        self.validator.validate_agents_release_policy()

        for token in ("`vX.Y.Z`", "`X.Y.Z - YYYY-MM-DD`", "`<claude-mem-context>`"):
            with self.subTest(token=token):
                self.assertIn(token, policy)
                self.write("AGENTS.md", policy.replace(token, "", 1))
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        self.validator.validate_agents_release_policy()

    def test_hooks_require_agent_event_policy_wiring(self) -> None:
        self.write_valid_bootstrap_context()
        self.write(
            "hooks/session-start",
            "CURSOR_PLUGIN_ROOT CLAUDE_PLUGIN_ROOT COPILOT_CLI additionalContext additional_context staff-engineer-mode skills/staff-engineer-mode/SKILL.md specialists ROUTER_PATH TEMPLATE_ROOT EVENT_HOOK CURRENT_REPO\n",
        )
        self.write("hooks/run-hook.cmd", "exec bash hook\n")
        self.write(
            "hooks/hooks-cursor.json",
            json.dumps(
                {
                    "version": 1,
                    "hooks": {
                        "sessionStart": [
                            {"command": "./hooks/run-hook.cmd session-start"},
                        ]
                    },
                }
            ),
        )
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

        self.write(
            "hooks/hooks-cursor.json",
            json.dumps(
                {
                    "version": 1,
                    "hooks": {
                        "sessionStart": [
                            {"command": "./hooks/session-start"},
                        ]
                    },
                }
            ),
        )
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_hooks()

    def test_hooks_require_codex_plugin_root_fallback(self) -> None:
        self.write_valid_bootstrap_context()
        self.write(
            "hooks/session-start",
            "CURSOR_PLUGIN_ROOT CLAUDE_PLUGIN_ROOT COPILOT_CLI additionalContext additional_context staff-engineer-mode skills/staff-engineer-mode/SKILL.md specialists ROUTER_PATH TEMPLATE_ROOT EVENT_HOOK CURRENT_REPO\n",
        )
        self.write("hooks/run-hook.cmd", "exec bash hook\n")
        self.write(
            "hooks/hooks-cursor.json",
            json.dumps(
                {
                    "version": 1,
                    "hooks": {
                        "sessionStart": [
                            {"command": "./hooks/run-hook.cmd session-start"},
                        ]
                    },
                }
            ),
        )
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

    def test_ci_workflow_requires_script_globs_and_test_discovery(self) -> None:
        self.write(
            ".github/workflows/validation.yml",
            "\n".join(
                [
                    "pull_request:",
                    "push:",
                    "python3 -m py_compile",
                    "scripts/run_router_eval.py",
                    "scripts/test_run_router_eval.py",
                    "scripts/test_agent_event_policy_hook.py",
                    "scripts/test_session_start_hook.py",
                    "scripts/test_validate_platform_support.py",
                    "bash -n hooks/agent-event-policy",
                    "bash -n hooks/session-start",
                    "bash -n hooks/run-hook.cmd",
                    "bash -n evals/adapters/codex-router.sh",
                    "bash -n evals/adapters/codex-specialist.sh",
                    "bash -n evals/adapters/claude-router.sh",
                    "bash -n scripts/bump-version.sh",
                    "python3 -m unittest scripts/test_run_router_eval.py",
                    "python3 -m unittest scripts/test_agent_event_policy_hook.py",
                    "python3 -m unittest scripts/test_session_start_hook.py",
                    "python3 -m unittest scripts/test_validate_platform_support.py",
                    "scripts/bump-version.sh --check",
                    "scripts/bump-version.sh --audit",
                    "python3 scripts/validate_source_quality.py",
                    "python3 scripts/validate_skill_pack.py",
                    "python3 scripts/validate_router_eval.py",
                    "python3 scripts/validate_platform_support.py",
                    "node --check .opencode/plugins/staff-engineer-mode.js",
                    "git grep -nI '[[:blank:]]$' -- .",
                    "",
                ]
            ),
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_ci_workflow()

    def test_ci_workflow_accepts_full_script_and_test_discovery(self) -> None:
        self.write(
            ".github/workflows/validation.yml",
            "\n".join(
                [
                    "pull_request:",
                    "push:",
                    "python3 -m py_compile scripts/*.py",
                    "bash -n hooks/agent-event-policy",
                    "bash -n hooks/session-start",
                    "bash -n hooks/run-hook.cmd",
                    "bash -n evals/adapters/codex-router.sh",
                    "bash -n evals/adapters/codex-specialist.sh",
                    "bash -n evals/adapters/claude-router.sh",
                    "bash -n scripts/bump-version.sh",
                    "python3 -m unittest discover -s scripts -p 'test_*.py'",
                    "scripts/bump-version.sh --check",
                    "scripts/bump-version.sh --audit",
                    "python3 scripts/validate_source_quality.py",
                    "python3 scripts/validate_skill_pack.py",
                    "python3 scripts/validate_router_eval.py",
                    "python3 scripts/validate_platform_support.py",
                    "python3 scripts/validate_markdown_links.py",
                    "node --check .opencode/plugins/staff-engineer-mode.js",
                    "git grep -nI '[[:blank:]]$' -- .",
                    "permissions:",
                    "  contents: read",
                    "uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4",
                    "uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5",
                    "uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4",
                    "",
                ]
            ),
        )

        self.validator.validate_ci_workflow()

    def test_action_security_rejects_mutable_tags_and_implicit_permissions(self) -> None:
        path = self.root / ".github/workflows/validation.yml"
        text = "uses: actions/checkout@v4\n"

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_action_security(text, path)

    def test_action_security_rejects_permission_evasions_and_job_overrides(self) -> None:
        path = self.root / ".github/workflows/validation.yml"
        cases = (
            "permissions: write-all\njobs:\n  build:\n    steps:\n      - run: |\n          contents: read\n",
            "permissions:\n  contents: read\n  issues: write\n",
            "permissions:\n  contents: read\njobs:\n  build:\n    permissions:\n      contents: write\n",
        )

        for text in cases:
            with self.subTest(text=text), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.validator.validate_action_security(text, path)

    def test_action_security_ignores_action_like_text_inside_block_scalars(self) -> None:
        path = self.root / ".github/workflows/validation.yml"
        text = "\n".join(
            [
                "permissions:",
                "  contents: read",
                "jobs:",
                "  build:",
                "    steps:",
                "      - run: |",
                "          uses: actions/checkout@v4",
                "          permissions: write-all",
                "",
            ]
        )

        self.validator.validate_action_security(text, path)

    def test_action_security_parses_spaced_uses_and_flow_permissions(self) -> None:
        path = self.root / ".github/workflows/validation.yml"
        text = "permissions: { contents: read }\njobs:\n  build:\n    steps:\n      - uses : actions/checkout@v4\n"

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_action_security(text, path)

        pinned = text.replace("@v4", "@" + "a" * 40)
        self.validator.validate_action_security(pinned, path)

    def test_action_security_rejects_nested_flow_style_bypasses(self) -> None:
        path = self.root / ".github/workflows/validation.yml"
        cases = (
            "permissions: {contents: read}\njobs:\n  build:\n    steps: [{ uses: actions/checkout@v4 }]\n",
            "permissions: {contents: read}\njobs: {build: {permissions: write-all}}\n",
        )

        for text in cases:
            with self.subTest(text=text), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.validator.validate_action_security(text, path)

    def test_ci_workflow_scans_yaml_extension_files(self) -> None:
        source_workflow = SCRIPT.parents[1] / ".github" / "workflows" / "validation.yml"
        self.write(".github/workflows/validation.yml", source_workflow.read_text(encoding="utf-8"))
        self.write(
            ".github/workflows/unpinned.yaml",
            "permissions:\n  contents: read\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n",
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_ci_workflow()

    def test_opencode_requires_every_bootstrap_placeholder_to_be_rendered(self) -> None:
        self.write(
            "package.json",
            json.dumps(
                {
                    "name": "staff-engineer-mode",
                    "version": "0.0.0",
                    "description": "test",
                    "main": ".opencode/plugins/staff-engineer-mode.js",
                }
            ),
        )
        self.write_valid_bootstrap_context()
        plugin = "\n".join(
            [
                "const skillsDir = 'skills';",
                "const specialistsDir = 'specialists';",
                "const routerPath = 'router';",
                "const toolMapping = 'tools';",
                "config.skills.paths = [skillsDir];",
                "experimental.chat.messages.transform",
                "staff-engineer-mode",
                "SPECIALIST_ROOT: specialistsDir,",
                "ROUTER_PATH: routerPath,",
                "EVENT_HOOK: 'hook',",
                "CURRENT_REPO: '',",
                "TOOL_MAPPING: toolMapping,",
                "",
            ]
        )
        self.write(".opencode/plugins/staff-engineer-mode.js", plugin)

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.validator.validate_opencode()

        self.write(
            ".opencode/plugins/staff-engineer-mode.js",
            plugin + "const templatesDir = 'templates';\nTEMPLATE_ROOT: templatesDir,\n",
        )
        self.validator.validate_opencode()


if __name__ == "__main__":
    unittest.main()
