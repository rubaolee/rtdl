#!/usr/bin/env python3
"""Build deterministic reviewer-rehashable Goal5774 result evidence."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5774_v13_rtx4000ada_prepared_v2_v4_evidence"
PREPARE_ROOT = Path("history/internal_docs/goal5774_v13_rtx4000ada_prepare_s3_20260813")
FORMAL_ROOT = Path("history/internal_docs/goal5774_v13_rtx4000ada_formal_result_20260813")
FAILURE_ROOTS = (
    Path("history/internal_docs/goal5774_v13_rtx4000ada_prepare_s1_zero_worker_failure_20260813"),
    Path("history/internal_docs/goal5774_v13_rtx4000ada_prepare_s2_zero_worker_failure_20260813"),
)
TOP_LEVEL = (
    "history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_formal_result_20260813.json",
    "history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_formal_technical_report_20260813.md",
    "history/internal_docs/self_review_goal5774_v13_rtx4000ada_prepared_v2_v4_formal_result_20260813.md",
    "history/internal_docs/call_for_review_goal5774_v13_rtx4000ada_prepared_v2_v4_formal_result_20260813.md",
    "history/internal_docs/self_review_goal5774_rtx4000ada_formal_admission_20260813.md",
    "history/internal_docs/goal5774_rtx4000ada_create_only_authority_v13_20260813.json",
    "history/internal_docs/goal5774_rtx4000ada_formal_authority_v13_20260813.json",
    "history/internal_docs/goal5774_v2_v4_pre_pod_bundle_v13_20260813.tar.gz",
    "history/internal_docs/goal5749_optix9_include_20260811.tar.gz",
    "history/internal_docs/goal5774_v2_v4_pre_pod_readiness_result_20260813.json",
    "history/internal_docs/goal5774_v2_v4_pre_pod_readiness_technical_report_20260813.md",
    "history/internal_docs/self_review_goal5774_v2_v4_pre_pod_readiness_20260813.md",
    "history/internal_docs/call_for_review_goal5774_v2_v4_pre_pod_readiness_20260813.md",
    "history/internal_docs/goal5774_v2_v4_pre_pod_review_packet_manifest_20260813.json",
    "scripts/goal5774_target_prepare.py",
    "scripts/goal5774_prepared_three_way_frontdoors.py",
    "scripts/goal5774_prepared_v2_v4_worker.py",
    "scripts/goal5774_prepared_v2_v4_controller.py",
    "scripts/goal5774_evaluate_prepared_v2_v4.py",
    "scripts/goal5774_recount_prepared_v2_v4_raw.py",
    "scripts/goal5774_close_formal_result.py",
    "scripts/goal5774_build_formal_result_evidence.py",
    "scripts/goal5774_verify_formal_result_evidence.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _members() -> tuple[Path, ...]:
    paths = [Path(name) for name in TOP_LEVEL]
    for relative_root in (PREPARE_ROOT, FORMAL_ROOT, *FAILURE_ROOTS):
        root = ROOT / relative_root
        if not root.is_dir():
            raise FileNotFoundError(root)
        paths.extend(path.relative_to(ROOT) for path in sorted(root.rglob("*"))
                     if path.is_file())
    unique = tuple(sorted(set(paths), key=lambda path: path.as_posix()))
    for relative in unique:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"unsafe or missing evidence member: {relative}")
    return unique


def _build(output: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    payloads: list[tuple[str, bytes]] = []
    for relative in _members():
        data = (ROOT / relative).read_bytes()
        name = relative.as_posix()
        rows.append({"path": name, "bytes": len(data), "sha256": _sha(data)})
        payloads.append((name, data))
    manifest: dict[str, object] = {
        "schema": "rtdl.goal5774.v13_formal_evidence_manifest.v1",
        "goal": 5774,
        "candidate": "v13",
        "formal_worker_count": 208,
        "independent_row_count": 26,
        "pass_count": 0,
        "fail_count": 26,
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
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
        info.size = len(manifest_data)
        info.mtime = 0
        info.mode = 0o644
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        archive.addfile(info, io.BytesIO(manifest_data))
    with output.open("wb") as handle:
        with gzip.GzipFile(filename="", fileobj=handle, mode="wb", mtime=0) as stream:
            stream.write(raw.getvalue())
    return manifest


def main() -> None:
    archive = ROOT / "history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_evidence_20260813.tar.gz"
    twin = ROOT / "history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_evidence_twin_20260813.tar.gz"
    first = _build(archive)
    second = _build(twin)
    if first != second or archive.read_bytes() != twin.read_bytes():
        raise RuntimeError("Goal5774 deterministic evidence twin mismatch")
    receipt = {
        "schema": "rtdl.goal5774.v13_formal_evidence_receipt.v1",
        "archive": archive.relative_to(ROOT).as_posix(),
        "archive_sha256": _sha(archive.read_bytes()),
        "twin_sha256": _sha(twin.read_bytes()),
        "payload_count": first["payload_count"],
        "payload_bytes": first["payload_bytes"],
    }
    receipt_path = ROOT / "history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_evidence_receipt_20260813.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
