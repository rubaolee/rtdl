#!/usr/bin/env python3
"""Build the deterministic Goal5798 portable performance successor."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v13.json"
FREEZE = ROOT / "history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json"
RUNNER = ROOT / "scripts/goal5798_portable_prepare_and_run.sh"
DEFAULT_OUTPUT = ROOT / "history/internal_docs/goal5798_portable_pod_candidate_v5_20260823.tar.gz"

SUPPORT = (
    "history/internal_docs/goal5798_a1_environment_portability_preaction_20260823.json",
    "history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json",
    "history/internal_docs/goal5798_s0_matched_workload_authority_20260823.json",
    "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v4_20260823.json",
    "scripts/goal5798_bind_host.py",
    "scripts/goal5798_build_execution_authority.py",
    "scripts/goal5798_independent_recount.py",
    "scripts/goal5798_portable_prepare_and_run.sh",
    "scripts/goal5798_validate_immutable_input_reuse.py",
    "scripts/goal5798_verify_v12_external_gate.py",
    "tests/__init__.py",
    "tests/goal5798_immutable_input_reuse_test.py",
    "tests/goal5798_portable_environment_test.py",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--runtime", type=Path, default=RUNTIME)
    parser.add_argument(
        "--schema",
        default="rtdl.goal5798.portable_pod_candidate.v5",
    )
    parser.add_argument(
        "--predecessor-sha256",
        default="97c4809840b1541a9b8b09965144627d456f34784145cb603aacb86cb8ff484f",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    runtime_path = args.runtime.resolve()
    try:
        runtime_relative = runtime_path.relative_to(ROOT.resolve()).as_posix()
    except ValueError as error:
        raise RuntimeError("runtime manifest must be inside the source root") from error
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
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
    payloads[f"source/{runtime_relative}"] = runtime_path.read_bytes()
    payloads["RUN_GOAL5798.sh"] = RUNNER.read_bytes()
    manifest = {
        "schema": args.schema,
        "status": "MODEL_AGNOSTIC_PERFORMANCE_SUCCESSOR__EXECUTION_REQUIRES_OWNER_LITERAL",
        "host_admission": {
            "gpu_model_filter": None,
            "compute_capability_filter": None,
            "vram_filter": None,
            "preferred_driver_filter": None,
            "underlying_supported_stack_floor": "NVIDIA OptiX 7.6 / driver 522.25",
            "stack_selection": freeze["stack_selection"],
            "compatible_stacks": freeze["compatible_stacks"],
        },
        "freeze_file_sha256": sha(FREEZE.read_bytes()),
        "freeze_sha256": freeze["freeze_sha256"],
        "runtime_manifest_file_sha256": sha(runtime_path.read_bytes()),
        "runtime_manifest_sha256": runtime["manifest_sha256"],
        "runtime_file_count": runtime["file_count"],
        "formal_schedule": {"memory_workers": 30, "performance_workers": 288},
        "authorization_environment_literal": "OWNER_AUTHORIZED_GOAL5798_PORTABLE=YES",
        "predecessor_candidate_sha256": args.predecessor_sha256,
        "claim_boundary": {
            "predecessor_formal_result_replaced": False,
            "successor_formal_performance_worker_count": 0,
            "engineering_diagnostics_are_formal": False,
        },
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
    with tarfile.open(
            fileobj=archive_bytes, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(payloads.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if name == "RUN_GOAL5798.sh" \
                or name.endswith("build_direct_measurement.sh") else 0o644
            archive.addfile(info, io.BytesIO(data))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            compressed.write(archive_bytes.getvalue())
    try:
        display_path = output.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        display_path = output.as_posix()
    print(json.dumps({
        "status": "PASS",
        "path": display_path,
        "bytes": output.stat().st_size,
        "sha256": sha(output.read_bytes()),
        "payload_count": len(payloads),
        "runtime_file_count": runtime["file_count"],
        "gpu_model_filter": None,
        "preferred_driver_filter": None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
