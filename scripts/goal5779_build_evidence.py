#!/usr/bin/env python3
"""Build deterministic, self-manifested Goal5779 evidence archives."""

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
    "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json",
    "history/internal_docs/goal5779_stage_a_v3_generated_vs_handwritten_freeze_20260814.json",
    "history/internal_docs/goal5779_stage_a_v2_generated_vs_handwritten_freeze_20260814.json",
    "history/internal_docs/goal5779_stage_a_generated_vs_handwritten_freeze_20260814.json",
    "history/internal_docs/goal5779_stage_a_repeat_diagnostic_20260814.json",
    "history/internal_docs/goal5779_stage_b_s1_partial_failure_20260814.json",
    "history/internal_docs/goal5779_stage_b_s1_partial_failure_20260814.log",
    "history/internal_docs/goal5779_generated_vs_handwritten_device_audit_result_20260814.json",
    "history/internal_docs/goal5779_generated_vs_handwritten_device_audit_independent_recount_20260814.json",
    "history/internal_docs/goal5779_generated_vs_handwritten_device_audit_independent_recount_v2_20260814.json",
    "history/internal_docs/goal5779_generated_vs_handwritten_device_audit_independent_recount_v3_20260814.json",
    "history/internal_docs/goal5779_executed_stage_b_device_audit_20260814.py",
    "history/internal_docs/goal5779_home_librtdl_optix.so",
    "history/internal_docs/goal5779_generated_vs_handwritten_device_audit_technical_report_20260814.md",
    "history/internal_docs/self_review_goal5779_generated_vs_handwritten_device_audit_20260814.md",
    "history/internal_docs/call_for_review_goal5779_generated_vs_handwritten_device_audit_20260814.md",
    "scripts/goal5779_stage_a_freeze.py",
    "scripts/goal5779_handwritten_leaf_controls.py",
    "scripts/goal5779_stage_b_device_audit.py",
    "scripts/goal5779_independent_recount.py",
    "scripts/goal5779_build_evidence.py",
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_spatial_candidate_callback.py",
    "src/rtdsl/v4_multiround_spatial_optix_compiler.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_workloads.cpp",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_bytes(tar: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(data); info.mtime = 0; info.mode = 0o644
    info.uid = 0; info.gid = 0; info.uname = ""; info.gname = ""
    tar.addfile(info, io.BytesIO(data))


def build(root: Path, output: Path) -> dict[str, object]:
    payloads = []
    content = {}
    for name in FILES:
        data = (root / name).read_bytes()
        content[name] = data
        payloads.append({"path": name, "bytes": len(data), "sha256": sha(data)})
    manifest = {
        "schema": "rtdl.goal5779.evidence_manifest.v1", "goal": 5779,
        "payload_count": len(payloads),
        "payload_bytes": sum(x["bytes"] for x in payloads),
        "payloads": payloads,
        "manifest_self_included": False,
    }
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0,
                           compresslevel=9) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for name in sorted(content):
                    add_bytes(tar, name, content[name])
                add_bytes(tar, "GOAL5779_EVIDENCE_MANIFEST.json", manifest_data)
    return {"archive": str(output.resolve()), "sha256": sha(output.read_bytes()),
            **{key: manifest[key] for key in ("payload_count", "payload_bytes")}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build(Path(args.root).resolve(), Path(args.output).resolve()),
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
