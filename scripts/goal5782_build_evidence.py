#!/usr/bin/env python3
"""Build deterministic, non-self-referential Goal5782 evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5782_unified_v4_candidate_evidence_20260814.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5782_unified_v4_candidate_evidence_twin_20260814.tar.gz"


FILES = (
    "history/internal_docs/review_v4_cgo_next_stage_plan_after_goal5776_20260814.md",
    "history/internal_docs/v4_cgo_next_stage_plan_owner_returned_external_review_absorption_20260814.json",
    "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json",
    "history/internal_docs/v4_post_goal5779_5781_mandatory_decision_register_20260814.json",
    "history/internal_docs/goal5779_generated_vs_handwritten_device_audit_result_20260814.json",
    "history/internal_docs/goal5780_rt_barneshut_residual_causal_audit_result_20260814.json",
    "history/internal_docs/goal5781_cold_compiler_preparation_architecture_audit_result_20260814.json",
    "history/internal_docs/goal5782_unified_v4_performance_candidate_and_home_closure_result_20260814.json",
    "history/internal_docs/goal5782_unified_v4_performance_candidate_and_home_closure_technical_report_20260814.md",
    "history/internal_docs/self_review_goal5782_unified_v4_performance_candidate_and_home_closure_20260814.md",
    "history/internal_docs/goal5782_portable_candidate_lineages_20260814.json",
    "history/internal_docs/goal5782_rtbh_candidate_profile_home_20260814.json",
    "history/internal_docs/goal5782_rtbh_candidate_profile_home_final_20260814.json",
    "history/internal_docs/goal5782_hierarchy_functional_home_20260814.json",
    "history/internal_docs/goal5782_checked_reduction_home_20260814.json",
    "history/internal_docs/goal5782_triangle_reduction_home_20260814.json",
    "history/internal_docs/goal5782_nine_app_functional_home_recount_20260814.json",
    "history/internal_docs/goal5782_home_clean_validation_v5_independent_local_recount_20260814.json",
    "history/internal_docs/goal5782_local_functional_candidate_v5_20260814.tar.gz",
    "history/internal_docs/goal5782_portable_source_v5_20260814.tar.gz",
    "src/rtdsl/v4_checked_u64_device_reduction.py",
    "src/rtdsl/v4_triangle_reduction_device_runtime.py",
    "src/rtdsl/aggregate_hierarchy_native.py",
    "src/rtdsl/v4_hierarchy_frontier.py",
    "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    "scripts/goal5782_build_portable_candidate.py",
    "scripts/goal5782_home_clean_validate.py",
    "scripts/goal5782_recount_home_functional.py",
    "tests/goal5782_canonical_packed_hierarchy_binding_test.py",
    "tests/goal5778_v4_checked_u64_device_reduction_test.py",
)
DIRECTORIES = (
    "history/internal_docs/goal5782_nine_app_functional_home_raw_20260814",
    "history/internal_docs/goal5782_home_clean_validation_v5_20260814",
    "history/internal_docs/goal5782_preclosure_lineages_20260814",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return output.getvalue()


def main() -> None:
    if OUT.exists() or TWIN.exists():
        raise FileExistsError("Goal5782 evidence output exists")
    names: set[str] = set(FILES)
    for directory_name in DIRECTORIES:
        directory = ROOT / directory_name
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        names.update(
            path.relative_to(ROOT).as_posix()
            for path in directory.rglob("*") if path.is_file())
    payloads: dict[str, bytes] = {}
    for name in sorted(names):
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if any(part in (".codex", ".git", "__pycache__") for part in Path(name).parts):
            raise RuntimeError(f"private/cache evidence member: {name}")
        payloads[name] = path.read_bytes()
    rows = [{"path": name, "sha256": digest(data), "size_bytes": len(data)}
            for name, data in sorted(payloads.items())]
    manifest = (json.dumps({
        "schema": "rtdl.goal5782.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "manifest_is_not_a_payload": True,
        "payloads": rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    final = archive({**payloads, "GOAL5782_EVIDENCE_MANIFEST.json": manifest})
    OUT.write_bytes(final)
    TWIN.write_bytes(final)
    if OUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("Goal5782 evidence twin differs")
    print(json.dumps({
        "archive_sha256": digest(final),
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
