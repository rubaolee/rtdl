"""Standard-library-only contracts for the Goal5848 experiment.

The module owns schedule and receipt shape, not any provider implementation.
It is intentionally importable by the independent authority without RTDL,
PyOptix, CUDA, NumPy, or Numba.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from collections.abc import Mapping, Sequence

from .workloads import (
    RELATION_COUNT,
    RELATION_INPUT_SHA256,
    RELATION_OUTPUT_SHA256,
    RELATION_TASK,
    TRIANGLE_COUNT,
    TRIANGLE_INPUT_SHA256,
    TRIANGLE_OUTPUT_SHA256,
    TRIANGLE_TASK,
)

WORKER_SCHEMA = "rtdl.goal5848.strong_baseline.worker.v1"
CONTROLLER_SCHEMA = "rtdl.goal5848.strong_baseline.controller.v1"
PREREGISTRATION_SCHEMA = "rtdl.goal5848.preregistration.v1"
PREFLIGHT_SCHEMA = "rtdl.goal5848.timer_free_preflight.v1"
PREFLIGHT_PASS_STATUS = (
    "PASS__ALL_FOUR_PRIMARY_ARMS_EXACT_AND_BASELINES_COMPETENT"
)
INSTRUMENTATION_AUTHORITY_SCHEMA = (
    "rtdl.goal5848.instrumentation_overhead_authority.v2"
)
INSTRUMENTATION_AUTHORITY_STATUS = (
    "PASS__PAIRED_FRESH_PROCESS_INSTRUMENTATION_OVERHEAD_WITHIN_FIVE_PERCENT"
)

PREREGISTRATION_ARTIFACT_ARGUMENTS = {
    "candidate_manifest": "candidate_manifest",
    "predecessor_candidate_manifest": "predecessor_candidate_manifest",
    "precompiled_ptx": "precompiled_ptx",
    "compaction_cubin": "compaction_cubin",
    "device_artifact_build_receipt": "device_artifact_build_receipt",
    "pyoptix_build_receipt": "pyoptix_build_receipt",
    "direct_worker": "direct_worker",
    "direct_build_receipt": "direct_build_receipt",
    "derivation_receipt": "derivation_receipt",
    "aot_cache_authority": "aot_cache_authority",
}

RTDL_ARM = "A_RTDL_AOT_PUBLIC"
IDIOMATIC_PYOPTIX_ARM = "B_IDIOMATIC_PINNED_PYOPTIX"
STRONG_PYOPTIX_ARM = "C_STRONG_DEVICE_CONTINUATION_PYOPTIX"
DIRECT_OPTIX_ARM = "D_DIRECT_CUDA_OPTIX"
PREDECESSOR_RTDL_ARM = "E_GOAL5847_RTDL_CONTROL"
PRIMARY_ARMS = (
    RTDL_ARM,
    IDIOMATIC_PYOPTIX_ARM,
    STRONG_PYOPTIX_ARM,
    DIRECT_OPTIX_ARM,
)
ARMS = (*PRIMARY_ARMS, PREDECESSOR_RTDL_ARM)
TASKS = (RELATION_TASK, TRIANGLE_TASK)

BLOCKS = 8
INSTRUMENTATION_BLOCKS = 8
INSTRUMENTATION_MODES = ("off", "on")
STEADY_WARMUPS = 16
STEADY_REPETITIONS = 128
POST_IMPORT_RATIO_LIMIT_PPM = 1_200_000
POST_IMPORT_BLOCK_RATIO_LIMIT_PPM = 1_350_000
PUBLIC_DIRECT_RATIO_LIMIT_PPM = 1_200_000
SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM = 1_050_000
STRONG_COMPETENCE_RATIO_LIMIT_PPM = 1_050_000
PARTITION_ABSOLUTE_TOLERANCE_NS = 2_000_000
PARTITION_RELATIVE_TOLERANCE_PPM = 10_000
INSTRUMENTATION_OVERHEAD_LIMIT_PPM = 50_000
AOT_HIT_REPETITIONS = 5
AOT_HIT_ABSOLUTE_LIMIT_NS = 1_000_000_000
AOT_HIT_COLD_RATIO_LIMIT_PPM = 100_000

# These wall intervals are pairwise disjoint and sum to the post-import
# endpoint. Concurrent component timers belong in COMPONENT_DIAGNOSTIC_KEYS.
PARTITION_KEYS = (
    "canonical_input_construction",
    "signed_deployment_install",
    "parallel_artifact_and_provider_admission",
    "provider_artifact_bind_wait",
    "static_input_deployment",
    "dynamic_input_deployment",
    "native_prepare",
    "first_complete_execution",
    "public_output_validation",
    "unattributed_control_plane",
)

COMPONENT_DIAGNOSTIC_KEYS = (
    "trust_root_and_package_discovery",
    "artifact_metadata_decode",
    "artifact_bytes_read_and_hash",
    "authority_bytes_read_and_hash",
    "rsa_verification",
    "native_image_read_and_hash",
    "native_dso_load_and_symbol_binding",
    "cuda_primary_context",
    "optix_module_program_pipeline_sbt",
    "provider_unexplained_wait",
    "static_input_validation_and_allocation",
    "dynamic_input_validation_and_allocation",
    "host_to_device_transfer",
    "gas_build_or_reuse",
)

TASK_CONTRACTS = {
    RELATION_TASK: {
        "input_sha256": RELATION_INPUT_SHA256,
        "public_output_sha256": RELATION_OUTPUT_SHA256,
        "primitive_count": RELATION_COUNT,
        "query_count": RELATION_COUNT,
        "public_output_contract": "canonical_u32_pair_rows.v1",
        "required_optix_launch_count": 2,
        "public_output_bytes": RELATION_COUNT * 2 * 4,
    },
    TRIANGLE_TASK: {
        "input_sha256": TRIANGLE_INPUT_SHA256,
        "public_output_sha256": TRIANGLE_OUTPUT_SHA256,
        "primitive_count": TRIANGLE_COUNT,
        "query_count": TRIANGLE_COUNT,
        "public_output_contract": "checked_u64_scalar.v1",
        "required_optix_launch_count": 1,
        "public_output_bytes": 8,
    },
}

_RTDL_ROUTE_IDENTITIES = {
    RELATION_TASK: "v4_callback_ir:custom_aabb_bounded_relation_v1",
    TRIANGLE_TASK: "v4_builtin_triangle_callback_ir:checked_reduction_v1",
}
_RTDL_PROGRAM_BUNDLES = {
    RELATION_TASK: "v4_custom_aabb_bounded_relation_composed",
    TRIANGLE_TASK: "v4_builtin_triangle_checked_reduction_composed",
}
_DIRECT_TASKS = {
    RELATION_TASK: "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED",
    TRIANGLE_TASK: "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED",
}
_COMPACT_TRAVERSAL_SCHEMA = (
    "rtdl.physical_execution.compact_traversal_receipt.v1"
)
_COMPACT_STAMP_LENGTH = 19


def rtdl_program_bundles(task: str) -> tuple[str, ...]:
    """Return the one physical bundle authorized for a frozen task."""

    try:
        return (_RTDL_PROGRAM_BUNDLES[task],)
    except KeyError as error:
        raise ValueError(
            f"Goal5848 task has no RTDL program bundle: {task}"
        ) from error


def direct_worker_task(task: str) -> str:
    """Map a Goal5848 task to the frozen Goal5802 Direct worker task."""

    try:
        return _DIRECT_TASKS[task]
    except KeyError as error:
        raise ValueError(
            f"Goal5848 task has no Direct worker mapping: {task}"
        ) from error


def build_instrumentation_schedule() -> tuple[dict[str, object], ...]:
    """Build the frozen paired fresh-process instrumentation schedule."""

    rows: list[dict[str, object]] = []
    sequence = 0
    for block in range(INSTRUMENTATION_BLOCKS):
        task_order = TASKS if block % 2 == 0 else tuple(reversed(TASKS))
        for task in task_order:
            mode_order = (
                INSTRUMENTATION_MODES
                if (block + TASKS.index(task)) % 2 == 0
                else tuple(reversed(INSTRUMENTATION_MODES))
            )
            for mode in mode_order:
                rows.append({
                    "sequence_index": sequence,
                    "block": block,
                    "task": task,
                    "mode": mode,
                    "worker_id": (
                        f"G5848_INSTRUMENTATION_B{block:02d}_{task}_"
                        f"{mode.upper()}"
                    ),
                })
                sequence += 1
    return tuple(rows)


def instrumentation_protocol() -> dict[str, object]:
    """Return the exact nonformal instrumentation authority contract."""

    schedule = list(build_instrumentation_schedule())
    return {
        "blocks": INSTRUMENTATION_BLOCKS,
        "modes": list(INSTRUMENTATION_MODES),
        "worker_count": len(schedule),
        "schedule": schedule,
        "schedule_sha256": digest(schedule),
        "endpoint": "rtdl_post_import_to_first_exact_public_result",
        "estimator": (
            "max_zero_median_of_within_block_on_over_off_ratios_minus_one"
        ),
        "limit_ppm": INSTRUMENTATION_OVERHEAD_LIMIT_PPM,
        "formal_estimator_inclusion": False,
    }


def aot_cache_protocol() -> dict[str, object]:
    return {
        "fresh_process_hit_repetitions_per_task": AOT_HIT_REPETITIONS,
        "task_count": len(TASKS),
        "worker_count": AOT_HIT_REPETITIONS * len(TASKS),
        "absolute_limit_ns": AOT_HIT_ABSOLUTE_LIMIT_NS,
        "relative_to_cold_limit_ppm": AOT_HIT_COLD_RATIO_LIMIT_PPM,
        "producer_invocation_count_across_hits": 0,
        "compiler_module_count_across_hits": 0,
        "nvrtc_mapping_count_across_hits": 0,
        "included_in_formal_estimators": False,
    }


class Goal5848ContractError(ValueError):
    """A frozen experiment contract or receipt is malformed."""


def strict_json_loads(payload: str | bytes | bytearray, *, label: str) -> object:
    """Decode one authority object without duplicate keys or non-finite values."""

    def object_from_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise Goal5848ContractError(
                    f"{label} contains duplicate JSON key: {key}"
                )
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise Goal5848ContractError(
            f"{label} contains non-finite JSON value: {value}"
        )

    try:
        return json.loads(
            payload,
            object_pairs_hook=object_from_pairs,
            parse_constant=reject_constant,
        )
    except Goal5848ContractError:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        raise Goal5848ContractError(f"{label} is not strict JSON") from error


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def require_formal_cache_policy() -> None:
    """Fail closed unless both driver and RTDL OptiX caches are disabled."""

    if (
        os.environ.get("CUDA_CACHE_DISABLE") != "1"
        or os.environ.get("RTDL_OPTIX_DISK_CACHE_POLICY") != "disabled"
    ):
        raise RuntimeError(
            "Goal5848 requires CUDA_CACHE_DISABLE=1 and "
            "RTDL_OPTIX_DISK_CACHE_POLICY=disabled"
        )


def _is_sha256(value: object) -> bool:
    return type(value) is str and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _physical_program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _native_audit_mix_u64(state: int, value: int) -> int:
    mask = (1 << 64) - 1
    state &= mask
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value ^= value >> 31
    value &= mask
    return (
        state
        ^ (
            value
            + 0x9E3779B97F4A7C15
            + ((state << 6) & mask)
            + (state >> 2)
        )
    ) & mask


def _repeated_native_audit_mix(value: int, count: int) -> int:
    state = 0
    for _ in range(count):
        state = _native_audit_mix_u64(state, value)
    return state


def _validate_rtdl_traversal_receipt(
    receipt: object,
    *,
    task: str,
    provider_library_sha256: object,
) -> None:
    expected_fields = {
        "schema",
        "provider_library_sha256",
        "route_identity",
        "semantic_digest",
        "output_digest",
        "physical_executor_classification",
        "expected_program_bundle",
        "expected_program_bundle_id",
        "expected_program_observed_at_receipt_edge",
        "native_stamp",
        "receipt_sha256",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != expected_fields:
        raise Goal5848ContractError("RTDL traversal receipt fields differ")
    body = dict(receipt)
    seal = body.pop("receipt_sha256", None)
    bundle = _RTDL_PROGRAM_BUNDLES[task]
    bundle_id = _physical_program_bundle_id(bundle)
    launches = int(TASK_CONTRACTS[task]["required_optix_launch_count"])
    raygen_count = 2 * RELATION_COUNT if task == RELATION_TASK else TRIANGLE_COUNT
    if (
        receipt.get("schema") != _COMPACT_TRAVERSAL_SCHEMA
        or not _is_sha256(provider_library_sha256)
        or receipt.get("provider_library_sha256") != provider_library_sha256
        or receipt.get("route_identity") != _RTDL_ROUTE_IDENTITIES[task]
        or not _is_sha256(receipt.get("semantic_digest"))
        or receipt.get("output_digest")
        != TASK_CONTRACTS[task]["public_output_sha256"]
        or receipt.get("physical_executor_classification")
        != "optix_traversal_observed"
        or receipt.get("expected_program_bundle") != bundle
        or receipt.get("expected_program_bundle_id") != bundle_id
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
        or seal != digest(body)
    ):
        raise Goal5848ContractError("RTDL traversal receipt envelope differs")
    stamp = receipt.get("native_stamp")
    if (
        not isinstance(stamp, list)
        or len(stamp) != _COMPACT_STAMP_LENGTH
        or any(type(value) is not int or not 0 <= value < 1 << 64 for value in stamp)
    ):
        raise Goal5848ContractError("RTDL traversal native stamp differs")
    (
        nonce_hi,
        nonce_lo,
        execution_sequence,
        attempted_launches,
        successful_launches,
        failed_launches,
        complete_context_launches,
        incomplete_context_launches,
        context_bind_count,
        observed_raygen_count,
        first_bundle_id,
        last_bundle_id,
        first_traversable,
        last_traversable,
        pending_context,
        session_error,
        incomplete_callsite_count,
        program_bundle_mix,
        traversable_mix,
    ) = stamp
    expected_traversable_mix = _native_audit_mix_u64(0, first_traversable)
    if launches == 2:
        expected_traversable_mix = _native_audit_mix_u64(
            expected_traversable_mix, last_traversable
        )
    if (
        nonce_hi == 0
        or nonce_lo == 0
        or execution_sequence == 0
        or nonce_lo != execution_sequence
        or attempted_launches != launches
        or successful_launches != launches
        or failed_launches != 0
        or complete_context_launches != launches
        or incomplete_context_launches != 0
        or context_bind_count != launches
        or observed_raygen_count != raygen_count
        or first_bundle_id != bundle_id
        or last_bundle_id != bundle_id
        or first_traversable == 0
        or last_traversable == 0
        or (launches == 1 and first_traversable != last_traversable)
        or pending_context != 0
        or session_error != 0
        or incomplete_callsite_count != 0
        or program_bundle_mix != _repeated_native_audit_mix(bundle_id, launches)
        or traversable_mix != expected_traversable_mix
    ):
        raise Goal5848ContractError("RTDL traversal native stamp differs")


def _validate_rtdl_evidence(
    evidence: Mapping[str, object],
    identity: object,
    *,
    task: str,
) -> None:
    if not isinstance(identity, Mapping):
        raise Goal5848ContractError("RTDL deployment identity is absent")
    phases = evidence.get("provider_initialization_phases_ns")
    if (
        evidence.get("runtime_compiler_attempt_count_before") != 0
        or evidence.get("runtime_compiler_attempt_count_after") != 0
        or evidence.get("runtime_compiler_modules") != []
        or evidence.get("nvrtc_mappings") != []
        or evidence.get("latest_output_sha256")
        != TASK_CONTRACTS[task]["public_output_sha256"]
        or evidence.get("phase_instrumentation") is not True
        or not isinstance(phases, Mapping)
        or not phases
        or any(type(value) is not int or value < 0 for value in phases.values())
    ):
        raise Goal5848ContractError("formal RTDL execution evidence differs")
    _validate_rtdl_traversal_receipt(
        evidence.get("diagnostic_traversal_receipt"),
        task=task,
        provider_library_sha256=identity.get("native_library_sha256"),
    )


def _validate_idiomatic_pyoptix_evidence(
    evidence: Mapping[str, object], *, task: str
) -> None:
    expected_host_continuation = task == RELATION_TASK
    expected_raw_count = 2 * RELATION_COUNT if expected_host_continuation else None
    if (
        evidence.get("source_compilation_inside_endpoint") is not False
        or evidence.get("phase_instrumentation") is not True
        or evidence.get("host_continuation_disclosed")
        is not expected_host_continuation
        or evidence.get("raw_event_count") != expected_raw_count
    ):
        raise Goal5848ContractError("idiomatic PyOptix execution evidence differs")


def _validate_strong_pyoptix_evidence(
    evidence: Mapping[str, object], *, task: str
) -> None:
    lifecycle = evidence.get("lifecycle")
    preload = evidence.get("runtime_preload_receipt")
    if (
        evidence.get("source_compilation_inside_endpoint") is not False
        or evidence.get("phase_instrumentation") is not True
        or evidence.get("optix_module_disk_cache_enabled") is not False
        or evidence.get("optix_validation_mode") != "OFF"
        or evidence.get("optix_log_callback_mode") != "OFF"
        or evidence.get("operation_evidence_source")
        != "UNTIMED_PREWORKER_KAT_AND_EXACT_SOURCE_BOUNDARY"
        or evidence.get("live_execute_guard_inside_timer") is not False
        or not isinstance(lifecycle, Mapping)
        or lifecycle.get("prepared_input_reused") is not True
        or lifecycle.get("dynamic_device_upload_call_count") != 0
        or lifecycle.get("dynamic_device_upload_bytes") != 0
        or lifecycle.get("dynamic_accel_build_count") != 0
        or lifecycle.get("dynamic_input_generation") != 1
        or not isinstance(preload, Mapping)
        or preload.get("schema") != "rtdl.goal5802.python_runtime_preload.v1"
        or preload.get("status") != "PASS__BEFORE_PRIMARY_CLOCK"
        or preload.get("compiler_only_nvrtc_loaded") is not False
        or preload.get("prebuilt_ptx_deployment") is not True
        or preload.get("runtime_import_inside_primary_timer") is not False
    ):
        raise Goal5848ContractError("strong PyOptix lifecycle evidence differs")
    if task == RELATION_TASK:
        valid = (
            evidence.get("output") == evidence.get("public_output")
            and evidence.get("raw_event_count") == 2 * RELATION_COUNT
            and evidence.get("semantic_unique_count") == RELATION_COUNT
            and evidence.get("device_status") == 0
            and evidence.get("device_overflow") == 0
            and evidence.get("optix_launch_count") == 2
            and evidence.get("semantic_compaction_launch_count") == 1
            and evidence.get("total_auxiliary_cuda_kernel_launch_count") == 1
        )
    else:
        valid = (
            evidence.get("reduced_u64") == evidence.get("public_output")
            and evidence.get("device_status") == 0
            and evidence.get("launch_count") == 1
            and evidence.get("semantic_compaction_launch_count") == 0
            and evidence.get("total_auxiliary_cuda_kernel_launch_count") == 0
        )
    if (
        not valid
        or evidence.get("application_output_d2h_bytes")
        != TASK_CONTRACTS[task]["public_output_bytes"]
        or evidence.get("per_ray_d2h_bytes") != 0
        or evidence.get("per_ray_host_materialized") is not False
        or evidence.get("status_output_commit_blocking_boundary_count") != 2
    ):
        raise Goal5848ContractError("strong PyOptix operation evidence differs")


def _validate_direct_evidence(
    evidence: Mapping[str, object],
    *,
    task: str,
    worker_id: object,
    steady_samples: list[int],
) -> None:
    direct = evidence.get("direct_worker_receipt")
    if (
        evidence.get("source_compilation_inside_endpoint") is not False
        or not _is_sha256(evidence.get("direct_stdout_sha256"))
        or not _is_sha256(evidence.get("direct_stderr_sha256"))
        or not isinstance(direct, Mapping)
        or direct.get("schema") != "rtdl.goal5802.direct_scalar.worker.v1"
        or direct.get("status") != "PASS"
        or direct.get("arm") != "A_DIRECT_CUDA_OPTIX"
        or direct.get("worker_id") != worker_id
        or direct.get("task") != _DIRECT_TASKS[task]
        or direct.get("regime") != "STEADY_E2E"
        or direct.get("registered_performance_timing_count")
        != STEADY_REPETITIONS
        or direct.get("execute_or_regime_durations_ns") != steady_samples
    ):
        raise Goal5848ContractError("Direct worker execution evidence differs")
    correctness = direct.get("correctness")
    ledger = direct.get("operation_ledger")
    lifecycle = direct.get("execution_lifecycle_receipts")
    if (
        not isinstance(correctness, Mapping)
        or correctness.get("oracle_exact") is not True
        or not isinstance(ledger, Mapping)
        or ledger.get("optix_launch_count")
        != TASK_CONTRACTS[task]["required_optix_launch_count"]
        or ledger.get("semantic_compaction_launch_count")
        != (1 if task == RELATION_TASK else 0)
        or ledger.get("application_output_d2h_bytes")
        != TASK_CONTRACTS[task]["public_output_bytes"]
        or ledger.get("per_ray_d2h_bytes") != 0
        or ledger.get("status_output_commit_blocking_boundary_count") != 2
        or not isinstance(lifecycle, list)
        or len(lifecycle) != STEADY_WARMUPS + STEADY_REPETITIONS
        or any(not isinstance(row, Mapping) for row in lifecycle)
        or lifecycle[0].get("prepared_input_reused") is not False
        or any(
            row.get("prepared_input_reused") is not True for row in lifecycle[1:]
        )
    ):
        raise Goal5848ContractError("Direct physical operation evidence differs")
    if task == RELATION_TASK:
        valid = (
            correctness.get("canonical_rows") == evidence.get("public_output")
            and correctness.get("canonical_row_count") == RELATION_COUNT
            and correctness.get("raw_event_count") == 2 * RELATION_COUNT
            and correctness.get("semantic_unique_count") == RELATION_COUNT
            and correctness.get("device_status") == 0
            and correctness.get("device_overflow") == 0
        )
    else:
        valid = (
            correctness.get("reduced_u64") == evidence.get("public_output")
            and correctness.get("device_status") == 0
        )
    if not valid:
        raise Goal5848ContractError("Direct correctness evidence differs")


def integer_median(values: Sequence[int]) -> int:
    if not values or any(type(value) is not int for value in values):
        raise Goal5848ContractError("median requires nonempty exact integers")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def ratio_ppm(numerator: int, denominator: int) -> int:
    if type(numerator) is not int or numerator < 0:
        raise Goal5848ContractError("ratio numerator must be a nonnegative int")
    if type(denominator) is not int or denominator <= 0:
        raise Goal5848ContractError("ratio denominator must be a positive int")
    return (numerator * 1_000_000 + denominator // 2) // denominator


def build_schedule() -> tuple[dict[str, object], ...]:
    """Build the frozen balanced schedule including separate predecessor rows."""

    rows: list[dict[str, object]] = []
    sequence = 0
    for block in range(BLOCKS):
        task_order = TASKS if block % 2 == 0 else tuple(reversed(TASKS))
        for task_position, task in enumerate(task_order):
            shift = (block + 2 * TASKS.index(task)) % len(ARMS)
            arm_order = ARMS[shift:] + ARMS[:shift]
            for arm_position, arm in enumerate(arm_order):
                rows.append({
                    "sequence_index": sequence,
                    "block": block,
                    "task": task,
                    "task_position": task_position,
                    "arm": arm,
                    "arm_position": arm_position,
                    "comparison_role": (
                        "REGRESSION_CONTROL"
                        if arm == PREDECESSOR_RTDL_ARM
                        else "PRIMARY"
                    ),
                    "worker_id": (
                        f"G5848_S{sequence:03d}_B{block:02d}_{task}_{arm}"
                    ),
                })
                sequence += 1
    return tuple(rows)


def validate_schedule(rows: Sequence[Mapping[str, object]]) -> None:
    expected_count = BLOCKS * len(TASKS) * len(ARMS)
    if len(rows) != expected_count:
        raise Goal5848ContractError("schedule row count differs")
    if [row.get("sequence_index") for row in rows] != list(
        range(expected_count)
    ):
        raise Goal5848ContractError("schedule sequence differs")
    if len({row.get("worker_id") for row in rows}) != expected_count:
        raise Goal5848ContractError("schedule worker ids are not unique")
    counts = Counter((row.get("task"), row.get("arm")) for row in rows)
    expected = Counter(
        {(task, arm): BLOCKS for task in TASKS for arm in ARMS}
    )
    if counts != expected:
        raise Goal5848ContractError("schedule task/arm balance differs")
    for task in TASKS:
        for arm in ARMS:
            positions = Counter(
                row.get("arm_position")
                for row in rows
                if row.get("task") == task and row.get("arm") == arm
            )
            if (
                set(positions) != set(range(len(ARMS)))
                or max(positions.values()) - min(positions.values()) > 1
            ):
                raise Goal5848ContractError(
                    "schedule arm-position balance differs"
                )
    for block in range(BLOCKS):
        for task in TASKS:
            selected = [
                row for row in rows
                if row.get("block") == block and row.get("task") == task
            ]
            if Counter(row.get("arm") for row in selected) != Counter(ARMS):
                raise Goal5848ContractError("within-block arm balance differs")
            regression = [
                row for row in selected
                if row.get("arm") == PREDECESSOR_RTDL_ARM
            ]
            if len(regression) != 1 or regression[0].get(
                "comparison_role"
            ) != "REGRESSION_CONTROL":
                raise Goal5848ContractError("predecessor schedule differs")


def validate_phase_partition(
    partition: Mapping[str, object],
    *,
    endpoint_ns: int,
    uninstrumented_endpoint_median_ns: int | None = None,
    measured_instrumentation_overhead_ns: int | None = None,
) -> dict[str, int]:
    """Reconcile one non-overlapping post-import endpoint partition."""

    if set(partition) != set(PARTITION_KEYS):
        raise Goal5848ContractError("endpoint partition keys differ")
    values: dict[str, int] = {}
    for name in PARTITION_KEYS:
        value = partition[name]
        if type(value) is not int or value < 0:
            raise Goal5848ContractError(f"invalid partition duration: {name}")
        values[name] = value
    if type(endpoint_ns) is not int or endpoint_ns <= 0:
        raise Goal5848ContractError("endpoint duration must be positive")
    partition_total = sum(values.values())
    error = abs(endpoint_ns - partition_total)
    tolerance = max(
        PARTITION_ABSOLUTE_TOLERANCE_NS,
        (endpoint_ns * PARTITION_RELATIVE_TOLERANCE_PPM) // 1_000_000,
    )
    if error > tolerance:
        raise Goal5848ContractError("endpoint partition does not reconcile")
    if (uninstrumented_endpoint_median_ns is None) != (
        measured_instrumentation_overhead_ns is None
    ):
        raise Goal5848ContractError(
            "instrumentation overhead gate requires both measurements"
        )
    if uninstrumented_endpoint_median_ns is not None:
        if (
            type(uninstrumented_endpoint_median_ns) is not int
            or uninstrumented_endpoint_median_ns <= 0
        ):
            raise Goal5848ContractError("uninstrumented endpoint is invalid")
        if (
            type(measured_instrumentation_overhead_ns) is not int
            or measured_instrumentation_overhead_ns < 0
        ):
            raise Goal5848ContractError("instrumentation overhead is invalid")
        overhead_limit = (
            uninstrumented_endpoint_median_ns
            * INSTRUMENTATION_OVERHEAD_LIMIT_PPM
        ) // 1_000_000
        if measured_instrumentation_overhead_ns > overhead_limit:
            raise Goal5848ContractError("instrumentation overhead exceeds gate")
    return {
        "endpoint_ns": endpoint_ns,
        "partition_total_ns": partition_total,
        "absolute_error_ns": error,
        "tolerance_ns": tolerance,
    }


def validate_component_diagnostics(
    diagnostics: Mapping[str, object],
) -> None:
    if set(diagnostics) != set(COMPONENT_DIAGNOSTIC_KEYS):
        raise Goal5848ContractError("component diagnostic keys differ")
    for name, value in diagnostics.items():
        if value is not None and (type(value) is not int or value < 0):
            raise Goal5848ContractError(
                f"invalid component diagnostic duration: {name}"
            )


def _validated_timing_summary(
    value: object,
    *,
    repetitions: int,
    label: str,
) -> dict[str, object]:
    if not isinstance(value, Mapping) or set(value) != {
        "sample_count",
        "samples_ns",
        "minimum_ns",
        "median_ns",
        "maximum_ns",
    }:
        raise Goal5848ContractError(f"{label} timing summary differs")
    samples = value["samples_ns"]
    if (
        not isinstance(samples, list)
        or len(samples) != repetitions
        or any(type(item) is not int or item <= 0 for item in samples)
        or value["sample_count"] != repetitions
        or value["minimum_ns"] != min(samples)
        or value["median_ns"] != integer_median(samples)
        or value["maximum_ns"] != max(samples)
    ):
        raise Goal5848ContractError(f"{label} timing samples differ")
    return dict(value)


def validate_worker_receipt(
    value: Mapping[str, object],
    *,
    expected_row: Mapping[str, object],
    expected_source_commit: str,
    expected_predecessor_commit: str,
) -> dict[str, object]:
    """Validate one normalized fresh-process receipt without trusting a worker."""

    required = {
        "schema",
        "status",
        "arm",
        "task",
        "block",
        "worker_id",
        "classification",
        "warmups",
        "repetitions",
        "python",
        "source",
        "hardware",
        "measurements",
        "claim_boundary",
        "result_sha256",
    }
    if set(value) != required:
        raise Goal5848ContractError("worker receipt fields differ")
    unsigned = dict(value)
    seal = unsigned.pop("result_sha256")
    if seal != digest(unsigned):
        raise Goal5848ContractError("worker receipt seal differs")
    for name in ("arm", "task", "block", "worker_id"):
        if value[name] != expected_row[name]:
            raise Goal5848ContractError(f"worker schedule binding differs: {name}")
    if (
        value["schema"] != WORKER_SCHEMA
        or value["status"] != "PASS__GOAL5848_WORKER"
        or value["classification"] != "formal"
        or value["warmups"] != STEADY_WARMUPS
        or value["repetitions"] != STEADY_REPETITIONS
    ):
        raise Goal5848ContractError("formal worker contract differs")
    source = value["source"]
    expected_commit = (
        expected_predecessor_commit
        if value["arm"] == PREDECESSOR_RTDL_ARM
        else expected_source_commit
    )
    if (
        not isinstance(source, Mapping)
        or set(source) != {"commit", "tree", "status", "clean"}
        or source["commit"] != expected_commit
        or source["clean"] is not True
        or source["status"] != ""
    ):
        raise Goal5848ContractError("worker source identity differs")
    hardware = value["hardware"]
    if (
        not isinstance(hardware, Mapping)
        or set(hardware) != {
            "gpu_name",
            "gpu_uuid",
            "driver_version",
            "memory_mib",
            "compute_capability",
        }
        or not all(
            isinstance(hardware[name], str) and hardware[name]
            for name in (
                "gpu_name",
                "gpu_uuid",
                "driver_version",
                "compute_capability",
            )
        )
        or type(hardware["memory_mib"]) is not int
        or hardware["memory_mib"] <= 0
    ):
        raise Goal5848ContractError("worker hardware identity differs")
    measurements = value["measurements"]
    if not isinstance(measurements, Mapping):
        raise Goal5848ContractError("worker measurements are absent")
    endpoint = measurements.get("post_import_to_first_correct_result_ns")
    partition = measurements.get("endpoint_partition_ns")
    if value["arm"] == DIRECT_OPTIX_ARM:
        if endpoint is not None or partition is not None \
                or measurements.get("partition_reconciliation") is not None:
            raise Goal5848ContractError(
                "Direct arm must not invent a Python post-import endpoint"
            )
    else:
        if type(endpoint) is not int or endpoint <= 0:
            raise Goal5848ContractError("worker post-import endpoint differs")
        if not isinstance(partition, Mapping):
            raise Goal5848ContractError("worker endpoint partition is absent")
        reconciliation = validate_phase_partition(
            partition, endpoint_ns=endpoint
        )
        if measurements.get("partition_reconciliation") != reconciliation:
            raise Goal5848ContractError(
                "worker partition reconciliation differs"
            )
    components = measurements.get("component_diagnostics_ns")
    if not isinstance(components, Mapping):
        raise Goal5848ContractError("worker component diagnostics are absent")
    validate_component_diagnostics(components)
    steady = _validated_timing_summary(
        measurements.get("steady_complete_execution"),
        repetitions=STEADY_REPETITIONS,
        label="steady complete execution",
    )
    steady_samples = steady.get("samples_ns")
    if not isinstance(steady_samples, list):
        raise Goal5848ContractError("steady timing sample storage differs")
    evidence = measurements.get("evidence")
    identity = measurements.get("identity")
    task = str(value["task"])
    expected_public_output: object = (
        [[index, index] for index in range(RELATION_COUNT)]
        if task == RELATION_TASK
        else sum(1 + index % 7 for index in range(TRIANGLE_COUNT))
    )
    if (
        not isinstance(evidence, Mapping)
        or evidence.get("output_sha256")
        != TASK_CONTRACTS[task]["public_output_sha256"]
        or evidence.get("public_output") != expected_public_output
        or digest(evidence["public_output"])
        != TASK_CONTRACTS[task]["public_output_sha256"]
    ):
        raise Goal5848ContractError("worker output evidence differs")
    arm = str(value["arm"])
    if arm in {RTDL_ARM, PREDECESSOR_RTDL_ARM}:
        _validate_rtdl_evidence(evidence, identity, task=task)
    elif arm == IDIOMATIC_PYOPTIX_ARM:
        _validate_idiomatic_pyoptix_evidence(evidence, task=task)
    elif arm == STRONG_PYOPTIX_ARM:
        _validate_strong_pyoptix_evidence(evidence, task=task)
    elif arm == DIRECT_OPTIX_ARM:
        _validate_direct_evidence(
            evidence,
            task=task,
            worker_id=value["worker_id"],
            steady_samples=steady_samples,
        )
    else:  # pragma: no cover - guarded by the frozen schedule.
        raise Goal5848ContractError("worker arm differs")
    boundary = value["claim_boundary"]
    if (
        not isinstance(boundary, Mapping)
        or boundary.get("public_or_manuscript_claim_authorized") is not False
        or boundary.get("external_review_complete") is not False
    ):
        raise Goal5848ContractError("worker claim boundary differs")
    return dict(value)


def evaluate_complete_transaction(
    receipts: Sequence[Mapping[str, object]],
    *,
    expected_source_commit: str,
    expected_predecessor_commit: str,
) -> dict[str, object]:
    """Recount all Goal5848 performance gates from normalized worker receipts."""

    schedule = build_schedule()
    if len(receipts) != len(schedule):
        raise Goal5848ContractError("transaction worker count differs")
    by_worker_id = {}
    for receipt in receipts:
        worker_id = receipt.get("worker_id")
        if not isinstance(worker_id, str) or worker_id in by_worker_id:
            raise Goal5848ContractError("transaction worker ids differ")
        by_worker_id[worker_id] = receipt
    validated = []
    for row in schedule:
        receipt = by_worker_id.get(row["worker_id"])
        if receipt is None:
            raise Goal5848ContractError("scheduled worker is absent")
        validated.append(validate_worker_receipt(
            receipt,
            expected_row=row,
            expected_source_commit=expected_source_commit,
            expected_predecessor_commit=expected_predecessor_commit,
        ))
    hardware_rows = {
        canonical_bytes(receipt["hardware"]) for receipt in validated
    }
    if len(hardware_rows) != 1:
        raise Goal5848ContractError("transaction spans different GPU identities")

    indexed = {
        (receipt["block"], receipt["task"], receipt["arm"]): receipt
        for receipt in validated
    }

    def metric(receipt: Mapping[str, object], name: str) -> int:
        measurements = receipt["measurements"]
        if not isinstance(measurements, Mapping):
            raise Goal5848ContractError("transaction measurements are absent")
        if name == "post_import":
            value = measurements["post_import_to_first_correct_result_ns"]
        else:
            steady = measurements["steady_complete_execution"]
            if not isinstance(steady, Mapping):
                raise Goal5848ContractError("transaction steady timing is absent")
            value = steady["median_ns"]
        if type(value) is not int:
            raise Goal5848ContractError("transaction timing value differs")
        return value

    def arm(block: int, task: str, name: str) -> Mapping[str, object]:
        return indexed[(block, task, name)]

    result = {}
    for task in TASKS:
        post_import = []
        competence = []
        public_direct = []
        regression = []
        for block in range(BLOCKS):
            post_import.append(ratio_ppm(
                metric(arm(block, task, RTDL_ARM), "post_import"),
                metric(arm(block, task, STRONG_PYOPTIX_ARM), "post_import"),
            ))
            competence.append(ratio_ppm(
                metric(arm(block, task, STRONG_PYOPTIX_ARM), "steady"),
                metric(arm(block, task, IDIOMATIC_PYOPTIX_ARM), "steady"),
            ))
            public_direct.append(ratio_ppm(
                metric(arm(block, task, RTDL_ARM), "steady"),
                metric(arm(block, task, DIRECT_OPTIX_ARM), "steady"),
            ))
            regression.append(ratio_ppm(
                metric(arm(block, task, RTDL_ARM), "steady"),
                metric(arm(block, task, PREDECESSOR_RTDL_ARM), "steady"),
            ))
        task_result = {
            "post_import_rtdl_over_strong_pyoptix_ppm_by_block": post_import,
            "post_import_median_ppm": integer_median(post_import),
            "strong_over_idiomatic_pyoptix_ppm_by_block": competence,
            "strong_competence_median_ppm": integer_median(competence),
            "rtdl_public_over_direct_ppm_by_block": public_direct,
            "public_direct_median_ppm": integer_median(public_direct),
            "successor_over_predecessor_ppm_by_block": regression,
            "successor_predecessor_median_ppm": integer_median(regression),
        }
        task_result["all_performance_gates_pass"] = (
            task_result["post_import_median_ppm"] <= POST_IMPORT_RATIO_LIMIT_PPM
            and max(post_import) <= POST_IMPORT_BLOCK_RATIO_LIMIT_PPM
            and task_result["strong_competence_median_ppm"]
            <= STRONG_COMPETENCE_RATIO_LIMIT_PPM
            and task_result["public_direct_median_ppm"]
            <= PUBLIC_DIRECT_RATIO_LIMIT_PPM
            and task_result["successor_predecessor_median_ppm"]
            <= SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM
        )
        result[task] = task_result
    if not all(row["all_performance_gates_pass"] for row in result.values()):
        raise Goal5848ContractError("one or more Goal5848 performance gates fail")
    return {
        "schema": CONTROLLER_SCHEMA,
        "status": "PASS__GOAL5848_SINGLE_GENERATION_PERFORMANCE_GATES",
        "worker_count": len(validated),
        "retained_steady_sample_count": (
            len(validated) * STEADY_REPETITIONS
        ),
        "tasks": result,
        "hardware": validated[0]["hardware"],
    }


validate_schedule(build_schedule())


__all__ = [
    "AOT_HIT_ABSOLUTE_LIMIT_NS",
    "AOT_HIT_COLD_RATIO_LIMIT_PPM",
    "AOT_HIT_REPETITIONS",
    "ARMS",
    "BLOCKS",
    "COMPONENT_DIAGNOSTIC_KEYS",
    "CONTROLLER_SCHEMA",
    "DIRECT_OPTIX_ARM",
    "IDIOMATIC_PYOPTIX_ARM",
    "INSTRUMENTATION_AUTHORITY_SCHEMA",
    "INSTRUMENTATION_AUTHORITY_STATUS",
    "INSTRUMENTATION_BLOCKS",
    "INSTRUMENTATION_MODES",
    "INSTRUMENTATION_OVERHEAD_LIMIT_PPM",
    "PARTITION_ABSOLUTE_TOLERANCE_NS",
    "PARTITION_KEYS",
    "PARTITION_RELATIVE_TOLERANCE_PPM",
    "POST_IMPORT_BLOCK_RATIO_LIMIT_PPM",
    "POST_IMPORT_RATIO_LIMIT_PPM",
    "PREDECESSOR_RTDL_ARM",
    "PREFLIGHT_PASS_STATUS",
    "PREFLIGHT_SCHEMA",
    "PREREGISTRATION_ARTIFACT_ARGUMENTS",
    "PREREGISTRATION_SCHEMA",
    "PRIMARY_ARMS",
    "PUBLIC_DIRECT_RATIO_LIMIT_PPM",
    "RTDL_ARM",
    "STEADY_REPETITIONS",
    "STEADY_WARMUPS",
    "STRONG_COMPETENCE_RATIO_LIMIT_PPM",
    "STRONG_PYOPTIX_ARM",
    "SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM",
    "TASKS",
    "TASK_CONTRACTS",
    "WORKER_SCHEMA",
    "Goal5848ContractError",
    "aot_cache_protocol",
    "build_instrumentation_schedule",
    "build_schedule",
    "canonical_bytes",
    "digest",
    "direct_worker_task",
    "evaluate_complete_transaction",
    "instrumentation_protocol",
    "integer_median",
    "ratio_ppm",
    "require_formal_cache_policy",
    "rtdl_program_bundles",
    "strict_json_loads",
    "validate_component_diagnostics",
    "validate_phase_partition",
    "validate_schedule",
    "validate_worker_receipt",
]
