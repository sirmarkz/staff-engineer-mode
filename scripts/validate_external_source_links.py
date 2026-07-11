#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import re
import sys
import time
from typing import Callable, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE_INDEX = ROOT / "skills" / "_shared" / "references" / "source-index.md"
URL_RE = re.compile(r"^-.+?:\s+(https://\S+)$", re.MULTILINE)
ACCESS_RESTRICTED_STATUS = {401, 403, 405}
MAX_RETRY_DELAY_SECONDS = 8.0
VERSION_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])v?\d+(?:\.\d+)+(?![A-Za-z0-9])|"
    r"(?<!\d)(?:19|20)\d{2}(?!\d)|"
    r"(?<![A-Za-z0-9])r\d+(?![A-Za-z0-9])",
    re.IGNORECASE,
)


class LinkResult:
    __slots__ = ("status", "detail")

    def __init__(self, status: str, detail: str = "") -> None:
        self.status = status
        self.detail = detail


def version_tokens(url: str) -> set[str]:
    parsed = urlsplit(url)
    searchable = unquote(f"{parsed.path}?{parsed.query}")
    return {match.group(0).lower() for match in VERSION_TOKEN_RE.finditer(searchable)}


def check_url(
    url: str,
    *,
    timeout: int,
    retries: int,
    opener: Callable = urlopen,
    sleeper: Callable[[float], None] = time.sleep,
) -> LinkResult:
    request = Request(
        url,
        headers={"User-Agent": "staff-engineer-mode-source-check/1.0", "Range": "bytes=0-1023"},
    )
    last_error = "unknown failure"
    for attempt in range(retries):
        try:
            response = opener(request, timeout=timeout)
            try:
                response.read(1)
                final_url = response.geturl() if hasattr(response, "geturl") else url
            finally:
                response.close()
            requested_versions = version_tokens(url)
            final_versions = version_tokens(final_url)
            if requested_versions and requested_versions != final_versions:
                return LinkResult("failed", f"version-changing redirect: {url} -> {final_url}")
            return LinkResult("verified")
        except HTTPError as exc:
            if exc.code in ACCESS_RESTRICTED_STATUS:
                return LinkResult(
                    "unverified",
                    f"HTTP {exc.code}: {exc.reason}; reachability unverified",
                )
            last_error = f"HTTP {exc.code}: {exc.reason}"
            if exc.code == 429 and attempt + 1 < retries:
                retry_after = exc.headers.get("Retry-After") if exc.headers is not None else None
                try:
                    requested_delay = float(retry_after) if retry_after is not None else 2**attempt
                except (TypeError, ValueError):
                    requested_delay = 2**attempt
                sleeper(max(0.0, min(requested_delay, MAX_RETRY_DELAY_SECONDS)))
        except (TimeoutError, URLError, OSError) as exc:
            last_error = str(exc)
    return LinkResult("failed", last_error)


def report_results(
    results: list[tuple[str, LinkResult]],
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    verified = [(url, result) for url, result in results if result.status == "verified"]
    unverified = [(url, result) for url, result in results if result.status == "unverified"]
    failures = [(url, result) for url, result in results if result.status not in {"verified", "unverified"}]

    for url, result in sorted(unverified, key=lambda item: item[0]):
        print(f"source link unverified: {url}: {result.detail}", file=stderr)
    for url, result in sorted(failures, key=lambda item: item[0]):
        print(f"source link failed: {url}: {result.detail}", file=stderr)

    total = len(results)
    counts = f"{len(verified)} verified, {len(unverified)} unverified, {total} total"
    if failures:
        print(
            f"external source link validation failed: {len(failures)} failed, {counts}",
            file=stderr,
        )
        return 1
    print(f"external source link validation passed: {counts}", file=stdout)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scheduled reachability check for source-index URLs.")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.timeout < 1 or args.retries < 1 or args.jobs < 1:
        parser.error("--timeout, --retries, and --jobs must be positive")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    urls = URL_RE.findall(SOURCE_INDEX.read_text())
    if args.limit is not None:
        urls = urls[: args.limit]
    results: list[tuple[str, LinkResult]] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(
                check_url,
                url,
                timeout=args.timeout,
                retries=args.retries,
            ): url
            for url in urls
        }
        for future in as_completed(futures):
            results.append((futures[future], future.result()))

    return report_results(results)


if __name__ == "__main__":
    raise SystemExit(main())
