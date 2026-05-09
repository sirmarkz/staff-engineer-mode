#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

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
            "expected_gates": ["single_primary", "intent_inference"],
        }
        response = """```routing
{"primary":"observability-and-alerting","secondary":null,"confidence":"medium","artifact":"investigation plan","surface":"observability","phase":"active incident","rationale":"The user needs telemetry to locate failures."}
```"""

        result = runner.score_case(case, response, ["observability-and-alerting"])

        self.assertTrue(result.passed, result.failures)

    def test_score_ambiguous_case_rejects_forbidden_skill_names(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Make alerts better for checkout.",
            "expected_primary": "staff-engineer-mode",
            "expected_behavior": "ask without naming specialists",
            "category": "ambiguous",
            "expected_gates": ["ambiguity_check"],
            "forbidden_in_response": ["all_specialist_names"],
        }

        result = runner.score_case(
            case,
            "Do you want observability-and-alerting work or SLO policy?",
            ["observability-and-alerting", "slo-and-error-budgets"],
        )

        self.assertFalse(result.passed)
        self.assertIn("forbidden skill name leaked: observability-and-alerting", result.failures)

    def test_score_capability_translation_rejects_repeated_tool_terms(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Configure Istio retry policy for checkout calls.",
            "expected_primary": "dependency-resilience",
            "expected_behavior": "translate tool name into dependency controls",
            "category": "paraphrase",
            "expected_gates": ["single_primary", "capability_translation", "intent_inference"],
        }
        response = """```routing
{"primary":"dependency-resilience","secondary":null,"confidence":"high","artifact":"Istio retry policy","surface":"dependency resilience","phase":"design","rationale":"Istio retry settings are the requested control."}
```"""

        result = runner.score_case(case, response, ["dependency-resilience"])

        self.assertFalse(result.passed)
        self.assertIn("capability_translation gate failed: repeated tool term 'istio'", result.failures)


if __name__ == "__main__":
    unittest.main()
