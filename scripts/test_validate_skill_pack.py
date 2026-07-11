#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_skill_pack.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skill_pack", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load validate_skill_pack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def remove_term(text: str, term: str) -> str:
    mutated, replacements = re.subn(re.escape(term), "_" * len(term), text, flags=re.IGNORECASE)
    if replacements == 0:
        raise AssertionError(f"fixture does not contain declared term {term!r}")
    return mutated


class ValidateSkillPackPhaseBehaviorTest(unittest.TestCase):
    def test_specialist_sections_may_inherit_router_lifecycle_behavior(self) -> None:
        validator = load_validator()
        text = "\n\n".join(
            [
                "# Example",
                "## When To Use\n\n- Use when example work needs decisions.",
                "## When Not To Use\n\n- Use another specialist for other work.",
                "## Info To Gather\n\n- Gather local facts.",
                "## Workflow\n\n1. Make the decision.",
                "## Synthesized Default\n\nUse the safe default.",
                "## Exceptions\n\n- Record exceptions.",
                "## Response Quality Bar\n\n- Lead with the decision.",
                "## Required Outputs\n\n- Decision record.",
                "## Checks Before Moving On\n\n- `decision`: decision is explicit.",
                "## Red Flags - Stop And Rework\n\n- No evidence.",
                "## Common Mistakes\n\n| Mistake | Correction |\n| --- | --- |",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "example.md"
            path.write_text(text)
            validator.validate_operational_sections(
                text, path, validator.SPECIALIST_OPERATIONAL_SECTIONS
            )

    def test_router_load_contract_requires_section_after_iron_law(self) -> None:
        validator = load_validator()
        source_path = ROOT / "skills" / "staff-engineer-mode" / "SKILL.md"
        missing_text = source_path.read_text().replace("## Load Contract", "Load Contract", 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(missing_text)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(missing_text, path)

    def test_router_load_contract_requires_platform_fallback_markers(self) -> None:
        validator = load_validator()
        source_path = ROOT / "skills" / "staff-engineer-mode" / "SKILL.md"
        text = remove_term(source_path.read_text(), validator.ROUTER_LOAD_CONTRACT_PLATFORM_TERMS[0])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(text, path)

    def test_router_load_contract_rejects_obsolete_relative_path(self) -> None:
        validator = load_validator()
        source_path = ROOT / "skills" / "staff-engineer-mode" / "SKILL.md"
        text = source_path.read_text() + "\n" + validator.ROUTER_LOAD_CONTRACT_BANNED_SUBSTRINGS[0]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text(text)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_router_load_contract(text, path)

    def test_router_load_contract_accepts_complete_section(self) -> None:
        validator = load_validator()
        path = ROOT / "skills" / "staff-engineer-mode" / "SKILL.md"
        validator.validate_router_load_contract(path.read_text(), path)

class ValidateTemplateContractTest(unittest.TestCase):
    def test_template_index_requires_owner_for_every_specialist(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            templates = root / "templates"
            templates.mkdir()
            index = templates / "README.md"
            index.write_text(
                """# Shared Templates

| Template | Owning Specialist Or Shared Use | Artifact | Maintenance Notes |
| --- | --- | --- | --- |
| `one.md` | `one` | One | Keep fields aligned. |
"""
            )
            (templates / "one.md").write_text("# One\n")
            specialists = [root / "specialists" / "one.md", root / "specialists" / "two.md"]

            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_template_ownership(specialists, templates, index)

    def test_template_index_rejects_unindexed_template(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            templates = root / "templates"
            templates.mkdir()
            index = templates / "README.md"
            index.write_text(
                """# Shared Templates

| Template | Owning Specialist Or Shared Use | Artifact | Maintenance Notes |
| --- | --- | --- | --- |
| `one.md` | `one` | One | Keep fields aligned. |
"""
            )
            (templates / "one.md").write_text("# One\n")
            (templates / "orphan.md").write_text("# Orphan\n")

            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_template_ownership(
                    [root / "specialists" / "one.md"], templates, index
                )

    def test_template_contract_requires_all_named_fields(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "llm-serving-cost-latency.md"
            path.write_text(
                """# LLM Serving Cost And Latency Plan

| Route | p95 | p99 | Cache Scope |
| --- | --- | --- | --- |
"""
            )

            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_template_required_terms(
                    path,
                    ("p50", "p95", "p99", "Authorization Scope", "Observed Or Target Hit Rate"),
                )

    def test_repository_templates_satisfy_declared_contracts(self) -> None:
        validator = load_validator()
        validator.validate_template_contracts()

    def test_declared_template_contract_detects_a_removed_field(self) -> None:
        validator = load_validator()
        filename, terms = next(iter(validator.TEMPLATE_REQUIRED_TERMS.items()))
        source = (validator.TEMPLATES / filename).read_text()
        mutated = remove_term(source, terms[0])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / filename
            path.write_text(mutated)
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                validator.validate_template_required_terms(path, terms)


if __name__ == "__main__":
    unittest.main()
