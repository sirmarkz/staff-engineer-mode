#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
import random
import re
import shlex
import signal
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from eval_adapter_protocol import (
    AdapterSettings,
    adapter_failure_message,
    build_adapter_environment,
    open_exclusive_file,
    open_exclusive_file_at,
    reserve_directory_at,
    reserve_run_directory,
    resolve_adapter_settings as resolve_protocol_settings,
)
from staff_engineer_mode_contract import ROUTER_EVAL_CHECKS, ROUTER_SAMPLE_PROMPT_CHECKS

POSITIVE_ROUTING_PROMPTS = ROOT / "evals" / "prompts" / "expected-routes.md"
ROUTER_CONTRACT_PROMPTS = ROOT / "evals" / "prompts" / "router-contracts.md"
ADVERSARIAL_SPLIT_PROMPTS = ROOT / "evals" / "prompts" / "adversarial-split.md"
ADVERSARIAL_SPLIT_DRAFT = ROOT / "evals" / "prompts" / "adversarial-split-draft.json"
ADVERSARIAL_SPLIT_REVIEW = ROOT / "evals" / "prompts" / "adversarial-split-review.json"
ADVERSARIAL_SPLIT_PROVENANCE_PATHS = (
    ADVERSARIAL_SPLIT_DRAFT,
    ADVERSARIAL_SPLIT_PROMPTS,
    ADVERSARIAL_SPLIT_REVIEW,
)
BOUNDARY_PROMPT_DIR = ROOT / "evals" / "prompts"
BOUNDARY_PROMPT_FILES = {
    "negative": BOUNDARY_PROMPT_DIR / "negative.md",
    "near_miss": BOUNDARY_PROMPT_DIR / "near-miss.md",
    "keyword_bait": BOUNDARY_PROMPT_DIR / "keyword-bait.md",
    "adversarial": BOUNDARY_PROMPT_DIR / "adversarial.md",
}
SKILLS = ROOT / "skills"
SPECIALISTS = ROOT / "specialists"
ROUTER_CONTEXT_PATHS = (
    ROOT / "skills" / "staff-engineer-mode" / "SKILL.md",
    ROOT / "skills" / "staff-engineer-mode" / "references" / "routing-matrix.md",
)
ADAPTER_PROTOCOL_PATH = SCRIPT_DIR / "eval_adapter_protocol.py"
ROUTING_BLOCK_RE = re.compile(r"```routing\s*(?P<body>.*?)```", re.DOTALL)
ROUTING_BLOCK_FIELDS = {
    "primary",
    "secondary",
    "confidence",
    "artifact",
    "surface",
    "phase",
    "rationale",
}
CUSTOM_EVAL_REQUIRED_FIELDS = {
    "prompt",
    "expected_primary",
    "expected_behavior",
    "category",
    "expected_checks",
}
CUSTOM_EVAL_OPTIONAL_FIELDS = {
    "expected_secondary",
    "expected_phase",
    "forbidden_in_response",
    "target_specialist",
}
ALLOWED_ROUTING_PHASES = {
    "ideation",
    "design",
    "development",
    "testing",
    "before merge",
    "release",
    "migration",
    "active incident",
    "post-incident",
    "regression",
    "readiness",
    "maintenance",
}
LOW_CONFIDENCE_PRIMARIES = {"staff-engineer-mode", "none"}
TOOL_BAIT_TERMS = [
    "argocd",
    "argo cd",
    "cache product",
    "datadog",
    "graphql",
    "istio",
]
SPECIALIST_HEADING_RE = re.compile(r"^### `(?P<slug>[^`]+)`$")
PROMPT_RE = re.compile(r'^- "(?P<prompt>.+)"$')
BOUNDARY_PROMPT_RE = re.compile(
    r'^- "(?P<prompt>.+)" '
    r"\(-> `(?P<expected_primary>[^`]+)`\)$"
)
PHASE_DIVERSITY_EXCEPTIONS = {
    "agent-pr-review",
    "incident-response-and-postmortems",
    "production-readiness-review",
    "vulnerability-management",
}
PHASE_HINTS = {
    "ideation": ["idea", "ideating", "decide", "choose", "propose", "recommend", "draft"],
    "design": [
        "design",
        "shape",
        "define",
        "tradeoff",
        "boundary",
        "target",
        "requirements",
        "policy",
        "names",
        "template",
        "scorecard",
        "tenant",
        "topology",
        "workflow",
        "producer",
        "consumer",
        "migration",
    ],
    "development": ["development", "implement", "code", "repo", "branch", "changed files", "code path", "inspect", "ci"],
    "testing": [
        "test",
        "tests",
        "eval",
        "fixture",
        "failure",
        "prove",
        "verify",
        "coverage",
        "regression",
        "correctness",
        "safe",
        "runtime errors",
        "latency budgets",
        "threat-model",
        "cannot reach",
        "narrow down",
    ],
    "release": [
        "release",
        "rollout",
        "launch",
        "ship",
        "rollback",
        "go/no-go",
        "merge",
        "approve",
        "promoted",
        "transition",
        "degradation",
        "outage",
        "migration",
        "pr ",
    ],
    "maintenance": [
        "maintenance",
        "cleanup",
        "drift",
        "owner",
        "expiry",
        "refresh",
        "stale",
        "inventory",
        "remove",
        "retirement",
        "rotation",
        "freshness",
        "runbook",
    ],
}
CONTEXT_ONLY_HINTS = [
    "timeout",
    "duplicate work",
    "old branches",
    "lose work",
    "suspicious spikes",
    "protect origin",
]
EXPLICIT_PHASE_WORDS = [
    "ideation",
    "ideating",
    "idea",
    "design",
    "development",
    "develop",
    "implementation",
    "implement",
    "testing",
    "test",
    "release",
    "rollout",
    "launch",
    "maintenance",
    "maintain",
    "review",
    "audit",
]


class CaseResult(NamedTuple):
    case_id: str
    category: str
    expected_primary: str
    actual_primary: str | None
    passed: bool
    failures: list[str]
    response: str = ""
    structured_output: dict[str, Any] | None = None


class SavedResponse(NamedTuple):
    text: str
    sha256: str


def fail(message: str) -> None:
    print(f"router eval failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
        if isinstance(parsed, str):
            return parsed
    return value


def inline_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"expected inline list, found {value!r}")
    body = value[1:-1].strip()
    if not body:
        return []
    return [scalar(part.strip()) for part in body.split(",")]


def parse_value(key: str, value: str) -> str | list[str]:
    if key in {"expected_checks", "forbidden_in_response"}:
        return inline_list(value)
    return scalar(value)


def parse_cases(text: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        if line.startswith("  - "):
            if current is not None:
                cases.append(current)
            current = {}
            remainder = line[4:]
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = parse_value(key.strip(), value)
            continue
        if current is not None and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key.strip()] = parse_value(key.strip(), value)
    if current is not None:
        cases.append(current)
    return cases


def validate_custom_eval_cases(cases: list[dict[str, Any]], path: Path) -> None:
    if not cases:
        fail(f"{path} produced no eval cases")
    known = set(specialist_names())
    valid_primaries = known | LOW_CONFIDENCE_PRIMARIES
    valid_forbidden = known | {"all_specialist_names"}
    allowed_fields = CUSTOM_EVAL_REQUIRED_FIELDS | CUSTOM_EVAL_OPTIONAL_FIELDS
    for index, case in enumerate(cases, 1):
        missing = CUSTOM_EVAL_REQUIRED_FIELDS - set(case)
        extra = set(case) - allowed_fields
        if missing or extra:
            fail(
                f"{path} case {index} fields mismatch: "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
        for field in ("prompt", "expected_behavior", "category"):
            if not isinstance(case[field], str) or not case[field].strip():
                fail(f"{path} case {index} {field} must be a non-empty string")
        primary = case["expected_primary"]
        if not isinstance(primary, str) or primary not in valid_primaries:
            fail(f"{path} case {index} has unknown expected_primary {primary!r}")
        phase = case.get("expected_phase")
        if phase is not None and phase not in ALLOWED_ROUTING_PHASES:
            fail(f"{path} case {index} has unknown expected_phase {phase!r}")
        secondary = case.get("expected_secondary")
        if secondary is not None and secondary not in known:
            fail(f"{path} case {index} has unknown expected_secondary {secondary!r}")
        target = case.get("target_specialist")
        if target is not None and target not in known:
            fail(f"{path} case {index} has unknown target_specialist {target!r}")
        checks = case["expected_checks"]
        if not isinstance(checks, list) or not checks or not all(
            isinstance(check, str) and check for check in checks
        ):
            fail(f"{path} case {index} expected_checks must be a non-empty string list")
        unknown_checks = sorted(set(checks) - set(ROUTER_EVAL_CHECKS))
        if unknown_checks:
            fail(f"{path} case {index} has unknown expected_checks {unknown_checks}")
        if primary not in LOW_CONFIDENCE_PRIMARIES:
            for required_check in ("single_primary", "intent_inference"):
                if required_check not in checks:
                    fail(
                        f"{path} case {index} routed case must include "
                        f"{required_check!r}"
                    )
        if secondary is not None and "secondary_cap" not in checks:
            fail(
                f"{path} case {index} with expected_secondary must include "
                "'secondary_cap'"
            )
        forbidden = case.get("forbidden_in_response", [])
        if not isinstance(forbidden, list) or not all(
            isinstance(value, str) and value in valid_forbidden for value in forbidden
        ):
            fail(
                f"{path} case {index} forbidden_in_response must contain only "
                "known specialist names or all_specialist_names"
            )
        if primary == "none" and (
            "scope_check" not in checks or not forbidden
        ):
            fail(
                f"{path} case {index} out-of-scope case needs scope_check and "
                "forbidden_in_response"
            )
        if primary == "staff-engineer-mode" and (
            "ambiguity_check" not in checks or not forbidden
        ):
            fail(
                f"{path} case {index} ambiguous case needs ambiguity_check and "
                "forbidden_in_response"
            )


def load_custom_eval_cases(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"custom eval file {path} is not valid UTF-8: {exc}")
    except OSError as exc:
        fail(f"cannot read custom eval file {path}: {exc}")
    try:
        cases = parse_cases(text)
    except ValueError as exc:
        fail(f"cannot parse custom eval file {path}: {exc}")
    validate_custom_eval_cases(cases, path)
    prefix = re.sub(r"[^a-z0-9-]+", "-", path.stem.lower()).strip("-")
    return assign_catalog_case_ids(cases, f"file-{prefix or 'catalog'}")


def specialist_names() -> list[str]:
    return sorted(path.stem for path in SPECIALISTS.glob("*.md"))


def parse_positive_routings(path: Path = POSITIVE_ROUTING_PROMPTS) -> list[dict[str, Any]]:
    known = set(specialist_names())
    seen_headings: set[str] = set()
    counts: dict[str, int] = {}
    phase_counts = {phase: 0 for phase in PHASE_HINTS}
    phase_by_slug: dict[str, set[str]] = {}
    context_only_count = 0
    cases: list[dict[str, Any]] = []
    current: str | None = None

    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        heading = SPECIALIST_HEADING_RE.match(line)
        if heading:
            current = heading.group("slug")
            seen_headings.add(current)
            counts.setdefault(current, 0)
            if current not in known | {"none"}:
                fail(f"{path}:{line_number} unknown specialist heading {current!r}")
            continue

        prompt_match = PROMPT_RE.match(line)
        if prompt_match:
            if current is None:
                fail(f"{path}:{line_number} prompt appears before a specialist heading")
            prompt = prompt_match.group("prompt")
            counts[current] = counts.get(current, 0) + 1
            prompt_lower = prompt.lower()
            prompt_phases = {
                phase for phase, hints in PHASE_HINTS.items() if any(hint in prompt_lower for hint in hints)
            }
            for phase in prompt_phases:
                phase_counts[phase] += 1
                phase_by_slug.setdefault(current, set()).add(phase)
            if (
                not any(word in prompt_lower for word in EXPLICIT_PHASE_WORDS)
                and any(hint in prompt_lower for hint in CONTEXT_ONLY_HINTS)
            ):
                context_only_count += 1
            if current == "none":
                cases.append(
                    {
                        "prompt": prompt,
                        "expected_primary": "none",
                        "expected_behavior": "withhold routing for out-of-scope prompt without naming specialists",
                        "category": "out_of_scope",
                        "expected_checks": ["scope_check"],
                        "forbidden_in_response": ["all_specialist_names"],
                    }
                )
            else:
                cases.append(
                    {
                        "prompt": prompt,
                        "expected_primary": current,
                        "expected_behavior": "route positive routing prompt to its grouped specialist",
                        "category": "positive_routing",
                        "expected_checks": list(ROUTER_SAMPLE_PROMPT_CHECKS),
                    }
                )

    missing = sorted(known - seen_headings)
    if missing:
        fail(f"{path} missing specialist headings: {', '.join(missing)}")
    if "none" not in seen_headings:
        fail(f"{path} missing out-of-scope heading: none")

    bad_counts = {
        slug: count
        for slug, count in counts.items()
        if (slug == "none" and count != 4) or (slug != "none" and count != 5)
    }
    if bad_counts:
        details = ", ".join(f"{slug}={count}" for slug, count in sorted(bad_counts.items()))
        fail(f"{path} must have exactly five prompts per specialist and four none prompts: {details}")

    if not cases:
        fail(f"{path} produced no positive routing prompt cases")

    missing_phases = [phase for phase, count in phase_counts.items() if count == 0]
    if missing_phases:
        fail(f"{path} positive routing prompts do not cover lifecycle phases: {', '.join(missing_phases)}")

    if context_only_count < 4:
        fail(f"{path} needs at least four context-only prompts without explicit lifecycle phase words")

    low_diversity = []
    for slug in sorted(known - PHASE_DIVERSITY_EXCEPTIONS):
        phases = phase_by_slug.get(slug, set())
        if len(phases) < 3:
            low_diversity.append(f"{slug}={','.join(sorted(phases)) or 'none'}")
    if low_diversity:
        fail(
            f"{path} positive routing prompts need at least three lifecycle phases per non-exception specialist: "
            + "; ".join(low_diversity)
        )

    return cases


def parse_boundary_prompt_file(path: Path, category: str) -> list[dict[str, Any]]:
    if not path.exists():
        fail(f"missing boundary router eval catalog {path.relative_to(ROOT)}")
    known = set(specialist_names())
    cases: list[dict[str, Any]] = []
    current: str | None = None

    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        heading = SPECIALIST_HEADING_RE.match(line)
        if heading:
            current = heading.group("slug")
            if current not in known:
                fail(f"{path}:{line_number} unknown specialist heading {current!r}")
            continue

        prompt_match = BOUNDARY_PROMPT_RE.match(line)
        if not prompt_match:
            continue
        if current is None:
            fail(f"{path}:{line_number} prompt appears before a specialist heading")

        expected_primary = prompt_match.group("expected_primary")
        checks = ["scope_check"] if expected_primary == "none" else ["single_primary", "intent_inference"]
        if category == "adversarial":
            checks.append("no_skill_invoke")
        case: dict[str, Any] = {
            "target_specialist": current,
            "prompt": prompt_match.group("prompt"),
            "expected_primary": expected_primary,
            "expected_behavior": (
                f"withhold routing; {current} must not fire"
                if expected_primary == "none"
                else f"route to {expected_primary}; {current} must not fire"
            ),
            "category": category,
            "expected_checks": checks,
        }
        if expected_primary == "none":
            case["forbidden_in_response"] = ["all_specialist_names"]
        cases.append(case)

    if not cases:
        fail(f"{path} produced no boundary eval cases")
    return cases


def parse_boundary_prompts(paths: dict[str, Path] = BOUNDARY_PROMPT_FILES) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for category in ["negative", "near_miss", "keyword_bait", "adversarial"]:
        cases.extend(parse_boundary_prompt_file(paths[category], category))
    return cases


def select_sample_cases(cases: list[dict[str, Any]], sample: str) -> list[dict[str, Any]]:
    if sample == "all":
        return cases
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        grouped.setdefault(str(case["expected_primary"]), []).append(case)
    selected: list[dict[str, Any]] = []
    for offset, primary in enumerate(sorted(grouped)):
        prompts = grouped[primary]
        selected.append(prompts[offset % len(prompts)])
    return selected


def assign_catalog_case_ids(
    cases: list[dict[str, Any]], catalog_prefix: str
) -> list[dict[str, Any]]:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", catalog_prefix):
        fail(f"unsafe catalog case ID prefix {catalog_prefix!r}")
    assigned: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for case in cases:
        item = dict(case)
        normalized_prompt = " ".join(str(item["prompt"]).casefold().split())
        fingerprint = hashlib.sha256(normalized_prompt.encode("utf-8")).hexdigest()[:16]
        result_id = f"{catalog_prefix}-{fingerprint}"
        if result_id in seen:
            fail(
                f"catalog case ID collision {result_id!r} for prompts "
                f"{seen[result_id]!r} and {item['prompt']!r}"
            )
        seen[result_id] = str(item["prompt"])
        item["_case_id"] = result_id
        assigned.append(item)
    return assigned


def load_catalog_cases(catalog: str, sample: str) -> list[dict[str, Any]]:
    if catalog in {"positive", "sample"}:
        return select_sample_cases(
            assign_catalog_case_ids(parse_positive_routings(), "positive"), sample
        )
    if catalog == "boundary":
        return assign_catalog_case_ids(
            parse_boundary_prompts()
            + parse_cases(ADVERSARIAL_SPLIT_PROMPTS.read_text(encoding="utf-8")),
            "boundary",
        )
    if catalog == "adversarial-split":
        return assign_catalog_case_ids(
            parse_cases(ADVERSARIAL_SPLIT_PROMPTS.read_text(encoding="utf-8")),
            "boundary",
        )
    if catalog == "contract":
        return assign_catalog_case_ids(
            parse_cases(ROUTER_CONTRACT_PROMPTS.read_text()), "contract"
        )
    if catalog == "all":
        return (
            select_sample_cases(
                assign_catalog_case_ids(parse_positive_routings(), "positive"), sample
            )
            + assign_catalog_case_ids(
                parse_boundary_prompts()
                + parse_cases(ADVERSARIAL_SPLIT_PROMPTS.read_text(encoding="utf-8")),
                "boundary",
            )
            + assign_catalog_case_ids(
                parse_cases(ROUTER_CONTRACT_PROMPTS.read_text()), "contract"
            )
        )
    fail(f"unknown catalog {catalog!r}")


def canonical_catalog_name(catalog: str) -> str:
    return "positive" if catalog == "sample" else catalog


def filter_cases_by_category(cases: list[dict[str, Any]], category: str | None) -> list[dict[str, Any]]:
    if category is None:
        return cases
    selected = [case for case in cases if case.get("category") == category]
    if not selected:
        fail(f"no cases found for category {category!r}")
    return selected


def random_specialist_cases(cases: list[dict[str, Any]], count: int, seed: str) -> list[dict[str, Any]]:
    if count < 1:
        fail("--random-specialists must be at least 1")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        primary = str(case.get("target_specialist") or case["expected_primary"])
        if primary == "none":
            continue
        grouped.setdefault(primary, []).append(case)
    if count > len(grouped):
        fail(f"--random-specialists {count} exceeds available specialists ({len(grouped)})")
    rng = random.Random(seed)
    selected_primaries = rng.sample(sorted(grouped), count)
    return [rng.choice(grouped[primary]) for primary in selected_primaries]


def stratified_category_cases(
    cases: list[dict[str, Any]], count_per_category: int, seed: str
) -> list[dict[str, Any]]:
    if count_per_category < 1:
        fail("--stratified-categories must be at least 1")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        grouped.setdefault(str(case["category"]), []).append(case)
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    for category in sorted(grouped):
        category_cases = grouped[category]
        if count_per_category > len(category_cases):
            fail(
                f"--stratified-categories {count_per_category} exceeds available "
                f"cases for {category} ({len(category_cases)})"
            )
        selected.extend(rng.sample(category_cases, count_per_category))
    return selected


def check_cover_cases(
    cases: list[dict[str, Any]], required_checks: list[str], seed: str
) -> list[dict[str, Any]]:
    requested = set(required_checks)
    if not requested:
        fail("--check-cover requires at least one check")
    unknown = sorted(requested - set(ROUTER_EVAL_CHECKS))
    if unknown:
        fail(f"--check-cover has unknown checks: {', '.join(unknown)}")

    remaining = set(requested)
    selected: list[dict[str, Any]] = []
    available = list(enumerate(cases, start=1))
    while remaining:
        candidates: list[tuple[int, str, int, dict[str, Any], set[str]]] = []
        for index, case in available:
            coverage = remaining & set(case.get("expected_checks", []))
            if not coverage:
                continue
            result_id = case_id(index, case)
            rank = hashlib.sha256(f"{seed}\0{result_id}".encode()).hexdigest()
            candidates.append((-len(coverage), rank, index, case, coverage))
        if not candidates:
            fail(f"--check-cover cannot cover checks: {', '.join(sorted(remaining))}")
        _negative_coverage, _rank, chosen_index, chosen, coverage = min(candidates)
        selected.append(chosen)
        remaining -= coverage
        available = [(index, case) for index, case in available if index != chosen_index]
    return selected


CASE_ID_RE = re.compile(
    r"^(?P<case_id>(?:"
    r"[a-z][a-z0-9-]*-[0-9a-f]{12,16}|"
    r"(?:[a-z][a-z0-9-]*-)?[0-9]{3,}-[a-z0-9-]+"
    r"))\b"
)


def load_case_id_file(path: Path) -> list[str]:
    case_ids: list[str] = []
    for line_number, raw_line in enumerate(path.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = CASE_ID_RE.match(line)
        if not match:
            fail(f"{path}:{line_number} expected case ID, found {line!r}")
        case_ids.append(match.group("case_id"))
    if not case_ids:
        fail(f"{path} did not contain any case IDs")
    return case_ids


def select_cases_by_id(cases: list[dict[str, Any]], requested_ids: list[str]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for requested_id in requested_ids:
        if requested_id in seen:
            duplicates.append(requested_id)
        seen.add(requested_id)
    if duplicates:
        fail(f"duplicate --case-id values: {', '.join(sorted(set(duplicates)))}")

    by_id = {case_id(index, case): case for index, case in enumerate(cases, 1)}
    missing = [requested_id for requested_id in requested_ids if requested_id not in by_id]
    if missing:
        fail(f"unknown case IDs for selected catalog: {', '.join(missing)}")

    selected: list[dict[str, Any]] = []
    for requested_id in requested_ids:
        case = dict(by_id[requested_id])
        case["_case_id"] = requested_id
        selected.append(case)
    return selected


def case_id(index: int, case: dict[str, Any]) -> str:
    if "_case_id" in case:
        return str(case["_case_id"])
    primary = str(case["expected_primary"]).replace("_", "-")
    primary = re.sub(r"[^a-zA-Z0-9-]+", "-", primary).strip("-")
    return f"{index:03d}-{primary}"


def parse_routing_block(response: str) -> dict[str, Any] | None:
    wire = response.strip()
    if wire == "WITHHOLD":
        return None
    matches = list(ROUTING_BLOCK_RE.finditer(wire))
    if not matches:
        raise ValueError(
            "response must be exact WITHHOLD or exactly one fenced routing block"
        )
    if len(matches) != 1:
        raise ValueError(f"expected exactly one routing block, found {len(matches)}")
    match = matches[0]
    surrounding = wire[: match.start()] + wire[match.end() :]
    if surrounding.strip():
        raise ValueError("routed response contains surrounding prose")
    body = match.group("body").strip()
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("routing block must contain a JSON object")
    keys = set(value)
    if keys != ROUTING_BLOCK_FIELDS:
        missing = sorted(ROUTING_BLOCK_FIELDS - keys)
        extra = sorted(keys - ROUTING_BLOCK_FIELDS)
        raise ValueError(f"routing block keys mismatch: missing={missing}, extra={extra}")
    for field in ("primary", "artifact", "surface", "phase", "rationale"):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ValueError(f"routing block field {field!r} must be a non-empty string")
    secondary = value["secondary"]
    if secondary is not None and (not isinstance(secondary, str) or not secondary.strip()):
        raise ValueError("routing block field 'secondary' must be a non-empty string or null")
    if value["confidence"] not in {"high", "medium"}:
        raise ValueError("routing block confidence must be high or medium")
    if value["phase"] not in ALLOWED_ROUTING_PHASES:
        raise ValueError(f"routing block phase is not allowed: {value['phase']!r}")
    return value


def expand_forbidden(values: list[str], names: list[str]) -> list[str]:
    expanded: list[str] = []
    for value in values:
        if value == "all_specialist_names":
            expanded.extend(names)
        else:
            expanded.append(value)
    return sorted(set(expanded))


def text_fields(block: dict[str, Any]) -> str:
    values = [
        block.get("primary"),
        block.get("secondary"),
        block.get("artifact"),
        block.get("surface"),
        block.get("phase"),
        block.get("rationale"),
    ]
    return " ".join(str(value) for value in values if value not in (None, ""))


def score_case(case: dict[str, Any], response: str, names: list[str], index: int = 1) -> CaseResult:
    failures: list[str] = []
    expected_primary = str(case["expected_primary"])
    category = str(case["category"])
    checks = case.get("expected_checks", [])
    if not isinstance(checks, list):
        checks = []
    unknown_checks = sorted(set(checks) - set(ROUTER_EVAL_CHECKS))
    if unknown_checks:
        failures.append(f"unknown expected_checks values: {unknown_checks}")

    withheld = response.strip() == "WITHHOLD"
    try:
        block = parse_routing_block(response)
    except (json.JSONDecodeError, ValueError) as exc:
        block = None
        failures.append(f"invalid routing block: {exc}")

    structured_output: dict[str, Any] | None
    if block is not None:
        structured_output = {"kind": "routed", **block}
    elif withheld:
        structured_output = {"kind": "withhold"}
    else:
        structured_output = None

    actual_primary = None if block is None else str(block.get("primary") or "")

    forbidden = case.get("forbidden_in_response", [])
    if isinstance(forbidden, list):
        response_lower = response.lower()
        for name in expand_forbidden(forbidden, names):
            if name.lower() in response_lower:
                failures.append(f"forbidden skill name leaked: {name}")

    if expected_primary in LOW_CONFIDENCE_PRIMARIES:
        if block is not None:
            failures.append("routing block emitted for low-confidence or out-of-scope case")
    else:
        if withheld:
            failures.append("WITHHOLD emitted for a routed case")
        elif block is None:
            failures.append("missing routing block")
        elif block.get("primary") != expected_primary:
            failures.append(f"primary mismatch: expected {expected_primary}, got {block.get('primary')}")

    if block is not None:
        confidence = block.get("confidence")
        if confidence not in {"high", "medium"}:
            failures.append(f"confidence must be high or medium, got {confidence!r}")
        expected_phase = case.get("expected_phase")
        if expected_phase is not None and block.get("phase") != expected_phase:
            failures.append(
                f"phase mismatch: expected {expected_phase}, got {block.get('phase')}"
            )

    if "single_primary" in checks and block is not None:
        primary = block.get("primary")
        if not isinstance(primary, str) or not primary:
            failures.append("single_primary check failed: primary must be one skill name")
        elif "," in primary or " " in primary:
            failures.append("single_primary check failed: primary contains multiple values")

    if "secondary_cap" in checks and block is not None:
        secondary = block.get("secondary")
        expected_secondary = case.get("expected_secondary")
        if isinstance(secondary, list):
            failures.append("secondary_cap check failed: secondary must not be a list")
        elif expected_secondary and secondary != expected_secondary:
            failures.append(f"secondary mismatch: expected {expected_secondary}, got {secondary}")
        elif not expected_secondary and secondary not in (None, ""):
            failures.append(f"unexpected secondary: {secondary}")

    if "intent_inference" in checks and block is not None:
        for field in ["artifact", "surface", "phase", "rationale"]:
            if not isinstance(block.get(field), str) or not block.get(field):
                failures.append(f"intent_inference check failed: missing {field}")

    if "capability_translation" in checks and block is not None:
        prompt_lower = str(case["prompt"]).lower()
        routed_text = text_fields(block).lower()
        for term in TOOL_BAIT_TERMS:
            if term in prompt_lower and term in routed_text:
                failures.append(f"capability_translation check failed: repeated tool term {term!r}")

    if "ambiguity_check" in checks:
        if block is not None:
            failures.append("ambiguity_check check failed: emitted routing block")

    if "scope_check" in checks and expected_primary == "none" and block is not None:
        failures.append("scope_check check failed: routed out-of-scope prompt")

    if "no_skill_invoke" in checks:
        skill_pattern = re.compile(
            r"""\bSkill\s*[\(\s:'"]+(?:staff-engineer-mode:)?["']?([a-z0-9-]+)""",
            re.IGNORECASE,
        )
        for match in skill_pattern.finditer(response):
            candidate = match.group(1)
            if candidate in names:
                failures.append(
                    f"no_skill_invoke check failed: response invokes Skill tool on specialist {candidate!r}"
                )
                break

    return CaseResult(
        case_id=case_id(index, case),
        category=category,
        expected_primary=expected_primary,
        actual_primary=actual_primary or None,
        passed=not failures,
        failures=failures,
        response=response,
        structured_output=structured_output,
    )


def read_response(responses_dir: Path, result_id: str) -> str:
    path = responses_dir / f"{result_id}.txt"
    if not path.exists():
        fail(f"missing response file {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def preflight_saved_responses(
    responses_dir: Path, cases: list[dict[str, Any]]
) -> dict[str, SavedResponse]:
    if not responses_dir.is_dir() or responses_dir.is_symlink():
        fail(f"responses path is not a real directory: {responses_dir}")
    captured: dict[str, SavedResponse] = {}
    for index, case in enumerate(cases, 1):
        result_id = case_id(index, case)
        path = responses_dir / f"{result_id}.txt"
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(path, flags)
            with os.fdopen(descriptor, "rb") as handle:
                if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                    fail(f"response path is not a regular file: {path}")
                raw = handle.read()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            fail(f"cannot read UTF-8 response file {path}: {exc}")
        captured[result_id] = SavedResponse(text=text, sha256=sha256_bytes(raw))
    return captured


def command_response(
    command: str,
    prompt: str,
    timeout: int | None = None,
    adapter_settings: AdapterSettings | None = None,
) -> str:
    settings = adapter_settings or resolve_adapter_settings(command)
    with tempfile.TemporaryDirectory(prefix="sem-eval-adapter-") as workspace_value:
        workspace = Path(workspace_value)
        workspace.chmod(0o700)
        environment = build_adapter_environment(settings, workspace)
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            env=environment,
        )
        try:
            stdout, stderr = process.communicate(input=prompt, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            if hasattr(os, "killpg"):
                os.killpg(process.pid, signal.SIGKILL)
            else:  # pragma: no cover - Windows fallback
                process.kill()
            process.communicate()
            raise RuntimeError(
                f"command failed: case timed out after {timeout} seconds"
            ) from exc
        if process.returncode != 0:
            raise RuntimeError(
                f"command failed: {adapter_failure_message(process.returncode, stdout, stderr)}"
            )
        return stdout


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_catalog(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        try:
            label = str(path.resolve().relative_to(ROOT))
        except ValueError:
            label = path.name
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def command_identity(command: str) -> dict[str, Any]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = []
    executable = next(
        (
            token
            for token in tokens
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token)
        ),
        "",
    )
    identity: dict[str, Any] = {
        "kind": "shell-command",
        "command_sha256": sha256_bytes(command.encode("utf-8")),
    }
    if not executable:
        return identity
    candidate = Path(executable)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(ROOT)
    except (OSError, ValueError):
        return identity
    if resolved.is_file():
        identity["adapter"] = str(resolved.relative_to(ROOT))
        identity["adapter_sha256"] = sha256_bytes(resolved.read_bytes())
        identity["executable"] = resolved.name
    elif "/" not in executable and executable in {
        "bash",
        "claude",
        "codex",
        "python",
        "python3",
        "sh",
    }:
        identity["executable"] = executable
    return identity


def resolve_adapter_settings(command: str) -> AdapterSettings:
    adapter = command_identity(command).get("adapter")
    return resolve_protocol_settings(
        adapter=str(adapter) if adapter is not None else None,
        command=command,
    )


def model_environment(command: str) -> tuple[str | None, str | None]:
    return resolve_adapter_settings(command)


def query_host_cli_version(command: str | None) -> tuple[str | None, str | None]:
    if command is None:
        return None, None
    lowered = command.lower()
    host = "claude" if "claude" in lowered else "codex" if "codex" in lowered else None
    if host is None:
        return None, None
    try:
        completed = subprocess.run(
            [host, "--version"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return host, None
    output = completed.stdout.strip() or completed.stderr.strip()
    version = output.splitlines()[0][:200] if completed.returncode == 0 and output else None
    return host, version


def git_state() -> dict[str, Any]:
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return {
        "sha": sha.stdout.strip() if sha.returncode == 0 else None,
        "dirty": bool(status.stdout) if status.returncode == 0 else None,
    }


def adversarial_provenance_record(catalog_paths: list[Path]) -> dict[str, Any] | None:
    resolved = {path.resolve() for path in catalog_paths}
    required = {path.resolve() for path in ADVERSARIAL_SPLIT_PROVENANCE_PATHS}
    if not required.issubset(resolved):
        return None
    draft = json.loads(ADVERSARIAL_SPLIT_DRAFT.read_text(encoding="utf-8"))
    review = json.loads(ADVERSARIAL_SPLIT_REVIEW.read_text(encoding="utf-8"))
    return {
        "batch_id": review["batch_id"],
        "draft_schema_version": draft["schema_version"],
        "review_schema_version": review["schema_version"],
        "review_version": review["review_version"],
        "review_date": review["review_date"],
        "author_access": draft["author_access"],
        "reviewer_access": review["reviewer_access"],
        "summary": review["summary"],
    }


def split_access_context(
    execution_mode: str, command_record: dict[str, Any]
) -> str:
    if execution_mode == "saved":
        return (
            "The evaluator scores pre-existing response files and does not infer their "
            "model, tool access, working directory, or prompt-isolation controls."
        )
    if command_record.get("adapter") in {
        "evals/adapters/claude-router.sh",
        "evals/adapters/codex-router.sh",
    }:
        return (
            "The target model receives only inline local router context and the user prompt "
            "in an isolated, tool-disabled temporary working directory; expected routes, "
            "check labels, and scoring rationale remain in the evaluator."
        )
    return (
        "The evaluator withholds expected routes, check labels, and scoring rationale from "
        "the command input; command isolation and tool access are not verified."
    )


def build_run_manifest(
    *,
    cases: list[dict[str, Any]],
    catalog: str,
    seed: str,
    command: str | None,
    catalog_paths: list[Path],
    execution_mode: str = "live",
    selection_mode: str = "catalog",
    jobs: int = 1,
    case_timeout: int | None = 600,
    run_controls: dict[str, Any] | None = None,
    saved_response_sha256: dict[str, str] | None = None,
    adapter_settings: AdapterSettings | None = None,
) -> dict[str, Any]:
    prompt_sha256 = {
        case_id(index, case): sha256_bytes(str(case["prompt"]).encode("utf-8"))
        for index, case in enumerate(cases, 1)
    }
    prompt_set = json.dumps(prompt_sha256, sort_keys=True, separators=(",", ":"))
    if execution_mode not in {"live", "saved"}:
        raise ValueError(f"unknown execution mode {execution_mode!r}")
    if execution_mode == "live":
        if command is None:
            raise ValueError("live execution manifest requires a command")
        settings = adapter_settings or resolve_adapter_settings(command)
        model, effort = settings
        command_record = command_identity(command)
        host_cli, host_cli_version = query_host_cli_version(command)
    else:
        model, effort = None, None
        command_record = {"kind": "saved-responses"}
        host_cli, host_cli_version = None, None
        if saved_response_sha256 is None:
            raise ValueError("saved execution manifest requires response hashes")
        expected_ids = set(prompt_sha256)
        if set(saved_response_sha256) != expected_ids:
            raise ValueError("saved response hashes must match the selected case IDs")
    controls = run_controls or {
        "selection_mode": selection_mode,
        "jobs": jobs,
        "case_timeout": case_timeout,
    }
    return {
        "type": "manifest",
        "schema_version": 2,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": execution_mode,
        "catalog": catalog,
        "seed": seed,
        "selected_case_ids": list(prompt_sha256),
        "prompt_sha256": prompt_sha256,
        "prompt_set_sha256": sha256_bytes(prompt_set.encode("utf-8")),
        "catalog_sha256": hash_catalog(catalog_paths),
        "catalog_inputs_sha256": {
            (
                str(path.resolve().relative_to(ROOT))
                if path.resolve().is_relative_to(ROOT)
                else path.name
            ): sha256_bytes(path.read_bytes())
            for path in catalog_paths
        },
        "adversarial_provenance": adversarial_provenance_record(catalog_paths),
        "harness_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "adapter_protocol": {
            "path": str(ADAPTER_PROTOCOL_PATH.relative_to(ROOT)),
            "sha256": sha256_bytes(ADAPTER_PROTOCOL_PATH.read_bytes()),
        },
        "context_sha256": {
            str(path.relative_to(ROOT)): sha256_bytes(path.read_bytes())
            for path in ROUTER_CONTEXT_PATHS
        },
        "command": command_record,
        "model": model,
        "effort": effort,
        "host_cli": host_cli,
        "host_cli_version": host_cli_version,
        "run_controls": controls,
        "saved_response_sha256": (
            dict(saved_response_sha256) if saved_response_sha256 is not None else None
        ),
        "git": git_state(),
        "split_access_context": split_access_context(execution_mode, command_record),
    }


def print_case_list(cases: list[dict[str, Any]]) -> None:
    for index, case in enumerate(cases, 1):
        print(f"{case_id(index, case)}\t{case['category']}\t{case['prompt']}")


def failure_type(message: str) -> str:
    if message.startswith("command failed:"):
        return "command_error"
    if "missing routing block" in message or "invalid routing block" in message:
        return "model_format"
    if (
        "routing block emitted for low-confidence or out-of-scope case" in message
        or "scope_check check failed" in message
        or "forbidden skill name leaked" in message
    ):
        return "over_route"
    if "primary mismatch" in message:
        return "route_mismatch"
    if "unknown expected_checks" in message:
        return "harness_contract"
    return "check_failure"


def summarize(results: list[CaseResult]) -> dict[str, Any]:
    categories: dict[str, dict[str, int]] = {}
    failure_types: dict[str, int] = {}
    for result in results:
        bucket = categories.setdefault(result.category, {"passed": 0, "total": 0})
        bucket["total"] += 1
        if result.passed:
            bucket["passed"] += 1
        for message_type in {failure_type(message) for message in result.failures}:
            failure_types[message_type] = failure_types.get(message_type, 0) + 1
    return {
        "passed": sum(1 for result in results if result.passed),
        "total": len(results),
        "categories": categories,
        "failure_types": dict(sorted(failure_types.items())),
        "failures": [
            {
                "case_id": result.case_id,
                "category": result.category,
                "expected_primary": result.expected_primary,
                "actual_primary": result.actual_primary,
                "failure_types": sorted({failure_type(message) for message in result.failures}),
                "failures": result.failures,
            }
            for result in results
            if not result.passed
        ],
    }


def case_result_record(
    result: CaseResult, *, include_response: bool = False
) -> dict[str, Any]:
    record = {
        "case_id": result.case_id,
        "category": result.category,
        "expected_primary": result.expected_primary,
        "actual_primary": result.actual_primary,
        "passed": result.passed,
        "failure_types": sorted({failure_type(message) for message in result.failures}),
        "failures": result.failures,
        "structured_output": result.structured_output,
        "response_sha256": sha256_bytes(result.response.encode("utf-8")),
    }
    if include_response:
        record["response"] = result.response
    return record


class JsonlProgressWriter:
    def __init__(
        self,
        path: Path,
        total: int,
        manifest: dict[str, Any] | None = None,
        include_response: bool = True,
        directory_descriptor: int | None = None,
    ) -> None:
        self.path = path
        self.total = total
        self.completed = 0
        self.passed = 0
        self.failed = 0
        self.include_response = include_response
        try:
            descriptor = (
                open_exclusive_file_at(
                    directory_descriptor,
                    self.path.name,
                    mode=0o600,
                )
                if directory_descriptor is not None
                else open_exclusive_file(self.path, mode=0o600)
            )
        except FileExistsError:
            fail(f"refusing to overwrite results JSONL {self.path}")
        except (OSError, ValueError) as exc:
            fail(f"cannot reserve results JSONL {self.path}: {exc}")
        self._handle = os.fdopen(descriptor, "w", encoding="utf-8")
        if manifest is not None:
            self._append(manifest)

    def write_case(self, result: CaseResult) -> None:
        self.completed += 1
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1

        record = case_result_record(result, include_response=self.include_response)
        record.update(
            {
                "type": "case",
                "completed": self.completed,
                "total": self.total,
                "passed_so_far": self.passed,
                "failed_so_far": self.failed,
            }
        )
        self._append(record)

    def write_summary(self, summary: dict[str, Any]) -> None:
        self._append(
            {
                "type": "summary",
                "completed": self.completed,
                "total": self.total,
                "passed_so_far": self.passed,
                "failed_so_far": self.failed,
                "summary": summary,
            }
        )

    def _append(self, record: dict[str, Any]) -> None:
        self._handle.write(json.dumps(record, sort_keys=True) + "\n")
        self._handle.flush()

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.close()


class RouterRunWriter:
    def __init__(
        self,
        path: Path,
        total: int,
        manifest: dict[str, Any],
    ) -> None:
        self.path = path
        self.responses_dir = self.path / "responses"
        self._directory_descriptor: int | None = None
        self._responses_descriptor: int | None = None
        self._progress: JsonlProgressWriter | None = None
        try:
            self._directory_descriptor = reserve_run_directory(
                self.path, mode=0o700
            )
        except FileExistsError:
            fail(f"refusing to reuse results directory {self.path}")
        except (OSError, ValueError) as exc:
            fail(f"cannot reserve results directory {self.path}: {exc}")
        try:
            self._responses_descriptor = reserve_directory_at(
                self._directory_descriptor,
                "responses",
                mode=0o700,
            )
            self._progress = JsonlProgressWriter(
                self.path / "results.jsonl",
                total,
                manifest=manifest,
                include_response=False,
                directory_descriptor=self._directory_descriptor,
            )
        except BaseException:
            self.close()
            raise

    def write_case(self, result: CaseResult) -> None:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", result.case_id):
            fail(f"unsafe result case ID {result.case_id!r}")
        response_path = self.responses_dir / f"{result.case_id}.txt"
        if self._responses_descriptor is None:
            fail("cannot write a response after closing the run directory")
        try:
            descriptor = open_exclusive_file_at(
                self._responses_descriptor,
                response_path.name,
                mode=0o600,
            )
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
                handle.write(result.response)
        except FileExistsError:
            fail(f"refusing to overwrite response file {response_path}")
        except (OSError, ValueError) as exc:
            fail(f"cannot write response file {response_path}: {exc}")
        if self._progress is None:
            fail("cannot record a response after closing the run directory")
        self._progress.write_case(result)

    def write_summary(self, summary: dict[str, Any]) -> None:
        if self._progress is None:
            fail("cannot record a summary after closing the run directory")
        self._progress.write_summary(summary)

    def close(self) -> None:
        if self._progress is not None:
            self._progress.close()
            self._progress = None
        if self._responses_descriptor is not None:
            os.close(self._responses_descriptor)
            self._responses_descriptor = None
        if self._directory_descriptor is not None:
            os.close(self._directory_descriptor)
            self._directory_descriptor = None


def score_cases(
    cases: list[dict[str, Any]],
    names: list[str],
    responses_dir: Path | None = None,
    saved_responses: dict[str, SavedResponse] | None = None,
    command: str | None = None,
    case_timeout: int | None = None,
    jobs: int = 1,
    on_result: Callable[[CaseResult], None] | None = None,
    adapter_settings: AdapterSettings | None = None,
) -> list[CaseResult]:
    if jobs < 1:
        fail("--jobs must be at least 1")
    if responses_dir is not None and saved_responses is not None:
        fail("provide only one saved response source")

    def run_one(index: int, case: dict[str, Any]) -> CaseResult:
        result_id = case_id(index, case)
        try:
            response = (
                saved_responses[result_id].text
                if saved_responses is not None
                else read_response(responses_dir, result_id)
                if responses_dir is not None
                else command_response(
                    str(command),
                    str(case["prompt"]),
                    timeout=case_timeout,
                    adapter_settings=adapter_settings,
                )
            )
        except RuntimeError as exc:
            return CaseResult(
                case_id=result_id,
                category=str(case["category"]),
                expected_primary=str(case["expected_primary"]),
                actual_primary=None,
                passed=False,
                failures=[str(exc)],
            )
        return score_case(case, response, names, index)

    def emit(result: CaseResult) -> None:
        if on_result is not None:
            on_result(result)

    if jobs == 1 or len(cases) <= 1:
        results = []
        for index, case in enumerate(cases, 1):
            result = run_one(index, case)
            results.append(result)
            emit(result)
        return results

    results: list[CaseResult | None] = [None] * len(cases)
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_index = {
            executor.submit(run_one, index, case): index
            for index, case in enumerate(cases, 1)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            result = future.result()
            results[index - 1] = result
            emit(result)
    return [result for result in results if result is not None]


def print_summary(summary: dict[str, Any]) -> None:
    print(f"router eval: {summary['passed']}/{summary['total']} cases passed")
    for category, counts in sorted(summary["categories"].items()):
        print(f"  {category:12s} {counts['passed']}/{counts['total']}")
    if summary["failures"]:
        print()
        for failure in summary["failures"]:
            print(f"{failure['case_id']} failed:")
            for message in failure["failures"]:
                print(f"  - {message}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score Staff Engineer Mode router eval responses."
    )
    parser.add_argument(
        "--catalog",
        choices=[
            "positive",
            "sample",
            "boundary",
            "adversarial-split",
            "contract",
            "all",
        ],
        default="positive",
        help=(
            "built-in router eval catalog to score when --eval-file is not provided; "
            "sample is a legacy alias for positive"
        ),
    )
    parser.add_argument("--eval-file", help="optional router eval YAML fixture")
    parser.add_argument("--responses-dir", help="directory containing <case-id>.txt responses")
    parser.add_argument("--command", help="command that reads a prompt on stdin and writes a response")
    parser.add_argument(
        "--sample",
        choices=["one-per-specialist", "all"],
        default=None,
        help="sampling mode for built-in catalogs; not valid with --eval-file",
    )
    parser.add_argument("--category", help="score only one case category")
    parser.add_argument("--case-id", action="append", default=[], help="score one stable case ID from the selected catalog")
    parser.add_argument("--case-id-file", help="file containing stable case IDs to score, one per line")
    parser.add_argument("--list-cases", action="store_true", help="print stable case IDs and prompts")
    parser.add_argument("--limit", type=int, help="score only the first N cases")
    parser.add_argument("--random", type=int, help="score N randomly selected cases after category filtering")
    parser.add_argument(
        "--random-specialists",
        type=int,
        help="score one randomly selected prompt from N randomly selected specialist groups",
    )
    parser.add_argument(
        "--stratified-categories",
        type=int,
        help="score N randomly selected cases from every available category",
    )
    parser.add_argument(
        "--check-cover",
        action="append",
        default=[],
        help="select a deterministic case set covering this expected check; repeatable",
    )
    parser.add_argument(
        "--seed",
        default="staff-engineer-mode-release",
        help="seed for random, specialist, and stratified selection",
    )
    parser.add_argument("--jobs", type=int, default=1, help="number of cases to score concurrently")
    parser.add_argument(
        "--case-timeout",
        type=int,
        default=600,
        help="maximum seconds for each live model case",
    )
    result_group = parser.add_mutually_exclusive_group()
    result_group.add_argument(
        "--results-jsonl",
        help=(
            "write one JSON record per completed case, including the response, "
            "and a final summary to a new file"
        ),
    )
    result_group.add_argument(
        "--results-dir",
        help=(
            "reserve a new run directory containing a manifest, case records, "
            "and one final response file per case"
        ),
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument("--warn-only", action="store_true", help="return zero even when cases fail")
    args = parser.parse_args()

    if args.jobs < 1:
        fail("--jobs must be at least 1")
    if args.case_timeout < 1:
        fail("--case-timeout must be at least 1")
    if args.limit is not None and args.limit < 1:
        fail("--limit must be at least 1")

    if args.eval_file:
        eval_path = Path(args.eval_file)
        if args.sample is not None:
            fail("--sample applies only to built-in catalogs, not --eval-file")
        cases = load_custom_eval_cases(eval_path)
        effective_sample = None
        try:
            catalog_label = f"file:{eval_path.resolve().relative_to(ROOT)}"
        except ValueError:
            catalog_label = "external-catalog"
        catalog_paths = [eval_path]
    else:
        effective_sample = args.sample or "one-per-specialist"
        cases = load_catalog_cases(args.catalog, effective_sample)
        catalog_label = canonical_catalog_name(args.catalog)
        if args.catalog in {"positive", "sample"}:
            catalog_paths = [POSITIVE_ROUTING_PROMPTS]
        elif args.catalog == "boundary":
            catalog_paths = [
                *BOUNDARY_PROMPT_FILES.values(),
                *ADVERSARIAL_SPLIT_PROVENANCE_PATHS,
            ]
        elif args.catalog == "adversarial-split":
            catalog_paths = list(ADVERSARIAL_SPLIT_PROVENANCE_PATHS)
        elif args.catalog == "contract":
            catalog_paths = [ROUTER_CONTRACT_PROMPTS]
        else:
            catalog_paths = [
                POSITIVE_ROUTING_PROMPTS,
                *BOUNDARY_PROMPT_FILES.values(),
                *ADVERSARIAL_SPLIT_PROVENANCE_PATHS,
                ROUTER_CONTRACT_PROMPTS,
            ]
    cases = filter_cases_by_category(cases, args.category)
    requested_case_ids = list(args.case_id)
    if args.case_id_file:
        requested_case_ids.extend(load_case_id_file(Path(args.case_id_file)))
    random_modes = [
        args.random is not None,
        args.random_specialists is not None,
        args.stratified_categories is not None,
        bool(args.check_cover),
    ]
    if sum(random_modes) > 1:
        fail("provide at most one random selection mode")
    if requested_case_ids and (
        args.limit is not None
        or args.random is not None
        or args.random_specialists is not None
        or args.stratified_categories is not None
        or args.check_cover
    ):
        fail("--case-id and --case-id-file cannot be combined with sampling limits or random selection")
    if args.limit is not None and any(random_modes):
        fail("--limit cannot be combined with random selection")
    if requested_case_ids:
        cases = select_cases_by_id(cases, requested_case_ids)
    if args.limit is not None:
        cases = cases[: args.limit]
    if args.random is not None:
        if args.random < 1:
            fail("--random must be at least 1")
        if args.random > len(cases):
            fail(f"--random {args.random} exceeds available cases ({len(cases)})")
        rng = random.Random(args.seed)
        cases = rng.sample(cases, args.random)
    if args.random_specialists is not None:
        cases = random_specialist_cases(cases, args.random_specialists, args.seed)
    if args.stratified_categories is not None:
        cases = stratified_category_cases(cases, args.stratified_categories, args.seed)
    if args.check_cover:
        cases = check_cover_cases(cases, args.check_cover, args.seed)
    if not cases:
        fail("no cases selected")

    if requested_case_ids:
        selection_mode = "case_ids"
    elif args.limit is not None:
        selection_mode = "limit"
    elif args.random is not None:
        selection_mode = "random"
    elif args.random_specialists is not None:
        selection_mode = "random_specialists"
    elif args.stratified_categories is not None:
        selection_mode = "stratified_categories"
    elif args.check_cover:
        selection_mode = "check_cover"
    elif args.category is not None:
        selection_mode = "category"
    elif args.eval_file:
        selection_mode = "custom_catalog"
    elif effective_sample != "all":
        selection_mode = "catalog_sample"
    else:
        selection_mode = "catalog"

    if args.list_cases:
        print_case_list(cases)
        return 0

    if bool(args.responses_dir) == bool(args.command):
        fail("provide exactly one of --responses-dir or --command")

    adapter_settings = (
        resolve_adapter_settings(args.command) if args.command is not None else None
    )
    names = specialist_names()
    responses_dir = Path(args.responses_dir) if args.responses_dir else None
    saved_responses = (
        preflight_saved_responses(responses_dir, cases)
        if responses_dir is not None
        else None
    )
    saved_response_sha256 = (
        {
            result_id: response.sha256
            for result_id, response in saved_responses.items()
        }
        if saved_responses is not None
        else None
    )
    progress_writer: JsonlProgressWriter | RouterRunWriter | None = None
    if args.results_jsonl or args.results_dir:
        run_controls = {
            "selection_mode": selection_mode,
            "catalog": catalog_label,
            "requested_catalog": args.catalog if not args.eval_file else "eval-file",
            "sample": effective_sample,
            "category": args.category,
            "requested_case_ids": requested_case_ids,
            "case_id_file_sha256": (
                sha256_bytes(Path(args.case_id_file).read_bytes())
                if args.case_id_file
                else None
            ),
            "limit": args.limit,
            "random": args.random,
            "random_specialists": args.random_specialists,
            "stratified_categories": args.stratified_categories,
            "check_cover": list(args.check_cover),
            "seed": args.seed,
            "jobs": args.jobs,
            "case_timeout": args.case_timeout if args.command else None,
            "warn_only": args.warn_only,
            "summary_format": "json" if args.json else "text",
            "evidence_sink": "run_directory" if args.results_dir else "jsonl",
        }
        manifest = build_run_manifest(
            cases=cases,
            catalog=catalog_label,
            seed=args.seed,
            command=args.command,
            catalog_paths=catalog_paths,
            execution_mode="live" if args.command else "saved",
            selection_mode=selection_mode,
            jobs=args.jobs,
            case_timeout=args.case_timeout if args.command else None,
            run_controls=run_controls,
            saved_response_sha256=saved_response_sha256,
            adapter_settings=adapter_settings,
        )
        if args.results_dir:
            progress_writer = RouterRunWriter(
                Path(args.results_dir), len(cases), manifest=manifest
            )
        else:
            progress_writer = JsonlProgressWriter(
                Path(args.results_jsonl), len(cases), manifest=manifest
            )
    try:
        results = score_cases(
            cases,
            names,
            saved_responses=saved_responses,
            command=args.command,
            case_timeout=args.case_timeout,
            jobs=args.jobs,
            on_result=progress_writer.write_case if progress_writer is not None else None,
            adapter_settings=adapter_settings,
        )

        summary = summarize(results)
        if progress_writer is not None:
            progress_writer.write_summary(summary)
    finally:
        if progress_writer is not None:
            progress_writer.close()
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary)
    return 0 if args.warn_only or not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
