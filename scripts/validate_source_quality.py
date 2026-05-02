#!/usr/bin/env python3
from __future__ import annotations

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
ENTRY_RE = re.compile(r"^- \[(S\d+)\] (?P<title>.+?): (?P<url>https?://\S+)$")


def fail(message: str) -> None:
    print(f"source quality validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def host_is_disallowed(host: str) -> bool:
    return any(host == blocked or host.endswith(f".{blocked}") for blocked in DISALLOWED_HOSTS)


def main() -> int:
    if not SOURCE_INDEX.exists():
        fail(f"missing {SOURCE_INDEX.relative_to(ROOT)}")

    text = SOURCE_INDEX.read_text()
    if REQUIRED_POLICY_HEADING not in text:
        fail("source index is missing the source quality policy")

    entries = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("- [S"):
            continue
        match = ENTRY_RE.match(line)
        if not match:
            fail(f"malformed source entry on line {line_number}: {line}")
        source_id = match.group(1)
        url = match.group("url")
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if parsed.scheme != "https":
            fail(f"{source_id} must use https: {url}")
        if host_is_disallowed(host):
            fail(f"{source_id} uses a disallowed low-authority host: {host}")
        entries.append((source_id, line_number))

    seen: dict[str, int] = {}
    for source_id, line_number in entries:
        if source_id in seen:
            fail(f"{source_id} duplicated on lines {seen[source_id]} and {line_number}")
        seen[source_id] = line_number

    if len(entries) < 50:
        fail("source index appears incomplete")

    print(f"source quality validation passed: {len(entries)} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
