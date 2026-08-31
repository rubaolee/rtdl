"""Controlling hardened final-receipt validator for Goal5798 execution.

The S0 validator is immutable because it is already inside the design freeze.
This successor closes its deliberately narrow future-receipt checks without
editing a frozen byte.
"""

from __future__ import annotations

from typing import Any

from contract_runtime import MEMORY_MODE, digest


def _integer_median(values: list[int]) -> int:
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (
        ordered[middle - 1] + ordered[middle]) // 2


def validate_final_worker_receipt(
    freeze: dict[str, Any], receipt: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    required_fields = set(freeze["future_worker_receipt_required_fields"])
    if not required_fields.issubset(receipt):
        reasons.append("RECEIPT_REQUIRED_FIELDS_MISSING")
    if receipt.get("schema") != "rtdl.goal5798.formal_worker_receipt.v1":
        reasons.append("RECEIPT_SCHEMA_MISMATCH")
    seal = receipt.get("receipt_sha256")
    unsealed = dict(receipt)
    unsealed.pop("receipt_sha256", None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        reasons.append("RECEIPT_SEAL_MISMATCH")
    schedule = {
        row["worker_id"]: row
        for row in freeze["performance_schedule"] + freeze["memory_schedule"]
    }
    planned = schedule.get(receipt.get("worker_id"))
    if planned is None:
        return reasons + ["WORKER_NOT_IN_FROZEN_SCHEDULE"]
    for key in ("arm", "task", "mode", "row_sample_index"):
        if receipt.get(key) != planned.get(key):
            reasons.append(f"SCHEDULE_{key.upper()}_MISMATCH")
    if receipt.get("source_manifest_sha256") != freeze["source_manifest_sha256"]:
        reasons.append("WORKER_SOURCE_MANIFEST_MISMATCH")
    if receipt.get("workload_authority_sha256") != freeze[
            "workload_authority"]["authority_sha256"]:
        reasons.append("WORKLOAD_AUTHORITY_MISMATCH")
    for field in (
        "host_binding_sha256", "raw_output_sha256", "runtime_manifest_sha256",
        "execution_authority_sha256", "worker_payload_receipt_file_sha256",
    ):
        if not isinstance(receipt.get(field), str) or len(receipt[field]) != 64:
            reasons.append(f"{field.upper()}_INVALID")
    correctness = receipt.get("correctness")
    if not isinstance(correctness, dict) or correctness.get("oracle_exact") is not True:
        reasons.append("CORRECTNESS_NOT_EXACT")
    elif correctness.get("raw_output_sha256") != receipt.get("raw_output_sha256"):
        reasons.append("CORRECTNESS_OUTPUT_IDENTITY_MISMATCH")

    durations = receipt.get("durations_ns")
    required_phases = set(freeze["required_phase_keys"])
    if not isinstance(durations, dict) or set(durations) != required_phases:
        reasons.append("DURATION_PHASE_KEYS_INVALID")
        durations = {}
    scalar_phases = required_phases - {"complete_execute_ns"}
    for phase in scalar_phases:
        value = durations.get(phase)
        if phase == "controller_process_wall_ns":
            if type(value) is not int or value <= 0:
                reasons.append("CONTROLLER_PROCESS_WALL_INVALID")
        elif value is not None and (type(value) is not int or value < 0):
            reasons.append(f"DURATION_{phase.upper()}_INVALID")
    complete = durations.get("complete_execute_ns")
    if not isinstance(complete, list) or any(
            type(value) is not int or value < 0 for value in complete):
        reasons.append("COMPLETE_EXECUTE_VECTOR_INVALID")
        complete = []

    mode = planned["mode"]
    if mode == MEMORY_MODE:
        if receipt.get("timing_eligible") is not False:
            reasons.append("MEMORY_RECEIPT_TIMING_ELIGIBLE")
        memory = receipt.get("memory")
        metrics = freeze["measurement_modes"][MEMORY_MODE]["primary_metrics"]
        if not isinstance(memory, dict) or any(
                type(memory.get(metric)) is not int or memory[metric] <= 0
                for metric in metrics):
            reasons.append("MEMORY_METRICS_INVALID")
        if len(complete) != 1:
            reasons.append("MEMORY_EXECUTE_DENOMINATOR_INVALID")
        if receipt.get("primary_sample_ns") is not None:
            reasons.append("MEMORY_PRIMARY_SAMPLE_PRESENT")
        if receipt.get("warmup_execute_count") != 8:
            reasons.append("MEMORY_POST_WARMUP_BARRIER_NOT_PROVEN")
    else:
        if receipt.get("timing_eligible") is not True:
            reasons.append("TIMED_RECEIPT_NOT_ELIGIBLE")
        if receipt.get("memory") is not None:
            reasons.append("TIMED_RECEIPT_CARRIES_MEMORY")
        expected_count = 64 if mode == "PREPARED_EXECUTION" else 1
        if len(complete) != expected_count:
            reasons.append("TIMED_EXECUTE_DENOMINATOR_INVALID")
        expected_primary = (
            _integer_median(complete) if mode == "PREPARED_EXECUTION"
            else durations.get("controller_process_wall_ns"))
        if receipt.get("primary_sample_ns") != expected_primary:
            reasons.append("PRIMARY_SAMPLE_MISMATCH")
        expected_warmups = 8 if mode == "PREPARED_EXECUTION" else 0
        if receipt.get("warmup_execute_count") != expected_warmups:
            reasons.append("WARMUP_DENOMINATOR_MISMATCH")
    return reasons

