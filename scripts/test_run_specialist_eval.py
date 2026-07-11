#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_specialist_eval.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_specialist_eval", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load run_specialist_eval.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpecialistEvalTests(unittest.TestCase):
    def test_codex_specialist_workspace_is_removed_after_timeout(self) -> None:
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            source_home = temp / "source-home"
            source_home.mkdir()
            (source_home / "auth.json").write_text(
                '{"fixture":"credential"}\n', encoding="utf-8"
            )
            observation = temp / "adapter-observation.txt"
            caller_workspace = temp / "caller-workspace"
            caller_workspace.mkdir()
            fake_codex = fake_bin / "codex"
            fake_codex.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        'test -f "${CODEX_HOME}/auth.json"',
                        (
                            "printf '%s\\n%s\\n%s\\n%s\\n%s\\n' "
                            '"${SEM_EVAL_ADAPTER_WORKSPACE}" "${CODEX_HOME}" '
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
            fake_codex.chmod(0o755)
            environment = {
                "CODEX_HOME": str(source_home),
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
                        runner.command_response(
                            str(ROOT / "evals" / "adapters" / "codex-specialist.sh"),
                            "prompt",
                            0.5,
                        )

                lines = observation.read_text(encoding="utf-8").splitlines()
                workspace = Path(lines[0])
                isolated_root = Path(lines[1]).parent
                self.assertEqual(workspace, isolated_root)
                self.assertNotEqual(workspace, caller_workspace)
                self.assertEqual(lines[2:4], ["gpt-5.6-terra", "high"])
                self.assertEqual(lines[4], "700")
                self.assertFalse(workspace.exists())
                self.assertTrue(caller_workspace.exists())
            finally:
                if isolated_root is not None and isolated_root != caller_workspace:
                    shutil.rmtree(isolated_root, ignore_errors=True)

    def test_canonical_catalog_loads(self) -> None:
        runner = load_runner()

        cases = runner.load_cases()

        self.assertTrue(cases)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertTrue(
            all(
                {"id", "specialist", "prompt", "required", "forbidden"}
                <= set(case)
                for case in cases
            )
        )

    def test_score_response_accepts_alternative_required_terms(self) -> None:
        runner = load_runner()
        case = {
            "id": "database-sequence",
            "required": ["dual-write|change capture", "reconciliation"],
            "forbidden": ["every pre-contract phase is rollback-safe"],
        }

        failures = runner.score_response(
            case,
            "Start change capture before the backfill, then run reconciliation before cutover.",
        )

        self.assertEqual(failures, [])

    def test_score_response_reports_missing_and_forbidden_terms(self) -> None:
        runner = load_runner()
        case = {
            "id": "database-sequence",
            "required": ["dual-write|change capture", "reconciliation"],
            "forbidden": ["every pre-contract phase is rollback-safe"],
        }

        failures = runner.score_response(
            case,
            "Every pre-contract phase is rollback-safe, so begin the backfill.",
        )

        self.assertEqual(
            len(failures),
            len(case["required"]) + len(case["forbidden"]),
        )

    def test_score_response_rejects_each_forbidden_alternative(self) -> None:
        runner = load_runner()
        case = {
            "id": "forbidden-alternatives",
            "required": ["bounded rollout"],
            "forbidden": ["final disposal|destructive teardown"],
        }

        for claim in ("final disposal", "destructive teardown"):
            with self.subTest(claim=claim):
                failures = runner.score_response(
                    case,
                    f"Use a bounded rollout, then migration performs {claim}.",
                )
                self.assertEqual(len(failures), 1)

    def test_score_response_uses_term_boundaries_and_rejects_negated_evidence(self) -> None:
        runner = load_runner()
        case = {
            "id": "boundary-and-negation",
            "required": ["sign", "reconcile|reconciliation"],
            "forbidden": ["release every name"],
        }

        failures = runner.score_response(
            case,
            (
                "Assign an owner, but do not sign the artifact. "
                "There is no reconciliation step. "
                "Never release every name."
            ),
        )

        self.assertEqual(len(failures), len(case["required"]))

        positive_forbidden = runner.score_response(
            case,
            "Assign an owner without signing or reconciliation. Release every name.",
        )
        self.assertGreater(len(positive_forbidden), len(failures))

    def test_score_response_scopes_negation_to_one_table_cell(self) -> None:
        runner = load_runner()
        case = {"id": "table-cell-negation", "required": ["oom"], "forbidden": []}

        failures = runner.score_response(
            case,
            "| Expected behavior | no request loss | Signal | OOM and eviction events |",
        )

        self.assertEqual(failures, [])

    def test_score_response_scopes_negation_in_delimiter_row_tables(self) -> None:
        runner = load_runner()
        case = {"id": "table-cell-negation", "required": ["oom"], "forbidden": []}

        failures = runner.score_response(
            case,
            (
                "Expected behavior | Signal\n"
                "--- | ---\n"
                "no request loss | OOM and eviction events"
            ),
        )

        self.assertEqual(failures, [])

    def test_score_response_resumes_table_detection_after_list_fence(self) -> None:
        runner = load_runner()
        case = {
            "id": "table-after-list-fence",
            "required": ["eviction"],
            "forbidden": [],
        }

        failures = runner.score_response(
            case,
            (
                "  - ```text\n"
                "    code\n"
                "    ```\n"
                "| Guidance | Do not accept OOM | Signal | eviction |"
            ),
        )

        self.assertEqual(failures, [])

    def test_score_response_does_not_scope_negation_at_non_table_pipes(self) -> None:
        runner = load_runner()
        case = {
            "id": "non-table-pipe-negation",
            "required": ["eviction"],
            "forbidden": [],
        }
        responses = {
            "escaped pipe": "Do not accept OOM \\| eviction as safe.",
            "inline code": "Do not accept `OOM | eviction` as safe.",
            "escaped pipe in table cell": (
                "| Guidance | Do not accept OOM \\| eviction as safe. |"
            ),
            "inline code in table cell": (
                "| Guidance | Do not accept `OOM | eviction` as safe. |"
            ),
            "fenced code": (
                "```text\n"
                "| Do not accept OOM | eviction as safe. |\n"
                "```"
            ),
            "indented code": "    | Do not accept OOM | eviction as safe. |",
            "multiline code span": (
                "`prefix\n"
                "| Do not accept OOM | eviction as safe. |\n"
                "suffix`"
            ),
            "list-contained fence": (
                "- ```text\n"
                "  | Do not accept OOM | eviction as safe. |\n"
                "  ```"
            ),
            "ordinary prose": "Do not accept OOM | eviction as safe.",
        }

        for label, response in responses.items():
            with self.subTest(label=label):
                self.assertEqual(
                    runner.score_response(case, response),
                    ["missing required concept: eviction"],
                )

    def test_score_response_accepts_inflected_positive_terms(self) -> None:
        runner = load_runner()
        case = {
            "id": "inflected-terms",
            "required": ["fenc*", "reauthoriz*"],
            "forbidden": [],
        }

        failures = runner.score_response(
            case,
            "Fence stale writers with fencing tokens and reauthorize every cache hit.",
        )

        self.assertEqual(failures, [])

    def test_score_response_matches_multiword_concepts_in_identifiers(self) -> None:
        runner = load_runner()
        case = {
            "id": "identifier-separator",
            "required": ["data classification", "entitlement"],
            "forbidden": [],
        }

        failures = runner.score_response(
            case,
            "Include data_classification and entitlement_version in the cache partition key.",
        )

        self.assertEqual(failures, [])

    def test_score_response_does_not_treat_signal_as_sign(self) -> None:
        runner = load_runner()
        case = {"id": "token-boundary", "required": ["sign"], "forbidden": []}

        signal_failures = runner.score_response(
            case,
            "Record a latency signal and assign an owner.",
        )
        signed_failures = runner.score_response(case, "Use a signed artifact.")

        self.assertEqual(len(signal_failures), len(case["required"]))
        self.assertEqual(signed_failures, [])

    def test_load_cases_rejects_unsafe_ids_slugs_and_field_types(self) -> None:
        runner = load_runner()
        invalid_cases = [
            {
                "id": "../../escape",
                "specialist": "database-operations",
                "prompt": "prompt",
                "required": ["backfill"],
                "forbidden": [],
            },
            {
                "id": "safe-id",
                "specialist": "../README",
                "prompt": "prompt",
                "required": ["backfill"],
                "forbidden": [],
            },
            {
                "id": "safe-id",
                "specialist": "database-operations",
                "prompt": 7,
                "required": ["backfill"],
                "forbidden": [],
            },
        ]

        for case in invalid_cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "catalog.json"
                path.write_text(json.dumps([case]))
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    runner.load_cases(path)

    def test_main_rejects_nonpositive_limit(self) -> None:
        runner = load_runner()

        for value in ("0", "-1"):
            with self.subTest(value=value), patch.object(
                sys,
                "argv",
                ["run_specialist_eval.py", "--limit", value, "--command", "false"],
            ):
                with self.assertRaises(SystemExit):
                    runner.main()

    def test_write_results_uses_exclusive_safe_files(self) -> None:
        runner = load_runner()
        result = {
            "id": "safe-case",
            "specialist": "database-operations",
            "passed": True,
            "failures": [],
            "response": "response",
        }
        manifest = {
            "type": "manifest",
            "scoring_mode": "lexical_smoke",
            "selected_case_ids": [result["id"]],
        }

        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "results"
            runner.write_results(results_dir, [result], manifest)
            response_path = results_dir / f"{result['id']}.txt"
            self.assertEqual(
                response_path.read_text(),
                result["response"],
            )
            self.assertEqual(json.loads((results_dir / "manifest.json").read_text()), manifest)
            records = [
                json.loads(line)
                for line in (results_dir / "results.jsonl").read_text().splitlines()
            ]
            self.assertEqual([record["type"] for record in records], ["manifest", "case", "summary"])
            self.assertEqual(records[1]["case_id"], result["id"])
            self.assertEqual(records[1]["specialist"], result["specialist"])
            self.assertTrue(records[1]["passed"])
            self.assertEqual(records[1]["failures"], [])
            self.assertEqual(
                records[1]["response_sha256"],
                runner.sha256_bytes(response_path.read_bytes()),
            )
            self.assertEqual(
                records[2]["summary"],
                {
                    "scoring_mode": "lexical_smoke",
                    "passed": 1,
                    "total": 1,
                    "failures": [],
                },
            )
            for path in (
                results_dir / "manifest.json",
                results_dir / "results.jsonl",
                response_path,
            ):
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            with self.assertRaises(SystemExit):
                runner.write_results(results_dir, [result], manifest)

    def test_scored_evidence_audits_all_selected_cases_by_response_hash(self) -> None:
        runner = load_runner()
        results = [
            {
                "id": f"case-{index}",
                "specialist": "database-operations",
                "passed": True,
                "failures": [],
                "response": f"response {index}",
            }
            for index in range(1, 15)
        ]
        manifest = {
            "type": "manifest",
            "scoring_mode": "lexical_smoke",
            "selected_case_ids": [result["id"] for result in results],
        }

        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "results"
            runner.write_results(results_dir, results, manifest)
            records = [
                json.loads(line)
                for line in (results_dir / "results.jsonl").read_text().splitlines()
            ]
            case_records = [record for record in records if record["type"] == "case"]

            self.assertEqual(
                {record["case_id"] for record in case_records},
                set(manifest["selected_case_ids"]),
            )
            self.assertEqual(len(case_records), 14)
            self.assertTrue(all(record["passed"] for record in case_records))
            self.assertEqual(
                records[-1]["summary"],
                {
                    "scoring_mode": "lexical_smoke",
                    "passed": 14,
                    "total": 14,
                    "failures": [],
                },
            )

            first_record = case_records[0]
            response_path = results_dir / f"{first_record['case_id']}.txt"
            response_path.write_text("mutated response", encoding="utf-8")
            self.assertNotEqual(
                first_record["response_sha256"],
                runner.sha256_bytes(response_path.read_bytes()),
            )

    def test_specialist_writer_refuses_symlink_response_target(self) -> None:
        runner = load_runner()
        result = {
            "id": "safe-case",
            "specialist": "database-operations",
            "passed": True,
            "failures": [],
            "response": "replacement",
        }
        manifest = {
            "type": "manifest",
            "selected_case_ids": [result["id"]],
        }

        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            outside = temp / "outside.txt"
            outside.write_text("original", encoding="utf-8")
            writer = runner.SpecialistRunWriter(temp / "results", 1, manifest)
            (writer.results_dir / f"{result['id']}.txt").symlink_to(outside)
            try:
                with self.assertRaises(SystemExit):
                    writer.write_result(result)
            finally:
                writer.close()

            self.assertEqual(outside.read_text(encoding="utf-8"), "original")

    def test_specialist_writer_refuses_symlinked_directory_ancestor(self) -> None:
        runner = load_runner()
        result = {
            "id": "safe-case",
            "specialist": "database-operations",
            "passed": True,
            "failures": [],
            "response": "response",
        }
        manifest = {
            "type": "manifest",
            "selected_case_ids": [result["id"]],
        }

        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            outside = temp / "outside"
            outside.mkdir()
            linked_parent = temp / "linked-parent"
            linked_parent.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(SystemExit):
                runner.write_results(linked_parent / "results", [result], manifest)

            self.assertFalse((outside / "results").exists())

    def test_main_persists_final_scored_summary(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "results"
            with patch.object(
                sys,
                "argv",
                [
                    "run_specialist_eval.py",
                    "--limit",
                    "1",
                    "--command",
                    "adapter",
                    "--results-dir",
                    str(results_dir),
                    "--json",
                ],
            ), patch.object(
                runner,
                "command_response",
                return_value="response without required concepts",
            ), redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(), 1)

            records = [
                json.loads(line)
                for line in (results_dir / "results.jsonl").read_text().splitlines()
            ]
            self.assertEqual(records[-1]["type"], "summary")
            self.assertEqual(records[-1]["completed"], 1)
            self.assertEqual(records[-1]["total"], 1)
            self.assertEqual(records[-1]["summary"]["total"], 1)

    def test_main_preflights_results_directory_before_adapter_invocation(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "results"
            results_dir.mkdir()
            with patch.object(
                sys,
                "argv",
                [
                    "run_specialist_eval.py",
                    "--limit",
                    "1",
                    "--command",
                    "adapter",
                    "--results-dir",
                    str(results_dir),
                ],
            ), patch.object(runner, "command_response") as command_response:
                with self.assertRaises(SystemExit):
                    runner.main()

            command_response.assert_not_called()

    def test_build_run_manifest_records_lineage_without_secrets(self) -> None:
        runner = load_runner()
        cases = runner.load_cases()[:2]

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
                catalog_path=runner.CATALOG,
                command="evals/adapters/codex-specialist.sh",
                selection_mode="limit",
                jobs=2,
                case_timeout=45,
            )

        self.assertEqual(manifest["scoring_mode"], "lexical_smoke")
        self.assertEqual(manifest["schema_version"], 3)
        self.assertEqual(manifest["selected_case_ids"], [case["id"] for case in cases])
        self.assertEqual(manifest["model"], "gpt-5.5")
        self.assertEqual(manifest["execution_mode"], "live")
        self.assertEqual(manifest["host_cli_version"], "codex-cli 1.2.3")
        self.assertEqual(
            manifest["run_controls"],
            {"selection_mode": "limit", "jobs": 2, "case_timeout": 45},
        )
        self.assertEqual(len(manifest["catalog_sha256"]), 64)
        self.assertEqual(len(manifest["harness_sha256"]), 64)
        self.assertIsInstance(manifest["split_access_context"], str)
        self.assertTrue(manifest["split_access_context"])
        self.assertNotIn("do-not-record", json.dumps(manifest))
        self.assertEqual(
            manifest.get("adapter_protocol", {}).get("path"),
            "scripts/eval_adapter_protocol.py",
        )
        self.assertEqual(
            manifest.get("evidence"),
            {
                "manifest": "manifest.json",
                "results": "results.jsonl",
                "response_path_pattern": "{case_id}.txt",
                "response_digest": "sha256",
            },
        )

    def test_known_specialist_adapter_records_defaults_without_provider_environment(self) -> None:
        runner = load_runner()
        cases = runner.load_cases()[:1]

        with patch.dict(
            runner.os.environ,
            {"PATH": runner.os.environ.get("PATH", "")},
            clear=True,
        ), patch.object(
            runner,
            "query_host_cli_version",
            return_value=(None, None),
        ), patch.object(runner, "git_state", return_value={"sha": None, "dirty": None}):
            manifest = runner.build_run_manifest(
                cases=cases,
                catalog_path=runner.CATALOG,
                command="evals/adapters/codex-specialist.sh",
            )

        self.assertEqual(
            (manifest["model"], manifest["effort"]),
            ("gpt-5.6-terra", "high"),
        )
        self.assertEqual(
            manifest.get("adapter_protocol", {}).get("path"),
            "scripts/eval_adapter_protocol.py",
        )
        protocol_path = ROOT / manifest["adapter_protocol"]["path"]
        self.assertEqual(
            manifest["adapter_protocol"]["sha256"],
            runner.sha256_bytes(protocol_path.read_bytes()),
        )

    def test_command_identity_does_not_persist_secret_arguments(self) -> None:
        runner = load_runner()

        identity = runner.command_identity(
            "AUTH_TOKEN=do-not-record evals/adapters/codex-specialist.sh --token do-not-record"
        )

        serialized = json.dumps(identity)
        self.assertNotIn("do-not-record", serialized)
        self.assertEqual(identity["adapter"], "evals/adapters/codex-specialist.sh")

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
                runner.command_response("adapter", "prompt", 1)

        killpg.assert_called_once_with(process.pid, runner.signal.SIGKILL)

    def test_command_response_omits_sensitive_stderr_from_adapter_failures(self) -> None:
        runner = load_runner()
        process = Mock()
        sensitive = "api_key=sk-test-adapter-secret-value"
        process.communicate.return_value = ("", sensitive + "\n")
        process.returncode = 23

        with patch.object(runner.subprocess, "Popen", return_value=process):
            with self.assertRaises(RuntimeError) as raised:
                runner.command_response("adapter", "prompt", 1)

        self.assertNotIn(sensitive, str(raised.exception))
        self.assertIn(str(process.returncode), str(raised.exception))


if __name__ == "__main__":
    unittest.main()
