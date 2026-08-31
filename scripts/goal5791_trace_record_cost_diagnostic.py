"""CPU-only Goal5791 operation-trace record-cost diagnostic.

This diagnostic is intentionally outside every registered scientific timer.
It measures the Python cost of the exact ``OperationTrace.execute`` record
path against the same no-op callable loop.  It never imports CuPy, CUDA, or
OptiX, and it cannot change a row statistic, confidence interval, threshold,
or verdict.  The frozen result supplies a conservative per-event record-cost
bound and the corresponding five-extra-event bound requested by the
owner-returned Goal5791 review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_operation_evidence import (  # noqa: E402
    OperationKind,
    OperationRequirement,
    OperationSequenceContract,
    OperationTrace,
    preverify_operation_trace_authority,
)


SCHEMA = "rtdl.goal5791.cpu_trace_record_cost_diagnostic.v2"
STATUS = "PASS__CPU_ONLY_TRACE_RECORD_COST_BOUND_FROZEN_BEFORE_WORKER_ZERO"
SUPERSEDED_V1_PATH = (
    "history/internal_docs/"
    "goal5791_cpu_trace_record_cost_diagnostic_20260818.json"
)
SUPERSEDED_V1_FILE_SHA256 = (
    "f6ca8119200c5fcbf9887f2a2ba07f8cc2dfd9c54ca178b1dc2a6474d8a72b54"
)
SUPERSEDED_V1_DIAGNOSTIC_SHA256 = (
    "84a13ee1e7c2fce17ec6351762860cb7a8fbff28061ade44e21056b918fdd551"
)
OWNER_REVIEW_PATH = (
    "history/internal_docs/"
    "review_goal5791_post_external_review_pre_pod_readiness_20260817.md"
)
OWNER_REVIEW_SHA256 = (
    "331212c140cd67e6eb5ba8b3bf71946b983f0d7b9b54e475be6b185ad06fc502"
)
OPERATION_EVIDENCE_PATH = "src/rtdsl/v4_operation_evidence.py"

FUSION_OFF = "fusion_off"
FUSION_ON = "fusion_on"
FUSION_OFF_OPERATIONS = (
    ("maximum_weight.logical_reduce", OperationKind.LOGICAL_REDUCTION),
    ("maximum_weight.scalar_copy_sync", OperationKind.HOST_COPY_SYNCHRONIZATION),
    ("weight_sum.logical_reduce", OperationKind.LOGICAL_REDUCTION),
    ("weight_sum.scalar_copy_sync", OperationKind.HOST_COPY_SYNCHRONIZATION),
    ("weighted_product.materialize", OperationKind.DEVICE_MATERIALIZATION),
    ("weighted_product_sum.logical_reduce", OperationKind.LOGICAL_REDUCTION),
    ("weighted_product_sum.scalar_copy_sync", OperationKind.HOST_COPY_SYNCHRONIZATION),
)
FUSION_ON_OPERATIONS = (
    ("checked_summary.kernel_launch", OperationKind.COMPILER_KERNEL_INVOCATION),
    ("checked_summary.summary_copy_sync", OperationKind.HOST_COPY_SYNCHRONIZATION),
)
OPERATIONS = {FUSION_OFF: FUSION_OFF_OPERATIONS, FUSION_ON: FUSION_ON_OPERATIONS}

WARMUP_BLOCK_COUNT = 16
MEASURED_BLOCK_COUNT = 257
TRACES_PER_BLOCK = 64
UPPER_BOUND_QUANTILE_NUMERATOR = 99
UPPER_BOUND_QUANTILE_DENOMINATOR = 100
EXTRA_EVENT_COUNT_PER_SEGMENT = 5
SMALL_RELATIVE_TO_ABSOLUTE_ROW_DIFFERENCE_MAX_FRACTION = 0.01


class Goal5791TraceCostDiagnosticError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contract(variant: str) -> OperationSequenceContract:
    requirements = tuple(
        OperationRequirement(
            ordinal=index,
            operation_id=operation_id,
            kind=kind,
            fixed_units=1,
            host_visibility_boundary=(
                kind is OperationKind.HOST_COPY_SYNCHRONIZATION
            ),
        )
        for index, (operation_id, kind) in enumerate(OPERATIONS[variant])
    )
    return OperationSequenceContract(
        plan_sha256=hashlib.sha256(
            f"goal5791-trace-cost-{variant}".encode("ascii")
        ).hexdigest(),
        mechanism_id="checked_u64_downstream_reducer_fusion_ablation",
        variant=variant,
        declared_value_count=1,
        requirements=requirements,
    )


def _authority(variant: str) -> object:
    return preverify_operation_trace_authority(
        _contract(variant),
        execution_nonce=(
            "goal5791-cpu-trace-record-cost-diagnostic-" + variant
        ),
        value_count=1,
    )


def _noop() -> None:
    return None


def _baseline_batch(
    *, operations: tuple[tuple[str, OperationKind], ...], repetitions: int,
) -> None:
    action: Callable[[], None] = _noop
    for _ in range(repetitions):
        for _operation_id, _kind in operations:
            action()


def _traced_record_batch(
    *, traces: list[OperationTrace],
    operations: tuple[tuple[str, OperationKind], ...],
) -> None:
    action: Callable[[], None] = _noop
    for trace in traces:
        for operation_id, _kind in operations:
            trace.execute(operation_id, action)


def _elapsed_ns(action: Callable[[], None]) -> int:
    started = time.perf_counter_ns()
    action()
    ended = time.perf_counter_ns()
    if ended < started:
        raise Goal5791TraceCostDiagnosticError("performance counter regressed")
    return ended - started


def _one_variant_block(
    *, variant: str, trace_first: bool,
) -> dict[str, object]:
    operations = OPERATIONS[variant]
    authority = _authority(variant)
    traces = [
        OperationTrace.from_preverified_authority(authority)
        for _ in range(TRACES_PER_BLOCK)
    ]
    baseline = lambda: _baseline_batch(
        operations=operations, repetitions=TRACES_PER_BLOCK)
    traced = lambda: _traced_record_batch(
        traces=traces, operations=operations)
    if trace_first:
        traced_ns = _elapsed_ns(traced)
        baseline_ns = _elapsed_ns(baseline)
        order = "trace_then_baseline"
    else:
        baseline_ns = _elapsed_ns(baseline)
        traced_ns = _elapsed_ns(traced)
        order = "baseline_then_trace"
    # Construction is before both measured intervals and completion is after
    # both.  Completion proves that every measured trace recorded its exact
    # sequence without charging constructor or receipt/seal work to the
    # event-record diagnostic.
    for trace in traces:
        trace.complete()
    event_count = TRACES_PER_BLOCK * len(operations)
    delta_ns = traced_ns - baseline_ns
    per_event_ceiling_ns = math.ceil(delta_ns / event_count)
    return {
        "variant": variant,
        "order": order,
        "trace_ns": traced_ns,
        "baseline_ns": baseline_ns,
        "delta_ns": delta_ns,
        "event_count": event_count,
        "signed_per_event_delta_ceiling_ns": per_event_ceiling_ns,
    }


def _nearest_rank(values: Iterable[int], *, numerator: int, denominator: int) -> int:
    ordered = sorted(values)
    if not ordered:
        raise Goal5791TraceCostDiagnosticError("empty diagnostic sample")
    rank = math.ceil(len(ordered) * numerator / denominator)
    return int(ordered[max(0, rank - 1)])


def build_diagnostic() -> dict[str, object]:
    review_path = ROOT / OWNER_REVIEW_PATH
    operation_path = ROOT / OPERATION_EVIDENCE_PATH
    if _file_sha256(review_path) != OWNER_REVIEW_SHA256:
        raise Goal5791TraceCostDiagnosticError("owner review bytes drifted")

    for warmup_index in range(WARMUP_BLOCK_COUNT):
        for variant in (
            (FUSION_OFF, FUSION_ON)
            if warmup_index % 2 == 0 else (FUSION_ON, FUSION_OFF)
        ):
            _one_variant_block(
                variant=variant,
                trace_first=(warmup_index + len(variant)) % 2 == 0,
            )

    samples: list[dict[str, object]] = []
    for block_index in range(MEASURED_BLOCK_COUNT):
        variant_order = (
            (FUSION_OFF, FUSION_ON)
            if block_index % 2 == 0 else (FUSION_ON, FUSION_OFF)
        )
        block = {
            "block_index": block_index,
            "variant_order": list(variant_order),
            "measurements": [],
        }
        for variant_ordinal, variant in enumerate(variant_order):
            measurement = _one_variant_block(
                variant=variant,
                trace_first=(block_index + variant_ordinal) % 2 == 1,
            )
            block["measurements"].append(measurement)
        samples.append(block)

    per_variant: dict[str, object] = {}
    all_per_event: list[int] = []
    for variant in (FUSION_OFF, FUSION_ON):
        rows = [
            measurement
            for block in samples
            for measurement in block["measurements"]
            if measurement["variant"] == variant
        ]
        per_event = [
            int(row["signed_per_event_delta_ceiling_ns"])
            for row in rows
        ]
        all_per_event.extend(per_event)
        per_variant[variant] = {
            "declared_event_count": len(OPERATIONS[variant]),
            "measured_block_count": len(rows),
            "signed_per_event_delta_ceiling_ns_median": (
                statistics.median(per_event)
            ),
            "signed_per_event_delta_ceiling_ns_p99_nearest_rank": (
                _nearest_rank(
                    per_event,
                    numerator=UPPER_BOUND_QUANTILE_NUMERATOR,
                    denominator=UPPER_BOUND_QUANTILE_DENOMINATOR,
                )
            ),
            "minimum_signed_per_event_delta_ceiling_ns": min(per_event),
            "maximum_signed_per_event_delta_ceiling_ns": max(per_event),
        }
    per_event_bound_ns = max(
        0,
        *(
            int(per_variant[variant][
                "signed_per_event_delta_ceiling_ns_p99_nearest_rank"
            ])
            for variant in (FUSION_OFF, FUSION_ON)
        ),
    )
    five_event_bound_ns = per_event_bound_ns * EXTRA_EVENT_COUNT_PER_SEGMENT

    protocol = {
        "clock": "time.perf_counter_ns",
        "clock_is_cpu_diagnostic_only_not_registered_scientific_timing": True,
        "warmup_block_count": WARMUP_BLOCK_COUNT,
        "measured_block_count": MEASURED_BLOCK_COUNT,
        "traces_per_block": TRACES_PER_BLOCK,
        "variant_order": "alternating_off_on_then_on_off",
        "baseline_trace_order": "alternating_by_block_and_variant_ordinal",
        "baseline_callable": "same_python_noop_callable",
        "trace_constructor_and_complete_outside_measured_interval": True,
        "trace_execute_record_path_inside_measured_interval": True,
        "receipt_hashing_serialization_and_io_inside_interval": False,
        "gpu_cuda_cupy_or_optix_imported_or_used": False,
        "upper_bound_estimator": "max_variant_nearest_rank_p99_per_event_delta",
        "upper_bound_quantile_numerator": UPPER_BOUND_QUANTILE_NUMERATOR,
        "upper_bound_quantile_denominator": UPPER_BOUND_QUANTILE_DENOMINATOR,
        "extra_event_count_per_segment": EXTRA_EVENT_COUNT_PER_SEGMENT,
        "row_total_bound_rule": (
            "per_event_record_cost_bound_ns * 5 * exact_row_segment_count"
        ),
        "small_relative_rule": (
            "row_total_bound_seconds <= 0.01 * absolute_difference_between_"
            "row_median_off_seconds_and_row_median_on_seconds"
        ),
        "small_relative_max_fraction": (
            SMALL_RELATIVE_TO_ABSOLUTE_ROW_DIFFERENCE_MAX_FRACTION
        ),
        "statistic_ci_threshold_or_verdict_correction_allowed": False,
    }
    body = {
        "schema": SCHEMA,
        "goal": 5791,
        "status": STATUS,
        "owner_review_path": OWNER_REVIEW_PATH,
        "owner_review_sha256": OWNER_REVIEW_SHA256,
        "superseded_preformal_diagnostic": {
            "path": SUPERSEDED_V1_PATH,
            "file_sha256": SUPERSEDED_V1_FILE_SHA256,
            "diagnostic_sha256": SUPERSEDED_V1_DIAGNOSTIC_SHA256,
            "disposition": (
                "SUPERSEDED_BEFORE_FORMAL_SOURCE_FREEZE__V1_MEASURED_TRACE_"
                "CONSTRUCTION_DESPITE_PROTOCOL_TEXT__NOT_FORMAL_AUTHORITY"
            ),
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "pod_connection_count": 0,
        },
        "diagnostic_source_path": "scripts/goal5791_trace_record_cost_diagnostic.py",
        "diagnostic_source_sha256": _file_sha256(Path(__file__).resolve()),
        "operation_evidence_path": OPERATION_EVIDENCE_PATH,
        "operation_evidence_file_sha256": _file_sha256(operation_path),
        "operation_ids": {
            variant: [operation_id for operation_id, _kind in OPERATIONS[variant]]
            for variant in (FUSION_OFF, FUSION_ON)
        },
        "protocol": protocol,
        "protocol_sha256": _digest(protocol),
        "environment": {
            "python_executable": str(Path(sys.executable).resolve()),
            "python_executable_sha256": _file_sha256(Path(sys.executable).resolve()),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform_system": platform.system(),
            "platform_release": platform.release(),
            "platform_machine": platform.machine(),
            "platform_processor": platform.processor(),
        },
        "variant_summaries": per_variant,
        "per_event_record_cost_median_ns_all_variants": statistics.median(
            all_per_event
        ),
        "per_event_record_cost_bound_ns": per_event_bound_ns,
        "five_extra_event_differential_bound_per_segment_ns": five_event_bound_ns,
        "five_extra_event_differential_bound_per_segment_seconds": (
            five_event_bound_ns / 1_000_000_000.0
        ),
        "small_relative_max_fraction": (
            SMALL_RELATIVE_TO_ABSOLUTE_ROW_DIFFERENCE_MAX_FRACTION
        ),
        "sample_blocks": samples,
        "cpu_diagnostic_timing_observation_count": (
            MEASURED_BLOCK_COUNT * 4
        ),
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "pod_connection_count": 0,
        "stage_a_created": False,
        "stage_b_created": False,
        "diagnostic_may_change_row_statistic_ci_threshold_or_verdict": False,
        "measured_claim": (
            "end_to_end_compiler_runtime_lowering_including_evidence_overhead"
        ),
        "pure_device_kernel_timing_claimed": False,
    }
    return {**body, "diagnostic_sha256": _digest(body)}


def _write_create_only(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False,
    ) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build_diagnostic()
    _write_create_only(args.output.resolve(), value)
    print(json.dumps({
        "output": str(args.output.resolve()),
        "diagnostic_sha256": value["diagnostic_sha256"],
        "per_event_record_cost_bound_ns": value[
            "per_event_record_cost_bound_ns"
        ],
        "five_extra_event_differential_bound_per_segment_ns": value[
            "five_extra_event_differential_bound_per_segment_ns"
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
