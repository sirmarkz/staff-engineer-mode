#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SPECIALISTS = ROOT / "specialists"
README = ROOT / "README.md"
SAMPLE_PROMPTS = ROOT / "SAMPLE-PROMPTS.md"
SKILL_CONTRACT = SKILLS / "_shared" / "references" / "skill-contract.md"
CODEX_NAMESPACED_PREFIX = "staff-engineer-mode:"
CODEX_MAX_SKILL_NAME_LENGTH = 64
MAX_SKILL_LINES = 300
MAX_DESCRIPTION_CHARS = 120
SAMPLE_PROMPTS_PER_SPECIALIST = 4
ROUTER_MAX_WORDS = 1600
ROUTER_TIEBREAKER_MAX_WORDS = 260
SAMPLE_PROMPT_RE = re.compile(r'^- ".+"$')
ROUTER_EVIDENCE_GATES = {
    "single_primary",
    "secondary_cap",
    "capability_translation",
    "scope_check",
    "ambiguity_check",
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
}

SPECIALIST_OPERATIONAL_SECTIONS = [
    "## When To Use",
    "## When Not To Use",
    "## Inputs To Collect",
    "## Workflow",
    "## Synthesized Default",
    "## Phase Behavior",
    "## Exceptions",
    "## Response Quality Bar",
    "## Required Outputs",
    "## Evidence Gates",
    "## Red Flags - Stop And Rework",
    "## Common Mistakes",
]

PHASE_BEHAVIOR_TERMS = {
    "ideation": ["ideation", "risks", "options"],
    "design": ["design", "tradeoffs", "gates"],
    "development": ["development", "sequencing", "checks"],
    "testing": ["testing", "tests", "failure"],
    "release": ["release", "rollout", "rollback"],
    "maintenance": ["maintenance", "owners", "drift"],
    "existing artifact": ["existing artifact", "evidence", "engineering decision"],
    "missing evidence": ["missing evidence", "assumptions", "evidence plan"],
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
    "signals, not hard gates",
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

ROUTER_EVAL_SCOPE_TERMS = [
    "eval-harness",
    "confident in-scope routing",
    "never emit a routing block",
    "low-confidence",
    "ambiguous",
    "out-of-scope",
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
    "## Evidence Gates",
    "## Routing Tiebreakers",
    "## Red Flags - Stop And Rework",
    "## Common Mistakes",
]

PROHIBITED_BODY_TERMS = [
    "Amazon",
    "AWS",
    "Azure",
    "Auth0",
    "GCP",
    "Google",
    "Datadog",
    "New Relic",
    "Splunk",
    "Sentry",
    "PagerDuty",
    "Opsgenie",
    "Kubernetes",
    "K8s",
    "EKS",
    "GKE",
    "AKS",
    "ECS",
    "Fargate",
    "Terraform",
    "Argo",
    "Argo CD",
    "OPA",
    "Rego",
    "Istio",
    "Envoy",
    "Linkerd",
    "Consul",
    "PostgreSQL",
    "Postgres",
    "MySQL",
    "Redis",
    "Memcached",
    "Kafka",
    "Pulsar",
    "RabbitMQ",
    "Cassandra",
    "MongoDB",
    "Spark",
    "Flink",
    "Snowflake",
    "BigQuery",
    "DynamoDB",
    "Spanner",
    "RDS",
    "Aurora",
    "Elasticsearch",
    "OpenSearch",
    "S3",
    "Lambda",
    "CloudFront",
    "Cloudflare",
    "Fastly",
    "CDN",
    "WAF",
    "React",
    "Vue",
    "Angular",
    "Next.js",
    "Tailwind",
    "Express.js",
    "Django",
    "FastAPI",
    "Vercel",
    "Netlify",
    "Node",
    "npm",
    "iOS",
    "Android",
    "Swift",
    "Kotlin",
    "Docker",
    "OpenTelemetry",
    "Prometheus",
    "Grafana",
    "Vault",
    "Okta",
    "Jira",
    "GitHub",
    "GitLab",
    "Jenkins",
    "CircleCI",
    "Buildkite",
    "Bazel",
    "Helm",
    "GraphQL",
    "gRPC",
    "REST",
    "OWASP",
    "OAuth",
    "OIDC",
    "JWT",
    "mTLS",
    "SLSA",
    "SBOM",
    "SBOMs",
    "Sigstore",
    "Cosign",
    "in-toto",
    "RAG",
    "CVE",
    "CVSS",
    "EPSS",
    "KEV",
    "SOC 2",
    "PCI",
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
        for term in PROHIBITED_BODY_TERMS:
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


def evidence_gate_ids(text: str, path: Path) -> list[str]:
    evidence_body = section_body(text, "## Evidence Gates", path)
    return re.findall(r"^- `([^`]+)`:", evidence_body, re.MULTILINE)


def evidence_gate_bodies(text: str, path: Path) -> dict[str, str]:
    evidence_body = section_body(text, "## Evidence Gates", path)
    return {
        match.group("id"): match.group("body")
        for match in re.finditer(r"^- `(?P<id>[^`]+)`:\s*(?P<body>.+)$", evidence_body, re.MULTILINE)
    }


def require_gate_terms(gate_bodies: dict[str, str], gate_id: str, terms: list[str], path: Path) -> None:
    body = gate_bodies.get(gate_id, "").lower()
    missing = [term for term in terms if term not in body]
    if missing:
        fail(f"{path} gate {gate_id!r} missing behavior terms: {', '.join(missing)}")


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


def validate_router_eval_scope(text: str, path: Path) -> None:
    lowered = text.lower()
    missing = [term for term in ROUTER_EVAL_SCOPE_TERMS if term not in lowered]
    if missing:
        fail(f"{path} missing eval-harness scope terms: {', '.join(missing)}")


def validate_decision_guide_framing(text: str, path: Path) -> None:
    slug = path.parent.name
    if slug in AUDIT_ONLY_EXCEPTIONS:
        return
    sections = [
        section_body(text, "## When To Use", path),
        section_body(text, "## Inputs To Collect", path),
        section_body(text, "## Workflow", path),
        section_body(text, "## Required Outputs", path),
    ]
    joined = "\n".join(sections).lower()
    required = ["decision", "evidence", "assumptions"]
    missing = [term for term in required if term not in joined]
    if missing:
        fail(f"{path} decision-guide framing missing: {', '.join(missing)}")
    for pattern in AUDIT_ONLY_ANTI_PATTERNS:
        if pattern in joined:
            fail(f"{path} has audit-only framing pattern: {pattern}")


def validate_specialist_skill(text: str, path: Path) -> None:
    slug = path.parent.name
    description = parse_frontmatter(text, path)["description"].lower()
    if slug not in SPECIALIST_DESCRIPTION_REVIEW_EXCEPTIONS:
        for term in ["review", "audit"]:
            if term in description:
                fail(f"{path} description must trigger decision/design work, not {term}-only work")
    validate_operational_sections(text, path, SPECIALIST_OPERATIONAL_SECTIONS)
    validate_phase_behavior(text, path)
    validate_decision_guide_framing(text, path)
    gates = evidence_gate_ids(text, path)
    if len(gates) < 3:
        fail(f"{path} needs at least three evidence gates under ## Evidence Gates")


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
    validate_router_eval_scope(text, path)
    word_count = len(re.findall(r"\S+", text))
    if word_count > ROUTER_MAX_WORDS:
        fail(f"{path} is {word_count} words; compact router skills must stay under {ROUTER_MAX_WORDS}")
    gate_ids = set(evidence_gate_ids(text, path))
    missing = ROUTER_EVIDENCE_GATES - gate_ids
    if missing:
        fail(f"{path} missing router evidence gates: {', '.join(sorted(missing))}")
    gate_bodies = evidence_gate_bodies(text, path)
    require_gate_terms(gate_bodies, "capability_translation", ["tool", "translated", "not repeated"], path)
    require_gate_terms(gate_bodies, "scope_check", ["out-of-scope", "without specialist names"], path)
    require_gate_terms(gate_bodies, "ambiguity_check", ["ambiguous", "infer", "intake questions", "specialist names"], path)


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
        fail(f"{path} is {line_count} lines; SKILL.md files must stay at or below {MAX_SKILL_LINES}")
    if not text.endswith("\n"):
        fail(f"{path} must end with a newline")
    frontmatter_delimiters = sum(1 for line in text.splitlines() if line == "---")
    if frontmatter_delimiters != 2:
        fail(f"{path} must contain exactly one YAML frontmatter block")
    frontmatter = parse_frontmatter(text, path)
    expected_name = path.parent.name
    name = frontmatter.get("name")
    description = frontmatter.get("description", "")

    if name != expected_name:
        fail(f"{path} frontmatter name {name!r} does not match directory {expected_name!r}")
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
        name = path.parent.name
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


def validate_skill_contract() -> None:
    if not SKILL_CONTRACT.exists():
        fail("shared skill contract is missing")


def validate_sample_prompts(skill_files: list[Path]) -> None:
    if not SAMPLE_PROMPTS.exists():
        fail("SAMPLE-PROMPTS.md is missing")

    specialist_names = {
        path.parent.name for path in skill_files if path.parent.name != "staff-engineer-mode"
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
    missing = specialist_names - section_names
    extra = section_names - specialist_names
    if missing:
        fail(f"SAMPLE-PROMPTS.md missing specialists: {', '.join(sorted(missing))}")
    if extra:
        fail(f"SAMPLE-PROMPTS.md has unknown specialist sections: {', '.join(sorted(extra))}")

    wrong_counts = {
        name: prompt_count
        for name, prompt_count in sections.items()
        if prompt_count != SAMPLE_PROMPTS_PER_SPECIALIST
    }
    if wrong_counts:
        details = ", ".join(f"{name}={count}" for name, count in sorted(wrong_counts.items()))
        fail(
            "SAMPLE-PROMPTS.md must list "
            f"{SAMPLE_PROMPTS_PER_SPECIALIST} prompts per specialist; found {details}"
        )

    if README.exists():
        readme = README.read_text()
        match = re.search(r"with (\w+) representative prompts", readme)
        if match and match.group(1).lower() != "four":
            fail(
                "README.md representative prompt count must match "
                f"SAMPLE-PROMPTS.md ({SAMPLE_PROMPTS_PER_SPECIALIST})"
            )


def main() -> int:
    router_file = SKILLS / "staff-engineer-mode" / "SKILL.md"
    if not router_file.exists():
        fail("missing router skill at skills/staff-engineer-mode/SKILL.md")
    native_skill_files = sorted(path for path in SKILLS.glob("**/SKILL.md") if "_shared" not in path.parts)
    if native_skill_files != [router_file]:
        unexpected = [str(path.relative_to(ROOT)) for path in native_skill_files if path != router_file]
        fail(f"only the router may live under skills/; found {', '.join(unexpected)}")

    specialist_files = sorted(SPECIALISTS.glob("*/SKILL.md"))
    if not specialist_files:
        fail("no routed specialists found under specialists/")

    skill_files = [router_file, *specialist_files]

    validate_codex_namespaced_length([router_file])
    validate_unique_skill_metadata(skill_files)
    validate_skill(router_file)
    for path in specialist_files:
        relative = path.relative_to(SPECIALISTS)
        if len(relative.parts) != 2:
            fail(f"{path} must live at specialists/<specialist-name>/SKILL.md")
        validate_skill(path)

    router_eval = SKILLS / "staff-engineer-mode" / "references" / "router-eval-set.yaml"
    routing_matrix = SKILLS / "staff-engineer-mode" / "references" / "routing-matrix.md"
    if not router_eval.exists():
        fail("router eval fixture is missing")
    if not routing_matrix.exists():
        fail("router routing matrix is missing")
    validate_router_boundary_split(router_file.read_text(), routing_matrix.read_text(), router_file, routing_matrix)

    validate_skill_contract()
    validate_sample_prompts(skill_files)
    print(f"skill pack validation passed: 1 router skill, {len(specialist_files)} routed specialists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
