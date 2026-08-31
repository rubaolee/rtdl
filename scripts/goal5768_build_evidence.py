#!/usr/bin/env python3
"""Build deterministic evidence for the Goal5768 fail-closed audit."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5768_performance_eligibility_evidence"
MEMBERS = (
    "scripts/goal5768_audit_v2_v3_v4_performance_eligibility.py",
    "tests/goal5768_performance_eligibility_test.py",
    "tests/goal5768_v4_performance_eligibility_test.py",
    "history/internal_docs/goal5768_v2_v3_v4_performance_eligibility_audit_20260812.json",
    "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json",
    "history/internal_docs/goal5765_integrated_nine_app_recount_20260812.json",
    "history/internal_docs/goal5765_nine_app_single_identity_result_20260812.json",
    "history/internal_docs/goal5766_portable_v4_release_candidate_result_20260812.json",
    "history/internal_docs/goal5767_v4_usable_release_surface_result_20260812.json",
    "history/internal_docs/self_review_goal5767_v4_usable_release_surface_20260812.md",
    "docs/v4/nine_app_coverage.md",
    "scripts/goal5759_home_triangle_reduction_device_validation.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive(output: Path) -> dict[str, object]:
    rows = []
    for name in MEMBERS:
        data = (ROOT / name).read_bytes()
        rows.append({"path": name, "size": len(data), "sha256": _sha(data)})
    manifest = {
        "schema": "rtdl.goal5768.evidence_manifest.v1",
        "goal": 5768,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for name in MEMBERS:
            data = (ROOT / name).read_bytes()
            info = tarfile.TarInfo(f"{PREFIX}/{name}")
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(data))
        info = tarfile.TarInfo(f"{PREFIX}/MANIFEST.json")
        info.size = len(manifest_bytes)
        info.mtime = 0
        info.mode = 0o644
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        tar.addfile(info, io.BytesIO(manifest_bytes))
    with output.open("wb") as handle:
        with gzip.GzipFile(filename="", fileobj=handle, mode="wb", mtime=0) as gz:
            gz.write(raw.getvalue())
    return manifest


def main() -> None:
    archive = ROOT / "history/internal_docs/goal5768_performance_eligibility_evidence_20260812.tar.gz"
    twin = ROOT / "history/internal_docs/goal5768_performance_eligibility_evidence_twin_20260812.tar.gz"
    for path in (archive, twin):
        if path.exists():
            path.unlink()
        manifest = _archive(path)
    if archive.read_bytes() != twin.read_bytes():
        raise RuntimeError("deterministic evidence twin mismatch")
    print(json.dumps({
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": _sha(archive.read_bytes()),
        "twin_sha256": _sha(twin.read_bytes()),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
