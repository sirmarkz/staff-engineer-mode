#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER_EVAL_CANDIDATES = [
    ROOT / "skills" / "routing" / "staff-engineer-mode" / "references" / "router-eval-set.yaml",
]
REQUIRED_KEYS = {"prompt", "expected_primary", "expected_behavior", "category"}
REQUIRED_CATEGORIES = {"direct", "paraphrase", "ambiguous", "mixed_intent", "out_of_scope"}
MIN_CASES = 35


def fail(message: str) -> None:
    print(f"router eval validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def parse_cases(text: str) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        if line.startswith("  - "):
            if current is not None:
                cases.append(current)
            current = {}
            remainder = line[4:]
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = scalar(value)
            continue
        if current is not None and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key.strip()] = scalar(value)
    if current is not None:
        cases.append(current)
    return cases


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
    for index, case in enumerate(cases, 1):
        missing = REQUIRED_KEYS - set(case)
        if missing:
            fail(f"case {index} missing keys: {sorted(missing)}")
        if not case["prompt"]:
            fail(f"case {index} prompt is empty")
        if not case["expected_behavior"]:
            fail(f"case {index} expected_behavior is empty")
        categories.add(case["category"])
        primaries.add(case["expected_primary"])

    missing_categories = REQUIRED_CATEGORIES - categories
    if missing_categories:
        fail(f"missing categories: {sorted(missing_categories)}")
    if "none" not in primaries:
        fail("out-of-scope fixture must include expected_primary: none")
    if "staff-engineer-mode" not in primaries:
        fail("ambiguous fixture must include router fallback cases")

    print(f"router eval fixture validation passed: {len(cases)} cases, {len(categories)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
