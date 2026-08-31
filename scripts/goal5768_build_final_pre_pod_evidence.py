#!/usr/bin/env python3
"""Build deterministic local evidence for the final Goal5768 pre-POD gate."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5768_three_way_pre_pod_readiness_evidence"
MEMBERS = (
    "history/internal_docs/goal5768_three_way_pre_pod_readiness_result_20260812.json",
    "history/internal_docs/goal5768_three_way_pre_pod_readiness_technical_report_20260812.md",
    "history/internal_docs/self_review_goal5768_three_way_pre_pod_readiness_20260812.md",
    "history/internal_docs/goal5768_v2_v3_v4_performance_readiness_result_20260812.json",
    "history/internal_docs/self_review_goal5768_v2_v3_v4_performance_readiness_20260812.md",
    "history/internal_docs/call_for_review_goals5763_5768_v4_completion_and_performance_hard_stop_20260812.md",
    "history/internal_docs/goal5768_application_frontdoor_completion_audit_v5_20260812.json",
    "history/internal_docs/goal5768_three_way_pre_pod_bundle_v9_20260812.tar.gz",
    "scripts/goal5768_audit_v2_v3_v4_performance_eligibility.py",
    "scripts/goal5768_three_way_frontdoors.py",
    "scripts/goal5768_three_way_functional_smoke.py",
    "scripts/goal5768_three_way_worker.py",
    "scripts/goal5768_formal_controller.py",
    "scripts/goal5768_evaluate_three_way_formal.py",
    "scripts/goal5768_recount_three_way_raw.py",
    "scripts/goal5768_target_prepare.py",
    "scripts/goal5768_build_pre_pod_bundle.py",
    "tests/goal5768_performance_eligibility_test.py",
    "tests/goal5768_three_way_frontdoors_test.py",
    "tests/goal5768_formal_harness_test.py",
    "tests/goal5768_pre_pod_bundle_test.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build(output: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    payloads: list[tuple[str, bytes]] = []
    for name in MEMBERS:
        data = (ROOT / name).read_bytes()
        payloads.append((name, data))
        rows.append({"path": name, "size": len(data), "sha256": _sha(data)})
    manifest: dict[str, object] = {
        "schema": "rtdl.goal5768.three_way_pre_pod_readiness_evidence_manifest.v1",
        "goal": 5768,
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size"]) for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in payloads:
            info = tarfile.TarInfo(f"{PREFIX}/{name}")
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
        info = tarfile.TarInfo(f"{PREFIX}/MANIFEST.json")
        info.size = len(manifest_bytes)
        info.mtime = 0
        info.mode = 0o644
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        archive.addfile(info, io.BytesIO(manifest_bytes))
    with output.open("wb") as handle:
        with gzip.GzipFile(filename="", fileobj=handle, mode="wb", mtime=0) as stream:
            stream.write(raw.getvalue())
    return manifest


def main() -> None:
    output = ROOT / "history/internal_docs/goal5768_three_way_pre_pod_readiness_evidence_20260812.tar.gz"
    twin = ROOT / "history/internal_docs/goal5768_three_way_pre_pod_readiness_evidence_twin_20260812.tar.gz"
    first = _build(output)
    second = _build(twin)
    if first != second or output.read_bytes() != twin.read_bytes():
        raise RuntimeError("deterministic evidence twin mismatch")
    print(json.dumps({
        "archive": str(output.relative_to(ROOT)),
        "archive_sha256": _sha(output.read_bytes()),
        "twin_sha256": _sha(twin.read_bytes()),
        "payload_count": first["payload_count"],
        "payload_bytes": first["payload_bytes"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
