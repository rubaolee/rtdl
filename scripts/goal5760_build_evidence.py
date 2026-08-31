#!/usr/bin/env python3
"""Build deterministic, reviewer-visible Goal5760 evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5760_m2_bounded_relation_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5760_m2_bounded_relation_evidence_twin_20260812.tar.gz"

PATHS = (
    "docs/v4/bounded_relation_emission.md",
    "src/rtdsl/v4_bounded_relation.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_bounded_relation_optix_runtime.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "examples/current/features/spatial/rtdl_polygon_set_jaccard.py",
    "scripts/goal5757_verify_core_freeze.py",
    "scripts/goal5760_m2_consumer_fixtures.py",
    "scripts/goal5760_home_bounded_relation_device_validation.py",
    "scripts/goal5760_recount_home_bounded_relation.py",
    "scripts/goal5760_home_remote_execute.sh",
    "scripts/goal5760_build_evidence.py",
    "tests/goal5760_v4_bounded_relation_test.py",
    "history/internal_docs/goal5757_v4_nine_app_migration_batches_20260811.json",
    "history/internal_docs/goal5759_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5760_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5760_development_lineages_20260812.json",
    "history/internal_docs/goal5760_m2_bounded_relation_emission_result_20260812.json",
    "history/internal_docs/self_review_goal5760_m2_bounded_relation_emission_20260812.md",
    "history/internal_docs/goal5760_home_bounded_relation_raw_20260812/RESULT.json",
    "history/internal_docs/goal5760_home_bounded_relation_raw_20260812/librtdl_optix.so",
    "history/internal_docs/goal5760_home_bounded_relation_recount_20260812.json",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payloads():
    rows = []
    for relative in PATHS:
        path = ROOT / relative
        data = path.read_bytes()
        rows.append((relative.replace("\\", "/"), data))
    return rows


def build(path: Path) -> None:
    rows = payloads()
    manifest = {
        "schema": "rtdl.goal5760.evidence_manifest.v1",
        "goal": 5760,
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


def main() -> None:
    for path in (OUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
    build(OUT)
    build(TWIN)
    if OUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("deterministic evidence twin mismatch")
    print(json.dumps({
        "archive": str(OUT),
        "sha256": sha(OUT.read_bytes()),
        "byte_count": OUT.stat().st_size,
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
