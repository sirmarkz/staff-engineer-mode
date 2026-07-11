#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_source_quality.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_source_quality", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load validate_source_quality.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceFreshnessContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.path = ROOT / "skills" / "_shared" / "references" / "source-index.md"
        self.text = self.path.read_text()

    def test_repository_source_index_satisfies_freshness_contract(self) -> None:
        self.validator.validate_freshness_contract(self.text, self.path)
        self.validator.validate_superseded_labels(self.text, self.path)
        self.validator.validate_current_baseline_sources(self.text, self.path)

    def test_freshness_contract_rejects_each_removed_required_field(self) -> None:
        required = (
            self.validator.REQUIRED_FRESHNESS_HEADING,
            *self.validator.REQUIRED_FRESHNESS_TERMS,
        )
        for term in required:
            with self.subTest(term=term):
                mutated = self.text.replace(term, "_" * len(term))
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    self.validator.validate_freshness_contract(mutated, self.path)

    def test_superseded_sources_require_historical_classification(self) -> None:
        for title in self.validator.SUPERSEDED_TITLES:
            with self.subTest(title=title):
                unclassified = f"- {title}: https://example.invalid/source\n"
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    self.validator.validate_superseded_labels(unclassified, self.path)

                classified = f"- Historical — {title}: https://example.invalid/source\n"
                self.validator.validate_superseded_labels(classified, self.path)

    def test_current_baseline_validation_detects_each_omitted_source(self) -> None:
        self.validator.validate_current_baseline_sources(self.text, self.path)
        for url in self.validator.CURRENT_BASELINE_URLS:
            with self.subTest(url=url):
                mutated = self.text.replace(url, "")
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    self.validator.validate_current_baseline_sources(mutated, self.path)

    def test_freshness_contract_rejects_stale_last_verified_date(self) -> None:
        today = date(2026, 7, 10)
        stale = today - timedelta(days=self.validator.MAX_FRESHNESS_DAYS + 1)
        mutated, replacements = self.validator.LAST_VERIFIED_RE.subn(
            f"| Last verified | {stale.isoformat()} |",
            self.text,
            count=1,
        )
        self.assertEqual(replacements, 1)
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            self.validator.validate_freshness_contract(mutated, self.path, today=today)

if __name__ == "__main__":
    unittest.main()
