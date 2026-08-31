#!/usr/bin/env python3
"""Build deterministic reviewer-visible Goal5762 evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5762_m4_exact_predicate_witness_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5762_m4_exact_predicate_witness_evidence_twin_20260812.tar.gz"

PATHS = (
    "docs/v4/exact_predicate_global_witness_composition.md",
    "src/rtdsl/v4_exact_predicate_witness.py",
    "scripts/goal5762_m4_exact_fixtures.py",
    "scripts/goal5762_home_exact_predicate_witness_validation.py",
    "scripts/goal5762_recount_home_exact_predicate_witness.py",
    "scripts/goal5762_home_remote_execute.sh",
    "scripts/goal5762_build_evidence.py",
    "scripts/goal5757_verify_core_freeze.py",
    "tests/goal5762_v4_exact_predicate_witness_test.py",
    "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json",
    "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json",
    "history/internal_docs/goal5761_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/review_goal5761_owner_returned_external_20260812.md",
    "history/internal_docs/goal5761_owner_returned_external_review_absorption_20260812.json",
    "history/internal_docs/goal5762_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5762_development_lineages_20260812.json",
    "history/internal_docs/goal5762_m4_exact_predicate_witness_result_20260812.json",
    "history/internal_docs/goal5762_m4_exact_predicate_witness_technical_report_20260812.md",
    "history/internal_docs/self_review_goal5762_m4_exact_predicate_witness_20260812.md",
    "history/internal_docs/goal5762_home_source_v4_20260812.tar.gz",
    "history/internal_docs/goal5762_home_exact_predicate_witness_raw_20260812/RESULT.json",
    "history/internal_docs/goal5762_home_exact_predicate_witness_raw_20260812/librtdl_optix.so",
    "history/internal_docs/goal5762_home_exact_predicate_witness_recount_20260812.json",
    "history/internal_docs/goal5762_home_exact_predicate_witness_pre_projection_raw_20260812/RESULT.json",
    "history/internal_docs/goal5762_home_exact_predicate_witness_pre_projection_raw_20260812/librtdl_optix.so",
    "history/internal_docs/goal5762_home_exact_predicate_witness_pre_projection_recount_20260812.json",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payloads() -> list[tuple[str, bytes]]:
    return [
        (relative.replace("\\", "/"), (ROOT / relative).read_bytes())
        for relative in PATHS
    ]


def build(path: Path) -> dict[str, object]:
    rows = payloads()
    manifest = {
        "schema": "rtdl.goal5762.evidence_manifest.v1",
        "goal": 5762,
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
