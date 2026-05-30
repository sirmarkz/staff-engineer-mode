#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_router_eval.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_router_eval", RUNNER)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load run_router_eval.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RouterEvalHarnessTests(unittest.TestCase):
    def test_parse_sample_prompts_produces_four_cases_per_specialist(self) -> None:
        runner = load_runner()

        cases = runner.parse_sample_prompts()
        names = runner.specialist_names()

        self.assertEqual(len(cases), len(names) * 4 + 4)
        self.assertEqual(sum(1 for case in cases if case["expected_primary"] == "none"), 4)
        self.assertTrue(all(case["category"] in {"sample_prompt", "out_of_scope"} for case in cases))

    def test_filter_cases_by_category_selects_out_of_scope_cases(self) -> None:
        runner = load_runner()

        cases = runner.filter_cases_by_category(runner.parse_sample_prompts(), "out_of_scope")

        self.assertEqual(len(cases), 4)
        self.assertTrue(all(case["expected_primary"] == "none" for case in cases))

    def test_random_specialist_cases_selects_distinct_specialists(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(runner.parse_sample_prompts(), "sample_prompt")

        selected = runner.random_specialist_cases(cases, 10, "release-seed")

        primaries = [case["expected_primary"] for case in selected]
        self.assertEqual(len(selected), 10)
        self.assertEqual(len(set(primaries)), 10)
        self.assertNotIn("none", primaries)

    def test_random_specialist_cases_is_seed_deterministic(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(runner.parse_sample_prompts(), "sample_prompt")

        first = runner.random_specialist_cases(cases, 10, "release-seed")
        second = runner.random_specialist_cases(cases, 10, "release-seed")

        self.assertEqual(
            [case["prompt"] for case in first],
            [case["prompt"] for case in second],
        )

    def test_random_specialist_cases_rejects_invalid_counts(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(runner.parse_sample_prompts(), "sample_prompt")

        with self.assertRaises(SystemExit):
            runner.random_specialist_cases(cases, 0, "release-seed")
        with self.assertRaises(SystemExit):
            runner.random_specialist_cases(cases, len(runner.specialist_names()) + 1, "release-seed")

    def test_main_rejects_limit_with_random_selection(self) -> None:
        runner = load_runner()

        for flag in ("--random", "--random-specialists"):
            with self.subTest(flag=flag):
                with patch.object(
                    sys,
                    "argv",
                    ["run_router_eval.py", "--sample", "all", "--limit", "5", flag, "2", "--list-cases"],
                ):
                    with self.assertRaises(SystemExit):
                        runner.main()

    def test_parse_routing_block_reads_json_payload(self) -> None:
        runner = load_runner()
        response = """Reasoning summary.

```routing
{"primary":"observability-and-alerting","secondary":null,"confidence":"high","artifact":"plan","surface":"observability","phase":"design","rationale":"Telemetry construction is the requested artifact."}
```
"""

        block = runner.parse_routing_block(response)

        self.assertEqual(block["primary"], "observability-and-alerting")
        self.assertIsNone(block["secondary"])
        self.assertEqual(block["confidence"], "high")

    def test_score_confident_case_requires_primary_and_intent_fields(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "During incidents the team cannot find the failing dependency.",
            "expected_primary": "observability-and-alerting",
            "expected_behavior": "route to observability",
            "category": "paraphrase",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        response = """```routing
{"primary":"observability-and-alerting","secondary":null,"confidence":"medium","artifact":"investigation plan","surface":"observability","phase":"active incident","rationale":"The user needs telemetry to locate failures."}
```"""

        result = runner.score_case(case, response, ["observability-and-alerting"])

        self.assertTrue(result.passed, result.failures)

    def test_score_cases_preserves_order_with_parallel_jobs(self) -> None:
        runner = load_runner()
        cases = [
            {
                "prompt": "Design a highly available checkout service.",
                "expected_primary": "high-availability-design",
                "expected_behavior": "route to HA",
                "category": "sample_prompt",
                "expected_checks": ["single_primary", "intent_inference"],
            },
            {
                "prompt": "Define error budget policy for checkout.",
                "expected_primary": "slo-and-error-budgets",
                "expected_behavior": "route to SLO policy",
                "category": "sample_prompt",
                "expected_checks": ["single_primary", "intent_inference"],
            },
        ]
        responses = [
            """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"survivability."}
```""",
            """```routing
{"primary":"slo-and-error-budgets","secondary":null,"confidence":"medium","artifact":"policy","surface":"reliability","phase":"design","rationale":"budget policy."}
```""",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            response_dir = Path(tmp)
            for index, case in enumerate(cases, 1):
                (response_dir / f"{runner.case_id(index, case)}.txt").write_text(
                    responses[index - 1],
                    encoding="utf-8",
                )

            results = runner.score_cases(
                cases,
                names=["high-availability-design", "slo-and-error-budgets"],
                responses_dir=response_dir,
                jobs=2,
            )

        self.assertEqual([result.case_id for result in results], ["001-high-availability-design", "002-slo-and-error-budgets"])
        self.assertTrue(all(result.passed for result in results), [result.failures for result in results])

    def test_score_no_route_case_rejects_forbidden_skill_names(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Write a marketing launch plan.",
            "expected_primary": "none",
            "expected_behavior": "decline without naming specialists",
            "category": "out_of_scope",
            "expected_checks": ["scope_check"],
            "forbidden_in_response": ["all_specialist_names"],
        }

        result = runner.score_case(
            case,
            "This is out of scope. Try observability-and-alerting instead.",
            ["observability-and-alerting", "slo-and-error-budgets"],
        )

        self.assertFalse(result.passed)

    def test_score_capability_translation_rejects_repeated_tool_terms(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Configure Istio retry policy for checkout calls.",
            "expected_primary": "dependency-resilience",
            "expected_behavior": "translate tool name into dependency controls",
            "category": "paraphrase",
            "expected_checks": ["single_primary", "capability_translation", "intent_inference"],
        }
        response = """```routing
{"primary":"dependency-resilience","secondary":null,"confidence":"high","artifact":"Istio retry policy","surface":"dependency resilience","phase":"design","rationale":"Istio retry settings are the requested control."}
```"""

        result = runner.score_case(case, response, ["dependency-resilience"])

        self.assertFalse(result.passed)

    def test_score_rejects_unknown_expected_check_ids(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "unknown_shape_check"],
        }
        response = """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability plan."}
```"""

        result = runner.score_case(case, response, ["high-availability-design"])

        self.assertFalse(result.passed)
        self.assertTrue(
            any("unknown expected_checks" in failure for failure in result.failures),
            result.failures,
        )


    def test_no_skill_invoke_check_fails_on_specialist_skill_call(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "no_skill_invoke"],
        }
        response = """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability plan."}
```

Skill(staff-engineer-mode:high-availability-design)
"""
        result = runner.score_case(case, response, ["high-availability-design"])
        self.assertFalse(result.passed)

    def test_no_skill_invoke_check_catches_quoted_skill_call(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "no_skill_invoke"],
        }
        for invocation in (
            'Skill("staff-engineer-mode:high-availability-design")',
            "Skill: high-availability-design",
            "Skill 'high-availability-design'",
            'Skill("high-availability-design")',
        ):
            response = (
                "```routing\n"
                '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability."}\n'
                "```\n\n"
                + invocation
                + "\n"
            )
            result = runner.score_case(case, response, ["high-availability-design"])
            self.assertFalse(
                result.passed,
                f"expected failure for invocation {invocation!r}, got pass",
            )

    def test_no_skill_invoke_check_passes_without_skill_call(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "no_skill_invoke"],
        }
        response = """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability plan."}
```

Read(/abs/path/specialists/high-availability-design.md)
"""
        result = runner.score_case(case, response, ["high-availability-design"])
        self.assertTrue(result.passed, result.failures)

    def test_read_load_check_fails_on_substantive_answer_without_read(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "read_load"],
        }
        body = (
            "Here is the high-availability design. "
            + "Use multiple fault domains and partition state with replicas across zones, sized for static capacity. " * 2
        )
        response = (
            "```routing\n"
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability."}\n'
            "```\n\n"
            + body
        )
        result = runner.score_case(case, response, ["high-availability-design"])
        self.assertFalse(result.passed)

    def test_read_load_check_passes_with_matching_read(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "read_load"],
        }
        body = (
            "Here is the high-availability design. "
            + "Use multiple fault domains and partition state with replicas across zones, sized for static capacity. " * 2
        )
        response = (
            "```routing\n"
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability."}\n'
            "```\n\n"
            "Read(/abs/path/specialists/high-availability-design.md)\n\n"
            + body
        )
        result = runner.score_case(case, response, ["high-availability-design"])
        self.assertTrue(result.passed, result.failures)

    def test_read_load_check_rejects_non_specialist_markdown_read(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "read_load"],
        }
        body = (
            "Here is the high-availability design. "
            + "Use multiple fault domains and partition state with replicas across zones, sized for static capacity. " * 2
        )
        response = (
            "```routing\n"
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability."}\n'
            "```\n\n"
            "Read(/abs/path/docs/high-availability-design.md)\n\n"
            + body
        )

        result = runner.score_case(case, response, ["high-availability-design"])

        self.assertFalse(result.passed)
        self.assertTrue(
            any("read_load" in f for f in result.failures),
            f"expected read_load failure, got {result.failures}",
        )

    def test_read_load_check_passes_when_body_below_threshold(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "sample_prompt",
            "expected_checks": ["single_primary", "intent_inference", "read_load"],
        }
        response = (
            "```routing\n"
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"high availability","phase":"design","rationale":"survivability."}\n'
            "```\n"
        )
        result = runner.score_case(case, response, ["high-availability-design"])
        self.assertTrue(result.passed, result.failures)


if __name__ == "__main__":
    unittest.main()
