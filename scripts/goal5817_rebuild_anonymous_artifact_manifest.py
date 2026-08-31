#!/usr/bin/env python3
"""Rebuild the compact anonymous artifact manifest from its payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PAYLOADS = (
    "README.md",
    "data/executable_residual.json",
    "data/mechanism_liveness.json",
    "data/native_typed_residual.json",
    "data/performance_workers.json",
    "data/scope_and_transfer.json",
    "data/sql_reuse.json",
    "verify.py",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.artifact_root
    rows = []
    for relative in PAYLOADS:
        path = root / relative
        payload = path.read_bytes()
        rows.append({
            "bytes": len(payload),
            "path": relative,
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    value = {
        "file_count": len(rows),
        "files": rows,
        "payload_bytes": sum(row["bytes"] for row in rows),
        "schema": "rtdl.artifact.manifest.v1",
        "scope": "ANONYMOUS_SCIENTIFIC_EVIDENCE_PROJECTION",
    }
    (root / "manifest.json").write_bytes(json.dumps(
        value, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "file_count": value["file_count"],
        "payload_bytes": value["payload_bytes"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
