from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"

PAYLOADS = (
    "src/rtdsl/v4_checked_u64_device_reduction.py",
    "src/rtdsl/v4_triangle_reduction_device_runtime.py",
    "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    "scripts/goal5778_home_checked_u64_reduction_validation.py",
    "scripts/goal5778_home_triangle_checked_reduction_validation.py",
    "scripts/goal5778_recount_home_evidence.py",
    "tests/goal5778_v4_checked_u64_device_reduction_test.py",
    "tests/goal5776_v4_triangle_device_columns_test.py",
    "tests/goal5759_v4_triangle_reduction_target_test.py",
    "history/internal_docs/goal5778_home_checked_u64_reduction_validation_20260814.json",
    "history/internal_docs/goal5778_home_triangle_checked_reduction_validation_20260814.json",
    "history/internal_docs/goal5778_home_triangle_checked_reduction_validation_20260814.log",
    "history/internal_docs/goal5778_home_triangle_final_byte_replay_s1_zero_result_failure_20260814.log",
    "history/internal_docs/goal5778_independent_recount_20260814.json",
    "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json",
    "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.md",
    "history/internal_docs/v4_cgo_next_stage_plan_owner_returned_external_review_absorption_20260814.json",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def build(output: Path) -> dict:
    rows = []
    blobs = []
    for relative in sorted(PAYLOADS):
        path = ROOT / relative
        data = path.read_bytes()
        blobs.append((relative.replace("\\", "/"), data))
        rows.append({
            "path": relative.replace("\\", "/"),
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        })
    manifest = {
        "schema": "rtdl.goal5778.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in blobs:
            add_bytes(archive, f"goal5778_evidence/{name}", data)
        add_bytes(archive, "goal5778_evidence/MANIFEST.json", manifest_bytes)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as destination:
        with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=0) as compressed:
            compressed.write(raw.getvalue())
    return manifest


def main() -> None:
    output = DOCS / "goal5778_generic_checked_u64_reduction_evidence_20260814.tar.gz"
    twin = DOCS / "goal5778_generic_checked_u64_reduction_evidence_twin_20260814.tar.gz"
    manifest = build(output)
    build(twin)
    first = output.read_bytes()
    second = twin.read_bytes()
    if first != second:
        raise AssertionError("deterministic evidence twin mismatch")
    print(json.dumps({
        "archive": str(output.relative_to(ROOT)).replace("\\", "/"),
        "archive_bytes": len(first),
        "archive_sha256": sha256_bytes(first),
        "twin_byte_identical": True,
        **{key: manifest[key] for key in ("payload_count", "payload_bytes")},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
