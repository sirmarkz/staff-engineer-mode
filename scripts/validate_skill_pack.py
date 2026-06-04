#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from staff_engineer_mode_contract import PROHIBITED_SPECIALIST_BODY_TERMS, ROUTER_ROUTING_CHECKS

SKILLS = ROOT / "skills"
SPECIALISTS = ROOT / "specialists"
README = ROOT / "README.md"
SAMPLE_PROMPTS = ROOT / "evals/prompts/expected-routes.md"
SKILL_CONTRACT = SKILLS / "_shared" / "references" / "skill-contract.md"
CODEX_NAMESPACED_PREFIX = "staff-engineer-mode:"
CODEX_MAX_SKILL_NAME_LENGTH = 64
MAX_SKILL_LINES = 300
MAX_DESCRIPTION_CHARS = 180
SAMPLE_PROMPTS_PER_SPECIALIST = 5
ROUTER_MAX_WORDS = 2300
ROUTER_TIEBREAKER_MAX_WORDS = 450
SAMPLE_PROMPT_RE = re.compile(r'^- ".+"$')
PROCESS_PAGE_RE = re.compile(r"\b(?:pages?|paging)\b", re.IGNORECASE)
PROCESS_PAGE_ALLOWED_SPECIALISTS = {
    "agent-pr-review",
    "ai-coding-governance",
    "documentation-lifecycle",
    "engineering-control-evidence",
    "incident-response-and-postmortems",
    "oncall-health",
    "operational-ownership-transfer",
    "platform-golden-paths",
    "production-readiness-review",
}
ROUTING_MATRIX_REQUIRED_BOUNDARIES = {
    "active incident precedence": [
        "active incident",
        "incident-response-and-postmortems",
    ],
    "narrow route precedence": [
        "narrow routes beat",
        "broad neighbors",
    ],
    "production-affecting rollout plans": [
        "production-affecting",
        "progressive-delivery",
        "configuration-and-automation-safety",
    ],
    "tenant incident boundary": [
        "tenant-boundary",
        "tenant-isolation",
        "incident-response-and-postmortems",
    ],
    "service ownership boundary": [
        "service/module/worker",
        "architecture-decisions",
        "dependency-resilience",
    ],
    "distributed data boundary": [
        "data model splits",
        "distributed-data-and-consistency",
        "database-operations",
    ],
    "workflow storage boundary": [
        "cross-service workflows",
        "state-machine-correctness",
    ],
    "client release boundary": [
        "ui pr review",
        "web-release-gates",
        "mobile-release-engineering",
    ],
    "declarative infrastructure boundary": [
        "declarative infrastructure",
        "policy checks",
        "drift detection",
        "reconciliation",
        "infrastructure-and-policy-as-code",
        "configuration-and-automation-safety",
    ],
    "review workflow non-route boundary": [
        "generic review",
        "do not route",
        "agent-pr-review",
        "ai-coding-governance",
    ],
    "cache overload boundary": [
        "hot cache keys",
        "caching-and-derived-data",
        "dependency-resilience",
    ],
    "llm security eval boundary": [
        "prompt-injection or red-team evals",
        "llm-application-security",
        "llm-evaluation",
    ],
    "retired flag hygiene boundary": [
        "after a retired flag is gone",
        "dependency-and-code-hygiene",
        "feature-flag-lifecycle",
    ],
}

SPECIALIST_OPERATIONAL_SECTIONS = [
    "## When To Use",
    "## When Not To Use",
    "## Info To Gather",
    "## Workflow",
    "## Synthesized Default",
    "## Phase Behavior",
    "## Exceptions",
    "## Response Quality Bar",
    "## Required Outputs",
    "## Checks Before Moving On",
    "## Red Flags - Stop And Rework",
    "## Common Mistakes",
]

PHASE_BEHAVIOR_TERMS = {
    "ideation": ["ideation", "risks", "options"],
    "design": ["design", "tradeoffs", "checks"],
    "development": ["development", "sequencing", "checks"],
    "testing": ["testing", "tests", "failure"],
    "release": ["release", "rollout", "rollback"],
    "maintenance": ["maintenance", "owners", "drift"],
    "existing artifact": ["existing artifact", "context", "engineering decision"],
    "missing details": ["missing details", "assumptions", "check next"],
}

ROUTER_PHASE_TRIGGER_TERMS = [
    "guide",
    "ideation",
    "design",
    "development",
    "testing",
    "release",
    "maintenance",
    "decisions",
    "plan implementation",
    "guide development",
    "de-risk an idea",
    "before code exists",
]

ROUTER_CONTEXT_APPLICABILITY_TERMS = [
    "context",
    "repo",
    "files",
    "branch context",
    "conversation",
    "artifact",
    "surface",
    "risk",
    "next decision",
    "signals, not hard requirements",
]

ROUTER_INFERENCE_FIRST_TERMS = [
    "inputs to infer",
    "do not ask",
    "intake fields",
    "infer the safest narrow in-scope route",
    "withhold routing only",
]

ROUTER_DESCRIPTION_TERMS = [
    "engineering decisions",
    "ideation",
    "design",
    "development",
    "testing",
    "release",
    "operations",
    "maintenance",
]

ROUTER_RUNTIME_BANNED_EVAL_TERMS = [
    "eval-harness",
    "fenced routing",
    "routing block",
]

ROUTER_LOAD_CONTRACT_RULE_TERMS = [
    "Read tool",
    "Do not use the Skill tool",
    "before producing engineering guidance",
    "without a matching Read",
]

ROUTER_LOAD_CONTRACT_PLATFORM_TERMS = [
    "SPECIALIST_ROOT=",
    "Codex plugin",
    "Codex skills-only fallback",
    "Gemini:",
]

ROUTER_LOAD_CONTRACT_BANNED_SUBSTRINGS = [
    "../../specialists/",
    "<slug>/SKILL.md",
    "specialists/<specialist-name>/SKILL.md",
]

AUDIT_ONLY_ANTI_PATTERNS = [
    "requires an existing",
    "requires a diff",
    "requires a branch",
    "requires a pr",
    "post-merge only",
    "after deployment only",
    "review existing artifacts only",
]

AUDIT_ONLY_EXCEPTIONS = {
    "agent-pr-review",
    "incident-response-and-postmortems",
    "production-readiness-review",
    "vulnerability-management",
}

AGENT_PR_REVIEW_COMMIT_REQUIRED_TERMS = [
    "create or amend a commit",
    "exact staged diff",
    "regardless of change size",
]

AGENT_PR_REVIEW_COMMIT_SKIP_PATTERNS = [
    "trivial fix",
    "trivial change",
    "human author can self-review",
    "without a structured pass",
]

SLO_BURN_RESPONSE_TERMS = [
    "urgent burn alerts",
    "follow-up-only budget responses",
    "short-window",
    "longer-window",
    "multi-hour",
    "multi-day",
    "diagnostic non-urgent",
]

CONFIG_RUNTIME_OVERRIDE_TERMS = [
    "runtime config values",
    "unsafe values",
    "temporary overrides",
    "owner",
    "expiry",
    "validation evidence",
    "cleanup automation",
    "rollback target",
]

SPECIALIST_DESCRIPTION_REVIEW_EXCEPTIONS = {
    "agent-pr-review",
}

ROUTER_OPERATIONAL_SECTIONS = [
    "## When To Use",
    "## When Not To Use",
    "## Inputs To Infer",
    "## Workflow",
    "## Synthesized Default",
    "## Exceptions",
    "## Required Outputs",
    "## Checks Before Moving On",
    "## Routing Tiebreakers",
    "## Red Flags - Stop And Rework",
    "## Common Mistakes",
]

def fail(message: str) -> None:
    print(f"validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str, path: Path) -> dict[str, str]:
    match = re.match(r"---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(f"{path} missing YAML frontmatter")
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line:
            fail(f"{path} has invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    expected_keys = {"name", "description"}
    unknown_keys = set(values) - expected_keys
    missing_keys = expected_keys - set(values)
    if unknown_keys:
        fail(f"{path} has unsupported frontmatter keys: {', '.join(sorted(unknown_keys))}")
    if missing_keys:
        fail(f"{path} missing frontmatter keys: {', '.join(sorted(missing_keys))}")
    return values


def validate_technology_agnostic_body(text: str, path: Path) -> None:
    for line_number, line in enumerate(text.splitlines(), 1):
        for term in PROHIBITED_SPECIALIST_BODY_TERMS:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])", line):
                fail(f"{path} hardcodes technology term {term!r} at line {line_number}")


def section_body(text: str, heading: str, path: Path) -> str:
    pattern = rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        fail(f"{path} missing section {heading}")
    return match.group("body")


def validate_operational_sections(text: str, path: Path, headings: list[str]) -> None:
    for heading in headings:
        body = section_body(text, heading, path)
        if not re.search(r"\S", body):
            fail(f"{path} section {heading} must include operational guidance")


def check_ids(text: str, path: Path, heading: str) -> list[str]:
    body = section_body(text, heading, path)
    return re.findall(r"^- `([^`]+)`:", body, re.MULTILINE)


def check_bodies(text: str, path: Path, heading: str) -> dict[str, str]:
    body = section_body(text, heading, path)
    return {
        match.group("id"): match.group("body")
        for match in re.finditer(r"^- `(?P<id>[^`]+)`:\s*(?P<body>.+)$", body, re.MULTILINE)
    }


def require_check_terms(check_bodies: dict[str, str], check_id: str, terms: list[str], path: Path) -> None:
    body = check_bodies.get(check_id, "").lower()
    missing = [term for term in terms if term not in body]
    if missing:
        fail(f"{path} check {check_id!r} missing behavior terms: {', '.join(missing)}")


def validate_phase_behavior(text: str, path: Path) -> None:
    body = section_body(text, "## Phase Behavior", path)
    lowered = body.lower()
    for label, terms in PHASE_BEHAVIOR_TERMS.items():
        missing = [term for term in terms if term not in lowered]
        if missing:
            fail(f"{path} Phase Behavior missing {label} terms: {', '.join(missing)}")


def validate_router_phase_triggers(text: str, path: Path) -> None:
    lowered = text.lower()
    missing = [term for term in ROUTER_PHASE_TRIGGER_TERMS if term not in lowered]
    if missing:
        fail(f"{path} missing lifecycle routing trigger terms: {', '.join(missing)}")


def validate_router_context_applicability(text: str, path: Path) -> None:
    lowered = text.lower()
    missing = [term for term in ROUTER_CONTEXT_APPLICABILITY_TERMS if term not in lowered]
    if missing:
        fail(f"{path} missing context-applicability routing terms: {', '.join(missing)}")


def validate_router_inference_first(text: str, path: Path) -> None:
    lowered = text.lower()
    missing = [term for term in ROUTER_INFERENCE_FIRST_TERMS if term not in lowered]
    if missing:
        fail(f"{path} missing inference-first routing terms: {', '.join(missing)}")


def validate_router_load_contract(text: str, path: Path) -> None:
    iron_law_pos = text.find("## Iron Law")
    load_contract_pos = text.find("## Load Contract")
    overview_pos = text.find("## Overview")
    if load_contract_pos < 0:
        fail(f"{path} must declare a '## Load Contract' section after '## Iron Law'")
    if iron_law_pos < 0 or overview_pos < 0:
        fail(f"{path} must contain both '## Iron Law' and '## Overview' sections")
    if not (iron_law_pos < load_contract_pos < overview_pos):
        fail(
            f"{path} Load Contract must sit between '## Iron Law' and '## Overview' "
            f"(found positions iron_law={iron_law_pos}, load_contract={load_contract_pos}, "
            f"overview={overview_pos})"
        )
    body = section_body(text, "## Load Contract", path)
    missing_rules = [term for term in ROUTER_LOAD_CONTRACT_RULE_TERMS if term not in body]
    if missing_rules:
        fail(f"{path} Load Contract missing required rule fragments: {', '.join(missing_rules)}")
    missing_platforms = [term for term in ROUTER_LOAD_CONTRACT_PLATFORM_TERMS if term not in body]
    if missing_platforms:
        fail(f"{path} Load Contract missing platform fallback markers: {', '.join(missing_platforms)}")
    for banned in ROUTER_LOAD_CONTRACT_BANNED_SUBSTRINGS:
        if banned in text:
            fail(
                f"{path} contains obsolete relative path {banned!r}; "
                f"remove it and rely on the Load Contract"
            )


def validate_router_runtime_scope(text: str, path: Path) -> None:
    lowered = text.lower()
    present = [term for term in ROUTER_RUNTIME_BANNED_EVAL_TERMS if term in lowered]
    if present:
        fail(f"{path} contains eval-harness-only runtime terms: {', '.join(present)}")


def validate_decision_guide_framing(text: str, path: Path) -> None:
    slug = skill_name_for_path(path)
    if slug in AUDIT_ONLY_EXCEPTIONS:
        return
    sections = [
        section_body(text, "## When To Use", path),
        section_body(text, "## Info To Gather", path),
        section_body(text, "## Workflow", path),
        section_body(text, "## Required Outputs", path),
    ]
    joined = "\n".join(sections).lower()
    required = ["decision", "assumptions"]
    missing = [term for term in required if term not in joined]
    if missing:
        fail(f"{path} decision-guide framing missing: {', '.join(missing)}")
    for pattern in AUDIT_ONLY_ANTI_PATTERNS:
        if pattern in joined:
            fail(f"{path} has audit-only framing pattern: {pattern}")


def validate_agent_pr_review_commit_policy(text: str, path: Path) -> None:
    if skill_name_for_path(path) != "agent-pr-review":
        return
    when_to_use = section_body(text, "## When To Use", path).lower()
    missing = [term for term in AGENT_PR_REVIEW_COMMIT_REQUIRED_TERMS if term not in when_to_use]
    if missing:
        fail(f"{path} agent-pr-review commit policy missing terms: {', '.join(missing)}")

    when_not_to_use = section_body(text, "## When Not To Use", path).lower()
    for pattern in AGENT_PR_REVIEW_COMMIT_SKIP_PATTERNS:
        if pattern in when_not_to_use:
            fail(
                f"{path} agent-pr-review permits a trivial change skip via {pattern!r}; "
                "commit and amend attempts must be reviewed regardless of size"
            )


def validate_slo_burn_response_split(text: str, path: Path) -> None:
    if skill_name_for_path(path) != "slo-and-error-budgets":
        return
    lowered = text.lower()
    missing = [term for term in SLO_BURN_RESPONSE_TERMS if term not in lowered]
    if missing:
        fail(f"{path} SLO burn-response policy missing terms: {', '.join(missing)}")


def validate_config_runtime_override_controls(text: str, path: Path) -> None:
    if skill_name_for_path(path) != "configuration-and-automation-safety":
        return
    lowered = text.lower()
    missing = [term for term in CONFIG_RUNTIME_OVERRIDE_TERMS if term not in lowered]
    if missing:
        fail(f"{path} runtime override cleanup controls missing terms: {', '.join(missing)}")


def validate_specialist_skill(text: str, path: Path) -> None:
    slug = skill_name_for_path(path)
    description = parse_frontmatter(text, path)["description"].lower()
    if slug not in PROCESS_PAGE_ALLOWED_SPECIALISTS:
        match = PROCESS_PAGE_RE.search(text)
        if match:
            line = text[: match.start()].count("\n") + 1
            fail(f"{path} uses process-style page/paging language outside workflow, readiness, or control specialists at line {line}")
    if slug not in SPECIALIST_DESCRIPTION_REVIEW_EXCEPTIONS:
        for term in ["review", "audit"]:
            if term in description:
                fail(f"{path} description must trigger decision/design work, not {term}-only work")
    validate_operational_sections(text, path, SPECIALIST_OPERATIONAL_SECTIONS)
    validate_phase_behavior(text, path)
    validate_decision_guide_framing(text, path)
    validate_agent_pr_review_commit_policy(text, path)
    validate_slo_burn_response_split(text, path)
    validate_config_runtime_override_controls(text, path)
    checks = check_ids(text, path, "## Checks Before Moving On")
    if len(checks) < 3:
        fail(f"{path} needs at least three checks under ## Checks Before Moving On")


def validate_router_skill(text: str, path: Path) -> None:
    frontmatter = parse_frontmatter(text, path)
    description = frontmatter["description"].lower()
    missing_description_terms = [term for term in ROUTER_DESCRIPTION_TERMS if term not in description]
    if missing_description_terms:
        fail(f"{path} router description missing trigger terms: {', '.join(missing_description_terms)}")
    if "needs routing" in description or "need routing" in description:
        fail(f"{path} router description must describe engineering decision work, not 'needs routing'")
    validate_operational_sections(text, path, ROUTER_OPERATIONAL_SECTIONS)
    validate_router_phase_triggers(text, path)
    validate_router_context_applicability(text, path)
    validate_router_inference_first(text, path)
    validate_router_runtime_scope(text, path)
    validate_router_load_contract(text, path)
    word_count = len(re.findall(r"\S+", text))
    if word_count > ROUTER_MAX_WORDS:
        fail(f"{path} is {word_count} words; compact router skills must stay under {ROUTER_MAX_WORDS}")
    routing_check_ids = set(check_ids(text, path, "## Checks Before Moving On"))
    missing = set(ROUTER_ROUTING_CHECKS) - routing_check_ids
    if missing:
        fail(f"{path} missing router checks: {', '.join(sorted(missing))}")
    routing_check_bodies = check_bodies(text, path, "## Checks Before Moving On")
    require_check_terms(routing_check_bodies, "capability_translation", ["tool", "translated", "not repeated"], path)
    require_check_terms(routing_check_bodies, "scope_check", ["out-of-scope", "without specialist names"], path)
    require_check_terms(routing_check_bodies, "ambiguity_check", ["ambiguous", "infer", "intake questions", "specialist names"], path)


def validate_router_boundary_split(router_text: str, matrix_text: str, router_path: Path, matrix_path: Path) -> None:
    tiebreaker_body = section_body(router_text, "## Routing Tiebreakers", router_path)
    word_count = len(re.findall(r"\S+", tiebreaker_body))
    if word_count > ROUTER_TIEBREAKER_MAX_WORDS:
        fail(
            f"{router_path} Routing Tiebreakers is {word_count} words; "
            f"keep detailed boundary rules in {matrix_path.relative_to(ROOT)}"
        )
    if "Load `references/routing-matrix.md`" not in tiebreaker_body:
        fail(f"{router_path} Routing Tiebreakers must point to references/routing-matrix.md")

    normalized_lines = [line.lower() for line in matrix_text.splitlines()]
    for boundary, terms in ROUTING_MATRIX_REQUIRED_BOUNDARIES.items():
        if not any(all(term in line for term in terms) for line in normalized_lines):
            fail(
                f"{matrix_path} missing {boundary} routing boundary terms: "
                f"{', '.join(terms)}"
            )


def validate_no_duplicate_fragments(text: str, path: Path) -> None:
    frontmatter = re.match(r"---\n.*?\n---\n", text, re.DOTALL)
    body = text[frontmatter.end() :] if frontmatter else text

    seen_headings: dict[str, int] = {}
    for match in re.finditer(r"^(#{1,2} .+)$", body, re.MULTILINE):
        heading = match.group(1).strip()
        line_number = body[: match.start()].count("\n") + 1
        if heading in seen_headings:
            fail(
                f"{path} repeats heading {heading!r} "
                f"at lines {seen_headings[heading]} and {line_number}"
            )
        seen_headings[heading] = line_number

    seen_blocks: dict[str, int] = {}
    for index, block in enumerate(re.split(r"\n\s*\n", body), 1):
        normalized = re.sub(r"\s+", " ", block.strip())
        if len(normalized) < 180:
            continue
        if normalized in seen_blocks:
            fail(f"{path} repeats a substantial text block at blocks {seen_blocks[normalized]} and {index}")
        seen_blocks[normalized] = index


def validate_skill(path: Path) -> None:
    text = path.read_text()
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        fail(f"{path} is {line_count} lines; skill files must stay at or below {MAX_SKILL_LINES}")
    if not text.endswith("\n"):
        fail(f"{path} must end with a newline")
    frontmatter_delimiters = sum(1 for line in text.splitlines() if line == "---")
    if frontmatter_delimiters != 2:
        fail(f"{path} must contain exactly one YAML frontmatter block")
    frontmatter = parse_frontmatter(text, path)
    expected_name = skill_name_for_path(path)
    name = frontmatter.get("name")
    description = frontmatter.get("description", "")

    if name != expected_name:
        fail(f"{path} frontmatter name {name!r} does not match file name {expected_name!r}")
    if not description:
        fail(f"{path} missing description")
    if not description.startswith("Use when"):
        fail(f"{path} description must start with 'Use when'")
    if len(description) > MAX_DESCRIPTION_CHARS:
        fail(
            f"{path} description is {len(description)} chars; "
            f"frontmatter descriptions must stay at or below {MAX_DESCRIPTION_CHARS}"
        )
    validate_no_duplicate_fragments(text, path)
    if expected_name == "staff-engineer-mode":
        validate_router_skill(text, path)
    else:
        validate_specialist_skill(text, path)

    validate_technology_agnostic_body(text, path)


def validate_codex_namespaced_length(skill_files: list[Path]) -> None:
    for path in skill_files:
        name = skill_name_for_path(path)
        namespaced = f"{CODEX_NAMESPACED_PREFIX}{name}"
        if len(namespaced) > CODEX_MAX_SKILL_NAME_LENGTH:
            fail(
                f"{path} name is too long for Codex namespaced install: "
                f"{namespaced!r} is {len(namespaced)} chars, max {CODEX_MAX_SKILL_NAME_LENGTH}"
            )


def validate_unique_skill_metadata(skill_files: list[Path]) -> None:
    seen_names: dict[str, Path] = {}
    seen_descriptions: dict[str, Path] = {}
    for path in skill_files:
        frontmatter = parse_frontmatter(path.read_text(), path)
        name = frontmatter["name"]
        description = frontmatter["description"]
        if name in seen_names:
            fail(f"{path} duplicates skill name already used by {seen_names[name]}")
        if description in seen_descriptions:
            fail(f"{path} duplicates description already used by {seen_descriptions[description]}")
        seen_names[name] = path
        seen_descriptions[description] = path


def skill_name_for_path(path: Path) -> str:
    if path.parent == SPECIALISTS and path.suffix == ".md":
        return path.stem
    return path.parent.name


def validate_skill_contract() -> None:
    if not SKILL_CONTRACT.exists():
        fail("shared skill contract is missing")


def validate_positive_routings(skill_files: list[Path]) -> None:
    if not SAMPLE_PROMPTS.exists():
        fail("evals/prompts/expected-routes.md is missing")

    specialist_names = {
        skill_name_for_path(path)
        for path in skill_files
        if skill_name_for_path(path) != "staff-engineer-mode"
    }
    text = SAMPLE_PROMPTS.read_text()
    sections: dict[str, int] = {}
    current: str | None = None
    count = 0
    for line in text.splitlines():
        heading = re.match(r"^### `([^`]+)`\s*$", line)
        if heading:
            if current is not None:
                sections[current] = count
            current = heading.group(1)
            count = 0
        elif current is not None and SAMPLE_PROMPT_RE.match(line):
            count += 1
    if current is not None:
        sections[current] = count

    section_names = set(sections)
    allowed_sections = specialist_names | {"none"}
    missing = specialist_names - section_names
    extra = section_names - allowed_sections
    if missing:
        fail(f"evals/prompts/expected-routes.md missing specialists: {', '.join(sorted(missing))}")
    if extra:
        fail(f"evals/prompts/expected-routes.md has unknown specialist sections: {', '.join(sorted(extra))}")
    if "none" not in section_names:
        fail("evals/prompts/expected-routes.md missing out-of-scope section: none")

    wrong_counts = {
        name: prompt_count
        for name, prompt_count in sections.items()
        if (name == "none" and prompt_count != 4)
        or (name != "none" and prompt_count != SAMPLE_PROMPTS_PER_SPECIALIST)
    }
    if wrong_counts:
        details = ", ".join(f"{name}={count}" for name, count in sorted(wrong_counts.items()))
        fail(
            "evals/prompts/expected-routes.md must list "
            f"{SAMPLE_PROMPTS_PER_SPECIALIST} prompts per specialist and 4 none prompts; found {details}"
        )

    if README.exists():
        readme = README.read_text()
        match = re.search(r"with (\w+) representative prompts", readme)
        if match and match.group(1).lower() != "four":
            fail(
                "README.md representative prompt count must match "
                f"evals/prompts/expected-routes.md ({SAMPLE_PROMPTS_PER_SPECIALIST})"
            )


def main() -> int:
    router_file = SKILLS / "staff-engineer-mode" / "SKILL.md"
    if not router_file.exists():
        fail("missing router skill at skills/staff-engineer-mode/SKILL.md")
    native_skill_files = sorted(path for path in SKILLS.glob("**/SKILL.md") if "_shared" not in path.parts)
    if native_skill_files != [router_file]:
        unexpected = [str(path.relative_to(ROOT)) for path in native_skill_files if path != router_file]
        fail(f"only the router may live under skills/; found {', '.join(unexpected)}")

    specialist_files = sorted(SPECIALISTS.glob("*.md"))
    if not specialist_files:
        fail("no routed specialists found under specialists/")

    skill_files = [router_file, *specialist_files]

    validate_codex_namespaced_length([router_file])
    validate_unique_skill_metadata(skill_files)
    validate_skill(router_file)
    for path in specialist_files:
        relative = path.relative_to(SPECIALISTS)
        if len(relative.parts) != 1 or path.suffix != ".md":
            fail(f"{path} must live at specialists/<specialist-name>.md")
        validate_skill(path)

    routing_matrix = SKILLS / "staff-engineer-mode" / "references" / "routing-matrix.md"
    if not routing_matrix.exists():
        fail("router routing matrix is missing")
    validate_router_boundary_split(router_file.read_text(), routing_matrix.read_text(), router_file, routing_matrix)

    validate_skill_contract()
    validate_positive_routings(skill_files)
    print(f"skill pack validation passed: 1 router skill, {len(specialist_files)} routed specialists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
