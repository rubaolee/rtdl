#!/usr/bin/env python3
"""Build deterministic reviewer-visible evidence for Goal5780."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


FILES = (
    "history/internal_docs/review_v4_cgo_next_stage_plan_after_goal5776_20260814.md",
    "history/internal_docs/v4_cgo_next_stage_plan_owner_returned_external_review_absorption_20260814.json",
    "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json",
    "history/internal_docs/goal5776_v9_rtx4000ada_real_scale_v2_v4_result_20260814.json",
    "history/internal_docs/goal5777_source_supported_causal_findings_20260814.json",
    "history/internal_docs/goal5776_v9_execution_source_rtx4000ada_20260814.tar.gz",
    "history/internal_docs/goal5779_home_librtdl_optix.so",
    "history/internal_docs/goal5780_rt_barneshut_residual_inputs_20260814/prepared_arrays.json",
    "history/internal_docs/goal5780_rt_barneshut_residual_inputs_20260814/expected_forces.txt",
    "scripts/goal5780_rtbh_unchanged_route_profile.py",
    "scripts/goal5780_independent_recount.py",
    "scripts/goal5780_build_evidence.py",
    "history/internal_docs/goal5780_rtbh_unchanged_route_profile_raw_20260814.json",
    "history/internal_docs/goal5780_rtbh_unchanged_route_profile_v3_20260814.json",
    "history/internal_docs/goal5780_rtbh_unchanged_route_profile_independent_recount_20260814.json",
    "history/internal_docs/goal5780_rt_barneshut_residual_causal_audit_result_20260814.json",
    "history/internal_docs/goal5780_rt_barneshut_residual_causal_audit_technical_report_20260814.md",
    "history/internal_docs/self_review_goal5780_rt_barneshut_residual_causal_audit_20260814.md",
    "history/internal_docs/call_for_review_goal5780_rt_barneshut_residual_causal_audit_20260814.md",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    payloads: list[tuple[str, bytes]] = []
    for relative in FILES:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        payloads.append((relative.replace("\\", "/"), path.read_bytes()))
    manifest = {
        "schema": "rtdl.goal5780.evidence_manifest.v1",
        "payload_count": len(payloads),
        "payload_bytes": sum(len(data) for _, data in payloads),
        "members": [
            {"path": path, "bytes": len(data), "sha256": _sha(data)}
            for path, data in payloads
        ],
        "manifest_self_referential": False,
    }
    manifest_data = (json.dumps(
        manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
    archive_buffer = io.BytesIO()
    with tarfile.open(fileobj=archive_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path, data in payloads + [("MANIFEST.json", manifest_data)]:
            info = tarfile.TarInfo(path)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as zipped:
            zipped.write(archive_buffer.getvalue())
    print(json.dumps({
        "archive": str(args.output),
        "sha256": _sha(args.output.read_bytes()),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
