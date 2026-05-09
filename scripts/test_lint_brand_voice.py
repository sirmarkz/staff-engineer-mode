#!/usr/bin/env python3
"""Unit tests for ``scripts/lint_brand_voice.py``.

Each rule has at least one positive (violation present) and one negative
(violation absent) case.  Tests run in a temporary directory so they never
depend on or touch the real repository contents.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "lint_brand_voice.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_brand_voice", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec so dataclass introspection (Python 3.10) can find
    # the owning module.
    sys.modules["lint_brand_voice"] = module
    spec.loader.exec_module(module)
    return module


lint = load_module()


class _TmpRepoMixin:
    """Provides a fresh temporary directory for each test."""

    def setUp(self) -> None:  # noqa: D401 - unittest hook
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def lint(self, *relatives: str) -> list:
        files = [self.root / r for r in relatives]
        findings: list = []
        for path in files:
            findings.extend(lint.lint_file(path))
        return findings

    def rules(self, findings) -> list[str]:
        return [f.rule for f in findings]


# ---------------------------------------------------------------------------
# BV001 — FAANG/cloud vendor in headers or first 5 lines
# ---------------------------------------------------------------------------


class FaangInOpeningTests(_TmpRepoMixin, unittest.TestCase):
    def test_faang_in_h1_is_flagged(self) -> None:
        path = self.write(
            "README.md",
            "# Built like Google does it\n\nA short body line.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV001/faang-in-opening", rules)

    def test_faang_in_first_five_lines_is_flagged(self) -> None:
        path = self.write(
            "README.md",
            "# Title\n\nAdopted from AWS practice.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV001/faang-in-opening", rules)

    def test_faang_deep_in_body_is_allowed(self) -> None:
        # Body line that mentions Google appears on line ~12 (well past the
        # first five content lines and not in a heading).
        body = (
            "# Title\n\n"
            "Real opening line one.\n"
            "Real opening line two.\n"
            "Real opening line three.\n"
            "Real opening line four.\n"
            "Real opening line five.\n"
            "\n"
            "## Sources\n\n"
            "Cites the Google SRE Workbook chapter on alerting.\n"
        )
        self.write("README.md", body)
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV001/faang-in-opening", rules)

    def test_skill_md_skips_yaml_frontmatter_when_locating_opening(self) -> None:
        # Frontmatter does not count toward the first-five-content-lines
        # window.  The H1, Iron Law heading, Iron Law body, and the first two
        # non-blank lines under When-To-Use already exhaust the window; the
        # mention of AWS appears later, in body prose, so it must NOT trip
        # BV001 (it would still trip BV004, which is a separate rule).
        body = (
            "---\n"
            "name: example\n"
            'description: "Use when X."\n'
            "---\n\n"
            "# Example Skill\n\n"
            "Real opening line one.\n\n"
            "## Iron Law\n\n"
            "ALWAYS DO THE THING.\n\n"
            "## When To Use\n\n"
            "When the orchestrator needs a rolling-update strategy.\n"
            "When the workflow needs idempotent retries.\n\n"
            "## Notes\n\n"
            "Cites the AWS Well-Architected reliability pillar.\n"
        )
        self.write("skills/example/SKILL.md", body)
        rules = self.rules(self.lint("skills/example/SKILL.md"))
        self.assertNotIn("BV001/faang-in-opening", rules)


# ---------------------------------------------------------------------------
# BV002 — marketing adjectives in headings/descriptions
# ---------------------------------------------------------------------------


class MarketingAdjectiveTests(_TmpRepoMixin, unittest.TestCase):
    def test_powerful_in_heading_is_flagged(self) -> None:
        self.write("README.md", "# A powerful new way to ship\n\nBody.\n")
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV002/marketing-adjective", rules)

    def test_world_class_in_description_is_flagged(self) -> None:
        self.write(
            "README.md",
            "# Title\n\n**A world-class engineering review pack.**\n\nBody.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV002/marketing-adjective", rules)

    def test_clean_heading_is_allowed(self) -> None:
        self.write("README.md", "# Staff Engineer Mode\n\nClean body line.\n")
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV002/marketing-adjective", rules)

    def test_marketing_word_in_body_prose_is_allowed(self) -> None:
        # 'comprehensive' inside body prose (not heading, not description) is
        # allowed: the brand-guardian doc only forbids it in headlines.
        body = (
            "# Title\n\nReal opening line.\n\n"
            "## Body\n\nThis section provides comprehensive coverage of the API.\n"
        )
        self.write("README.md", body)
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV002/marketing-adjective", rules)


# ---------------------------------------------------------------------------
# BV003 — vague hedging in headlines/descriptions
# ---------------------------------------------------------------------------


class HedgingTests(_TmpRepoMixin, unittest.TestCase):
    def test_helps_you_in_description_is_flagged(self) -> None:
        self.write(
            "README.md",
            "# Title\n\n**This pack helps you ship better code.**\n\nBody.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV003/hedging-in-headline", rules)

    def test_designed_to_in_heading_is_flagged(self) -> None:
        self.write(
            "README.md",
            "# A pack designed to review AI code\n\nBody.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV003/hedging-in-headline", rules)

    def test_hedging_in_body_prose_is_allowed(self) -> None:
        body = (
            "# Title\n\nReal opening line.\n\n"
            "## Notes\n\n"
            "This rule is designed to catch the most common failure modes; "
            "it can help in mixed-language repos.\n"
        )
        self.write("README.md", body)
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV003/hedging-in-headline", rules)


# ---------------------------------------------------------------------------
# BV004 — vendor names in specialist SKILL.md prose
# ---------------------------------------------------------------------------


class VendorNameInSpecialistTests(_TmpRepoMixin, unittest.TestCase):
    def _skill(self, body: str) -> str:
        return (
            "---\n"
            "name: example-skill\n"
            'description: "Use when X."\n'
            "---\n\n"
            "# Example Skill\n\n"
            "## Iron Law\n\nALWAYS DO THE THING.\n\n"
            f"{body}"
        )

    def test_kubernetes_in_specialist_body_is_flagged(self) -> None:
        self.write(
            "specialists/example-skill/SKILL.md",
            self._skill("## When To Use\n\nWhen using Kubernetes for orchestration.\n"),
        )
        rules = self.rules(self.lint("specialists/example-skill/SKILL.md"))
        self.assertIn("BV004/vendor-in-specialist", rules)

    def test_capability_language_is_allowed(self) -> None:
        self.write(
            "specialists/example-skill/SKILL.md",
            self._skill(
                "## When To Use\n\n"
                "When the orchestrator needs a rolling-update strategy.\n"
            ),
        )
        rules = self.rules(self.lint("specialists/example-skill/SKILL.md"))
        self.assertNotIn("BV004/vendor-in-specialist", rules)

    def test_vendor_inside_fenced_code_block_is_allowed(self) -> None:
        body = (
            "## When To Use\n\nA capability description.\n\n"
            "```yaml\nkind: Deployment\n# Kubernetes manifest example\n```\n"
        )
        self.write("specialists/example-skill/SKILL.md", self._skill(body))
        rules = self.rules(self.lint("specialists/example-skill/SKILL.md"))
        self.assertNotIn("BV004/vendor-in-specialist", rules)

    def test_router_skill_skips_specialist_only_rules(self) -> None:
        # The router lives at skills/staff-engineer-mode/SKILL.md and is not
        # subject to the vendor-in-specialist or iron-law-required checks.
        body = (
            "---\n"
            "name: staff-engineer-mode\n"
            'description: "Router."\n'
            "---\n\n"
            "# Staff Engineer Mode\n\n## Overview\n\nRouting body.\n"
        )
        self.write("skills/staff-engineer-mode/SKILL.md", body)
        findings = self.lint("skills/staff-engineer-mode/SKILL.md")
        rules = self.rules(findings)
        self.assertNotIn("BV004/vendor-in-specialist", rules)
        self.assertNotIn("BV005/missing-iron-law", rules)


# ---------------------------------------------------------------------------
# BV005 — every specialist SKILL.md must include ## Iron Law
# ---------------------------------------------------------------------------


class IronLawTests(_TmpRepoMixin, unittest.TestCase):
    def test_specialist_missing_iron_law_is_flagged(self) -> None:
        body = (
            "---\n"
            "name: missing-law\n"
            'description: "Use when X."\n'
            "---\n\n"
            "# Missing Law\n\n## When To Use\n\nA body.\n"
        )
        self.write("specialists/missing-law/SKILL.md", body)
        rules = self.rules(self.lint("specialists/missing-law/SKILL.md"))
        self.assertIn("BV005/missing-iron-law", rules)

    def test_specialist_with_iron_law_is_clean(self) -> None:
        body = (
            "---\n"
            "name: has-law\n"
            'description: "Use when X."\n'
            "---\n\n"
            "# Has Law\n\n## Iron Law\n\nALWAYS DO THE THING.\n\n"
            "## When To Use\n\nBody.\n"
        )
        self.write("specialists/has-law/SKILL.md", body)
        rules = self.rules(self.lint("specialists/has-law/SKILL.md"))
        self.assertNotIn("BV005/missing-iron-law", rules)


# ---------------------------------------------------------------------------
# BV101 — first-person plural marketing voice (warn)
# ---------------------------------------------------------------------------


class FirstPersonPluralTests(_TmpRepoMixin, unittest.TestCase):
    def test_we_believe_is_warned(self) -> None:
        self.write("README.md", "# Title\n\nBody.\n\nWe believe in shipping carefully.\n")
        findings = self.lint("README.md")
        rules = self.rules(findings)
        self.assertIn("BV101/first-person-plural", rules)
        # And it must be a warning, not a hard error.
        for f in findings:
            if f.rule == "BV101/first-person-plural":
                self.assertEqual(f.severity, "WARN")

    def test_clean_text_is_clean(self) -> None:
        self.write("README.md", "# Title\n\nBody.\n\nThe pack reads the diff and reports risks.\n")
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV101/first-person-plural", rules)


# ---------------------------------------------------------------------------
# BV102 — marketing-pattern line openers (warn)
# ---------------------------------------------------------------------------


class MarketingOpenerTests(_TmpRepoMixin, unittest.TestCase):
    def test_unlock_opener_is_warned(self) -> None:
        self.write(
            "README.md",
            "# Title\n\nBody.\n\nUnlock your team's potential with this pack.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV102/marketing-opener", rules)

    def test_word_starting_with_unlock_substring_is_not_flagged(self) -> None:
        # 'Discoverability' starts with 'Discover' — must NOT be flagged
        # because the opener requires a word boundary after it.
        self.write(
            "README.md",
            "# Title\n\nBody.\n\nDiscoverability of skills depends on the router.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV102/marketing-opener", rules)


# ---------------------------------------------------------------------------
# BV103 — specific count claims in headings (warn)
# ---------------------------------------------------------------------------


class SpecificCountTests(_TmpRepoMixin, unittest.TestCase):
    def test_count_in_heading_is_warned(self) -> None:
        self.write("README.md", "# 55 specialists across 8 surfaces\n\nBody.\n")
        rules = self.rules(self.lint("README.md"))
        self.assertIn("BV103/specific-count-in-headline", rules)

    def test_count_in_body_is_not_warned(self) -> None:
        self.write(
            "README.md",
            "# Title\n\nBody.\n\nThe pack ships with 55 specialists today.\n",
        )
        rules = self.rules(self.lint("README.md"))
        self.assertNotIn("BV103/specific-count-in-headline", rules)


# ---------------------------------------------------------------------------
# Exit-code behavior
# ---------------------------------------------------------------------------


class ExitCodeTests(_TmpRepoMixin, unittest.TestCase):
    def test_main_returns_nonzero_on_hard_violation(self) -> None:
        self.write("README.md", "# Built on AWS like Google does\n\nBody.\n")
        rc = lint.main(
            [
                "--root",
                str(self.root),
                "--scope",
                "README.md",
            ]
        )
        self.assertEqual(rc, 1)

    def test_main_returns_zero_when_only_warnings(self) -> None:
        # Only soft (warn) issues -> exit 0.
        self.write(
            "README.md",
            "# Title\n\nBody.\n\nWe believe in shipping carefully.\n",
        )
        rc = lint.main(
            [
                "--root",
                str(self.root),
                "--scope",
                "README.md",
            ]
        )
        self.assertEqual(rc, 0)

    def test_main_returns_zero_on_clean_repo(self) -> None:
        self.write("README.md", "# Staff Engineer Mode\n\nClean body line.\n")
        rc = lint.main(
            [
                "--root",
                str(self.root),
                "--scope",
                "README.md",
            ]
        )
        self.assertEqual(rc, 0)


# ---------------------------------------------------------------------------
# Helper coverage
# ---------------------------------------------------------------------------


class HelperTests(unittest.TestCase):
    def test_strip_frontmatter_handles_yaml(self) -> None:
        lines = [
            "---",
            "name: x",
            'description: "y"',
            "---",
            "",
            "# Title",
            "Body.",
        ]
        content, offset = lint.strip_frontmatter(lines)
        self.assertEqual(content[0], "")
        self.assertEqual(content[1], "# Title")
        self.assertEqual(offset, 5)

    def test_strip_frontmatter_no_frontmatter(self) -> None:
        lines = ["# Title", "Body."]
        content, offset = lint.strip_frontmatter(lines)
        self.assertEqual(content, lines)
        self.assertEqual(offset, 1)

    def test_is_specialist_skill(self) -> None:
        self.assertTrue(lint.is_specialist_skill(Path("specialists/foo/SKILL.md")))
        self.assertFalse(lint.is_specialist_skill(Path("skills/_shared/SKILL.md")))
        self.assertFalse(
            lint.is_specialist_skill(Path("skills/staff-engineer-mode/SKILL.md"))
        )
        self.assertFalse(lint.is_specialist_skill(Path("README.md")))


if __name__ == "__main__":
    unittest.main()
