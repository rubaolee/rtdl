#!/usr/bin/env python3
"""Phase-instrumented current NVIDIA PyOptiX compatible-API arm."""

from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
from typing import Any

if __package__:
    from .worker_common import (
        MEMORY_MODE,
        PREPARED_REPETITIONS,
        PREPARED_WARMUPS,
        admit,
        create_json,
        finish_receipt,
        load_runtime_manifest,
        measured,
        now_ns,
        parser_for,
        plan_result,
        wait_memory_barrier,
    )
    from .workload import digest, relation_workload, triangle_workload
else:
    from worker_common import (
        MEMORY_MODE,
        PREPARED_REPETITIONS,
        PREPARED_WARMUPS,
        admit,
        create_json,
        finish_receipt,
        load_runtime_manifest,
        measured,
        now_ns,
        parser_for,
        plan_result,
        wait_memory_barrier,
    )
    from workload import digest, relation_workload, triangle_workload


ARM = "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"
LEGACY_ARM = "B_STOCK_CURRENT_PYOPTIX_9_1"
RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
RAW_RELATION_CAPACITY = 8194


class PyOptixRelationPrepared:
    def __init__(self, baseline, context, pipeline, sbt, fixture: dict[str, Any]):
        self.baseline = baseline
        self.pipeline = pipeline
        self.sbt = sbt
        self.fixture = fixture
        self.indexed = baseline.boxes_array(fixture["indexed"])
        self.sources = baseline.boxes_array(fixture["sources"])
        self.d_indexed = baseline.to_device(self.indexed)
        self.d_sources = baseline.to_device(self.sources)
        cp = baseline.cp
        self.d_rows = cp.zeros(RAW_RELATION_CAPACITY * 2, dtype=cp.uint32)
        self.d_count = cp.zeros(1, dtype=cp.uint32)
        self.d_overflow = cp.zeros(1, dtype=cp.uint32)
        self.d_status = cp.zeros(1, dtype=cp.uint32)
        self.indexed_handle, self.indexed_gas = baseline.build_custom_gas(context, self.indexed)
        self.source_handle, self.source_gas = baseline.build_custom_gas(context, self.sources)

    def execute(self) -> dict[str, Any]:
        b = self.baseline
        cp = b.cp
        self.d_rows.fill(0)
        self.d_count.fill(0)
        self.d_overflow.fill(0)
        self.d_status.fill(0)
        cp.cuda.get_current_stream().synchronize()
        for reverse, primitive_host, query_host, d_primitive, d_query, handle in (
            (0, self.indexed, self.sources, self.d_indexed, self.d_sources, self.indexed_handle),
            (1, self.sources, self.indexed, self.d_sources, self.d_indexed, self.source_handle),
        ):
            params = b.np.zeros(1, dtype=b.PARAM_DTYPE)
            params[0] = (
                handle, d_primitive.ptr, d_query.ptr, self.d_rows.data.ptr,
                self.d_count.data.ptr, self.d_overflow.data.ptr,
                len(primitive_host), len(query_host), RAW_RELATION_CAPACITY, reverse,
                b.np.float32(self.fixture["minimum_overlap"]), b.np.float32(0.0),
                b.np.float32(1.0), 0, 0, 0, 0, 0, self.d_status.data.ptr,
            )
            b.launch(self.pipeline, self.sbt, params, len(query_host))
        raw_count = int(cp.asnumpy(self.d_count)[0])
        overflow = int(cp.asnumpy(self.d_overflow)[0])
        status = int(cp.asnumpy(self.d_status)[0])
        if overflow or status or raw_count > RAW_RELATION_CAPACITY:
            raise RuntimeError(
                f"PyOptiX formal relation status failure: count={raw_count} "
                f"overflow={overflow} status={status}")
        raw = cp.asnumpy(self.d_rows[:raw_count * 2]).reshape((-1, 2))
        rows = sorted(set(map(tuple, raw.tolist())))
        output = [list(row) for row in rows]
        if len(output) > int(self.fixture["capacity"]):
            raise RuntimeError("PyOptiX formal relation capacity exceeded")
        if output != self.fixture["expected_rows"]:
            raise RuntimeError("PyOptiX formal relation oracle mismatch")
        return {
            "output": output,
            "raw_event_count": raw_count,
            "duplicate_count": raw_count - len(output),
            "device_status": status,
            "device_overflow": overflow,
        }


class PyOptixTrianglePrepared:
    def __init__(self, baseline, context, pipeline, sbt, task: dict[str, Any]):
        self.baseline = baseline
        self.pipeline = pipeline
        self.sbt = sbt
        self.task = task
        b = baseline
        self.vertices = b.np.asarray(task["vertices"], dtype=b.np.float32)
        self.handle, self.gas = b.build_triangle_gas(context, self.vertices)
        rays = b.np.zeros(len(task["rays"]), dtype=b.RAY_DTYPE)
        for index, (origin, direction) in enumerate(task["rays"]):
            rays[index] = tuple(b.np.float32(value) for value in (*origin, *direction))
        self.rays = rays
        self.weights = b.np.asarray(task["weights"], dtype=b.np.uint64)
        self.d_rays = b.to_device(rays)
        self.d_weights = b.cp.asarray(self.weights)
        self.d_per_ray = b.cp.zeros(len(rays), dtype=b.cp.uint64)
        self.d_weighted = b.cp.zeros(1, dtype=b.cp.uint64)
        self.d_status = b.cp.zeros(1, dtype=b.cp.uint32)

    def execute(self) -> dict[str, Any]:
        b = self.baseline
        cp = b.cp
        self.d_per_ray.fill(0)
        self.d_weighted.fill(0)
        self.d_status.fill(0)
        cp.cuda.get_current_stream().synchronize()
        params = b.np.zeros(1, dtype=b.PARAM_DTYPE)
        params[0] = (
            self.handle, 0, 0, 0, 0, 0, 0, len(self.rays), 0, 0,
            b.np.float32(0.0), b.np.float32(self.task["tmin"]),
            b.np.float32(self.task["tmax"]), 0, self.d_rays.ptr,
            self.d_weights.data.ptr, self.d_per_ray.data.ptr,
            self.d_weighted.data.ptr, self.d_status.data.ptr,
        )
        b.launch(self.pipeline, self.sbt, params, len(self.rays))
        status = int(cp.asnumpy(self.d_status)[0])
        per_ray = cp.asnumpy(self.d_per_ray).tolist()
        weighted = int(cp.asnumpy(self.d_weighted)[0])
        if status:
            raise RuntimeError(f"PyOptiX formal triangle status failure: {status}")
        if per_ray != self.task["expected_per_ray"] \
                or weighted != self.task["expected_weighted_sum"]:
            raise RuntimeError("PyOptiX formal triangle oracle mismatch")
        return {"per_ray": per_ray, "weighted_sum": weighted, "device_status": status}


def main() -> None:
    parser = parser_for((ARM, LEGACY_ARM))
    parser.add_argument("--device-source", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    args = parser.parse_args()
    freeze, row, authority = admit(args)
    runtime = load_runtime_manifest(args.runtime_manifest.resolve(), verify_files=False)
    if args.plan_only:
        print(json.dumps(plan_result(
            freeze=freeze, row=row, runtime_manifest=runtime, arm=row["arm"],
        ), sort_keys=True))
        return
    for name in ("device_source", "optix_include", "cuda_include"):
        if getattr(args, name) is None:
            raise ValueError(f"execution requires --{name.replace('_', '-')}")

    # CUDA/OptiX imports occur only after the execution authority has passed.
    repository = Path(__file__).resolve().parents[2]
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))
    from experiments.goal5796_matched import pyoptix_baseline as baseline

    selected = authority["host_binding"]["selected_stack"]
    expected_api = tuple(int(value) for value in selected["optix_api_version"].split("."))
    if tuple(int(value) for value in baseline.optix.version()) != expected_api:
        raise RuntimeError(
            f"selected PyOptiX arm requires OptiX {selected['optix_api_version']}, "
            f"got {baseline.optix.version()}")
    distribution_name = selected["pyoptix_distribution_name"]
    distribution_version = importlib.metadata.version(distribution_name)
    if distribution_version != selected["pyoptix_distribution_version"]:
        raise RuntimeError("installed PyOptiX distribution differs from selected stack")
    if baseline.PYOPTIX_COMMIT != authority["host_binding"]["pyoptix_commit"]:
        raise RuntimeError("PyOptiX source commit constant differs from host binding")

    phases: dict[str, int | None] = {
        "deterministic_input_materialization": 0,
        "protocol_validation_and_codegen": None,
        "device_compile": 0,
        "module_program_pipeline_sbt": 0,
        "gas_and_static_prepare": 0,
        "common_preparation_total": 0,
        "close": 0,
    }
    task_value: dict[str, Any]
    task_value, phases["deterministic_input_materialization"] = measured(
        relation_workload if row["task"] == RELATION_TASK else triangle_workload)
    preparation_start = now_ns()
    ptx, phases["device_compile"] = measured(lambda: baseline.compile_ptx(
        args.device_source.resolve(), args.optix_include.resolve(), args.cuda_include.resolve()))

    def make_pipeline():
        context, logger = baseline.make_context()
        task_name = "relation" if row["task"] == RELATION_TASK else "triangle"
        pipeline, groups, logs = baseline.build_pipeline(context, ptx, task=task_name)
        sbt, sbt_keepalive = baseline.make_sbt(groups)
        return context, logger, pipeline, groups, logs, sbt, sbt_keepalive

    pipeline_state, phases["module_program_pipeline_sbt"] = measured(make_pipeline)
    context, logger, pipeline, groups, logs, sbt, sbt_keepalive = pipeline_state
    if row["task"] == RELATION_TASK:
        prepared, phases["gas_and_static_prepare"] = measured(
            lambda: PyOptixRelationPrepared(baseline, context, pipeline, sbt, task_value))
    else:
        prepared, phases["gas_and_static_prepare"] = measured(
            lambda: PyOptixTrianglePrepared(baseline, context, pipeline, sbt, task_value))
    phases["common_preparation_total"] = now_ns() - preparation_start

    durations: list[int] = []
    latest: dict[str, Any] | None = None
    if row["mode"] == "PREPARED_EXECUTION":
        for _ in range(PREPARED_WARMUPS):
            latest = prepared.execute()
        for _ in range(PREPARED_REPETITIONS):
            latest, elapsed = measured(prepared.execute)
            durations.append(elapsed)
    elif row["mode"] == MEMORY_MODE:
        for _ in range(PREPARED_WARMUPS):
            latest = prepared.execute()
        wait_memory_barrier(args.barrier_dir, {
            "schema": "rtdl.goal5798.prepared_memory_barrier.v1",
            "worker_id": row["worker_id"], "pid": os.getpid(),
            "arm": ARM, "task": row["task"],
        })
        latest, elapsed = measured(prepared.execute)
        durations.append(elapsed)
    else:
        latest, elapsed = measured(prepared.execute)
        durations.append(elapsed)
    if latest is None:
        raise RuntimeError("worker produced no correctness result")

    if row["task"] == RELATION_TASK:
        correctness = {
            "oracle_exact": True,
            "canonical_row_count": len(latest["output"]),
            "output_sha256": digest(latest["output"]),
            "expected_output_sha256": digest(task_value["expected_rows"]),
            "raw_output_sha256": digest(latest["output"]),
            "raw_event_count": latest["raw_event_count"],
            "raw_event_capacity": RAW_RELATION_CAPACITY,
            "device_status": latest["device_status"],
            "device_overflow": latest["device_overflow"],
        }
    else:
        correctness = {
            "oracle_exact": True,
            "per_ray_count": len(latest["per_ray"]),
            "per_ray_sha256": digest(latest["per_ray"]),
            "expected_per_ray_sha256": digest(task_value["expected_per_ray"]),
            "weighted_sum": latest["weighted_sum"],
            "expected_weighted_sum": task_value["expected_weighted_sum"],
            "device_status": latest["device_status"],
            "raw_output_sha256": digest({
                "per_ray": latest["per_ray"], "weighted_sum": latest["weighted_sum"]}),
        }

    close_start = now_ns()
    del prepared, sbt, sbt_keepalive, groups, pipeline, context
    gc.collect()
    baseline.cp.get_default_memory_pool().free_all_blocks()
    phases["close"] = now_ns() - close_start
    import resource
    host_rusage_maxrss_bytes = int(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    receipt = finish_receipt(
        freeze=freeze, row=row, runtime_manifest=runtime, authority=authority,
        phases_ns=phases, execute_durations_ns=durations,
        correctness=correctness,
        implementation={
            "arm": ARM,
            "selected_stack_id": selected["stack_id"],
            "pyoptix_distribution_name": distribution_name,
            "pyoptix_distribution_version": distribution_version,
            "pyoptix_repository_commit": baseline.PYOPTIX_COMMIT,
            "optix_api_version": ".".join(str(value) for value in baseline.optix.version()),
            "device_source_sha256": hashlib.sha256(args.device_source.read_bytes()).hexdigest(),
            "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
            "public_pyoptix_host_api": True,
            "rtdl_imported": False,
            "host_rusage_maxrss_bytes": host_rusage_maxrss_bytes,
        },
    )
    create_json(args.output, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
