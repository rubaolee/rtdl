#!/usr/bin/env python3
"""One fresh-process Goal5807 provider-ready confirmatory worker."""

from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any, Mapping

from scripts.goal5807_provider_ready_formal_protocol import (
    ARMS,
    PILOT_SCHEMA,
    PREFIX_REGIMES,
    PRIMARY_PHASES,
    REGISTERED_TIMINGS_PER_WORKER,
    TARGET_MANIFEST_SHA256,
    TASKS,
    canonical,
    file_sha256,
    read_object,
    validate_contract,
    validate_phase_ledger,
    value_sha256,
)


WORKER_SCHEMA = "rtdl.goal5807.provider_ready_formal_worker.v2"


def _validate_pilot_receipt(
    receipt: Mapping[str, Any], *, arm: str, task: str,
    pilot_path: Path, target_path: Path,
) -> dict[str, int]:
    body = dict(receipt)
    claimed_receipt_sha = body.pop("pilot_sha256", None)
    if claimed_receipt_sha != value_sha256(body):
        raise RuntimeError("Goal5807 pilot receipt seal differs")
    if receipt.get("schema") != PILOT_SCHEMA \
            or receipt.get("arm") != arm or receipt.get("task") != task:
        raise RuntimeError("Goal5807 pilot receipt identity differs")
    pilot_source = receipt.get("pilot_source")
    target = receipt.get("target_manifest")
    if not isinstance(pilot_source, Mapping) \
            or pilot_source.get("sha256") != file_sha256(pilot_path) \
            or pilot_source.get("bytes") != pilot_path.stat().st_size \
            or not isinstance(target, Mapping) \
            or target.get("sha256") != TARGET_MANIFEST_SHA256 \
            or target.get("sha256") != file_sha256(target_path):
        raise RuntimeError("Goal5807 pilot source/target identity differs")
    assertions = receipt.get("provider_program_ready_assertions")
    if not isinstance(assertions, Mapping) or not assertions \
            or not all(value is True for value in assertions.values()) \
            or assertions.get("runtime_provider_loaded") is not True \
            or assertions.get("cuda_primary_ready") is not True \
            or assertions.get("exact_program_bytes_loaded") is not True \
            or assertions.get("optix_device_context_absent") is not True \
            or assertions.get("pipeline_absent") is not True:
        raise RuntimeError("Goal5807 provider/program assertions differ")
    for name in (
            "cuda_current_context_is_device0_primary_at_app_timer_entry",
            "cuda_current_context_matches_retained_primary_handle",
            "device_ordinal_is_zero",
            "target_compute_capability_is_8_6",
            "temporary_primary_retain_balanced"):
        if assertions.get(name) is not True:
            raise RuntimeError(
                f"Goal5807 DEVICE0 primary assertion differs: {name}")
    comparison = receipt.get("comparison_contract")
    if not isinstance(comparison, Mapping) \
            or comparison.get("comparison_authorized") is not True \
            or comparison.get("app_boundary_ratio_computation_authorized") \
            is not True \
            or comparison.get("timer_entry_state_mechanically_matched") \
            is not True \
            or comparison.get("app_timer_entry_cuda_context") != (
                "DEVICE0_PRIMARY_CURRENT") \
            or comparison.get("pilot_is_formal_or_paper_evidence") is not False \
            or comparison.get("provider_bind_phase_comparison_authorized") \
            is not False \
            or comparison.get("full_profiled_process_comparison_authorized") \
            is not False:
        raise RuntimeError("Goal5807 pilot comparison contract differs")
    ledger = receipt.get("phase_ledger")
    if not isinstance(ledger, Mapping):
        raise RuntimeError("Goal5807 pilot phase ledger is absent")
    validate_phase_ledger(ledger)
    phases = ledger["phases"]
    primary = sum(int(phases[name]["duration_ns"]) for name in PRIMARY_PHASES)
    comparable = receipt.get("comparable_app_boundary")
    if not isinstance(comparable, Mapping) \
            or comparable.get("definition") != (
                "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE") \
            or comparable.get("duration_ns_additive") != primary \
            or primary <= 0:
        raise RuntimeError("Goal5807 pilot primary boundary differs")
    prefix_rows = receipt.get("contiguous_prefix_boundaries")
    if not isinstance(prefix_rows, Mapping) \
            or set(prefix_rows) != set(PREFIX_REGIMES):
        raise RuntimeError("Goal5807 contiguous prefix universe differs")
    prefixes: dict[str, int] = {}
    for name in PREFIX_REGIMES:
        row = prefix_rows[name]
        if not isinstance(row, Mapping) \
                or row.get("single_contiguous_timer") is not True \
                or row.get("stop_event") != "FIRST_EXACT_OUTPUT_VALIDATED" \
                or type(row.get("duration_ns")) is not int \
                or row["duration_ns"] <= 0:
            raise RuntimeError(f"Goal5807 contiguous prefix differs: {name}")
        prefixes[name] = row["duration_ns"]
    if prefixes[PREFIX_REGIMES[0]] < prefixes[PREFIX_REGIMES[1]] \
            or prefixes[PREFIX_REGIMES[1]] < primary:
        raise RuntimeError("Goal5807 contiguous prefix nesting differs")
    measurement = receipt.get("measurement_contract")
    if not isinstance(measurement, Mapping) \
            or measurement.get("diagnostic_pilot_only") is not True \
            or measurement.get("exact_program_bytes_loaded_before_comparable_boundary") \
            is not True \
            or measurement.get("current_cuda_context_restored_before_comparable_boundary") \
            is not True \
            or measurement.get("formal_worker_count") != 0 \
            or measurement.get("registered_performance_timing_count") != 0 \
            or measurement.get("may_replace_goal5806") is not False \
            or measurement.get("paper_claim_authorized") is not False \
            or measurement.get("inferential_claim_authorized") is not False \
            or measurement.get("threshold_claim_authorized") is not False \
            or measurement.get("formal_design_input_only") is not True:
        raise RuntimeError("Goal5807 pilot measurement contract differs")
    validation = receipt.get("validation")
    if not isinstance(validation, Mapping) \
            or validation.get("oracle_validated_execution_count") != 2 \
            or not isinstance(validation.get("first_evidence_sha256"), str):
        raise RuntimeError("Goal5807 pilot oracle evidence differs")
    expected_close = (
        "PARTIAL_OWNER_CLOSE__PROCESS_TEARDOWN_RETAINS_CONTEXT_PIPELINE_SBT"
        if arm == ARMS[1] else "COMPLETE_PROVIDER_OWNER_CLOSE")
    if validation.get("pyoptix_prepared_close_semantics") != expected_close \
            or measurement.get("pyoptix_prepared_close_semantics") \
            != expected_close:
        raise RuntimeError("Goal5807 prepared-close semantics differ")
    if arm == ARMS[1] and task == "relation" \
            and validation.get(
                "relation_cubin_loader_fd_closed_after_adapter_close") is not True:
        raise RuntimeError("Goal5807 sealed cubin loader did not close")
    if receipt.get("formal_worker_count") != 0 \
            or receipt.get("registered_performance_timing_count") != 0:
        raise RuntimeError("Goal5807 diagnostic receipt contains formal timing")
    identities = receipt.get("identities")
    if not isinstance(identities, Mapping) \
            or not all(name in identities for name in (
                "construction", "runtime", "inputs")):
        raise RuntimeError("Goal5807 pilot identities differ")
    return {
        "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE": primary,
        **prefixes,
    }


def run_worker(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve(strict=True)
    contract_path = args.contract.resolve(strict=True)
    contract = read_object(contract_path)
    files = validate_contract(contract, root, rehash=True)
    if files["formal_worker"] != Path(__file__).resolve(strict=True):
        raise RuntimeError("Goal5807 formal worker path differs")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    pilot = importlib.import_module("scripts.goal5807_provider_ready_pilot")
    if Path(pilot.__file__).resolve(strict=True) != files["pilot"]:
        raise RuntimeError("Goal5807 imported pilot path differs")
    pilot_args = SimpleNamespace(
        target_manifest=files["target_manifest"],
        expected_target_manifest_sha256=TARGET_MANIFEST_SHA256,
        arm=args.arm,
        task=args.task,
        steady_repetitions=1,
    )
    receipt = pilot._run(pilot_args)
    registered_timings = _validate_pilot_receipt(
        receipt, arm=args.arm, task=args.task,
        pilot_path=files["pilot"], target_path=files["target_manifest"])
    primary_ns = registered_timings[
        "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"]
    result = {
        "schema": WORKER_SCHEMA,
        "status": "PASS__EXACT_ORACLE_AND_PHASE_LEDGER",
        "worker_id": args.worker_id,
        "pid": os.getpid(),
        "task": args.task,
        "arm": args.arm,
        "contract_sha256": file_sha256(contract_path),
        "primary_app_prepare_plus_first_exact_execute_ns": primary_ns,
        "registered_timing_ns": registered_timings,
        "registered_performance_timing_count": (
            REGISTERED_TIMINGS_PER_WORKER),
        "pilot_receipt": receipt,
        "pilot_receipt_sha256": value_sha256(receipt),
        "full_process_total_ns_nonprimary": receipt[
            "phase_ledger"]["total_profiled_full_process_ns"],
        "all_phases_preserved_nonprimary": True,
        "formal_worker_count": 1,
    }
    return {**result, "worker_receipt_sha256": value_sha256(result)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--worker-id", required=True)
    result = run_worker(parser.parse_args())
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
