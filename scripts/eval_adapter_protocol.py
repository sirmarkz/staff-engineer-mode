#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path
from typing import NamedTuple

ADAPTER_WORKSPACE_ENV = "SEM_EVAL_ADAPTER_WORKSPACE"
ADAPTER_MODEL_ENV = "SEM_EVAL_MODEL"
ADAPTER_EFFORT_ENV = "SEM_EVAL_EFFORT"


def directory_open_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def validate_child_name(name: str) -> None:
    if (
        not name
        or name in {".", ".."}
        or os.path.basename(name) != name
        or "\x00" in name
    ):
        raise ValueError(f"unsafe output path component {name!r}")


def open_directory_no_symlinks(path: Path, *, create: bool = False) -> int:
    absolute = Path(os.path.abspath(os.fspath(path)))
    anchor = absolute.anchor
    if not anchor:
        raise ValueError(f"output path has no filesystem anchor: {path}")
    anchor_parts = Path(anchor).parts
    components = absolute.parts[len(anchor_parts) :]
    descriptor = os.open(anchor, directory_open_flags())
    try:
        for component in components:
            validate_child_name(component)
            try:
                child = os.open(
                    component,
                    directory_open_flags(),
                    dir_fd=descriptor,
                )
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    os.mkdir(component, 0o777, dir_fd=descriptor)
                except FileExistsError:
                    pass
                child = os.open(
                    component,
                    directory_open_flags(),
                    dir_fd=descriptor,
                )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def reserve_directory_at(
    parent_descriptor: int,
    name: str,
    *,
    mode: int = 0o700,
) -> int:
    validate_child_name(name)
    os.mkdir(name, mode, dir_fd=parent_descriptor)
    descriptor = os.open(
        name,
        directory_open_flags(),
        dir_fd=parent_descriptor,
    )
    try:
        os.fchmod(descriptor, mode)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def reserve_run_directory(path: Path, *, mode: int = 0o700) -> int:
    absolute = Path(os.path.abspath(os.fspath(path)))
    if absolute.parent == absolute:
        raise ValueError("the filesystem root cannot be a run directory")
    parent_descriptor = open_directory_no_symlinks(absolute.parent, create=True)
    try:
        return reserve_directory_at(
            parent_descriptor,
            absolute.name,
            mode=mode,
        )
    finally:
        os.close(parent_descriptor)


def open_exclusive_file_at(
    directory_descriptor: int,
    name: str,
    *,
    mode: int = 0o600,
) -> int:
    validate_child_name(name)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(
        name,
        flags,
        mode,
        dir_fd=directory_descriptor,
    )
    try:
        os.fchmod(descriptor, mode)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def open_exclusive_file(path: Path, *, mode: int = 0o600) -> int:
    absolute = Path(os.path.abspath(os.fspath(path)))
    parent_descriptor = open_directory_no_symlinks(absolute.parent, create=True)
    try:
        return open_exclusive_file_at(
            parent_descriptor,
            absolute.name,
            mode=mode,
        )
    finally:
        os.close(parent_descriptor)


class KnownAdapterDefaults(NamedTuple):
    model_environment: str
    effort_environment: str
    model: str
    effort: str


class AdapterSettings(NamedTuple):
    model: str | None
    effort: str | None


def adapter_failure_message(returncode: int, stdout: str, stderr: str) -> str:
    channels = [
        name
        for name, value in (("stdout", stdout), ("stderr", stderr))
        if value.strip()
    ]
    diagnostic_state = (
        f"diagnostics on {' and '.join(channels)} omitted"
        if channels
        else "no diagnostics emitted"
    )
    return f"adapter exited with status {returncode}; {diagnostic_state}"


KNOWN_ADAPTER_DEFAULTS = {
    "evals/adapters/codex-router.sh": KnownAdapterDefaults(
        "CODEX_MODEL", "CODEX_EFFORT", "gpt-5.6-terra", "high"
    ),
    "evals/adapters/claude-router.sh": KnownAdapterDefaults(
        "CLAUDE_MODEL", "CLAUDE_EFFORT", "claude-opus-4-8", "medium"
    ),
    "evals/adapters/codex-specialist.sh": KnownAdapterDefaults(
        "CODEX_MODEL", "CODEX_EFFORT", "gpt-5.6-terra", "high"
    ),
}


def resolve_adapter_settings(
    *,
    adapter: str | None,
    command: str,
    environment: Mapping[str, str] | None = None,
) -> AdapterSettings:
    source = os.environ if environment is None else environment
    defaults = KNOWN_ADAPTER_DEFAULTS.get(adapter or "")
    if defaults is not None:
        return AdapterSettings(
            source.get(defaults.model_environment) or defaults.model,
            source.get(defaults.effort_environment) or defaults.effort,
        )
    if "claude" in command.lower():
        return AdapterSettings(
            source.get("CLAUDE_MODEL"), source.get("CLAUDE_EFFORT")
        )
    if "codex" in command.lower():
        return AdapterSettings(source.get("CODEX_MODEL"), source.get("CODEX_EFFORT"))
    return AdapterSettings(
        source.get("CODEX_MODEL") or source.get("CLAUDE_MODEL"),
        source.get("CODEX_EFFORT") or source.get("CLAUDE_EFFORT"),
    )


def build_adapter_environment(
    settings: AdapterSettings,
    workspace: Path,
    environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    result = dict(os.environ if environment is None else environment)
    result[ADAPTER_WORKSPACE_ENV] = str(workspace)
    for name, value in (
        (ADAPTER_MODEL_ENV, settings.model),
        (ADAPTER_EFFORT_ENV, settings.effort),
    ):
        if value is None:
            result.pop(name, None)
        else:
            result[name] = value
    return result
