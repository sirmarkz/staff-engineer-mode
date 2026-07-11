#!/usr/bin/env python3
"""Shared validation contract for Staff Engineer Mode.

Keep manifest description copy and specialist vendor-name lists here so
platform validators, skill-pack validation, and brand linting cannot drift.
"""

from __future__ import annotations

CANONICAL_PLUGIN_DESCRIPTION = (
    "Applies engineering best practices to reliability, security, delivery, "
    "data, and architecture work."
)

CLAUDE_PLUGIN_DESCRIPTION = (
    CANONICAL_PLUGIN_DESCRIPTION
)

CODEX_INTERFACE_SHORT_DESCRIPTION = (
    CANONICAL_PLUGIN_DESCRIPTION
)

CODEX_INTERFACE_LONG_DESCRIPTION = (
    "Technology-agnostic guidance for applying engineering best practices "
    "to architecture, reliability, resilience, delivery, operations, security, "
    "privacy, data, platform, client, and cost-aware reliability work. The router "
    "automatically selects the smallest useful routed specialist set from natural-"
    "language engineering requests."
)

MANIFEST_DESCRIPTION_FIELDS: dict[str, str] = {
    "package.json:description": CANONICAL_PLUGIN_DESCRIPTION,
    "gemini-extension.json:description": CANONICAL_PLUGIN_DESCRIPTION,
    ".codex-plugin/plugin.json:description": CANONICAL_PLUGIN_DESCRIPTION,
    ".codex-plugin/plugin.json:interface.shortDescription": CODEX_INTERFACE_SHORT_DESCRIPTION,
    ".codex-plugin/plugin.json:interface.longDescription": CODEX_INTERFACE_LONG_DESCRIPTION,
    ".cursor-plugin/plugin.json:description": CANONICAL_PLUGIN_DESCRIPTION,
    ".claude-plugin/plugin.json:description": CLAUDE_PLUGIN_DESCRIPTION,
    ".claude-plugin/marketplace.json:description": CLAUDE_PLUGIN_DESCRIPTION,
    ".claude-plugin/marketplace.json:plugins.0.description": CLAUDE_PLUGIN_DESCRIPTION,
}

ROUTER_EVAL_CHECKS: tuple[str, ...] = (
    "single_primary",
    "secondary_cap",
    "capability_translation",
    "scope_check",
    "ambiguity_check",
    "intent_inference",
    "no_skill_invoke",
)

ROUTER_ROUTING_CHECKS: tuple[str, ...] = (
    "single_primary",
    "secondary_cap",
    "capability_translation",
    "scope_check",
    "ambiguity_check",
)

ROUTER_SAMPLE_PROMPT_CHECKS: tuple[str, ...] = (
    "single_primary",
    "intent_inference",
    "no_skill_invoke",
)

PROHIBITED_SPECIALIST_BODY_TERMS: tuple[str, ...] = (
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
)

BRAND_LINTER_SPECIALIST_VENDOR_NAMES: tuple[str, ...] = (
    "AWS",
    "Azure",
    "GCP",
    "Google Cloud",
    "Kubernetes",
    "Terraform",
    "Docker",
    "Datadog",
    "Splunk",
    "PagerDuty",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Kafka",
    "Redis",
    "Snowflake",
    "BigQuery",
    "DynamoDB",
    "Prometheus",
    "Grafana",
    "GitHub",
    "GitLab",
    "Jenkins",
    "React",
    "Django",
)
