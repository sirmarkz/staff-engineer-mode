#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "staff-engineer-mode"


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


def require(value: dict, key: str, path: Path) -> object:
    if key not in value or value[key] in ("", None, []):
        fail(f"{path.relative_to(ROOT)} missing required field {key}")
    return value[key]


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


def validate_codex() -> None:
    path = ROOT / ".codex-plugin" / "plugin.json"
    value = require_name_version(path)
    if value.get("skills") != "./skills/":
        fail(".codex-plugin/plugin.json skills must be ./skills/")
    assert_path_exists(path, "skills")
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
    if "@./skills/staff-engineer-mode/SKILL.md" not in claude_text:
        fail("CLAUDE.md must name the flat router entrypoint")
    if "Keep guidance technology-agnostic by default" not in claude_text:
        fail("CLAUDE.md must require technology-agnostic guidance by default")
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    value = read_json(marketplace)
    if value.get("name") != NAME:
        fail(".claude-plugin/marketplace.json name must be staff-engineer-mode")
    plugins = value.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail(".claude-plugin/marketplace.json must list exactly one plugin")
    entry = plugins[0]
    if entry.get("name") != NAME or entry.get("source") != "./":
        fail(".claude-plugin/marketplace.json plugin entry must use source ./")


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
    if "staff-engineer-mode" not in text:
        fail("GEMINI.md must name the router entrypoint")
    if "skills/routing/staff-engineer-mode" in text:
        fail("GEMINI.md must not reference the old nested router path")
    if "Keep guidance technology-agnostic by default" not in text:
        fail("GEMINI.md must require technology-agnostic guidance by default")


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
    if "skillsDir" not in text or "config.skills.paths" not in text:
        fail("OpenCode plugin must register skillsDir in config.skills.paths")
    if "experimental.chat.messages.transform" not in text or "staff-engineer-mode" not in text:
        fail("OpenCode plugin must inject the router bootstrap")
    if "Keep guidance technology-agnostic by default" not in text:
        fail("OpenCode plugin must require technology-agnostic guidance by default")
    if not (ROOT / ".opencode" / "INSTALL.md").exists():
        fail("missing .opencode/INSTALL.md")


def validate_hooks() -> None:
    for relative in [
        "hooks/hooks.json",
        "hooks/hooks-cursor.json",
        "hooks/session-start",
        "hooks/run-hook.cmd",
    ]:
        if not (ROOT / relative).exists():
            fail(f"missing {relative}")
    session_start = (ROOT / "hooks" / "session-start").read_text()
    for term in [
        "CURSOR_PLUGIN_ROOT",
        "CLAUDE_PLUGIN_ROOT",
        "COPILOT_CLI",
        "additionalContext",
        "additional_context",
        "staff-engineer-mode",
        "skills/staff-engineer-mode/SKILL.md",
        "Keep guidance technology-agnostic by default",
    ]:
        if term not in session_start:
            fail(f"hooks/session-start missing {term}")


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
    if version == "0.0.0":
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
        "bash -n scripts/bump-version.sh",
        "python3 -m unittest scripts/test_run_router_eval.py",
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
    for relative in ["README.md", "NOTICE.md", ".codex/INSTALL.md"]:
        if not (ROOT / relative).exists():
            fail(f"missing {relative}")
    readme = (ROOT / "README.md").read_text()
    for term in [
        "How It Works",
        "Installation",
        "What's Inside",
        "Claude Code",
        "Codex CLI",
        "Codex App",
        "Cursor",
        "OpenCode",
        "GitHub Copilot CLI",
        "Gemini CLI",
    ]:
        if term not in readme:
            fail(f"README.md missing required section or supported tool {term}")
    if "staff-engineer-mode" not in readme:
        fail("README.md must document router entrypoint")
    if "/plugin marketplace add https://github.com/tnilabs/staff-engineer-mode" not in readme:
        fail("README.md must use an HTTPS Claude marketplace add command")
    if "/plugin marketplace add tnilabs/staff-engineer-mode" in readme:
        fail("README.md must not use the SSH-prone Claude owner/repo marketplace shorthand")
    codex_install = (ROOT / ".codex" / "INSTALL.md").read_text()
    if "~/.agents/skills/staff-engineer-mode" not in codex_install:
        fail(".codex/INSTALL.md must use the native ~/.agents/skills/staff-engineer-mode install path")
    if 'ln -s ~/.codex/staff-engineer-mode/skills ~/.agents/skills/staff-engineer-mode' not in codex_install:
        fail(".codex/INSTALL.md must symlink the Staff Engineer Mode skill tree for Codex")
    if "original synthesis" not in (ROOT / "NOTICE.md").read_text():
        fail("NOTICE.md must state original synthesis/source boundary")


def main() -> int:
    validate_codex()
    validate_claude()
    validate_cursor()
    validate_gemini()
    validate_opencode()
    validate_hooks()
    validate_version_metadata()
    validate_ci_workflow()
    validate_docs()
    print("platform support validation passed: Claude Code, Codex CLI, Codex App, Cursor, OpenCode, GitHub Copilot CLI, Gemini CLI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
