#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE_INDEX = ROOT / "skills" / "_shared" / "references" / "source-index.md"

DISALLOWED_HOSTS = {
    "wikipedia.org",
    "medium.com",
    "readmedium.com",
    "rssing.com",
    "reddit.com",
    "quora.com",
    "stackoverflow.com",
    "stackexchange.com",
    "blogspot.com",
    "dev.to",
    "hashnode.dev",
    "substack.com",
}

REQUIRED_POLICY_HEADING = "## Source Quality Policy"
REQUIRED_FRESHNESS_HEADING = "## Freshness Contract"
REQUIRED_FRESHNESS_TERMS = ("Last verified", "Verification cadence", "Staleness signal")
SUPERSEDED_TITLES = (
    "NIST SP 800-88 Revision 1",
    "NIST SP 800-53 Revision 5",
    "SLSA Specification v1.0",
    "OWASP Top 10:2021",
    "CWE Top 25 Most Dangerous Software Weaknesses 2024",
)
MAX_FRESHNESS_DAYS = 100
LAST_VERIFIED_RE = re.compile(r"^\|\s*Last verified\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|$", re.MULTILINE)
CURRENT_BASELINE_URLS = (
    "https://csrc.nist.gov/pubs/sp/800/88/r2/final",
    "https://csrc.nist.gov/News/2025/nist-releases-revision-to-sp-800-53-controls",
    "https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/800-53",
    "https://slsa.dev/spec/v1.2/",
    "https://cwe.mitre.org/top25/index.html",
    "https://owasp.org/Top10/2025/0x00_2025-Introduction/",
)
ENTRY_RE = re.compile(r"^- (?:\[(?P<source_id>S\d+)\] )?(?P<title>.+?): (?P<url>https?://\S+)$")


def fail(message: str) -> None:
    print(f"source quality validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def host_is_disallowed(host: str) -> bool:
    return any(host == blocked or host.endswith(f".{blocked}") for blocked in DISALLOWED_HOSTS)


def validate_freshness_contract(text: str, path: Path, *, today: date | None = None) -> None:
    if REQUIRED_FRESHNESS_HEADING not in text:
        fail(f"{path} is missing {REQUIRED_FRESHNESS_HEADING}")
    missing = [term for term in REQUIRED_FRESHNESS_TERMS if term not in text]
    if missing:
        fail(f"{path} freshness contract missing: {', '.join(missing)}")
    match = LAST_VERIFIED_RE.search(text)
    if not match:
        fail(f"{path} freshness contract needs an ISO Last verified table value")
    try:
        verified = date.fromisoformat(match.group(1))
    except ValueError:
        fail(f"{path} has invalid Last verified date {match.group(1)!r}")
    current = today or date.today()
    age_days = (current - verified).days
    if age_days < 0:
        fail(f"{path} Last verified date {verified.isoformat()} is in the future")
    if age_days > MAX_FRESHNESS_DAYS:
        fail(
            f"{path} source verification is stale: {age_days} days old, "
            f"maximum {MAX_FRESHNESS_DAYS} days"
        )


def validate_superseded_labels(text: str, path: Path) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("- "):
            continue
        for title in SUPERSEDED_TITLES:
            if title in line and not any(marker in line for marker in ("Historical", "Superseded")):
                fail(f"{path}:{line_number} superseded source {title!r} must be marked historical")


def validate_current_baseline_sources(text: str, path: Path) -> None:
    missing = [url for url in CURRENT_BASELINE_URLS if url not in text]
    if missing:
        fail(f"{path} missing current baseline sources: {', '.join(missing)}")


def main() -> int:
    if not SOURCE_INDEX.exists():
        fail(f"missing {SOURCE_INDEX.relative_to(ROOT)}")

    text = SOURCE_INDEX.read_text()
    if REQUIRED_POLICY_HEADING not in text:
        fail("source index is missing the source quality policy")
    validate_freshness_contract(text, SOURCE_INDEX)
    validate_superseded_labels(text, SOURCE_INDEX)
    validate_current_baseline_sources(text, SOURCE_INDEX)

    entries = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("- "):
            continue
        match = ENTRY_RE.match(line)
        if not match:
            fail(f"malformed source entry on line {line_number}: {line}")
        source_id = match.group("source_id")
        source_label = source_id or f"line {line_number}"
        url = match.group("url")
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if parsed.scheme != "https":
            fail(f"{source_label} must use https: {url}")
        if host_is_disallowed(host):
            fail(f"{source_label} uses a disallowed low-authority host: {host}")
        entries.append((source_id, line_number))

    seen: dict[str, int] = {}
    for source_id, line_number in entries:
        if source_id is None:
            continue
        if source_id in seen:
            fail(f"{source_id} duplicated on lines {seen[source_id]} and {line_number}")
        seen[source_id] = line_number

    if len(entries) < 50:
        fail("source index appears incomplete")

    print(f"source quality validation passed: {len(entries)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
