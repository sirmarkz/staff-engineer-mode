#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
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
    def test_parse_positive_routings_produces_five_cases_per_specialist(self) -> None:
        runner = load_runner()

        cases = runner.parse_positive_routings()
        names = runner.specialist_names()

        self.assertEqual(len(cases), len(names) * 5 + 4)
        self.assertEqual(sum(1 for case in cases if case["expected_primary"] == "none"), 4)
        self.assertTrue(all(case["category"] in {"positive_routing", "out_of_scope"} for case in cases))

    def test_parse_boundary_prompts_has_all_boundary_categories_per_specialist(self) -> None:
        runner = load_runner()

        cases = runner.parse_boundary_prompts()
        names = set(runner.specialist_names())
        counts: dict[str, int] = {}
        by_target: dict[str, set[str]] = {}
        for case in cases:
            target = str(case["target_specialist"])
            counts[target] = counts.get(target, 0) + 1
            by_target.setdefault(target, set()).add(str(case["category"]))

        self.assertEqual(len(cases), len(names) * 20)
        self.assertEqual(set(by_target), names)
        for name in names:
            self.assertEqual(counts[name], 20)
            self.assertEqual(
                by_target[name],
                {"negative", "near_miss", "keyword_bait", "adversarial"},
            )
        self.assertTrue(all("design_source" not in case for case in cases))
        self.assertTrue(
            all(case["expected_primary"] != case["target_specialist"] for case in cases),
            "boundary cases should prove the named specialist does not fire on near misses",
        )

    def test_load_catalog_cases_selects_boundary_catalog(self) -> None:
        runner = load_runner()

        cases = runner.load_catalog_cases("boundary", "all")

        self.assertTrue(cases)
        self.assertTrue(
            all(
                case["category"]
                in {"negative", "near_miss", "keyword_bait", "adversarial"}
                for case in cases
            )
        )

    def test_load_catalog_cases_combines_sample_and_boundary_catalogs(self) -> None:
        runner = load_runner()

        sample_cases = runner.load_catalog_cases("positive", "all")
        boundary_cases = runner.load_catalog_cases("boundary", "all")
        all_cases = runner.load_catalog_cases("all", "all")

        self.assertEqual(len(all_cases), len(sample_cases) + len(boundary_cases))

    def test_filter_cases_by_category_selects_out_of_scope_cases(self) -> None:
        runner = load_runner()

        cases = runner.filter_cases_by_category(runner.parse_positive_routings(), "out_of_scope")

        self.assertEqual(len(cases), 4)
        self.assertTrue(all(case["expected_primary"] == "none" for case in cases))

    def test_select_cases_by_id_preserves_requested_order_and_original_ids(self) -> None:
        runner = load_runner()
        cases = [
            {
                "prompt": "Design a highly available checkout service.",
                "expected_primary": "high-availability-design",
                "expected_behavior": "route to HA",
                "category": "positive_routing",
                "expected_checks": ["single_primary", "intent_inference"],
            },
            {
                "prompt": "Define error budget policy for checkout.",
                "expected_primary": "slo-and-error-budgets",
                "expected_behavior": "route to SLO policy",
                "category": "positive_routing",
                "expected_checks": ["single_primary", "intent_inference"],
            },
        ]

        selected = runner.select_cases_by_id(cases, ["002-slo-and-error-budgets", "001-high-availability-design"])

        self.assertEqual(
            [case["expected_primary"] for case in selected],
            ["slo-and-error-budgets", "high-availability-design"],
        )
        self.assertEqual(runner.case_id(1, selected[0]), "002-slo-and-error-budgets")
        self.assertEqual(runner.case_id(2, selected[1]), "001-high-availability-design")

    def test_select_cases_by_id_rejects_unknown_and_duplicate_ids(self) -> None:
        runner = load_runner()
        cases = [
            {
                "prompt": "Design a highly available checkout service.",
                "expected_primary": "high-availability-design",
                "expected_behavior": "route to HA",
                "category": "positive_routing",
                "expected_checks": ["single_primary", "intent_inference"],
            }
        ]

        with self.assertRaises(SystemExit):
            runner.select_cases_by_id(cases, ["999-missing"])
        with self.assertRaises(SystemExit):
            runner.select_cases_by_id(cases, ["001-high-availability-design", "001-high-availability-design"])

    def test_load_case_id_file_accepts_plain_ids_and_failure_summary_lines(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failures.txt"
            path.write_text(
                "# failed full run\n"
                "068-release-build-reproducibility\n"
                "748-data-contracts failed:\n"
                "1089-resilience-experiments\n"
                "\n",
                encoding="utf-8",
            )

            ids = runner.load_case_id_file(path)

        self.assertEqual(ids, ["068-release-build-reproducibility", "748-data-contracts", "1089-resilience-experiments"])

    def test_random_specialist_cases_selects_distinct_specialists(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(runner.parse_positive_routings(), "positive_routing")

        selected = runner.random_specialist_cases(cases, 10, "release-seed")

        primaries = [case["expected_primary"] for case in selected]
        self.assertEqual(len(selected), 10)
        self.assertEqual(len(set(primaries)), 10)
        self.assertNotIn("none", primaries)

    def test_random_specialist_cases_uses_boundary_target_specialists(self) -> None:
        runner = load_runner()
        cases = runner.parse_boundary_prompts()

        selected = runner.random_specialist_cases(cases, 10, "release-seed")

        targets = [case["target_specialist"] for case in selected]
        self.assertEqual(len(selected), 10)
        self.assertEqual(len(set(targets)), 10)

    def test_random_specialist_cases_is_seed_deterministic(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(runner.parse_positive_routings(), "positive_routing")

        first = runner.random_specialist_cases(cases, 10, "release-seed")
        second = runner.random_specialist_cases(cases, 10, "release-seed")

        self.assertEqual(
            [case["prompt"] for case in first],
            [case["prompt"] for case in second],
        )

    def test_random_specialist_cases_rejects_invalid_counts(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(runner.parse_positive_routings(), "positive_routing")

        with self.assertRaises(SystemExit):
            runner.random_specialist_cases(cases, 0, "release-seed")
        with self.assertRaises(SystemExit):
            runner.random_specialist_cases(cases, len(runner.specialist_names()) + 1, "release-seed")

    def test_command_response_reports_stdout_when_command_fails_without_stderr(self) -> None:
        runner = load_runner()

        with patch.object(
            runner.subprocess,
            "run",
            return_value=subprocess.CompletedProcess("adapter", 1, "stdout-failure-token\n", ""),
        ):
            with self.assertRaisesRegex(RuntimeError, "stdout-failure-token"):
                runner.command_response("adapter", "prompt")

    def test_command_response_marks_adapter_failures(self) -> None:
        runner = load_runner()

        with patch.object(
            runner.subprocess,
            "run",
            return_value=subprocess.CompletedProcess("adapter", 1, "", "transient provider failure\n"),
        ):
            with self.assertRaisesRegex(RuntimeError, "command failed: transient provider failure"):
                runner.command_response("adapter", "prompt")

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

    def test_main_rejects_case_ids_with_random_or_limit_selection(self) -> None:
        runner = load_runner()

        for flag in ("--random", "--random-specialists", "--limit"):
            with self.subTest(flag=flag):
                with patch.object(
                    sys,
                    "argv",
                    [
                        "run_router_eval.py",
                        "--sample",
                        "all",
                        "--case-id",
                        "001-high-availability-design",
                        flag,
                        "1",
                        "--list-cases",
                    ],
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
                "category": "positive_routing",
                "expected_checks": ["single_primary", "intent_inference"],
            },
            {
                "prompt": "Define error budget policy for checkout.",
                "expected_primary": "slo-and-error-budgets",
                "expected_behavior": "route to SLO policy",
                "category": "positive_routing",
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
            "category": "positive_routing",
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

    def test_summarize_counts_failure_types(self) -> None:
        runner = load_runner()
        results = [
            runner.CaseResult(
                case_id="748-data-contracts",
                category="near_miss",
                expected_primary="data-contracts",
                actual_primary=None,
                passed=False,
                failures=["missing routing block"],
            ),
            runner.CaseResult(
                case_id="278-none",
                category="negative",
                expected_primary="none",
                actual_primary="api-design-and-compatibility",
                passed=False,
                failures=[
                    "forbidden skill name leaked: api-design-and-compatibility",
                    "routing block emitted for low-confidence or out-of-scope case",
                    "scope_check check failed: routed out-of-scope prompt",
                ],
            ),
        ]

        summary = runner.summarize(results)

        self.assertEqual(summary["failure_types"], {"model_format": 1, "over_route": 1})
        self.assertEqual(summary["failures"][0]["failure_types"], ["model_format"])
        self.assertEqual(summary["failures"][1]["failure_types"], ["over_route"])

    def test_summarize_counts_command_errors(self) -> None:
        runner = load_runner()
        results = [
            runner.CaseResult(
                case_id="673-observability-and-alerting",
                category="near_miss",
                expected_primary="observability-and-alerting",
                actual_primary=None,
                passed=False,
                failures=["command failed: gpt-image-2 does not exist"],
            )
        ]

        summary = runner.summarize(results)

        self.assertEqual(summary["failure_types"], {"command_error": 1})
        self.assertEqual(summary["failures"][0]["failure_types"], ["command_error"])

    def test_progress_writer_appends_case_records_and_summary(self) -> None:
        runner = load_runner()
        results = [
            runner.CaseResult(
                case_id="001-high-availability-design",
                category="positive_routing",
                expected_primary="high-availability-design",
                actual_primary="high-availability-design",
                passed=True,
                failures=[],
            ),
            runner.CaseResult(
                case_id="002-slo-and-error-budgets",
                category="positive_routing",
                expected_primary="slo-and-error-budgets",
                actual_primary="observability-and-alerting",
                passed=False,
                failures=[
                    "primary mismatch: expected slo-and-error-budgets, got observability-and-alerting"
                ],
            ),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress" / "router-eval.jsonl"
            writer = runner.JsonlProgressWriter(path, total=2)

            writer.write_case(results[0])
            first_snapshot = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            writer.write_case(results[1])
            writer.write_summary(runner.summarize(results))
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(len(first_snapshot), 1)
        self.assertEqual(first_snapshot[0]["type"], "case")
        self.assertEqual(first_snapshot[0]["completed"], 1)
        self.assertEqual(first_snapshot[0]["total"], 2)
        self.assertEqual(records[1]["failure_types"], ["route_mismatch"])
        self.assertEqual(records[2]["type"], "summary")
        self.assertEqual(records[2]["summary"]["passed"], 1)
        self.assertEqual(records[2]["summary"]["total"], 2)


    def test_no_skill_invoke_check_fails_on_specialist_skill_call(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "positive_routing",
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
            "category": "positive_routing",
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
            "category": "positive_routing",
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
            "category": "positive_routing",
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
            "category": "positive_routing",
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
            "category": "positive_routing",
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
            "category": "positive_routing",
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
