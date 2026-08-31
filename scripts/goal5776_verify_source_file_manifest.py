#!/usr/bin/env python3
"""Verify every exact pre-rematerialization Goal5776 source member."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


MANIFEST_MEMBER = "history/internal_docs/goal5776_source_file_manifest.json"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(source_root: Path, manifest_path: Path) -> dict[str, object]:
    root = source_root.resolve()
    manifest = manifest_path.resolve()
    if root.is_symlink() or not root.is_dir() or manifest.is_symlink() \
            or not manifest.is_file():
        raise RuntimeError("Goal5776 source manifest authority is absent")
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    if payload.get("schema") != "rtdl.goal5776.source_file_manifest.v1":
        raise RuntimeError("Goal5776 source manifest schema mismatch")
    rows = payload.get("files")
    if not isinstance(rows, list) or payload.get("file_count") != len(rows):
        raise RuntimeError("Goal5776 source manifest cardinality mismatch")
    expected = {str(row["path"]): row for row in rows}
    if len(expected) != len(rows) or MANIFEST_MEMBER in expected:
        raise RuntimeError("Goal5776 source manifest has duplicate/self row")
    actual: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"Goal5776 source contains symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise RuntimeError(f"Goal5776 source contains special file: {path}")
        name = path.relative_to(root).as_posix()
        if name == MANIFEST_MEMBER:
            continue
        actual[name] = path
    if set(actual) != set(expected):
        raise RuntimeError("Goal5776 source membership differs from manifest")
    for name, path in actual.items():
        row = expected[name]
        if path.stat().st_size != int(row["size_bytes"]) \
                or _sha(path) != row["sha256"]:
            raise RuntimeError(f"Goal5776 source byte mismatch: {name}")
    return {
        "schema": "rtdl.goal5776.source_file_manifest_check.v1",
        "status": "PASS", "file_count": len(actual),
        "manifest_sha256": _sha(manifest),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.source_root, args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()
