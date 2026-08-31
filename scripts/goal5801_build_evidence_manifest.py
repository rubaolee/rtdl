#!/usr/bin/env python3
"""Build the deterministic Goal5801 local evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "rtdl.goal5801.local_evidence_manifest.v1"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    rows = []
    paths = (
        path for path in root.rglob("*")
        if path.is_file() and path.resolve() != output
    )
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        payload = path.read_bytes()
        rows.append(
            {
                "bytes": len(payload),
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256(payload),
            }
        )
    manifest = {
        "date": "2026-08-24",
        "file_count": len(rows),
        "files": rows,
        "private_signing_key_included": False,
        "schema": SCHEMA,
        "total_payload_bytes": sum(row["bytes"] for row in rows),
    }
    payload = json.dumps(
        manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    output.write_bytes(payload)
    print(
        json.dumps(
            {
                "bytes": len(payload),
                "file_count": len(rows),
                "manifest_sha256": sha256(payload),
                "total_payload_bytes": manifest["total_payload_bytes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
