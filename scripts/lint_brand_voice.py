#!/usr/bin/env python3
"""Brand-voice linter for Staff Engineer Mode.

Scans Markdown surfaces (README, top-level docs, and specialist files)
for brand-voice violations described in the brand guardian style guide.

Findings are printed in a machine-parseable format::

    path:line:column: SEVERITY: RULE: message

Hard violations (rule classes BV001-BV005) cause a non-zero exit.  Soft
violations (BV101-BV103) are reported but never fail the run.

The linter is intentionally conservative.  Each rule is bounded to the
surfaces where the brand guardian actually argues for the constraint
(headlines, openings, one-line descriptions) so that it does not fire on
legitimate body prose, citations, or comparison passages.

Usage::

    python3 scripts/lint_brand_voice.py
    python3 scripts/lint_brand_voice.py --scope 'docs/**/*.md'
    python3 scripts/lint_brand_voice.py path/to/file.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from staff_engineer_mode_contract import BRAND_LINTER_SPECIALIST_VENDOR_NAMES

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default scope: top-level user-facing docs plus router and specialist files.
DEFAULT_SCOPE: tuple[str, ...] = (
    "README.md",
    "CONTRIBUTING.md",
    "skills/staff-engineer-mode/SKILL.md",
    "specialists/*.md",
)

# FAANG and major cloud vendors whose appearance in titles or first content
# lines reads as credibility transfer rather than a real technical reference.
FAANG_AND_CLOUDS: tuple[str, ...] = (
    "Google",
    "Amazon",
    "Meta",
    "Microsoft",
    "Apple",
    "Netflix",
    "AWS",
    "Azure",
    "GCP",
)

# Marketing adjectives that the brand guardian explicitly forbids.  Matched
# case-insensitively as whole words (with light punctuation tolerance).
MARKETING_ADJECTIVES: tuple[str, ...] = (
    "powerful",
    "world-class",
    "cutting-edge",
    "revolutionary",
    "seamless",
    "comprehensive",
    "enterprise-grade",
    "best-in-class",
    "next-generation",
    "game-changing",
    "state-of-the-art",
    "industry-leading",
    "production-grade",
)

# Vague hedging in declarative claims.  Forbidden in headings and one-line
# descriptions only.  The body of a specialist file is allowed to use them.
HEDGING_PHRASES: tuple[str, ...] = (
    "helps you",
    "can help",
    "aims to",
    "tries to",
    "designed to",
    "intended to",
)

# Marketing-pattern line openers (warn, do not fail).
MARKETING_OPENERS: tuple[str, ...] = (
    "Discover",
    "Unlock",
    "Transform your",
    "Empower",
    "Streamline your",
)

# First-person plural marketing voice (warn).
FIRST_PERSON_PLURAL: tuple[str, ...] = (
    "we believe",
    "we built",
    "our mission",
    "our team",
)

# Exact-count claims in headlines (warn — counts go stale).  We match a digit
# run followed by the word "specialists" or "skills" inside heading lines.
COUNT_CLAIM_PATTERN = re.compile(
    r"\b(\d{2,4})\s+(specialists?|skills?)\b",
    re.IGNORECASE,
)

HEADING_LINE_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*$")
FENCE_OPEN_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
LIST_BULLET_RE = re.compile(r"^\s*[-*+]\s+")

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    column: int
    severity: str  # "ERROR" or "WARN"
    rule: str
    message: str

    def format(self, root: Path) -> str:
        try:
            display = self.path.relative_to(root)
        except ValueError:
            display = self.path
        return (
            f"{display}:{self.line}:{self.column}: {self.severity}: "
            f"{self.rule}: {self.message}"
        )


# ---------------------------------------------------------------------------
# File parsing helpers
# ---------------------------------------------------------------------------


def strip_frontmatter(lines: list[str]) -> tuple[list[str], int]:
    """Return (content_lines, offset) where offset is the original line number
    of the first content line (1-indexed).

    YAML frontmatter is delimited by lines that are exactly ``---``.  A
    SKILL.md with frontmatter has its title and opening prose *after* the
    closing ``---``; the brand linter measures "first 5 lines" against the
    content body, not the frontmatter envelope.
    """
    if lines and lines[0].rstrip() == "---":
        for index in range(1, len(lines)):
            if lines[index].rstrip() == "---":
                # Lines after the closing marker.
                return lines[index + 1 :], index + 2
    return lines, 1


def code_fence_mask(lines: Sequence[str]) -> list[bool]:
    """Return a boolean per line: True when the line is inside a fenced code
    block (or is itself a fence delimiter).  Used to skip code samples.
    """
    inside = False
    fence_marker: str | None = None
    mask: list[bool] = []
    for raw in lines:
        stripped = raw.lstrip()
        match = FENCE_OPEN_RE.match(raw)
        if match:
            marker = match.group(1)[:3]
            if not inside:
                inside = True
                fence_marker = marker
                mask.append(True)
                continue
            if fence_marker and stripped.startswith(fence_marker):
                mask.append(True)
                inside = False
                fence_marker = None
                continue
        mask.append(inside)
    return mask


def is_heading(line: str) -> bool:
    return HEADING_LINE_RE.match(line) is not None


def heading_level_and_text(line: str) -> tuple[int, str] | None:
    match = HEADING_LINE_RE.match(line)
    if not match:
        return None
    return len(match.group(1)), match.group(2)


def first_content_lines(
    content_lines: list[str],
    fence_mask: list[bool],
    n: int,
) -> list[tuple[int, str]]:
    """Return up to ``n`` non-blank, non-fence content lines as (index, text).

    Index is 0-based into ``content_lines``.  Lines inside fenced code blocks
    are skipped because vendor names inside install snippets are legitimate.
    """
    out: list[tuple[int, str]] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        if not raw.strip():
            continue
        out.append((index, raw))
        if len(out) >= n:
            break
    return out


def whole_word_finditer(needle: str, haystack: str) -> Iterable[re.Match[str]]:
    """Case-insensitive whole-word match.  Hyphenated needles are matched
    literally; their internal hyphens count as word characters.
    """
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_]){re.escape(needle)}(?![A-Za-z0-9_])",
        re.IGNORECASE,
    )
    return pattern.finditer(haystack)


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------


def check_faang_in_headers_and_opening(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
) -> list[Finding]:
    """BV001: FAANG/cloud vendor name in H1/H2 or in lines 1-5 of content."""
    findings: list[Finding] = []
    opening = first_content_lines(content_lines, fence_mask, 5)
    opening_indexes = {index for index, _ in opening}

    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        heading = heading_level_and_text(raw)
        in_heading = heading is not None and heading[0] in (1, 2)
        in_opening = index in opening_indexes
        if not (in_heading or in_opening):
            continue
        for term in FAANG_AND_CLOUDS:
            for match in whole_word_finditer(term, raw):
                where = "H1/H2 heading" if in_heading else "opening lines"
                findings.append(
                    Finding(
                        path=path,
                        line=index + offset,
                        column=match.start() + 1,
                        severity="ERROR",
                        rule="BV001/faang-in-opening",
                        message=(
                            f"vendor name '{term}' in {where} reads as "
                            "credibility transfer; move citations deeper in the body"
                        ),
                    )
                )
    return findings


def check_marketing_adjectives(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
    description_line_index: int | None,
) -> list[Finding]:
    """BV002: marketing adjectives in headings or one-line descriptions."""
    findings: list[Finding] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        heading = heading_level_and_text(raw)
        is_description = index == description_line_index
        if not (heading or is_description):
            continue
        for word in MARKETING_ADJECTIVES:
            for match in whole_word_finditer(word, raw):
                surface = "heading" if heading else "description"
                findings.append(
                    Finding(
                        path=path,
                        line=index + offset,
                        column=match.start() + 1,
                        severity="ERROR",
                        rule="BV002/marketing-adjective",
                        message=(
                            f"marketing adjective '{match.group(0)}' in {surface}; "
                            "the brand says less, not more"
                        ),
                    )
                )
    return findings


def check_hedging_in_headlines(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
    description_line_index: int | None,
) -> list[Finding]:
    """BV003: vague hedging in headings or one-line descriptions only."""
    findings: list[Finding] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        heading = heading_level_and_text(raw)
        is_description = index == description_line_index
        if not (heading or is_description):
            continue
        lowered = raw.lower()
        for phrase in HEDGING_PHRASES:
            start = 0
            while True:
                position = lowered.find(phrase, start)
                if position == -1:
                    break
                surface = "heading" if heading else "description"
                findings.append(
                    Finding(
                        path=path,
                        line=index + offset,
                        column=position + 1,
                        severity="ERROR",
                        rule="BV003/hedging-in-headline",
                        message=(
                            f"hedging phrase '{phrase}' in {surface}; state the "
                            "claim directly"
                        ),
                    )
                )
                start = position + len(phrase)
    return findings


def check_specialist_vendor_names(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
) -> list[Finding]:
    """BV004: specialist file must not name vendors/frameworks in prose.

    This is a brand-aligned subset of the technology-agnostic rule already
    enforced by ``validate_skill_pack.py``.  We restrict the check to body
    prose outside fenced code blocks so it doesn't redundantly fire on every
    line — but we still flag any occurrence as ERROR because it is the
    repository's stated contract.
    """
    findings: list[Finding] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        for term in BRAND_LINTER_SPECIALIST_VENDOR_NAMES:
            for match in whole_word_finditer(term, raw):
                findings.append(
                    Finding(
                        path=path,
                        line=index + offset,
                        column=match.start() + 1,
                        severity="ERROR",
                        rule="BV004/vendor-in-specialist",
                        message=(
                            f"vendor or framework name '{term}' in technology-"
                            "agnostic specialist prose; describe the capability instead"
                        ),
                    )
                )
    return findings


def check_iron_law_present(
    path: Path,
    full_text: str,
    offset_unused: int,
) -> list[Finding]:
    """BV005: every specialist file must contain an ``## Iron Law`` section."""
    if re.search(r"^\s{0,3}##\s+Iron Law\s*$", full_text, re.MULTILINE):
        return []
    return [
        Finding(
            path=path,
            line=1,
            column=1,
            severity="ERROR",
            rule="BV005/missing-iron-law",
            message=(
                "specialist file is missing the '## Iron Law' section; "
                "every specialist must declare its central rule"
            ),
        )
    ]


def check_first_person_plural(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
) -> list[Finding]:
    """BV101 (warn): first-person plural marketing voice."""
    findings: list[Finding] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        lowered = raw.lower()
        for phrase in FIRST_PERSON_PLURAL:
            position = lowered.find(phrase)
            if position == -1:
                continue
            findings.append(
                Finding(
                    path=path,
                    line=index + offset,
                    column=position + 1,
                    severity="WARN",
                    rule="BV101/first-person-plural",
                    message=(
                        f"first-person plural marketing voice '{phrase}'; "
                        "the brand speaks about the work, not the team"
                    ),
                )
            )
    return findings


def check_marketing_openers(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
) -> list[Finding]:
    """BV102 (warn): lines that open with marketing patterns."""
    findings: list[Finding] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        # Strip leading list bullets and emphasis markers before testing.
        body = LIST_BULLET_RE.sub("", raw).lstrip("*_> ").strip()
        for opener in MARKETING_OPENERS:
            if not body:
                continue
            if not body.lower().startswith(opener.lower()):
                continue
            # Require the opener to be followed by whitespace or end-of-line
            # so we don't catch words like "Discoverability".
            tail = body[len(opener) :]
            if tail and not tail[0].isspace() and tail[0] not in ".!?,:;":
                continue
            position = raw.lower().find(opener.lower())
            findings.append(
                Finding(
                    path=path,
                    line=index + offset,
                    column=max(position, 0) + 1,
                    severity="WARN",
                    rule="BV102/marketing-opener",
                    message=(
                        f"line opens with marketing pattern '{opener}'; "
                        "name the work, not the feeling"
                    ),
                )
            )
    return findings


def check_specific_count_in_headlines(
    path: Path,
    content_lines: list[str],
    offset: int,
    fence_mask: list[bool],
) -> list[Finding]:
    """BV103 (warn): specific specialist count in headings."""
    findings: list[Finding] = []
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        if not is_heading(raw):
            continue
        match = COUNT_CLAIM_PATTERN.search(raw)
        if not match:
            continue
        findings.append(
            Finding(
                path=path,
                line=index + offset,
                column=match.start() + 1,
                severity="WARN",
                rule="BV103/specific-count-in-headline",
                message=(
                    f"specific count '{match.group(0)}' in heading goes stale; "
                    "use qualitative framing instead"
                ),
            )
        )
    return findings


# ---------------------------------------------------------------------------
# Per-file orchestration
# ---------------------------------------------------------------------------


def find_description_line(content_lines: list[str], fence_mask: list[bool]) -> int | None:
    """Heuristic: a one-line description is the first non-heading, non-blank,
    non-fence line that appears within the first eight content lines and is a
    short sentence (<= 30 words) on its own.  Used as the second target
    (alongside headings) for marketing-adjective and hedging checks.

    Returns the index into ``content_lines`` or ``None`` if not found.
    """
    seen = 0
    for index, raw in enumerate(content_lines):
        if fence_mask[index]:
            continue
        if not raw.strip():
            continue
        seen += 1
        if seen > 8:
            return None
        if is_heading(raw):
            continue
        # A description is a short emphasized line: bold marker or a single
        # sentence under ~30 words.
        body = raw.strip().strip(">").strip()
        word_count = len(body.split())
        is_emphasized = body.startswith("**") and body.endswith("**")
        if is_emphasized or (word_count and word_count <= 30 and not body.startswith(("|", "-", "*"))):
            return index
    return None


def lint_file(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    raw_lines = text.splitlines()
    content_lines, offset = strip_frontmatter(raw_lines)
    fence_mask = code_fence_mask(content_lines)
    description_line_index = find_description_line(content_lines, fence_mask)

    findings: list[Finding] = []

    # Hard rules (every file)
    findings.extend(
        check_faang_in_headers_and_opening(path, content_lines, offset, fence_mask)
    )
    findings.extend(
        check_marketing_adjectives(
            path, content_lines, offset, fence_mask, description_line_index
        )
    )
    findings.extend(
        check_hedging_in_headlines(
            path, content_lines, offset, fence_mask, description_line_index
        )
    )

    # Hard rules (specialist files only)
    if is_specialist_skill(path):
        findings.extend(
            check_specialist_vendor_names(path, content_lines, offset, fence_mask)
        )
        findings.extend(check_iron_law_present(path, text, offset))

    # Soft rules
    findings.extend(
        check_first_person_plural(path, content_lines, offset, fence_mask)
    )
    findings.extend(
        check_marketing_openers(path, content_lines, offset, fence_mask)
    )
    findings.extend(
        check_specific_count_in_headlines(path, content_lines, offset, fence_mask)
    )

    return findings


def is_specialist_skill(path: Path) -> bool:
    """A specialist file lives under ``specialists/<name>.md``."""
    if path.suffix != ".md":
        return False
    parts = path.parts
    if "specialists" not in parts:
        return False
    specialists_index = parts.index("specialists")
    if specialists_index != len(parts) - 2:
        return False
    return bool(path.stem)


# ---------------------------------------------------------------------------
# Scope resolution
# ---------------------------------------------------------------------------


def resolve_scope(
    root: Path, scope: Sequence[str], explicit_paths: Sequence[Path]
) -> list[Path]:
    if explicit_paths:
        return [p.resolve() for p in explicit_paths if p.exists()]
    matches: list[Path] = []
    seen: set[Path] = set()
    for pattern in scope:
        for match in sorted(root.glob(pattern)):
            if not match.is_file():
                continue
            resolved = match.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            matches.append(resolved)
    return matches


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Brand-voice linter for Staff Engineer Mode.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional explicit Markdown paths to lint (overrides --scope).",
    )
    parser.add_argument(
        "--scope",
        action="append",
        default=None,
        metavar="GLOB",
        help=(
            "Glob pattern relative to the repo root.  May be passed multiple "
            "times.  Defaults to README.md, top-level docs, the router, and specialists/*.md."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root (default: auto-detected).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root: Path = args.root.resolve()
    scope = tuple(args.scope) if args.scope else DEFAULT_SCOPE
    explicit = [p if p.is_absolute() else (root / p) for p in args.paths]

    files = resolve_scope(root, scope, explicit)
    if not files:
        print("brand voice linter: no files matched scope", file=sys.stderr)
        return 0

    all_findings: list[Finding] = []
    for path in files:
        all_findings.extend(lint_file(path))

    if args.format == "json":
        payload = [
            {
                "path": str(f.path.relative_to(root))
                if str(f.path).startswith(str(root))
                else str(f.path),
                "line": f.line,
                "column": f.column,
                "severity": f.severity,
                "rule": f.rule,
                "message": f.message,
            }
            for f in all_findings
        ]
        print(json.dumps(payload, indent=2))
    else:
        for finding in all_findings:
            print(finding.format(root))

    hard = sum(1 for f in all_findings if f.severity == "ERROR")
    soft = sum(1 for f in all_findings if f.severity == "WARN")
    summary = (
        f"brand voice linter: {len(files)} file(s) scanned, "
        f"{hard} hard violation(s), {soft} warning(s)"
    )
    print(summary, file=sys.stderr)
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
