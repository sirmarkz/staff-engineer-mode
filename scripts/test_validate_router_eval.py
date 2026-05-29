#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_router_eval.py"
SAMPLE_RUNNER_PATH = ROOT / "scripts" / "run_sample_prompt_router_eval.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RouterEvalDataContractTests(unittest.TestCase):
    def test_validator_accepts_sample_prompt_check_shape(self) -> None:
        validator = load_module(VALIDATOR_PATH, "validate_router_eval")
        sample_runner = load_module(SAMPLE_RUNNER_PATH, "run_sample_prompt_router_eval")

        missing = set(sample_runner.ROUTER_SAMPLE_PROMPT_CHECKS) - validator.ALLOWED_CHECKS

        self.assertEqual(missing, set())

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


if __name__ == "__main__":
    unittest.main()
