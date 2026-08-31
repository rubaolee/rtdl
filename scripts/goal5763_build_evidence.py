#!/usr/bin/env python3
"""Build deterministic, self-contained Goal5763 evidence and twin archives."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5763_m5_grouped_event_reduction_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5763_m5_grouped_event_reduction_evidence_twin_20260812.tar.gz"
PAYLOADS = (
    "src/rtdsl/v4_grouped_event_reduction.py",
    "scripts/goal5763_home_grouped_event_reduction_validation.py",
    "scripts/goal5763_recount_home_grouped_event_reduction.py",
    "scripts/goal5763_build_evidence.py",
    "scripts/goal5757_verify_core_freeze.py",
    "tests/goal5763_v4_grouped_event_reduction_test.py",
    "history/internal_docs/goal5763_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/review_goal5762_owner_returned_external_20260812.md",
    "history/internal_docs/goal5762_owner_returned_external_review_absorption_20260812.json",
    "history/internal_docs/goal5762_postreview_closure_20260812.md",
    "history/internal_docs/goal5760_home_bounded_relation_raw_20260812/RESULT.json",
    "history/internal_docs/goal5762_home_exact_predicate_witness_raw_20260812/RESULT.json",
    "history/internal_docs/goal5763_home_grouped_event_reduction_raw_20260812/RESULT.json",
    "history/internal_docs/goal5763_home_grouped_event_reduction_final_raw_20260812/RESULT.json",
    "history/internal_docs/goal5763_home_grouped_event_reduction_final_raw_v3_20260812/RESULT.json",
    "history/internal_docs/goal5763_home_grouped_event_reduction_final_raw_v4_20260812/RESULT.json",
    "history/internal_docs/goal5763_independent_recount_20260812.json",
    "history/internal_docs/goal5763_home_execution_source_20260812.tar.gz",
    "history/internal_docs/goal5763_home_librtdl_optix_20260812.so",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tar_bytes() -> tuple[bytes, dict[str, object]]:
    payloads: list[tuple[str, bytes]] = []
    rows: list[dict[str, object]] = []
    for path_text in PAYLOADS:
        path = ROOT / path_text
        data = path.read_bytes()
        payloads.append((path_text.replace("\\", "/"), data))
        rows.append({
            "path": path_text.replace("\\", "/"),
            "sha256": _sha(data),
            "size_bytes": len(data),
        })
    manifest = {
        "schema": "rtdl.goal5763.evidence_manifest.v1",
        "goal": 5763,
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_data = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    payloads.append(("GOAL5763_EVIDENCE_MANIFEST.json", manifest_data))

    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return compressed.getvalue(), manifest


def main() -> None:
    data, manifest = _tar_bytes()
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(data)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise AssertionError("deterministic twin mismatch")
    print(json.dumps({
        "archive_sha256": _sha(data),
        "twin_sha256": _sha(TWIN.read_bytes()),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "byte_identical_twin": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
