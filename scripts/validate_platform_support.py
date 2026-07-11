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
YAML_MAPPING_RE = re.compile(
    r"^(?P<key>\"(?:[^\"\\]|\\.)*\"|'(?:[^']|'')*'|[A-Za-z_][A-Za-z0-9_.-]*)\s*:\s*(?P<value>.*)$"
)


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


def validate_agents_release_policy() -> None:
    path = ROOT / "AGENTS.md"
    if not path.exists():
        fail("missing AGENTS.md")
    text = path.read_text()
    for term in [
        "Release tags and hosted GitHub release titles must both be exactly `vX.Y.Z`.",
        "`RELEASE-NOTES.md` headings keep the plain `X.Y.Z - YYYY-MM-DD` format.",
        "local memory",
        "`<claude-mem-context>`",
    ]:
        if term not in text:
            fail(f"AGENTS.md missing release policy term: {term}")
    if "<claude-mem-context>" in text.replace("`<claude-mem-context>`", ""):
        fail("AGENTS.md must not contain committed claude-mem-context payloads")


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
    if "templatesDir" not in text or re.search(r"\bTEMPLATE_ROOT\s*:\s*templatesDir\b", text) is None:
        fail("OpenCode plugin must render TEMPLATE_ROOT from the bundled templates directory")
    if "experimental.chat.messages.transform" not in text or "staff-engineer-mode" not in text:
        fail("OpenCode plugin must inject the router bootstrap")
    if "Keep guidance technology-agnostic by default" not in bootstrap_text:
        fail("OpenCode plugin must require technology-agnostic guidance by default")
    rendered_bootstrap = bootstrap_text
    placeholders = set(re.findall(r"{{([A-Z][A-Z0-9_]*)}}", bootstrap_text))
    for placeholder in placeholders:
        if re.search(rf"\b{re.escape(placeholder)}\s*:", text) is None:
            fail(f"OpenCode plugin must render bootstrap placeholder {placeholder}")
        rendered_bootstrap = rendered_bootstrap.replace(f"{{{{{placeholder}}}}}", f"/{placeholder.lower()}")
    if re.search(r"{{[^{}]+}}", rendered_bootstrap):
        fail("OpenCode plugin bootstrap rendering leaves unresolved placeholders")
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
    hooks_path = ROOT / "hooks" / "hooks.json"
    hooks_config = hooks_path.read_text()
    for term in [
        '"PreToolUse"',
        '"Bash"',
        "agent-event-policy pretooluse",
    ]:
        if term not in hooks_config:
            fail(f"hooks/hooks.json missing {term}")
    hooks_value = read_json(hooks_path)
    hook_commands = []
    hook_events = hooks_value.get("hooks")
    if not isinstance(hook_events, dict):
        fail("hooks/hooks.json hooks must be an object")
    for event_entries in hook_events.values():
        if not isinstance(event_entries, list):
            fail("hooks/hooks.json hook event entries must be lists")
        for event_entry in event_entries:
            if not isinstance(event_entry, dict):
                fail("hooks/hooks.json hook event entries must be objects")
            commands = event_entry.get("hooks")
            if not isinstance(commands, list):
                fail("hooks/hooks.json hook entries must contain hooks lists")
            for hook in commands:
                if not isinstance(hook, dict) or not isinstance(hook.get("command"), str):
                    fail("hooks/hooks.json command hooks must include command strings")
                hook_commands.append(hook["command"])
    run_hook_commands = [command for command in hook_commands if "hooks/run-hook.cmd" in command]
    if not run_hook_commands:
        fail("hooks/hooks.json must invoke hooks/run-hook.cmd")
    for command in run_hook_commands:
        if "${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}" not in command:
            fail("hooks/hooks.json run-hook commands must support PLUGIN_ROOT with CLAUDE_PLUGIN_ROOT fallback")
    cursor_hooks_path = ROOT / "hooks" / "hooks-cursor.json"
    cursor_hooks = read_json(cursor_hooks_path)
    if cursor_hooks.get("version") != 1:
        fail("hooks/hooks-cursor.json version must be 1")
    cursor_events = cursor_hooks.get("hooks")
    if not isinstance(cursor_events, dict):
        fail("hooks/hooks-cursor.json hooks must be an object")
    cursor_session_start = cursor_events.get("sessionStart")
    if not isinstance(cursor_session_start, list) or not cursor_session_start:
        fail("hooks/hooks-cursor.json must declare at least one sessionStart hook")
    for hook in cursor_session_start:
        if not isinstance(hook, dict) or hook.get("command") != "./hooks/run-hook.cmd session-start":
            fail("Cursor sessionStart hooks must invoke ./hooks/run-hook.cmd session-start")
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
        "ROUTER_PATH",
        "TEMPLATE_ROOT",
        "EVENT_HOOK",
        "CURRENT_REPO",
    ]:
        if term not in session_start:
            fail(f"hooks/session-start missing {term}")
    for term in [
        "SPECIALIST_ROOT={{SPECIALIST_ROOT}}",
        "TEMPLATE_ROOT={{TEMPLATE_ROOT}}",
        "ROUTER_PATH={{ROUTER_PATH}}",
        "EVENT_HOOK={{EVENT_HOOK}}",
        "CURRENT_REPO={{CURRENT_REPO}}",
        "load the native `staff-engineer-mode` router",
        "Read `${ROUTER_PATH}`",
        "Router load alone is not enough",
        "Read `${SPECIALIST_ROOT}/<slug>.md`",
        "Read `${TEMPLATE_ROOT}/README.md`",
        "before any repo file",
        "Do not parallel-load router and repo files",
        "never call `Skill staff-engineer-mode:<slug>`",
        "Read `${SPECIALIST_ROOT}/agent-pr-review.md` before code-review",
        "Keep guidance technology-agnostic by default",
        "agent-pr-review",
        "release-build-reproducibility",
        "production-readiness-review",
        "Do not combine stage/commit/push",
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


def strip_yaml_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if quote == '"':
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if quote == "'":
            if character == quote:
                if index + 1 < len(value) and value[index + 1] == quote:
                    continue
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
            continue
        if character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        if value[0] == "'":
            return value[1:-1].replace("''", "'")
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
        return decoded if isinstance(decoded, str) else value
    return value


def split_yaml_flow(value: str) -> list[str]:
    parts: list[str] = []
    start = 0
    quote: str | None = None
    escaped = False
    depth = 0
    for index, character in enumerate(value):
        if quote == '"':
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if quote == "'":
            if character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character in "[{(":
            depth += 1
        elif character in "]})":
            depth = max(0, depth - 1)
        elif character == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return [part for part in parts if part]


def yaml_flow_has_mapping_key(value: str, expected: str) -> bool:
    index = 0
    while index < len(value):
        character = value[index]
        if character in {'"', "'"}:
            quote = character
            start = index
            index += 1
            escaped = False
            while index < len(value):
                current = value[index]
                if quote == '"' and escaped:
                    escaped = False
                elif quote == '"' and current == "\\":
                    escaped = True
                elif current == quote:
                    if quote == "'" and index + 1 < len(value) and value[index + 1] == quote:
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            end = index
            while index < len(value) and value[index].isspace():
                index += 1
            if index < len(value) and value[index] == ":" and yaml_scalar(value[start:end]) == expected:
                return True
            continue
        match = re.match(r"[A-Za-z_][A-Za-z0-9_.-]*", value[index:])
        if match is None:
            index += 1
            continue
        key = match.group(0)
        index += len(key)
        while index < len(value) and value[index].isspace():
            index += 1
        if index < len(value) and value[index] == ":" and key == expected:
            return True
    return False


def workflow_mapping_entries(text: str) -> list[tuple[int, int, str, str, tuple[str, ...]]]:
    """Return YAML mapping entries while excluding literal/folded scalar bodies."""
    entries: list[tuple[int, int, str, str, tuple[str, ...]]] = []
    stack: list[tuple[int, str]] = []
    block_parent_indent: int | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            fail(f"workflow YAML line {line_number} must not indent with tabs")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if block_parent_indent is not None:
            if indent > block_parent_indent:
                continue
            block_parent_indent = None

        content = strip_yaml_comment(raw_line[indent:]).strip()
        if not content or content in {"---", "..."}:
            continue
        effective_indent = indent
        if content.startswith("-") and (len(content) == 1 or content[1].isspace()):
            content = content[1:].lstrip()
            effective_indent += 2
            if not content:
                continue

        while stack and stack[-1][0] >= effective_indent:
            stack.pop()
        parents = tuple(key for _parent_indent, key in stack)

        candidate_mappings = [content]
        if content.startswith("{") and content.endswith("}"):
            candidate_mappings = split_yaml_flow(content[1:-1])

        parsed_entries: list[tuple[str, str]] = []
        for candidate in candidate_mappings:
            match = YAML_MAPPING_RE.match(candidate)
            if match is None:
                continue
            key = yaml_scalar(match.group("key"))
            value = match.group("value").strip()
            parsed_entries.append((key, value))
            entries.append((line_number, effective_indent, key, value, parents))

        if len(parsed_entries) != 1:
            continue
        key, value = parsed_entries[0]
        if re.match(r"^[|>][0-9+-]*(?:\s|$)", value):
            block_parent_indent = indent
        elif not value:
            stack.append((effective_indent, key))

    return entries


def valid_top_level_permissions(value: str) -> bool:
    value = value.strip()
    if not (value.startswith("{") and value.endswith("}")):
        return False
    pairs = split_yaml_flow(value[1:-1])
    if len(pairs) != 1:
        return False
    match = YAML_MAPPING_RE.match(pairs[0])
    return bool(
        match
        and yaml_scalar(match.group("key")) == "contents"
        and yaml_scalar(match.group("value")) == "read"
    )


def validate_ci_workflow() -> None:
    workflow = ROOT / ".github" / "workflows" / "validation.yml"
    if not workflow.exists():
        fail("missing .github/workflows/validation.yml")
    text = workflow.read_text()
    for term in [
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
    ]:
        if term not in text:
            fail(f".github/workflows/validation.yml missing {term}")
    workflow_root = ROOT / ".github" / "workflows"
    workflow_paths = set(workflow_root.glob("*.yml")) | set(workflow_root.glob("*.yaml"))
    for path in sorted(workflow_paths):
        validate_action_security(path.read_text(), path)


def validate_action_security(text: str, path: Path) -> None:
    entries = workflow_mapping_entries(text)
    top_permissions = [entry for entry in entries if entry[1] == 0 and entry[2] == "permissions"]
    if len(top_permissions) != 1:
        fail(f"{path.relative_to(ROOT)} must declare one top-level permissions mapping")
    _line, _indent, _key, permission_value, _parents = top_permissions[0]
    if permission_value:
        if not valid_top_level_permissions(permission_value):
            fail(f"{path.relative_to(ROOT)} top-level permissions must be exactly contents: read")
    else:
        permission_children = [
            entry for entry in entries if entry[4] == ("permissions",)
        ]
        if len(permission_children) != 1 or permission_children[0][2] != "contents" or yaml_scalar(
            permission_children[0][3]
        ) != "read":
            fail(f"{path.relative_to(ROOT)} top-level permissions must be exactly contents: read")

    for line_number, indent, key, value, _parents in entries:
        if key == "permissions" and indent != 0:
            fail(f"{path.relative_to(ROOT)}:{line_number} job-level permissions overrides are not allowed")
        if key != "permissions" and yaml_flow_has_mapping_key(value, "permissions"):
            fail(f"{path.relative_to(ROOT)}:{line_number} nested permissions overrides are not allowed")
        if key != "uses" and yaml_flow_has_mapping_key(value, "uses"):
            fail(f"{path.relative_to(ROOT)}:{line_number} action references must use block-style uses entries")
        if key != "uses":
            continue
        reference = yaml_scalar(value)
        if reference.startswith("./"):
            continue
        if not re.search(r"@[0-9a-f]{40}$", reference):
            fail(
                f"{path.relative_to(ROOT)}:{line_number} action reference must use a full commit SHA: "
                f"{reference}"
            )


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
    validate_agents_release_policy()
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
