#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from staff_engineer_mode_contract import MANIFEST_DESCRIPTION_FIELDS

NAME = "staff-engineer-mode"
BOOTSTRAP_TEMPLATE_RELATIVE = Path("skills/staff-engineer-mode/references/bootstrap-context.md")
PRE_RELEASE_VERSION = ".".join(("0", "0", "0"))


def package_version() -> str:
    package_path = ROOT / "package.json"
    if not package_path.exists():
        fail("missing package.json")
    try:
        value = json.loads(package_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"package.json is not valid JSON: {exc}")
    version = value.get("version")
    if not isinstance(version, str) or not version:
        fail("package.json missing version")
    return version


def fail(message: str) -> None:
    print(f"platform validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def git_commit(ref: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", f"{ref}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def bootstrap_template_text() -> str:
    path = ROOT / BOOTSTRAP_TEMPLATE_RELATIVE
    if not path.exists():
        fail(f"missing {BOOTSTRAP_TEMPLATE_RELATIVE}")
    return path.read_text()


def require(value: dict, key: str, path: Path) -> object:
    if key not in value or value[key] in ("", None, []):
        fail(f"{path.relative_to(ROOT)} missing required field {key}")
    return value[key]


def value_at_path(value: dict, dotted: str) -> object:
    current: object = value
    for part in dotted.split("."):
        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                fail(f"cannot index list with {part!r} in description contract")
            try:
                current = current[index]
            except IndexError:
                fail(f"description contract path {dotted!r} references missing list item")
            continue
        if not isinstance(current, dict) or part not in current:
            fail(f"description contract path {dotted!r} references missing field")
        current = current[part]
    return current


def validate_manifest_descriptions() -> None:
    cache: dict[Path, dict] = {}
    for key, expected in MANIFEST_DESCRIPTION_FIELDS.items():
        relative, field_path = key.split(":", 1)
        path = ROOT / relative
        value = cache.setdefault(path, read_json(path))
        actual = value_at_path(value, field_path)
        if actual != expected:
            fail(f"{relative} {field_path} must match the canonical description copy")


def require_name_version(path: Path) -> dict:
    value = read_json(path)
    if require(value, "name", path) != NAME:
        fail(f"{path.relative_to(ROOT)} name must be {NAME}")
    version = package_version()
    if require(value, "version", path) != version:
        fail(f"{path.relative_to(ROOT)} version must be {version}")
    require(value, "description", path)
    require(value, "homepage", path) if path.name == "plugin.json" else None
    return value


def assert_path_exists(owner: Path, relative: str) -> None:
    target = (ROOT / relative).resolve()
    if not target.exists():
        fail(f"{owner.relative_to(ROOT)} references missing path {relative}")


def validate_https_plugin_install_paths() -> None:
    paths = [
        ".claude-plugin/marketplace.json",
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        ".codex/INSTALL.md",
        ".cursor-plugin/INSTALL.md",
        ".cursor-plugin/plugin.json",
        ".opencode/INSTALL.md",
        "README.md",
        "gemini-extension.json",
        "package.json",
    ]
    for relative in paths:
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text()
        if re.search(r"\b(?:git@github\.com[:/]|ssh://)", text):
            fail(f"{relative} must not use SSH git install paths")


def validate_codex() -> None:
    path = ROOT / ".codex-plugin" / "plugin.json"
    value = require_name_version(path)
    if value.get("skills") != "./skills/":
        fail(".codex-plugin/plugin.json skills must be ./skills/")
    assert_path_exists(path, "skills")
    assert_path_exists(path, "specialists")
    interface = value.get("interface")
    if not isinstance(interface, dict):
        fail(".codex-plugin/plugin.json missing interface object")
    for key in [
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
        "brandColor",
    ]:
        require(interface, key, path)
    if "Interactive" not in interface["capabilities"]:
        fail(".codex-plugin/plugin.json interface.capabilities must include Interactive")


def validate_claude() -> None:
    plugin = ROOT / ".claude-plugin" / "plugin.json"
    value = require_name_version(plugin)
    if "skills" in value:
        fail(".claude-plugin/plugin.json must rely on flat skills/ auto-discovery, not explicit nested skill paths")
    router = ROOT / "skills" / "staff-engineer-mode" / "SKILL.md"
    if not router.exists():
        fail("missing skills/staff-engineer-mode/SKILL.md")
    claude = ROOT / "CLAUDE.md"
    if not claude.exists():
        fail("missing CLAUDE.md")
    claude_text = claude.read_text()
    if "@AGENTS.md" not in claude_text:
        fail("CLAUDE.md must reference AGENTS.md as the repository rules source")
    if "@./skills/staff-engineer-mode/SKILL.md" not in claude_text:
        fail("CLAUDE.md must name the flat router entrypoint")
    if len([line for line in claude_text.splitlines() if line.strip()]) > 4:
        fail("CLAUDE.md must stay a thin pointer to AGENTS.md and the router skill")
    if "## Bash Preflight" in claude_text or "specialists/<specialist-name>.md" in claude_text:
        fail("CLAUDE.md must not duplicate repository or router policy")
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    value = read_json(marketplace)
    if value.get("name") != NAME:
        fail(".claude-plugin/marketplace.json name must be staff-engineer-mode")
    plugins = value.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail(".claude-plugin/marketplace.json must list exactly one plugin")
    entry = plugins[0]
    if entry.get("name") != NAME:
        fail(".claude-plugin/marketplace.json plugin entry name must be staff-engineer-mode")
    source = entry.get("source")
    if not isinstance(source, dict):
        fail(".claude-plugin/marketplace.json plugin entry source must pin git metadata")
    if source.get("source") != "url" or source.get("url") != "https://github.com/sirmarkz/staff-engineer-mode.git":
        fail(".claude-plugin/marketplace.json plugin entry source must use the HTTPS git URL")
    version = package_version()
    if version == PRE_RELEASE_VERSION:
        if source.get("ref") != "main":
            fail(".claude-plugin/marketplace.json pre-release source must use main")
        if "sha" in source:
            fail(".claude-plugin/marketplace.json pre-release source must not pin stale sha metadata")
    else:
        expected_ref = f"v{version}"
        if source.get("ref") != expected_ref:
            fail(f".claude-plugin/marketplace.json plugin entry source must pin ref {expected_ref}")
        sha = source.get("sha")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            fail(".claude-plugin/marketplace.json plugin entry source must include a 40-character sha")
        resolved = git_commit(expected_ref)
        if resolved is not None and sha != resolved:
            fail(f".claude-plugin/marketplace.json source sha must match {expected_ref} commit {resolved}")


def validate_cursor() -> None:
    path = ROOT / ".cursor-plugin" / "plugin.json"
    value = require_name_version(path)
    if value.get("skills") != "./skills/":
        fail(".cursor-plugin/plugin.json skills must be ./skills/")
    if value.get("hooks") != "./hooks/hooks-cursor.json":
        fail(".cursor-plugin/plugin.json hooks must be ./hooks/hooks-cursor.json")
    assert_path_exists(path, "skills")
    assert_path_exists(path, "hooks/hooks-cursor.json")
    require(value, "displayName", path)
    require(value, "keywords", path)
    if not (ROOT / ".cursor-plugin" / "INSTALL.md").exists():
        fail("missing .cursor-plugin/INSTALL.md")


def validate_gemini() -> None:
    path = ROOT / "gemini-extension.json"
    value = require_name_version(path)
    if value.get("contextFileName") != "GEMINI.md":
        fail("gemini-extension.json contextFileName must be GEMINI.md")
    gemini = ROOT / "GEMINI.md"
    if not gemini.exists():
        fail("missing GEMINI.md")
    text = gemini.read_text()
    if "@AGENTS.md" not in text:
        fail("GEMINI.md must reference AGENTS.md as the repository rules source")
    if "@./skills/staff-engineer-mode/SKILL.md" not in text:
        fail("GEMINI.md must name the router entrypoint")
    if "skills/routing/staff-engineer-mode" in text:
        fail("GEMINI.md must not reference the old nested router path")
    if len([line for line in text.splitlines() if line.strip()]) > 4:
        fail("GEMINI.md must stay a thin pointer to AGENTS.md and the router skill")
    if "specialists/<specialist-name>.md" in text or "## Routing Discipline" in text:
        fail("GEMINI.md must not duplicate repository or router policy")


def validate_opencode() -> None:
    package_path = ROOT / "package.json"
    package = require_name_version(package_path)
    main = package.get("main")
    if main != ".opencode/plugins/staff-engineer-mode.js":
        fail("package.json main must point to .opencode/plugins/staff-engineer-mode.js")
    plugin_path = ROOT / main
    if not plugin_path.exists():
        fail("missing OpenCode plugin file")
    text = plugin_path.read_text()
    bootstrap_text = bootstrap_template_text()
    if "skillsDir" not in text or "config.skills.paths" not in text:
        fail("OpenCode plugin must register skillsDir in config.skills.paths")
    if "specialistsDir" not in text or "<slug>.md" not in (text + bootstrap_text):
        fail("OpenCode plugin must route to hidden specialist reference files")
    if "experimental.chat.messages.transform" not in text or "staff-engineer-mode" not in text:
        fail("OpenCode plugin must inject the router bootstrap")
    if "Keep guidance technology-agnostic by default" not in bootstrap_text:
        fail("OpenCode plugin must require technology-agnostic guidance by default")
    if not (ROOT / ".opencode" / "INSTALL.md").exists():
        fail("missing .opencode/INSTALL.md")


def validate_hooks() -> None:
    for relative in [
        "hooks/hooks.json",
        "hooks/hooks-cursor.json",
        "hooks/agent-event-policy",
        "hooks/session-start",
        "hooks/run-hook.cmd",
    ]:
        if not (ROOT / relative).exists():
            fail(f"missing {relative}")
    hooks_config = (ROOT / "hooks" / "hooks.json").read_text()
    for term in [
        '"PreToolUse"',
        '"Bash"',
        "agent-event-policy pretooluse",
    ]:
        if term not in hooks_config:
            fail(f"hooks/hooks.json missing {term}")
    agent_event_policy = (ROOT / "hooks" / "agent-event-policy").read_text()
    for term in [
        "before_commit",
        "before_release",
        "agent-pr-review",
        "release-build-reproducibility",
        "production-readiness-review",
    ]:
        if term not in agent_event_policy:
            fail(f"hooks/agent-event-policy missing {term}")
    session_start = (ROOT / "hooks" / "session-start").read_text()
    bootstrap_text = bootstrap_template_text()
    for term in [
        "CURSOR_PLUGIN_ROOT",
        "CLAUDE_PLUGIN_ROOT",
        "COPILOT_CLI",
        "additionalContext",
        "additional_context",
        "staff-engineer-mode",
        "skills/staff-engineer-mode/SKILL.md",
        "specialists",
        "EVENT_HOOK",
        "CURRENT_REPO",
    ]:
        if term not in session_start:
            fail(f"hooks/session-start missing {term}")
    for term in [
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
    ]:
        if term not in bootstrap_text:
            fail(f"bootstrap-context.md missing {term}")


def validate_version_metadata() -> None:
    bump_config = ROOT / ".version-bump.json"
    if not bump_config.exists():
        fail("missing .version-bump.json")
    config = read_json(bump_config)
    files = config.get("files")
    if not isinstance(files, list) or not files:
        fail(".version-bump.json must declare versioned files")
    declared = {(item.get("path"), item.get("field")) for item in files if isinstance(item, dict)}
    required = {
        ("package.json", "version"),
        (".claude-plugin/plugin.json", "version"),
        (".cursor-plugin/plugin.json", "version"),
        (".codex-plugin/plugin.json", "version"),
        (".claude-plugin/marketplace.json", "plugins.0.version"),
        (".claude-plugin/marketplace.json", "plugins.0.source.ref"),
        ("gemini-extension.json", "version"),
    }
    missing = required - declared
    if missing:
        fail(f".version-bump.json missing version fields: {sorted(missing)}")
    if not (ROOT / "scripts" / "bump-version.sh").exists():
        fail("missing scripts/bump-version.sh")
    notes = ROOT / "RELEASE-NOTES.md"
    if not notes.exists():
        fail("missing RELEASE-NOTES.md")
    version = package_version()
    notes_text = notes.read_text()
    if version == PRE_RELEASE_VERSION:
        if "No public release history yet." not in notes_text:
            fail("RELEASE-NOTES.md must describe initial state without public release history")
    elif f"## {version} -" not in notes_text:
        fail(f"RELEASE-NOTES.md must include a release entry for {version}")


def validate_ci_workflow() -> None:
    workflow = ROOT / ".github" / "workflows" / "validation.yml"
    if not workflow.exists():
        fail("missing .github/workflows/validation.yml")
    text = workflow.read_text()
    for term in [
        "pull_request:",
        "push:",
        "python3 -m py_compile",
        "scripts/run_router_eval.py",
        "scripts/test_run_router_eval.py",
        "scripts/test_agent_event_policy_hook.py",
        "scripts/test_validate_platform_support.py",
        "bash -n hooks/agent-event-policy",
        "bash -n scripts/bump-version.sh",
        "python3 -m unittest scripts/test_run_router_eval.py",
        "python3 -m unittest scripts/test_agent_event_policy_hook.py",
        "python3 -m unittest scripts/test_validate_platform_support.py",
        "scripts/bump-version.sh --check",
        "scripts/bump-version.sh --audit",
        "python3 scripts/validate_source_quality.py",
        "python3 scripts/validate_skill_pack.py",
        "python3 scripts/validate_router_eval.py",
        "python3 scripts/validate_platform_support.py",
        "node --check .opencode/plugins/staff-engineer-mode.js",
        "git grep -nI '[[:blank:]]$' -- .",
    ]:
        if term not in text:
            fail(f".github/workflows/validation.yml missing {term}")


def validate_docs() -> None:
    for relative in ["README.md", "LICENSE", ".codex/INSTALL.md"]:
        if not (ROOT / relative).exists():
            fail(f"missing {relative}")
    readme = (ROOT / "README.md").read_text()
    if "staff-engineer-mode" not in readme:
        fail("README.md must document the router entrypoint")
    if "claude plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git" not in readme:
        fail("README.md must show the Claude terminal marketplace add command")
    if "/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git" not in readme:
        fail("README.md must show the Claude agent-chat marketplace add command")
    if "staff-engineer-mode-marketplace" in readme:
        fail("README.md must not require a manual Claude marketplace checkout for normal installs")
    if "/plugin marketplace add sirmarkz/staff-engineer-mode" in readme:
        fail("README.md must not use the Claude GitHub owner/repo marketplace add command")
    if "/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode\n" in readme:
        fail("README.md Claude HTTPS marketplace add command must include the .git suffix")
    if "copilot plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git" not in readme:
        fail("README.md must use the GitHub Copilot CLI HTTPS git URL marketplace add command")
    if "copilot plugin marketplace add sirmarkz/staff-engineer-mode" in readme:
        fail("README.md must not use the GitHub Copilot CLI owner/repo marketplace add command")
    if "```text\n/plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git\n/plugin install staff-engineer-mode@staff-engineer-mode\n```" in readme:
        fail("README.md must show Claude install commands in separate copyable blocks")
    if "```bash\ncopilot plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git\ncopilot plugin install staff-engineer-mode@staff-engineer-mode\n```" in readme:
        fail("README.md must show GitHub Copilot CLI install commands in separate copyable blocks")
    if "git clone https://github.com/sirmarkz/staff-engineer-mode.git ~/.cursor/staff-engineer-mode-src" not in readme:
        fail("README.md must show the Cursor local terminal install path")
    if "/add-plugin staff-engineer-mode" in readme:
        fail("README.md must not use Cursor /add-plugin before marketplace publication")
    cursor_install = (ROOT / ".cursor-plugin" / "INSTALL.md").read_text()
    for text, label in [(readme, "README.md"), (cursor_install, ".cursor-plugin/INSTALL.md")]:
        if "Cursor Plugin Marketplace" in text:
            fail(f"{label} must not claim Staff Engineer Mode is available in the Cursor Plugin Marketplace")
    codex_install = (ROOT / ".codex" / "INSTALL.md").read_text()
    if "codex plugin marketplace add https://github.com/sirmarkz/staff-engineer-mode.git" not in codex_install:
        fail(".codex/INSTALL.md must use the Codex plugin marketplace install path")
    if "codex plugin add staff-engineer-mode@staff-engineer-mode" not in codex_install:
        fail(".codex/INSTALL.md must install the Staff Engineer Mode Codex plugin")
    if "--ref" in codex_install:
        fail(".codex/INSTALL.md must not require a Codex marketplace --ref for normal installs")
    if "Skills-Only Fallback" not in codex_install:
        fail(".codex/INSTALL.md must label the native skills symlink path as a fallback")
    if "specialists/<slug>.md" not in codex_install:
        fail(".codex/INSTALL.md must document routed specialist files")
    opencode_install = (ROOT / ".opencode" / "INSTALL.md").read_text()
    if "opencode plugin 'staff-engineer-mode@git+https://github.com/sirmarkz/staff-engineer-mode.git'" not in opencode_install:
        fail(".opencode/INSTALL.md must use the normal OpenCode Git plugin install path")
    if "staff-engineer-mode.git#" in opencode_install:
        fail(".opencode/INSTALL.md must not pin OpenCode installs with #commit")


def main() -> int:
    validate_https_plugin_install_paths()
    validate_manifest_descriptions()
    validate_codex()
    validate_claude()
    validate_cursor()
    validate_gemini()
    validate_opencode()
    validate_hooks()
    validate_version_metadata()
    validate_ci_workflow()
    validate_docs()
    print("platform support validation passed: Claude Code, Codex CLI, Cursor, OpenCode, GitHub Copilot CLI, Gemini CLI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
