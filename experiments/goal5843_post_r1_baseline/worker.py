"""PyOptiX and public RTDL subworkers for Goal5843."""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from experiments.goal5842_causal_admission.baseline_worker import (
    measured,
    run_pyoptix,
    verify_public_output,
)
from experiments.goal5842_causal_admission.tasks import build_task, program_signature

from .contracts import (
    FIRST_MODE,
    MODES,
    PYOPTIX_ARM,
    RELATION_TASK,
    RTDL_ARM,
    STEADY_MODE,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    SUBWORKER_SCHEMA,
    TRIANGLE_TASK,
    digest,
    schedule_row,
    task_contract,
)
from .runtime import (
    bind_authorized_native_library,
    create_json,
    load_execution_authority,
    require_bound_path,
)


ROOT = Path(__file__).resolve().parents[2]


def _plain_json_mapping(value: object, *, label: str) -> dict[str, Any]:
    def thaw(item: object, path: str) -> object:
        if isinstance(item, Mapping):
            result: dict[str, object] = {}
            for key, nested in item.items():
                if not isinstance(key, str):
                    raise RuntimeError(f"{label} has a non-string key at {path}")
                result[key] = thaw(nested, f"{path}.{key}")
            return result
        if isinstance(item, (list, tuple)):
            return [thaw(nested, f"{path}[]") for nested in item]
        if item is None or isinstance(item, (str, int, float, bool)):
            return item
        raise RuntimeError(f"{label} has a non-JSON value at {path}")

    result = thaw(value, label)
    if not isinstance(result, dict):
        raise RuntimeError(f"{label} must be a mapping")
    return result


def _provider_execution_boundary(prepared: object) -> dict[str, Any]:
    receipt = getattr(prepared, "lifecycle_receipt", None)
    if not isinstance(receipt, Mapping):
        raise RuntimeError("RTDL generic lifecycle receipt missing")
    if receipt.get("schema") != "rtdl.generic_family_lifecycle.v1":
        raise RuntimeError("RTDL generic lifecycle receipt schema mismatch")
    provider = receipt.get("provider_receipt")
    if not isinstance(provider, Mapping):
        raise RuntimeError("RTDL provider lifecycle receipt missing")
    if provider.get("schema") != "rtdl.v4.public_protocol_lifecycle.v1":
        raise RuntimeError("RTDL provider lifecycle receipt schema mismatch")
    boundary = provider.get("provider_execution")
    return _plain_json_mapping(
        boundary, label="RTDL provider execution boundary"
    )


def _rtdl_public_value(task_id: str, result: object) -> object:
    output = getattr(result, "output", None)
    if task_id == RELATION_TASK:
        try:
            rows = tuple(tuple(int(item) for item in row) for row in output)
        except (TypeError, ValueError) as exc:
            raise RuntimeError("RTDL relation public output is not canonical rows") from exc
        return {"output": rows}
    if task_id == TRIANGLE_TASK:
        if hasattr(result, "details"):
            raise RuntimeError("generic RTDL result exposed provider diagnostic details")
        if type(output) is not int:
            raise RuntimeError("RTDL triangle public output is not an exact integer scalar")
        return output
    raise RuntimeError(f"unsupported RTDL Goal5843 task: {task_id}")


def _validate_rtdl_triangle_boundary(
    boundary: object, *, mode: str, prereg: dict[str, Any]
) -> dict[str, Any]:
    boundary = _plain_json_mapping(
        boundary, label="RTDL triangle execution boundary"
    )
    gate = prereg["rtdl_triangle_receipt_gate"]
    exact = {
        "schema": "rtdl.v4.triangle_reduction_execution_boundary.v1",
        "execution_path": gate["execution_path"],
        "prepared_query_input_reused": mode == STEADY_MODE,
        "per_ray_u64_materialized_on_host": gate["per_ray_u64_materialized_on_host"],
        "event_rows_materialized_on_host": gate["event_rows_materialized_on_host"],
        "public_output_scalar_bytes": gate["public_output_scalar_bytes"],
    }
    for key, expected in exact.items():
        if boundary.get(key) != expected:
            raise RuntimeError(f"RTDL triangle boundary mismatch: {key}")
    fast = boundary.get("fast_operation_receipt")
    if not isinstance(fast, dict):
        raise RuntimeError("RTDL triangle fast-operation receipt missing")
    for key in (
        "optix_launch_count",
        "dynamic_accel_build_count",
        "control_d2h_bytes",
        "output_d2h_bytes",
        "role_counters_materialized",
        "total_auxiliary_cuda_kernel_launch_count",
    ):
        if fast.get(key) != gate[key]:
            raise RuntimeError(f"RTDL triangle fast-operation mismatch: {key}")
    if mode == STEADY_MODE:
        if (
            fast.get("dynamic_device_upload_call_count")
            != gate["steady_dynamic_device_upload_call_count"]
            or fast.get("dynamic_device_upload_bytes")
            != gate["steady_dynamic_device_upload_bytes"]
        ):
            raise RuntimeError("RTDL steady execution repeated query upload")
    elif (
        gate["first_dynamic_device_upload_required"] is not True
        or type(fast.get("dynamic_device_upload_call_count")) is not int
        or fast["dynamic_device_upload_call_count"] <= 0
        or type(fast.get("dynamic_device_upload_bytes")) is not int
        or fast["dynamic_device_upload_bytes"] <= 0
    ):
        raise RuntimeError("RTDL first execution did not expose initial query upload")
    if fast.get("prepared_input_reused") is not (mode == STEADY_MODE):
        raise RuntimeError("RTDL native prepared-input reuse mismatch")
    return dict(boundary)


def run_rtdl(
    args: argparse.Namespace,
    task: object,
    mode: str,
    authority: dict[str, Any],
    prereg: dict[str, Any],
) -> tuple[dict[str, int | None | list[int]], dict[str, object], str, object]:
    from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain
    from rtdsl.v4_callback_numba_codegen import (
        formal_numba_leaf_cache_lifecycle_metadata,
    )

    capability = tuple(
        int(part) for part in authority["hardware"]["compute_capability"].split(".")
    )
    cache = authority["formal_leaf_cache"]
    cache_policy = FormalNumbaLeafCachePolicy(
        root=Path(cache["root"]),
        manifest=Path(cache["manifest"]),
        manifest_sha256=cache["manifest_file_sha256"],
    )

    def bind_runtime():
        return (
            V4Target.from_native(
                args.native,
                optix_sdk=args.optix_sdk,
                compute_capability=authority["hardware"]["compute_capability"],
            ),
            V4Toolchain.current(
                compute_capability=capability,
                optix_include=args.optix_include,
                cuda_include=args.cuda_include,
                formal_leaf_cache=cache_policy,
            ),
        )

    (target, toolchain), runtime_binding_ns = measured(bind_runtime)
    route, declaration_ns = measured(task.route_factory)
    program, admission_ns = measured(route.compile)
    cache_before = formal_numba_leaf_cache_lifecycle_metadata()
    materialized, materialize_ns = measured(
        lambda: program.materialize(target=target, toolchain=toolchain)
    )
    cache_after = formal_numba_leaf_cache_lifecycle_metadata()
    if (
        int(cache_after["hit_count"]) <= int(cache_before["hit_count"])
        or cache_after["miss_count"] != cache_before["miss_count"]
        or cache_after["disabled_count"] != cache_before["disabled_count"]
    ):
        raise RuntimeError("RTDL worker did not use only sealed formal-cache hits")
    prepared, prepare_ns = measured(lambda: materialized.prepare(task.static_input))

    def execute():
        return prepared.execute(task.batch)

    def validate_result(result: object) -> str:
        public_value = _rtdl_public_value(task.task_id, result)
        output_sha = verify_public_output(task.task_id, public_value, task.expected_output)
        if result.output_sha256 != output_sha:
            raise RuntimeError("RTDL public output digest mismatch")
        traversal = dict(result.traversal_receipt)
        if traversal.get("physical_executor_classification") != "optix_traversal_observed":
            raise RuntimeError("RTDL subworker did not observe OptiX traversal")
        return output_sha

    first_ns: int | None = None
    steady_ns: list[int] = []
    output_sha: str | None = None
    latest_boundary: object = None
    if mode == FIRST_MODE:
        result, first_ns = measured(execute)
        output_sha = validate_result(result)
        latest_boundary = _provider_execution_boundary(prepared)
    else:
        for _ in range(STEADY_WARMUPS):
            output_sha = validate_result(execute())
        for _ in range(STEADY_REPETITIONS):
            result, elapsed = measured(execute)
            steady_ns.append(elapsed)
            output_sha = validate_result(result)
        latest_boundary = _provider_execution_boundary(prepared)
    if output_sha is None:
        raise RuntimeError("RTDL subworker produced no output")
    if task.task_id == TRIANGLE_TASK:
        latest_boundary = _validate_rtdl_triangle_boundary(
            latest_boundary, mode=mode, prereg=prereg
        )
    close_started = time.perf_counter_ns()
    prepared.close()
    close_ns = time.perf_counter_ns() - close_started
    phases: dict[str, int | None | list[int]] = {
        "route_declaration_and_artifact_binding": declaration_ns,
        "provider_projection_and_generic_family_admission": admission_ns,
        "runtime_target_and_toolchain_binding": runtime_binding_ns,
        "device_compile": None,
        "module_program_pipeline_sbt": None,
        "target_materialization": materialize_ns,
        "native_prepare": prepare_ns,
        "first_complete_execution": first_ns,
        "steady_complete_execution": steady_ns,
        "close": close_ns,
    }
    identity = {
        "program": program_signature(program),
        "executable": materialized.identity.to_dict(),
        "native_library_sha256": authority["execution_paths"]["native_library_sha256"],
        "formal_leaf_cache_manifest_sha256": cache["manifest_file_sha256"],
        "formal_leaf_cache_hits": (
            int(cache_after["hit_count"]) - int(cache_before["hit_count"])
        ),
        "formal_leaf_cache_misses": 0,
    }
    return phases, identity, output_sha, latest_boundary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--schedule-worker-id", required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--arm", choices=(PYOPTIX_ARM, RTDL_ARM), required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    row = schedule_row(prereg, args.schedule_worker_id)
    if row["arm"] != args.arm:
        raise RuntimeError("subworker arm differs from frozen schedule")
    for key, supplied in (
        ("native_library", args.native),
        ("device_source", args.device_source),
        ("optix_include", args.optix_include),
        ("cuda_include", args.cuda_include),
    ):
        require_bound_path(authority, key, supplied)
    if args.optix_sdk != authority["toolchain"]["optix_sdk"]:
        raise RuntimeError("OptiX SDK argument differs from authority")
    if args.arm == RTDL_ARM:
        bind_authorized_native_library(authority, args.native)
    started = time.perf_counter_ns()
    task = build_task(row["task"])
    input_ns = time.perf_counter_ns() - started
    contract = task_contract(prereg, task.task_id)
    if task.input_sha256 != contract["input_sha256"]:
        raise RuntimeError("task input differs from preregistration")
    if args.arm == RTDL_ARM:
        phases, identity, output_sha, execution_boundary = run_rtdl(
            args, task, args.mode, authority, prereg
        )
    else:
        phases, identity, output_sha = run_pyoptix(
            args, task, args.mode, authority
        )
        execution_boundary = {
            "schema": "rtdl.goal5843.inherited_pyoptix_execution_boundary.v1",
            "static_and_query_inputs_uploaded_during_prepare": True,
            "execute_reuploads_static_or_query_inputs": False,
            "same_prepared_owner_reused_across_steady_samples": (
                args.mode == STEADY_MODE
            ),
            "gpu_completion_before_timer_stop": True,
            "public_output_scope": contract["public_output_scope"],
            "optix_launch_count": 2 if task.task_id == RELATION_TASK else 1,
            "source_audit_not_hardware_counter": True,
        }
    phases["deterministic_input_materialization"] = input_ns
    if output_sha != contract["public_output_sha256"]:
        raise RuntimeError("public output differs from preregistered digest")
    receipt: dict[str, object] = {
        "schema": SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": row["worker_id"],
        "subworker_id": f"{row['worker_id']}__{args.mode}",
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "mode": args.mode,
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "input_sha256": task.input_sha256,
        "output_sha256": output_sha,
        "public_output_contract_id": contract["public_output_contract_id"],
        "public_output_oracle_exact": True,
        "oracle_validation_outside_registered_interval": True,
        "independent_oracle_witness_sha256": authority[
            "independent_oracle_witness"
        ]["witness_sha256"],
        "phases_ns": phases,
        "identity": identity,
        "latest_execution_boundary": execution_boundary,
    }
    receipt["receipt_sha256"] = digest(receipt)
    create_json(args.output, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
