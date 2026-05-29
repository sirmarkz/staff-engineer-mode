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
    def test_agent_pr_review_rejects_trivial_commit_skip(self) -> None:
        validator = load_validator()
        text = """---
name: agent-pr-review
description: Use when reviewing a PR, diff, branch, commit, staged change, merge, or pre-release change set
---

# Pre-Merge PR Review

## When To Use

- The agent is about to create or amend a commit and needs review of the exact staged diff before the commit exists, regardless of change size.

## When Not To Use

- The diff is one trivial fix the human author can self-review without a structured pass.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent-pr-review" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_agent_pr_review_commit_policy(text, path)

    def test_agent_pr_review_requires_commit_attempts_regardless_of_size(self) -> None:
        validator = load_validator()
        text = """---
name: agent-pr-review
description: Use when reviewing a PR, diff, branch, commit, staged change, merge, or pre-release change set
---

# Pre-Merge PR Review

## When To Use

- The agent is about to create or amend a commit and needs review of the exact staged diff before the commit exists, regardless of change size.

## When Not To Use

- The work is pre-design: there is no diff yet; use another specialist instead.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent-pr-review" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            validator.validate_agent_pr_review_commit_policy(text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_phase_behavior(text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_eval_scope(text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(missing_text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(text, path)

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
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_decision_guide_framing(text, path)

    def test_slo_specialist_requires_burn_response_split(self) -> None:
        validator = load_validator()
        text = """---
name: slo-and-error-budgets
description: Use when user journeys need SLOs
---

# SLO Error Budget Engineering

## Workflow

1. Design burn-rate alerts.

## Required Outputs

- Burn-rate alert rules.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "slo-and-error-budgets" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_slo_burn_response_split(text, path)

    def test_slo_specialist_accepts_burn_response_split(self) -> None:
        validator = load_validator()
        text = """---
name: slo-and-error-budgets
description: Use when user journeys need SLOs
---

# SLO Error Budget Engineering

## Workflow

1. Separate urgent burn alerts from follow-up-only budget responses with short-window and longer-window checks.
2. Keep multi-hour and multi-day budget threats as diagnostic non-urgent follow-up work when immediate action is not required.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "slo-and-error-budgets" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            validator.validate_slo_burn_response_split(text, path)

    def test_config_specialist_requires_runtime_override_cleanup_controls(self) -> None:
        validator = load_validator()
        text = """---
name: configuration-and-automation-safety
description: Use when config automation touches production state
---

# Configuration And Automation Safety

## When To Use

- Use when configuration decisions and assumptions need production safety checks.

## When Not To Use

- Local-only settings with no shared-state risk.

## Info To Gather

- Config surface, assumptions, consumers, schema, defaults, and change path.

## Workflow

1. Classify the change, define the contract, validate, preview, and recover.

## Synthesized Default

Use typed contracts and previews.

## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, checks, and details to gather.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness details.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Existing artifact: use current code, docs, telemetry, incidents, or diffs as context for the next engineering decision; do not wait for a finished artifact before guiding design, build, release, or operation.
- Missing details: state assumptions and say what to check next instead of blocking lifecycle guidance.

## Exceptions

- Emergency changes still need confirmation.

## Response Quality Bar

- Lead with the safety decision.

## Required Outputs

- Contract and validation plan.

## Checks Before Moving On

- `contract_defined`: schema and defaults are explicit.
- `preview_checked`: intended effect is visible.
- `recovery_path`: recovery is defined.

## Red Flags - Stop And Rework

- Config bypasses validation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Syntax only | Add semantic checks. |
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "configuration-and-automation-safety" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_specialist_skill(text, path)

    def test_config_specialist_accepts_runtime_override_cleanup_controls(self) -> None:
        validator = load_validator()
        text = """---
name: configuration-and-automation-safety
description: Use when config automation touches production state
---

# Configuration And Automation Safety

## When To Use

- Use when runtime config values, temporary overrides, cleanup automation, decisions, and assumptions need production safety checks.

## When Not To Use

- Local-only settings with no shared-state risk.

## Info To Gather

- Runtime config values, unsafe values, temporary overrides, owner, expiry, validation evidence, rollback target, consumers, schema, defaults, and change path.

## Workflow

1. Classify the change, define the contract, validate, preview, block cleanup automation when override records are incomplete, and recover.

## Synthesized Default

Use typed contracts and previews.

## Phase Behavior

- Ideation: identify risks, defaults, unknowns, options, and the next decision before code exists.
- Design: shape the target artifact, tradeoffs, checks, and details to gather.
- Development: guide sequencing, code boundaries, checks, and acceptance criteria.
- Testing: define release-blocking tests, evals, fixtures, and failure probes.
- Release: define rollout, observability, abort, rollback, and readiness details.
- Maintenance: define owners, drift checks, cleanup triggers, and refresh cadence.
- Existing artifact: use current code, docs, telemetry, incidents, or diffs as context for the next engineering decision; do not wait for a finished artifact before guiding design, build, release, or operation.
- Missing details: state assumptions and say what to check next instead of blocking lifecycle guidance.

## Exceptions

- Emergency changes still need confirmation.

## Response Quality Bar

- Lead with the safety decision.

## Required Outputs

- Contract and validation plan.

## Checks Before Moving On

- `contract_defined`: schema and defaults are explicit.
- `preview_checked`: intended effect is visible.
- `recovery_path`: recovery is defined.

## Red Flags - Stop And Rework

- Config bypasses validation.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Syntax only | Add semantic checks. |
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "configuration-and-automation-safety" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(text)
            validator.validate_specialist_skill(text, path)


if __name__ == "__main__":
    unittest.main()
