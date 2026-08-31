#!/usr/bin/env python3
"""Byte-rehash a Goal5769 evidence archive against its embedded manifest."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import PurePosixPath
import tarfile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    args = parser.parse_args()
    payloads: dict[str, bytes] = {}
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if member.isdir():
                continue
            if not member.isfile() or path.is_absolute() or ".." in path.parts \
                    or member.name in payloads:
                raise RuntimeError(f"unsafe/duplicate member: {member.name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable member: {member.name}")
            payloads[member.name] = handle.read()
    manifest = json.loads(payloads.pop("EVIDENCE_MANIFEST.json"))
    rows = manifest["payloads"]
    if len(rows) != manifest["payload_count"] or \
            sum(row["size_bytes"] for row in rows) != manifest["payload_bytes"]:
        raise RuntimeError("manifest arithmetic mismatch")
    if {row["path"] for row in rows} != set(payloads):
        raise RuntimeError("manifest membership mismatch")
    for row in rows:
        data = payloads[row["path"]]
        if len(data) != row["size_bytes"] or \
                hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise RuntimeError(f"payload mismatch: {row['path']}")
    print(json.dumps({
        "payload_count": len(rows),
        "payload_bytes": sum(len(data) for data in payloads.values()),
        "mismatch": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
