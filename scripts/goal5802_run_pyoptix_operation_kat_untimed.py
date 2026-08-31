#!/usr/bin/env python3
"""Run the PyOptiX operation guard only as an untimed preworker KAT.

The comparative path deliberately does not monkeypatch CuPy or allocate a
forensic observer.  This KAT executes the same reviewed owner methods before
worker zero, checks both first-input materialization and cache reuse, and emits
a create-only receipt for the target runtime manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from experiments.goal5802_premeasurement.pyoptix_scalar_arm import (
    DeviceStatusFailure,
    PyOptixScalarAdapter,
    validate_scalar_execute_source,
)
from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    digest,
    relation_k_plus_one_workload,
    relation_workload,
    triangle_workload,
)


EXPECTED_GUARD = {
    "scope": "PYTHON_VISIBLE_TASK_OWNER_EXECUTE__NOT_CUPTI_OR_DRIVER_WIDE",
    "unapproved_device_allocation_call_count": 0,
    "unapproved_pinned_host_allocation_call_count": 0,
    "unapproved_blocking_asnumpy_call_count": 0,
    "unauthorized_direct_stream_sync_count": 0,
    "complete_driver_operation_observation_claimed": False,
}


def _projection(result: dict[str, object], *, first: bool, relation: bool) \
        -> dict[str, object]:
    guard = result.get("independent_execute_guard")
    dynamic = result.get("dynamic_input_receipt")
    if guard != EXPECTED_GUARD or result.get(
            "live_execute_guard_inside_timer") is not True:
        raise RuntimeError("untimed PyOptiX operation guard did not hold")
    if not isinstance(dynamic, dict):
        raise RuntimeError("untimed PyOptiX dynamic receipt absent")
    expected_reuse = not first
    if dynamic.get("prepared_input_reused") is not expected_reuse \
            or dynamic.get("dynamic_input_generation") != 1 \
            or dynamic.get("dynamic_explicit_sync_count") != 0 \
            or dynamic.get("dynamic_blocking_upload_call_count") != 0:
        raise RuntimeError("untimed PyOptiX dynamic lifecycle differs")
    if first:
        if not isinstance(dynamic.get("dynamic_device_upload_call_count"), int) \
                or dynamic["dynamic_device_upload_call_count"] <= 0 \
                or not isinstance(dynamic.get("dynamic_device_upload_bytes"), int) \
                or dynamic["dynamic_device_upload_bytes"] <= 0 \
                or dynamic.get("dynamic_accel_build_count") != (1 if relation else 0):
            raise RuntimeError("untimed PyOptiX first input was not materialized")
    elif any(dynamic.get(key) != 0 for key in (
            "dynamic_device_upload_call_count", "dynamic_device_upload_bytes",
            "dynamic_accel_build_count", "dynamic_explicit_sync_count",
            "dynamic_blocking_upload_call_count")):
        raise RuntimeError("untimed PyOptiX reuse performed setup work")
    return {
        "independent_execute_guard": guard,
        "dynamic_input_receipt": dynamic,
        "execute_operation_counts": result.get("execute_operation_counts"),
        "operation_order": result.get("operation_order"),
        "prepare_operation_counts": result.get("prepare_operation_counts"),
        "live_execute_guard_inside_timer": True,
    }


def _relation_k_plus_one_failure(
        *, ptx: Path, compaction_cubin: Path) -> dict[str, object]:
    workload = relation_k_plus_one_workload()
    adapter = PyOptixScalarAdapter(
        RELATION_TASK, workload, ptx_path=ptx,
        compaction_cubin_path=compaction_cubin,
        record_operation_evidence=True)
    adapter.load()
    try:
        adapter.prepare()
        try:
            adapter.execute_with_operation_guard()
        except DeviceStatusFailure as failure:
            evidence = dict(failure.evidence)
        else:
            raise RuntimeError(
                "PyOptiX K+1 semantic-capacity workload unexpectedly succeeded")
        owner = adapter.owner
        if owner is None or not isinstance(getattr(owner, "params", None), tuple) \
                or len(owner.params) != 2:
            raise RuntimeError("PyOptiX K+1 executed parameters absent")
        projections = []
        for params in owner.params:
            row = params[0]
            overlap = float(row["minimum_overlap"])
            projections.append({
                "minimum_overlap_f32_bits": struct.unpack(
                    "<I", struct.pack("<f", overlap))[0],
                "semantic_capacity": int(row["reserved0"]),
                "raw_capacity": int(row["raw_row_capacity"]),
            })
        if len({json.dumps(item, sort_keys=True) for item in projections}) != 1:
            raise RuntimeError("PyOptiX K+1 orientation parameters differ")
        executed_parameter_projection = {
            "orientation_count": len(projections), **projections[0]}
    finally:
        adapter.close()
    expected = dict(workload["expected_failure"])
    observed_control = {
        "raw_event_count": evidence.get("raw_event_count"),
        "unique_event_count": evidence.get("semantic_unique_count"),
        "overflowed": evidence.get("device_overflow"),
        "status": evidence.get("device_status"),
        "semantic_capacity": evidence.get("semantic_capacity"),
        "raw_capacity": evidence.get("raw_capacity"),
        "control_d2h_bytes": 16,
    }
    expected_control = {
        key: expected[key] for key in (
            "raw_event_count", "unique_event_count", "overflowed", "status",
            "semantic_capacity", "raw_capacity", "control_d2h_bytes")}
    expected_order = [
        "control_reset", "max_key_reset", "unique_count_reset",
        "keys_fill_ff", "params0_h2d", "launch0", "params1_h2d",
        "launch1", "semantic_compaction", "unique_count_d2d",
        "control_d2h", "status_ready_sync",
    ]
    counts = evidence.get("execute_operation_counts")
    if observed_control != expected_control \
            or executed_parameter_projection != {
                "orientation_count": 2,
                "minimum_overlap_f32_bits": 0x3f800000,
                "semantic_capacity": 4096,
                "raw_capacity": 8192,
            } \
            or evidence.get("application_output_exposed") is not False \
            or evidence.get("application_output_d2h_call_count") != 0 \
            or evidence.get("status_output_commit_blocking_boundary_count") != 1 \
            or evidence.get("independent_execute_guard") != EXPECTED_GUARD \
            or evidence.get("operation_order") != expected_order \
            or not isinstance(counts, dict) \
            or counts.get("execute_async_d2h_call_count") != 1 \
            or counts.get("execute_explicit_stream_sync_call_count") != 1 \
            or counts.get("execute_launch_call_count") != 3:
        raise RuntimeError({"PyOptiX K+1 evidence differs": evidence})
    return {
        "schema": "rtdl.goal5802.relation_k_plus_one_device_failure.v1",
        "arm": "B_NVIDIA_PYOPTIX_9_1_SOURCE_OPTIX_9_0_COMPAT_SCALAR_ONLY",
        "task": RELATION_TASK,
        "workload_sha256": workload["workload_sha256"],
        "packed_input_sha256": workload["packed_input_sha256"],
        "indexed_count": len(workload["indexed"]),
        "source_count": len(workload["sources"]),
        "raw_count_below_raw_capacity": True,
        "compact_control": observed_control,
        "executed_parameter_projection": executed_parameter_projection,
        "status_output_commit_blocking_boundary_count": 1,
        "application_output_exposed": False,
        "application_output_d2h_call_count": 0,
        "application_output_d2h_bytes": 0,
        "operation_order": expected_order,
        "execute_operation_counts": counts,
        "independent_execute_guard": EXPECTED_GUARD,
        "dynamic_input_receipt": evidence.get("dynamic_input_receipt"),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ptx", type=Path, required=True)
    parser.add_argument("--compaction-cubin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    rows = []
    for task, workload in (
            (RELATION_TASK, relation_workload()),
            (TRIANGLE_TASK, triangle_workload())):
        adapter = PyOptixScalarAdapter(
            task, workload, ptx_path=args.ptx,
            compaction_cubin_path=(
                args.compaction_cubin if task == RELATION_TASK else None),
            record_operation_evidence=True)
        adapter.load()
        try:
            adapter.prepare()
            first = adapter.execute_with_operation_guard()
            second = adapter.execute_with_operation_guard()
            rows.append({
                "task": task,
                "first_execute": _projection(
                    first, first=True, relation=task == RELATION_TASK),
                "reused_execute": _projection(
                    second, first=False, relation=task == RELATION_TASK),
                "runtime_identity": adapter.runtime_identity(),
            })
        finally:
            adapter.close()
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.pyoptix_operation_guard_untimed_kat.v1",
        "status": "PASS__UNTIMED_PREWORKER_OPERATION_GUARD",
        "rows": rows,
        "task_count": 2,
        "guard_inside_comparative_timer": False,
        "source_boundary": validate_scalar_execute_source(),
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        # Two executions per task: relation is two OptiX launches plus one
        # semantic-compaction CUDA launch; triangle is one OptiX launch.
        "untimed_optix_launch_count": 8,
        "untimed_auxiliary_cuda_kernel_launch_count": 3,
        "untimed_gpu_launch_count": 11,
        "relation_k_plus_one_hostile": _relation_k_plus_one_failure(
            ptx=args.ptx, compaction_cubin=args.compaction_cubin),
    }
    value["receipt_sha256"] = digest(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
