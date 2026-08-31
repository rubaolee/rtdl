#!/usr/bin/env python3
"""Build the deterministic exact Goal5798 RTX 4000 Ada POD candidate."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v5.json"
FREEZE = ROOT / "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v4_20260823.json"
RUNNER = ROOT / "scripts/goal5798_pod_prepare_and_run.sh"
OUTPUT = ROOT / "history/internal_docs/goal5798_formal_pod_candidate_v1_20260823.tar.gz"

SUPPORT = (
    "experiments/goal5798_premeasurement/runtime_manifest_v5.json",
    "history/internal_docs/goal5798_s0_matched_workload_authority_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v4_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_amendment_a1_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_amendment_a2_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_preaction_amendment_a3_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v3_20260823.json",
    "scripts/goal5798_bind_host.py",
    "scripts/goal5798_build_execution_authority.py",
    "scripts/goal5798_build_runtime_manifest.py",
    "scripts/goal5798_independent_recount.py",
    "tests/__init__.py",
    "tests/goal5798_formal_harness_test.py",
    "tests/goal5798_premeasurement_freeze_test.py",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    payloads: dict[str, bytes] = {}
    for row in runtime["files"]:
        relative = row["path"]
        data = (ROOT / relative).read_bytes()
        if len(data) != row["bytes"] or sha(data) != row["sha256"]:
            raise RuntimeError(f"runtime identity drift: {relative}")
        payloads[f"source/{relative}"] = data
    for relative in SUPPORT:
        payloads[f"source/{relative}"] = (ROOT / relative).read_bytes()
    payloads["RUN_GOAL5798.sh"] = RUNNER.read_bytes()
    manifest = {
        "schema": "rtdl.goal5798.formal_pod_candidate.v1",
        "status": "EXACT_POD_CANDIDATE__EXECUTION_REQUIRES_OWNER_ENV_LITERAL",
        "target": {
            "gpu_model": "NVIDIA RTX 4000 Ada Generation",
            "compute_capability": "8.9", "driver_branch_minimum": 590,
            "linux_non_wsl": True,
        },
        "freeze_file_sha256": sha(FREEZE.read_bytes()),
        "freeze_sha256": freeze["freeze_sha256"],
        "runtime_manifest_file_sha256": sha(RUNTIME.read_bytes()),
        "runtime_manifest_sha256": runtime["manifest_sha256"],
        "runtime_file_count": runtime["file_count"],
        "formal_schedule": {"memory_workers": 30, "performance_workers": 288},
        "authorization_environment_literal": "OWNER_AUTHORIZED_EXACT_GOAL5798=YES",
        "payloads": {
            name: {"bytes": len(data), "sha256": sha(data)}
            for name, data in sorted(payloads.items())
        },
    }
    payloads["MANIFEST.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    payloads["SHA256SUMS"] = "".join(
        f"{sha(data)}  {name}\n" for name, data in sorted(payloads.items())
    ).encode("utf-8")
    archive_bytes = io.BytesIO()
    with tarfile.open(fileobj=archive_bytes, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(payloads.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if name == "RUN_GOAL5798.sh" \
                or name.endswith("build_direct_measurement.sh") else 0o644
            archive.addfile(info, io.BytesIO(data))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            compressed.write(archive_bytes.getvalue())
    print(json.dumps({
        "status": "PASS", "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "bytes": OUTPUT.stat().st_size, "sha256": sha(OUTPUT.read_bytes()),
        "payload_count": len(payloads), "runtime_file_count": runtime["file_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

