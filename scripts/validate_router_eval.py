#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTER_EVAL_FILES = [
    ROOT / "skills" / "staff-engineer-mode" / "references" / "router-eval-set.yaml",
    ROOT / "skills" / "staff-engineer-mode" / "references" / "router-phase-eval-set.yaml",
]
REQUIRED_KEYS = {"prompt", "expected_primary", "expected_behavior", "category"}
REQUIRED_CATEGORIES = {"direct", "paraphrase", "mixed_intent", "out_of_scope"}
REQUIRED_CHECK_KEY = "expected_checks"
FORBIDDEN_KEY = "forbidden_in_response"
ALLOWED_CHECKS = {
    "single_primary",
    "secondary_cap",
    "capability_translation",
    "scope_check",
    "ambiguity_check",
    "intent_inference",
}
MIN_CASES = 35
MIN_SECONDARY_CASES = 8
PHASE_EVAL_MIN_CASES = 30
REQUIRED_PHASES = {"ideation", "design", "development", "testing", "release", "maintenance"}
PHASE_BOUNDARY_SPECIALISTS = {
    "agent-pr-review",
    "incident-response-and-postmortems",
    "production-readiness-review",
    "vulnerability-management",
}
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


def fail(message: str) -> None:
    print(f"router eval validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def inline_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        fail(f"expected inline list, found {value!r}")
    body = value[1:-1].strip()
    if not body:
        return []
    return [scalar(part.strip()) for part in body.split(",")]


def parse_value(key: str, value: str) -> str | list[str]:
    if key in {REQUIRED_CHECK_KEY, FORBIDDEN_KEY}:
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


def skill_names() -> set[str]:
    specialists_dir = ROOT / "specialists"
    return {"staff-engineer-mode"} | {path.stem for path in specialists_dir.glob("*.md")}


def validate_common_cases(cases: list[dict[str, Any]], path: Path) -> tuple[set[str], set[str], int]:
    categories = set()
    primaries = set()
    secondary_cases = 0
    valid_skill_names = skill_names()
    valid_primary_names = valid_skill_names | {"none"}
    valid_forbidden_names = (valid_skill_names - {"staff-engineer-mode"}) | {"all_specialist_names"}
    for index, case in enumerate(cases, 1):
        missing = REQUIRED_KEYS - set(case)
        if missing:
            fail(f"{path} case {index} missing keys: {sorted(missing)}")
        if not case["prompt"]:
            fail(f"{path} case {index} prompt is empty")
        if not case["expected_behavior"]:
            fail(f"{path} case {index} expected_behavior is empty")
        if case["expected_primary"] not in valid_primary_names:
            fail(f"{path} case {index} has unknown expected_primary {case['expected_primary']!r}")
        if "expected_secondary" in case and case["expected_secondary"] not in valid_skill_names:
            fail(f"{path} case {index} has unknown expected_secondary {case['expected_secondary']!r}")
        if case["expected_primary"] == "staff-engineer-mode" and "without naming specialists" not in case["expected_behavior"]:
            fail(
                f"{path} no-route case {index} must withhold routing without naming specialists"
            )
        checks = case.get(REQUIRED_CHECK_KEY)
        if not isinstance(checks, list) or not checks:
            fail(f"{path} case {index} must include non-empty {REQUIRED_CHECK_KEY}")
        unknown_checks = set(checks) - ALLOWED_CHECKS
        if unknown_checks:
            fail(f"{path} case {index} has unknown expected checks: {sorted(unknown_checks)}")
        if case["expected_primary"] not in {"staff-engineer-mode", "none"}:
            for check in ["single_primary", "intent_inference"]:
                if check not in checks:
                    fail(f"{path} case {index} must include expected check {check}")
        if "expected_secondary" in case and "secondary_cap" not in checks:
            fail(f"{path} case {index} with expected_secondary must include secondary_cap")
        if "expected_secondary" in case:
            secondary_cases += 1
        if case["expected_primary"] == "staff-engineer-mode" and "ambiguity_check" not in checks:
            fail(f"{path} ambiguous case {index} must include ambiguity_check")
        if case["expected_primary"] == "none" and "scope_check" not in checks:
            fail(f"{path} out-of-scope case {index} must include scope_check")
        if case["category"] in {"ambiguous", "out_of_scope"}:
            forbidden = case.get(FORBIDDEN_KEY)
            if not isinstance(forbidden, list) or not forbidden:
                fail(f"{path} case {index} must include non-empty {FORBIDDEN_KEY}")
            unknown_forbidden = set(forbidden) - valid_forbidden_names
            if unknown_forbidden:
                fail(f"{path} case {index} has unknown forbidden names: {sorted(unknown_forbidden)}")
        categories.add(case["category"])
        primaries.add(case["expected_primary"])
    return categories, primaries, secondary_cases


def validate_main_fixture(cases: list[dict[str, Any]], path: Path) -> None:
    if len(cases) < MIN_CASES:
        fail(f"{path} expected at least {MIN_CASES} cases, found {len(cases)}")
    categories, primaries, secondary_cases = validate_common_cases(cases, path)

    missing_categories = REQUIRED_CATEGORIES - categories
    if missing_categories:
        fail(f"{path} missing categories: {sorted(missing_categories)}")
    if "none" not in primaries:
        fail(f"{path} out-of-scope fixture must include expected_primary: none")
    if secondary_cases < MIN_SECONDARY_CASES:
        fail(f"{path} expected at least {MIN_SECONDARY_CASES} expected_secondary cases, found {secondary_cases}")

    small_commit_cases = [
        index
        for index, case in enumerate(cases, 1)
        if "commit" in str(case["prompt"]).lower()
        and any(word in str(case["prompt"]).lower() for word in ["small", "tiny", "typo", "mechanical"])
    ]
    missing_agent_review = [
        index
        for index in small_commit_cases
        if cases[index - 1]["expected_primary"] != "agent-pr-review"
    ]
    if missing_agent_review:
        fail(
            f"{path} small commit cases must route to agent-pr-review regardless of size: "
            f"{missing_agent_review}"
        )


def has_explicit_phase_word(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    return any(word in prompt_lower for word in EXPLICIT_PHASE_WORDS)


def validate_phase_fixture(cases: list[dict[str, Any]], path: Path) -> None:
    if len(cases) < PHASE_EVAL_MIN_CASES:
        fail(f"{path} expected at least {PHASE_EVAL_MIN_CASES} cases, found {len(cases)}")
    categories, primaries, _secondary_cases = validate_common_cases(cases, path)
    if "none" not in primaries:
        fail(f"{path} out-of-scope fixture must include expected_primary: none")

    phases = {
        str(case["expected_phase"])
        for case in cases
        if case["expected_primary"] not in {"staff-engineer-mode", "none"} and "expected_phase" in case
    }
    missing_phases = REQUIRED_PHASES - phases
    if missing_phases:
        fail(f"{path} missing expected_phase coverage: {sorted(missing_phases)}")

    missing_boundaries = PHASE_BOUNDARY_SPECIALISTS - primaries
    if missing_boundaries:
        fail(f"{path} missing boundary specialist coverage: {sorted(missing_boundaries)}")

    context_only_cases = [
        index
        for index, case in enumerate(cases, 1)
        if case["category"] == "paraphrase" and not has_explicit_phase_word(str(case["prompt"]))
    ]
    if len(context_only_cases) < 4:
        fail(f"{path} needs at least 4 context-only paraphrase cases; found {context_only_cases}")

    if "out_of_scope" not in categories:
        fail(f"{path} must include an out_of_scope case")


def main() -> int:
    total_cases = 0
    for router_eval in ROUTER_EVAL_FILES:
        if not router_eval.exists():
            fail(f"missing router eval fixture {router_eval.relative_to(ROOT)}")
        cases = parse_cases(router_eval.read_text())
        if router_eval.name == "router-eval-set.yaml":
            validate_main_fixture(cases, router_eval)
        elif router_eval.name == "router-phase-eval-set.yaml":
            validate_phase_fixture(cases, router_eval)
        else:
            fail(f"unknown router eval fixture {router_eval}")
        total_cases += len(cases)

    print(f"router eval fixture validation passed: {len(ROUTER_EVAL_FILES)} files, {total_cases} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
