#!/usr/bin/env python3
"""Shared frozen-shape protocol for Goal5807 confirmatory measurement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_SCHEMA = "rtdl.goal5807.provider_ready_formal_contract.v2"
PILOT_SCHEMA = "rtdl.goal5807.provider_ready_pilot.v3"
ARMS = (
    "RTDL_PROVIDER_READY",
    "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY",
)
TASKS = ("relation", "triangle")
PHASES = (
    "input_admission",
    "runtime_preload",
    "adapter_construct",
    "install_load",
    "provider_bind",
    "app_prepare",
    "first_exact_execute",
    "steady",
    "evidence_identity",
    "prepared_close",
    "provider_session_close",
)
PRIMARY_PHASES = ("app_prepare", "first_exact_execute")
PREFIX_REGIMES = (
    "HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT",
    "POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT",
)
THRESHOLDED_REGIMES = (
    "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE",
    PREFIX_REGIMES[0],
)
BLOCK_COUNT = 16
POSITIONS_PER_BLOCK = 4
TOTAL_WORKERS = len(TASKS) * BLOCK_COUNT * POSITIONS_PER_BLOCK
REGISTERED_TIMINGS_PER_WORKER = 3
TOTAL_REGISTERED_TIMINGS = TOTAL_WORKERS * REGISTERED_TIMINGS_PER_WORKER
BOOTSTRAP_DRAWS = 10_000
CI_INDICES = (249, 9749)
SEEDS = {"relation": 58_070_000, "triangle": 58_070_001}
TARGET_MANIFEST_SHA256 = (
    "61fadabb738d311e0bd73add3fa41a2d24215324cb779c0aef5a94435f380a13")
FILE_KEYS = frozenset({
    "formal_protocol",
    "formal_worker",
    "formal_controller",
    "formal_evaluator",
    "formal_recount",
    "core_runtime",
    "rtdlexe_adapter",
    "pyoptix_adapter",
    "workload",
    "pyoptix_baseline",
    "pyoptix_idiomatic",
    "pilot",
    "target_manifest",
    "goal5806_result",
    "goal5806_postimport_evaluation",
    "goal5806_process_cold_evaluation",
    "pilot_rtdl_relation",
    "pilot_pyoptix_relation",
    "pilot_rtdl_triangle",
    "pilot_pyoptix_triangle",
    "pilot_rtdl_relation_stderr",
    "pilot_pyoptix_relation_stderr",
    "pilot_rtdl_triangle_stderr",
    "pilot_pyoptix_triangle_stderr",
})
CONTRACT_FIELDS = frozenset({
    "schema",
    "status",
    "goal",
    "governance",
    "files",
    "matrix",
    "cache_policy",
    "primary_timing",
    "statistics",
    "hypotheses",
    "evidence_policy",
    "claim_boundary",
    "predecessor_results",
    "observed_pilot",
    "formal_worker_count",
    "registered_performance_timing_count",
})


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def value_sha256(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5807 JSON root is not an object: {path}")
    return value


def create_only(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical(value) + b"\n")


def arm_order(_block: int) -> tuple[str, str, str, str]:
    """The frozen four-observation ABBA order for every block."""

    if type(_block) is not int or not 0 <= _block < BLOCK_COUNT:
        raise ValueError("Goal5807 block is outside the frozen matrix")
    return ARMS[0], ARMS[1], ARMS[1], ARMS[0]


def arm_slug(arm: str) -> str:
    if arm == ARMS[0]:
        return "rtdl"
    if arm == ARMS[1]:
        return "pyoptix"
    raise ValueError(f"Goal5807 unknown arm: {arm}")


def worker_id(task: str, block: int, position: int, arm: str) -> str:
    if task not in TASKS or arm_order(block)[position] != arm:
        raise ValueError("Goal5807 worker coordinates differ")
    return f"{task}_b{block:02d}_p{position}_{arm_slug(arm)}"


def expected_worker_coordinates() -> tuple[tuple[str, int, int, str], ...]:
    return tuple(
        (task, block, position, arm)
        for task in TASKS
        for block in range(BLOCK_COUNT)
        for position, arm in enumerate(arm_order(block))
    )


def _resolved_file(
    root: Path, descriptor: Mapping[str, Any], name: str,
) -> Path:
    if set(descriptor) != {"path", "bytes", "sha256"}:
        raise RuntimeError(f"Goal5807 file descriptor fields differ: {name}")
    raw_path = descriptor.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise RuntimeError(f"Goal5807 file path differs: {name}")
    path = Path(raw_path)
    return (path if path.is_absolute() else root / path).resolve(strict=True)


def validate_contract(
    contract: Mapping[str, Any], root: Path, *, rehash: bool,
) -> dict[str, Path]:
    if set(contract) != CONTRACT_FIELDS \
            or contract.get("schema") != CONTRACT_SCHEMA:
        raise RuntimeError("Goal5807 contract schema or field universe differs")
    if contract.get("status") != (
            "FROZEN_V2_AFTER_OBSERVED_REPAIRED_V3_PILOT__WORKER_ZERO") \
            or contract.get("goal") != "GOAL5807":
        raise RuntimeError("Goal5807 contract status differs")
    if contract.get("formal_worker_count") != 0 \
            or contract.get("registered_performance_timing_count") != 0:
        raise RuntimeError("Goal5807 contract contains formal observations")
    if contract.get("governance") != {
            "repaired_unregistered_pilot_observed_before_freeze": True,
            "pilot_values_observed_before_threshold_freeze": True,
            "formal_thresholds_outcome_directed_after_pilot_values": True,
            "confirmatory_not_blind_preregistered": True,
            "v3_four_cell_unregistered_pilot_observed_before_v2_freeze": True,
            "v3_unregistered_pilot_cell_count": 4,
            "v3_unregistered_pilot_formal_timing_count": 0,
            "formal_design_input_pilot_not_inferential_result": True,
            "pilot_not_formal_evidence": True,
            "all_structurally_valid_formal_results_accepted": True,
            "execution_requires_separate_owner_command": True}:
        raise RuntimeError("Goal5807 governance disclosure differs")
    if contract.get("matrix") != {
            "tasks": list(TASKS),
            "arms": list(ARMS),
            "blocks_per_task": BLOCK_COUNT,
            "workers_per_block": POSITIONS_PER_BLOCK,
            "total_workers": TOTAL_WORKERS,
            "schedule": "ABBA_EACH_BLOCK",
            "fresh_pid_per_arm_observation": True,
            "retry_count": 0,
            "resume_count": 0,
            "replacement_count": 0,
            "row_drop_count": 0,
            "registered_timings_per_worker": REGISTERED_TIMINGS_PER_WORKER,
            "total_registered_timings": TOTAL_REGISTERED_TIMINGS}:
        raise RuntimeError("Goal5807 formal matrix differs")
    if contract.get("primary_timing") != {
            "definition": "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE",
            "component_phase_names": list(PRIMARY_PHASES),
            "additive_two_component_measurement": True,
            "single_contiguous_timer": False,
            "primary_registered_timing_count_per_worker": 1,
            "secondary_registered_prefix_timing_count_per_worker": 2,
            "total_registered_timing_count_per_worker": (
                REGISTERED_TIMINGS_PER_WORKER),
            "registered_prefix_regimes": list(PREFIX_REGIMES),
            "measurement_execution_callable_acquisition_excluded": True,
            "all_close_and_full_ledger_phases_nonprimary_evidence_only": True,
            "steady_repetitions_nonprimary": 1}:
        raise RuntimeError("Goal5807 primary timing differs")
    if contract.get("statistics") != {
            "block_ratio": "MEDIAN_OF_TWO_RTDL_DIV_MEDIAN_OF_TWO_PYOPTIX",
            "primary_statistic": "MEDIAN_OF_16_BLOCK_LOCAL_RATIOS",
            "bootstrap_draw_count": BOOTSTRAP_DRAWS,
            "bootstrap_method": "RANDOM_CHOICES_OF_16_BLOCK_RATIOS",
            "ci_indices_zero_based": list(CI_INDICES),
            "relation_seed": SEEDS["relation"],
            "triangle_seed": SEEDS["triangle"]}:
        raise RuntimeError("Goal5807 statistics differ")
    threshold = {
        "median_block_ratio_rtdl_over_pyoptix_max": 1.05,
        "bootstrap_ci_upper_max": 1.10,
        "positive_rtdl_minus_pyoptix_arm_median_gap_ns_max": 25_000_000,
        "rtdl_faster_passes_absolute_gap_gate": True,
        "each_task_must_pass_all_three": True,
    }
    if contract.get("hypotheses") != {
            "thresholded_regimes": list(THRESHOLDED_REGIMES),
            "app_boundary": threshold,
            "harness_run_entry_prefix": threshold,
            "post_runtime_preload_prefix_has_threshold": False,
            "all_structurally_valid_results_accepted": True}:
        raise RuntimeError("Goal5807 hypotheses differ")
    if contract.get("cache_policy") != {
            "fresh_private_cache_directory_per_worker": True,
            "cuda_cache_disable": "1",
            "optix_cache_enabled": "0",
            "optix_cache_maxsize": "0",
            "rtdl_disable_cubin_cache": "1",
            "no_cross_worker_cache_reuse": True}:
        raise RuntimeError("Goal5807 cache policy differs")
    if contract.get("evidence_policy") != {
            "pilot_schema": PILOT_SCHEMA,
            "provider_and_primary_context_ready_before_primary_boundary": True,
            "exact_program_bytes_loaded_before_primary_boundary": True,
            "current_cuda_context_state_at_primary_boundary": (
                "DEVICE0_PRIMARY_CURRENT"),
            "device_ordinal": 0,
            "target_compute_capability": [8, 6],
            "retained_primary_handle_equals_current_handle": True,
            "temporary_primary_retain_balanced": True,
            "neither_arm_has_optix_context_pipeline_or_sbt_before_primary": (
                True),
            "provider_ready_state_is_harness_constructed": True,
            "pyoptix_provider_ready_is_native_public_lifecycle_claim": False,
            "each_worker_embeds_complete_pilot_receipt": True,
            "exact_oracle_required": True,
            "both_contiguous_prefixes_stop_at_first_exact_output": True,
            "pyoptix_prepared_close_is_partial": True,
            "all_phase_durations_and_full_process_total_preserved": True}:
        raise RuntimeError("Goal5807 evidence policy differs")
    if contract.get("claim_boundary") != {
            "registered_boundary": (
                "DEVICE0_PRIMARY_CURRENT_PROVIDER_PRIMARY_AND_"
                "PROGRAM_READY__APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"),
            "tasks_only": list(TASKS),
            "target_manifest_sha256": TARGET_MANIFEST_SHA256,
            "pilot_is_unregistered_diagnostic": True,
            "pilot_is_formal_or_paper_evidence": False,
            "pyoptix_provider_ready_is_natural_product_boundary_claim": False,
            "public_api_usability_claim_authorized": False,
            "deployment_cold_claim_authorized": False,
            "postimport_claim_authorized": False,
            "full_ledger_ratio_claim_authorized": False,
            "prepared_close_ratio_claim_authorized": False,
            "run_entry_prefix_ratio_claim_authorized": True,
            "post_runtime_preload_prefix_ratio_claim_authorized": True,
            "post_runtime_preload_prefix_threshold_claim_authorized": False,
            "direct_cuda_optix_claim_authorized": False,
            "other_hardware_or_task_generalization_authorized": False,
            "old_goal5806_rows_replaced": False}:
        raise RuntimeError("Goal5807 claim boundary differs")
    if contract.get("predecessor_results") != {
            "goal5806_deployment_cold_retained": True,
            "goal5806_postimport_retained": True,
            "goal5806_process_cold_retained": True,
            "predecessor_result_count": 3,
            "superseded_zero_worker_contract_sha256": (
                "f992669efca937d7c3aed61dc66efa45e610927cffde47cfb3e9a3cba8153ebb"),
            "predecessor_results_replaced": False}:
        raise RuntimeError("Goal5807 predecessor policy differs")
    if contract.get("observed_pilot") != {
            "status": "PASS__UNREGISTERED_4_CELL__FORMAL_DESIGN_INPUT_ONLY",
            "cell_count": 4,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "all_exit_codes_zero": True,
            "all_stderr_empty": True,
            "paper_claim_authorized": False,
            "inferential_claim_authorized": False,
            "threshold_claim_authorized": False,
            "cells": {
                "rtdl_relation": {
                    "app_boundary_ns": 252_583_635,
                    "run_entry_prefix_ns": 912_971_583,
                    "post_runtime_preload_prefix_ns": 714_638_343,
                    "steady_ns_nonformal": 1_166_787,
                    "full_ledger_ns_raw_only": 987_696_105,
                    "pilot_receipt_seal": (
                        "e5f724783607ca4c2cc10c27504064380e99b7a9f36dc836567086c191a3ccdd")},
                "pyoptix_relation": {
                    "app_boundary_ns": 272_947_469,
                    "run_entry_prefix_ns": 1_026_146_881,
                    "post_runtime_preload_prefix_ns": 284_478_944,
                    "steady_ns_nonformal": 1_159_046,
                    "full_ledger_ns_raw_only": 1_065_671_190,
                    "pilot_receipt_seal": (
                        "9fdb0a0928e31b99cf0cd7633a313cb129af7883a16c25a820a50228f73a22bb")},
                "rtdl_triangle": {
                    "app_boundary_ns": 244_111_628,
                    "run_entry_prefix_ns": 1_038_936_825,
                    "post_runtime_preload_prefix_ns": 783_571_492,
                    "steady_ns_nonformal": 94_513,
                    "full_ledger_ns_raw_only": 1_099_369_846,
                    "pilot_receipt_seal": (
                        "19f6cb6b5fcf8ea12057c201a0ef7b534371e744daac6237f47e006a33dbab2f")},
                "pyoptix_triangle": {
                    "app_boundary_ns": 340_493_165,
                    "run_entry_prefix_ns": 1_116_961_402,
                    "post_runtime_preload_prefix_ns": 449_483_910,
                    "steady_ns_nonformal": 90_483,
                    "full_ledger_ns_raw_only": 1_155_322_425,
                    "pilot_receipt_seal": (
                        "6441a0d2500e99236f928559bb4cb67f6739233fd7a2a58cac49a767ff400867")}},
            "full_ledger_ratio_claim_authorized": False,
            "formal_design_input_only": True}:
        raise RuntimeError("Goal5807 observed pilot disclosure differs")
    files = contract.get("files")
    if not isinstance(files, Mapping) or set(files) != FILE_KEYS:
        raise RuntimeError("Goal5807 file universe differs")
    resolved: dict[str, Path] = {}
    for name in sorted(FILE_KEYS):
        descriptor = files[name]
        if not isinstance(descriptor, Mapping):
            raise RuntimeError(f"Goal5807 file descriptor is not a map: {name}")
        path = _resolved_file(root, descriptor, name)
        expected_bytes = descriptor.get("bytes")
        expected_sha = descriptor.get("sha256")
        if type(expected_bytes) is not int or expected_bytes < 0 \
                or not isinstance(expected_sha, str) or len(expected_sha) != 64:
            raise RuntimeError(f"Goal5807 file identity shape differs: {name}")
        if rehash and (
                path.stat().st_size != expected_bytes
                or file_sha256(path) != expected_sha):
            raise RuntimeError(f"Goal5807 file identity differs: {name}")
        resolved[name] = path
    if files["target_manifest"]["sha256"] != TARGET_MANIFEST_SHA256:
        raise RuntimeError("Goal5807 target manifest identity differs")
    return resolved


def validate_phase_ledger(ledger: Mapping[str, Any]) -> int:
    phases = ledger.get("phases")
    if not isinstance(phases, Mapping) or set(phases) != set(PHASES) \
            or ledger.get("phases_are_sequential_and_nonoverlapping") \
            is not True \
            or ledger.get("nonobserved_phase_zero_imputed") is not False:
        raise RuntimeError("Goal5807 phase ledger universe/order differs")
    observed_sum = 0
    last_observed_end = 0
    for name in PHASES:
        row = phases[name]
        if not isinstance(row, Mapping):
            raise RuntimeError(f"Goal5807 phase row differs: {name}")
        duration = row.get("duration_ns")
        if duration is None:
            if name != "provider_session_close" \
                    or row.get("status") != (
                        "UNAVAILABLE__NO_EQUIVALENT_PUBLIC_STATE") \
                    or row.get("start_offset_ns") is not None:
                raise RuntimeError(f"Goal5807 phase unavailable: {name}")
            continue
        start = row.get("start_offset_ns")
        if row.get("status") != "OBSERVED" \
                or type(start) is not int or start < last_observed_end \
                or type(duration) is not int or duration < 0:
            raise RuntimeError(f"Goal5807 phase duration differs: {name}")
        observed_sum += duration
        last_observed_end = start + duration
    total = ledger.get("total_profiled_full_process_ns")
    between = ledger.get("between_phase_unclassified_ns_additive")
    if type(total) is not int or total <= 0 \
            or type(between) is not int or between < 0 \
            or ledger.get("observed_phase_sum_ns_additive") != observed_sum \
            or observed_sum + between != total \
            or ledger.get("additive_closure_ns") != total:
        raise RuntimeError("Goal5807 full-process phase accounting differs")
    return total
