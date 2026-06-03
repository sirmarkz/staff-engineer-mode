#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from staff_engineer_mode_contract import ROUTER_EVAL_CHECKS, ROUTER_SAMPLE_PROMPT_CHECKS

POSITIVE_ROUTING_PROMPTS = ROOT / "evals" / "prompts" / "expected-routes.md"
BOUNDARY_PROMPT_DIR = ROOT / "evals" / "prompts"
BOUNDARY_PROMPT_FILES = {
    "negative": BOUNDARY_PROMPT_DIR / "negative.md",
    "near_miss": BOUNDARY_PROMPT_DIR / "near-miss.md",
    "keyword_bait": BOUNDARY_PROMPT_DIR / "keyword-bait.md",
    "adversarial": BOUNDARY_PROMPT_DIR / "adversarial.md",
}
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


def load_catalog_cases(catalog: str, sample: str) -> list[dict[str, Any]]:
    if catalog in {"positive", "sample"}:
        return select_sample_cases(parse_positive_routings(), sample)
    if catalog == "boundary":
        return parse_boundary_prompts()
    if catalog == "all":
        return select_sample_cases(parse_positive_routings(), sample) + parse_boundary_prompts()
    fail(f"unknown catalog {catalog!r}")


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


CASE_ID_RE = re.compile(r"^(?P<case_id>[0-9]{3}-[a-z0-9-]+)\b")


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
    checks = case.get("expected_checks", [])
    if not isinstance(checks, list):
        checks = []
    unknown_checks = sorted(set(checks) - set(ROUTER_EVAL_CHECKS))
    if unknown_checks:
        failures.append(f"unknown expected_checks values: {unknown_checks}")

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

    if "read_load" in checks and expected_primary not in LOW_CONFIDENCE_PRIMARIES and expected_primary != "none":
        body_without_routing = ROUTING_BLOCK_RE.sub("", response).strip()
        if len(body_without_routing) >= 200:
            read_pattern = re.compile(
                rf"\bRead\b[^\n]*?"
                rf"(?:SPECIALIST_ROOT[^\n]*?{re.escape(expected_primary)}\.md|"
                rf"[/\\]specialists[/\\]{re.escape(expected_primary)}\.md)",
                re.IGNORECASE,
            )
            if not read_pattern.search(response):
                failures.append(
                    f"read_load check failed: substantive answer without Read of "
                    f"specialists/{expected_primary}.md"
                )

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
        detail = completed.stderr.strip() or completed.stdout.strip() or f"command exited {completed.returncode}"
        raise RuntimeError(f"command failed: {detail}")
    return completed.stdout


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


def score_cases(
    cases: list[dict[str, Any]],
    names: list[str],
    responses_dir: Path | None = None,
    command: str | None = None,
    jobs: int = 1,
) -> list[CaseResult]:
    if jobs < 1:
        fail("--jobs must be at least 1")

    def run_one(index: int, case: dict[str, Any]) -> CaseResult:
        result_id = case_id(index, case)
        try:
            response = (
                read_response(responses_dir, result_id)
                if responses_dir is not None
                else command_response(str(command), str(case["prompt"]))
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

    if jobs == 1 or len(cases) <= 1:
        return [run_one(index, case) for index, case in enumerate(cases, 1)]

    results: list[CaseResult | None] = [None] * len(cases)
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        future_to_index = {
            executor.submit(run_one, index, case): index
            for index, case in enumerate(cases, 1)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            results[index - 1] = future.result()
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
        choices=["positive", "sample", "boundary", "all"],
        default="positive",
        help=(
            "built-in router eval catalog to score when --eval-file is not provided; "
            "sample is a legacy alias for positive"
        ),
    )
    parser.add_argument("--eval-file", help="optional router eval YAML fixture")
    parser.add_argument("--responses-dir", help="directory containing <case-id>.txt responses")
    parser.add_argument("--command", help="command that reads a prompt on stdin and writes a response")
    parser.add_argument("--sample", choices=["one-per-specialist", "all"], default="one-per-specialist")
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
        "--seed",
        default="staff-engineer-mode-release",
        help="seed for --random and --random-specialists selection",
    )
    parser.add_argument("--jobs", type=int, default=1, help="number of cases to score concurrently")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument("--warn-only", action="store_true", help="return zero even when cases fail")
    args = parser.parse_args()

    if args.eval_file:
        eval_path = Path(args.eval_file)
        cases = parse_cases(eval_path.read_text())
    else:
        cases = load_catalog_cases(args.catalog, args.sample)
    cases = filter_cases_by_category(cases, args.category)
    requested_case_ids = list(args.case_id)
    if args.case_id_file:
        requested_case_ids.extend(load_case_id_file(Path(args.case_id_file)))
    if args.random is not None and args.random_specialists is not None:
        fail("provide at most one of --random or --random-specialists")
    if requested_case_ids and (
        args.limit is not None or args.random is not None or args.random_specialists is not None
    ):
        fail("--case-id and --case-id-file cannot be combined with --limit, --random, or --random-specialists")
    if args.limit is not None and (args.random is not None or args.random_specialists is not None):
        fail("--limit cannot be combined with --random or --random-specialists")
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

    if args.list_cases:
        print_case_list(cases)
        return 0

    if bool(args.responses_dir) == bool(args.command):
        fail("provide exactly one of --responses-dir or --command")

    names = specialist_names()
    responses_dir = Path(args.responses_dir) if args.responses_dir else None
    results = score_cases(cases, names, responses_dir=responses_dir, command=args.command, jobs=args.jobs)

    summary = summarize(results)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary)
    return 0 if args.warn_only or not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
