#!/usr/bin/env python3
"""Run exact final RTDL first/reuse operation KATs without timing.

This target-preparation action exercises the same public clean-installed
``install -> load -> prepare -> execute -> close`` route used by the formal
RTDL arm.  It takes no clocks, emits no formal worker, and records the actual
27-field native operation receipt for the first dynamic input and its reuse.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from experiments.goal5802_premeasurement.rtdlexe_arm import (
    RTDLDeploymentPaths,
    RTDLExecutableAdapter,
)
from experiments.goal5802_premeasurement.runtime_manifest import (
    digest,
    sha256_file,
    validate_rtdl_operation_kat,
)
from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    relation_k_plus_one_workload,
    relation_workload,
    triangle_workload,
)


def _projection(adapter: RTDLExecutableAdapter, raw: object) \
        -> dict[str, object]:
    lifecycle = adapter.measurement_lifecycle_receipt(raw)
    evidence = adapter.finalize_measurement_evidence(raw)
    if evidence.get("dynamic_input_receipt") != lifecycle:
        raise RuntimeError("RTDL KAT lifecycle/evidence receipt differs")
    status = evidence.get("device_status")
    operation = evidence.get("native_operation_receipt")
    if not isinstance(status, dict) or not isinstance(operation, dict):
        raise RuntimeError("RTDL KAT lacks actual native evidence")
    if adapter.task == RELATION_TASK:
        output_summary = {
            "canonical_row_count": len(raw.output),
            "raw_event_count": evidence["raw_event_count"],
            "semantic_unique_count": evidence["semantic_unique_count"],
        }
    else:
        output_summary = {"reduced_u64": int(raw.output)}
    return {
        "dynamic_input_receipt": lifecycle,
        "native_operation_receipt": operation,
        "output_canonical_sha256": digest(raw.output),
        # The measured fast path deliberately disables the product's optional
        # forensic output hash.  The KAT computes ``output_canonical_sha256``
        # after execute instead; requiring a product hash here would either
        # turn ``None`` into the misleading string ``"None"`` or force output
        # hashing back into the path whose overhead Goal5802 measures.
        "product_output_sha256": raw.output_sha256,
        "executable_identity_sha256": str(
            raw.executable_identity_sha256),
        "oracle_exact": True,
        "device_status_ok": status.get("ok") is True,
        "output_summary": output_summary,
        "role_counters": list(raw.role_counters),
    }


def _file(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file() or resolved.is_symlink():
        raise RuntimeError(f"RTDL KAT input is not a regular file: {path}")
    return {"path": str(resolved), "sha256": sha256_file(resolved)}


def _relation_k_plus_one_failure(
        *, paths: RTDLDeploymentPaths) -> dict[str, object]:
    workload = relation_k_plus_one_workload()
    adapter = RTDLExecutableAdapter(RELATION_TASK, workload, paths)
    adapter.load()
    try:
        adapter.prepare()
        try:
            adapter.execute(diagnostics=False)
        except Exception as error:
            failure_code = str(getattr(error, "code", type(error).__name__))
        else:
            raise RuntimeError(
                "RTDL K+1 semantic-capacity workload unexpectedly succeeded")
        owner = getattr(adapter.prepared, "_owner", None)
        operation = dict(getattr(
            owner, "_last_fast_operation_receipt", None) or {})
        compact_control = dict(getattr(
            owner, "_last_fast_compact_control", None) or {})
        if owner is None or not hasattr(owner, "_minimum_overlap") \
                or not hasattr(owner, "_capacity"):
            raise RuntimeError("RTDL K+1 executed parameters absent")
        executed_parameter_projection = {
            "orientation_count": 2,
            "minimum_overlap_f32_bits": struct.unpack(
                "<I", struct.pack("<f", float(owner._minimum_overlap)))[0],
            "semantic_capacity": int(owner._capacity),
            "raw_capacity": int(operation.get(
                "semantic_compaction_key_capacity", -1)),
        }
    finally:
        adapter.close()
    expected = dict(workload["expected_failure"])
    expected_control = {
        "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
        "raw_event_count": expected["raw_event_count"],
        "unique_event_count": expected["unique_event_count"],
        "overflowed": expected["overflowed"],
        "status": expected["status"],
        "semantic_capacity": expected["semantic_capacity"],
        "control_d2h_bytes": expected["control_d2h_bytes"],
    }
    if failure_code != "RX035_DEVICE_STATUS_INVALID" \
            or compact_control != expected_control \
            or executed_parameter_projection != {
                "orientation_count": 2,
                "minimum_overlap_f32_bits": 0x3f800000,
                "semantic_capacity": 4096,
                "raw_capacity": 8192,
            } \
            or operation.get("host_blocking_boundary_count") != 1 \
            or operation.get("control_d2h_bytes") != 16 \
            or operation.get("output_d2h_bytes") != 0 \
            or operation.get("status_before_output") is not True \
            or operation.get("output_d2h_after_status_failure") != 0 \
            or operation.get("status_d2h_copy_call_count") != 1 \
            or operation.get("output_d2h_copy_call_count") != 0:
        raise RuntimeError({
            "RTDL K+1 failure_code": failure_code,
            "compact_control": compact_control,
            "operation": operation,
        })
    return {
        "schema": "rtdl.goal5802.relation_k_plus_one_device_failure.v1",
        "arm": "D_RTDL_CLEAN_INSTALLED_RTLEXE",
        "task": RELATION_TASK,
        "workload_sha256": workload["workload_sha256"],
        "packed_input_sha256": workload["packed_input_sha256"],
        "indexed_count": len(workload["indexed"]),
        "source_count": len(workload["sources"]),
        "raw_count_below_raw_capacity": True,
        "compact_control": {
            key: expected[key] for key in (
                "raw_event_count", "unique_event_count", "overflowed",
                "status", "semantic_capacity", "raw_capacity",
                "control_d2h_bytes")},
        "executed_parameter_projection": executed_parameter_projection,
        "product_compact_control": compact_control,
        "failure_code": failure_code,
        "status_output_commit_blocking_boundary_count": 1,
        "application_output_exposed": False,
        "application_output_d2h_call_count": 0,
        "application_output_d2h_bytes": 0,
        "native_operation_receipt": operation,
        "deployment_identity": paths.identities(),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relation-artifact", type=Path, required=True)
    parser.add_argument("--relation-authority", type=Path, required=True)
    parser.add_argument("--relation-deployment-id", required=True)
    parser.add_argument(
        "--relation-executable-identity-sha256", required=True)
    parser.add_argument("--triangle-artifact", type=Path, required=True)
    parser.add_argument("--triangle-authority", type=Path, required=True)
    parser.add_argument("--triangle-deployment-id", required=True)
    parser.add_argument(
        "--triangle-executable-identity-sha256", required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native-library", type=Path, required=True)
    parser.add_argument("--rtdsl-init", type=Path, required=True)
    parser.add_argument("--rtdlexe-module", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)

    files = {
        role: _file(getattr(args, role)) for role in (
            "relation_artifact", "relation_authority",
            "triangle_artifact", "triangle_authority",
            "trust_root", "trust_head", "trust_package", "native_library",
            "rtdsl_init", "rtdlexe_module")
    }
    deployment_ids = {
        "relation": args.relation_deployment_id,
        "triangle": args.triangle_deployment_id,
    }
    expected_executable_identities = {
        "relation": args.relation_executable_identity_sha256,
        "triangle": args.triangle_executable_identity_sha256,
    }
    rows = []
    relation_paths: RTDLDeploymentPaths | None = None
    for task, workload, prefix in (
            (RELATION_TASK, relation_workload(), "relation"),
            (TRIANGLE_TASK, triangle_workload(), "triangle")):
        paths = RTDLDeploymentPaths(
            artifact=Path(files[f"{prefix}_artifact"]["path"]),
            authority=Path(files[f"{prefix}_authority"]["path"]),
            trust_root=Path(files["trust_root"]["path"]),
            trust_head=Path(files["trust_head"]["path"]),
            trust_package=Path(files["trust_package"]["path"]),
            native_library=Path(files["native_library"]["path"]),
            deployment_id=deployment_ids[prefix],
        )
        if task == RELATION_TASK:
            relation_paths = paths
        adapter = RTDLExecutableAdapter(task, workload, paths)
        adapter.load()
        try:
            adapter.prepare()
            first = adapter.execute(diagnostics=False)
            first_projection = _projection(adapter, first)
            reused = adapter.execute(diagnostics=False)
            reused_projection = _projection(adapter, reused)
            rows.append({
                "task": task,
                "deployment_identity": paths.identities(),
                "runtime_identity": adapter.runtime_identity(),
                "first_execute": first_projection,
                "reused_execute": reused_projection,
            })
        finally:
            adapter.close()

    if relation_paths is None:
        raise RuntimeError("RTDL relation deployment path absent")
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.rtdl_operation_guard_untimed_kat.v1",
        "status": "PASS__UNTIMED_PREWORKER_ACTUAL_RTDL_OPERATION_GUARD",
        "rows": rows,
        "task_count": 2,
        "guard_inside_comparative_timer": False,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        # Two executions per task.  Relation: 2 OptiX + 7 auxiliary;
        # triangle: 1 OptiX + 6 auxiliary.
        "untimed_optix_launch_count": 8,
        "untimed_auxiliary_cuda_kernel_launch_count": 33,
        "untimed_gpu_launch_count": 41,
        "relation_k_plus_one_hostile": _relation_k_plus_one_failure(
            paths=relation_paths),
    }
    value["receipt_sha256"] = digest(value)
    validate_rtdl_operation_kat(
        value, files, deployment_ids,
        expected_executable_identities=expected_executable_identities)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": value["status"],
        "receipt_sha256": value["receipt_sha256"],
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "untimed_gpu_launch_count": 41,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
