#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from staff_engineer_mode_contract import ROUTER_SAMPLE_PROMPT_CHECKS

ROUTER_EVAL_PATH = ROOT / "scripts" / "run_router_eval.py"
SPEC = importlib.util.spec_from_file_location("run_router_eval", ROUTER_EVAL_PATH)
assert SPEC is not None
router_eval = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(router_eval)

SAMPLE_PROMPTS = ROOT / "SAMPLE-PROMPTS.md"
SPECIALIST_HEADING_RE = re.compile(r"^### `(?P<slug>[^`]+)`$")
PROMPT_RE = re.compile(r'^- "(?P<prompt>.+)"$')
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


def fail(message: str) -> None:
    print(f"sample prompt eval failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_sample_prompts(path: Path = SAMPLE_PROMPTS) -> list[dict[str, Any]]:
    known = set(router_eval.specialist_names())
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
            if current not in known:
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
            cases.append(
                {
                    "prompt": prompt,
                    "expected_primary": current,
                    "expected_behavior": "route sample prompt to its grouped specialist",
                    "category": "sample_prompt",
                    "expected_checks": list(ROUTER_SAMPLE_PROMPT_CHECKS),
                }
            )

    missing = sorted(known - seen_headings)
    if missing:
        fail(f"{path} missing specialist headings: {', '.join(missing)}")

    bad_counts = {slug: count for slug, count in counts.items() if count != 4}
    if bad_counts:
        details = ", ".join(f"{slug}={count}" for slug, count in sorted(bad_counts.items()))
        fail(f"{path} must have exactly four prompts per specialist: {details}")

    if not cases:
        fail(f"{path} produced no sample prompt cases")

    missing_phases = [phase for phase, count in phase_counts.items() if count == 0]
    if missing_phases:
        fail(f"{path} sample prompts do not cover lifecycle phases: {', '.join(missing_phases)}")

    if context_only_count < 4:
        fail(f"{path} needs at least four context-only prompts without explicit lifecycle phase words")

    low_diversity = []
    for slug in sorted(known - PHASE_DIVERSITY_EXCEPTIONS):
        phases = phase_by_slug.get(slug, set())
        if len(phases) < 3:
            low_diversity.append(f"{slug}={','.join(sorted(phases)) or 'none'}")
    if low_diversity:
        fail(
            f"{path} sample prompts need at least three lifecycle phases per non-exception specialist: "
            + "; ".join(low_diversity)
        )

    return cases


def select_cases(cases: list[dict[str, Any]], sample: str) -> list[dict[str, Any]]:
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score SAMPLE-PROMPTS.md through the Staff Engineer Mode router."
    )
    parser.add_argument("--responses-dir", help="directory containing <case-id>.txt responses")
    parser.add_argument("--command", help="command that reads a prompt on stdin and writes a response")
    parser.add_argument("--sample", choices=["one-per-specialist", "all"], default="one-per-specialist")
    parser.add_argument("--list-cases", action="store_true", help="print stable case IDs and prompts")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument("--warn-only", action="store_true", help="return zero even when cases fail")
    args = parser.parse_args()

    cases = select_cases(parse_sample_prompts(), args.sample)
    if args.list_cases:
        router_eval.print_case_list(cases)
        return 0

    if bool(args.responses_dir) == bool(args.command):
        fail("provide exactly one of --responses-dir or --command")

    names = router_eval.specialist_names()
    responses_dir = Path(args.responses_dir) if args.responses_dir else None
    results: list[router_eval.CaseResult] = []
    for index, case in enumerate(cases, 1):
        result_id = router_eval.case_id(index, case)
        try:
            response = (
                router_eval.read_response(responses_dir, result_id)
                if responses_dir is not None
                else router_eval.command_response(str(args.command), str(case["prompt"]))
            )
        except RuntimeError as exc:
            results.append(
                router_eval.CaseResult(
                    case_id=result_id,
                    category=str(case["category"]),
                    expected_primary=str(case["expected_primary"]),
                    actual_primary=None,
                    passed=False,
                    failures=[str(exc)],
                )
            )
            continue
        results.append(router_eval.score_case(case, response, names, index))

    summary = router_eval.summarize(results)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        router_eval.print_summary(summary)
    return 0 if args.warn_only or not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
