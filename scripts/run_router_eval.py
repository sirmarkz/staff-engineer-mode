#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
ROUTER_EVAL = ROOT / "skills" / "staff-engineer-mode" / "references" / "router-eval-set.yaml"
SKILLS = ROOT / "skills"
SPECIALISTS = ROOT / "specialists"
ROUTING_BLOCK_RE = re.compile(r"```routing\s*(?P<body>.*?)```", re.DOTALL)
LOW_CONFIDENCE_PRIMARIES = {"staff-engineer-mode", "none"}
TOOL_BAIT_TERMS = [
    "argocd",
    "argo cd",
    "cache product",
    "datadog",
    "graphql",
    "istio",
]


class CaseResult(NamedTuple):
    case_id: str
    category: str
    expected_primary: str
    actual_primary: str | None
    passed: bool
    failures: list[str]


def fail(message: str) -> None:
    print(f"router eval failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
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
    if key in {"expected_gates", "forbidden_in_response"}:
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


def specialist_names() -> list[str]:
    return sorted(path.parent.name for path in SPECIALISTS.glob("*/SKILL.md"))


def case_id(index: int, case: dict[str, Any]) -> str:
    primary = str(case["expected_primary"]).replace("_", "-")
    primary = re.sub(r"[^a-zA-Z0-9-]+", "-", primary).strip("-")
    return f"{index:03d}-{primary}"


def parse_routing_block(response: str) -> dict[str, Any] | None:
    match = ROUTING_BLOCK_RE.search(response)
    if not match:
        return None
    body = match.group("body").strip()
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("routing block must contain a JSON object")
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
    gates = case.get("expected_gates", [])
    if not isinstance(gates, list):
        gates = []

    try:
        block = parse_routing_block(response)
    except (json.JSONDecodeError, ValueError) as exc:
        block = None
        failures.append(f"invalid routing block: {exc}")

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
        if block is None:
            failures.append("missing routing block")
        elif block.get("primary") != expected_primary:
            failures.append(f"primary mismatch: expected {expected_primary}, got {block.get('primary')}")

    if block is not None:
        confidence = block.get("confidence")
        if confidence not in {"high", "medium"}:
            failures.append(f"confidence must be high or medium, got {confidence!r}")

    if "single_primary" in gates and block is not None:
        primary = block.get("primary")
        if not isinstance(primary, str) or not primary:
            failures.append("single_primary gate failed: primary must be one skill name")
        elif "," in primary or " " in primary:
            failures.append("single_primary gate failed: primary contains multiple values")

    if "secondary_cap" in gates and block is not None:
        secondary = block.get("secondary")
        expected_secondary = case.get("expected_secondary")
        if isinstance(secondary, list):
            failures.append("secondary_cap gate failed: secondary must not be a list")
        elif expected_secondary and secondary != expected_secondary:
            failures.append(f"secondary mismatch: expected {expected_secondary}, got {secondary}")
        elif not expected_secondary and secondary not in (None, ""):
            failures.append(f"unexpected secondary: {secondary}")

    if "intent_inference" in gates and block is not None:
        for field in ["artifact", "surface", "phase", "rationale"]:
            if not isinstance(block.get(field), str) or not block.get(field):
                failures.append(f"intent_inference gate failed: missing {field}")

    if "capability_translation" in gates and block is not None:
        prompt_lower = str(case["prompt"]).lower()
        routed_text = text_fields(block).lower()
        for term in TOOL_BAIT_TERMS:
            if term in prompt_lower and term in routed_text:
                failures.append(f"capability_translation gate failed: repeated tool term {term!r}")

    if "ambiguity_check" in gates:
        if block is not None:
            failures.append("ambiguity_check gate failed: emitted routing block")

    if "scope_check" in gates and expected_primary == "none" and block is not None:
        failures.append("scope_check gate failed: routed out-of-scope prompt")

    return CaseResult(
        case_id=case_id(index, case),
        category=category,
        expected_primary=expected_primary,
        actual_primary=actual_primary or None,
        passed=not failures,
        failures=failures,
    )


def read_response(responses_dir: Path, result_id: str) -> str:
    path = responses_dir / f"{result_id}.txt"
    if not path.exists():
        fail(f"missing response file {path}")
    return path.read_text()


def command_response(command: str, prompt: str) -> str:
    completed = subprocess.run(
        command,
        input=prompt,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"command exited {completed.returncode}")
    return completed.stdout


def print_case_list(cases: list[dict[str, Any]]) -> None:
    for index, case in enumerate(cases, 1):
        print(f"{case_id(index, case)}\t{case['category']}\t{case['prompt']}")


def summarize(results: list[CaseResult]) -> dict[str, Any]:
    categories: dict[str, dict[str, int]] = {}
    for result in results:
        bucket = categories.setdefault(result.category, {"passed": 0, "total": 0})
        bucket["total"] += 1
        if result.passed:
            bucket["passed"] += 1
    return {
        "passed": sum(1 for result in results if result.passed),
        "total": len(results),
        "categories": categories,
        "failures": [
            {
                "case_id": result.case_id,
                "category": result.category,
                "expected_primary": result.expected_primary,
                "actual_primary": result.actual_primary,
                "failures": result.failures,
            }
            for result in results
            if not result.passed
        ],
    }


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
        description="Score saved or command-generated Staff Engineer Mode routing eval responses."
    )
    parser.add_argument("--eval-file", default=str(ROUTER_EVAL), help="router eval YAML fixture")
    parser.add_argument("--responses-dir", help="directory containing <case-id>.txt responses")
    parser.add_argument("--command", help="command that reads a prompt on stdin and writes a response")
    parser.add_argument("--list-cases", action="store_true", help="print stable case IDs and prompts")
    parser.add_argument("--limit", type=int, help="score only the first N cases")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument("--warn-only", action="store_true", help="return zero even when cases fail")
    args = parser.parse_args()

    eval_path = Path(args.eval_file)
    cases = parse_cases(eval_path.read_text())
    if args.limit is not None:
        cases = cases[: args.limit]

    if args.list_cases:
        print_case_list(cases)
        return 0

    if bool(args.responses_dir) == bool(args.command):
        fail("provide exactly one of --responses-dir or --command")

    names = specialist_names()
    results: list[CaseResult] = []
    responses_dir = Path(args.responses_dir) if args.responses_dir else None
    for index, case in enumerate(cases, 1):
        result_id = case_id(index, case)
        try:
            response = (
                read_response(responses_dir, result_id)
                if responses_dir is not None
                else command_response(str(args.command), str(case["prompt"]))
            )
        except RuntimeError as exc:
            results.append(
                CaseResult(
                    case_id=result_id,
                    category=str(case["category"]),
                    expected_primary=str(case["expected_primary"]),
                    actual_primary=None,
                    passed=False,
                    failures=[str(exc)],
                )
            )
            continue
        results.append(score_case(case, response, names, index))

    summary = summarize(results)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary)
    return 0 if args.warn_only or not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
