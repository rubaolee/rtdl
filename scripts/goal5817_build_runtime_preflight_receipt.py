#!/usr/bin/env python3
"""Bind the six live untimed KATs into the Direct-worker compatibility gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5817_three_arm.protocol import digest, file_record


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5817 JSON root differs: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kat-manifest", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    kat_path = args.kat_manifest.resolve(strict=True)
    runtime_path = args.runtime_manifest.resolve(strict=True)
    output = args.output.absolute()
    if output.exists():
        raise RuntimeError("Goal5817 preflight receipt output already exists")
    kat = _read(kat_path)
    unsigned_kat = dict(kat)
    kat_seal = unsigned_kat.pop("kat_manifest_sha256", None)
    rows = kat.get("rows")
    if kat.get("schema") != "rtdl.goal5817.target_untimed_kat_manifest.v1" \
            or kat.get("status") != (
                "PASS__ALL_SIX_ARM_TASK_KATS__FORMAL_WORKER_ZERO") \
            or kat_seal != digest(unsigned_kat) \
            or not isinstance(rows, list) or len(rows) != 6:
        raise RuntimeError("Goal5817 KAT manifest differs")
    expected = {(arm, task) for arm in ("DIRECT", "PYOPTIX", "RTDL")
                for task in ("relation", "triangle")}
    observed = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("Goal5817 KAT row differs")
        observed.add((row.get("arm"), row.get("task")))
        record = row.get("file")
        if not isinstance(record, dict) \
                or record != file_record(Path(str(record.get("path")))):
            raise RuntimeError("Goal5817 KAT payload identity differs")
    if observed != expected:
        raise RuntimeError("Goal5817 KAT arm/task universe differs")
    runtime_record = file_record(runtime_path)
    base = {
        "schema": "rtdl.goal5802.formal_runtime_preflight.v1",
        "status": "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO",
        "runtime_manifest_file_sha256": runtime_record["sha256"],
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "goal5817_kat_manifest_file": file_record(kat_path),
        "goal5817_runtime_manifest_file": runtime_record,
        "compatibility_tail": "GOAL5817_LIVE_SIX_KAT_BINDING",
    }
    seal = digest(base)
    # Preserve this insertion order: the inherited Direct worker checks the
    # exact pretty-printed lines and requires a trailing comma on every legacy
    # field. New Goal5817 fields follow those legacy fields.
    value = {
        "schema": base["schema"],
        "status": base["status"],
        "runtime_manifest_file_sha256": base["runtime_manifest_file_sha256"],
        "preflight_sha256": seal,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "goal5817_kat_manifest_file": base["goal5817_kat_manifest_file"],
        "goal5817_runtime_manifest_file": base["goal5817_runtime_manifest_file"],
        "compatibility_tail": base["compatibility_tail"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        json.dumps(value, indent=2, allow_nan=False).encode("utf-8") + b"\n")
    text = output.read_text(encoding="utf-8")
    for literal in (
        '  "schema": "rtdl.goal5802.formal_runtime_preflight.v1",',
        '  "status": "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO",',
        f'  "runtime_manifest_file_sha256": "{runtime_record["sha256"]}",',
        f'  "preflight_sha256": "{seal}",',
        '  "clock_read_count": 0,',
        '  "registered_performance_timing_count": 0,',
        '  "gpu_kernel_launch_count": 0,',
        '  "formal_worker_count": 0,',
    ):
        if f"\n{literal}\n" not in f"\n{text}":
            raise RuntimeError(f"Goal5817 inherited Direct gate line absent: {literal}")
    print(json.dumps({
        "status": value["status"],
        "preflight_sha256": seal,
        "preflight_file": file_record(output),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
