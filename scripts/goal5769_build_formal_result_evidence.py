#!/usr/bin/env python3
"""Build deterministic, reviewer-rehashable Goal5769 v33 result evidence.

The formal transaction itself is immutable.  This post-run packager only reads
the locally preserved Stage-A identity, all raw formal workers, three independent
statistical products, governance records, and the durable result documents.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5769_v33_rtx4000ada_formal_evidence"
RESULT_ROOT = Path(
    "history/internal_docs/goal5769_v33_rtx4000ada_formal_result_20260813"
)
STAGE_A_ROOT = Path(
    "history/internal_docs/goal5769_v33_stage_a_rtx4000ada_result_20260813"
)
TOP_LEVEL = (
    "history/internal_docs/goal5769_v33_rtx4000ada_three_way_formal_result_20260813.json",
    "history/internal_docs/goal5769_v33_rtx4000ada_three_way_formal_technical_report_20260813.md",
    "history/internal_docs/self_review_goal5769_v33_rtx4000ada_three_way_formal_result_20260813.md",
    "history/internal_docs/call_for_review_goal5769_v33_rtx4000ada_three_way_formal_result_20260813.md",
    "history/internal_docs/goal5769_v24_owner_continuous_execution_directive_20260812.md",
    "history/internal_docs/goal5769_v33_stage_a_strict_internal_review_20260813.json",
    "history/internal_docs/goal5769_v33_stage_a_owner_direct_authority_rtx4000ada_20260813.json",
    "history/internal_docs/goal5769_v33_stage_b_strict_internal_review_20260813.json",
    "history/internal_docs/goal5769_v33_stage_b_owner_direct_authority_rtx4000ada_20260813.json",
    "history/internal_docs/goal5769_v28_zero_worker_governance_failure_20260813.json",
    "history/internal_docs/goal5769_v29_stage_b_s1_formal_environment_failure_20260813/formal_v29/TERMINAL_FAILURE.json",
    "history/internal_docs/goal5769_v30_zero_worker_governance_failure_20260813.json",
    "history/internal_docs/goal5769_v32_zero_worker_test_manifest_governance_failure_20260813.json",
    "history/internal_docs/goal5773_v4_application_lifecycle_source_audit_20260813.json",
    "history/internal_docs/goal5773_v4_prepared_application_lifecycle_plan_20260813.md",
    "history/internal_docs/self_review_goal5773_v4_prepared_application_lifecycle_decision_20260813.md",
    "scripts/goal5768_evaluate_three_way_formal.py",
    "scripts/goal5768_recount_three_way_raw.py",
    "scripts/goal5769_independent_formal_raw_audit.py",
    "scripts/goal5769_close_formal_result.py",
    "scripts/goal5769_build_formal_result_evidence.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _members() -> tuple[Path, ...]:
    paths = [Path(name) for name in TOP_LEVEL]
    for relative_root in (RESULT_ROOT, STAGE_A_ROOT):
        payload_root = ROOT / relative_root
        if not payload_root.is_dir():
            raise FileNotFoundError(payload_root)
        paths.extend(path.relative_to(ROOT)
                     for path in sorted(payload_root.rglob("*"))
                     if path.is_file())
    unique = tuple(sorted(set(paths), key=lambda path: path.as_posix()))
    for relative in unique:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"unsafe or missing evidence payload: {relative}")
    return unique


def _build(output: Path) -> dict[str, object]:
    members = _members()
    payloads: list[tuple[str, bytes]] = []
    rows: list[dict[str, object]] = []
    for relative in members:
        name = relative.as_posix()
        data = (ROOT / relative).read_bytes()
        payloads.append((name, data))
        rows.append({"path": name, "bytes": len(data), "sha256": _sha(data)})
    manifest: dict[str, object] = {
        "schema": "rtdl.goal5769.v33_formal_evidence_manifest.v1",
        "goal": 5769,
        "candidate": "v33",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
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
    archive = ROOT / "history/internal_docs/goal5769_v33_rtx4000ada_formal_evidence_20260813.tar.gz"
    twin = ROOT / "history/internal_docs/goal5769_v33_rtx4000ada_formal_evidence_twin_20260813.tar.gz"
    first = _build(archive)
    second = _build(twin)
    if first != second or archive.read_bytes() != twin.read_bytes():
        raise RuntimeError("deterministic result evidence twin mismatch")
    print(json.dumps({
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": _sha(archive.read_bytes()),
        "twin_sha256": _sha(twin.read_bytes()),
        "payload_count": first["payload_count"],
        "payload_bytes": first["payload_bytes"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
