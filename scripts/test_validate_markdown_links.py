#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_markdown_links.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_markdown_links", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load validate_markdown_links.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarkdownLinkValidationTests(unittest.TestCase):
    def test_discovery_honors_repository_ignore_rules(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / ".gitignore").write_text(
                "evals/runs/\ndocs/\ndecisions/\n",
                encoding="utf-8",
            )
            tracked = root / "README.md"
            tracked.write_text("# Repository\n", encoding="utf-8")
            generated = root / "evals" / "runs" / "probe" / "copied.md"
            generated.parent.mkdir(parents=True)
            generated.write_text("[missing](not-in-evidence.md)\n", encoding="utf-8")
            scratch_docs = root / "docs" / "draft.md"
            scratch_docs.parent.mkdir()
            scratch_docs.write_text("[missing](not-in-scratch.md)\n", encoding="utf-8")
            scratch_decision = root / "decisions" / "draft.md"
            scratch_decision.parent.mkdir()
            scratch_decision.write_text("[missing](not-in-scratch.md)\n", encoding="utf-8")

            files = validator.discover_markdown_files(root)

            self.assertIn(tracked, files)
            self.assertNotIn(generated, files)
            self.assertNotIn(scratch_docs, files)
            self.assertNotIn(scratch_decision, files)
            validator.validate_files(files, root)

    def test_missing_relative_link_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc = root / "README.md"
            doc.write_text("[missing](docs/missing.md)\n")

            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_files([doc], root)

    def test_existing_relative_link_and_anchor_pass(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            target = root / "docs" / "guide.md"
            target.write_text("# Guide\n")
            doc = root / "README.md"
            doc.write_text("[guide](docs/guide.md#guide) [local](#section)\n")

            validator.validate_files([doc, target], root)

    def test_existing_link_outside_repository_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            root = temp_root / "repo"
            root.mkdir()
            (temp_root / "outside.md").write_text("outside\n", encoding="utf-8")
            doc = root / "README.md"
            doc.write_text("[outside](../outside.md)\n", encoding="utf-8")
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as raised, redirect_stderr(stderr):
                validator.validate_files([doc], root)

            self.assertEqual(raised.exception.code, 1)
            self.assertIn("README.md:1", stderr.getvalue())
            self.assertIn("../outside.md", stderr.getvalue())

    def test_symlinked_link_outside_repository_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            root = temp_root / "repo"
            root.mkdir()
            outside = temp_root / "outside"
            outside.mkdir()
            (outside / "guide.md").write_text("outside\n", encoding="utf-8")
            os.symlink(outside, root / "docs", target_is_directory=True)
            doc = root / "README.md"
            doc.write_text("[guide](docs/guide.md)\n", encoding="utf-8")
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as raised, redirect_stderr(stderr):
                validator.validate_files([doc], root)

            self.assertEqual(raised.exception.code, 1)
            self.assertIn("README.md:1", stderr.getvalue())
            self.assertIn("docs/guide.md", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
