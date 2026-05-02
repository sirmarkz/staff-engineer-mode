#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SKILL_CONTRACT = SKILLS / "_shared" / "references" / "skill-contract.md"
CODEX_NAMESPACED_PREFIX = "staff-engineer-mode:"
CODEX_MAX_SKILL_NAME_LENGTH = 64
ROUTER_MAX_WORDS = 1200

COMMON_H2_ORDER = [
    "## Overview",
    "## Iron Law",
    "## When To Use",
    "## When Not To Use",
    "## Inputs To Collect",
    "## Workflow",
    "## Synthesized Default",
    "## Exceptions",
]

SPECIALIST_H2_ORDER = [
    *COMMON_H2_ORDER,
    "## Response Quality Bar",
    "## Required Outputs",
    "## Evidence Gates",
    "## Red Flags - Stop And Rework",
    "## Common Mistakes",
]

ROUTER_H2_ORDER = [
    *COMMON_H2_ORDER,
    "## Required Outputs",
    "## Evidence Gates",
    "## Routing Tiebreakers",
    "## Red Flags - Stop And Rework",
    "## Common Mistakes",
]

ROUTER_EVIDENCE_GATES = {
    "single_primary",
    "secondary_cap",
    "capability_translation",
    "scope_check",
    "ambiguity_check",
}

FORBIDDEN_SOURCE_HEADINGS = [
    "## References",
    "## Sources",
    "## Source References",
    "## Reading List",
    "## Bibliography",
    "## Citations",
    "## Further Reading",
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


def h2_headings(text: str) -> list[str]:
    return re.findall(r"^## .+$", text, re.MULTILINE)


def section_body(text: str, heading: str, path: Path) -> str:
    pattern = rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        fail(f"{path} missing section {heading}")
    return match.group("body")


def validate_h2_order(text: str, path: Path, expected_headings: list[str]) -> None:
    actual_headings = h2_headings(text)
    if actual_headings != expected_headings:
        fail(
            f"{path} headings must be exactly {expected_headings!r}; "
            f"found {actual_headings!r}"
        )


def validate_no_source_sections(text: str, path: Path) -> None:
    headings = set(h2_headings(text))
    forbidden = sorted(headings.intersection(FORBIDDEN_SOURCE_HEADINGS))
    if forbidden:
        fail(f"{path} must not contain per-skill source sections: {', '.join(forbidden)}")


def evidence_gate_ids(text: str, path: Path) -> list[str]:
    evidence_body = section_body(text, "## Evidence Gates", path)
    return re.findall(r"^- `([^`]+)`:", evidence_body, re.MULTILINE)


def validate_specialist_skill(text: str, path: Path) -> None:
    validate_h2_order(text, path, SPECIALIST_H2_ORDER)
    gates = evidence_gate_ids(text, path)
    if len(gates) < 3:
        fail(f"{path} needs at least three evidence gates under ## Evidence Gates")
    if "Stay technology-agnostic by default" not in section_body(text, "## Response Quality Bar", path):
        fail(f"{path} Response Quality Bar must require technology-agnostic guidance by default")


def validate_router_skill(text: str, path: Path) -> None:
    validate_h2_order(text, path, ROUTER_H2_ORDER)
    word_count = len(re.findall(r"\S+", text))
    if word_count > ROUTER_MAX_WORDS:
        fail(f"{path} is {word_count} words; compact router skills must stay under {ROUTER_MAX_WORDS}")
    gate_ids = set(evidence_gate_ids(text, path))
    missing = ROUTER_EVIDENCE_GATES - gate_ids
    if missing:
        fail(f"{path} missing router evidence gates: {', '.join(sorted(missing))}")
    required_phrases = [
        "For low-confidence routing: questions only.",
        "Do not include a primary, secondary, confidence label, routing draft, candidate list, or any specialist skill names.",
        "expose zero skill names",
        "Do not invent tool, vendor, framework, protocol, database, or command examples",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"{path} must require low-confidence routing to ask questions without exposing skill names")


def validate_skill(path: Path) -> None:
    text = path.read_text()
    frontmatter = parse_frontmatter(text, path)
    expected_name = path.parent.name
    name = frontmatter.get("name")
    description = frontmatter.get("description", "")

    if name != expected_name:
        fail(f"{path} frontmatter name {name!r} does not match directory {expected_name!r}")
    if not description:
        fail(f"{path} missing description")
    if len(description) > 600:
        fail(f"{path} description is too long")
    if expected_name == "staff-engineer-mode":
        if not description.startswith("Use to "):
            fail(f"{path} router description must start with 'Use to '")
        validate_router_skill(text, path)
    elif not description.startswith("Use when "):
        fail(f"{path} description must start with 'Use when '")
    else:
        validate_specialist_skill(text, path)

    if "TODO" in text or "TBD" in text:
        fail(f"{path} contains placeholder text")

    validate_no_source_sections(text, path)
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
    contract = SKILL_CONTRACT.read_text()
    for heading in SPECIALIST_H2_ORDER:
        if heading not in contract:
            fail(f"{SKILL_CONTRACT} does not document required heading {heading}")
    for heading in FORBIDDEN_SOURCE_HEADINGS:
        if heading in contract:
            fail(f"{SKILL_CONTRACT} reintroduces forbidden per-skill source heading {heading}")


def main() -> int:
    skill_files = sorted(path for path in SKILLS.glob("**/SKILL.md") if "_shared" not in path.parts)
    if not skill_files:
        fail("no skills found")

    validate_codex_namespaced_length(skill_files)
    validate_unique_skill_metadata(skill_files)
    for path in skill_files:
        relative = path.relative_to(SKILLS)
        if len(relative.parts) != 2:
            fail(f"{path} must live at skills/<skill-name>/SKILL.md")
        validate_skill(path)

    router_eval = SKILLS / "staff-engineer-mode" / "references" / "router-eval-set.yaml"
    routing_matrix = SKILLS / "staff-engineer-mode" / "references" / "routing-matrix.md"
    if not router_eval.exists():
        fail("router eval fixture is missing")
    if not routing_matrix.exists():
        fail("router routing matrix is missing")

    validate_skill_contract()
    print(f"skill pack validation passed: {len(skill_files)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
