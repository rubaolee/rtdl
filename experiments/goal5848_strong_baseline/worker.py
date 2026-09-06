"""Fresh-process Python-arm worker for Goal5848 exploration and formal runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .contracts import (
    BLOCKS,
    COMPONENT_DIAGNOSTIC_KEYS,
    IDIOMATIC_PYOPTIX_ARM,
    PARTITION_KEYS,
    RELATION_TASK,
    RTDL_ARM,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    STRONG_PYOPTIX_ARM,
    TASK_CONTRACTS,
    TRIANGLE_TASK,
    WORKER_SCHEMA,
    digest,
    require_formal_cache_policy,
    rtdl_program_bundles,
    strict_json_loads,
    validate_component_diagnostics,
    validate_phase_partition,
)
from .workloads import relation_workload, triangle_workload

PYTHON_ARMS = (RTDL_ARM, IDIOMATIC_PYOPTIX_ARM, STRONG_PYOPTIX_ARM)
ROOT = Path(__file__).resolve().parents[2]

_RTDL_ROUTE_IDENTITIES = {
    RELATION_TASK: "v4_callback_ir:custom_aabb_bounded_relation_v1",
    TRIANGLE_TASK: "v4_builtin_triangle_callback_ir:checked_reduction_v1",
}


def _measure(action: Callable[[], Any]) -> tuple[Any, int]:
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def _measure_if(
    action: Callable[[], Any], *, enabled: bool,
) -> tuple[Any, int]:
    if not enabled:
        return action(), 0
    return _measure(action)


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git_identity() -> dict[str, object]:
    values = {}
    for label, arguments in (
        ("commit", ("rev-parse", "HEAD")),
        ("tree", ("rev-parse", "HEAD^{tree}")),
        ("status", ("status", "--porcelain=v1", "--untracked-files=all")),
    ):
        values[label] = subprocess.run(
            ["git", "-C", str(ROOT), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    return {**values, "clean": values["status"] == ""}


def _git_identity_at(path: Path) -> dict[str, object]:
    values = {}
    for label, arguments in (
        ("commit", ("rev-parse", "HEAD")),
        ("tree", ("rev-parse", "HEAD^{tree}")),
        ("status", ("status", "--porcelain=v1", "--untracked-files=all")),
    ):
        values[label] = subprocess.run(
            ["git", "-C", str(path), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    return {**values, "clean": values["status"] == ""}


def _hardware() -> dict[str, object]:
    row = subprocess.run(
        [
            "nvidia-smi",
            "--id=0",
            "--query-gpu=name,uuid,driver_version,memory.total,compute_cap",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().splitlines()
    if len(row) != 1:
        raise RuntimeError("Goal5848 requires exactly one visible GPU")
    fields = [field.strip() for field in row[0].split(",")]
    if len(fields) != 5:
        raise RuntimeError("Goal5848 GPU identity row differs")
    return {
        "gpu_name": fields[0],
        "gpu_uuid": fields[1],
        "driver_version": fields[2],
        "memory_mib": int(fields[3]),
        "compute_capability": fields[4],
    }


def _nvrtc_mappings() -> tuple[str, ...]:
    maps = Path("/proc/self/maps")
    if not maps.is_file():
        return ()
    return tuple(sorted({
        line.rsplit(None, 1)[-1]
        for line in maps.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        if "nvrtc" in line.lower()
    }))


def _compiler_modules() -> tuple[str, ...]:
    exact = {
        "numba",
        "llvmlite",
        "rtdsl.v4_callback_lifecycle",
        "rtdsl.v4_generic_family_lifecycle",
    }
    prefixes = ("numba.", "llvmlite.")
    return tuple(sorted(
        name
        for name in sys.modules
        if name in exact or name.startswith(prefixes)
    ))


def _summary(samples: list[int]) -> dict[str, object]:
    if not samples or any(type(value) is not int or value <= 0 for value in samples):
        raise ValueError("Goal5848 requires positive retained samples")
    return {
        "sample_count": len(samples),
        "samples_ns": samples,
        "minimum_ns": min(samples),
        "median_ns": int(statistics.median(samples)),
        "maximum_ns": max(samples),
    }


def _sample(
    action: Callable[[], object],
    validate: Callable[[object], None],
    *,
    warmups: int,
    repetitions: int,
) -> tuple[dict[str, object], object]:
    latest = None
    for _ in range(warmups):
        latest = action()
        validate(latest)
    samples = []
    for _ in range(repetitions):
        latest, elapsed = _measure(action)
        validate(latest)
        samples.append(elapsed)
    if latest is None:
        raise RuntimeError("Goal5848 timing loop produced no result")
    return _summary(samples), latest


def _empty_partition() -> dict[str, int]:
    return {name: 0 for name in PARTITION_KEYS}


def _empty_components() -> dict[str, int | None]:
    return {name: None for name in COMPONENT_DIAGNOSTIC_KEYS}


def _finish_partition(
    partition: dict[str, int],
    *,
    endpoint_start_ns: int,
    endpoint_end_ns: int,
) -> tuple[int, dict[str, int]]:
    endpoint_ns = endpoint_end_ns - endpoint_start_ns
    attributed = sum(partition.values())
    residual = endpoint_ns - attributed
    if residual < 0:
        raise RuntimeError("Goal5848 endpoint partition over-attributed time")
    partition["unattributed_control_plane"] = residual
    reconciliation = validate_phase_partition(
        partition,
        endpoint_ns=endpoint_ns,
    )
    return endpoint_ns, reconciliation


def _candidate(manifest_path: Path, task: str) -> tuple[dict[str, object], Path]:
    manifest = strict_json_loads(
        manifest_path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 RTDL candidate manifest",
    )
    if manifest.get("schema") not in {
        "rtdl.goal5847.aot_candidates.v1",
        "rtdl.goal5848.aot_candidates.v1",
    }:
        raise RuntimeError("Goal5848 RTDL candidate manifest differs")
    rows = manifest.get("rows")
    label = "relation" if task == RELATION_TASK else "triangle"
    if not isinstance(rows, dict) or not isinstance(rows.get(label), dict):
        raise TypeError(f"Goal5848 candidate is absent: {label}")
    native = Path(str(manifest["native"])).resolve(strict=True)
    return dict(rows[label]), native


def _public_output(task: str, result: object) -> object:
    if task == RELATION_TASK:
        raw = result.get("output") if isinstance(result, Mapping) else getattr(
            result, "output", None
        )
        return tuple(tuple(int(item) for item in row) for row in raw)
    if isinstance(result, Mapping):
        candidates = [
            int(result[key])
            for key in ("weighted_sum", "output", "reduced_u64")
            if key in result
        ]
        if not candidates:
            raise TypeError("Goal5848 triangle public output is absent")
        if any(value != candidates[0] for value in candidates[1:]):
            raise RuntimeError("Goal5848 triangle public outputs disagree")
        return candidates[0]
    return int(getattr(result, "output", getattr(result, "reduced_u64", None)))


def _validate_rtdl_result(task: str, result: object, expected: object) -> None:
    output = _public_output(task, result)
    if output != expected or digest(output) != TASK_CONTRACTS[task][
        "public_output_sha256"
    ]:
        raise RuntimeError("Goal5848 RTDL output differs from frozen oracle")


def _begin_rtdl_provider_initialization(
    deployment: Any,
    native: Path,
    *,
    collect_phase_timings: bool,
    legacy_provider_timing_api: bool,
) -> Any:
    if legacy_provider_timing_api:
        return deployment.begin_provider_initialization(native)
    return deployment.begin_provider_initialization(
        native,
        collect_phase_timings=collect_phase_timings,
    )


def _admit_rtdl_artifact_and_start_provider(
    runtime: Any,
    deployment: Any,
    native: Path,
    candidate: Mapping[str, object],
    *,
    collect_phase_timings: bool,
    legacy_provider_timing_api: bool,
) -> tuple[Any, Any]:
    """Start admission and close it if the parallel artifact load fails."""

    initializing = _begin_rtdl_provider_initialization(
        deployment,
        native,
        collect_phase_timings=collect_phase_timings,
        legacy_provider_timing_api=legacy_provider_timing_api,
    )
    try:
        loaded = runtime.load_rtdlexe(
            Path(str(candidate["artifact"])),
            authority_path=Path(str(candidate["authority"])),
            deployment=deployment,
        )
    except BaseException as error:
        try:
            initializing.close()
        except Exception as cleanup_error:  # noqa: BLE001
            error.add_note(
                "RTDL provider initialization cleanup also failed: "
                + repr(cleanup_error)
            )
        raise
    return initializing, loaded


def _close_rtdl_worker_resources(
    *,
    prepared: Any | None,
    provider: Any | None,
    initializing: Any | None,
) -> None:
    """Close every acquired layer while retaining all cleanup failures."""

    errors: list[Exception] = []
    for resource in (
        prepared,
        provider if provider is not None else initializing,
    ):
        if resource is None:
            continue
        try:
            resource.close()
        except Exception as error:  # noqa: BLE001
            errors.append(error)
    if errors:
        primary = errors[0]
        for secondary in errors[1:]:
            primary.add_note("additional cleanup failure: " + repr(secondary))
        raise primary


def _run_rtdl(
    args: argparse.Namespace,
    *,
    legacy_provider_timing_api: bool = False,
) -> dict[str, object]:
    imported_started = time.perf_counter_ns()
    from rtdsl import v4_rtdlexe as runtime
    from rtdsl.physical_execution_provenance import validate_traversal_receipt

    import_ns = time.perf_counter_ns() - imported_started
    phase_instrumentation = args.phase_instrumentation == "on"
    partition = _empty_partition()
    components = _empty_components()
    endpoint_start = time.perf_counter_ns()

    candidate, native = _candidate(args.candidate_manifest, args.task)

    workload_factory = (
        relation_workload if args.task == RELATION_TASK else triangle_workload
    )
    workload, partition["canonical_input_construction"] = _measure_if(
        workload_factory,
        enabled=phase_instrumentation,
    )
    expected = (
        workload.expected_rows
        if args.task == RELATION_TASK
        else workload.expected_reduced_u64
    )
    deployment, partition["signed_deployment_install"] = _measure_if(
        lambda: runtime.install_rtdlexe_deployment(
            trust_root_path=Path(str(candidate["public"])),
            trust_head_path=Path(str(candidate["head"])),
            trust_package_path=Path(str(candidate["package"])),
            deployment_id=str(candidate["deployment_id"]),
        ),
        enabled=phase_instrumentation,
    )

    state, partition["parallel_artifact_and_provider_admission"] = _measure_if(
        lambda: _admit_rtdl_artifact_and_start_provider(
            runtime,
            deployment,
            native,
            candidate,
            collect_phase_timings=phase_instrumentation,
            legacy_provider_timing_api=legacy_provider_timing_api,
        ),
        enabled=phase_instrumentation,
    )
    initializing, loaded = state
    provider = prepared = None
    try:
        if args.task == RELATION_TASK:
            static_input, partition["static_input_deployment"] = _measure_if(
                lambda: runtime.BoundedRelationBufferStaticInput(
                    workload.indexed_bounds_f32le,
                    workload.indexed_ids_u32le,
                    workload.count,
                ),
                enabled=phase_instrumentation,
            )
            batch, partition["dynamic_input_deployment"] = _measure_if(
                lambda: runtime.BoundedRelationBufferBatch(
                    workload.source_bounds_f32le,
                    workload.source_ids_u32le,
                    workload.count,
                    expected_rows=workload.expected_rows,
                ),
                enabled=phase_instrumentation,
            )
        else:
            static_input, partition["static_input_deployment"] = _measure_if(
                lambda: runtime.TriangleReductionBufferStaticInput(
                    workload.vertices_f32le,
                    workload.triangles_u32le,
                    workload.vertex_count,
                    workload.triangle_count,
                    event_capacity=workload.query_count,
                ),
                enabled=phase_instrumentation,
            )
            batch, partition["dynamic_input_deployment"] = _measure_if(
                lambda: runtime.TriangleReductionBufferBatch(
                    workload.query_origins_f32le,
                    workload.query_directions_f32le,
                    workload.query_tmax_f32le,
                    workload.query_count,
                    query_weights_u64le=workload.query_weights_u64le,
                    expected_reduced_u64=workload.expected_reduced_u64,
                ),
                enabled=phase_instrumentation,
            )
        provider, partition["provider_artifact_bind_wait"] = _measure_if(
            lambda: initializing.bind(loaded),
            enabled=phase_instrumentation,
        )
        prepared, partition["native_prepare"] = _measure_if(
            lambda: provider.prepare(static_input),
            enabled=phase_instrumentation,
        )
        first, partition["first_complete_execution"] = _measure_if(
            lambda: prepared.execute(batch),
            enabled=phase_instrumentation,
        )
        _, partition["public_output_validation"] = _measure_if(
            lambda: _validate_rtdl_result(args.task, first, expected),
            enabled=phase_instrumentation,
        )
        endpoint_end = time.perf_counter_ns()
        endpoint_ns, reconciliation = _finish_partition(
            partition,
            endpoint_start_ns=endpoint_start,
            endpoint_end_ns=endpoint_end,
        )
        compiler_before = provider.runtime_compiler_attempt_count
        steady, latest = _sample(
            lambda: prepared.execute(batch),
            lambda result: _validate_rtdl_result(args.task, result, expected),
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        diagnostic = prepared.execute(batch, include_diagnostics=True)
        _validate_rtdl_result(args.task, diagnostic, expected)
        traversal = dict(diagnostic.traversal_receipt)
        expected_launches = int(
            TASK_CONTRACTS[args.task]["required_optix_launch_count"]
        )
        expected_invocations = (
            2 * workload.count
            if args.task == RELATION_TASK
            else workload.query_count
        )
        route_identity = _RTDL_ROUTE_IDENTITIES[args.task]
        validate_traversal_receipt(
            traversal,
            provider_library_sha256=_sha256_file(native),
            route_identity=route_identity,
            output_digest=TASK_CONTRACTS[args.task]["public_output_sha256"],
            expected_program_bundles=rtdl_program_bundles(args.task),
            expected_successful_launch_count=expected_launches,
            expected_raygen_invocation_count=expected_invocations,
        )
        compiler_after = provider.runtime_compiler_attempt_count
        compiler_modules = _compiler_modules()
        nvrtc_mappings = _nvrtc_mappings()
        if (
            compiler_before != 0
            or compiler_after != 0
            or compiler_modules
            or nvrtc_mappings
        ):
            raise RuntimeError("Goal5848 RTDL deploy touched a runtime compiler")
        provider_phases = dict(initializing.phase_timings_ns)
        if phase_instrumentation:
            components["trust_root_and_package_discovery"] = partition[
                "signed_deployment_install"
            ]
            # The public loader does not yet expose separate artifact
            # decode/hash timers. Preserve the exact aggregate instead of
            # inventing overlapping component attribution.
            components["native_image_read_and_hash"] = provider_phases.get(
                "sealed_native_image"
            )
            components["cuda_primary_context"] = provider_phases.get(
                "cuda_primary_context"
            )
            components["optix_module_program_pipeline_sbt"] = (
                provider_phases.get("native_runtime_warm")
            )
            components["provider_unexplained_wait"] = partition[
                "provider_artifact_bind_wait"
            ]
            components["static_input_validation_and_allocation"] = partition[
                "static_input_deployment"
            ]
            components["dynamic_input_validation_and_allocation"] = partition[
                "dynamic_input_deployment"
            ]
        validate_component_diagnostics(components)
        return {
            "implementation_import_ns": import_ns,
            "post_import_to_first_correct_result_ns": endpoint_ns,
            "endpoint_partition_ns": partition,
            "partition_reconciliation": reconciliation,
            "component_diagnostics_ns": components,
            "steady_complete_execution": steady,
            "identity": {
                "artifact_sha256": _sha256_file(
                    Path(str(candidate["artifact"]))
                ),
                "authority_sha256": _sha256_file(
                    Path(str(candidate["authority"]))
                ),
                "native_library_sha256": _sha256_file(native),
                "family_executable_identity_sha256": (
                    loaded.family_executable_identity_sha256
                ),
            },
            "evidence": {
                "output_sha256": TASK_CONTRACTS[args.task][
                    "public_output_sha256"
                ],
                "runtime_compiler_attempt_count_before": compiler_before,
                "runtime_compiler_attempt_count_after": compiler_after,
                "runtime_compiler_modules": list(compiler_modules),
                "nvrtc_mappings": list(nvrtc_mappings),
                "provider_initialization_phases_ns": provider_phases,
                "phase_instrumentation": phase_instrumentation,
                "diagnostic_traversal_receipt": traversal,
                "latest_output_sha256": getattr(latest, "output_sha256", None),
                "public_output": _public_output(args.task, latest),
            },
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
                "RTDL worker cleanup also failed: " + repr(cleanup_error)
            )


def _validate_pyoptix_result(task: str, result: object, expected: object) -> None:
    output = _public_output(task, result)
    if output != expected or digest(output) != TASK_CONTRACTS[task][
        "public_output_sha256"
    ]:
        raise RuntimeError("Goal5848 PyOptix output differs from frozen oracle")


def _pyoptix_context(baseline: Any) -> tuple[Any, Any]:
    baseline.cp.cuda.runtime.free(0)
    if hasattr(baseline.optix, "init"):
        baseline.optix.init()
    logger = baseline.Logger()
    options = baseline.optix.DeviceContextOptions(
        logCallbackFunction=logger,
        logCallbackLevel=4,
    )
    if baseline.optix.version()[1] >= 2:
        options.validationMode = baseline.optix.DEVICE_CONTEXT_VALIDATION_MODE_OFF
    context = baseline.optix.deviceContextCreate(0, options)
    set_cache_enabled = getattr(context, "setCacheEnabled", None)
    if not callable(set_cache_enabled):
        raise TypeError("PyOptix context does not expose disk-cache control")
    set_cache_enabled(False)
    return context, logger


def _validate_pyoptix_deployment(
    baseline: Any,
    args: argparse.Namespace,
) -> dict[str, object]:
    from experiments.goal5844_compact_execution.provenance import (
        validate_pyoptix_build_receipt,
    )
    from experiments.goal5847_aot_startup.contracts import (
        PYOPTIX_COMMIT,
        PYOPTIX_TREE,
    )

    if tuple(int(item) for item in baseline.optix.version()) != tuple(
        int(item) for item in args.expected_optix_sdk.split(".")
    ):
        raise RuntimeError("Goal5848 PyOptix API differs")
    build_receipt = validate_pyoptix_build_receipt(
        args.pyoptix_build_receipt.resolve(strict=True)
    )
    source = _git_identity_at(args.pyoptix_source.resolve(strict=True))
    if (
        source["commit"] != PYOPTIX_COMMIT
        or source["tree"] != PYOPTIX_TREE
        or source["clean"] is not True
        or baseline.PYOPTIX_COMMIT != PYOPTIX_COMMIT
    ):
        raise RuntimeError("Goal5848 pinned PyOptix source differs")
    extension = sys.modules.get("optix._optix")
    extension_path = Path(str(getattr(extension, "__file__", ""))).resolve(
        strict=True
    )
    extension_sha256 = _sha256_file(extension_path)
    installed = build_receipt["installed"]["loaded_extension"]
    if (
        extension_path.stat().st_size != installed["bytes"]
        or extension_sha256 != installed["sha256"]
        or extension_sha256 != build_receipt["wheel"]["extension_sha256"]
    ):
        raise RuntimeError("Goal5848 loaded PyOptix extension differs")
    return {
        "source": source,
        "build_receipt_sha256": _sha256_file(
            args.pyoptix_build_receipt.resolve(strict=True)
        ),
        "loaded_extension_path": str(extension_path),
        "loaded_extension_sha256": extension_sha256,
        "optix_api_version": list(baseline.optix.version()),
    }


def _run_idiomatic_pyoptix(args: argparse.Namespace) -> dict[str, object]:
    imported_started = time.perf_counter_ns()
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
        PyOptixTrianglePrepared,
    )
    from experiments.goal5798_premeasurement.workload import (
        relation_workload as idiomatic_relation_workload,
    )
    from experiments.goal5798_premeasurement.workload import (
        triangle_workload as idiomatic_triangle_workload,
    )

    import_ns = time.perf_counter_ns() - imported_started
    phase_instrumentation = args.phase_instrumentation == "on"
    partition = _empty_partition()
    components = _empty_components()
    endpoint_start = time.perf_counter_ns()
    workload_factory = (
        idiomatic_relation_workload
        if args.task == RELATION_TASK
        else idiomatic_triangle_workload
    )
    workload, partition["canonical_input_construction"] = _measure_if(
        workload_factory,
        enabled=phase_instrumentation,
    )
    expected = (
        tuple(tuple(row) for row in workload["expected_rows"])
        if args.task == RELATION_TASK
        else int(workload["expected_weighted_sum"])
    )
    ptx_state, partition[
        "parallel_artifact_and_provider_admission"
    ] = _measure_if(
        lambda: (
            args.precompiled_ptx.resolve(strict=True).read_bytes(),
            _pyoptix_context(baseline),
        ),
        enabled=phase_instrumentation,
    )
    ptx, (context, logger) = ptx_state

    def prepare_owner():
        pipeline, groups, logs = baseline.build_pipeline(
            context,
            ptx,
            task="relation" if args.task == RELATION_TASK else "triangle",
        )
        sbt, keepalive = baseline.make_sbt(groups)
        owner = (
            PyOptixRelationPrepared(baseline, context, pipeline, sbt, workload)
            if args.task == RELATION_TASK
            else PyOptixTrianglePrepared(
                baseline,
                context,
                pipeline,
                sbt,
                workload,
            )
        )
        return owner, pipeline, groups, logs, sbt, keepalive

    owner_state, partition["native_prepare"] = _measure_if(
        prepare_owner,
        enabled=phase_instrumentation,
    )
    owner, pipeline, groups, logs, sbt, keepalive = owner_state

    def execute():
        return (
            owner.execute(validate_expected=False)
            if args.task == RELATION_TASK
            else owner.execute(public_output_only=True, validate_expected=False)
        )

    first, partition["first_complete_execution"] = _measure_if(
        execute,
        enabled=phase_instrumentation,
    )
    _, partition["public_output_validation"] = _measure_if(
        lambda: _validate_pyoptix_result(args.task, first, expected),
        enabled=phase_instrumentation,
    )
    endpoint_end = time.perf_counter_ns()
    endpoint_ns, reconciliation = _finish_partition(
        partition,
        endpoint_start_ns=endpoint_start,
        endpoint_end_ns=endpoint_end,
    )
    steady, latest = _sample(
        execute,
        lambda result: _validate_pyoptix_result(args.task, result, expected),
        warmups=args.warmups,
        repetitions=args.repetitions,
    )
    deployment_identity = _validate_pyoptix_deployment(baseline, args)
    # Frozen PTX loading, context admission, pipeline creation and GAS build
    # share the current baseline's public setup calls.  Their aggregate phases
    # remain in the disjoint endpoint partition; unavailable subphases stay
    # null rather than being double-counted.
    validate_component_diagnostics(components)
    _ = (pipeline, groups, logs, sbt, keepalive, context, logger)
    return {
        "implementation_import_ns": import_ns,
        "post_import_to_first_correct_result_ns": endpoint_ns,
        "endpoint_partition_ns": partition,
        "partition_reconciliation": reconciliation,
        "component_diagnostics_ns": components,
        "steady_complete_execution": steady,
        "identity": {
            "precompiled_ptx_sha256": hashlib.sha256(ptx).hexdigest(),
            "pyoptix_api_version": list(baseline.optix.version()),
            "deployment": deployment_identity,
        },
        "evidence": {
            "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
            "phase_instrumentation": phase_instrumentation,
            "host_continuation_disclosed": args.task == RELATION_TASK,
            "raw_event_count": (
                int(latest["raw_event_count"])
                if args.task == RELATION_TASK
                else None
            ),
            "source_compilation_inside_endpoint": False,
            "public_output": _public_output(args.task, latest),
        },
    }


def _run_strong_pyoptix(args: argparse.Namespace) -> dict[str, object]:
    imported_started = time.perf_counter_ns()
    from experiments.goal5802_premeasurement import pyoptix_scalar_arm as old_arm

    baseline, preload_receipt = old_arm.preload_pyoptix_runtime()
    from .strong_pyoptix import StrongPyOptixAdapter

    import_ns = time.perf_counter_ns() - imported_started
    phase_instrumentation = args.phase_instrumentation == "on"
    partition = _empty_partition()
    components = _empty_components()
    endpoint_start = time.perf_counter_ns()
    factory = relation_workload if args.task == RELATION_TASK else triangle_workload
    workload, partition["canonical_input_construction"] = _measure_if(
        factory,
        enabled=phase_instrumentation,
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
        preloaded_runtime=baseline,
        runtime_preload_receipt=preload_receipt,
    )
    try:
        _, partition["parallel_artifact_and_provider_admission"] = _measure_if(
            adapter.load,
            enabled=phase_instrumentation,
        )
        _, partition["native_prepare"] = _measure_if(
            adapter.prepare,
            enabled=phase_instrumentation,
        )
        execute = adapter.measurement_execution_callable()
        first, partition["first_complete_execution"] = _measure_if(
            execute,
            enabled=phase_instrumentation,
        )
        _, partition["public_output_validation"] = _measure_if(
            lambda: _validate_pyoptix_result(args.task, first, expected),
            enabled=phase_instrumentation,
        )
        endpoint_end = time.perf_counter_ns()
        endpoint_ns, reconciliation = _finish_partition(
            partition,
            endpoint_start_ns=endpoint_start,
            endpoint_end_ns=endpoint_end,
        )
        steady, latest = _sample(
            execute,
            lambda result: _validate_pyoptix_result(args.task, result, expected),
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        lifecycle = adapter.measurement_lifecycle_receipt(latest)
        evidence = adapter.finalize_measurement_evidence(latest)
        identity = adapter.runtime_identity()
        identity["deployment"] = _validate_pyoptix_deployment(
            baseline, args
        )
    finally:
        active_error = sys.exc_info()[1]
        try:
            adapter.close()
        except Exception as cleanup_error:
            if active_error is None:
                raise
            active_error.add_note(
                "strong PyOptix worker cleanup also failed: "
                + repr(cleanup_error)
            )
    # The frozen strong baseline exposes aggregate lifecycle timings but does
    # not split PTX read, module creation and GAS build into exact subphases.
    # Preserve the aggregates in the endpoint partition and leave diagnostic
    # components null.
    validate_component_diagnostics(components)
    return {
        "implementation_import_ns": import_ns,
        "post_import_to_first_correct_result_ns": endpoint_ns,
        "endpoint_partition_ns": partition,
        "partition_reconciliation": reconciliation,
        "component_diagnostics_ns": components,
        "steady_complete_execution": steady,
        "identity": identity,
        "evidence": {
            **evidence,
            "output_sha256": TASK_CONTRACTS[args.task]["public_output_sha256"],
            "phase_instrumentation": phase_instrumentation,
            "public_output": _public_output(args.task, latest),
            "lifecycle": lifecycle,
            "source_compilation_inside_endpoint": False,
            "runtime_preload_receipt": preload_receipt,
        },
    }


def _write_create(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        payload = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=PYTHON_ARMS, required=True)
    parser.add_argument("--task", choices=(RELATION_TASK, TRIANGLE_TASK), required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument(
        "--classification",
        choices=("exploration", "formal"),
        default="exploration",
    )
    parser.add_argument("--expected-source-commit")
    parser.add_argument("--candidate-manifest", type=Path)
    parser.add_argument("--precompiled-ptx", type=Path)
    parser.add_argument("--compaction-cubin", type=Path)
    parser.add_argument("--pyoptix-source", type=Path)
    parser.add_argument("--pyoptix-build-receipt", type=Path)
    parser.add_argument("--expected-optix-sdk")
    parser.add_argument(
        "--phase-instrumentation",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument("--warmups", type=int, default=STEADY_WARMUPS)
    parser.add_argument("--repetitions", type=int, default=STEADY_REPETITIONS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require_formal_cache_policy()
    if not 0 <= args.block < BLOCKS or args.warmups <= 0 or args.repetitions <= 0:
        raise ValueError("Goal5848 worker timing arguments are invalid")
    git_identity = _git_identity()
    if args.classification == "formal" and (
        args.expected_source_commit is None
        or git_identity["commit"] != args.expected_source_commit
        or git_identity["clean"] is not True
    ):
        raise RuntimeError("Goal5848 formal worker source identity differs")
    if args.arm == RTDL_ARM and args.candidate_manifest is None:
        raise ValueError("RTDL arm requires --candidate-manifest")
    if args.arm != RTDL_ARM and args.precompiled_ptx is None:
        raise ValueError("PyOptix arm requires --precompiled-ptx")
    if args.arm != RTDL_ARM and any(
        value is None
        for value in (
            args.pyoptix_source,
            args.pyoptix_build_receipt,
            args.expected_optix_sdk,
        )
    ):
        raise ValueError("PyOptix arm requires pinned deployment evidence")
    if (
        args.arm == STRONG_PYOPTIX_ARM
        and args.task == RELATION_TASK
        and args.compaction_cubin is None
    ):
        raise ValueError("strong relation arm requires --compaction-cubin")
    runner = {
        RTDL_ARM: _run_rtdl,
        IDIOMATIC_PYOPTIX_ARM: _run_idiomatic_pyoptix,
        STRONG_PYOPTIX_ARM: _run_strong_pyoptix,
    }[args.arm]
    measurements = runner(args)
    result: dict[str, object] = {
        "schema": WORKER_SCHEMA,
        "status": "PASS__GOAL5848_WORKER",
        "arm": args.arm,
        "task": args.task,
        "block": args.block,
        "worker_id": args.worker_id,
        "classification": args.classification,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "python": sys.version.split()[0],
        "source": git_identity,
        "hardware": _hardware(),
        "measurements": measurements,
        "claim_boundary": {
            "exploration_or_formal_classification_owned_by_controller": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
