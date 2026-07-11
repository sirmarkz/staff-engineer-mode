#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_RELEASE_MODEL = "claude-opus-4-8"
CODEX_RELEASE_MODEL = "gpt-5.6-terra"
RELEASE_EFFORT = "high"


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
            "seeded positive, boundary-category, and router-contract eval slices for each host."
        )
    )
    parser.add_argument("--random-specialists", type=int, default=5)
    parser.add_argument("--seed", default="staff-engineer-mode-release")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--eval-case-timeout", type=int, default=600)
    parser.add_argument(
        "--evidence-dir",
        help=(
            "new directory for write-once router eval manifests, case records, "
            "and final responses"
        ),
    )
    parser.add_argument("--keep-temp", action="store_true")
    return parser.parse_args()


def reserve_evidence_dir(value: str | None) -> Path:
    if value is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = ROOT / "evals" / "runs" / f"release-{stamp}-{os.getpid()}"
    else:
        candidate = Path(value)
        path = candidate if candidate.is_absolute() else ROOT / candidate
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.mkdir(mode=0o700)
    except FileExistsError:
        raise SystemExit(f"refusing to reuse release evidence directory {path}")
    except OSError as exc:
        raise SystemExit(f"cannot reserve release evidence directory {path}: {exc}")
    return path


def main() -> int:
    args = parse_args()
    if args.eval_case_timeout < 1 or args.jobs < 1 or args.random_specialists < 1:
        raise SystemExit(
            "--eval-case-timeout, --jobs, and --random-specialists must be positive"
        )
    if args.timeout is not None and args.timeout < 1:
        raise SystemExit("--timeout must be positive")
    evidence_dir = reserve_evidence_dir(args.evidence_dir)
    print(f"release evidence: {evidence_dir}", flush=True)
    run_step(
        "platform support validation",
        ["python3", "scripts/validate_platform_support.py"],
    )
    run_step(
        "router eval static validation",
        ["python3", "scripts/validate_router_eval.py"],
    )
    run_step(
        "event policy regression tests",
        ["python3", "scripts/test_agent_event_policy_hook.py"],
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
        CLAUDE_RELEASE_MODEL,
        "--claude-effort",
        RELEASE_EFFORT,
        "--codex-model",
        CODEX_RELEASE_MODEL,
        "--codex-effort",
        RELEASE_EFFORT,
        "--work-dir",
        str(evidence_dir / "hook-probes"),
    ]
    if args.timeout is not None:
        hook_command.extend(["--timeout", str(args.timeout)])
    if args.keep_temp:
        hook_command.append("--keep-temp")
    run_step("live hook probes", hook_command)

    host_configs = [
        (
            "Codex",
            CODEX_RELEASE_MODEL,
            "evals/adapters/codex-router.sh",
            {"CODEX_MODEL": CODEX_RELEASE_MODEL, "CODEX_EFFORT": RELEASE_EFFORT},
        ),
        (
            "Claude",
            CLAUDE_RELEASE_MODEL,
            "evals/adapters/claude-router.sh",
            {"CLAUDE_MODEL": CLAUDE_RELEASE_MODEL, "CLAUDE_EFFORT": RELEASE_EFFORT},
        ),
    ]
    for host, model, adapter, env in host_configs:
        host_slug = host.lower()
        common = [
            "--seed",
            args.seed,
            "--jobs",
            str(args.jobs),
            "--case-timeout",
            str(args.eval_case_timeout),
            "--command",
            adapter,
            "--json",
        ]
        run_step(
            f"{host} {model} {RELEASE_EFFORT} positive router eval",
            [
                "python3",
                "scripts/run_router_eval.py",
                "--catalog",
                "positive",
                "--sample",
                "all",
                "--category",
                "positive_routing",
                "--random-specialists",
                str(args.random_specialists),
                "--results-dir",
                str(evidence_dir / f"{host_slug}-positive"),
                *common,
            ],
            env=env,
        )
        run_step(
            f"{host} {model} {RELEASE_EFFORT} boundary router eval",
            [
                "python3",
                "scripts/run_router_eval.py",
                "--catalog",
                "boundary",
                "--stratified-categories",
                "1",
                "--results-dir",
                str(evidence_dir / f"{host_slug}-boundary"),
                *common,
            ],
            env=env,
        )
        run_step(
            f"{host} {model} {RELEASE_EFFORT} contract router eval",
            [
                "python3",
                "scripts/run_router_eval.py",
                "--catalog",
                "contract",
                "--check-cover",
                "capability_translation",
                "--check-cover",
                "ambiguity_check",
                "--check-cover",
                "scope_check",
                "--check-cover",
                "secondary_cap",
                "--results-dir",
                str(evidence_dir / f"{host_slug}-contract"),
                *common,
            ],
            env=env,
        )

    print("release live checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
