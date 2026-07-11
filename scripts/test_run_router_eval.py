#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

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
    def assert_adapter_workspace_removed_after_timeout(
        self,
        runner,
        *,
        adapter: Path,
        host: str,
        expected_model: str,
        expected_effort: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            source_home = temp / "source-home"
            source_home.mkdir()
            observation = temp / "adapter-observation.txt"
            caller_workspace = temp / "caller-workspace"
            caller_workspace.mkdir()

            if host == "codex":
                (source_home / "auth.json").write_text(
                    '{"fixture":"credential"}\n', encoding="utf-8"
                )
                credential_path = '${CODEX_HOME}/auth.json'
                isolated_home = '${CODEX_HOME}'
                provider_environment = {"CODEX_HOME": str(source_home)}
            else:
                (source_home / ".credentials.json").write_text(
                    '{"fixture":"credential"}\n', encoding="utf-8"
                )
                credential_path = '${CLAUDE_CONFIG_DIR}/.credentials.json'
                isolated_home = '${CLAUDE_CONFIG_DIR}'
                provider_environment = {"CLAUDE_CONFIG_DIR": str(source_home)}

            fake_host = fake_bin / host
            fake_host.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        f'test -f "{credential_path}"',
                        (
                            "printf '%s\\n%s\\n%s\\n%s\\n%s\\n' "
                            '"${SEM_EVAL_ADAPTER_WORKSPACE}" '
                            f'"{isolated_home}" '
                            '"${SEM_EVAL_MODEL}" "${SEM_EVAL_EFFORT}" '
                            '"$(python3 -c \'import os,sys; print(format(os.stat(sys.argv[1]).st_mode & 0o777, "o"))\' "${SEM_EVAL_ADAPTER_WORKSPACE}")" '
                            '> "${SEM_TEST_OBSERVATION}"'
                        ),
                        "sleep 30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_host.chmod(0o755)
            environment = {
                **provider_environment,
                "PATH": f"{fake_bin}:{runner.os.environ.get('PATH', '')}",
                "SEM_EVAL_ADAPTER_WORKSPACE": str(caller_workspace),
                "SEM_EVAL_MODEL": "caller-model",
                "SEM_EVAL_EFFORT": "caller-effort",
                "SEM_TEST_OBSERVATION": str(observation),
            }

            isolated_root: Path | None = None
            try:
                with patch.dict(runner.os.environ, environment, clear=False):
                    with self.assertRaisesRegex(RuntimeError, "timed out"):
                        runner.command_response(str(adapter), "prompt", timeout=0.5)

                lines = observation.read_text(encoding="utf-8").splitlines()
                workspace = Path(lines[0])
                host_home = Path(lines[1])
                isolated_root = (
                    host_home.parent if host == "codex" else host_home.parents[1]
                )
                self.assertEqual(workspace, isolated_root)
                self.assertNotEqual(workspace, caller_workspace)
                self.assertEqual(lines[2:4], [expected_model, expected_effort])
                self.assertEqual(lines[4], "700")
                self.assertFalse(workspace.exists())
                self.assertTrue(caller_workspace.exists())
            finally:
                if isolated_root is not None and isolated_root != caller_workspace:
                    shutil.rmtree(isolated_root, ignore_errors=True)

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
                in {
                    "negative",
                    "near_miss",
                    "keyword_bait",
                    "adversarial",
                    "adversarial_split",
                }
                for case in cases
            )
        )

    def test_load_adversarial_split_catalog_binds_reviewed_cases(self) -> None:
        runner = load_runner()

        cases = runner.load_catalog_cases("adversarial-split", "all")
        review = json.loads(runner.ADVERSARIAL_SPLIT_REVIEW.read_text())
        reviewed_cases = review["cases"]
        accepted_cases = [
            case for case in reviewed_cases if case["disposition"] == "accepted"
        ]
        rejected_cases = [
            case for case in reviewed_cases if case["disposition"] == "rejected"
        ]

        self.assertEqual(len(cases), len(accepted_cases))
        self.assertTrue(all(case["category"] == "adversarial_split" for case in cases))
        self.assertTrue(all(str(case["_case_id"]).startswith("boundary-") for case in cases))
        self.assertEqual(
            review["summary"],
            {
                "reviewed": len(reviewed_cases),
                "accepted": len(accepted_cases),
                "rejected": len(rejected_cases),
            },
        )

    def test_load_catalog_cases_selects_router_contract_catalog(self) -> None:
        runner = load_runner()

        cases = runner.load_catalog_cases("contract", "all")

        self.assertGreaterEqual(len(cases), 35)
        self.assertIn("mixed_intent", {case["category"] for case in cases})
        self.assertGreaterEqual(
            sum(case["category"] == "ambiguous" for case in cases),
            4,
        )
        self.assertTrue(any("expected_secondary" in case for case in cases))
        self.assertTrue(
            all("read_load" not in case.get("expected_checks", []) for case in cases),
            "classifier-only router evals must not claim to prove specialist Read calls",
        )
        self.assertTrue(all(str(case["_case_id"]).startswith("contract-") for case in cases))

    def test_load_catalog_cases_combines_sample_and_boundary_catalogs(self) -> None:
        runner = load_runner()

        sample_cases = runner.load_catalog_cases("positive", "all")
        boundary_cases = runner.load_catalog_cases("boundary", "all")
        contract_cases = runner.load_catalog_cases("contract", "all")
        all_cases = runner.load_catalog_cases("all", "all")

        self.assertEqual(
            len(all_cases), len(sample_cases) + len(boundary_cases) + len(contract_cases)
        )

    def test_filter_cases_by_category_selects_out_of_scope_cases(self) -> None:
        runner = load_runner()

        cases = runner.filter_cases_by_category(runner.parse_positive_routings(), "out_of_scope")

        self.assertEqual(len(cases), 4)
        self.assertTrue(all(case["expected_primary"] == "none" for case in cases))

    def test_stratified_category_cases_selects_each_category(self) -> None:
        runner = load_runner()
        cases = [
            {
                "prompt": f"{category} {index}",
                "expected_primary": "documentation-lifecycle",
                "expected_behavior": "route",
                "category": category,
                "expected_checks": ["single_primary", "intent_inference"],
            }
            for category in ["direct", "paraphrase", "mixed_intent", "out_of_scope"]
            for index in range(2)
        ]

        selected = runner.stratified_category_cases(cases, 1, "stable-seed")

        self.assertEqual(len(selected), 4)
        self.assertEqual(
            {case["category"] for case in selected},
            {"direct", "paraphrase", "mixed_intent", "out_of_scope"},
        )

    def test_check_cover_cases_covers_every_requested_check_deterministically(self) -> None:
        runner = load_runner()
        cases = runner.load_catalog_cases("contract", "all")
        required = [
            "capability_translation",
            "ambiguity_check",
            "scope_check",
            "secondary_cap",
        ]

        first = runner.check_cover_cases(cases, required, "release-seed")
        second = runner.check_cover_cases(cases, required, "release-seed")

        covered = {
            check
            for case in first
            for check in case.get("expected_checks", [])
            if check in required
        }
        self.assertEqual(covered, set(required))
        self.assertEqual(
            [case["_case_id"] for case in first],
            [case["_case_id"] for case in second],
        )

    def test_catalog_case_ids_survive_sampling(self) -> None:
        runner = load_runner()
        full = runner.load_catalog_cases("contract", "all")
        sampled = runner.stratified_category_cases(full, 1, "stable-seed")
        full_ids = {case["prompt"]: case["_case_id"] for case in full}

        self.assertTrue(sampled)
        for case in sampled:
            self.assertEqual(runner.case_id(999, case), full_ids[case["prompt"]])

    def test_catalog_case_ids_survive_insertion_and_reordering(self) -> None:
        runner = load_runner()
        first = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        second = {
            "prompt": "Define checkout error budget policy.",
            "expected_primary": "slo-and-error-budgets",
            "expected_behavior": "route to SLO",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        inserted = {
            "prompt": "Design checkout telemetry.",
            "expected_primary": "observability-and-alerting",
            "expected_behavior": "route to observability",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }

        original = runner.assign_catalog_case_ids([first, second], "contract")
        reordered = runner.assign_catalog_case_ids([inserted, second, first], "contract")

        original_ids = {case["prompt"]: case["_case_id"] for case in original}
        reordered_ids = {case["prompt"]: case["_case_id"] for case in reordered}
        self.assertEqual(reordered_ids[first["prompt"]], original_ids[first["prompt"]])
        self.assertEqual(reordered_ids[second["prompt"]], original_ids[second["prompt"]])

    def test_catalog_case_ids_survive_expected_route_corrections(self) -> None:
        runner = load_runner()
        original = {
            "prompt": "Decide the consistency behavior for concurrent writes.",
            "expected_primary": "distributed-data-and-consistency",
            "expected_behavior": "route to distributed data",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        corrected = {
            **original,
            "expected_primary": "state-machine-correctness",
            "expected_behavior": "route to state machine correctness",
            "category": "paraphrase",
        }

        original_id = runner.assign_catalog_case_ids([original], "contract")[0]["_case_id"]
        corrected_id = runner.assign_catalog_case_ids([corrected], "contract")[0]["_case_id"]

        self.assertEqual(corrected_id, original_id)
        self.assertRegex(original_id, r"^contract-[0-9a-f]{16}$")

    def test_catalog_case_id_assignment_rejects_hash_collisions(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }

        with self.assertRaises(SystemExit):
            runner.assign_catalog_case_ids([case, dict(case)], "contract")

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

    def test_command_response_omits_sensitive_stdout_from_adapter_failures(self) -> None:
        runner = load_runner()
        process = Mock()
        sensitive = "Bearer sk-test-adapter-secret-value"
        process.communicate.return_value = (sensitive + "\n", "")
        process.returncode = 1
        with patch.object(
            runner.subprocess,
            "Popen",
            return_value=process,
        ):
            with self.assertRaises(RuntimeError) as raised:
                runner.command_response("adapter", "prompt")

        self.assertNotIn(sensitive, str(raised.exception))
        self.assertIn(str(process.returncode), str(raised.exception))

    def test_command_response_marks_adapter_failures(self) -> None:
        runner = load_runner()
        process = Mock()
        process.communicate.return_value = ("", "transient provider failure\n")
        process.returncode = 1
        with patch.object(
            runner.subprocess,
            "Popen",
            return_value=process,
        ):
            with self.assertRaises(RuntimeError):
                runner.command_response("adapter", "prompt")

    def test_command_response_forwards_case_timeout(self) -> None:
        runner = load_runner()
        process = Mock()
        process.communicate.return_value = ("ok\n", "")
        process.returncode = 0
        with patch.object(
            runner.subprocess,
            "Popen",
            return_value=process,
        ) as popen:
            self.assertEqual(runner.command_response("adapter", "prompt", timeout=17), "ok\n")

        self.assertEqual(process.communicate.call_args.kwargs["timeout"], 17)
        self.assertTrue(popen.call_args.kwargs["start_new_session"])

    def test_command_response_terminates_process_group_on_timeout(self) -> None:
        runner = load_runner()
        process = Mock()
        process.pid = 4123
        process.communicate.side_effect = [
            subprocess.TimeoutExpired("adapter", 1),
            ("", ""),
        ]

        with patch.object(runner.subprocess, "Popen", return_value=process), patch.object(
            runner.os,
            "killpg",
        ) as killpg:
            with self.assertRaises(RuntimeError):
                runner.command_response("adapter", "prompt", timeout=1)

        killpg.assert_called_once_with(process.pid, runner.signal.SIGKILL)

    def test_codex_router_workspace_is_removed_after_timeout(self) -> None:
        runner = load_runner()

        self.assert_adapter_workspace_removed_after_timeout(
            runner,
            adapter=ROOT / "evals" / "adapters" / "codex-router.sh",
            host="codex",
            expected_model="gpt-5.6-terra",
            expected_effort="high",
        )

    def test_claude_router_workspace_is_removed_after_timeout(self) -> None:
        runner = load_runner()

        self.assert_adapter_workspace_removed_after_timeout(
            runner,
            adapter=ROOT / "evals" / "adapters" / "claude-router.sh",
            host="claude",
            expected_model="claude-opus-4-8",
            expected_effort="medium",
        )

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

    def test_main_rejects_nonpositive_limit(self) -> None:
        runner = load_runner()

        for value in ("0", "-1"):
            with self.subTest(value=value), patch.object(
                sys,
                "argv",
                ["run_router_eval.py", "--catalog", "contract", "--limit", value, "--list-cases"],
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
        response = """```routing
{"primary":"observability-and-alerting","secondary":null,"confidence":"high","artifact":"plan","surface":"observability","phase":"design","rationale":"Telemetry construction is the requested artifact."}
```"""

        block = runner.parse_routing_block(response)

        self.assertEqual(block["primary"], "observability-and-alerting")
        self.assertIsNone(block["secondary"])
        self.assertEqual(block["confidence"], "high")

    def test_exact_withhold_passes_only_withheld_cases(self) -> None:
        runner = load_runner()
        cases = [
            {
                "prompt": "Write launch copy.",
                "expected_primary": "none",
                "expected_behavior": "withhold",
                "category": "out_of_scope",
                "expected_checks": ["scope_check"],
                "forbidden_in_response": ["all_specialist_names"],
            },
            {
                "prompt": "Help with engineering.",
                "expected_primary": "staff-engineer-mode",
                "expected_behavior": "withhold",
                "category": "ambiguous",
                "expected_checks": ["ambiguity_check"],
                "forbidden_in_response": ["all_specialist_names"],
            },
        ]

        for case in cases:
            with self.subTest(primary=case["expected_primary"]):
                for response in ("WITHHOLD", "\n  WITHHOLD\r\n"):
                    result = runner.score_case(case, response, ["documentation-lifecycle"])
                    self.assertTrue(result.passed, result.failures)

    def test_withheld_cases_reject_every_noncanonical_wire_form(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Write launch copy.",
            "expected_primary": "none",
            "expected_behavior": "withhold",
            "category": "out_of_scope",
            "expected_checks": ["scope_check"],
            "forbidden_in_response": ["all_specialist_names"],
        }
        valid_block = (
            "```routing\n"
            '{"primary":"documentation-lifecycle","secondary":null,'
            '"confidence":"high","artifact":"audit","surface":"documentation",'
            '"phase":"maintenance","rationale":"operational truth"}\n'
            "```"
        )
        invalid_responses = [
            "",
            "No route applies.",
            "WITHHOLD\nNo route applies.",
            "prefix WITHHOLD",
            f"WITHHOLD\n{valid_block}",
            "```routing\n{not json}\n```",
            f"{valid_block}\n{valid_block}",
        ]

        for response in invalid_responses:
            with self.subTest(response=response):
                result = runner.score_case(case, response, ["documentation-lifecycle"])
                self.assertFalse(result.passed, result.failures)

    def test_withhold_fails_a_routed_case(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }

        result = runner.score_case(case, "WITHHOLD", ["high-availability-design"])

        self.assertFalse(result.passed)
        self.assertTrue(result.failures)
        self.assertEqual(result.structured_output, {"kind": "withhold"})

    def test_parse_routing_block_rejects_arbitrary_non_wire_text(self) -> None:
        runner = load_runner()

        with self.assertRaises(ValueError):
            runner.parse_routing_block("No route applies.")

    def test_score_routed_case_rejects_surrounding_prose(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        response = """Reasoning summary.
```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"survivability"}
```"""

        result = runner.score_case(case, response, ["high-availability-design"])

        self.assertFalse(result.passed)
        self.assertTrue(result.failures)
        self.assertIsNone(result.structured_output)

    def test_score_routed_case_rejects_multiple_routing_blocks(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        block = """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"survivability"}
```"""

        result = runner.score_case(case, f"{block}\n{block}", ["high-availability-design"])

        self.assertFalse(result.passed)
        self.assertTrue(result.failures)
        self.assertIsNone(result.structured_output)

    def test_score_routed_case_rejects_invalid_schema(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        invalid_payloads = [
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"ok","extra":true}',
            '{"primary":"high-availability-design","secondary":["one","two"],"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"ok"}',
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"banana","rationale":"ok"}',
            '{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"","surface":"availability","phase":"design","rationale":"ok"}',
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                result = runner.score_case(
                    case,
                    f"```routing\n{payload}\n```",
                    ["high-availability-design"],
                )
                self.assertFalse(result.passed, result.failures)

    def test_score_routed_case_requires_expected_phase_match(self) -> None:
        runner = load_runner()
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "expected_phase": "testing",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        response = """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"survivability"}
```"""

        result = runner.score_case(case, response, ["high-availability-design"])

        self.assertFalse(result.passed)
        self.assertTrue(result.failures)
        self.assertEqual(result.structured_output["phase"], "design")
        self.assertNotEqual(result.structured_output["phase"], case["expected_phase"])

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
        self.assertEqual(len(result.failures), 1)

    def test_summarize_counts_failure_types(self) -> None:
        runner = load_runner()
        routed_case = {
            "prompt": "Design a data contract.",
            "expected_primary": "data-contracts",
            "expected_behavior": "route",
            "category": "near_miss",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        withheld_case = {
            "prompt": "Write launch copy.",
            "expected_primary": "none",
            "expected_behavior": "withhold",
            "category": "negative",
            "expected_checks": ["scope_check"],
            "forbidden_in_response": ["all_specialist_names"],
        }
        over_route_response = """```routing
{"primary":"api-design-and-compatibility","secondary":null,"confidence":"high","artifact":"copy","surface":"marketing","phase":"design","rationale":"launch copy"}
```"""
        results = [
            runner.score_case(
                routed_case,
                "not a routing response",
                ["data-contracts", "api-design-and-compatibility"],
            ),
            runner.score_case(
                withheld_case,
                over_route_response,
                ["data-contracts", "api-design-and-compatibility"],
            ),
        ]

        self.assertTrue(all(not result.passed for result in results))

        summary = runner.summarize(results)

        self.assertEqual(summary["failure_types"], {"model_format": 1, "over_route": 1})
        self.assertEqual(summary["failures"][0]["failure_types"], ["model_format"])
        self.assertEqual(summary["failures"][1]["failure_types"], ["over_route"])

    def test_summarize_counts_command_errors(self) -> None:
        runner = load_runner()
        process = Mock()
        process.communicate.return_value = ("", "provider-failure-sentinel")
        process.returncode = 1
        with patch.object(runner.subprocess, "Popen", return_value=process):
            with self.assertRaises(RuntimeError) as raised:
                runner.command_response("adapter", "prompt")
        results = [
            runner.CaseResult(
                case_id="673-observability-and-alerting",
                category="near_miss",
                expected_primary="observability-and-alerting",
                actual_primary=None,
                passed=False,
                failures=[str(raised.exception)],
            )
        ]

        summary = runner.summarize(results)

        self.assertEqual(summary["failure_types"], {"command_error": 1})
        self.assertEqual(summary["failures"][0]["failure_types"], ["command_error"])

    def test_progress_writer_appends_case_records_and_summary(self) -> None:
        runner = load_runner()
        cases = [
            {
                "prompt": "Design a highly available service.",
                "expected_primary": "high-availability-design",
                "expected_behavior": "route",
                "category": "positive_routing",
                "expected_checks": ["single_primary", "intent_inference"],
            },
            {
                "prompt": "Define an error budget.",
                "expected_primary": "slo-and-error-budgets",
                "expected_behavior": "route",
                "category": "positive_routing",
                "expected_checks": ["single_primary", "intent_inference"],
            },
        ]
        responses = [
            """```routing
{"primary":"high-availability-design","secondary":null,"confidence":"high","artifact":"design","surface":"availability","phase":"design","rationale":"survivability"}
```""",
            """```routing
{"primary":"observability-and-alerting","secondary":null,"confidence":"high","artifact":"policy","surface":"reliability","phase":"design","rationale":"error budget"}
```""",
        ]
        names = [
            "high-availability-design",
            "slo-and-error-budgets",
            "observability-and-alerting",
        ]
        results = [
            runner.score_case(case, response, names, index=index)
            for index, (case, response) in enumerate(zip(cases, responses), 1)
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress" / "router-eval.jsonl"
            writer = runner.JsonlProgressWriter(path, total=2)

            writer.write_case(results[0])
            first_snapshot = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            writer.write_case(results[1])
            writer.write_summary(runner.summarize(results))
            writer.close()
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(len(first_snapshot), 1)
        self.assertEqual(first_snapshot[0]["type"], "case")
        self.assertEqual(first_snapshot[0]["completed"], 1)
        self.assertEqual(first_snapshot[0]["total"], 2)
        self.assertEqual(records[1]["failure_types"], ["route_mismatch"])
        self.assertEqual(len(records[0]["response_sha256"]), 64)
        self.assertEqual(records[0]["structured_output"]["primary"], "high-availability-design")
        self.assertEqual(records[0]["response"], results[0].response)
        self.assertEqual(records[2]["type"], "summary")
        self.assertEqual(records[2]["summary"]["passed"], 1)
        self.assertEqual(records[2]["summary"]["total"], 2)

    def test_progress_writer_records_manifest_before_case_results(self) -> None:
        runner = load_runner()
        result = runner.CaseResult(
            case_id="contract-0001-documentation-lifecycle",
            category="direct",
            expected_primary="documentation-lifecycle",
            actual_primary="documentation-lifecycle",
            passed=True,
            failures=[],
        )
        manifest = {"type": "manifest", "catalog": "contract", "selected_case_ids": [result.case_id]}

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "router.jsonl"
            writer = runner.JsonlProgressWriter(path, total=1, manifest=manifest)
            writer.write_case(result)
            writer.close()
            records = [json.loads(line) for line in path.read_text().splitlines()]

        self.assertEqual(records[0], manifest)
        self.assertEqual(records[1]["case_id"], result.case_id)

    def test_progress_writer_refuses_existing_file_and_final_symlink(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            existing = directory / "existing.jsonl"
            existing.write_text("original", encoding="utf-8")
            with self.assertRaises(SystemExit):
                runner.JsonlProgressWriter(existing, total=1)
            self.assertEqual(existing.read_text(encoding="utf-8"), "original")

            target = directory / "target.jsonl"
            target.write_text("target", encoding="utf-8")
            link = directory / "link.jsonl"
            link.symlink_to(target)
            with self.assertRaises(SystemExit):
                runner.JsonlProgressWriter(link, total=1)
            self.assertEqual(target.read_text(encoding="utf-8"), "target")

    def test_evidence_writers_refuse_symlinked_directory_ancestors(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            ancestor = root / "linked-parent"
            ancestor.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(SystemExit):
                runner.JsonlProgressWriter(ancestor / "results.jsonl", total=1)
            with self.assertRaises(SystemExit):
                runner.RouterRunWriter(
                    ancestor / "run",
                    total=1,
                    manifest={"type": "manifest"},
                )

            self.assertEqual(list(outside.iterdir()), [])

    def test_progress_writer_never_reopens_replaced_path(self) -> None:
        runner = load_runner()
        result = runner.CaseResult(
            case_id="contract-0001-documentation-lifecycle",
            category="direct",
            expected_primary="documentation-lifecycle",
            actual_primary="documentation-lifecycle",
            passed=True,
            failures=[],
        )

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / "router.jsonl"
            target = directory / "target.jsonl"
            target.write_text("target", encoding="utf-8")
            writer = runner.JsonlProgressWriter(path, total=1)
            path.unlink()
            path.symlink_to(target)

            writer.write_case(result)
            writer.close()

            self.assertEqual(target.read_text(encoding="utf-8"), "target")

    def test_main_refuses_results_collision_before_adapter_invocation(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "router.jsonl"
            path.write_text("original", encoding="utf-8")
            with patch.object(
                sys,
                "argv",
                [
                    "run_router_eval.py",
                    "--catalog",
                    "contract",
                    "--limit",
                    "1",
                    "--command",
                    "adapter",
                    "--results-jsonl",
                    str(path),
                ],
            ), patch.object(runner, "command_response") as command_response:
                with self.assertRaises(SystemExit):
                    runner.main()

            command_response.assert_not_called()
            self.assertEqual(path.read_text(encoding="utf-8"), "original")

    def test_run_directory_reserves_all_evidence_before_adapter_invocation(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "router-run"
            run_dir.mkdir()
            with patch.object(
                sys,
                "argv",
                [
                    "run_router_eval.py",
                    "--catalog",
                    "contract",
                    "--limit",
                    "1",
                    "--command",
                    "adapter",
                    "--results-dir",
                    str(run_dir),
                ],
            ), patch.object(runner, "command_response") as command_response:
                with self.assertRaises(SystemExit):
                    runner.main()

            command_response.assert_not_called()

    def test_run_directory_persists_rescorable_response_and_structured_record(self) -> None:
        runner = load_runner()
        response = (
            "\n```routing\n"
            '{"primary":"high-availability-design","secondary":null,'
            '"confidence":"high","artifact":"design","surface":"availability",'
            '"phase":"design","rationale":"survivability"}\n'
            "```\n"
        )
        result = runner.score_case(
            {
                "_case_id": "contract-aabbccddeeff0011",
                "prompt": "Design a highly available service.",
                "expected_primary": "high-availability-design",
                "expected_behavior": "route",
                "category": "direct",
                "expected_checks": ["single_primary", "intent_inference"],
            },
            response,
            ["high-availability-design"],
        )
        manifest = {"type": "manifest", "schema_version": 2}

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            writer = runner.RouterRunWriter(run_dir, total=1, manifest=manifest)
            writer.write_case(result)
            writer.write_summary(runner.summarize([result]))
            writer.close()

            self.assertEqual(
                (run_dir / "responses" / f"{result.case_id}.txt").read_text(),
                response,
            )
            records = [
                json.loads(line)
                for line in (run_dir / "results.jsonl").read_text().splitlines()
            ]

        self.assertEqual(records[0], manifest)
        self.assertEqual(records[1]["structured_output"]["primary"], "high-availability-design")
        self.assertEqual(records[1]["response_sha256"], runner.sha256_bytes(response.encode()))
        self.assertNotIn("response", records[1], "raw response belongs in the exclusive response file")

    def test_saved_mode_main_records_source_hashes_and_full_run_controls(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(
            runner.load_catalog_cases("positive", "all"), "out_of_scope"
        )[:1]
        result_id = runner.case_id(1, cases[0])
        response = "\nWITHHOLD\r\n"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            responses_dir = root / "saved"
            responses_dir.mkdir()
            (responses_dir / f"{result_id}.txt").write_text(response)
            results_dir = root / "rescored"
            with patch.object(
                sys,
                "argv",
                [
                    "run_router_eval.py",
                    "--catalog",
                    "sample",
                    "--sample",
                    "all",
                    "--category",
                    "out_of_scope",
                    "--limit",
                    "1",
                    "--responses-dir",
                    str(responses_dir),
                    "--results-dir",
                    str(results_dir),
                    "--json",
                ],
            ):
                self.assertEqual(runner.main(), 0)
            records = [
                json.loads(line)
                for line in (results_dir / "results.jsonl").read_text().splitlines()
            ]

        manifest = records[0]
        self.assertEqual(manifest["execution_mode"], "saved")
        self.assertEqual(manifest["catalog"], "positive")
        self.assertEqual(manifest["run_controls"]["requested_catalog"], "sample")
        self.assertEqual(manifest["run_controls"]["category"], "out_of_scope")
        self.assertEqual(manifest["run_controls"]["limit"], 1)
        self.assertEqual(
            manifest["saved_response_sha256"][result_id],
            runner.sha256_bytes(response.encode()),
        )
        self.assertEqual(
            records[1]["response_sha256"],
            manifest["saved_response_sha256"][result_id],
        )
        self.assertEqual(records[1]["structured_output"], {"kind": "withhold"})

    def test_saved_response_scoring_uses_preflight_snapshot_after_file_replacement(self) -> None:
        runner = load_runner()
        cases = runner.filter_cases_by_category(
            runner.load_catalog_cases("positive", "all"), "out_of_scope"
        )[:1]
        result_id = runner.case_id(1, cases[0])
        original = "WITHHOLD\n"

        with tempfile.TemporaryDirectory() as tmp:
            responses_dir = Path(tmp)
            path = responses_dir / f"{result_id}.txt"
            path.write_text(original)
            captured = runner.preflight_saved_responses(responses_dir, cases)
            replacement = responses_dir / "replacement.txt"
            replacement.write_text("not the preflighted response")
            replacement.replace(path)

            results = runner.score_cases(
                cases,
                runner.specialist_names(),
                saved_responses=captured,
            )

        self.assertTrue(results[0].passed, results[0].failures)
        self.assertEqual(results[0].response, original)
        self.assertEqual(
            runner.sha256_bytes(results[0].response.encode()),
            captured[result_id].sha256,
        )

    def test_custom_eval_file_rejects_invalid_contract_with_clean_error(self) -> None:
        runner = load_runner()
        invalid = """cases:
  - prompt: ""
    expected_primary: invented-specialist
    expected_behavior: ""
    category: direct
    expected_phase: invented-phase
    expected_checks: [invented-check]
"""

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.md"
            path.write_text(invalid)
            with patch.object(
                sys,
                "argv",
                ["run_router_eval.py", "--eval-file", str(path), "--list-cases"],
            ), self.assertRaises(SystemExit) as raised, patch(
                "sys.stderr", new_callable=io.StringIO
            ) as stderr:
                runner.main()

        self.assertNotEqual(raised.exception.code, 0)
        self.assertTrue(stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_custom_eval_contract_rejects_bad_route_phase_check_and_types(self) -> None:
        runner = load_runner()
        base = {
            "prompt": "Design availability.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }
        invalid = [
            {**base, "expected_primary": "invented-specialist"},
            {**base, "expected_phase": "invented-phase"},
            {**base, "expected_checks": ["invented-check"]},
            {**base, "expected_checks": "single_primary"},
            {**base, "unexpected_field": "value"},
        ]

        for case in invalid:
            with self.subTest(case=case), self.assertRaises(SystemExit), patch(
                "sys.stderr", new_callable=io.StringIO
            ):
                runner.validate_custom_eval_cases([case], Path("custom.md"))

    def test_custom_eval_file_rejects_builtin_sample_flag(self) -> None:
        runner = load_runner()
        fixture = """cases:
  - prompt: "Design availability."
    expected_primary: high-availability-design
    expected_behavior: "route"
    category: direct
    expected_checks: [single_primary, intent_inference]
"""

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "custom.md"
            path.write_text(fixture)
            with patch.object(
                sys,
                "argv",
                [
                    "run_router_eval.py",
                    "--eval-file",
                    str(path),
                    "--sample",
                    "all",
                    "--list-cases",
                ],
            ), self.assertRaises(SystemExit), patch(
                "sys.stderr", new_callable=io.StringIO
            ):
                runner.main()

    def test_custom_eval_file_reports_malformed_check_syntax_without_traceback(self) -> None:
        runner = load_runner()
        malformed_values = (
            "single_primary",
            "[single_primary",
        )

        for value in malformed_values:
            fixture = f"""cases:
  - prompt: "Design availability."
    expected_primary: high-availability-design
    expected_behavior: "route"
    category: direct
    expected_checks: {value}
"""
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "malformed.md"
                path.write_text(fixture)
                stderr = io.StringIO()
                with patch.object(
                    sys,
                    "argv",
                    ["run_router_eval.py", "--eval-file", str(path), "--list-cases"],
                ), patch("sys.stderr", stderr), self.assertRaises(SystemExit):
                    runner.main()

                self.assertTrue(stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())

    def test_custom_eval_file_reports_invalid_utf8_without_traceback(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid-utf8.md"
            path.write_bytes(b"cases:\n\xff")
            stderr = io.StringIO()
            with patch.object(
                sys,
                "argv",
                ["run_router_eval.py", "--eval-file", str(path), "--list-cases"],
            ), patch("sys.stderr", stderr), self.assertRaises(SystemExit):
                runner.main()

        self.assertTrue(stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_custom_eval_file_uses_full_catalog_without_implicit_sample(self) -> None:
        runner = load_runner()
        fixture = """cases:
  - prompt: "First availability prompt."
    expected_primary: high-availability-design
    expected_behavior: "route"
    category: direct
    expected_checks: [single_primary, intent_inference]
  - prompt: "Second availability prompt."
    expected_primary: high-availability-design
    expected_behavior: "route"
    category: direct
    expected_checks: [single_primary, intent_inference]
"""

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "custom.md"
            path.write_text(fixture)
            with patch.object(
                sys,
                "argv",
                ["run_router_eval.py", "--eval-file", str(path), "--list-cases"],
            ), patch("sys.stdout", new_callable=io.StringIO) as stdout:
                self.assertEqual(runner.main(), 0)

        lines = stdout.getvalue().splitlines()
        self.assertEqual(len(lines), len(runner.parse_cases(fixture)))

    def test_custom_eval_manifest_labels_selection_without_builtin_sample(self) -> None:
        runner = load_runner()
        fixture = """cases:
  - prompt: "Write launch copy."
    expected_primary: none
    expected_behavior: "withhold routing"
    category: out_of_scope
    expected_checks: [scope_check]
    forbidden_in_response: [all_specialist_names]
"""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            eval_path = root / "custom.md"
            eval_path.write_text(fixture)
            cases = runner.assign_catalog_case_ids(
                runner.parse_cases(fixture), "file-custom"
            )
            responses_dir = root / "responses"
            responses_dir.mkdir()
            (responses_dir / f"{runner.case_id(1, cases[0])}.txt").write_text("WITHHOLD")
            results_dir = root / "results"
            with patch.object(
                sys,
                "argv",
                [
                    "run_router_eval.py",
                    "--eval-file",
                    str(eval_path),
                    "--responses-dir",
                    str(responses_dir),
                    "--results-dir",
                    str(results_dir),
                    "--json",
                ],
            ), patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(runner.main(), 0)
            manifest = json.loads(
                (results_dir / "results.jsonl").read_text().splitlines()[0]
            )

        self.assertEqual(manifest["run_controls"]["selection_mode"], "custom_catalog")
        self.assertIsNone(manifest["run_controls"]["sample"])

    def test_build_run_manifest_records_reproducible_safe_lineage(self) -> None:
        runner = load_runner()
        cases = runner.load_catalog_cases("contract", "all")[:2]

        with patch.dict(
            runner.os.environ,
            {
                "CODEX_MODEL": "gpt-5.5",
                "CODEX_EFFORT": "high",
                "AUTH_TOKEN": "do-not-record",
            },
            clear=False,
        ), patch.object(
            runner,
            "query_host_cli_version",
            return_value=("codex", "codex-cli 1.2.3"),
            create=True,
        ):
            manifest = runner.build_run_manifest(
                cases=cases,
                catalog="contract",
                seed="release-seed",
                command="evals/adapters/codex-router.sh",
                catalog_paths=[runner.ROUTER_CONTRACT_PROMPTS],
                execution_mode="live",
                selection_mode="check_cover",
                jobs=4,
                case_timeout=37,
                run_controls={
                    "selection_mode": "check_cover",
                    "catalog": "contract",
                    "sample": "all",
                    "category": None,
                    "requested_case_ids": [],
                    "limit": None,
                    "random": None,
                    "random_specialists": None,
                    "stratified_categories": None,
                    "check_cover": ["scope_check"],
                    "seed": "release-seed",
                    "jobs": 4,
                    "case_timeout": 37,
                    "warn_only": False,
                },
            )

        self.assertEqual(manifest["type"], "manifest")
        self.assertEqual(manifest["selected_case_ids"], [case["_case_id"] for case in cases])
        self.assertEqual(manifest["model"], "gpt-5.5")
        self.assertEqual(manifest["effort"], "high")
        self.assertEqual(manifest["execution_mode"], "live")
        self.assertEqual(manifest["host_cli"], "codex")
        self.assertEqual(manifest["host_cli_version"], "codex-cli 1.2.3")
        self.assertEqual(manifest["run_controls"]["catalog"], "contract")
        self.assertEqual(manifest["run_controls"]["check_cover"], ["scope_check"])
        self.assertEqual(manifest["run_controls"]["case_timeout"], 37)
        self.assertEqual(len(manifest["catalog_sha256"]), 64)
        expected_catalog_inputs = {
            str(runner.ROUTER_CONTRACT_PROMPTS.relative_to(runner.ROOT)):
                runner.sha256_bytes(runner.ROUTER_CONTRACT_PROMPTS.read_bytes())
        }
        self.assertEqual(
            manifest["catalog_inputs_sha256"],
            expected_catalog_inputs,
        )
        self.assertEqual(len(manifest["harness_sha256"]), 64)
        self.assertEqual(len(manifest["prompt_set_sha256"]), 64)
        self.assertEqual(len(manifest["prompt_sha256"]), len(cases))
        self.assertIn("sha", manifest["git"])
        self.assertIn("dirty", manifest["git"])
        self.assertEqual(
            manifest["context_sha256"],
            {
                str(path.relative_to(runner.ROOT)): runner.sha256_bytes(path.read_bytes())
                for path in runner.ROUTER_CONTEXT_PATHS
            },
        )
        self.assertIsInstance(manifest["split_access_context"], str)
        self.assertTrue(manifest["split_access_context"])
        self.assertNotIn("do-not-record", json.dumps(manifest))
        self.assertEqual(
            manifest.get("adapter_protocol", {}).get("path"),
            "scripts/eval_adapter_protocol.py",
        )

    def test_known_router_adapters_record_defaults_without_provider_environment(self) -> None:
        runner = load_runner()
        cases = runner.load_catalog_cases("contract", "all")[:1]
        path = runner.ROUTER_CONTRACT_PROMPTS

        with patch.dict(
            runner.os.environ,
            {"PATH": runner.os.environ.get("PATH", "")},
            clear=True,
        ), patch.object(
            runner,
            "query_host_cli_version",
            return_value=(None, None),
        ), patch.object(runner, "git_state", return_value={"sha": None, "dirty": None}):
            manifests = {
                adapter: runner.build_run_manifest(
                    cases=cases,
                    catalog="contract",
                    seed="default-model-test",
                    command=adapter,
                    catalog_paths=[path],
                )
                for adapter in (
                    "evals/adapters/codex-router.sh",
                    "evals/adapters/claude-router.sh",
                )
            }

        self.assertEqual(
            (manifests["evals/adapters/codex-router.sh"]["model"],
             manifests["evals/adapters/codex-router.sh"]["effort"]),
            ("gpt-5.6-terra", "high"),
        )
        self.assertEqual(
            (manifests["evals/adapters/claude-router.sh"]["model"],
             manifests["evals/adapters/claude-router.sh"]["effort"]),
            ("claude-opus-4-8", "medium"),
        )
        for manifest in manifests.values():
            self.assertEqual(
                manifest.get("adapter_protocol", {}).get("path"),
                "scripts/eval_adapter_protocol.py",
            )
            protocol_path = ROOT / manifest["adapter_protocol"]["path"]
            self.assertEqual(
                manifest["adapter_protocol"]["sha256"],
                runner.sha256_bytes(protocol_path.read_bytes()),
            )

    def test_adversarial_manifest_records_versioned_split_access_provenance(self) -> None:
        runner = load_runner()
        cases = runner.load_catalog_cases("adversarial-split", "all")[:2]
        draft = json.loads(runner.ADVERSARIAL_SPLIT_DRAFT.read_text())
        review = json.loads(runner.ADVERSARIAL_SPLIT_REVIEW.read_text())

        with patch.object(
            runner,
            "query_host_cli_version",
            return_value=("codex", "codex-cli 1.2.3"),
        ):
            manifest = runner.build_run_manifest(
                cases=cases,
                catalog="adversarial-split",
                seed="split-seed",
                command="evals/adapters/codex-router.sh",
                catalog_paths=list(runner.ADVERSARIAL_SPLIT_PROVENANCE_PATHS),
            )

        provenance = manifest["adversarial_provenance"]
        reviewed_cases = review["cases"]
        accepted = sum(case["disposition"] == "accepted" for case in reviewed_cases)
        rejected = sum(case["disposition"] == "rejected" for case in reviewed_cases)
        self.assertEqual(draft["batch_id"], review["batch_id"])
        self.assertEqual(provenance["batch_id"], draft["batch_id"])
        self.assertEqual(provenance["draft_schema_version"], draft["schema_version"])
        self.assertEqual(provenance["review_schema_version"], review["schema_version"])
        self.assertEqual(provenance["review_version"], review["review_version"])
        self.assertEqual(provenance["author_access"], draft["author_access"])
        self.assertEqual(provenance["reviewer_access"], review["reviewer_access"])
        self.assertEqual(
            provenance["summary"],
            {
                "reviewed": len(reviewed_cases),
                "accepted": accepted,
                "rejected": rejected,
            },
        )
        self.assertEqual(
            set(manifest["catalog_inputs_sha256"]),
            {
                str(path.relative_to(runner.ROOT))
                for path in runner.ADVERSARIAL_SPLIT_PROVENANCE_PATHS
            },
        )

    def test_saved_response_manifest_ignores_ambient_model_environment(self) -> None:
        runner = load_runner()
        cases = runner.load_catalog_cases("contract", "all")[:1]

        with patch.dict(
            runner.os.environ,
            {"CODEX_MODEL": "ambient-model", "CODEX_EFFORT": "ambient-effort"},
            clear=False,
        ):
            with tempfile.TemporaryDirectory() as tmp:
                responses_dir = Path(tmp)
                response_hashes = {}
                for index, case in enumerate(cases, 1):
                    response = "WITHHOLD\n"
                    result_id = runner.case_id(index, case)
                    (responses_dir / f"{result_id}.txt").write_text(response)
                    response_hashes[result_id] = runner.sha256_bytes(response.encode())
                manifest = runner.build_run_manifest(
                    cases=cases,
                    catalog="contract",
                    seed="saved-run",
                    command=None,
                    catalog_paths=[runner.ROUTER_CONTRACT_PROMPTS],
                    execution_mode="saved",
                    selection_mode="case_ids",
                    jobs=2,
                    case_timeout=None,
                    saved_response_sha256=response_hashes,
                )

        self.assertEqual(manifest["execution_mode"], "saved")
        self.assertIsNone(manifest["model"])
        self.assertIsNone(manifest["effort"])
        self.assertIsNone(manifest["host_cli"])
        self.assertIsNone(manifest["host_cli_version"])
        self.assertEqual(manifest["command"], {"kind": "saved-responses"})
        self.assertEqual(manifest["saved_response_sha256"], response_hashes)
        self.assertIsInstance(manifest["split_access_context"], str)
        self.assertTrue(manifest["split_access_context"])

    def test_legacy_sample_catalog_is_canonicalized_to_positive(self) -> None:
        runner = load_runner()

        self.assertEqual(runner.canonical_catalog_name("sample"), "positive")
        sample = runner.load_catalog_cases("sample", "all")
        positive = runner.load_catalog_cases("positive", "all")
        self.assertEqual(
            [case["_case_id"] for case in sample],
            [case["_case_id"] for case in positive],
        )

    def test_command_identity_hashes_arguments_without_recording_secret_values(self) -> None:
        runner = load_runner()

        identity = runner.command_identity(
            "AUTH_TOKEN=do-not-record evals/adapters/codex-router.sh --token do-not-record"
        )

        serialized = json.dumps(identity)
        self.assertNotIn("do-not-record", serialized)
        self.assertEqual(identity["adapter"], "evals/adapters/codex-router.sh")


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
```"""
        result = runner.score_case(case, response, ["high-availability-design"])
        self.assertTrue(result.passed, result.failures)


if __name__ == "__main__":
    unittest.main()
