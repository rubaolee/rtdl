#!/usr/bin/env python3
"""Build deterministic reviewer-visible Goal5773 evidence and a twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5773_v4_prepared_application_lifecycle_evidence_20260813.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5773_v4_prepared_application_lifecycle_evidence_twin_20260813.tar.gz"


PAYLOADS = (
    "history/internal_docs/goal5773_v4_prepared_application_lifecycle_plan_20260813.md",
    "history/internal_docs/goal5773_v4_prepared_application_lifecycle_result_20260813.json",
    "history/internal_docs/goal5773_v4_prepared_application_lifecycle_technical_report_20260813.md",
    "history/internal_docs/self_review_goal5773_v4_prepared_application_lifecycle_20260813.md",
    "history/internal_docs/goal5773_v4_core_successor_manifest_20260813.json",
    "history/internal_docs/goal5773_v4_application_lifecycle_source_audit_20260813.json",
    "history/internal_docs/goal5773_t4_t5_prepared_lifecycle_interim_report_20260813.md",
    "history/internal_docs/goal5773_v4_verification_receipt_20260813.json",
    "history/internal_docs/goal5773_t7_home_all_app_prepared_lifecycle_result_20260813/MULTIROUND.json",
    "history/internal_docs/goal5773_t7_home_all_app_prepared_lifecycle_result_20260813/TRIANGLE.json",
    "history/internal_docs/goal5773_t7_home_all_app_prepared_lifecycle_result_20260813/PARTICLE_RELATION.json",
    "history/internal_docs/goal5773_t7_home_all_app_prepared_lifecycle_result_20260813/HIERARCHY.json",
    "history/internal_docs/goal5773_t7_home_all_app_prepared_lifecycle_result_20260813/INDEPENDENT_RECOUNT.json",
    "history/internal_docs/goal5773_t7_home_all_app_prepared_lifecycle_result_20260813/librtdl_optix.so",
    "docs/v4/README.md",
    "docs/v4/api_reference.md",
    "docs/v4/tutorial.md",
    "docs/v4/prepared_application_lifecycle.md",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/rtdsl/action_numba_continuation.py",
    "src/rtdsl/default_physical_selection.py",
    "src/rtdsl/v4_prepared_provider.py",
    "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
    "src/rtdsl/v4_triangle_prepared_runtime.py",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
    "src/rtdsl/v4_grouped_event_reduction.py",
    "src/rtdsl/v4_hierarchy_frontier.py",
    "src/rtdsl/v4_multiround_spatial.py",
    "src/rtdsl/v4_multiround_spatial_optix_runtime.py",
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
    "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
    "Paper-reproduction-apps/raydb-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
    "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
    "scripts/goal5757_verify_core_freeze.py",
    "scripts/goal5773_build_evidence.py",
    "scripts/goal5773_audit_v4_application_lifecycle.py",
    "scripts/goal5773_home_hierarchy_lifecycle_validation.py",
    "scripts/goal5773_home_multiround_lifecycle_validation.py",
    "scripts/goal5773_home_particle_relation_lifecycle_validation.py",
    "scripts/goal5773_home_triangle_reduction_lifecycle_validation.py",
    "scripts/goal5773_independent_home_lifecycle_recount.py",
    "tests/goal5773_v4_multiround_application_frontdoors_test.py",
    "tests/goal5773_v4_prepared_application_lifecycle_test.py",
    "tests/goal5773_v4_prepared_hierarchy_lifecycle_test.py",
    "tests/goal5773_v4_prepared_provider_test.py",
    "tests/goal5773_v4_remaining_prepared_lifecycle_test.py",
)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tar_info(name: str, size: int, mode: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = mode
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    return info


def _archive_bytes() -> tuple[bytes, dict[str, object]]:
    payloads: dict[str, bytes] = {}
    rows = []
    for relative in PAYLOADS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"unsafe or missing Goal5773 payload: {relative}")
        data = path.read_bytes()
        payloads[relative] = data
        rows.append({"path": relative, "sha256": _digest(data), "size_bytes": len(data)})
    rows.sort(key=lambda row: row["path"])
    manifest = {
        "schema": "rtdl.goal5773.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative in sorted(payloads):
            data = payloads[relative]
            mode = 0o755 if relative.startswith("scripts/") else 0o644
            archive.addfile(_tar_info(f"goal5773/{relative}", len(data), mode), io.BytesIO(data))
        archive.addfile(
            _tar_info("goal5773/GOAL5773_EVIDENCE_MANIFEST.json", len(manifest_bytes), 0o644),
            io.BytesIO(manifest_bytes),
        )
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, mtime=0) as stream:
        stream.write(raw.getvalue())
    return compressed.getvalue(), manifest


def main() -> None:
    first, manifest = _archive_bytes()
    second, twin_manifest = _archive_bytes()
    if first != second or manifest != twin_manifest:
        raise RuntimeError("Goal5773 deterministic twin mismatch")
    OUT.write_bytes(first)
    TWIN.write_bytes(second)
    print(json.dumps({
        "archive": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "archive_sha256": _digest(first),
        "archive_bytes": len(first),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
