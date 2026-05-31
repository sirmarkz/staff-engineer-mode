#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, command: list[str], env: dict[str, str] | None = None) -> None:
    print(f"==> {name}", flush=True)
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    completed = subprocess.run(command, cwd=ROOT, env=process_env, check=False)
    if completed.returncode != 0:
        print(f"release live checks failed at {name}", file=sys.stderr)
        raise SystemExit(completed.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Release-blocking live checks: Claude/Codex hook probes plus "
            "5 seeded random specialist router evals from SAMPLE-PROMPTS.md for each host."
        )
    )
    parser.add_argument("--random-specialists", type=int, default=5)
    parser.add_argument("--seed", default="staff-engineer-mode-release")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=360)
    parser.add_argument("--claude-model", default="claude-opus-4-8")
    parser.add_argument("--codex-model", default="gpt-5.5")
    parser.add_argument("--hook-effort", default="high")
    parser.add_argument("--eval-effort", default="high")
    parser.add_argument("--keep-temp", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_step(
        "platform support validation",
        ["python3", "scripts/validate_platform_support.py"],
    )
    hook_command = [
        "python3",
        "scripts/run_live_hook_probes.py",
        "--host",
        "all",
        "--event",
        "all",
        "--probe",
        "all",
        "--claude-model",
        args.claude_model,
        "--claude-effort",
        args.hook_effort,
        "--codex-model",
        args.codex_model,
        "--codex-effort",
        args.hook_effort,
        "--timeout",
        str(args.timeout),
    ]
    if args.keep_temp:
        hook_command.append("--keep-temp")
    run_step("live hook probes", hook_command)

    run_step(
        f"Codex {args.codex_model} {args.eval_effort} random router eval",
        [
            "python3",
            "scripts/run_router_eval.py",
            "--sample",
            "all",
            "--category",
            "sample_prompt",
            "--random-specialists",
            str(args.random_specialists),
            "--seed",
            args.seed,
            "--jobs",
            str(args.jobs),
            "--command",
            "evals/adapters/codex-router.sh",
            "--json",
        ],
        env={"CODEX_MODEL": args.codex_model, "CODEX_EFFORT": args.eval_effort},
    )
    run_step(
        f"Claude {args.claude_model} {args.eval_effort} random router eval",
        [
            "python3",
            "scripts/run_router_eval.py",
            "--sample",
            "all",
            "--category",
            "sample_prompt",
            "--random-specialists",
            str(args.random_specialists),
            "--seed",
            args.seed,
            "--jobs",
            str(args.jobs),
            "--command",
            "evals/adapters/claude-router.sh",
            "--json",
        ],
        env={"CLAUDE_MODEL": args.claude_model, "CLAUDE_EFFORT": args.eval_effort},
    )

    print("release live checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
