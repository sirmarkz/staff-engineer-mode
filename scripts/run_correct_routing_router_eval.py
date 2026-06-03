#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from staff_engineer_mode_contract import ROUTER_SAMPLE_PROMPT_CHECKS

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

ROUTER_EVAL_PATH = ROOT / "scripts" / "run_router_eval.py"
SPEC = importlib.util.spec_from_file_location("run_router_eval", ROUTER_EVAL_PATH)
assert SPEC is not None
router_eval = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(router_eval)

POSITIVE_ROUTING_PROMPTS = ROOT / "evals" / "prompts" / "expected-routes.md"


def fail(message: str) -> None:
    print(f"positive routing prompt eval failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_positive_routings(path: Path = POSITIVE_ROUTING_PROMPTS) -> list[dict[str, Any]]:
    return router_eval.parse_positive_routings(path)


def select_cases(cases: list[dict[str, Any]], sample: str) -> list[dict[str, Any]]:
    return router_eval.select_sample_cases(cases, sample)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score evals/prompts/expected-routes.md through the Staff Engineer Mode router."
    )
    parser.add_argument("--responses-dir", help="directory containing <case-id>.txt responses")
    parser.add_argument("--command", help="command that reads a prompt on stdin and writes a response")
    parser.add_argument("--sample", choices=["one-per-specialist", "all"], default="one-per-specialist")
    parser.add_argument("--list-cases", action="store_true", help="print stable case IDs and prompts")
    parser.add_argument("--jobs", type=int, default=1, help="number of cases to score concurrently")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument("--warn-only", action="store_true", help="return zero even when cases fail")
    args = parser.parse_args()

    cases = select_cases(parse_positive_routings(), args.sample)
    if args.list_cases:
        router_eval.print_case_list(cases)
        return 0

    if bool(args.responses_dir) == bool(args.command):
        fail("provide exactly one of --responses-dir or --command")

    names = router_eval.specialist_names()
    responses_dir = Path(args.responses_dir) if args.responses_dir else None
    results = router_eval.score_cases(
        cases,
        names,
        responses_dir=responses_dir,
        command=args.command,
        jobs=args.jobs,
    )

    summary = router_eval.summarize(results)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        router_eval.print_summary(summary)
    return 0 if args.warn_only or not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
