#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import re
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_external_source_links.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_external_source_links", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load validate_external_source_links.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExternalSourceLinkTests(unittest.TestCase):
    def test_access_restricted_source_is_reported_as_unverified(self) -> None:
        validator = load_validator()
        attempts = 0

        def forbidden(_request, timeout):
            nonlocal attempts
            attempts += 1
            raise HTTPError("https://example.com", 403, "forbidden", {}, None)

        result = validator.check_url(
            "https://example.com", timeout=1, retries=1, opener=forbidden
        )

        self.assertEqual(result.status, "unverified")
        self.assertEqual(attempts, 1)

    def test_rate_limit_is_retried_then_reported(self) -> None:
        validator = load_validator()
        attempts = 0

        def rate_limited(_request, timeout):
            nonlocal attempts
            attempts += 1
            raise HTTPError("https://example.com", 429, "too many requests", {}, None)

        sleeps: list[float] = []
        result = validator.check_url(
            "https://example.com",
            timeout=1,
            retries=3,
            opener=rate_limited,
            sleeper=sleeps.append,
        )

        self.assertEqual(attempts, 3)
        self.assertEqual(sleeps, [1.0, 2.0])
        self.assertEqual(result.status, "failed")

    def test_network_failure_is_reported_after_retries(self) -> None:
        validator = load_validator()
        attempts = 0

        def unavailable(_request, timeout):
            nonlocal attempts
            attempts += 1
            raise URLError("offline")

        result = validator.check_url(
            "https://example.com",
            timeout=1,
            retries=2,
            opener=unavailable,
            sleeper=lambda _delay: None,
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(attempts, 2)

    def test_version_changing_redirect_is_reported_as_stale(self) -> None:
        validator = load_validator()

        class Response:
            def read(self, _size):
                return b"x"

            def close(self):
                return None

            def geturl(self):
                return "https://example.com/spec/v2.0/"

        result = validator.check_url(
            "https://example.com/spec/v1.0/",
            timeout=1,
            retries=1,
            opener=lambda _request, timeout: Response(),
        )

        self.assertEqual(result.status, "failed")
        self.assertNotEqual(
            validator.version_tokens("https://example.com/spec/v1.0/"),
            validator.version_tokens("https://example.com/spec/v2.0/"),
        )

    def test_trailing_slash_redirect_does_not_count_as_version_change(self) -> None:
        validator = load_validator()

        class Response:
            def read(self, _size):
                return b"x"

            def close(self):
                return None

            def geturl(self):
                return "https://example.com/spec/v1.0/"

        result = validator.check_url(
            "https://example.com/spec/v1.0",
            timeout=1,
            retries=1,
            opener=lambda _request, timeout: Response(),
        )

        self.assertEqual(result.status, "verified")

    def test_unverified_links_are_counted_but_do_not_fail_the_run(self) -> None:
        validator = load_validator()
        stdout = io.StringIO()
        stderr = io.StringIO()
        results = [
            ("https://verified.example", validator.LinkResult("verified")),
            (
                "https://restricted.example",
                validator.LinkResult("unverified", "403"),
            ),
        ]

        status = validator.report_results(results, stdout=stdout, stderr=stderr)

        self.assertEqual(status, 0)
        counts = {
            label: int(value)
            for value, label in re.findall(
                r"\b(\d+)\s+(verified|unverified|total)\b", stdout.getvalue()
            )
        }
        self.assertEqual(
            counts,
            {"verified": 1, "unverified": 1, "total": 2},
        )
        self.assertIn("https://restricted.example", stderr.getvalue())
        self.assertNotIn("https://verified.example", stderr.getvalue())

    def test_retry_after_is_capped_to_bounded_delay(self) -> None:
        validator = load_validator()
        sleeps: list[float] = []

        def rate_limited(_request, timeout):
            raise HTTPError(
                "https://example.com",
                429,
                "too many requests",
                {"Retry-After": "120"},
                None,
            )

        result = validator.check_url(
            "https://example.com",
            timeout=1,
            retries=2,
            opener=rate_limited,
            sleeper=sleeps.append,
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(sleeps, [validator.MAX_RETRY_DELAY_SECONDS])


if __name__ == "__main__":
    unittest.main()
