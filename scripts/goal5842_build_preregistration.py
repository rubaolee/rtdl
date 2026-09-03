#!/usr/bin/env python3
"""Build the no-result Goal5842 preregistration."""

from __future__ import annotations

import json
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import (
    ADMISSION_TASKS,
    BASELINE_ARMS,
    BASELINE_BLOCKS,
    BASELINE_PHASE_BOUNDARIES,
    BASELINE_TASKS,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_LOWER_INDEX,
    BOOTSTRAP_SEED_BASE,
    BOOTSTRAP_UPPER_INDEX,
    CAUSAL_ARMS,
    CAUSAL_BLOCKS,
    CAUSAL_PHASE_BOUNDARIES,
    PREREGISTRATION_SCHEMA,
    REQUIRED_SOURCE_PATHS,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TASK_CONTRACTS,
    build_baseline_schedule,
    build_causal_schedule,
    digest,
    pin_file,
    preregistration_supersession,
    validate_preregistration,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V4.json"
)


def source_paths() -> tuple[Path, ...]:
    return tuple(ROOT / relative for relative in REQUIRED_SOURCE_PATHS)


def build() -> dict[str, object]:
    causal_schedule = build_causal_schedule()
    baseline_schedule = build_baseline_schedule()
    manifest = [pin_file(ROOT, path) for path in source_paths()]
    result: dict[str, object] = {
        "schema": PREREGISTRATION_SCHEMA,
        "date": "2026-09-03",
        "status": "FROZEN_BEFORE_TIMING",
        "supersession": preregistration_supersession(),
        "scientific_question": (
            "How much cold post-import generic-family latency is attributable "
            "to RTDL's admission integrity checks when both arms perform the "
            "same route construction, provider projection, and capability "
            "construction?"
        ),
        "causal_estimand": (
            "within-block CHECK_ON_COLD_PUBLIC_ADMISSION median minus "
            "CHECK_OFF_COLD_UNCHECKED_CONSTRUCTION median for the registered "
            "provider-projection-and-admission phase, in absolute nanoseconds"
        ),
        "admission_tasks": list(ADMISSION_TASKS),
        "baseline_tasks": list(BASELINE_TASKS),
        "task_contracts": [dict(row) for row in TASK_CONTRACTS],
        "causal_arms": list(CAUSAL_ARMS),
        "baseline_arms": list(BASELINE_ARMS),
        "cohort_boundary": {
            "three_task_admission_ablation": True,
            "two_task_same_contract_provider_comparison": True,
            "sphere_provider_baseline_timing": "EXCLUDED_NO_INDEPENDENT_EXACT_COMPARATOR",
            "owl_timing": "EXCLUDED_UNLESS_PUBLIC_EXACT_ARM_IS_FROZEN_BEFORE_WORKER_ZERO",
            "owl_responsibility_analysis_retained": True,
        },
        "causal_phase_boundaries": list(CAUSAL_PHASE_BOUNDARIES),
        "baseline_phase_boundaries": list(BASELINE_PHASE_BOUNDARIES),
        "cold_counterfactual_design": {
            "check_on": "public route.compile on its first call in a fresh process",
            "check_off": (
                "experiment-only direct capability construction after the same "
                "provider.project call, skipping generic admission integrity checks"
            ),
            "route_factory_first_call_in_both_arms": True,
            "pre_timing_public_admission": False,
            "materialization_revalidation_remains_outside_causal_estimand": True,
        },
        "post_estimand_reference_admission": {
            "purpose": "prove exact program identity against normal public admission",
            "included_in_causal_estimand": False,
            "performed_after_registered_interval_in_both_arms": True,
            "cannot_warm_registered_timing": True,
        },
        "execution_identity_requirements": {
            "clean_exact_source_commit": True,
            "exact_python_executable": True,
            "native_library_and_build_manifest_sha256": True,
            "direct_binary_sha256": True,
            "device_source_sha256": True,
            "optix_and_cuda_header_sha256": True,
            "pyoptix_distribution_version_repository_commit_and_module_tree": True,
            "cupy_version_and_module_file": True,
        },
        "baseline_worker_design": {
            "composite_workers": len(baseline_schedule),
            "fresh_subworkers_per_composite": 2,
            "total_subworkers": 2 * len(baseline_schedule),
            "first_and_steady_processes_are_independent": True,
            "direct_close_phase_available": False,
            "close_phase_cross_arm_ratio_forbidden": True,
            "input_materialization_reported_separately_from_setup": True,
            "setup_total_excludes_input_first_execution_and_close": True,
        },
        "byte_identity_invariant": {
            "family_plan": "EXACT_SHA256_EQUAL",
            "family_artifacts": "EXACT_SHA256_EQUAL",
            "provider_projection": "EXACT_SHA256_EQUAL",
            "generated_executable": "EXACT_SHA256_EQUAL",
            "composed_ptx": "EXACT_SHA256_EQUAL",
            "native_library": "EXACT_SHA256_EQUAL",
            "input": "EXACT_SHA256_EQUAL",
            "output": "EXACT_SHA256_EQUAL",
        },
        "causal_schedule": causal_schedule,
        "causal_schedule_sha256": digest(causal_schedule),
        "baseline_schedule": baseline_schedule,
        "baseline_schedule_sha256": digest(baseline_schedule),
        "statistics": {
            "causal_block_count": CAUSAL_BLOCKS,
            "baseline_block_count": BASELINE_BLOCKS,
            "causal_block_summary": (
                "median_of_two_per_arm_then_public_admission_minus_unchecked_construction"
            ),
            "primary_summary": (
                "median_of_provider_projection_and_admission_phase_block_deltas_"
                "absolute_nanoseconds"
            ),
            "secondary_summary": (
                "median_of_full_route_to_capability_block_deltas_absolute_nanoseconds"
            ),
            "negative_control": "route_declaration_on_minus_off_median_nanoseconds",
            "ratio_to_near_zero_control_is_forbidden": True,
            "baseline_summary": "median_of_per-block_arm_ratios",
            "steady_warmups": STEADY_WARMUPS,
            "steady_repetitions": STEADY_REPETITIONS,
            "steady_worker_summary": "median_of_64_complete_execution_samples",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_lower_index": BOOTSTRAP_LOWER_INDEX,
            "bootstrap_upper_index": BOOTSTRAP_UPPER_INDEX,
            "bootstrap_seed_base": BOOTSTRAP_SEED_BASE,
            "success_threshold": None,
            "all_adverse_rows_retained": True,
        },
        "hardware_design": {
            "minimum_distinct_gpu_architecture_generations": 2,
            "same_exact_harness_and_workloads_on_each": True,
            "cross_machine_raw_time_ratio_forbidden": True,
            "per_hardware_results_reported_separately": True,
            "current_available_ada_pod_counts_as_at_most_one_generation": True,
            "no_fixed_driver_cuda_or_optix_floor": True,
        },
        "failure_policy": {
            "preflight_repairs_before_worker_zero_allowed": True,
            "formal_worker_retry": False,
            "formal_worker_drop": False,
            "failed_or_incorrect_worker_in_aggregate": False,
            "failed_or_incorrect_worker_disclosed": True,
            "identity_mismatch_aborts_transaction": True,
            "foreign_gpu_process_aborts_transaction": True,
            "post_result_task_or_phase_change": False,
            "post_result_rtdl_only_optimization": False,
        },
        "claim_ceiling": {
            "checker_off_is_public_api": False,
            "checker_off_is_safe_for_users": False,
            "checker_off_is_experiment_only_counterfactual": True,
            "checker_off_is_supported_optimization": False,
            "materialization_still_revalidates_identity": True,
            "admission_delta_explains_entire_setup_gap": False,
            "two_task_baseline_result_generalizes_to_all_rt": False,
            "sphere_has_direct_pyoptix_or_owl_performance_claim": False,
            "cross_generation_equivalence": False,
            "one_generation_is_goal5842_complete": False,
            "external_review_or_consensus": False,
        },
        "source_manifest": manifest,
        "source_manifest_sha256": digest(manifest),
        "preregistration_build_counter_scope": {
            "top_level_counters_cover_this_v4_build_only": True,
            "prior_untimed_gpu_calls_are_in_supersession": True,
            "prior_untimed_gpu_complete_execution_call_count": 8,
            "prior_registered_timing_observation_count": 0,
        },
        "registered_timing_observation_count": 0,
        "gpu_execution_count": 0,
    }
    result["preregistration_sha256"] = digest(result)
    validate_preregistration(result, ROOT, verify_files=True)
    return result


def main() -> None:
    result = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True).encode("ascii") + b"\n"
    if OUTPUT.exists() and OUTPUT.read_bytes() != payload:
        raise RuntimeError(
            "existing preregistration differs; append a superseding authority"
        )
    OUTPUT.write_bytes(payload)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "preregistration_sha256": result["preregistration_sha256"],
                "causal_worker_count": len(result["causal_schedule"]),
                "baseline_worker_count": len(result["baseline_schedule"]),
                "registered_timing_observation_count": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
