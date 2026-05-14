#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_skill_pack.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skill_pack", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load validate_skill_pack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateSkillPackPhaseBehaviorTest(unittest.TestCase):
    def test_specialist_phase_behavior_requires_lifecycle_guidance(self) -> None:
        validator = load_validator()
        text = """---
name: example
description: Use when example work needs decisions
---

# Example

## Phase Behavior

- Ideation: identify risks.
- Ideation: compare options.
- Design: shape the target artifact.
- Design: name tradeoffs and checks.
- Release: define rollout checks.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_phase_behavior(text, path)
            self.assertIn("development", stderr.getvalue())

    def test_specialist_phase_behavior_accepts_full_lifecycle_guidance(self) -> None:
        validator = load_validator()
        text = """---
name: example
description: Use when example work needs decisions
---

# Example

## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, checks, and details to gather.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness details.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Existing artifact: use current code, docs, telemetry, incidents, or diffs as context for the next engineering decision; do not wait for a finished artifact before guiding design, build, release, or operation.
- Missing details: state assumptions and say what to check next instead of blocking lifecycle guidance.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            validator.validate_phase_behavior(text, path)

    def test_router_requires_lifecycle_and_context_triggers(self) -> None:
        validator = load_validator()
        text = """## When To Use

- The request asks for engineering design, review, delivery, operations, reliability, security, architecture, API, data, platform, or client guidance.
- The user asks to guide ideation, design, development, testing, release, or maintenance decisions.
- The user asks to plan implementation, guide development, de-risk an idea, or shape engineering decisions before code exists.
- The router infers applicability from context, repo, files, branch context, conversation, artifact, surface, risk, and the next decision; phase labels are signals, not hard requirements.

## Workflow

1. Identify the requested artifact and phase before naming any skill.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            validator.validate_router_phase_triggers(text, path)
            validator.validate_router_context_applicability(text, path)

    def test_router_requires_inference_first_intake_framing(self) -> None:
        validator = load_validator()
        text = """## Inputs To Infer

Infer these from the prompt, repo, files, branch context, and conversation. Do not ask the user to supply them as intake fields.

## Workflow

1. If confidence is low, infer the safest narrow in-scope route from available evidence; withhold routing only when no engineering lifecycle/control frame is present.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            validator.validate_router_inference_first(text, path)

    def test_router_requires_eval_harness_scope_boundary(self) -> None:
        validator = load_validator()
        text = """## Required Outputs

- For explicit eval-harness runs only: include a fenced routing block containing route details.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_router_eval_scope(text, path)
            self.assertIn("eval-harness scope", stderr.getvalue())

        valid = """## Required Outputs

- For explicit eval-harness runs only: include a fenced routing block only for confident in-scope routing; never emit a routing block for low-confidence, ambiguous, or out-of-scope prompts.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(valid)
            validator.validate_router_eval_scope(valid, path)

    def test_router_load_contract_requires_section_after_iron_law(self) -> None:
        validator = load_validator()
        missing_text = """# Router

## Iron Law

Stay narrow.

## Overview

Body.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(missing_text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_router_load_contract(missing_text, path)
            self.assertIn("Load Contract", stderr.getvalue())

    def test_router_load_contract_requires_three_rule_fragments(self) -> None:
        validator = load_validator()
        text = """# Router

## Iron Law

Stay narrow.

## Load Contract

Use SPECIALIST_ROOT=, Codex: , Gemini: paths. No rules listed.

## Overview

Body.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_router_load_contract(text, path)
            self.assertIn("rule fragments", stderr.getvalue())

    def test_router_load_contract_requires_platform_fallback_markers(self) -> None:
        validator = load_validator()
        text = """# Router

## Iron Law

Stay narrow.

## Load Contract

Use the Read tool. Do not use the Skill tool. Complete the Read before producing engineering guidance for routed work. A confidently-routed answer without a matching Read in the same turn is a failure.

## Overview

Body.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_router_load_contract(text, path)
            self.assertIn("platform fallback markers", stderr.getvalue())

    def test_router_load_contract_rejects_obsolete_relative_path(self) -> None:
        validator = load_validator()
        text = """# Router

## Iron Law

Stay narrow.

## Load Contract

Use the Read tool. Do not use the Skill tool. Complete the Read before producing engineering guidance for routed work. A confidently-routed answer without a matching Read in the same turn is a failure. SPECIALIST_ROOT=, Codex:, Gemini: ../../specialists/foo.md

## Overview

Body.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_router_load_contract(text, path)
            self.assertIn("obsolete relative path", stderr.getvalue())

    def test_router_load_contract_accepts_complete_section(self) -> None:
        validator = load_validator()
        text = """# Router

## Iron Law

Stay narrow.

## Load Contract

Resolve via SPECIALIST_ROOT= when present. Otherwise: Codex: ~/.codex/.../specialists. Gemini: relative to GEMINI.md.

- Use the Read tool. Do not use the Skill tool.
- Complete the Read before producing engineering guidance for routed work.
- A confidently-routed answer without a matching Read in the same turn is a routing failure.

## Overview

Body.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            validator.validate_router_load_contract(text, path)

    def test_non_exception_specialist_rejects_audit_only_framing(self) -> None:
        validator = load_validator()
        text = """---
name: example
description: Use when example work needs decisions
---

# Example

## When To Use

- Use only after a PR exists and review existing artifacts only, even when a decision and assumptions are needed.

## Info To Gather

- Existing diff, test evidence, and assumptions.

## Workflow

1. Review existing artifacts only and ignore the next decision.

## Required Outputs

- Findings from the existing diff, with decision evidence and assumptions.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "example" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            stderr = io.StringIO()
            with self.assertRaises(SystemExit), redirect_stderr(stderr):
                validator.validate_decision_guide_framing(text, path)
            self.assertIn("audit-only", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
