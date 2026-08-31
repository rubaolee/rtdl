"""Outcome-directed Goal5814 optimized full-public-boundary successor.

This module is intentionally separate from the immutable 144-worker formal
transaction and from the immutable v4 diagnostic.  It measures two boundaries
after retaining the exact Lean-PyOptiX lower-bound implementation and replacing
only RTDL host/lifecycle work that v4 proved unnecessary:

* one full public result from a sealed prevalidated input; and
* the ordinary complete public call, including input admission.

The native DSO, PTX, application inputs, GPU launch, transfers, exact oracle,
status-before-output gate, and Lean-B work are unchanged.  This successor was
designed after observing v4, has no pass threshold, is not confirmatory, and
cannot replace any formal row.
"""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time
from typing import Any, Mapping

import numpy as np

from .formal_worker import (
    _b_execution_ledger,
    _bundle_paths,
    _d_execution_ledger,
    _factory,
    _validate_arm,
    _validate_success,
    preload_symmetric_public_runtimes,
)
from .measurement_protocol import (
    ARM_B,
    ARM_D,
    ARMS,
    canonical_document,
    file_record,
    validate_live_target,
    validate_target_manifest,
)
from .public_pyoptix_owner import (
    prevalidate_formal_particle_execution_input,
)
from .untimed_dual_arm_kat import (
    KatArmSuccess,
    KatExecutionLedger,
    UINT32_MAX,
    load_durable_particle_kat,
)


PREACTION_SCHEMA = "rtdl.goal5814.postformal_confirmatory_preaction.v6"
WORKER_SCHEMA = "rtdl.goal5814.postformal_confirmatory_worker.v6"
CONTROLLER_SCHEMA = "rtdl.goal5814.postformal_confirmatory_controller.v6"
EVALUATION_SCHEMA = "rtdl.goal5814.postformal_confirmatory_evaluation.v6"

CURRENT_COMPLETE_PREVALIDATED = "CURRENT_COMPLETE_PREVALIDATED"
CURRENT_COMPLETE_PUBLIC_CALL = "CURRENT_COMPLETE_PUBLIC_CALL"
LEAN_B_COMPLETE_PREVALIDATED = "LEAN_B_COMPLETE_PREVALIDATED"
LEAN_B_COMPLETE_PUBLIC_CALL = "LEAN_B_COMPLETE_PUBLIC_CALL"
BOUNDARIES = (
    LEAN_B_COMPLETE_PREVALIDATED,
    LEAN_B_COMPLETE_PUBLIC_CALL,
)
BLOCK_COUNT = 24
WARMUP_COUNT = 64
REPETITION_COUNT = 256
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED_BASE = 58_142_000
WORKER_TIMEOUT_SECONDS = 600
PRODUCT_SOURCE_RELATIVE = Path("src/rtdsl/v4_particle_rtdlexe.py")
FAILURE_DISPOSITION = (
    "TERMINAL_PRESERVE_RAW_PARTIAL__NO_RETRY_RESUME_REPLACEMENT_OR_NEW_ROOT")
EXPECTED_AUTHORITY_ROOT = Path(
    "/root/work/goal5814_rtxa5000_20260828/repo")
EXPECTED_EXECUTION_ROOT = Path(
    "/root/work/goal5814_rtxa5000_20260828/repo_v5")
EXPECTED_OUTPUT_ROOT = Path(
    "/root/work/goal5814_rtxa5000_20260828/"
    "postformal_confirmatory_v6_result")
EXPECTED_SMOKE_RESULT_PATH = Path(
    "/root/work/goal5814_rtxa5000_20260828/"
    "postformal_optimized_public_v5_untimed_smoke.json")
EXPECTED_PREACTION_PATH = EXPECTED_EXECUTION_ROOT / (
    "history/internal_docs/"
    "goal5814_particle_postformal_confirmatory_v6_preaction_20260828.json")
EXPECTED_TARGET_PATH = Path(
    "/root/work/goal5814_rtxa5000_20260828/"
    "transaction_v2_venv_worker_fix_20260828/target_manifest.json")
EXPECTED_FORMAL_EVALUATION_PATH = Path(
    "/root/work/goal5814_rtxa5000_20260828/"
    "formal_v1_final_v3_v4_venvfix_20260828/evaluation.json")
EXPECTED_PREDECESSOR_EVALUATION_PATH = Path(
    "/root/work/goal5814_rtxa5000_20260828/"
    "postformal_optimized_public_v5_result/evaluation.json")

LEAN_SUCCESS_LEDGER = KatExecutionLedger(
    h2d_copy_call_count=9,
    h2d_bytes=140_136,
    query_h2d_copy_call_count=7,
    query_h2d_bytes=140_000,
    control_reset_h2d_copy_call_count=1,
    control_reset_h2d_bytes=16,
    parameter_h2d_copy_call_count=1,
    parameter_h2d_bytes=120,
    optix_launch_call_count=1,
    raygen_invocation_count=5_000,
    control_d2h_copy_call_count=1,
    control_d2h_bytes=16,
    output_d2h_copy_call_count=1,
    output_d2h_bytes=60_000,
    status_before_output=True,
    output_d2h_after_status_failure=0,
    blocking_boundary_count=2,
)


@dataclass(frozen=True)
class _LeanBPublicResult:
    output: np.ndarray
    control: tuple[int, int, int, int]
    ledger: KatExecutionLedger


class DiagnosticError(RuntimeError):
    """The frozen post-formal diagnostic contract was violated."""


def _strict_json(path: Path) -> Any:
    raw = Path(path).read_bytes()
    value = json.loads(raw)
    if canonical_document(value) != raw:
        raise DiagnosticError(f"noncanonical JSON: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _require_record(path: Path, record: Mapping[str, Any], label: str) -> None:
    if not isinstance(record, Mapping) or set(record) != {
            "path", "bytes", "sha256"}:
        raise DiagnosticError(f"{label} record schema differs")
    resolved = Path(path).resolve(strict=True)
    if record["path"] != str(resolved):
        raise DiagnosticError(f"{label} path differs")
    raw = resolved.read_bytes()
    if len(raw) != record["bytes"] \
            or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise DiagnosticError(f"{label} identity differs")


def _validate_preaction(
        path: Path, *, source: Path, product_source: Path, target: Path,
        formal_evaluation: Path, predecessor_evaluation: Path,
        authority_root: Path, execution_root: Path,
        output: Path | None = None) -> dict[str, Any]:
    value = _strict_json(path)
    if authority_root != EXPECTED_AUTHORITY_ROOT \
            or execution_root != EXPECTED_EXECUTION_ROOT \
            or authority_root == execution_root \
            or Path(path).resolve(strict=True) != EXPECTED_PREACTION_PATH \
            or Path(target).resolve(strict=True) != EXPECTED_TARGET_PATH \
            or Path(formal_evaluation).resolve(strict=True) \
            != EXPECTED_FORMAL_EVALUATION_PATH \
            or Path(predecessor_evaluation).resolve(strict=True) \
            != EXPECTED_PREDECESSOR_EVALUATION_PATH \
            or Path(source).resolve(strict=True) \
            != EXPECTED_EXECUTION_ROOT / (
                "experiments/goal5814_particle/"
                "postformal_full_public_diagnostic.py") \
            or Path(product_source).resolve(strict=True) \
            != EXPECTED_EXECUTION_ROOT / PRODUCT_SOURCE_RELATIVE:
        raise DiagnosticError("postformal fixed path authority differs")
    required = {
        "schema", "date", "status", "observed_before_freeze",
        "source", "product_source", "target_manifest", "formal_evaluation",
        "predecessor_evaluation", "design", "claim_boundary",
        "owner_directive",
    }
    expected_observed = {
        "formal_steady_rtdl_over_pyoptix": 0.7967252874487898,
        "formal_materialization_was_outside_end_clock": True,
        "v4_full_public_rtdl_over_lean_pyoptix": 1.0471814482944435,
        "v4_prevalidated_rtdl_over_lean_pyoptix": 1.084801532332439,
        "v4_outcome_directed": True,
        "v5_prevalidated_ratio": 1.0035123629624505,
        "v5_prevalidated_ci_upper": 1.012164642950999,
        "v5_complete_public_ratio": 0.9858500586015222,
        "v5_complete_public_ci_upper": 0.9944367408196709,
        "v5_evaluation_sha256": (
            "1833377cc1b9762ac409ae76d8822104b494f72ad00631e3f79a6e777bd08a83"),
        "v5_was_outcome_directed_descriptive_only": True,
        "prevalidation_trust_bypass_found_and_repaired_before_worker_zero": True,
        "fixed_product_untimed_exact_core_kat_sha256": (
            "a08463c82025988bea5b10c8c48cc99bd2ca19d8d9f2ad6ea4179c2831590f6a"),
        "preexisting_steady_e2e_rule": "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
        "preexisting_goal5799_a2_result_sha256": (
            "7e6964c0db84aac669814b8ce87dc9a01c104a4806783d79ec14ef91c8deeda8"),
    }
    if not isinstance(value, dict) or set(value) != required \
            or value.get("schema") != PREACTION_SCHEMA \
            or value.get("status") \
            != "FROZEN_CONFIRMATORY_FIXED_PRODUCT_EQUIVALENCE__NO_FURTHER_CHANGE" \
            or value.get("observed_before_freeze") != expected_observed:
        raise DiagnosticError("postformal preaction envelope differs")
    design = value.get("design")
    expected_design = {
        "authority_root": str(EXPECTED_AUTHORITY_ROOT),
        "execution_root": str(EXPECTED_EXECUTION_ROOT),
        "sole_remote_output_root": str(EXPECTED_OUTPUT_ROOT),
        "boundaries": list(BOUNDARIES),
        "balanced_paired_blocks_per_boundary": BLOCK_COUNT,
        "fresh_process_count": len(BOUNDARIES) * BLOCK_COUNT * len(ARMS),
        "warmups_per_worker": WARMUP_COUNT,
        "timed_repetitions_per_worker": REPETITION_COUNT,
        "registered_diagnostic_timing_count": (
            len(BOUNDARIES) * BLOCK_COUNT * len(ARMS) * REPETITION_COUNT),
        "block_order": "EVEN_B_THEN_D__ODD_D_THEN_B",
        "clock": "TIME_PERF_COUNTER_NS__TWO_READS_PER_SAMPLE",
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed_base": BOOTSTRAP_SEED_BASE,
        "primary_ratio": "RTDL_OVER_PYOPTIX",
        "threshold_count": 2,
        "decision_rule": "EACH_BOUNDARY_BOOTSTRAP_95_CI_UPPER_LE_1.05",
        "equivalence_margin": 1.05,
        "d_prevalidated_entrypoint": (
            "PreparedParticleRTDLExecutable.execute_complete_prevalidated"),
        "d_complete_entrypoint": (
            "PreparedParticleRTDLExecutable.execute_complete"),
        "lean_b_implementation_unchanged": True,
        "native_ptx_gpu_work_and_inputs_unchanged": True,
        "common_adapter_outside_clock": True,
        "public_result_observation_inside_clock": True,
        "outcome_directed_after_v4": True,
        "confirmatory_sampling_after_fixed_v5_candidate": True,
        "product_and_measured_functions_unchanged_from_v5": True,
        "formal_result_replacement_allowed": False,
        "confirmatory_claim_allowed": True,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "failure_disposition": FAILURE_DISPOSITION,
    }
    if design != expected_design:
        raise DiagnosticError("postformal diagnostic design differs")
    if output is not None \
            and output != EXPECTED_OUTPUT_ROOT:
        raise DiagnosticError("postformal sole output root differs")
    expected_claim = {
        "postformal_product_selection_was_outcome_directed": True,
        "new_v6_samples_are_confirmatory_for_fixed_candidate": True,
        "confirmatory_claim_allowed": True,
        "formal_result_replacement_allowed": False,
        "threshold_count": 2,
        "equivalence_margin": 1.05,
        "decision_rule": "EACH_BOUNDARY_BOOTSTRAP_95_CI_UPPER_LE_1.05",
        "unconditional_valid_outcome_acceptance": True,
        "baseline_label": "OPTIMIZED_LEAN_PYOPTIX_LOWER_BOUND",
        "speedup_claim_allowed": False,
        "no_stock_pyoptix_performance_claim": True,
        "no_generalization_or_usability_claim": True,
    }
    expected_owner = {
        "continuous_work_without_external_review_or_wait": True,
        "strict_self_review_required": True,
        "pod_budget_hours": 8,
    }
    if value.get("claim_boundary") != expected_claim \
            or value.get("owner_directive") != expected_owner:
        raise DiagnosticError("postformal claim or owner boundary differs")
    _require_record(source, value["source"], "diagnostic source")
    _require_record(product_source, value["product_source"], "product source")
    _require_record(target, value["target_manifest"], "target manifest")
    _require_record(
        formal_evaluation, value["formal_evaluation"], "formal evaluation")
    _require_record(
        predecessor_evaluation, value["predecessor_evaluation"],
        "predecessor evaluation")
    return value


def _order(block: int) -> tuple[str, str]:
    if type(block) is not int or not 0 <= block < BLOCK_COUNT:
        raise DiagnosticError("diagnostic block differs")
    return (ARM_B, ARM_D) if block % 2 == 0 else (ARM_D, ARM_B)


def _worker_id(boundary: str, block: int, position: int, arm: str) -> str:
    return f"{boundary.lower()}__block_{block:02d}__pos_{position}__{arm}"


def _public_complete_raw(arm: Any, bundle: Any) -> Any:
    """Invoke each arm's ordinary complete public entrypoint."""

    columns = bundle.success_queries.native_order()
    if arm.label == ARM_B:
        return arm._owner.execute_complete(*columns, bundle.expected_output)
    if arm.label == ARM_D:
        return arm._prepared.execute_complete(
            *columns, expected_u32x3=bundle.expected_output)
    raise DiagnosticError("public complete arm differs")


def _adapt_public_result(arm: Any, raw: Any) -> KatArmSuccess:
    """Map common benchmark evidence only after the measured end clock."""

    if isinstance(raw, _LeanBPublicResult) and arm.label == ARM_B:
        return KatArmSuccess(
            arm=ARM_B, output=raw.output, control=raw.control,
            ledger=raw.ledger)
    if arm.label == ARM_B:
        return KatArmSuccess(
            arm=ARM_B, output=raw.output, control=tuple(raw.control),
            ledger=_b_execution_ledger(raw.operation_counts))
    if arm.label == ARM_D:
        if raw.artifact_sha256 != arm.deployment_capability.artifact.sha256 \
                or raw.ptx_sha256 != arm.deployment_capability.ptx.sha256:
            raise DiagnosticError("public D complete result identity differs")
        return KatArmSuccess(
            arm=ARM_D,
            output=raw.output_u32x3,
            control=tuple(raw.control),
            ledger=_d_execution_ledger(raw.receipt),
        )
    raise DiagnosticError("public result arm/type differs")


def _observe_public_result(arm: Any, raw: Any) -> dict[str, Any]:
    if isinstance(raw, _LeanBPublicResult) and arm.label == ARM_B:
        output = raw.output
        control = raw.control
        status_before_output = raw.ledger.status_before_output
    elif arm.label == ARM_B:
        output = raw.output
        control = tuple(raw.control)
        status_before_output = bool(
            raw.operation_counts.status_before_output)
    elif arm.label == ARM_D:
        output = raw.output_u32x3
        control = tuple(raw.control)
        status_before_output = bool(raw.receipt["status_before_output"])
    else:
        raise DiagnosticError("public observation arm/type differs")
    return {
        "output_shape": list(output.shape),
        "control": list(control),
        "status_before_output": status_before_output,
    }


def _raw_b_owner(arm: Any) -> Any:
    """Reach the already-public owner behind the formal benchmark façade."""

    facade = getattr(arm, "_owner", None)
    owner = getattr(
        facade, "_FormalPublicPyOptixParticleOwner__owner", None)
    if owner is None or arm.label != ARM_B:
        raise DiagnosticError("lean B owner access differs")
    return owner


def _lean_b_execute_locked(
        owner: Any, columns: tuple[np.ndarray, ...],
        expected: np.ndarray) -> _LeanBPublicResult:
    """Run the same B work without benchmark-only Python evidence counters.

    This deliberately gives only the baseline arm a post-formal optimization.
    It retains seven pinned-staging copies, the exact CUDA/OptiX operations,
    status-before-output, two blocking boundaries, and the exact oracle.  The
    static operation ledger is published after those operations rather than
    reconstructed through approximately 49 Python field mutations and a
    31-field completion snapshot on every call.
    """

    if owner._closed:
        raise DiagnosticError("lean B owner is closed")
    query_count = owner.shape.query_count
    if query_count != 5_000 or len(columns) != 7:
        raise DiagnosticError("lean B query shape differs")
    owner._execution_generation += 1
    query_stride = query_count * np.dtype(np.float32).itemsize
    cuda = owner.runtime.cp.cuda.runtime
    h2d = int(cuda.memcpyHostToDevice)
    d2h = int(cuda.memcpyDeviceToHost)
    stream_pointer = int(owner.stream.ptr)
    for column_index, column in enumerate(columns):
        np.copyto(owner.host_queries[column_index], column, casting="no")
        cuda.memcpyAsync(
            int(owner.query_columns_device.ptr)
            + column_index * query_stride,
            int(owner.host_queries[column_index].ctypes.data),
            query_stride, h2d, stream_pointer)

    owner.host_control[0] = (
        np.uint32(0), UINT32_MAX, np.uint32(0), np.uint32(0))
    cuda.memcpyAsync(
        int(owner.control_device.ptr), int(owner.host_control.ctypes.data),
        16, h2d, stream_pointer)
    cuda.memcpyAsync(
        int(owner.params_device.ptr), int(owner.host_params.ctypes.data),
        120, h2d, stream_pointer)
    owner.runtime.optix.launch(
        owner.pipeline, stream_pointer, int(owner.params_device.ptr), 120,
        owner.sbt, query_count, 1, 1)
    cuda.memcpyAsync(
        int(owner.host_control.ctypes.data), int(owner.control_device.ptr),
        16, d2h, stream_pointer)
    owner.stream.synchronize()
    control = (
        int(owner.host_control["validated_row_count"][0]),
        int(owner.host_control["first_error"][0]),
        int(owner.host_control["error_code"][0]),
        int(owner.host_control["status"][0]),
    )
    if control != (query_count, UINT32_MAX, 0, 0):
        raise DiagnosticError(f"lean B device status differs: {control}")
    cuda.memcpyAsync(
        int(owner.host_output.ctypes.data),
        int(owner.output_columns_device.ptr), 60_000,
        d2h, stream_pointer)
    owner.stream.synchronize()
    output = owner.host_output_rows
    if np.shares_memory(output, expected) \
            or not np.array_equal(output, expected):
        raise DiagnosticError("lean B exact oracle differs")
    return _LeanBPublicResult(
        output=output, control=control, ledger=LEAN_SUCCESS_LEDGER)


def _lean_b_prevalidated(
        arm: Any, admitted: Any) -> _LeanBPublicResult:
    owner = _raw_b_owner(arm)
    with owner._execution_lock:
        columns, expected = owner._require_prevalidated_input(admitted)
        return _lean_b_execute_locked(owner, columns, expected)


def _lean_b_complete(arm: Any, bundle: Any) -> _LeanBPublicResult:
    owner = _raw_b_owner(arm)
    columns = bundle.success_queries.native_order()
    with owner._execution_lock:
        validated, expected = owner._validate_complete_input(
            *columns, bundle.expected_output)
        return _lean_b_execute_locked(owner, validated, expected)


def _execute_boundary(
        *, boundary: str, arm: Any, admitted: Any, bundle: Any,
        phase: str, repetition: int) -> tuple[Any, dict[str, Any]]:
    if boundary == LEAN_B_COMPLETE_PREVALIDATED:
        if arm.label == ARM_B:
            raw = _lean_b_prevalidated(arm, admitted)
        else:
            raw = arm._prepared.execute_complete_prevalidated(admitted)
    elif boundary == LEAN_B_COMPLETE_PUBLIC_CALL:
        raw = _lean_b_complete(arm, bundle) \
            if arm.label == ARM_B else _public_complete_raw(arm, bundle)
    else:
        raise DiagnosticError("diagnostic boundary differs")
    # These reads remain inside the clock.  The end clock therefore follows
    # construction of, and access to, the public output/control/evidence view.
    return raw, _observe_public_result(arm, raw)


def _worker(
        *, authority_root: Path, execution_root: Path, preaction: Path,
        target: Path, formal_evaluation: Path,
        predecessor_evaluation: Path, boundary: str, block: int,
        position: int, arm_label: str) -> dict[str, Any]:
    source = Path(__file__).resolve(strict=True)
    product_source = (execution_root / PRODUCT_SOURCE_RELATIVE).resolve(
        strict=True)
    _validate_preaction(
        preaction, source=source, product_source=product_source,
        target=target, formal_evaluation=formal_evaluation,
        predecessor_evaluation=predecessor_evaluation,
        authority_root=authority_root, execution_root=execution_root)
    expected_order = _order(block)
    if boundary not in BOUNDARIES or position not in (0, 1) \
            or arm_label != expected_order[position]:
        raise DiagnosticError("diagnostic worker schedule differs")
    target_value = validate_target_manifest(
        target, root=authority_root, rehash=True, rehash_wheels=False)
    runtimes = preload_symmetric_public_runtimes()
    imported_product = Path(runtimes.public_rtdlexe.__file__).resolve(
        strict=True)
    if imported_product != product_source:
        raise DiagnosticError("optimized product import root differs")
    bundle = load_durable_particle_kat(_bundle_paths(target_value))
    columns = bundle.success_queries.native_order()
    admitted_b = prevalidate_formal_particle_execution_input(
        *columns, bundle.expected_output)
    admitted_d = runtimes.public_rtdlexe.\
        prevalidate_particle_rtdlexe_exact_core_input(
            *columns, expected_u32x3=bundle.expected_output)
    admitted = admitted_b if arm_label == ARM_B else admitted_d
    arm = _factory(arm_label, runtimes)(bundle)
    _validate_arm(
        arm, expected_label=arm_label, bundle=bundle)
    receipts: list[dict[str, Any]] = []
    samples: list[int] = []
    observations: list[dict[str, Any]] = []
    try:
        for repetition in range(WARMUP_COUNT):
            raw, observation = _execute_boundary(
                boundary=boundary, arm=arm, admitted=admitted,
                bundle=bundle, phase="WARMUP", repetition=repetition)
            observations.append(observation)
            receipts.append(_validate_success(
                _adapt_public_result(arm, raw), arm=arm, bundle=bundle,
                phase="WARMUP", repetition=repetition))
        for repetition in range(REPETITION_COUNT):
            start = time.perf_counter_ns()
            raw, observation = _execute_boundary(
                boundary=boundary, arm=arm, admitted=admitted,
                bundle=bundle, phase="TIMED", repetition=repetition)
            end = time.perf_counter_ns()
            if end <= start:
                raise DiagnosticError("diagnostic clock interval differs")
            samples.append(end - start)
            observations.append(observation)
            receipts.append(_validate_success(
                _adapt_public_result(arm, raw), arm=arm, bundle=bundle,
                phase="TIMED", repetition=repetition))
    finally:
        arm.close()
    if len(samples) != REPETITION_COUNT \
            or len(receipts) != WARMUP_COUNT + REPETITION_COUNT \
            or any(item != observations[0] for item in observations):
        raise DiagnosticError("diagnostic repeated observation differs")
    return {
        "schema": WORKER_SCHEMA,
        "status": "PASS__POSTFORMAL_CONFIRMATORY_WORKER",
        "worker_id": _worker_id(boundary, block, position, arm_label),
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "boundary": boundary,
        "block": block,
        "position": position,
        "arm": arm_label,
        "warmup_count": WARMUP_COUNT,
        "timed_repetition_count": REPETITION_COUNT,
        "samples_ns": samples,
        "worker_median_ns": statistics.median(samples),
        "public_observation": observations[0],
        "last_receipt": receipts[-1],
        "preaction": file_record(preaction),
        "target_manifest": file_record(target),
        "formal_evaluation": file_record(formal_evaluation),
        "predecessor_evaluation": file_record(predecessor_evaluation),
        "source": file_record(source),
        "product_source": file_record(product_source),
        "authority_root": str(authority_root),
        "execution_root": str(execution_root),
        "postformal_outcome_directed": True,
        "confirmatory_sampling_after_fixed_candidate": True,
        "formal_result_replacement_allowed": False,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "registered_diagnostic_timing_count": REPETITION_COUNT,
    }


def _bootstrap_ci(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    medians = sorted(
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS)
    )
    return [medians[249], medians[9749]]


def _evaluate(workers: list[dict[str, Any]]) -> dict[str, Any]:
    expected_count = len(BOUNDARIES) * BLOCK_COUNT * len(ARMS)
    if len(workers) != expected_count:
        raise DiagnosticError("diagnostic worker count differs")
    if len({row["pid"] for row in workers}) != expected_count \
            or len({row["worker_id"] for row in workers}) != expected_count:
        raise DiagnosticError("diagnostic fresh process identity differs")
    for row in workers:
        if row.get("schema") != WORKER_SCHEMA \
                or row.get("status") \
                != "PASS__POSTFORMAL_CONFIRMATORY_WORKER" \
                or row.get("warmup_count") != WARMUP_COUNT \
                or row.get("timed_repetition_count") != REPETITION_COUNT \
                or not isinstance(row.get("samples_ns"), list) \
                or len(row["samples_ns"]) != REPETITION_COUNT \
                or any(type(value) is not int or value <= 0
                       for value in row["samples_ns"]) \
                or row.get("worker_median_ns") \
                != statistics.median(row["samples_ns"]) \
                or row.get("registered_diagnostic_timing_count") \
                != REPETITION_COUNT \
                or any(row.get(key) != 0 for key in (
                    "retry_count", "resume_count", "replacement_count",
                    "row_drop_count")) \
                or row.get("postformal_outcome_directed") is not True \
                or row.get("confirmatory_sampling_after_fixed_candidate") \
                is not True \
                or row.get("formal_result_replacement_allowed") is not False:
            raise DiagnosticError("diagnostic worker result schema differs")
    rows: list[dict[str, Any]] = []
    for boundary_index, boundary in enumerate(BOUNDARIES):
        paired: list[dict[str, Any]] = []
        for block in range(BLOCK_COUNT):
            matches = [
                row for row in workers
                if row["boundary"] == boundary and row["block"] == block]
            if len(matches) != 2 or {row["arm"] for row in matches} \
                    != set(ARMS):
                raise DiagnosticError("diagnostic paired block differs")
            by_arm = {row["arm"]: row for row in matches}
            b_value = by_arm[ARM_B]["worker_median_ns"]
            d_value = by_arm[ARM_D]["worker_median_ns"]
            paired.append({
                "block": block,
                "order": list(_order(block)),
                "pyoptix_worker_median_ns": b_value,
                "rtdl_worker_median_ns": d_value,
                "rtdl_over_pyoptix": d_value / b_value,
            })
        ratios = [row["rtdl_over_pyoptix"] for row in paired]
        b_values = [row["pyoptix_worker_median_ns"] for row in paired]
        d_values = [row["rtdl_worker_median_ns"] for row in paired]
        ci = _bootstrap_ci(
            ratios, BOOTSTRAP_SEED_BASE + boundary_index)
        rows.append({
            "boundary": boundary,
            "pyoptix_median_ns": statistics.median(b_values),
            "rtdl_median_ns": statistics.median(d_values),
            "median_of_paired_rtdl_over_pyoptix": statistics.median(ratios),
            "bootstrap_95_ci": ci,
            "ci_upper_le_1_05": ci[1] <= 1.05,
            "minimum_paired_ratio": min(ratios),
            "maximum_paired_ratio": max(ratios),
            "rtdl_slower_pair_count": sum(value > 1.0 for value in ratios),
            "paired_blocks": paired,
        })
    objective_met = all(row["ci_upper_le_1_05"] for row in rows)
    return {
        "schema": EVALUATION_SCHEMA,
        "status": (
            "COMPLETE__CONFIRMATORY_EQUIVALENCE_PASS"
            if objective_met else
            "COMPLETE__CONFIRMATORY_EQUIVALENCE_FAIL"),
        "worker_count": expected_count,
        "unique_pid_count": expected_count,
        "registered_diagnostic_timing_count": (
            expected_count * REPETITION_COUNT),
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "postformal_outcome_directed": True,
        "confirmatory_sampling_after_fixed_candidate": True,
        "confirmatory_claim_allowed": True,
        "speedup_claim_allowed": False,
        "formal_result_replacement_allowed": False,
        "threshold_count": 2,
        "decision_rule": "EACH_BOUNDARY_BOOTSTRAP_95_CI_UPPER_LE_1.05",
        "equivalence_margin": 1.05,
        "equivalence_objective_met": objective_met,
        "rows": rows,
    }


def _worker_environment(
        *, root: Path, target: Mapping[str, Any], directory: Path,
        base: Mapping[str, str]) -> dict[str, str]:
    cache = directory / "isolated_caches"
    paths = {
        "home": directory / "home",
        "tmp": directory / "tmp",
        "xdg": cache / "xdg",
        "cuda": cache / "cuda",
        "cupy": cache / "cupy",
        "numba": cache / "numba",
        "optix": cache / "optix",
    }
    for path in paths.values():
        path.mkdir(parents=True)
    environment = dict(base)
    environment.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONPATH": os.pathsep.join((str(root), str(root / "src"))),
        "PYTHONPYCACHEPREFIX": str(cache / "pycache"),
        "HOME": str(paths["home"]),
        "TMP": str(paths["tmp"]),
        "TEMP": str(paths["tmp"]),
        "TMPDIR": str(paths["tmp"]),
        "XDG_CACHE_HOME": str(paths["xdg"]),
        "CUDA_CACHE_PATH": str(paths["cuda"]),
        "CUDA_CACHE_DISABLE": "1",
        "CUPY_CACHE_DIR": str(paths["cupy"]),
        "NUMBA_CACHE_DIR": str(paths["numba"]),
        "OPTIX_CACHE_PATH": str(paths["optix"]),
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
        "RTDL_DISABLE_CUBIN_CACHE": "1",
        "RTDL_OPTIX_DISABLE_CUBIN_CACHE": "1",
        "CUDA_VISIBLE_DEVICES": target["cuda_visible_devices"],
    })
    for key, target_key in (
            ("LD_LIBRARY_PATH", "ld_library_path"),
            ("LD_PRELOAD", "ld_preload")):
        value = target[target_key]
        if value is None:
            environment.pop(key, None)
        else:
            environment[key] = value
    return environment


def _controller(
        *, authority_root: Path, execution_root: Path, preaction: Path,
        target: Path, formal_evaluation: Path,
        predecessor_evaluation: Path) -> dict[str, Any]:
    source = Path(__file__).resolve(strict=True)
    product_source = (execution_root / PRODUCT_SOURCE_RELATIVE).resolve(
        strict=True)
    preaction_value = _validate_preaction(
        preaction, source=source, product_source=product_source,
        target=target, formal_evaluation=formal_evaluation,
        predecessor_evaluation=predecessor_evaluation,
        authority_root=authority_root, execution_root=execution_root)
    output = Path(
        preaction_value["design"]["sole_remote_output_root"])
    if not output.is_absolute():
        raise DiagnosticError("diagnostic output root is not absolute")
    output = output.resolve(strict=False)
    _validate_preaction(
        preaction, source=source, product_source=product_source,
        target=target, formal_evaluation=formal_evaluation,
        predecessor_evaluation=predecessor_evaluation,
        authority_root=authority_root, execution_root=execution_root,
        output=output)
    if output.exists():
        raise DiagnosticError("diagnostic output already exists")
    target_value = validate_target_manifest(
        target, root=authority_root, rehash=True, rehash_wheels=True)
    live_target = validate_live_target(target_value)
    output.mkdir(parents=True, exist_ok=False)
    start = {
        "schema": "rtdl.goal5814.postformal_confirmatory_start.v6",
        "status": "STARTED__UNIQUE_ROOT_RESERVED__WORKER_ZERO",
        "preaction": file_record(preaction),
        "source": file_record(source),
        "product_source": file_record(product_source),
        "target_manifest": file_record(target),
        "formal_evaluation": file_record(formal_evaluation),
        "predecessor_evaluation": file_record(predecessor_evaluation),
        "authority_root": str(authority_root),
        "execution_root": str(execution_root),
        "sole_remote_output_root": str(output),
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "formal_worker_count": 0,
        "registered_diagnostic_timing_count": 0,
    }
    (output / "start.json").write_bytes(canonical_document(start))
    worker_root = output / "workers"
    worker_root.mkdir()
    rows: list[dict[str, Any]] = []
    source_record = file_record(source)
    for boundary in BOUNDARIES:
        for block in range(BLOCK_COUNT):
            for position, arm in enumerate(_order(block)):
                worker_id = _worker_id(boundary, block, position, arm)
                directory = worker_root / worker_id
                directory.mkdir()
                stdout_path = directory / "stdout.json"
                stderr_path = directory / "stderr.txt"
                environment = _worker_environment(
                    root=execution_root, target=target_value["target"],
                    directory=directory,
                    base=os.environ)
                command = [
                    sys.executable, "-m",
                    "experiments.goal5814_particle."
                    "postformal_full_public_diagnostic",
                    "worker", "--authority-root", str(authority_root),
                    "--execution-root", str(execution_root),
                    "--preaction", str(preaction),
                    "--target", str(target),
                    "--formal-evaluation", str(formal_evaluation),
                    "--predecessor-evaluation", str(predecessor_evaluation),
                    "--boundary", boundary,
                    "--block", str(block),
                    "--position", str(position),
                    "--arm", arm,
                ]
                (directory / "command.json").write_bytes(canonical_document({
                    "command": command,
                    "cwd": str(execution_root),
                    "worker_id": worker_id,
                }))
                timed_out = False
                with stdout_path.open("xb") as stdout_stream, \
                        stderr_path.open("xb") as stderr_stream:
                    process = subprocess.Popen(
                        command, cwd=execution_root, env=environment,
                        stdout=stdout_stream, stderr=stderr_stream)
                    try:
                        returncode = process.wait(
                            timeout=WORKER_TIMEOUT_SECONDS)
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        process.kill()
                        returncode = process.wait()
                    stdout_stream.flush()
                    stderr_stream.flush()
                    os.fsync(stdout_stream.fileno())
                    os.fsync(stderr_stream.fileno())
                if timed_out or returncode != 0:
                    terminal = {
                        "schema": (
                            "rtdl.goal5814.postformal_confirmatory_"
                            "terminal_failure.v6"),
                        "status": "TERMINAL__NO_RETRY_OR_NEW_ROOT",
                        "worker_id": worker_id,
                        "reason": "TIMEOUT" if timed_out else "NONZERO_EXIT",
                        "returncode": returncode,
                        "stdout": file_record(stdout_path),
                        "stderr": file_record(stderr_path),
                        "failure_disposition": FAILURE_DISPOSITION,
                    }
                    (directory / "terminal_failure.json").write_bytes(
                        canonical_document(terminal))
                    raise DiagnosticError(
                        f"diagnostic worker failed without retry: {worker_id}")
                stdout_bytes = stdout_path.read_bytes()
                try:
                    row = json.loads(stdout_bytes)
                except BaseException as error:
                    terminal = {
                        "schema": (
                            "rtdl.goal5814.postformal_confirmatory_"
                            "terminal_failure.v6"),
                        "status": "TERMINAL__NO_RETRY_OR_NEW_ROOT",
                        "worker_id": worker_id,
                        "reason": "MALFORMED_STDOUT",
                        "error_type": type(error).__name__,
                        "stdout": file_record(stdout_path),
                        "stderr": file_record(stderr_path),
                        "failure_disposition": FAILURE_DISPOSITION,
                    }
                    (directory / "terminal_failure.json").write_bytes(
                        canonical_document(terminal))
                    raise DiagnosticError(
                        f"diagnostic worker stdout differs: {worker_id}") \
                        from error
                if canonical_document(row) != stdout_bytes \
                        or row.get("worker_id") != worker_id \
                        or row.get("source") != source_record \
                        or row.get("product_source") \
                        != file_record(product_source) \
                        or row.get("authority_root") != str(authority_root) \
                        or row.get("execution_root") != str(execution_root):
                    raise DiagnosticError(
                        f"diagnostic worker receipt differs: {worker_id}")
                rows.append(row)
    evaluation = _evaluate(rows)
    evaluation_path = output / "evaluation.json"
    evaluation_path.write_bytes(canonical_document(evaluation))
    controller = {
        "schema": CONTROLLER_SCHEMA,
        "status": (
            "COMPLETE__96_FRESH_PROCESSES__POSTFORMAL_CONFIRMATORY"),
        "worker_count": len(rows),
        "unique_pid_count": len({row["pid"] for row in rows}),
        "registered_diagnostic_timing_count": sum(
            row["registered_diagnostic_timing_count"] for row in rows),
        "preaction": file_record(preaction),
        "target_manifest": file_record(target),
        "formal_evaluation": file_record(formal_evaluation),
        "predecessor_evaluation": file_record(predecessor_evaluation),
        "source": source_record,
        "product_source": file_record(product_source),
        "authority_root": str(authority_root),
        "execution_root": str(execution_root),
        "sole_remote_output_root": str(output),
        "live_target": live_target,
        "evaluation": file_record(evaluation_path),
        "postformal_outcome_directed": True,
        "confirmatory_sampling_after_fixed_candidate": True,
        "confirmatory_claim_allowed": True,
        "equivalence_objective_met": evaluation[
            "equivalence_objective_met"],
        "formal_result_replacement_allowed": False,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
    }
    (output / "controller.json").write_bytes(canonical_document(controller))
    return controller


def _untimed_smoke(
        *, authority_root: Path, execution_root: Path, preaction: Path,
        target: Path, formal_evaluation: Path,
        predecessor_evaluation: Path) -> dict[str, Any]:
    """Exercise every successor boundary once without reading a clock."""

    source = Path(__file__).resolve(strict=True)
    product_source = (execution_root / PRODUCT_SOURCE_RELATIVE).resolve(
        strict=True)
    _validate_preaction(
        preaction, source=source, product_source=product_source,
        target=target, formal_evaluation=formal_evaluation,
        predecessor_evaluation=predecessor_evaluation,
        authority_root=authority_root, execution_root=execution_root)
    target_value = validate_target_manifest(
        target, root=authority_root, rehash=True, rehash_wheels=True)
    live_target = validate_live_target(target_value)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(EXPECTED_SMOKE_RESULT_PATH, flags, 0o644)
    try:
        runtimes = preload_symmetric_public_runtimes()
        if Path(runtimes.public_rtdlexe.__file__).resolve(strict=True) \
                != product_source:
            raise DiagnosticError("optimized smoke product import differs")
        bundle = load_durable_particle_kat(_bundle_paths(target_value))
        columns = bundle.success_queries.native_order()
        admitted = {
            ARM_B: prevalidate_formal_particle_execution_input(
                *columns, bundle.expected_output),
            ARM_D: runtimes.public_rtdlexe.
            prevalidate_particle_rtdlexe_exact_core_input(
                *columns, expected_u32x3=bundle.expected_output),
        }
        receipts: list[dict[str, Any]] = []
        for boundary in BOUNDARIES:
            for arm_label in ARMS:
                arm = _factory(arm_label, runtimes)(bundle)
                try:
                    raw, observation = _execute_boundary(
                        boundary=boundary, arm=arm,
                        admitted=admitted[arm_label], bundle=bundle,
                        phase="UNTIMED_SMOKE", repetition=0)
                    receipt = _validate_success(
                        _adapt_public_result(arm, raw), arm=arm, bundle=bundle,
                        phase="UNTIMED_SMOKE", repetition=0)
                    receipts.append({
                        "boundary": boundary,
                        "arm": arm_label,
                        "public_observation": observation,
                        "receipt": receipt,
                    })
                finally:
                    arm.close()
        value = {
            "schema": (
                "rtdl.goal5814.postformal_optimized_public_untimed_smoke.v5"),
            "status": "PASS__FOUR_SUCCESS_PATHS__ZERO_TIMING",
            "source": file_record(Path(__file__).resolve(strict=True)),
            "product_source": file_record(product_source),
            "preaction": file_record(preaction),
            "target_manifest": file_record(target),
            "live_target": live_target,
            "receipts": receipts,
            "worker_count": 0,
            "registered_diagnostic_timing_count": 0,
        }
        encoded = canonical_document(value)
        offset = 0
        while offset != len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise DiagnosticError("short write of optimized smoke result")
            offset += written
        os.fsync(descriptor)
        return value
    finally:
        os.close(descriptor)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("smoke", "worker", "controller"):
        child = sub.add_parser(name)
        child.add_argument("--authority-root", type=Path, required=True)
        child.add_argument("--execution-root", type=Path, required=True)
        child.add_argument("--preaction", type=Path, required=True)
        child.add_argument("--target", type=Path, required=True)
        child.add_argument("--formal-evaluation", type=Path, required=True)
        child.add_argument(
            "--predecessor-evaluation", type=Path, required=True)
        if name == "worker":
            child.add_argument("--boundary", choices=BOUNDARIES, required=True)
            child.add_argument("--block", type=int, required=True)
            child.add_argument("--position", type=int, choices=(0, 1), required=True)
            child.add_argument("--arm", choices=ARMS, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    authority_root = args.authority_root.resolve(strict=True)
    execution_root = args.execution_root.resolve(strict=True)
    target = args.target.resolve(strict=True)
    preaction = args.preaction.resolve(strict=True)
    formal_evaluation = args.formal_evaluation.resolve(strict=True)
    predecessor_evaluation = args.predecessor_evaluation.resolve(strict=True)
    if args.command == "smoke":
        value = _untimed_smoke(
            authority_root=authority_root, execution_root=execution_root,
            preaction=preaction, target=target,
            formal_evaluation=formal_evaluation,
            predecessor_evaluation=predecessor_evaluation)
    elif args.command == "worker":
        value = _worker(
            authority_root=authority_root, execution_root=execution_root,
            preaction=preaction, target=target,
            formal_evaluation=formal_evaluation,
            predecessor_evaluation=predecessor_evaluation,
            boundary=args.boundary, block=args.block,
            position=args.position, arm_label=args.arm)
    else:
        value = _controller(
            authority_root=authority_root, execution_root=execution_root,
            preaction=preaction, target=target,
            formal_evaluation=formal_evaluation,
            predecessor_evaluation=predecessor_evaluation)
    print(canonical_document(value).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
