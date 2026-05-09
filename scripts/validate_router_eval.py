#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTER_EVAL_CANDIDATES = [
    ROOT / "skills" / "staff-engineer-mode" / "references" / "router-eval-set.yaml",
]
REQUIRED_KEYS = {"prompt", "expected_primary", "expected_behavior", "category"}
REQUIRED_CATEGORIES = {"direct", "paraphrase", "ambiguous", "mixed_intent", "out_of_scope"}
REQUIRED_GATE_KEY = "expected_gates"
FORBIDDEN_KEY = "forbidden_in_response"
ALLOWED_GATES = {
    "single_primary",
    "secondary_cap",
    "capability_translation",
    "scope_check",
    "ambiguity_check",
    "intent_inference",
}
MIN_CASES = 35
MIN_SECONDARY_CASES = 8


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
    if key in {REQUIRED_GATE_KEY, FORBIDDEN_KEY}:
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
    return {"staff-engineer-mode"} | {path.parent.name for path in specialists_dir.glob("*/SKILL.md")}


def main() -> int:
    router_eval = next((path for path in ROUTER_EVAL_CANDIDATES if path.exists()), None)
    if router_eval is None:
        checked = ", ".join(str(path.relative_to(ROOT)) for path in ROUTER_EVAL_CANDIDATES)
        fail(f"missing router eval fixture; checked {checked}")
    cases = parse_cases(router_eval.read_text())
    if len(cases) < MIN_CASES:
        fail(f"expected at least {MIN_CASES} cases, found {len(cases)}")

    categories = set()
    primaries = set()
    secondary_cases = 0
    valid_skill_names = skill_names()
    valid_primary_names = valid_skill_names | {"none"}
    valid_forbidden_names = (valid_skill_names - {"staff-engineer-mode"}) | {"all_specialist_names"}
    for index, case in enumerate(cases, 1):
        missing = REQUIRED_KEYS - set(case)
        if missing:
            fail(f"case {index} missing keys: {sorted(missing)}")
        if not case["prompt"]:
            fail(f"case {index} prompt is empty")
        if not case["expected_behavior"]:
            fail(f"case {index} expected_behavior is empty")
        if case["expected_primary"] not in valid_primary_names:
            fail(f"case {index} has unknown expected_primary {case['expected_primary']!r}")
        if "expected_secondary" in case and case["expected_secondary"] not in valid_skill_names:
            fail(f"case {index} has unknown expected_secondary {case['expected_secondary']!r}")
        if case["expected_primary"] == "staff-engineer-mode" and "without naming specialists" not in case["expected_behavior"]:
            fail(
                f"ambiguous case {index} must expect clarification questions without naming specialists"
            )
        gates = case.get(REQUIRED_GATE_KEY)
        if not isinstance(gates, list) or not gates:
            fail(f"case {index} must include non-empty {REQUIRED_GATE_KEY}")
        unknown_gates = set(gates) - ALLOWED_GATES
        if unknown_gates:
            fail(f"case {index} has unknown expected gates: {sorted(unknown_gates)}")
        if case["expected_primary"] not in {"staff-engineer-mode", "none"}:
            for gate in ["single_primary", "intent_inference"]:
                if gate not in gates:
                    fail(f"case {index} must include expected gate {gate}")
        if "expected_secondary" in case and "secondary_cap" not in gates:
            fail(f"case {index} with expected_secondary must include secondary_cap")
        if "expected_secondary" in case:
            secondary_cases += 1
        if case["expected_primary"] == "staff-engineer-mode" and "ambiguity_check" not in gates:
            fail(f"ambiguous case {index} must include ambiguity_check")
        if case["expected_primary"] == "none" and "scope_check" not in gates:
            fail(f"out-of-scope case {index} must include scope_check")
        if case["category"] in {"ambiguous", "out_of_scope"}:
            forbidden = case.get(FORBIDDEN_KEY)
            if not isinstance(forbidden, list) or not forbidden:
                fail(f"case {index} must include non-empty {FORBIDDEN_KEY}")
            unknown_forbidden = set(forbidden) - valid_forbidden_names
            if unknown_forbidden:
                fail(f"case {index} has unknown forbidden names: {sorted(unknown_forbidden)}")
        categories.add(case["category"])
        primaries.add(case["expected_primary"])

    missing_categories = REQUIRED_CATEGORIES - categories
    if missing_categories:
        fail(f"missing categories: {sorted(missing_categories)}")
    if "none" not in primaries:
        fail("out-of-scope fixture must include expected_primary: none")
    if "staff-engineer-mode" not in primaries:
        fail("ambiguous fixture must include router fallback cases")
    if secondary_cases < MIN_SECONDARY_CASES:
        fail(f"expected at least {MIN_SECONDARY_CASES} expected_secondary cases, found {secondary_cases}")

    print(f"router eval fixture validation passed: {len(cases)} cases, {len(categories)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
