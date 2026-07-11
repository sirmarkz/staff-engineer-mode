#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_router_eval.py"
SAMPLE_RUNNER_PATH = ROOT / "scripts" / "run_correct_routing_router_eval.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RouterEvalDataContractTests(unittest.TestCase):
    def test_validator_accepts_canonical_positive_routing_catalog(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        count = validator.validate_positive_routing_catalog()

        expected_count = (len(validator.skill_names() - {"staff-engineer-mode"}) * 5) + 4
        self.assertEqual(count, expected_count)

    def test_validator_accepts_boundary_prompt_catalog(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        count = validator.validate_boundary_prompt_catalog()

        self.assertEqual(count, len(validator.skill_names() - {"staff-engineer-mode"}) * 20)

    def test_validator_accepts_canonical_router_contract_catalog(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        count = validator.validate_router_contract_catalog()

        self.assertGreaterEqual(count, 35)
        cases = validator.parse_cases(validator.ROUTER_CONTRACT_PROMPTS.read_text())
        self.assertGreaterEqual(sum(case["category"] == "ambiguous" for case in cases), 4)
        self.assertTrue(
            any("ambiguity_check" in case.get("expected_checks", []) for case in cases)
        )

    def test_validator_accepts_versioned_split_access_adversarial_catalog(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        count = validator.validate_adversarial_split_catalog()
        accepted = validator.parse_cases(
            validator.ADVERSARIAL_SPLIT_PROMPTS.read_text(encoding="utf-8")
        )

        self.assertEqual(count, len(accepted))

    def test_validator_rejects_adversarial_review_count_mismatch(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        review = json.loads(validator.ADVERSARIAL_SPLIT_REVIEW.read_text())
        review["summary"]["accepted"] += 1

        with tempfile.TemporaryDirectory() as tmp:
            review_path = Path(tmp) / "review.json"
            review_path.write_text(json.dumps(review))
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_adversarial_split_catalog(review_path=review_path)

    def test_validator_rejects_contract_catalog_without_ambiguous_cases(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        cases = validator.parse_cases(validator.ROUTER_CONTRACT_PROMPTS.read_text())
        cases = [case for case in cases if case["category"] != "ambiguous"]

        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            validator.validate_main_fixture(cases, validator.ROUTER_CONTRACT_PROMPTS)

    def test_validator_rejects_boundary_catalog_without_every_target_category(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        cases = [
            {
                "target_specialist": "documentation-lifecycle",
                "prompt": "Fix README typos and spacing.",
                "expected_primary": "none",
                "expected_behavior": "withhold routing for routine docs cleanup",
                "category": "negative",
                "expected_checks": ["scope_check"],
                "forbidden_in_response": ["all_specialist_names"],
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "boundary-router-eval.yaml"
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_boundary_cases(cases, path)

    def test_validator_rejects_extra_boundary_case_for_target(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        cases = validator.run_router_eval.parse_boundary_prompts()
        cases.append(dict(cases[0]))

        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            validator.validate_boundary_cases(cases, validator.BOUNDARY_PROMPT_DIR)

    def test_validator_accepts_positive_routing_check_shape(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        sample_runner = load_module(SAMPLE_RUNNER_PATH, "run_correct_routing_router_eval")

        missing = set(sample_runner.ROUTER_SAMPLE_PROMPT_CHECKS) - validator.ALLOWED_CHECKS

        self.assertEqual(missing, set())

    def test_validator_accepts_live_adapter_context_contract(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        try:
            validator.validate_live_adapters()
        except SystemExit as exc:
            self.fail(f"canonical live adapters should satisfy the contract: {exc}")

    def test_validator_rejects_adapter_without_harness_owned_workspace_protocol(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_router = root / "codex-router.sh"
            claude_router = root / "claude-router.sh"
            codex_specialist = root / "codex-specialist.sh"
            codex_router.write_text((ROOT / "evals/adapters/codex-router.sh").read_text())
            claude_router.write_text((ROOT / "evals/adapters/claude-router.sh").read_text())
            codex_specialist.write_text(
                (ROOT / "evals/adapters/codex-specialist.sh").read_text()
            )
            codex_router.write_text(
                codex_router.read_text().replace(
                    "SEM_EVAL_ADAPTER_WORKSPACE",
                    "SEM_EVAL_ADAPTER_WORKSPACE_MISSING",
                    1,
                )
            )

            with patch.object(
                validator, "LIVE_ADAPTERS", (codex_router, claude_router)
            ), patch.object(
                validator, "CODEX_SPECIALIST_ADAPTER", codex_specialist
            ), self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_live_adapters()

    def test_validator_rejects_adapter_owned_workspace_cleanup(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_router = root / "codex-router.sh"
            claude_router = root / "claude-router.sh"
            codex_specialist = root / "codex-specialist.sh"
            codex_router.write_text(
                (ROOT / "evals/adapters/codex-router.sh").read_text()
                + '\nleaked_workspace="$(mktemp -d)"\n'
            )
            claude_router.write_text((ROOT / "evals/adapters/claude-router.sh").read_text())
            codex_specialist.write_text(
                (ROOT / "evals/adapters/codex-specialist.sh").read_text()
            )

            with patch.object(
                validator, "LIVE_ADAPTERS", (codex_router, claude_router)
            ), patch.object(
                validator, "CODEX_SPECIALIST_ADAPTER", codex_specialist
            ), self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_live_adapters()

    def test_codex_adapter_uses_isolated_home_auth_and_tool_controls(self) -> None:
        adapter = ROOT / "evals" / "adapters" / "codex-router.sh"
        prompt = "adapter-input-sentinel"
        response = "WITHHOLD"
        auth = '{"token":"test-only"}\n'

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_home = root / "source-home"
            source_home.mkdir()
            source_codex = root / "source-codex"
            source_codex.mkdir()
            (source_codex / "auth.json").write_text(auth)
            (source_codex / "config.toml").write_text("must_not_copy = true\n")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            workspace = root / "adapter-workspace"
            workspace.mkdir(mode=0o700)
            record_path = root / "record.json"
            fake = fake_bin / "codex"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, pathlib, sys\n"
                "args = sys.argv[1:]\n"
                "output = pathlib.Path(args[args.index('--output-last-message') + 1])\n"
                "work = pathlib.Path(args[args.index('-C') + 1])\n"
                "codex_home = pathlib.Path(os.environ['CODEX_HOME'])\n"
                "record = {\n"
                "  'argv': args,\n"
                "  'home': os.environ['HOME'],\n"
                "  'codex_home': str(codex_home),\n"
                "  'auth': (codex_home / 'auth.json').read_text(),\n"
                "  'config_exists': (codex_home / 'config.toml').exists(),\n"
                "  'work': str(work),\n"
                "  'work_empty': not any(work.iterdir()),\n"
                "  'prompt_present': os.environ['EXPECTED_PROMPT'] in args[-1],\n"
                "  'workspace': os.environ['SEM_EVAL_ADAPTER_WORKSPACE'],\n"
                "  'model': os.environ['SEM_EVAL_MODEL'],\n"
                "  'effort': os.environ['SEM_EVAL_EFFORT'],\n"
                "}\n"
                "pathlib.Path(os.environ['RECORD_PATH']).write_text(json.dumps(record))\n"
                "output.write_text(os.environ['EXPECTED_RESPONSE'])\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}:{env['PATH']}",
                    "HOME": str(source_home),
                    "CODEX_HOME": str(source_codex),
                    "EXPECTED_PROMPT": prompt,
                    "EXPECTED_RESPONSE": response,
                    "RECORD_PATH": str(record_path),
                    "SEM_EVAL_ADAPTER_WORKSPACE": str(workspace),
                    "SEM_EVAL_MODEL": "gpt-5.6-terra",
                    "SEM_EVAL_EFFORT": "high",
                }
            )

            completed = subprocess.run(
                [str(adapter)],
                input=prompt,
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            record = json.loads(record_path.read_text())
            self.assertTrue(workspace.exists(), "the adapter must not remove its caller's workspace")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, response)
        self.assertEqual(record["argv"][0], "exec")
        self.assertNotEqual(record["home"], str(source_home))
        self.assertNotEqual(record["codex_home"], str(source_codex))
        self.assertEqual(record["auth"], auth)
        self.assertFalse(record["config_exists"])
        self.assertTrue(record["work_empty"])
        self.assertTrue(record["prompt_present"])
        self.assertEqual(record["workspace"], str(workspace))
        self.assertEqual(record["model"], "gpt-5.6-terra")
        self.assertEqual(record["effort"], "high")
        self.assertEqual(Path(record["codex_home"]).parent, workspace)
        self.assertFalse(Path(record["work"]).exists())
        self.assertFalse(Path(record["codex_home"]).exists())

        argv = record["argv"]
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertTrue(
            {"--ignore-user-config", "--ignore-rules", "--ephemeral", "--strict-config"}
            <= set(argv)
        )
        disabled = {
            argv[index + 1]
            for index, value in enumerate(argv[:-1])
            if value == "--disable"
        }
        self.assertTrue(
            {
                "shell_tool",
                "unified_exec",
                "code_mode_host",
                "browser_use",
                "browser_use_external",
                "browser_use_full_cdp_access",
                "computer_use",
                "in_app_browser",
                "apps",
                "image_generation",
                "multi_agent",
                "goals",
                "hooks",
                "plugins",
                "remote_plugin",
                "skill_mcp_dependency_install",
                "tool_call_mcp_elicitation",
                "request_permissions_tool",
                "standalone_web_search",
            }
            <= disabled
        )

    def test_claude_adapter_copies_only_auth_into_isolated_config(self) -> None:
        adapter = ROOT / "evals" / "adapters" / "claude-router.sh"
        prompt = "adapter-input-sentinel"
        response = "WITHHOLD"
        credentials = '{"token":"test-only"}\n'

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source-claude"
            source.mkdir()
            (source / ".credentials.json").write_text(credentials)
            (source / "settings.json").write_text('{"must_not_copy":true}\n')
            fake_bin = root / "bin"
            fake_bin.mkdir()
            workspace = root / "adapter-workspace"
            workspace.mkdir(mode=0o700)
            record_path = root / "record.json"
            fake = fake_bin / "claude"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, pathlib, sys\n"
                "args = sys.argv[1:]\n"
                "config = pathlib.Path(os.environ['CLAUDE_CONFIG_DIR'])\n"
                "record = {\n"
                "  'argv': args,\n"
                "  'cwd': os.getcwd(),\n"
                "  'cwd_empty': not any(pathlib.Path.cwd().iterdir()),\n"
                "  'home': os.environ['HOME'],\n"
                "  'config': str(config),\n"
                "  'credentials': (config / '.credentials.json').read_text(),\n"
                "  'settings_exists': (config / 'settings.json').exists(),\n"
                "  'simple_present': 'CLAUDE_CODE_SIMPLE' in os.environ,\n"
                "  'prompt_present': os.environ['EXPECTED_PROMPT'] in args[args.index('-p') + 1],\n"
                "  'workspace': os.environ['SEM_EVAL_ADAPTER_WORKSPACE'],\n"
                "  'model': os.environ['SEM_EVAL_MODEL'],\n"
                "  'effort': os.environ['SEM_EVAL_EFFORT'],\n"
                "}\n"
                "pathlib.Path(os.environ['RECORD_PATH']).write_text(json.dumps(record))\n"
                "print(os.environ['EXPECTED_RESPONSE'], end='')\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}:{env['PATH']}",
                    "CLAUDE_CONFIG_DIR": str(source),
                    "CLAUDE_CODE_SIMPLE": "1",
                    "EXPECTED_PROMPT": prompt,
                    "EXPECTED_RESPONSE": response,
                    "RECORD_PATH": str(record_path),
                    "SEM_EVAL_ADAPTER_WORKSPACE": str(workspace),
                    "SEM_EVAL_MODEL": "claude-opus-4-8",
                    "SEM_EVAL_EFFORT": "medium",
                }
            )

            completed = subprocess.run(
                [str(adapter)],
                input=prompt,
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            record = json.loads(record_path.read_text())
            self.assertTrue(workspace.exists(), "the adapter must not remove its caller's workspace")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, response)
        self.assertNotEqual(record["home"], str(source))
        self.assertNotEqual(record["config"], str(source))
        self.assertEqual(record["credentials"], credentials)
        self.assertFalse(record["settings_exists"])
        self.assertFalse(record["simple_present"])
        self.assertTrue(record["cwd_empty"])
        self.assertTrue(record["prompt_present"])
        self.assertEqual(record["workspace"], str(workspace))
        self.assertEqual(record["model"], "claude-opus-4-8")
        self.assertEqual(record["effort"], "medium")
        self.assertEqual(Path(record["config"]).parents[1], workspace)
        self.assertFalse(Path(record["cwd"]).exists())
        self.assertFalse(Path(record["config"]).exists())

        argv = record["argv"]
        self.assertNotIn("--bare", argv)
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "")
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertTrue(
            {
                "--disable-slash-commands",
                "--strict-mcp-config",
                "--mcp-config",
                "--no-session-persistence",
            }
            <= set(argv)
        )

    def test_validator_rejects_unknown_expected_check_ids(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to HA",
            "category": "direct",
            "expected_checks": ["single_primary", "unknown_shape_check"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "router-eval-set.yaml"
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_common_cases([case], path)

    def test_validator_rejects_unknown_expected_phase(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        case = {
            "prompt": "Design a highly available checkout service.",
            "expected_primary": "high-availability-design",
            "expected_behavior": "route to high availability",
            "expected_phase": "pre-merge",
            "category": "direct",
            "expected_checks": ["single_primary", "intent_inference"],
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "router-eval-set.yaml"
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_common_cases([case], path)

    def test_validator_rejects_duplicate_prompts_across_catalogs(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        cases = [
            {"prompt": "Same prompt", "category": "negative"},
            {"prompt": "same prompt", "category": "near_miss"},
        ]

        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            validator.validate_unique_prompts(cases, Path("catalogs"))


if __name__ == "__main__":
    unittest.main()
