"""Untimed exactness and physical-operation witnesses for Goal5848."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .contracts import (
    DIRECT_OPTIX_ARM,
    IDIOMATIC_PYOPTIX_ARM,
    PRIMARY_ARMS,
    RELATION_TASK,
    RTDL_ARM,
    STRONG_PYOPTIX_ARM,
    TASK_CONTRACTS,
    TASKS,
    digest,
    direct_worker_task,
    require_formal_cache_policy,
    rtdl_program_bundles,
    strict_json_loads,
)
from .worker import (
    _RTDL_ROUTE_IDENTITIES,
    _admit_rtdl_artifact_and_start_provider,
    _candidate,
    _close_rtdl_worker_resources,
    _compiler_modules,
    _hardware,
    _nvrtc_mappings,
    _pyoptix_context,
    _validate_pyoptix_deployment,
    _validate_pyoptix_result,
    _validate_rtdl_result,
    _write_create,
)
from .workloads import relation_workload, triangle_workload


def _rtdl(args: argparse.Namespace) -> dict[str, object]:
    from rtdsl import v4_rtdlexe as runtime
    from rtdsl.physical_execution_provenance import validate_traversal_receipt

    candidate, native = _candidate(args.candidate_manifest, args.task)
    workload = (
        relation_workload() if args.task == RELATION_TASK else triangle_workload()
    )
    expected = (
        workload.expected_rows
        if args.task == RELATION_TASK
        else workload.expected_reduced_u64
    )
    deployment = runtime.install_rtdlexe_deployment(
        trust_root_path=Path(str(candidate["public"])),
        trust_head_path=Path(str(candidate["head"])),
        trust_package_path=Path(str(candidate["package"])),
        deployment_id=str(candidate["deployment_id"]),
    )
    initializing, loaded = _admit_rtdl_artifact_and_start_provider(
        runtime,
        deployment,
        native,
        candidate,
        collect_phase_timings=False,
        legacy_provider_timing_api=False,
    )
    provider = prepared = None
    try:
        if args.task == RELATION_TASK:
            static_input = runtime.BoundedRelationBufferStaticInput(
                workload.indexed_bounds_f32le,
                workload.indexed_ids_u32le,
                workload.count,
            )
            batch = runtime.BoundedRelationBufferBatch(
                workload.source_bounds_f32le,
                workload.source_ids_u32le,
                workload.count,
                expected_rows=workload.expected_rows,
            )
        else:
            static_input = runtime.TriangleReductionBufferStaticInput(
                workload.vertices_f32le,
                workload.triangles_u32le,
                workload.vertex_count,
                workload.triangle_count,
                event_capacity=workload.query_count,
            )
            batch = runtime.TriangleReductionBufferBatch(
                workload.query_origins_f32le,
                workload.query_directions_f32le,
                workload.query_tmax_f32le,
                workload.query_count,
                query_weights_u64le=workload.query_weights_u64le,
                expected_reduced_u64=workload.expected_reduced_u64,
            )
        provider = initializing.bind(loaded)
        prepared = provider.prepare(static_input)
        first = prepared.execute(batch)
        second = prepared.execute(batch)
        diagnostic = prepared.execute(batch, include_diagnostics=True)
        for result in (first, second, diagnostic):
            _validate_rtdl_result(args.task, result, expected)
        traversal = dict(diagnostic.traversal_receipt)
        validate_traversal_receipt(
            traversal,
            provider_library_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
            route_identity=_RTDL_ROUTE_IDENTITIES[args.task],
            output_digest=TASK_CONTRACTS[args.task]["public_output_sha256"],
            expected_program_bundles=rtdl_program_bundles(args.task),
            expected_successful_launch_count=int(
                TASK_CONTRACTS[args.task]["required_optix_launch_count"]
            ),
            expected_raygen_invocation_count=(
                2 * workload.count
                if args.task == RELATION_TASK
                else workload.query_count
            ),
        )
        compiler_modules = _compiler_modules()
        nvrtc_mappings = _nvrtc_mappings()
        if (
            provider.runtime_compiler_attempt_count != 0
            or compiler_modules
            or nvrtc_mappings
        ):
            raise RuntimeError("Goal5848 RTDL preflight touched compiler lifecycle")
        return {
            "execution_count": 3,
            "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
            "diagnostic_traversal_receipt": traversal,
            "runtime_compiler_attempt_count": (
                provider.runtime_compiler_attempt_count
            ),
            "runtime_compiler_modules": list(compiler_modules),
            "nvrtc_mappings": list(nvrtc_mappings),
        }
    finally:
        active_error = sys.exc_info()[1]
        try:
            _close_rtdl_worker_resources(
                prepared=prepared,
                provider=provider,
                initializing=initializing,
            )
        except Exception as cleanup_error:
            if active_error is None:
                raise
            active_error.add_note(
                "RTDL preflight cleanup also failed: " + repr(cleanup_error)
            )


def _idiomatic_pyoptix(args: argparse.Namespace) -> dict[str, object]:
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
        PyOptixTrianglePrepared,
    )
    from experiments.goal5798_premeasurement.workload import (
        relation_workload as old_relation_workload,
    )
    from experiments.goal5798_premeasurement.workload import (
        triangle_workload as old_triangle_workload,
    )

    workload = (
        old_relation_workload()
        if args.task == RELATION_TASK
        else old_triangle_workload()
    )
    expected = (
        tuple(tuple(row) for row in workload["expected_rows"])
        if args.task == RELATION_TASK
        else int(workload["expected_weighted_sum"])
    )
    ptx = args.precompiled_ptx.resolve(strict=True).read_bytes()
    context, logger = _pyoptix_context(baseline)
    pipeline, groups, logs = baseline.build_pipeline(
        context,
        ptx,
        task="relation" if args.task == RELATION_TASK else "triangle",
    )
    sbt, keepalive = baseline.make_sbt(groups)
    owner = (
        PyOptixRelationPrepared(baseline, context, pipeline, sbt, workload)
        if args.task == RELATION_TASK
        else PyOptixTrianglePrepared(baseline, context, pipeline, sbt, workload)
    )
    results = [
        owner.execute(validate_expected=False)
        if args.task == RELATION_TASK
        else owner.execute(public_output_only=True, validate_expected=False)
        for _ in range(2)
    ]
    for result in results:
        _validate_pyoptix_result(args.task, result, expected)
    deployment = _validate_pyoptix_deployment(baseline, args)
    _ = (logger, groups, logs, keepalive, owner)
    return {
        "execution_count": 2,
        "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
        "expected_optix_launch_count_per_execution": TASK_CONTRACTS[args.task][
            "required_optix_launch_count"
        ],
        "host_continuation_disclosed": args.task == RELATION_TASK,
        "deployment": deployment,
    }


def _strong_untimed_witness(
    adapter: Any,
    *,
    task: str,
    expected: object,
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    results = [adapter.execute_with_operation_guard() for _ in range(2)]
    for result in results:
        _validate_pyoptix_result(task, result, expected)
    lifecycle = []
    evidence_rows = []
    for result in results:
        dynamic = result.get("dynamic_input_receipt")
        guard = result.get("independent_execute_guard")
        if not isinstance(dynamic, Mapping) or not isinstance(guard, Mapping):
            raise TypeError("Goal5848 Strong PyOptix guard evidence differs")
        lifecycle.append(dict(dynamic))
        evidence_rows.append({
            "independent_execute_guard": dict(guard),
            "dynamic_input_receipt": dict(dynamic),
            "execute_operation_counts": result.get("execute_operation_counts"),
            "operation_order": result.get("operation_order"),
            "prepare_operation_counts": result.get("prepare_operation_counts"),
            "live_execute_guard_inside_timer": result.get(
                "live_execute_guard_inside_timer"
            ),
        })
    return lifecycle, {
        "first_execute": evidence_rows[0],
        "reused_execute": evidence_rows[1],
    }


def _strong_pyoptix(args: argparse.Namespace) -> dict[str, object]:
    from experiments.goal5802_premeasurement import pyoptix_scalar_arm as old_arm

    baseline, preload = old_arm.preload_pyoptix_runtime()
    from .strong_pyoptix import StrongPyOptixAdapter

    workload = (
        relation_workload() if args.task == RELATION_TASK else triangle_workload()
    )
    expected = (
        workload.expected_rows
        if args.task == RELATION_TASK
        else workload.expected_reduced_u64
    )
    adapter = StrongPyOptixAdapter(
        args.task,
        workload,
        ptx_path=args.precompiled_ptx,
        compaction_cubin_path=(
            args.compaction_cubin if args.task == RELATION_TASK else None
        ),
        record_operation_evidence=True,
        preloaded_runtime=baseline,
        runtime_preload_receipt=preload,
    )
    try:
        adapter.load()
        adapter.prepare()
        lifecycle, operation_evidence = _strong_untimed_witness(
            adapter,
            task=args.task,
            expected=expected,
        )
        deployment = _validate_pyoptix_deployment(baseline, args)
    finally:
        adapter.close()
    return {
        "execution_count": 2,
        "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
        "device_continuation": True,
        "lifecycle": lifecycle,
        "operation_evidence": operation_evidence,
        "deployment": deployment,
    }


def _direct(args: argparse.Namespace) -> dict[str, object]:
    mapped_task = direct_worker_task(args.task)
    command = [
        str(args.direct_worker.resolve(strict=True)),
        "--local-untimed-functional",
        "--task",
        mapped_task,
        "--ptx",
        str(args.precompiled_ptx.resolve(strict=True)),
    ]
    if args.task == RELATION_TASK:
        command.extend([
            "--compaction-cubin",
            str(args.compaction_cubin.resolve(strict=True)),
        ])
    completed = subprocess.run(command, capture_output=True, check=False)
    try:
        value = strict_json_loads(
            completed.stdout,
            label="Goal5848 Direct preflight stdout",
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError("Goal5848 Direct preflight output differs") from error
    expected_task = mapped_task
    correctness = value.get("correctness") if isinstance(value, dict) else None
    ledger = value.get("operation_ledger") if isinstance(value, dict) else None
    expected = (
        [list(row) for row in relation_workload().expected_rows]
        if args.task == RELATION_TASK
        else triangle_workload().expected_reduced_u64
    )
    if (
        completed.returncode != 0
        or completed.stderr
        or not isinstance(value, dict)
        or value.get("schema") != "rtdl.goal5802.direct_scalar.worker.v1"
        or value.get("status") != "PASS"
        or value.get("task") != expected_task
        or value.get("regime") != "LOCAL_UNTIMED"
        or value.get("registered_performance_timing_count") != 0
        or value.get("execute_or_regime_durations_ns") != []
        or not isinstance(correctness, Mapping)
        or correctness.get("oracle_exact") is not True
        or not isinstance(ledger, Mapping)
        or ledger.get("optix_launch_count")
        != TASK_CONTRACTS[args.task]["required_optix_launch_count"]
        or ledger.get("application_output_d2h_bytes")
        != TASK_CONTRACTS[args.task]["public_output_bytes"]
        or ledger.get("per_ray_d2h_bytes") != 0
        or (
            args.task == RELATION_TASK
            and correctness.get("canonical_rows") != expected
        )
        or (
            args.task != RELATION_TASK
            and correctness.get("reduced_u64") != expected
        )
    ):
        raise RuntimeError("Goal5848 Direct preflight contract differs")
    return {
        "execution_count": 2,
        "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
        "direct_receipt": value,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=PRIMARY_ARMS, required=True)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--precompiled-ptx", type=Path)
    parser.add_argument("--compaction-cubin", type=Path)
    parser.add_argument("--pyoptix-source", type=Path)
    parser.add_argument("--pyoptix-build-receipt", type=Path)
    parser.add_argument("--expected-optix-sdk")
    parser.add_argument("--direct-worker", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    if args.arm == RTDL_ARM and args.candidate_manifest is None:
        raise ValueError("Goal5848 RTDL preflight candidate is absent")
    if args.arm != RTDL_ARM and args.precompiled_ptx is None:
        raise ValueError("Goal5848 preflight PTX is absent")
    if args.arm in {IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM} and any(
        value is None
        for value in (
            args.pyoptix_source,
            args.pyoptix_build_receipt,
            args.expected_optix_sdk,
        )
    ):
        raise ValueError("Goal5848 PyOptix preflight provenance is absent")
    if args.arm == DIRECT_OPTIX_ARM and args.direct_worker is None:
        raise ValueError("Goal5848 Direct preflight worker is absent")
    if args.task == RELATION_TASK and args.arm in {
        STRONG_PYOPTIX_ARM,
        DIRECT_OPTIX_ARM,
    } and args.compaction_cubin is None:
        raise ValueError("Goal5848 relation preflight compaction is absent")
    runner: dict[str, Any] = {
        RTDL_ARM: _rtdl,
        IDIOMATIC_PYOPTIX_ARM: _idiomatic_pyoptix,
        STRONG_PYOPTIX_ARM: _strong_pyoptix,
        DIRECT_OPTIX_ARM: _direct,
    }
    details = runner[args.arm](args)
    result = {
        "schema": "rtdl.goal5848.timer_free_preflight_worker.v1",
        "status": "PASS__UNTIMED_EXACT_PHYSICAL_WITNESS",
        "arm": args.arm,
        "task": args.task,
        "hardware": _hardware(),
        "details": details,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "external_review_complete": False,
        "public_or_manuscript_claim_authorized": False,
    }
    result["receipt_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
