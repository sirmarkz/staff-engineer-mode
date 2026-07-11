#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\((?P<target>[^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def fail(message: str) -> None:
    print(f"markdown link validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def link_path(raw_target: str) -> str | None:
    target = raw_target.strip()
    if not target or target.startswith("#") or target.startswith(EXTERNAL_PREFIXES):
        return None
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    target = unquote(target).split("#", 1)[0].split("?", 1)[0]
    return target or None


def validate_files(files: list[Path], root: Path = ROOT) -> None:
    failures: list[str] = []
    resolved_root = root.resolve()
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            relative = link_path(match.group("target"))
            if relative is None:
                continue
            target = root / relative.lstrip("/") if relative.startswith("/") else path.parent / relative
            resolved_target = target.resolve()
            line = text[: match.start()].count("\n") + 1
            location = f"{path.relative_to(root)}:{line} -> {relative}"
            try:
                resolved_target.relative_to(resolved_root)
            except ValueError:
                failures.append(f"{location} (outside repository)")
                continue
            if not resolved_target.exists():
                failures.append(location)
    if failures:
        fail("broken local links:\n  " + "\n  ".join(failures))


def discover_markdown_files(root: Path = ROOT) -> list[Path]:
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        details = completed.stderr.decode("utf-8", errors="replace").strip()
        fail(f"could not discover repository files with Git: {details or 'unknown error'}")

    files = []
    for raw_relative in completed.stdout.split(b"\0"):
        if not raw_relative:
            continue
        relative = Path(raw_relative.decode(sys.getfilesystemencoding(), errors="surrogateescape"))
        path = root / relative
        if path.suffix.lower() == ".md" and path.is_file():
            files.append(path)
    return sorted(files)


def main() -> int:
    files = discover_markdown_files()
    validate_files(files)
    print(f"markdown link validation passed: {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
