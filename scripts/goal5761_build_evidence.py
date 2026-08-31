#!/usr/bin/env python3
"""Build deterministic reviewer-visible Goal5761 evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5761_m3_prepared_multiround_spatial_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5761_m3_prepared_multiround_spatial_evidence_twin_20260812.tar.gz"

PATHS = (
    "docs/v4/prepared_multiround_spatial_composition.md",
    "src/rtdsl/v4_multiround_spatial.py",
    "src/rtdsl/v4_multiround_spatial_optix_wrapper_codegen.py",
    "src/rtdsl/v4_multiround_spatial_optix_compiler.py",
    "src/rtdsl/v4_multiround_spatial_optix_runtime.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "scripts/goal5761_m3_spatial_fixtures.py",
    "scripts/goal5761_home_multiround_spatial_validation.py",
    "scripts/goal5761_recount_home_multiround_spatial.py",
    "scripts/goal5761_home_remote_execute.sh",
    "scripts/goal5761_build_evidence.py",
    "scripts/goal5757_verify_core_freeze.py",
    "tests/goal5761_v4_multiround_spatial_test.py",
    "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json",
    "history/internal_docs/goal5760_owner_returned_external_review_absorption_20260812.json",
    "history/internal_docs/goal5761_preimplementation_rtnn_contract_reconciliation_20260812.json",
    "history/internal_docs/goal5761_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5761_development_lineages_20260812.json",
    "history/internal_docs/goal5761_m3_prepared_multiround_spatial_result_20260812.json",
    "history/internal_docs/goal5761_m3_prepared_multiround_spatial_technical_report_20260812.md",
    "history/internal_docs/self_review_goal5761_m3_prepared_multiround_spatial_20260812.md",
    "history/internal_docs/goal5761_home_source_v4_20260812.tar.gz",
    "history/internal_docs/goal5761_home_multiround_spatial_raw_20260812/RESULT.json",
    "history/internal_docs/goal5761_home_multiround_spatial_raw_20260812/librtdl_optix.so",
    "history/internal_docs/goal5761_home_multiround_spatial_recount_20260812.json",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payloads() -> list[tuple[str, bytes]]:
    rows = []
    for relative in PATHS:
        path = ROOT / relative
        rows.append((relative.replace("\\", "/"), path.read_bytes()))
    return rows


def build(path: Path) -> dict[str, object]:
    rows = payloads()
    manifest = {
        "schema": "rtdl.goal5761.evidence_manifest.v1",
        "goal": 5761,
        "payload_count": len(rows),
        "payload_bytes": sum(len(data) for _, data in rows),
        "payloads": [
            {"path": name, "size_bytes": len(data), "sha256": sha(data)}
            for name, data in rows
        ],
    }
    manifest_data = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for name, data in (*rows, ("MANIFEST.json", manifest_data)):
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mode = 0o644
                    tar.addfile(info, io.BytesIO(data))
    return manifest


def main() -> None:
    for path in (OUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
    manifest = build(OUT)
    build(TWIN)
    if OUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("deterministic evidence twin mismatch")
    print(json.dumps({
        "archive": str(OUT),
        "sha256": sha(OUT.read_bytes()),
        "compressed_bytes": OUT.stat().st_size,
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
