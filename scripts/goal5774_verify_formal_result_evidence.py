#!/usr/bin/env python3
"""Byte-rehash every payload in the Goal5774 deterministic evidence archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import tarfile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    args = parser.parse_args()
    with tarfile.open(args.archive, "r:gz") as archive:
        files = {member.name: archive.extractfile(member).read()
                 for member in archive.getmembers() if member.isfile()}
    manifest_names = [name for name in files if name.endswith("/MANIFEST.json")]
    if len(manifest_names) != 1:
        raise RuntimeError("Goal5774 evidence manifest is absent or ambiguous")
    manifest_name = manifest_names[0]
    prefix = manifest_name.removesuffix("/MANIFEST.json")
    manifest = json.loads(files.pop(manifest_name))
    rows = manifest["payloads"]
    if len(rows) != manifest["payload_count"] or len(files) != len(rows):
        raise RuntimeError("Goal5774 evidence payload cardinality mismatch")
    total = 0
    for row in rows:
        relative = PurePosixPath(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("unsafe Goal5774 evidence path")
        name = f"{prefix}/{relative.as_posix()}"
        data = files.get(name)
        if data is None or len(data) != row["bytes"] \
                or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise RuntimeError(f"Goal5774 evidence payload mismatch: {relative}")
        total += len(data)
    if total != manifest["payload_bytes"]:
        raise RuntimeError("Goal5774 evidence byte total mismatch")
    print(json.dumps({
        "schema": "rtdl.goal5774.v13_formal_evidence_verification.v1",
        "payload_count": len(rows), "payload_bytes": total,
        "zero_mismatch": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
