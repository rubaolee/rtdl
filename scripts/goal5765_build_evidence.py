#!/usr/bin/env python3
"""Build deterministic Goal5765 evidence and byte-identical twin archives."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5765_nine_app_single_identity_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5765_nine_app_single_identity_evidence_twin_20260812.tar.gz"

STATIC = (
    "scripts/goal5765_integrated_nine_app_recount.py",
    "scripts/goal5765_build_evidence.py",
    "scripts/goal5757_verify_core_freeze.py",
    "history/internal_docs/goal5757_v4_nine_app_migration_batches_20260811.json",
    "history/internal_docs/goal5753_held_out_particle_tracking_exam_evidence_20260811.tar.gz",
    "history/internal_docs/goal5765_home_execution_source_20260812.tar.gz",
    "history/internal_docs/goal5765_home_librtdl_optix_20260812.so",
    "history/internal_docs/goal5765_integrated_nine_app_recount_20260812.json",
    "history/internal_docs/goal5765_development_lineages_20260812.json",
    "history/internal_docs/goal5765_nine_app_single_identity_result_20260812.json",
    "history/internal_docs/goal5765_nine_app_single_identity_technical_report_20260812.md",
    "history/internal_docs/self_review_goal5765_nine_app_single_identity_20260812.md",
    "history/internal_docs/goal5765_m1_recount_20260812.json",
    "history/internal_docs/goal5765_m2_recount_20260812.json",
    "history/internal_docs/goal5765_m3_recount_20260812.json",
    "history/internal_docs/goal5765_m4_recount_20260812.json",
    "history/internal_docs/goal5765_m5_recount_20260812.json",
    "history/internal_docs/goal5765_m6_recount_20260812.json",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _paths() -> list[str]:
    paths = list(STATIC)
    for rel_root in (
        "history/internal_docs/goal5765_home_nine_app_final_raw_20260812",
        "history/internal_docs/goal5765_preliminary_lineages_20260812",
    ):
        base = ROOT / rel_root
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            paths.append(path.relative_to(ROOT).as_posix())
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate evidence payload")
    return sorted(paths)


def _archive_bytes() -> tuple[bytes, dict]:
    payloads: list[tuple[str, bytes]] = []
    rows = []
    for name in _paths():
        data = (ROOT / name).read_bytes()
        payloads.append((name, data))
        rows.append({"path": name, "sha256": _sha(data), "size_bytes": len(data)})
    manifest = {
        "schema": "rtdl.goal5765.evidence_manifest.v1",
        "goal": 5765,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads.append((
        "GOAL5765_EVIDENCE_MANIFEST.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    ))
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
    data, manifest = _archive_bytes()
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(data)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("evidence twin differs")
    print(json.dumps({
        "archive_sha256": _sha(data),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
