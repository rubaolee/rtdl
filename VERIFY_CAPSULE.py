#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "CAPSULE_MANIFEST.json").read_text(encoding="utf-8"))
expected = manifest["payloads"]
optional_outer_capsule = {
    "history/internal_docs/goal5836_macbook_complete_handoff_capsule_20260831.tar.gz"
}
actual_paths = {
    p.relative_to(root).as_posix() for p in root.rglob("*")
    if p.is_file() and p.name != "CAPSULE_MANIFEST.json"
}
expected_paths = {row["path"] for row in expected}
if actual_paths - optional_outer_capsule != expected_paths:
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths - optional_outer_capsule)
    raise SystemExit(f"path-set mismatch missing={missing} extra={extra}")
for row in expected:
    path = root / row["path"]
    data = path.read_bytes()
    observed = hashlib.sha256(data).hexdigest()
    if len(data) != row["bytes"] or observed != row["sha256"]:
        raise SystemExit(f"payload mismatch: {row['path']}")
print(json.dumps({
    "status": "PASS__GOAL5836_MACBOOK_CAPSULE",
    "payload_count": len(expected),
    "payload_bytes": sum(row["bytes"] for row in expected),
}, sort_keys=True))
