#!/usr/bin/env python3
"""Fail closed if Goal5753 changes the frozen Goal5752 core surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath


EXACT_FILES = {
    "Makefile",
    "pyproject.toml",
    "requirements.txt",
}
EXACT_PREFIXES = ("src/",)
FREEZE_COMMIT_FILES = ("docs/v4/restricted_python_optix_callbacks_design.md",)
TEXT_SUFFIXES = {".c", ".cc", ".cpp", ".cu", ".cuh", ".h", ".hpp", ".py", ".toml", ".txt"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def admitted(path: str) -> bool:
    pure = PurePosixPath(path)
    if "__pycache__" in pure.parts or pure.suffix in {".pyc", ".nbc", ".nbi"}:
        return False
    return path in EXACT_FILES or any(path.startswith(prefix) for prefix in EXACT_PREFIXES)


def source_digest(path: str, data: bytes) -> str:
    """Digest source semantics while tolerating Windows checkout line endings."""
    if PurePosixPath(path).suffix.lower() in TEXT_SUFFIXES or path in EXACT_FILES:
        data = data.replace(b"\r\n", b"\n")
    return sha256(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--frozen-source", type=Path, required=True)
    parser.add_argument("--frozen-native", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-native-sha256", required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_bytes = args.frozen_source.read_bytes()
    native_bytes = args.frozen_native.read_bytes()
    if sha256(source_bytes) != args.expected_source_sha256:
        raise ValueError("frozen source archive identity mismatch")
    if sha256(native_bytes) != args.expected_native_sha256:
        raise ValueError("frozen native identity mismatch")

    expected: dict[str, str] = {}
    with tarfile.open(args.frozen_source, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe frozen source member: {member.name}")
            normalized = path.as_posix().lstrip("./")
            if member.isfile() and admitted(normalized):
                stream = archive.extractfile(member)
                assert stream is not None
                expected[normalized] = source_digest(normalized, stream.read())

    actual: dict[str, str] = {}
    for path in args.workspace.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(args.workspace).as_posix()
        if admitted(relative):
            actual[relative] = source_digest(relative, path.read_bytes())

    freeze_commit_files: dict[str, str] = {}
    for relative in FREEZE_COMMIT_FILES:
        frozen = subprocess.run(
            ["git", "show", f"{args.freeze_commit}:{relative}"],
            cwd=args.workspace,
            check=True,
            capture_output=True,
        ).stdout
        current = (args.workspace / relative).read_bytes()
        frozen_digest = source_digest(relative, frozen)
        current_digest = source_digest(relative, current)
        if frozen_digest != current_digest:
            raise RuntimeError(f"Goal5753 freeze-commit policy drift: {relative}")
        freeze_commit_files[relative] = frozen_digest

    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])
    if missing or added or changed:
        raise RuntimeError(
            f"Goal5753 frozen core drift: missing={missing}, added={added}, changed={changed}"
        )

    result = {
        "schema": "rtdl.v4.goal5753.frozen_core_seal_audit.v1",
        "status": "exact_goal5752_core_and_native_unchanged",
        "execution_source_archive_sha256": sha256(source_bytes),
        "native_sha256": sha256(native_bytes),
        "audited_file_count": len(expected),
        "missing": missing,
        "added": added,
        "changed": changed,
        "scope": {
            "exact_files": sorted(EXACT_FILES),
            "exact_prefixes": list(EXACT_PREFIXES),
            "freeze_commit": args.freeze_commit,
            "freeze_commit_files": freeze_commit_files,
            "line_endings_normalized_for_text_source_only": True,
        },
        "held_out_exam_core_diff_count": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
