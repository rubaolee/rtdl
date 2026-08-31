#!/usr/bin/env python3
"""Build deterministic Goal5774 V2/V4 pre-POD evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5774_v2_v4_pre_pod_evidence_v2_20260813.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5774_v2_v4_pre_pod_evidence_v2_twin_20260813.tar.gz"

FILES = (
    "history/internal_docs/goal5774_v2_v4_pre_pod_bundle_v13_20260813.tar.gz",
    "history/internal_docs/goal5774_v2_v4_pre_pod_bundle_v13_twin_20260813.tar.gz",
    "history/internal_docs/goal5774_home_create_only_authority_v13_20260813.json",
    "history/internal_docs/goal5774_v4_prepared_three_way_performance_plan_20260813.md",
    "history/internal_docs/self_review_goal5774_prepared_three_way_performance_plan_20260813.md",
    "history/internal_docs/goal5774_prepared_comparator_eligibility_audit_20260813.json",
    "history/internal_docs/goal5774_development_lineages_20260813.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/EXECUTION_SOURCE.tar.gz",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/librtdl_optix.so",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/PREPARED.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/PLAN.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/RUNTIME.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/REMATERIALIZATION.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/FIXED_RADIUS_REFINEMENT_EVIDENCE.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/TARGET_FUNCTIONAL_RESULT.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/result/TARGET_FUNCTIONAL_RECOUNT.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/WINDOWS_INDEPENDENT_RECOUNT.json",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/logs/build.log",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/logs/goal5774_tests.log",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/logs/rematerialization.log",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/logs/target_functional.log",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/logs/target_recount.log",
    "history/internal_docs/goal5774_home_clean_prepare_v13_20260813/logs/versions.log",
    "scripts/goal5774_build_v2_v4_pre_pod_bundle.py",
    "scripts/goal5774_target_prepare.py",
    "scripts/goal5774_prepared_three_way_frontdoors.py",
    "scripts/goal5774_prepared_v2_v4_worker.py",
    "scripts/goal5774_prepared_v2_v4_controller.py",
    "scripts/goal5774_evaluate_prepared_v2_v4.py",
    "scripts/goal5774_recount_prepared_v2_v4_raw.py",
    "scripts/goal5774_recount_home_v2_v4_prepared.py",
    "tests/goal5774_v2_v4_prepared_frontdoors_test.py",
    "tests/goal5774_v2_v4_formal_harness_test.py"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as gz:
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
    for path in (OUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
    payloads = {name: (ROOT / name).read_bytes() for name in FILES}
    rows = [
        {"path": name, "sha256": sha(data), "size_bytes": len(data)}
        for name, data in sorted(payloads.items())
    ]
    manifest = {
        "schema": "rtdl.goal5774.v2_v4_pre_pod_evidence_manifest.v1",
        "goal": 5774,
        "scope": "v2_direct_versus_v4_only",
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "v3_required_or_executed": False,
    }
    payloads["MANIFEST.json"] = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode()
    data = archive(payloads)
    OUT.write_bytes(data)
    TWIN.write_bytes(data)
    if OUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("Goal5774 evidence twin differs")
    print(json.dumps({
        "evidence_sha256": sha(data),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
