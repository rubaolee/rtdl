#!/usr/bin/env python3
"""Independently rehash a Goal5784 A4 final evidence archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath, Path
import tarfile


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    with tarfile.open(args.archive, "r:gz") as handle:
        members = handle.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise RuntimeError("duplicate archive member")
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not member.isfile():
                raise RuntimeError(f"unsafe or non-file member: {member.name}")
        manifest_member = handle.getmember("GOAL5784_A4_EVIDENCE_MANIFEST.json")
        manifest = json.loads(handle.extractfile(manifest_member).read())
        rows = manifest["payloads"]
        if manifest["payload_count"] != len(rows):
            raise RuntimeError("manifest payload count mismatch")
        if manifest["payload_bytes"] != sum(row["size_bytes"] for row in rows):
            raise RuntimeError("manifest byte count mismatch")
        if set(names) != {row["path"] for row in rows} | {manifest_member.name}:
            raise RuntimeError("manifest membership mismatch")
        for row in rows:
            data = handle.extractfile(handle.getmember(row["path"])).read()
            if len(data) != row["size_bytes"] or sha(data) != row["sha256"]:
                raise RuntimeError(f"payload mismatch: {row['path']}")
    print(json.dumps({
        "archive_sha256": sha(args.archive.read_bytes()),
        "member_count": len(names),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "unsafe_or_duplicate_count": 0,
        "payload_mismatch_count": 0,
        "external_sidecars": manifest["external_sidecars"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
