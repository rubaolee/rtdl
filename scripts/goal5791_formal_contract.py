#!/usr/bin/env python3
"""Goal5791 formal scientific contract and pre-execution authority loader.

This module is CPU/static only.  It freezes the six-row, 96-worker scientific
shape inherited from Goal5790 while deliberately leaving target-derived
identities unbound.  Exact source, data, budget, expected-value, citation, and
later target-materialization bytes enter only through a sealed pre-execution
authority document.  This module neither creates that authority nor launches a
worker.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
from typing import Mapping


GOAL = 5791
SCHEMA = "rtdl.goal5791.formal_contract.v1"
PREEXECUTION_AUTHORITY_SCHEMA = "rtdl.goal5791.preexecution_authority.v1"
TARGET_BINDING_SCHEMA = "rtdl.goal5791.target_materialization_binding.v1"
OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA = (
    "rtdl.goal5791.owner_formal_execution_authority.v1"
)
PRETARGET_STATUS = (
    "FROZEN_PRETARGET_INPUT_AUTHORITIES__NOT_EXECUTION_AUTHORITY"
)
POSTPREPARE_STATUS = (
    "FROZEN_POSTPREPARE_TARGET_BINDING__NOT_FORMAL_EXECUTION_AUTHORITY"
)
TARGET_BINDING_STATUS = "CREATE_ONLY_TARGET_MATERIALIZATION_FROZEN"
OWNER_FORMAL_EXECUTION_STATUS = (
    "OWNER_AUTHORIZED_EXACTLY_ONCE_GOAL5791_FORMAL_MATRIX"
)
EXECUTION_STATE = (
    "BASE_CONTRACT_FROZEN__SEPARATE_PREPARE_AND_FORMAL_AUTHORITIES_REQUIRED"
)

PREDECESSOR_STATIC_CONTRACT_FILE_SHA256 = (
    "b42b5cf7cfff3b5e1219aa3af7c85a6db271daef4705418bb55ab06bd0344c45"
)
PREDECESSOR_STATIC_CONTRACT_SHA256 = (
    "edacb13ae285775159ddde9224ff7c5a796925f05c75b09dddf3f28b4cad518b"
)
SEMANTIC_REQUEST_SHA256 = (
    "492c59b92f3ab8138d5bff6b481bff16e51db5028868732d266ef2948810f02e"
)
PHYSICAL_ENCODING_SHA256 = (
    "7f1d101e8f588571c58958152ed7f20ef43387a50d9fd00c5c7925d7405dc656"
)

PAPER_ALGORITHM = "RT-2A1"
MECHANISM_ID = "checked_u64_product_sum_downstream_lowering.v1"
ALLOWED_DELTA_ID = (
    "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
)
SIGMETRICS_DOI = "10.1145/3727108"

PROJECT_STATE_REVIEW_PATH = (
    "history/internal_docs/"
    "reviewer_project_state_and_remaining_work_to_cgo_20260817.md"
)
PROJECT_STATE_REVIEW_FILE_SHA256 = (
    "c74f3fd4348543dfe5bfa8c84a337160a05bb01eb2847798f0e2cf72f8b3734b"
)

MECHANISM_SCOPE_DECISION = {
    "review_input_path": PROJECT_STATE_REVIEW_PATH,
    "review_input_file_sha256": PROJECT_STATE_REVIEW_FILE_SHA256,
    "causally_tested_mechanism_families": [
        "triangle_rt2a1_checked_u64_cross_stage_reduction",
    ],
    "causally_tested_mechanism_family_count": 1,
    "particle_included_in_goal5791": False,
    "particle_same_source_same_cohort_ablation_claimed": False,
    "particle_evidence_disposition": (
        "associational_context_only__prepared_clear_win_cold_clear_loss_and_"
        "historical_reuse_break_even_are_retained_with_scope"
    ),
    "old_two_mechanism_success_criterion_controls_current_submission": False,
    "current_submission_accepts_one_causally_tested_mechanism_family": True,
    "new_particle_paid_transaction_or_benchmark_row_added_as_rescue": False,
    "paper_primary_contribution_remains_semantic_physical_contract": True,
}

PAPER_OUTCOME_CONSEQUENCE_CONTRACT = {
    "frozen_before_stage_b_worker_zero": True,
    "clear_winning_row_definition": (
        "row_local_95pct_bootstrap_ci_wholly_above_one_with_exact_output_and_"
        "frozen_seven_vs_two_successful_operation_sequence_and_published_"
        "trace_cost_bound_fraction_not_greater_than_0p01"
    ),
    "ci_clear_win_is_a_statistical_classification_not_by_itself_a_paper_claim": True,
    "paper_clear_winning_row_count_uses_mechanism_performance_statement_eligible": True,
    "published_paper_outcome_fields": [
        "paper_clear_winning_row_count",
        "paper_clear_winning_row_ids",
        "ci_clear_win_trace_cost_inconclusive_count",
        "ci_clear_win_trace_cost_inconclusive_row_ids",
        "paper_outcome_consequence_selection",
    ],
    "paper_outcome_branch_selection": {
        "paper_clear_winning_row_count_equals_0": "zero_clear_winning_rows",
        "paper_clear_winning_row_count_between_1_and_5": (
            "mixed_one_through_five_clear_winning_rows"
        ),
        "paper_clear_winning_row_count_equals_6": "all_six_clear_winning_rows",
    },
    "ci_clear_win_but_trace_bound_not_small": {
        "demonstrated_clear_win": False,
        "mechanism_performance_statement_eligible": False,
        "paper_classification": "trace_cost_inconclusive",
        "row_median_ci_and_trace_bound_still_reported": True,
    },
    "zero_clear_winning_rows": {
        "c3_disposition": (
            "preregistered_same_source_same_cohort_measurement_found_no_clear_"
            "end_to_end_fusion_benefit"
        ),
        "compiler_fusion_performance_claim_allowed": False,
        "all_negative_and_uncertain_rows_retained": True,
        "paper_center_of_gravity": "C1_semantic_physical_contract",
        "submission_decision_deferred_until_complete_evidence_review": True,
    },
    "mixed_one_through_five_clear_winning_rows": {
        "only_exact_named_row_local_findings_allowed": True,
        "all_negative_and_uncertain_rows_retained": True,
        "all_row_no_slower_or_universal_fusion_claim_allowed": False,
        "abstract_or_title_may_compress_result_to_fusion_wins": False,
    },
    "all_six_clear_winning_rows": {
        "claim_scope": (
            "exact_triangle_rt2a1_same_source_same_provider_same_cohort_"
            "three_dataset_two_lifecycle_ablation_only"
        ),
        "universal_compiler_fusion_claim_allowed": False,
        "particle_causal_claim_allowed": False,
    },
    "outcome_directed_retry_tuning_replacement_row_drop_or_relabel_allowed": False,
    "new_benchmark_rows_or_particle_ablation_added_after_outcome_allowed": False,
    "trace_cost_diagnostic_is_published_per_row": True,
    "trace_cost_diagnostic_may_change_statistic_ci_threshold_or_verdict": False,
}

SOURCE_AUTHORITY_FILE_SHA256 = (
    "d0366794d255e188bb1ad671ea0675f75a36f3ae4b752a377f56dfd45a298fb8"
)
SOURCE_AUTHORITY_SHA256 = (
    "7ed112379b179bc391fbfb5d7cc758e118a639a82353ba8a5b8fa4d554b3f01e"
)
DATA_AUTHORITY_FILE_SHA256 = (
    "b89496b22266c7953ae5608d998ed395cdde5f5bf0ae2f17ff34a37a8b7df181"
)
DATA_AUTHORITY_SHA256 = (
    "27f0eb74cd3a7f338fff678fd538fee4463ece6b87312f14f87d6776403aed06"
)
RUNTIME_BUDGET_AUTHORITY_FILE_SHA256 = (
    "e1510b9f5f1f22ce213d023828f10561dea6132369ef88e4484288293f439fc5"
)
EXPECTED_VALUE_AUTHORITY_FILE_SHA256 = (
    "3136257343614360131477031e7e203e1d22f3b93394c61c32f098b69c6a38ee"
)
CITATION_AUTHORITY_FILE_SHA256 = (
    "4851d3911c1bd124b041b7f656764b4521fc543963f3124625bd1ffae02c54f6"
)
TRACE_COST_DIAGNOSTIC_AUTHORITY_PATH = (
    "history/internal_docs/"
    "goal5791_cpu_trace_record_cost_diagnostic_v2_20260818.json"
)
TRACE_COST_DIAGNOSTIC_AUTHORITY_FILE_SHA256 = (
    "8a5d5924b54e0746a1ff83fa92d94c5977764b1b49fde8ac06790365f25436a2"
)
TRACE_COST_DIAGNOSTIC_AUTHORITY_SHA256 = (
    "f4dd262c6ae7338db39aaf307176b5673baa956fc18f202551cb8115467ad364"
)
TRACE_COST_DIAGNOSTIC_SOURCE_SHA256 = (
    "57635bafa0ae0649ff21c4f08ff0c2040f04856cbcb3dd56d32a9fdf64437fc2"
)

FUSION_OFF = "fusion_off"
FUSION_ON = "fusion_on"
VARIANTS = (FUSION_OFF, FUSION_ON)
COLD = "cold"
PREPARED = "prepared"
LIFECYCLES = (COLD, PREPARED)
RESULT_LIFECYCLE_LABELS = {
    COLD: "cold_process_warm_system",
    PREPARED: "prepared",
}
PAIR_COUNT = 8
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED_BASE = 57_900_000
BOOTSTRAP_CI_INDICES = (249, 9749)

DATASETS = (
    {
        "dataset_id": "com_dblp",
        "display_id": "com-dblp",
        "frozen_input_role": "small_graph_control",
    },
    {
        "dataset_id": "cit_patents",
        "display_id": "cit-Patents",
        "frozen_input_role": "medium_graph",
    },
    {
        "dataset_id": "soc_livejournal1",
        "display_id": "soc-LiveJournal1",
        "frozen_input_role": "large_graph",
    },
)
DATASET_IDS = tuple(str(unit["dataset_id"]) for unit in DATASETS)
DATA_AUTHORITY_DATASETS = {
    "com_dblp": {
        "display_id": "com-dblp",
        "member": "DATA/triangle/com-dblp.edge",
        "sha256": (
            "e9647564c1ca96589cc52314cabf5569ec80b9f5d697578a55d47fbe7aafca67"
        ),
        "bytes": 8_398_928,
        "expected_triangle_count": 2_224_385,
        "oracle_authority_sha256": (
            "2aba6effb60def2f6581f3f44fc1ba8d2e7a9fdab6a3337ac1564eea79869a79"
        ),
    },
    "cit_patents": {
        "display_id": "cit-Patents",
        "member": "DATA/triangle/cit-Patents.edge",
        "sha256": (
            "c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855"
        ),
        "bytes": 132_151_584,
        "expected_triangle_count": 7_515_023,
        "oracle_authority_sha256": (
            "0e50e235cb677da5964baba20cbe1d9b71463bd4e87d157eede72a98e56891b0"
        ),
    },
    "soc_livejournal1": {
        "display_id": "soc-LiveJournal1",
        "member": "DATA/triangle/soc-LiveJournal1.edge",
        "sha256": (
            "80199ecebb7ebdf3b4861748e009d16b1c5f93c35eba837a7ce37f94ada35f83"
        ),
        "bytes": 551_950_184,
        "expected_triangle_count": 285_730_264,
        "oracle_authority_sha256": (
            "99e0dfbca7c22c47af124bb10600050ce3e489e7d3d712a27e34b804c259809c"
        ),
    },
}

AUTHORITY_ROLES = (
    "source_authority",
    "data_authority",
    "runtime_budget_authority",
    "expected_value_authority",
    "citation_authority",
)
AUTHORITY_FILE_SHA256 = {
    "source_authority": SOURCE_AUTHORITY_FILE_SHA256,
    "data_authority": DATA_AUTHORITY_FILE_SHA256,
    "runtime_budget_authority": RUNTIME_BUDGET_AUTHORITY_FILE_SHA256,
    "expected_value_authority": EXPECTED_VALUE_AUTHORITY_FILE_SHA256,
    "citation_authority": CITATION_AUTHORITY_FILE_SHA256,
}

TARGET_HASH_SLOTS = (
    "execution_source_archive_sha256",
    "execution_source_tree_sha256",
    "execution_source_manifest_sha256",
    "native_library_sha256",
    "native_payload_sha256",
    "provider_library_sha256",
    "provider_program_bundle_sha256",
    "target_identity_sha256",
    "semantic_request_sha256",
    "physical_encoding_sha256",
    "reference_executable_family_sha256",
    "callback_ir_sha256",
    "contract_sha256",
    "abi_sha256",
    "composed_program_sha256",
    "composed_ptx_sha256",
    "fusion_off_recipe_sha256",
    "fusion_on_recipe_sha256",
    "dependency_lock_sha256",
    "materializer_sha256",
    "target_source_manifest_sha256",
    "target_evidence_contract_sha256",
    "target_materialization_authority_sha256",
    "runtime_identity_sha256",
    "prepared_identity_sha256",
    "formal_identity_sha256",
)
TARGET_NONCE_SLOTS = (
    "callback_authority_nonce",
    "target_evidence_nonce",
)
TARGET_VERSION_SLOTS = (
    "gpu_uuid",
    "compute_capability",
    "driver_version",
    "cuda_runtime_version",
    "optix_sdk_version",
    "python_version",
    "cupy_version",
)

# ``provider_program_bundle_sha256`` is a derived digest, not an opaque
# identity string and not a file hash.  These are its complete, frozen source
# bindings.  Keeping the nonce in its own namespace prevents callers from
# laundering it through a field whose name claims SHA-256 semantics.
PROVIDER_PROGRAM_BUNDLE_SOURCE_HASH_SLOTS = (
    "native_library_sha256",
    "native_payload_sha256",
    "provider_library_sha256",
    "target_identity_sha256",
    "semantic_request_sha256",
    "physical_encoding_sha256",
    "reference_executable_family_sha256",
    "callback_ir_sha256",
    "contract_sha256",
    "abi_sha256",
    "composed_program_sha256",
    "composed_ptx_sha256",
    "dependency_lock_sha256",
)
PROVIDER_PROGRAM_BUNDLE_SOURCE_NONCE_SLOTS = (
    "callback_authority_nonce",
)

FUSION_OFF_OPERATION_IDS = (
    "maximum_weight.logical_reduce",
    "maximum_weight.scalar_copy_sync",
    "weight_sum.logical_reduce",
    "weight_sum.scalar_copy_sync",
    "weighted_product.materialize",
    "weighted_product_sum.logical_reduce",
    "weighted_product_sum.scalar_copy_sync",
)
FUSION_ON_OPERATION_IDS = (
    "checked_summary.kernel_launch",
    "checked_summary.summary_copy_sync",
)
ACTUAL_FUSION_OFF_CUPY_OPERATIONS = (
    "cp.max(weights)",
    "maximum_weight.item()",
    "cp.sum(weights,dtype=cp.uint64)",
    "weight_sum.item()",
    "values*weights",
    "cp.sum(weighted_product,dtype=cp.uint64)",
    "weighted_sum.item()",
)
ACTUAL_FUSION_ON_ENTRY = "rtdl_v4_checked_u64_weighted_reduce"
ACTUAL_FUSION_ON_OPTIONS = ("-std=c++11",)

OUTPUT_CONTRACT = {
    "paper_algorithm": PAPER_ALGORITHM,
    "algorithm_owned_by": "application_and_xiao_et_al_2025",
    "result": "exact_u64_triangle_count",
    "reducer": "checked_u64_product_sum",
    "overflow": "fail_closed_before_provisional_sum_is_trusted",
    "same_result_required_across_variants": True,
}
INPUT_CONTRACT = {
    "paper_algorithm": PAPER_ALGORITHM,
    "dataset_ids": list(DATASET_IDS),
    "one_exact_input_sha256_per_dataset_required": True,
    "same_dataset_bytes_required_across_variant_and_lifecycle_arms": True,
    "variant_selection_may_depend_on_input_or_dataset": False,
    "particle_input_count": 0,
}
ORACLE_CONTRACT = {
    "one_exact_independent_oracle_authority_sha256_per_dataset_required": True,
    "oracle_output": "exact_u64_triangle_count",
    "oracle_comparison_inside_registered_timer": False,
    "worker_may_call_application_route_to_construct_oracle": False,
    "all_output_mismatches_fail_closed": True,
}

EXECUTE_INCLUDED_WORK = (
    "constant_time_pre_admitted_single_use_execution_token_binding",
    "bounded_device_geometry_production",
    "optix_traversal_and_per_ray_production",
    "declared_downstream_checked_u64_reducer",
    "all_required_host_scalar_synchronization_and_materialization",
    "native_traversal_audit_capture",
    "compiler_instrumented_operation_trace_capture",
    "device_phase_destroy_token_capture",
)
PREPARATION_REQUIRED_WORK = (
    "restricted_callback_verification_and_compile",
    "semantic_and_physical_admission",
    "program_and_runtime_preparation",
    "cpu_deterministic_segment_descriptor_pass",
    "deep_admission_of_every_single_use_execution_token",
)
EXECUTE_FORBIDDEN_WORK = (
    "deep_plan_verification",
    "deep_authority_verification",
    "deep_recipe_verification",
    "deep_operation_contract_verification",
    "timer_pause_restart_or_excluded_interval",
)
EXECUTE_CONTROL_CONTRACT = {
    "timer_interval": "one_continuous_interval_without_pause_or_restart",
    "deep_plan_authority_recipe_or_operation_contract_verification_allowed": False,
    "only_admission_action_allowed": (
        "constant_time_pre_admitted_single_use_execution_token_binding"
    ),
    "constant_time_token_binding_required": True,
}
TRACE_INSTRUMENTATION_CONTRACT = {
    "trace_capture_inside_execute_timer": True,
    "instrumentation_policy_identical_by_declared_operation_semantics": True,
    "one_success_event_per_declared_successful_operation": True,
    "expected_success_event_count": {
        FUSION_OFF: len(FUSION_OFF_OPERATION_IDS),
        FUSION_ON: len(FUSION_ON_OPERATION_IDS),
    },
    "event_count_is_expected_to_differ_between_variants": True,
    "subtract_correct_or_pause_timer_for_trace_cost_allowed": False,
    "cpu_only_diagnostic_required_before_stage_b_worker_zero": True,
    "cpu_only_diagnostic_completed_and_frozen": True,
    "cpu_only_diagnostic_authority_path": TRACE_COST_DIAGNOSTIC_AUTHORITY_PATH,
    "cpu_only_diagnostic_authority_file_sha256": (
        TRACE_COST_DIAGNOSTIC_AUTHORITY_FILE_SHA256
    ),
    "cpu_only_diagnostic_authority_sha256": (
        TRACE_COST_DIAGNOSTIC_AUTHORITY_SHA256
    ),
    "cpu_only_diagnostic_source_sha256": TRACE_COST_DIAGNOSTIC_SOURCE_SHA256,
    "per_event_record_cost_bound_ns": 12_202,
    "extra_event_count_per_segment": 5,
    "five_extra_event_differential_bound_per_segment_ns": 61_010,
    "row_total_bound_rule": (
        "per_event_record_cost_bound_ns * 5 * exact_row_segment_count"
    ),
    "small_relative_rule": (
        "row_total_bound_seconds <= 0.01 * absolute_difference_between_"
        "row_median_off_seconds_and_row_median_on_seconds"
    ),
    "small_relative_max_fraction": 0.01,
    "small_relative_comparison_arithmetic": (
        "exact_registered_phase_interval_nanoseconds_with_fractional_median_"
        "and_rational_less_equal_comparison_before_float_presentation"
    ),
    "ci_clear_win_requires_small_relative_rule_for_paper_claim": True,
    "ci_clear_win_failing_small_relative_rule_paper_classification": (
        "trace_cost_inconclusive"
    ),
    "diagnostic_may_change_row_statistic_ci_threshold_or_verdict": False,
    "measured_claim": (
        "end_to_end_compiler_runtime_lowering_including_evidence_overhead"
    ),
    "pure_device_kernel_timing_claimed": False,
    "every_result_row_must_publish_diagnostic_bound": True,
    "every_figure_caption_must_state_includes_evidence_overhead": True,
    "diagnostic_measurement_environment": {
        "platform_system": "Windows",
        "platform_release": "10",
        "platform_machine": "AMD64",
        "platform_processor": (
            "Intel64 Family 6 Model 45 Stepping 7, GenuineIntel"
        ),
        "python_implementation": "CPython",
        "python_version": "3.12.13",
        "measured_on_formal_target_host": False,
    },
    "paper_must_disclose_diagnostic_measurement_host": True,
    "cross_host_conservatism_is_argument_not_measured_target_fact": True,
    "stage_a_target_host_cpu_diagnostic_rerun_required": False,
}
INDEPENDENT_RECOUNT_REVIEW_STATUS = (
    "INDEPENDENT_RECOUNT_NOT_ITSELF_EXTERNALLY_REVIEWED"
)
STAGE_A_THIRD_POD_JUSTIFICATION = {
    "paid_transaction_ordinal_if_stage_a_is_authorized": 3,
    "original_v4_cgo_plan_paid_transaction_budget": 2,
    "original_two_transactions_spent_by": ["Goal5784", "Goal5785"],
    "original_two_transaction_budget_superseded": True,
    "superseding_requirement": (
        "Goal5788-A1 mandatory same-source same-cohort ablation before any "
        "checked-U64 causal performance claim"
    ),
    "goal5788_a1_mandatory_next_evidence_path": (
        "history/internal_docs/"
        "goal5788_amendment_a1_triangle_causal_interpretation_20260816.json"
    ),
    "goal5788_a1_mandatory_next_evidence_file_sha256": (
        "b13846a2bd37de10bdc1eae7df7620b0f32ce8824aed4310dbc2c5b62bfda157"
    ),
    "mandatory_next_evidence_same_source_tree": True,
    "mandatory_next_evidence_same_gpu_and_cohort": True,
    "pascal_cannot_execute_final_modern_rtx_measurement": True,
    "third_transaction_is_cost_of_correction_not_scope_creep": True,
    "stage_a_still_emits_zero_formal_workers_and_zero_registered_timings": True,
}
EVIDENCE_SEAL_WORK = (
    "receipt_hashing",
    "receipt_json_serialization",
    "receipt_and_event_chain_sealing",
    "oracle_comparison",
)

CACHE_POLICY = {
    "cupy_cache_dir_scope": "unique_per_worker",
    "numba_cache_dir_scope": "unique_per_worker",
    "cupy_and_numba_cache_dirs_are_distinct_siblings_under_worker_root": True,
    "shared_cache_between_workers_or_measured_arms": False,
    "cold_cache_initially_empty": True,
    "cold_definition": (
        "fresh_parent_process_and_empty_private_cupy_recipe_cache__"
        "not_cold_operating_system_page_cache_cuda_driver_jit_cache_or_"
        "optix_disk_cache"
    ),
    "cold_claim_excludes": [
        "operating_system_page_cache",
        "cuda_driver_jit_cache",
        "optix_disk_cache",
    ],
    "controller_rehashes_all_scheduled_inputs_before_worker_zero": True,
    "preworker_full_rehash_can_warm_operating_system_page_cache": True,
    "operating_system_page_cache_controlled_or_dropped": False,
    "operating_system_page_cache_scope": (
        "uncontrolled_same_cohort_balanced_pair_parity_interleaving"
    ),
    "cuda_driver_jit_cache_controlled_or_isolated": False,
    "optix_disk_cache_controlled_or_isolated": False,
    "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control": True,
    "round_major_abba_is_uncontrolled_cache_mitigation_not_control": True,
    "paper_must_disclose_page_cache_boundary": True,
    "cold_only_selected_recipe_first_compile_and_jit_inside_execute": True,
    "cold_preparation_may_compile_selected_recipe": False,
    "prepared_same_fresh_worker_prewarms_both_recipes": True,
    "prepared_private_cache_contains_both_neutral_prewarm_recipes": True,
    "prepared_neutral_recipe_prewarm_order": [FUSION_OFF, FUSION_ON],
    "prepared_each_recipe_launches_synchronizes_and_frees": True,
    "prepared_measurement_starts_only_after_both_neutral_prewarms": True,
    "prepared_cache_identity_bound_in_worker_receipt": True,
    "cache_receipts_preserved": True,
    "cache_payloads_are_authoritative_evidence": False,
    "successful_cohort_cache_payloads_removed_after_validation_before_publication": True,
    "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount": True,
    "successful_cohort_empty_cache_directory_shell_count": 96,
    "empty_cache_directory_shells_are_authoritative_evidence": False,
    "failed_terminal_staging_may_preserve_cache_payloads": True,
}

SOURCE_ADMISSION_POLICY = {
    "portable_manifest_is_non_self_referential": True,
    "expected_regular_file_set": "manifest_rows_plus_manifest_itself",
    "expected_directory_set": "root_plus_parents_implied_by_expected_files",
    "controller_full_rehash_and_exact_set_before_worker_zero": True,
    "every_worker_full_rehash_and_exact_set_before_product_import": True,
    "all_source_paths_without_write_bits_required": True,
    "extra_missing_symlink_reparse_or_special_paths_allowed": False,
    "worker_source_rehash_receipt_required": True,
    "same_host_malicious_root_race_excluded": False,
    "tcb_boundary": "does_not_exclude_a_malicious_same_host_root_race",
}

# Workers are launched with a deliberately minimal ``execve`` environment.
# Locale is explicit because CPython's PEP 538 startup can otherwise insert
# ``LC_CTYPE=C.UTF-8`` when it starts in the C locale, making an exact live-key
# audit target dependent.  A worker adds only its two private, source-external
# cache roots: CUPY_CACHE_DIR and NUMBA_CACHE_DIR.
FORMAL_WORKER_ENVIRONMENT_CONTRACT = {
    "frozen_keys": [
        "PYTHONPATH",
        "PATH",
        "PYTHONHASHSEED",
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONNOUSERSITE",
        "LC_ALL",
        "CUDA_HOME",
        "CUDA_PATH",
        "LD_LIBRARY_PATH",
        "LD_PRELOAD",
        "RTDL_OPTIX_LIB",
        "RTDL_OPTIX_LIBRARY",
        "RTDL_V4_CUDA_PREFIX",
        "RTDL_V4_OPTIX_PREFIX",
    ],
    "dynamic_keys": ["CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"],
    "exact_live_key_set_required": True,
    "lc_all": "C.UTF-8",
    "ld_preload": "",
    "ambient_environment_inherited": False,
    "python_locale_coercion_or_injected_lc_ctype_allowed": False,
}

FORMAL_OUTPUT_LAYOUT_CONTRACT = {
    "execution_target_fields": [
        "target_materialization_root",
        "create_only_formal_output_root",
        "controller_incomplete_staging_root",
        "target_materialization_root_observed_existing_and_bound_at_authority_creation",
        "formal_output_root_observed_absent_at_authority_creation",
        "controller_incomplete_staging_root_observed_absent_at_authority_creation",
        "preexisting_or_shared_formal_output_root_allowed",
        "pod_endpoint",
    ],
    "resource_confirmation_fields": [
        "owner_confirmed_uninterrupted_window_hours",
        "confirmed_free_disk_bytes",
        "confirmed_before_formal_worker_zero",
        "formal_output_parent_resolved_path",
        "formal_output_parent_free_bytes_observed_at_authority_creation",
        "minimum_required_free_disk_bytes",
    ],
    "minimum_required_free_disk_bytes": 20_000_000_000,
    "three_roots_are_pairwise_distinct_same_parent_siblings": True,
    "controller_staging_is_exact_hidden_derivative_of_formal_output": True,
    "materialization_preexists_formal_output_and_staging_are_absent": True,
    "runtime_preexecution_and_formal_authority_are_canonical_distinct_read_only_regular_nonlink_files_before_marker": True,
    "exclusive_controller_staging_marker_precedes_bootstrap_target_resource_data_and_source_admissions": True,
    "any_post_marker_failure_is_terminal_and_preserves_staging": True,
}

CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT = {
    "schema": "rtdl.goal5791.controller_bootstrap_observation.v1",
    "fields": [
        "schema", "controller_environment_sha256",
        "controller_environment_exact_frozen_14_keys_verified",
        "controller_environment_key_count", "controller_cupy_cache_dir_absent",
        "preimport_stdlib_bootstrap_verified", "loaded_harness_sources",
        "loaded_harness_paths_and_hashes_match_formal_identity_record",
        "immutable_control_file_observations",
        "no_gpu_product_process_state_observation",
        "cuda_context_or_product_import_used",
        "completed_after_transaction_marker_before_worker_zero",
    ],
    "loaded_harness_source_paths": [
        "scripts/goal5791_formal_controller.py",
        "scripts/goal5791_formal_contract.py",
        "scripts/goal5791_formal_worker.py",
    ],
    "stdlib_environment_and_entrypoint_gate_precedes_shared_imports": True,
    "runtime_bound_module_path_and_hash_gate_required": True,
}

IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT = {
    "roles": ["runtime", "preexecution_authority", "formal_authority"],
    "fields": [
        "resolved_path", "file_sha256", "bytes", "st_dev", "st_ino",
        "st_mtime_ns", "st_mode", "regular_nonlink", "read_only",
    ],
    "captured_before_transaction_marker": True,
    "rehash_and_stat_unchanged_after_marker_before_other_admissions": True,
}

NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT = {
    "schema": "rtdl.goal5791.no_gpu_product_process_state_observation.v1",
    "fields": [
        "schema", "phase", "forbidden_module_prefixes",
        "forbidden_dso_map_markers", "loaded_module_names",
        "proc_self_maps_lines", "proc_self_maps_sha256",
        "forbidden_module_matches", "forbidden_dso_map_matches",
    ],
    "phases": [
        "after_shared_import_before_target_probe",
        "before_nvidia_smi",
        "after_nvidia_smi",
    ],
    "forbidden_module_prefixes": ["cupy", "numba", "rtdsl"],
    "forbidden_dso_map_markers": [
        "/libcuda.so", "/libcudart.so", "/libnvrtc.so",
        "/libnvvm.so", "/libnvrtc-builtins.so", "/liboptix",
        "/libnvoptix.so", "/libnvidia-rtcore.so",
        "/libnvidia-ptxjitcompiler.so", "/libnvptxcompiler",
        "rtdl_optix",
    ],
    "proc_self_maps_encoding": "utf-8-strict",
    "proc_self_maps_line_representation": (
        "split_on_lf_without_terminators__all_lines_nonempty__"
        "reconstruct_by_joining_with_lf_and_appending_one_terminal_lf"
    ),
    "proc_self_maps_sha256_preimage": (
        "exact_reconstructed_utf8_bytes_equal_to_observed_proc_self_maps_bytes"
    ),
    "actual_formal_linux_must_read_proc_self_maps": True,
    "forbidden_matches_must_be_empty": True,
}

TARGET_RUNTIME_ADMISSION_CONTRACT = {
    "schema": "rtdl.goal5791.target_runtime_admission.v1",
    "status": "PASS__LIVE_TARGET_IDENTITY_RECHECKED_BEFORE_WORKER_ZERO",
    "fields": [
        "schema", "goal", "status", "formal_authority_file_sha256",
        "formal_authority_sha256", "target_materialization_binding_sha256",
        "pod_endpoint", "nvidia_smi_executable", "nvidia_smi_query",
        "visible_gpu_row_count", "observed_gpu_uuid",
        "observed_driver_version", "observed_compute_capability",
        "controlled_environment_sha256",
        "controlled_environment_exact_14_keys_verified",
        "cupy_cache_dir_absent",
        "no_gpu_product_process_state_before_nvidia_smi",
        "no_gpu_product_process_state_after_nvidia_smi",
        "cuda_context_or_product_import_used",
        "created_before_worker_zero", "admission_sha256",
    ],
    "nvidia_smi_executable": "/usr/bin/nvidia-smi",
    "nvidia_smi_query": "uuid,driver_version,compute_cap",
    "exact_visible_gpu_row_count": 1,
    "bound_target_version_fields": [
        "gpu_uuid", "driver_version", "compute_capability",
    ],
}

RESOURCE_ADMISSION_CONTRACT = {
    "schema": "rtdl.goal5791.resource_admission.v1",
    "status": "PASS__FORMAL_OUTPUT_PARENT_CAPACITY_RECHECKED_BEFORE_WORKER_ZERO",
    "fields": [
        "schema", "goal", "status", "formal_authority_file_sha256",
        "formal_authority_sha256", "target_materialization_root",
        "create_only_formal_output_root", "controller_incomplete_staging_root",
        "formal_output_parent_resolved_path",
        "authority_confirmed_free_disk_bytes",
        "authority_observed_free_disk_bytes_at_authority_creation",
        "controller_observed_free_disk_bytes_before_worker_zero",
        "minimum_required_free_disk_bytes", "same_parent_sibling_roots_verified",
        "controller_observation_meets_authority_confirmed_threshold",
        "controller_observation_meets_minimum_required_threshold",
        "created_before_worker_zero", "admission_sha256",
    ],
    "minimum_required_free_disk_bytes": 20_000_000_000,
    "controller_live_free_must_meet_authority_confirmed_and_minimum": True,
}

SEGMENT_PLAN_INPUT_CONTRACT = {
    "schema": "rtdl.goal5791.segment_plan_input.v1",
    "fields": [
        "schema",
        "source_input_sha256",
        "segment_descriptor_sha256",
        "formal_input",
    ],
    "formal_source_input": "selected_frozen_dataset_input_sha256",
    "prewarm_source_input": "neutral_k4_input_sha256",
    "descriptor_only_input_identity_allowed": False,
}

FORMAL_EXECUTION_POLICY = {
    "worker_index_domain": "contiguous_0_through_95",
    "each_worker_index_executes_exactly_once": True,
    "fresh_parent_pid_per_worker": True,
    "retry_allowed": False,
    "resume_allowed": False,
    "replacement_allowed": False,
    "timing_reuse_allowed": False,
    "row_drop_or_relabel_allowed": False,
    "cross_row_or_lifecycle_compensation_allowed": False,
    "target_binding_mutation_after_authority_allowed": False,
    "per_worker_timeout_seconds": 1_800,
}
FORMAL_AUTHORIZATION = {
    "authorizes_pod_connection": True,
    "authorizes_bound_create_only_formal_output_root": True,
    "authorizes_exact_goal5791_formal_matrix": True,
    "authorizes_formal_worker_zero": True,
    "authorizes_registered_timing": True,
    "authorizes_any_other_goal_matrix_target_or_worker": False,
}

PHASE_DEFINITIONS = {
    "loading": "graph input load and degree-oriented CSR construction",
    "preparation": (
        "all PREPARATION_REQUIRED_WORK obligations: restricted callback "
        "verification/compile, semantic and physical admission, program and "
        "runtime preparation, the CPU deterministic segment descriptor pass, "
        "and deep admission of every single-use execution token"
    ),
    "prewarm": (
        "prepared-only same-worker neutral OFF-then-ON cache/JIT prewarm; "
        "each recipe is launched, synchronized, and freed under the frozen "
        "private per-worker cache policy"
    ),
    "execute": (
        "one continuous, unpaused timer interval containing all "
        "EXECUTE_INCLUDED_WORK obligations; deep plan, authority, recipe, "
        "and operation-contract verification is forbidden and only "
        "constant-time binding of a pre-admitted single-use token is allowed"
    ),
    "close": "owner and runtime close",
}


class Goal5791ContractError(ValueError):
    """Fail-closed error for malformed or drifting Goal5791 authorities."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value != "0" * 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_sha256(value: object, label: str) -> str:
    if not _is_sha256(value):
        raise Goal5791ContractError(f"{label} must be a non-placeholder SHA-256")
    return str(value)


def _is_nonce(value: object) -> bool:
    """Return whether *value* follows the frozen 256-bit nonce encoding.

    The encoding intentionally resembles lowercase hexadecimal SHA-256 text,
    but its semantic type is a nonce.  It therefore travels in a distinct
    object and is never validated or described as a content digest.
    """

    return (
        isinstance(value, str)
        and len(value) == 64
        and value != "0" * 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_nonce(value: object, label: str) -> str:
    if not _is_nonce(value):
        raise Goal5791ContractError(
            f"{label} must be a non-placeholder 256-bit lowercase-hex nonce"
        )
    return str(value)


def provider_program_bundle_source_bindings(
    hashes: Mapping[str, object],
    nonces: Mapping[str, object],
) -> dict[str, object]:
    """Build the sole canonical preimage for the program-bundle digest."""

    return {
        "source_hashes": {
            field: hashes[field]
            for field in PROVIDER_PROGRAM_BUNDLE_SOURCE_HASH_SLOTS
        },
        "source_nonces": {
            field: nonces[field]
            for field in PROVIDER_PROGRAM_BUNDLE_SOURCE_NONCE_SLOTS
        },
    }


def provider_program_bundle_digest_record(
    hashes: Mapping[str, object],
    nonces: Mapping[str, object],
) -> dict[str, object]:
    """Return the complete inspectable derivation record for the bundle."""

    bindings = provider_program_bundle_source_bindings(hashes, nonces)
    return {
        "algorithm": "sha256_of_canonical_json_source_bindings",
        "source_hash_slots": list(
            PROVIDER_PROGRAM_BUNDLE_SOURCE_HASH_SLOTS
        ),
        "source_nonce_slots": list(
            PROVIDER_PROGRAM_BUNDLE_SOURCE_NONCE_SLOTS
        ),
        "source_bindings": bindings,
        "sha256": digest(bindings),
    }


def pod_endpoint_identity_record(
    *, ssh_user: str, host: str, port: int,
) -> dict[str, object]:
    """Build a credential-free, inspectable identity for one POD endpoint."""

    if not isinstance(ssh_user, str) or not ssh_user \
            or any(character.isspace() for character in ssh_user):
        raise Goal5791ContractError("POD SSH user is invalid")
    if not isinstance(host, str) or not host \
            or any(character.isspace() for character in host):
        raise Goal5791ContractError("POD host is invalid")
    if isinstance(port, bool) or not isinstance(port, int) \
            or not 1 <= port <= 65_535:
        raise Goal5791ContractError("POD port is invalid")
    source = {"ssh_user": ssh_user, "host": host, "port": port}
    return {**source, "identity_sha256": digest(source)}


def _validate_narrow_goal5791_remote_root(value: object) -> str:
    if not isinstance(value, str) or "\\" in value:
        raise Goal5791ContractError("Goal5791 remote root is invalid")
    pure = PurePosixPath(value)
    if not pure.is_absolute() or pure.as_posix() != value \
            or any(part in (".", "..") for part in pure.parts) \
            or value in ("/", "/root", "/tmp", "/workspace") \
            or "goal5791" not in pure.name.lower():
        raise Goal5791ContractError(
            "remote root must be a narrow Goal5791 absolute path"
        )
    return value


def _require_exact_keys(
    value: Mapping[str, object], expected: set[str], label: str,
) -> None:
    observed = set(value)
    if observed != expected:
        raise Goal5791ContractError(
            f"{label} keys drifted: missing={sorted(expected-observed)!r}, "
            f"extra={sorted(observed-expected)!r}"
        )


def _reject_duplicate_object(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise Goal5791ContractError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                Goal5791ContractError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Goal5791ContractError(f"cannot load strict JSON {path}") from exc
    if not isinstance(value, dict):
        raise Goal5791ContractError(f"{path} must contain one JSON object")
    return value


def output_contract_sha256() -> str:
    return digest(OUTPUT_CONTRACT)


def input_contract_sha256() -> str:
    return digest(INPUT_CONTRACT)


def oracle_contract_sha256() -> str:
    return digest(ORACLE_CONTRACT)


def statistical_rows() -> tuple[dict[str, object], ...]:
    result: list[dict[str, object]] = []
    for lifecycle in LIFECYCLES:
        for unit in DATASETS:
            row_index = len(result)
            result.append({
                "row_index": row_index,
                "row_id": f"{unit['dataset_id']}__{lifecycle}",
                "dataset_id": unit["dataset_id"],
                "dataset_display_id": unit["display_id"],
                "frozen_input_role": unit["frozen_input_role"],
                "lifecycle": lifecycle,
                "paper_algorithm": PAPER_ALGORITHM,
                "mechanism_id": MECHANISM_ID,
                "bootstrap_seed": BOOTSTRAP_SEED_BASE + row_index,
                "input_sha256_slot": (
                    f"dataset_input_sha256.{unit['dataset_id']}"
                ),
                "oracle_authority_sha256_slot": (
                    f"oracle_authority_sha256.{unit['dataset_id']}"
                ),
            })
    return tuple(result)


def result_lifecycle_label(lifecycle: str) -> str:
    """Return the reviewer-required public label for a lifecycle row.

    Internal schedule identities remain ``cold`` and ``prepared`` so the
    frozen row/order semantics are explicit.  Result schemas and tables must
    use these non-ambiguous presentation labels instead.
    """

    if lifecycle not in RESULT_LIFECYCLE_LABELS:
        raise Goal5791ContractError(f"unknown lifecycle: {lifecycle!r}")
    return RESULT_LIFECYCLE_LABELS[lifecycle]


def result_row_id(dataset_id: str, lifecycle: str) -> str:
    """Return the public row identifier used in result tables."""

    if dataset_id not in DATASET_IDS:
        raise Goal5791ContractError(f"unknown dataset: {dataset_id!r}")
    return f"{dataset_id}__{result_lifecycle_label(lifecycle)}"


def variant_order(pair_index: int) -> tuple[str, str]:
    if not isinstance(pair_index, int) or isinstance(pair_index, bool) \
            or not 0 <= pair_index < PAIR_COUNT:
        raise Goal5791ContractError("pair_index is outside the frozen schedule")
    return VARIANTS if pair_index % 2 == 0 else tuple(reversed(VARIANTS))


def schedule() -> tuple[dict[str, object], ...]:
    workers: list[dict[str, object]] = []
    # Round-major interleaving spreads every row's eight paired observations
    # across the complete cohort while keeping the two arms of each pair
    # adjacent.  Pair parity gives the repeated ABBA ordering within each row.
    for pair_index in range(PAIR_COUNT):
        for row in statistical_rows():
            for order_ordinal, variant in enumerate(variant_order(pair_index)):
                workers.append({
                    "worker_index": len(workers),
                    "row_index": row["row_index"],
                    "row_id": row["row_id"],
                    "dataset_id": row["dataset_id"],
                    "lifecycle": row["lifecycle"],
                    "pair_index": pair_index,
                    "order_ordinal": order_ordinal,
                    "variant": variant,
                    "paper_algorithm": PAPER_ALGORITHM,
                    "mechanism_id": MECHANISM_ID,
                    "fresh_parent_pid_required": True,
                })
    return tuple(workers)


def schedule_document() -> dict[str, object]:
    return {
        "schema": "rtdl.goal5791.formal_schedule.v1",
        "goal": GOAL,
        "selection_rule": (
            "round-major across all six rows; pair parity only within each "
            "row: even OFF/ON, odd ON/OFF"
        ),
        "global_order": "pair_round_then_frozen_row_then_adjacent_pair_arm",
        "pair_count_per_row": PAIR_COUNT,
        "independent_row_count": len(statistical_rows()),
        "worker_count": len(schedule()),
        "workers": list(schedule()),
    }


def schedule_sha256() -> str:
    return digest(schedule_document())


def timer_contract(lifecycle: str) -> dict[str, object]:
    if lifecycle not in LIFECYCLES:
        raise Goal5791ContractError(f"unknown lifecycle: {lifecycle!r}")
    registered_phases = (
        ["loading", "preparation", "execute", "close"]
        if lifecycle == COLD else ["execute"]
    )
    return {
        "schema": "rtdl.goal5791.timer_contract.v1",
        "lifecycle": lifecycle,
        "registered_endpoint": (
            "one_continuous_loading_start_through_close_end_outer_interval"
            if lifecycle == COLD
            else "one_continuous_first_post_preparation_measured_execute_interval"
        ),
        "registered_endpoint_formula": (
            "(close.ended_ns-loading.started_ns)/1e9"
            if lifecycle == COLD
            else "(execute.ended_ns-execute.started_ns)/1e9"
        ),
        "registered_endpoint_is_one_continuous_interval": True,
        "registered_phase_seconds_are_summed": False,
        "cold_interphase_dispatch_and_cache_check_are_inside_endpoint": (
            lifecycle == COLD
        ),
        "registered_phases": registered_phases,
        "all_phase_names": list(PHASE_DEFINITIONS),
        "phase_definitions": deepcopy(PHASE_DEFINITIONS),
        "all_five_raw_phase_seconds_required": True,
        "cold_prewarm_seconds_required_zero": lifecycle == COLD,
        "prepared_prewarm_seconds_required_positive": lifecycle == PREPARED,
        "same_worker_mutually_exclusive_phases": True,
        "nested_phase_medians_summed": False,
        "preparation_required_work": list(PREPARATION_REQUIRED_WORK),
        "execute_included_work": list(EXECUTE_INCLUDED_WORK),
        "execute_forbidden_work": list(EXECUTE_FORBIDDEN_WORK),
        "execute_control_contract": deepcopy(EXECUTE_CONTROL_CONTRACT),
        "trace_instrumentation_contract": deepcopy(
            TRACE_INSTRUMENTATION_CONTRACT
        ),
        "device_phase_terminal_state_before_seal": "device_complete_unsealed",
        "evidence_phase_terminal_state_after_seal": "sealed",
        "evidence_sealed_after_registered_endpoint_stops": True,
        "evidence_seal_work_outside_registered_timer": list(EVIDENCE_SEAL_WORK),
        "prepared_loading_preparation_prewarm_and_close_reported_separately": True,
        "prepared_work_called_free": False,
        "same_boundary_for_both_variants": True,
    }


def lifecycle_contract(lifecycle: str) -> dict[str, object]:
    if lifecycle not in LIFECYCLES:
        raise Goal5791ContractError(f"unknown lifecycle: {lifecycle!r}")
    return {
        "schema": "rtdl.goal5791.lifecycle_contract.v1",
        "lifecycle": lifecycle,
        "fresh_parent_pid": True,
        "paper_algorithm": PAPER_ALGORITHM,
        "complete_endpoint": lifecycle == COLD,
        "first_post_preparation_measured_execute": lifecycle == PREPARED,
        "prepared_state_built_in_same_worker": lifecycle == PREPARED,
        "cache_policy": deepcopy(CACHE_POLICY),
        "retry_resume_replacement_row_drop_or_relabel_allowed": False,
    }


def timer_contract_sha256(lifecycle: str) -> str:
    return digest(timer_contract(lifecycle))


def lifecycle_contract_sha256(lifecycle: str) -> str:
    return digest(lifecycle_contract(lifecycle))


def validate_phase_accounting(
    lifecycle: str,
    phase_seconds: Mapping[str, object],
    registered_seconds: object,
    phase_sequence: object,
) -> None:
    contract = timer_contract(lifecycle)
    expected = set(contract["all_phase_names"])
    _require_exact_keys(phase_seconds, expected, "phase_seconds")
    values: dict[str, float] = {}
    for name in expected:
        value = phase_seconds[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) \
                or not math.isfinite(float(value)) or float(value) < 0:
            raise Goal5791ContractError(f"phase_seconds.{name} is invalid")
        values[name] = float(value)
    for name in ("loading", "preparation", "execute", "close"):
        if values[name] <= 0.0:
            raise Goal5791ContractError(
                f"phase_seconds.{name} must be positive"
            )
    if lifecycle == COLD and values["prewarm"] != 0.0:
        raise Goal5791ContractError("cold lifecycle may not prewarm")
    if lifecycle == PREPARED and values["prewarm"] <= 0.0:
        raise Goal5791ContractError(
            "prepared lifecycle requires a positive prewarm duration"
        )
    if isinstance(registered_seconds, bool) \
            or not isinstance(registered_seconds, (int, float)) \
            or not math.isfinite(float(registered_seconds)) \
            or float(registered_seconds) <= 0:
        raise Goal5791ContractError("registered_seconds is invalid")

    if not isinstance(phase_sequence, list) \
            or len(phase_sequence) != len(PHASE_DEFINITIONS):
        raise Goal5791ContractError("phase_sequence is malformed")
    expected_phase_names = list(PHASE_DEFINITIONS)
    prior_end: int | None = None
    observed: dict[str, tuple[int, int]] = {}
    for index, (row, expected_name) in enumerate(zip(
        phase_sequence, expected_phase_names, strict=True,
    )):
        if not isinstance(row, Mapping) or set(row) != {
            "phase", "started_ns", "ended_ns", "seconds",
        }:
            raise Goal5791ContractError(
                f"phase_sequence[{index}] is malformed"
            )
        started = row["started_ns"]
        ended = row["ended_ns"]
        seconds = row["seconds"]
        if row["phase"] != expected_name \
                or isinstance(started, bool) or not isinstance(started, int) \
                or isinstance(ended, bool) or not isinstance(ended, int) \
                or started < 0 or ended < started \
                or prior_end is not None and started < prior_end \
                or isinstance(seconds, bool) \
                or not isinstance(seconds, (int, float)) \
                or not math.isfinite(float(seconds)):
            raise Goal5791ContractError(
                f"phase_sequence[{index}] order or value drifted"
            )
        observed_seconds = (ended - started) / 1_000_000_000.0
        if not math.isclose(
            float(seconds), observed_seconds, rel_tol=0.0, abs_tol=1e-12,
        ) or not math.isclose(
            float(seconds), values[expected_name],
            rel_tol=0.0, abs_tol=1e-12,
        ):
            raise Goal5791ContractError(
                f"phase_sequence[{index}] duration drifted"
            )
        observed[expected_name] = (started, ended)
        prior_end = ended

    expected_registered = (
        (observed["close"][1] - observed["loading"][0])
        / 1_000_000_000.0
        if lifecycle == COLD
        else (
            observed["execute"][1] - observed["execute"][0]
        ) / 1_000_000_000.0
    )
    if not math.isclose(
        float(registered_seconds), expected_registered,
        rel_tol=0.0, abs_tol=1e-12,
    ):
        raise Goal5791ContractError(
            "registered endpoint does not match frozen raw phase accounting"
        )


def expected_operation_contract(variant: str) -> dict[str, object]:
    if variant == FUSION_OFF:
        operations = FUSION_OFF_OPERATION_IDS
        counters = {
            "weighted_product_materializations": 1,
            "compiler_visible_logical_reductions": 3,
            "host_scalar_copy_or_sync_boundaries": 3,
            "checked_summary_kernel_invocations": 0,
            "summary_copy_or_sync_boundaries": 0,
        }
    elif variant == FUSION_ON:
        operations = FUSION_ON_OPERATION_IDS
        counters = {
            "weighted_product_materializations": 0,
            "compiler_visible_logical_reductions": 1,
            "host_scalar_copy_or_sync_boundaries": 1,
            "checked_summary_kernel_invocations": 1,
            "summary_copy_or_sync_boundaries": 1,
        }
    else:
        raise Goal5791ContractError(f"unknown variant: {variant!r}")
    return {
        "mechanism_id": MECHANISM_ID,
        "allowed_delta_id": ALLOWED_DELTA_ID,
        "variant": variant,
        "operation_ids": list(operations),
        "successful_event_count": len(operations),
        "counters": counters,
        "events_recorded_only_after_callable_success": True,
        "hardware_or_opaque_cupy_kernel_introspection_claimed": False,
    }


def contract_document() -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "goal": GOAL,
        "execution_state": EXECUTION_STATE,
        "predecessor_goal5790": {
            "static_contract_file_sha256": (
                PREDECESSOR_STATIC_CONTRACT_FILE_SHA256
            ),
            "static_contract_sha256": PREDECESSOR_STATIC_CONTRACT_SHA256,
            "relationship": (
                "scientific-shape predecessor only; no Goal5790 worker or "
                "result is reused"
            ),
        },
        "scientific_scope": {
            "paper_algorithm": PAPER_ALGORITHM,
            "triangle_weighted_rt2a1_only": True,
            "rt1a2_rows": 0,
            "particle_rows": 0,
            "v2_v3_author_or_cuda_arms": 0,
            "mechanism_id": MECHANISM_ID,
            "allowed_delta_id": ALLOWED_DELTA_ID,
            "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
            "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
            "mechanism_scope_decision": deepcopy(MECHANISM_SCOPE_DECISION),
        },
        "datasets": deepcopy(list(DATASETS)),
        "lifecycles": list(LIFECYCLES),
        "variants": list(VARIANTS),
        "independent_rows": list(statistical_rows()),
        "independent_row_count": len(statistical_rows()),
        "pair_count_per_row": PAIR_COUNT,
        "formal_worker_count": len(schedule()),
        "worker_count_derivation": (
            "3 datasets * 2 lifecycles * 8 ABBA pairs * 2 arms = 96"
        ),
        "schedule_sha256": schedule_sha256(),
        "statistics": {
            "ratio": "fusion_off_seconds / fusion_on_seconds",
            "greater_than_one_favors": FUSION_ON,
            "summary": "median of eight paired ABBA ratios",
            "bootstrap_population": "eight row-local paired OFF/ON ratios",
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_sampler": "python_random_Random_choices",
            "bootstrap_seed": f"{BOOTSTRAP_SEED_BASE} + row_index",
            "bootstrap_statistic": "python_statistics_median",
            "bootstrap_endpoint_rule": "sort draws, select indices 249 and 9749",
            "bootstrap_ci_indices": list(BOOTSTRAP_CI_INDICES),
            "row_local_only": True,
            "cross_dataset_lifecycle_or_row_compensation_allowed": False,
            "numeric_speedup_floor": None,
        },
        "result_presentation": {
            "internal_lifecycle_ids": list(LIFECYCLES),
            "public_lifecycle_labels": deepcopy(RESULT_LIFECYCLE_LABELS),
            "result_lifecycle_field_uses_public_label": True,
            "result_row_id_uses_public_lifecycle_label": True,
            "cold_process_warm_system_definition": CACHE_POLICY[
                "cold_definition"
            ],
            "cold_process_warm_system_excludes": deepcopy(
                CACHE_POLICY["cold_claim_excludes"]
            ),
            "every_table_and_figure_uses_public_lifecycle_label": True,
            "every_figure_caption_states_includes_evidence_overhead": True,
            "independent_recount_external_review_status": (
                INDEPENDENT_RECOUNT_REVIEW_STATUS
            ),
        },
        "trace_cost_diagnostic_authority": {
            "path": TRACE_COST_DIAGNOSTIC_AUTHORITY_PATH,
            "file_sha256": TRACE_COST_DIAGNOSTIC_AUTHORITY_FILE_SHA256,
            "diagnostic_sha256": TRACE_COST_DIAGNOSTIC_AUTHORITY_SHA256,
            "source_sha256": TRACE_COST_DIAGNOSTIC_SOURCE_SHA256,
            "per_event_record_cost_bound_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "per_event_record_cost_bound_ns"
                ]
            ),
            "five_extra_event_differential_bound_per_segment_ns": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "five_extra_event_differential_bound_per_segment_ns"
                ]
            ),
            "small_relative_max_fraction": (
                TRACE_INSTRUMENTATION_CONTRACT[
                    "small_relative_max_fraction"
                ]
            ),
            "required_before_stage_b_worker_zero": True,
            "diagnostic_may_change_row_statistic_ci_threshold_or_verdict": False,
        },
        "stage_a_paid_transaction_justification": deepcopy(
            STAGE_A_THIRD_POD_JUSTIFICATION
        ),
        "contracts": {
            "input": deepcopy(INPUT_CONTRACT),
            "input_sha256": input_contract_sha256(),
            "segment_plan_input": deepcopy(SEGMENT_PLAN_INPUT_CONTRACT),
            "output": deepcopy(OUTPUT_CONTRACT),
            "output_sha256": output_contract_sha256(),
            "oracle": deepcopy(ORACLE_CONTRACT),
            "oracle_sha256": oracle_contract_sha256(),
            "timer": {
                lifecycle: {
                    "contract": timer_contract(lifecycle),
                    "sha256": timer_contract_sha256(lifecycle),
                }
                for lifecycle in LIFECYCLES
            },
            "lifecycle": {
                lifecycle: {
                    "contract": lifecycle_contract(lifecycle),
                    "sha256": lifecycle_contract_sha256(lifecycle),
                }
                for lifecycle in LIFECYCLES
            },
        },
        "operation_contracts": {
            variant: expected_operation_contract(variant)
            for variant in VARIANTS
        },
        "identity_and_fairness": {
            "same_execution_source_provider_native_callback_and_target": True,
            "same_semantic_request_physical_encoding_input_and_oracle": True,
            "same_optix_per_ray_producer": True,
            "only_recipe_payloads_may_differ": list(VARIANTS),
            "fusion_recipe_hash_slots_bind": (
                "exact_rtdl_v4_checked_u64_downstream_operation_identity_payload"
            ),
            "claim_wrapper_digests_are_distinct_from_product_recipe_digests": True,
            "claim_wrappers_cross_bind_product_variant_and_two_vs_seven_events": True,
            "cache_policy": deepcopy(CACHE_POLICY),
            "source_admission_policy": deepcopy(SOURCE_ADMISSION_POLICY),
            "formal_worker_environment_contract": deepcopy(
                FORMAL_WORKER_ENVIRONMENT_CONTRACT
            ),
            "formal_output_layout_contract": deepcopy(
                FORMAL_OUTPUT_LAYOUT_CONTRACT
            ),
            "controller_bootstrap_observation_contract": deepcopy(
                CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT
            ),
            "immutable_control_file_observation_contract": deepcopy(
                IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT
            ),
            "no_gpu_product_process_state_observation_contract": deepcopy(
                NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT
            ),
            "target_runtime_admission_contract": deepcopy(
                TARGET_RUNTIME_ADMISSION_CONTRACT
            ),
            "resource_admission_contract": deepcopy(
                RESOURCE_ADMISSION_CONTRACT
            ),
            "fresh_parent_pid_per_worker": True,
            "app_dataset_timing_result_or_paper_dispatch_allowed": False,
        },
        "two_phase_evidence": {
            "phase_1": (
                "device_complete_unsealed; native traversal audit, operation "
                "trace, and destroy token captured before the execute phase "
                "stops"
            ),
            "phase_2": (
                "hash, JSON serialize, seal, and compare with the independent "
                "oracle only after the registered endpoint stops"
            ),
            "hashing_serialization_sealing_or_comparison_inside_registered_timer": False,
        },
        "required_authority_hash_slots": list(AUTHORITY_ROLES),
        "required_authority_file_sha256": deepcopy(AUTHORITY_FILE_SHA256),
        "required_target_materialization_hash_slots": list(TARGET_HASH_SLOTS),
        "required_target_materialization_nonce_slots": list(TARGET_NONCE_SLOTS),
        "required_target_version_slots": list(TARGET_VERSION_SLOTS),
        "provider_program_bundle_digest_contract": {
            "digest_field": "provider_program_bundle_sha256",
            "algorithm": "sha256_of_canonical_json_source_bindings",
            "source_hash_slots": list(
                PROVIDER_PROGRAM_BUNDLE_SOURCE_HASH_SLOTS
            ),
            "source_nonce_slots": list(
                PROVIDER_PROGRAM_BUNDLE_SOURCE_NONCE_SLOTS
            ),
            "opaque_identity_string_accepted_as_digest": False,
        },
        "target_derived_values_filled_by_this_contract": False,
        "claim_and_governance": {
            "sigmetrics_doi": SIGMETRICS_DOI,
            "rt1a2_rt2a1_and_graph_to_rt_mapping_owned_by_paper_authors": True,
            "goal5791_invents_or_selects_paper_algorithm": False,
            "author_binary_or_implementation_compared": False,
            "same_source_v4_downstream_lowering_ablation_only": True,
            "named_row_win_requires_ci_wholly_above_one_and_two_vs_seven_events": True,
            "ci_crossing_one_is_not_a_demonstrated_win": True,
            "ci_wholly_below_one_is_a_retained_loss": True,
            "all_six_rows_retained": True,
            "retry_resume_replacement_tuning_row_drop_or_relabel_allowed": False,
            "universal_rt_core_v4_or_compiler_fusion_claim_allowed": False,
            "measured_performance_claim": (
                "end_to_end_compiler_runtime_lowering_including_evidence_overhead"
            ),
            "pure_device_kernel_timing_claimed": False,
            "trace_overhead_subtraction_correction_or_threshold_change_allowed": False,
            "paper_outcome_consequence_contract": deepcopy(
                PAPER_OUTCOME_CONSEQUENCE_CONTRACT
            ),
        },
        "authority_boundary": {
            "base_contract_authorizes_pod": False,
            "base_contract_authorizes_target_prepare": False,
            "base_contract_authorizes_formal_worker_zero": False,
            "base_contract_authorizes_registered_timing": False,
            "preexecution_authority_is_formal_execution_authority": False,
            "separate_owner_formal_execution_authority_required": True,
            "owner_formal_execution_authority_schema": (
                OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA
            ),
            "owner_formal_execution_status": OWNER_FORMAL_EXECUTION_STATUS,
            "successor_formal_authority_must_pin": [
                "preexecution_authority_file_sha256",
                "target_materialization_binding_sha256",
                "formal_identity_sha256",
                "runtime_budget_authority_sha256",
                "runtime_file_sha256",
                "runtime_sha256",
                "owner_authorization_nonce",
                "execution_target.bound_materialization_and_distinct_create_only_formal_output_roots",
                "execution_target.pod_endpoint",
                "resource_confirmation.window_parent_disk_and_before_worker_zero",
            ],
            "formal_identity_unsigned_payload_may_include_successor_authority_sha256": False,
            "formal_workers_must_pin_successor_formal_authority_sha256": True,
            "formal_workers_must_pin_target_binding_and_formal_identity": True,
            "formal_execution_policy": deepcopy(FORMAL_EXECUTION_POLICY),
            "required_owner_stage_b_authorization_payload": deepcopy(
                FORMAL_AUTHORIZATION
            ),
            "owner_authority_is_absent_from_target_and_formal_identity_preimages": True,
        },
    }


def contract_sha256() -> str:
    return digest(contract_document())


def validate_predecessor_contract(repository_root: Path) -> None:
    path = repository_root / "scripts" / "goal5790_static_formal_contract.py"
    if not path.is_file() or file_sha256(path) \
            != PREDECESSOR_STATIC_CONTRACT_FILE_SHA256:
        raise Goal5791ContractError("Goal5790 predecessor contract file drifted")
    from scripts.goal5790_static_formal_contract import (  # local, audit-only
        contract_sha256 as predecessor_contract_sha256,
    )
    if predecessor_contract_sha256() != PREDECESSOR_STATIC_CONTRACT_SHA256:
        raise Goal5791ContractError("Goal5790 predecessor contract drifted")


def _resolve_authority_record(
    repository_root: Path,
    role: str,
    record: object,
) -> Path:
    if not isinstance(record, dict):
        raise Goal5791ContractError(f"authority_records.{role} is not an object")
    _require_exact_keys(record, {"path", "sha256", "bytes"}, role)
    relative = record["path"]
    if not isinstance(relative, str) or "\\" in relative:
        raise Goal5791ContractError(f"{role}.path must be a POSIX relative path")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or any(
        part in ("", ".", "..") for part in pure.parts
    ):
        raise Goal5791ContractError(f"{role}.path is unsafe")
    unresolved = repository_root.joinpath(*pure.parts)
    if unresolved.is_symlink():
        raise Goal5791ContractError(f"{role}.path may not be a symlink")
    root = repository_root.resolve()
    path = unresolved.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise Goal5791ContractError(f"{role}.path escapes repository root") from exc
    if not path.is_file():
        raise Goal5791ContractError(f"{role}.path is not a regular file")
    byte_count = record["bytes"]
    if not isinstance(byte_count, int) or isinstance(byte_count, bool) \
            or byte_count < 0 or path.stat().st_size != byte_count:
        raise Goal5791ContractError(f"{role}.bytes mismatch")
    expected = _require_sha256(record["sha256"], f"{role}.sha256")
    if file_sha256(path) != expected:
        raise Goal5791ContractError(f"{role}.sha256 mismatch")
    return path


def _require_authorization_false(
    value: object, *, required: set[str], label: str,
) -> dict[str, object]:
    if not isinstance(value, dict) or not required.issubset(value) \
            or any(value[key] is not False for key in required) \
            or any(item is not False for key, item in value.items()
                   if key.endswith("authorized") or key.startswith("authorizes_")):
        raise Goal5791ContractError(f"{label} grants execution or publication")
    return value


def validate_source_authority(path: Path) -> dict[str, object]:
    if file_sha256(path) != SOURCE_AUTHORITY_FILE_SHA256:
        raise Goal5791ContractError(
            "source authority is not the frozen successor authority")
    value = _load_json(path)
    _require_exact_keys(value, {
        "schema", "goal", "date", "status", "decision",
        "base_source_authority", "append_only_amendments",
        "predecessor_source_authority",
        "exact_product_source_delta", "replacement_source_policy",
        "scientific_boundary", "authorization", "authority_sha256",
    }, "source authority")
    claimed = _require_sha256(
        value.get("authority_sha256"), "source authority_sha256")
    unsigned = dict(value)
    del unsigned["authority_sha256"]
    if (
        value.get("schema")
            != "rtdl.goal5791.successor_source_authority.v2"
        or value.get("goal") != GOAL
        or value.get("date") != "2026-08-17"
        or value.get("status")
            != "FROZEN_PRETARGET_SUCCESSOR_SOURCE_POLICY__NOT_EXECUTION_AUTHORITY"
        or value.get("decision")
            != "SELECT_GOAL5790_A1_V4_BASE_PLUS_GOAL5791_A1_AND_A2_TOKEN_AMENDMENTS"
        or claimed != SOURCE_AUTHORITY_SHA256
        or digest(unsigned) != claimed
    ):
        raise Goal5791ContractError("source authority header drifted")
    if value.get("base_source_authority") != {
        "path": "history/internal_docs/goal5791_pre_pod_portable_base_and_bundle_audit_20260817.json",
        "sha256": "38eb0cc50367e65309aab85e8df1b9f9cf28d1922af7e04df5856207d92e0767",
        "bytes": 19_313,
        "selected_base_archive": "history/internal_docs/goal5790_a1_portable_source_v4_20260816.tar.gz",
        "selected_base_archive_sha256": "fe7cb3ea456b02432339dca6fe51f9bd8b05bfbb373c8f13fa38e3a68907fd1f",
        "selected_base_archive_bytes": 3_266_868,
        "selected_base_tree_sha256": "62ff2a310517eed5d3c8ef64d757f714346f211416a6cf7ba5034d9013b24de6",
    }:
        raise Goal5791ContractError("source base identity drifted")
    amendments = value.get("append_only_amendments")
    if not isinstance(amendments, list) or len(amendments) != 2:
        raise Goal5791ContractError("source amendment lineage drifted")
    expected_amendments = (
        (
            "Goal5791-A1",
            "history/internal_docs/goal5791_amendment_a1_pretimer_fusion_execution_token_result_20260817.json",
            "8d3318461956673417d1a57fb57d66d710ca0e96a49769cbbbe47112f7522b66",
            "8d832bcc0c8e93d4b288d84f7eeaec36a109cd6cdfad922f9e61e5e39be4d4ca",
        ),
        (
            "Goal5791-A2",
            "history/internal_docs/goal5791_amendment_a2_segment_plan_input_token_binding_result_20260817.json",
            "60e7fcbdc2ca7b817b76dcd75e283abc0db5b0ac77e59cfede99cb2295a47cfe",
            "4da97263ebfe6b626d93b800539a950efbd8d3138787edf706e6682d6427715e",
        ),
    )
    for record, expected in zip(amendments, expected_amendments):
        if not isinstance(record, dict) or (
            record.get("amendment_id"), record.get("result_path"),
            record.get("result_sha256"), record.get("canonical_content_sha256"),
        ) != expected:
            raise Goal5791ContractError("source amendment identity drifted")
    predecessor = value.get("predecessor_source_authority")
    if predecessor != {
        "path": "history/internal_docs/goal5791_successor_source_authority_20260817.json",
        "sha256": "1382ecb3531f642822dac7d477b1034938abb9d665533ce7f44de424cef66965",
        "bytes": 4_799,
        "authority_sha256": "246a75b62f64e198ecc70b89025a57489d30a68a948ccf14d75a763f521c0886",
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "disposition": "SUPERSEDED_PRETARGET_ONLY__NEVER_EXECUTABLE",
    }:
        raise Goal5791ContractError("source predecessor authority drifted")
    expected_delta = [
        {
            "path": "src/rtdsl/v4_operation_evidence.py",
            "base_sha256": "55aa2a2752914e393462fe501db8e22af1dcacce628ad09ea4d2d7903ca1c9e6",
            "successor_sha256": "ff59cba24c7ae188e9f99c3a29a968e0ea83e465033084e81665ee3eff129026",
            "successor_bytes": 29_709,
            "role": "Prevalidates the exact operation-sequence contract before the registered execute interval.",
        },
        {
            "path": "src/rtdsl/v4_triangle_reduction_device_runtime.py",
            "base_sha256": "bcaca714158eedafd102d73cb2ad0ec3b4c6efc7ec46fc2303d71c4d327a465e",
            "a1_intermediate_sha256": "c38bc3a22488680ecadd518f0e5321c3878f425af20765286716e5b359736741",
            "successor_sha256": "d045c9ce04e5b77bbb7785191cdd07d7430de97e7ffdd4f5e0c3a60937b6ba00",
            "successor_bytes": 36_870,
            "role": "Issues and consumes one exact process-local single-use token per segment while independently binding canonical plan input and segment descriptor.",
        },
    ]
    if value.get("exact_product_source_delta") != expected_delta:
        raise Goal5791ContractError("source exact product delta drifted")
    policy = value.get("replacement_source_policy")
    if not isinstance(policy, dict) or policy.get("exact_product_delta_count") != 2 \
            or any(policy.get(name) is not True for name in (
                "any_other_src_or_native_delta_is_a_stop_condition",
                "successor_source_must_receive_a_new_archive_tree_and_manifest_identity",
                "fresh_home_native_build_required",
                "fresh_home_explicit_plan_input_token_path_closure_required",
                "target_prepare_requires_a_later_exact_source_and_home_authority",
                "formal_worker_zero_requires_a_separate_owner_stage_b_authority",
            )) \
            or policy.get("goal5790_or_goal5791_a1_home_native_or_target_qualification_may_be_inherited") is not False \
            or policy.get("home_registered_performance_timing_count") != 0:
        raise Goal5791ContractError("source replacement policy drifted")
    authorization = value.get("authorization")
    if authorization != {
        "authorizes_home_functional_requalification": True,
        "authorizes_target_prepare": False,
        "authorizes_pod": False,
        "authorizes_formal_worker_zero": False,
        "authorizes_registered_timing": False,
        "authorizes_performance_claim": False,
        "authorizes_publication_or_submission": False,
    }:
        raise Goal5791ContractError("source authorization drifted")
    boundary = value.get("scientific_boundary")
    if not isinstance(boundary, dict) \
            or boundary.get("timing_seen_before_freeze") is not False \
            or boundary.get("native_cuda_optix_bytes_changed_by_amendments") is not False \
            or boundary.get("on_and_off_reducer_operations_changed_by_amendments") is not False \
            or boundary.get("two_versus_seven_operation_sequences_changed_by_amendments") is not False \
            or boundary.get("segment_plan_input_contract") != SEGMENT_PLAN_INPUT_CONTRACT["schema"] \
            or boundary.get("formal_paths_must_use_explicit_plan_input_binding") is not True:
        raise Goal5791ContractError("source scientific boundary drifted")
    return value


def validate_data_authority(path: Path) -> dict[str, object]:
    if file_sha256(path) != DATA_AUTHORITY_FILE_SHA256:
        raise Goal5791ContractError("data authority file identity drifted")
    value = _load_json(path)
    if (
        value.get("schema")
            != "rtdl.goal5791.frozen_triangle_data_and_oracle_authority.v1"
        or value.get("goal") != GOAL
        or value.get("paper_algorithm") != PAPER_ALGORITHM
        or "NOT_EXECUTION_AUTHORITY" not in str(value.get("status"))
    ):
        raise Goal5791ContractError("data authority header drifted")
    claimed = _require_sha256(
        value.get("authority_sha256"), "data authority_sha256",
    )
    unsigned = dict(value)
    del unsigned["authority_sha256"]
    if claimed != DATA_AUTHORITY_SHA256 or digest(unsigned) != claimed:
        raise Goal5791ContractError("data authority seal drifted")
    expected_bundle = {
        "path": "history/internal_docs/goal5784_targeted_data_bundle_v1_20260814.tar.gz",
        "sha256": "f186cd28a5ae767f968eaa1372cd66285934be430bceb77ff14c6cf94e33e6eb",
        "bytes": 273_707_175,
        "manifest_member": "DATA_MANIFEST.json",
        "manifest_member_sha256": "abdf4fb32d6d0f362fbddc9cc102e08c11952982c2804f209938e3035df82ad8",
        "manifest_member_bytes": 1_130,
    }
    if value.get("data_bundle") != expected_bundle:
        raise Goal5791ContractError("data bundle identity drifted")
    if value.get("edge_record_contract") != {
        "encoding": "little_endian_signed_int32_pair",
        "bytes_per_record": 8,
        "loader": "build_segmented_rt_graph_csr_binary",
        "max_relation_rows": 1_000_000,
        "max_directed_edge_rows": 1_000_000,
        "duplicate_and_self_edge_policy": "frozen_loader_canonicalization",
        "triangle_oracle_kind": "previously_frozen_exact_author_count",
    }:
        raise Goal5791ContractError("data edge-record contract drifted")
    datasets = value.get("datasets")
    if not isinstance(datasets, dict):
        raise Goal5791ContractError("data authority datasets are not an object")
    _require_exact_keys(datasets, set(DATASET_IDS), "data authority datasets")
    oracle_authority_id = "xiao_et_al_2025_and_frozen_goal5784_author_count"
    for dataset_id, frozen in DATA_AUTHORITY_DATASETS.items():
        oracle_contract = {
            "schema": "rtdl.goal5791.dataset_oracle_contract.v1",
            "dataset_id": dataset_id,
            "input_sha256": frozen["sha256"],
            "expected_triangle_count": frozen["expected_triangle_count"],
            "oracle_authority_id": oracle_authority_id,
            "paper_algorithm": PAPER_ALGORITHM,
        }
        expected_record = {
            "display_id": frozen["display_id"],
            "member": frozen["member"],
            "sha256": frozen["sha256"],
            "bytes": frozen["bytes"],
            "expected_triangle_count": frozen["expected_triangle_count"],
            "oracle_authority_id": oracle_authority_id,
            "oracle_contract": oracle_contract,
            "oracle_authority_sha256": frozen["oracle_authority_sha256"],
        }
        if datasets[dataset_id] != expected_record \
                or digest(oracle_contract) != frozen["oracle_authority_sha256"]:
            raise Goal5791ContractError(
                f"data or oracle authority drifted for {dataset_id}"
            )
    if value.get("scope") != {
        "scheduled_dataset_count": 3,
        "scheduled_member_count": 3,
        "rt_barneshut_bundle_members_scheduled": False,
        "worker_may_open_unscheduled_bundle_member": False,
        "input_or_oracle_may_change_after_target_timing": False,
        "input_or_oracle_may_select_variant": False,
        "independent_recount_must_rehash_extracted_edge_bytes": True,
    }:
        raise Goal5791ContractError("data scheduling boundary drifted")
    _require_authorization_false(
        value.get("authorization"),
        required={
            "authorizes_pod", "authorizes_target_prepare",
            "authorizes_formal_worker_zero", "authorizes_registered_timing",
            "authorizes_publication_or_submission",
        },
        label="data authority",
    )
    return value


def validate_runtime_budget_authority(path: Path) -> dict[str, object]:
    if file_sha256(path) != RUNTIME_BUDGET_AUTHORITY_FILE_SHA256:
        raise Goal5791ContractError("runtime budget authority identity drifted")
    value = _load_json(path)
    if (
        value.get("schema")
            != "rtdl.goal5791.pre_pod_conservative_runtime_budget.v1"
        or value.get("goal") != GOAL
        or value.get("not_a_performance_result") is not True
        or value.get("not_execution_authority") is not True
        or value.get("target_timing_observed_for_goal5791") is not False
        or value.get("formal_worker_count_for_goal5791") != 0
        or "NOT_EXECUTION_AUTHORITY" not in str(value.get("status"))
    ):
        raise Goal5791ContractError("runtime budget authority header drifted")
    cohort = value.get("cohort")
    frozen = value.get("frozen_budget")
    anti = value.get("anti_outcome_adjustment")
    if not isinstance(cohort, dict) or (
        cohort.get("paper_algorithm") != PAPER_ALGORITHM
        or cohort.get("independent_row_count") != 6
        or cohort.get("balanced_pairs_per_row") != PAIR_COUNT
        or cohort.get("arms_per_pair") != 2
        or cohort.get("fresh_parent_pid_worker_count") != 96
        or cohort.get("arm_ids") != list(VARIANTS)
        or cohort.get("ratio") != "fusion_off_seconds_over_fusion_on_seconds"
    ):
        raise Goal5791ContractError("runtime budget cohort drifted")
    if not isinstance(frozen, dict) or (
        frozen.get("formal_conservative_budget_seconds")
            != 16085.148858741304
        or frozen.get("prepare_conservative_budget_seconds") != 3600.0
        or frozen.get("total_transaction_conservative_budget_seconds")
            != 19685.148858741304
        or not isinstance(frozen.get("recommended_minimum_owner_window_hours"),
                          (int, float))
        or frozen.get("recommended_minimum_owner_window_hours") < 7.0
        or frozen.get("owner_must_confirm_budget_before_create_only_prepare")
            is not True
        or frozen.get("owner_must_confirm_budget_again_before_formal_worker_zero")
            is not True
    ):
        raise Goal5791ContractError("runtime budget values drifted")
    if not isinstance(anti, dict) or (
        anti.get("these_values_may_change_after_any_goal5791_target_timing")
            is not False
        or anti.get("these_values_may_change_after_a_goal5791_worker_starts")
            is not False
        or anti.get("target_timing_may_select_a_new_budget_formula_or_worker_shape")
            is not False
    ):
        raise Goal5791ContractError("runtime budget anti-outcome rule drifted")
    _require_authorization_false(
        value.get("authorization"),
        required={
            "pod_authorized", "create_only_target_prepare_authorized",
            "formal_worker_zero_authorized", "registered_timing_authorized",
            "public_release_authorized", "submission_authorized",
        },
        label="runtime budget authority",
    )
    return value


def validate_expected_value_authority(path: Path) -> dict[str, object]:
    if file_sha256(path) != EXPECTED_VALUE_AUTHORITY_FILE_SHA256:
        raise Goal5791ContractError("expected-value authority identity drifted")
    value = _load_json(path)
    if (
        value.get("schema")
            != "rtdl.goal5790.preregistered_expected_value_and_fallback.v1"
        or value.get("goal") != 5790
        or value.get("status") != "FROZEN_BEFORE_HOME_OR_TARGET_TIMING"
    ):
        raise Goal5791ContractError("expected-value authority header drifted")
    scope = value.get("scope")
    comparison = value.get("comparison")
    fallback = value.get("success_and_fallback")
    governance = value.get("governance")
    if not isinstance(scope, dict) or (
        scope.get("paper_algorithm") != PAPER_ALGORITHM
        or scope.get("datasets")
            != ["com-dblp", "cit-Patents", "soc-LiveJournal1"]
        or scope.get("lifecycles") != list(LIFECYCLES)
        or scope.get("independent_row_count") != 6
        or scope.get("particle_included") is not False
    ):
        raise Goal5791ContractError("expected-value scope drifted")
    if not isinstance(comparison, dict) or (
        comparison.get("ratio") != "fusion_off_seconds_over_fusion_on_seconds"
        or comparison.get("greater_than_one_favors") != FUSION_ON
        or comparison.get("row_local_only") is not True
        or comparison.get("cross_row_or_cross_dataset_compensation_allowed")
            is not False
        or comparison.get("fixed_speedup_floor_used") is not False
    ):
        raise Goal5791ContractError("expected-value comparison drifted")
    if not isinstance(fallback, dict) or (
        fallback.get("all_six_rows_must_be_retained") is not True
        or fallback.get(
            "outcome_directed_repair_retry_resume_replacement_or_row_dropping_allowed"
        ) is not False
        or not all(key in fallback for key in (
            "zero_ci_clear_wins", "mixed_result", "all_rows_win",
        ))
    ):
        raise Goal5791ContractError("expected-value fallback drifted")
    if not isinstance(governance, dict) or (
        governance.get("home_registered_performance_timing_allowed") is not False
        or governance.get("goal5791_target_execution_requires_separate_owner_authorization")
            is not True
        or governance.get("this_file_authorizes_home_or_target_execution")
            is not False
        or governance.get("compiler_fusion_performance_claimed") is not False
    ):
        raise Goal5791ContractError("expected-value governance drifted")
    return value


def validate_citation_authority(path: Path) -> dict[str, object]:
    if file_sha256(path) != CITATION_AUTHORITY_FILE_SHA256:
        raise Goal5791ContractError("citation authority identity drifted")
    value = _load_json(path)
    if value.get("schema") \
            != "rtdl.goal5791.pre_worker_zero_related_work_and_claim_freeze.v1" \
            or value.get("goal") != GOAL \
            or not isinstance(value.get("status"), str) \
            or not str(value["status"]).startswith("FROZEN_") \
            or "NOT_EXECUTION_AUTHORITY" not in str(value["status"]):
        raise Goal5791ContractError("citation authority schema or goal mismatch")
    prior = value.get("nearest_adjacent_primary_work")
    experiment = value.get("goal5791_experiment_claim_freeze")
    authorization = value.get("authorization")
    if not isinstance(prior, dict) or prior.get("doi") != SIGMETRICS_DOI:
        raise Goal5791ContractError("SIGMETRICS DOI is not frozen")
    attribution = prior.get("attribution")
    if not isinstance(attribution, dict) or (
        attribution.get("rt_1a2_algorithm_and_name_owned_by_paper_authors")
        is not True
        or attribution.get("rt_2a1_algorithm_and_name_owned_by_paper_authors")
        is not True
        or attribution.get("graph_to_bvh_geometry_mapping_owned_by_paper_authors")
        is not True
        or attribution.get("graph_to_ray_mapping_owned_by_paper_authors")
        is not True
        or attribution.get("goal5791_invents_or_selects_any_of_these")
        is not False
    ):
        raise Goal5791ContractError("paper algorithm ownership boundary drifted")
    if not isinstance(experiment, dict) or (
        experiment.get("paper_algorithm") != PAPER_ALGORITHM
        or experiment.get("paper_algorithm_is_fixed_not_selected") is not True
        or experiment.get("rt_1a2_included") is not False
        or experiment.get("particle_included") is not False
        or experiment.get("author_binary_arm_included") is not False
        or experiment.get("only_allowlisted_variant") != MECHANISM_ID
    ):
        raise Goal5791ContractError("Goal5791 citation claim boundary drifted")
    matrix = experiment.get("maximum_matrix")
    if not isinstance(matrix, dict) or (
        matrix.get("independent_rows") != 6
        or matrix.get("balanced_pairs_per_row") != PAIR_COUNT
        or matrix.get("arms_per_pair") != 2
        or matrix.get("maximum_fresh_parent_pid_workers") != 96
        or matrix.get("cross_dataset_lifecycle_or_row_compensation") is not False
    ):
        raise Goal5791ContractError("Goal5791 citation matrix drifted")
    required_non_authorizations = {
        "authorizes_pod",
        "authorizes_create_only_target_prepare",
        "authorizes_formal_worker_zero",
        "authorizes_registered_timing",
    }
    if not isinstance(authorization, dict) \
            or not required_non_authorizations.issubset(authorization) \
            or any(authorization[key] is not False
                   for key in required_non_authorizations) \
            or any(item is not False
                   for key, item in authorization.items()
                   if key.startswith("authorizes_")):
        raise Goal5791ContractError("citation authority grants execution")
    return value


def validate_target_materialization_binding(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise Goal5791ContractError("target_materialization_binding is not an object")
    _require_exact_keys(
        value,
        {
            "schema", "goal", "status", "hashes", "nonces", "versions",
            "recipes", "derived_digests", "cache_policy", "binding_sha256",
        },
        "target_materialization_binding",
    )
    if value["schema"] != TARGET_BINDING_SCHEMA or value["goal"] != GOAL \
            or value["status"] != TARGET_BINDING_STATUS:
        raise Goal5791ContractError("target materialization header mismatch")
    hashes = value["hashes"]
    nonces = value["nonces"]
    versions = value["versions"]
    recipes = value["recipes"]
    derived_digests = value["derived_digests"]
    cache = value["cache_policy"]
    if not isinstance(hashes, dict):
        raise Goal5791ContractError("target hashes are not an object")
    _require_exact_keys(hashes, set(TARGET_HASH_SLOTS), "target.hashes")
    for field in TARGET_HASH_SLOTS:
        _require_sha256(hashes[field], f"target.hashes.{field}")
    if not isinstance(nonces, dict):
        raise Goal5791ContractError("target nonces are not an object")
    _require_exact_keys(nonces, set(TARGET_NONCE_SLOTS), "target.nonces")
    for field in TARGET_NONCE_SLOTS:
        _require_nonce(nonces[field], f"target.nonces.{field}")
    if hashes["semantic_request_sha256"] != SEMANTIC_REQUEST_SHA256 \
            or hashes["physical_encoding_sha256"] != PHYSICAL_ENCODING_SHA256:
        raise Goal5791ContractError("frozen semantic or physical identity drifted")
    if not isinstance(versions, dict):
        raise Goal5791ContractError("target versions are not an object")
    _require_exact_keys(versions, set(TARGET_VERSION_SLOTS), "target.versions")
    for field in TARGET_VERSION_SLOTS:
        if not isinstance(versions[field], str) or not versions[field].strip():
            raise Goal5791ContractError(f"target.versions.{field} is empty")
    if not isinstance(recipes, dict):
        raise Goal5791ContractError("target recipes are not an object")
    _require_exact_keys(recipes, set(VARIANTS), "target.recipes")
    for variant, operation_ids in (
        (FUSION_OFF, FUSION_OFF_OPERATION_IDS),
        (FUSION_ON, FUSION_ON_OPERATION_IDS),
    ):
        record = recipes[variant]
        if not isinstance(record, dict):
            raise Goal5791ContractError(f"target.recipes.{variant} is invalid")
        _require_exact_keys(
            record,
            {
                "actual_recipe", "actual_recipe_sha256",
                "claim_wrapper", "claim_wrapper_sha256",
            },
            f"target.recipes.{variant}",
        )
        actual_recipe = record["actual_recipe"]
        if not isinstance(actual_recipe, dict):
            raise Goal5791ContractError(
                f"target actual recipe {variant} is not an object"
            )
        _require_exact_keys(
            actual_recipe,
            {
                "schema", "variant", "target_identity_sha256",
                "cupy_version", "implementation",
            },
            f"target.recipes.{variant}.actual_recipe",
        )
        if (
            actual_recipe["schema"]
                != "rtdl.v4.checked_u64_downstream_operation_identity.v1"
            or actual_recipe["variant"] != variant
            or actual_recipe["target_identity_sha256"]
                != hashes["target_identity_sha256"]
            or actual_recipe["cupy_version"] != versions["cupy_version"]
        ):
            raise Goal5791ContractError(
                f"target actual recipe {variant} identity drifted"
            )
        implementation = actual_recipe["implementation"]
        if not isinstance(implementation, dict):
            raise Goal5791ContractError(
                f"target actual recipe {variant} implementation is invalid"
            )
        if variant == FUSION_OFF:
            expected_implementation = {
                "kind": "trusted_cupy_operation_graph",
                "operations": list(ACTUAL_FUSION_OFF_CUPY_OPERATIONS),
                "opaque_partner_kernel_binary_claimed": False,
            }
            if implementation != expected_implementation:
                raise Goal5791ContractError(
                    "fusion-off actual CuPy operation recipe drifted"
                )
        else:
            _require_exact_keys(
                implementation,
                {
                    "kind", "entry", "source_sha256", "options",
                    "opaque_partner_kernel_binary_claimed",
                },
                "target.recipes.fusion_on.actual_recipe.implementation",
            )
            if (
                implementation["kind"] != "compiler_owned_rawkernel_recipe"
                or implementation["entry"] != ACTUAL_FUSION_ON_ENTRY
                or implementation["options"] != list(ACTUAL_FUSION_ON_OPTIONS)
                or implementation["opaque_partner_kernel_binary_claimed"]
                    is not False
            ):
                raise Goal5791ContractError(
                    "fusion-on actual compiler recipe drifted"
                )
            _require_sha256(
                implementation["source_sha256"],
                "target.recipes.fusion_on.actual_recipe.source_sha256",
            )
        if _require_sha256(
            record["actual_recipe_sha256"],
            f"target.recipes.{variant}.actual_recipe_sha256",
        ) != digest(actual_recipe):
            raise Goal5791ContractError(
                f"target actual recipe {variant} digest mismatch"
            )
        claim_wrapper = record["claim_wrapper"]
        if not isinstance(claim_wrapper, dict):
            raise Goal5791ContractError(
                f"target claim wrapper {variant} is not an object"
            )
        _require_exact_keys(
            claim_wrapper,
            {"variant", "mechanism_id", "allowed_delta_id", "operation_ids"},
            f"target.recipes.{variant}.claim_wrapper",
        )
        if (
            claim_wrapper["variant"] != variant
            or claim_wrapper["mechanism_id"] != MECHANISM_ID
            or claim_wrapper["allowed_delta_id"] != ALLOWED_DELTA_ID
            or claim_wrapper["operation_ids"] != list(operation_ids)
        ):
            raise Goal5791ContractError(
                f"target claim wrapper {variant} drifted"
            )
        if _require_sha256(
            record["claim_wrapper_sha256"],
            f"target.recipes.{variant}.claim_wrapper_sha256",
        ) != digest(claim_wrapper):
            raise Goal5791ContractError(
                f"target claim wrapper {variant} digest mismatch"
            )
    if recipes[FUSION_OFF]["actual_recipe_sha256"] \
            == recipes[FUSION_ON]["actual_recipe_sha256"]:
        raise Goal5791ContractError("target recipes do not encode an ablation")
    if hashes["fusion_off_recipe_sha256"] \
            != recipes[FUSION_OFF]["actual_recipe_sha256"] \
            or hashes["fusion_on_recipe_sha256"] \
            != recipes[FUSION_ON]["actual_recipe_sha256"]:
        raise Goal5791ContractError(
            "target product recipe hash slots drifted"
        )
    if cache != CACHE_POLICY:
        raise Goal5791ContractError("target cache policy drifted")
    if not isinstance(derived_digests, dict):
        raise Goal5791ContractError("target derived digests are not an object")
    _require_exact_keys(
        derived_digests,
        {"provider_program_bundle"},
        "target.derived_digests",
    )
    expected_program_bundle = provider_program_bundle_digest_record(
        hashes, nonces,
    )
    if derived_digests["provider_program_bundle"] != expected_program_bundle:
        raise Goal5791ContractError(
            "provider program bundle digest derivation drifted"
        )
    if hashes["provider_program_bundle_sha256"] \
            != expected_program_bundle["sha256"]:
        raise Goal5791ContractError(
            "provider program bundle hash slot is not its declared derivation"
        )
    claimed = _require_sha256(value["binding_sha256"], "binding_sha256")
    unsigned = dict(value)
    del unsigned["binding_sha256"]
    if digest(unsigned) != claimed:
        raise Goal5791ContractError("target materialization binding seal mismatch")
    return deepcopy(value)


def load_preexecution_authority(
    path: Path,
    *,
    repository_root: Path,
    require_target_binding: bool = False,
    contract_repository_root: Path | None = None,
) -> dict[str, object]:
    validate_predecessor_contract(
        contract_repository_root
        if contract_repository_root is not None
        else Path(__file__).resolve().parents[1]
    )
    value = _load_json(path)
    _require_exact_keys(
        value,
        {
            "schema", "goal", "status", "formal_contract_sha256",
            "schedule_sha256", "authority_records", "dataset_input_sha256",
            "oracle_authority_sha256", "target_materialization_binding",
            "formal_worker_count", "registered_performance_timing_count",
            "authorization", "authority_sha256",
        },
        "preexecution_authority",
    )
    if value["schema"] != PREEXECUTION_AUTHORITY_SCHEMA or value["goal"] != GOAL:
        raise Goal5791ContractError("preexecution authority header mismatch")
    target = value["target_materialization_binding"]
    expected_status = POSTPREPARE_STATUS if target is not None else PRETARGET_STATUS
    if value["status"] != expected_status:
        raise Goal5791ContractError("preexecution authority stage mismatch")
    if value["formal_contract_sha256"] != contract_sha256() \
            or value["schedule_sha256"] != schedule_sha256():
        raise Goal5791ContractError("formal contract or schedule identity drifted")
    claimed = _require_sha256(value["authority_sha256"], "authority_sha256")
    unsigned = dict(value)
    del unsigned["authority_sha256"]
    if digest(unsigned) != claimed:
        raise Goal5791ContractError("preexecution authority seal mismatch")

    records = value["authority_records"]
    if not isinstance(records, dict):
        raise Goal5791ContractError("authority_records is not an object")
    _require_exact_keys(records, set(AUTHORITY_ROLES), "authority_records")
    resolved: dict[str, Path] = {
        role: _resolve_authority_record(repository_root, role, records[role])
        for role in AUTHORITY_ROLES
    }
    if len(set(resolved.values())) != len(resolved):
        raise Goal5791ContractError("authority roles reuse one file path")
    validate_source_authority(resolved["source_authority"])
    data_authority = validate_data_authority(resolved["data_authority"])
    validate_runtime_budget_authority(resolved["runtime_budget_authority"])
    validate_expected_value_authority(resolved["expected_value_authority"])
    validate_citation_authority(resolved["citation_authority"])

    for field in ("dataset_input_sha256", "oracle_authority_sha256"):
        mapping = value[field]
        if not isinstance(mapping, dict):
            raise Goal5791ContractError(f"{field} is not an object")
        _require_exact_keys(mapping, set(DATASET_IDS), field)
        for dataset_id in DATASET_IDS:
            _require_sha256(mapping[dataset_id], f"{field}.{dataset_id}")
    data_records = data_authority["datasets"]
    expected_inputs = {
        dataset_id: data_records[dataset_id]["sha256"]
        for dataset_id in DATASET_IDS
    }
    expected_oracles = {
        dataset_id: data_records[dataset_id]["oracle_authority_sha256"]
        for dataset_id in DATASET_IDS
    }
    if value["dataset_input_sha256"] != expected_inputs \
            or value["oracle_authority_sha256"] != expected_oracles:
        raise Goal5791ContractError(
            "preexecution input or oracle map differs from data authority"
        )

    if value["formal_worker_count"] != 0 \
            or value["registered_performance_timing_count"] != 0:
        raise Goal5791ContractError("preexecution authority contains target work")
    authorization = value["authorization"]
    if not isinstance(authorization, dict):
        raise Goal5791ContractError("authorization is not an object")
    _require_exact_keys(
        authorization,
        {
            "authorizes_pod", "authorizes_target_prepare",
            "authorizes_formal_workers", "authorizes_registered_timing",
        },
        "authorization",
    )
    if any(item is not False for item in authorization.values()):
        raise Goal5791ContractError("preexecution authority grants execution")

    if target is None:
        if require_target_binding:
            raise Goal5791ContractError("target materialization is not yet bound")
    else:
        validate_target_materialization_binding(target)
    return deepcopy(value)


def load_owner_formal_execution_authority(
    path: Path,
    *,
    preexecution_authority_path: Path | None = None,
    repository_root: Path | None = None,
    contract_repository_root: Path | None = None,
    preexecution_authority: Mapping[str, object] | None = None,
    preexecution_authority_file_sha256: str | None = None,
) -> dict[str, object]:
    """Load the Stage-B owner authority and bind it to Stage A exactly.

    This is the only authority schema in this module that can authorize the
    formal workers.  Its seal is downstream of, and absent from, the target
    materialization binding and formal-identity preimages; the chain therefore
    remains acyclic.
    """

    path_mode = preexecution_authority_path is not None \
        or repository_root is not None
    snapshot_mode = preexecution_authority is not None \
        or preexecution_authority_file_sha256 is not None
    if path_mode == snapshot_mode:
        raise Goal5791ContractError(
            "owner loader requires exactly one preexecution input mode"
        )
    if path_mode:
        if preexecution_authority_path is None or repository_root is None:
            raise Goal5791ContractError(
                "path mode requires preexecution path and repository root"
            )
        preexecution = load_preexecution_authority(
            preexecution_authority_path,
            repository_root=repository_root,
            require_target_binding=True,
            contract_repository_root=contract_repository_root,
        )
        observed_preexecution_file_sha256 = file_sha256(
            preexecution_authority_path
        )
    else:
        # This mode exists for a worker that has just called the strict shared
        # loader itself and must not duplicate filesystem authority resolution.
        # Recheck every sealed matrix/target/authorization invariant consumed
        # below; file and citation rehashing remain the preceding loader call's
        # responsibility.
        if not isinstance(preexecution_authority, Mapping):
            raise Goal5791ContractError(
                "validated preexecution snapshot is not an object"
            )
        preexecution = deepcopy(dict(preexecution_authority))
        _require_exact_keys(
            preexecution,
            {
                "schema", "goal", "status", "formal_contract_sha256",
                "schedule_sha256", "authority_records", "dataset_input_sha256",
                "oracle_authority_sha256", "target_materialization_binding",
                "formal_worker_count", "registered_performance_timing_count",
                "authorization", "authority_sha256",
            },
            "validated_preexecution_snapshot",
        )
        if preexecution["schema"] != PREEXECUTION_AUTHORITY_SCHEMA \
                or preexecution["goal"] != GOAL \
                or preexecution["status"] != POSTPREPARE_STATUS \
                or preexecution["formal_contract_sha256"] != contract_sha256() \
                or preexecution["schedule_sha256"] != schedule_sha256():
            raise Goal5791ContractError(
                "validated preexecution snapshot identity drifted"
            )
        preexecution_claimed = _require_sha256(
            preexecution["authority_sha256"],
            "validated preexecution snapshot authority_sha256",
        )
        preexecution_unsigned = dict(preexecution)
        del preexecution_unsigned["authority_sha256"]
        if digest(preexecution_unsigned) != preexecution_claimed:
            raise Goal5791ContractError(
                "validated preexecution snapshot seal drifted"
            )
        if preexecution["formal_worker_count"] != 0 \
                or preexecution["registered_performance_timing_count"] != 0:
            raise Goal5791ContractError(
                "validated preexecution snapshot contains target work"
            )
        expected_preexecution_authorization = {
            "authorizes_pod": False,
            "authorizes_target_prepare": False,
            "authorizes_formal_workers": False,
            "authorizes_registered_timing": False,
        }
        if preexecution["authorization"] != expected_preexecution_authorization:
            raise Goal5791ContractError(
                "validated preexecution snapshot grants execution"
            )
        snapshot_records = preexecution["authority_records"]
        if not isinstance(snapshot_records, dict):
            raise Goal5791ContractError(
                "validated preexecution authority records are not an object"
            )
        _require_exact_keys(
            snapshot_records, set(AUTHORITY_ROLES),
            "validated_preexecution_snapshot.authority_records",
        )
        for role in AUTHORITY_ROLES:
            record = snapshot_records[role]
            if not isinstance(record, dict):
                raise Goal5791ContractError(
                    f"validated preexecution record {role} is not an object"
                )
            _require_exact_keys(
                record, {"path", "sha256", "bytes"},
                f"validated_preexecution_snapshot.{role}",
            )
            _require_sha256(
                record["sha256"],
                f"validated_preexecution_snapshot.{role}.sha256",
            )
            if not isinstance(record["path"], str) or not record["path"] \
                    or isinstance(record["bytes"], bool) \
                    or not isinstance(record["bytes"], int) \
                    or record["bytes"] < 0:
                raise Goal5791ContractError(
                    f"validated preexecution record {role} drifted"
                )
        for field in ("dataset_input_sha256", "oracle_authority_sha256"):
            mapping = preexecution[field]
            if not isinstance(mapping, dict):
                raise Goal5791ContractError(
                    f"validated preexecution {field} is not an object"
                )
            _require_exact_keys(
                mapping, set(DATASET_IDS),
                f"validated_preexecution_snapshot.{field}",
            )
            for dataset_id in DATASET_IDS:
                _require_sha256(
                    mapping[dataset_id],
                    f"validated_preexecution_snapshot.{field}.{dataset_id}",
                )
        snapshot_target = preexecution["target_materialization_binding"]
        validate_target_materialization_binding(snapshot_target)
        observed_preexecution_file_sha256 = _require_sha256(
            preexecution_authority_file_sha256,
            "preexecution_authority_file_sha256",
        )
    value = _load_json(path)
    _require_exact_keys(
        value,
        {
            "schema", "goal", "status", "formal_contract_sha256",
            "schedule_sha256", "preexecution_authority_file_sha256",
            "target_materialization_binding_sha256", "formal_identity_sha256",
            "runtime_budget_authority_sha256", "runtime_file_sha256",
            "runtime_sha256", "owner_authorization_nonce",
            "independent_row_count", "formal_worker_count", "execution_target",
            "resource_confirmation", "execution_policy", "authorization",
            "authority_sha256",
        },
        "owner_formal_execution_authority",
    )
    if value["schema"] != OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA \
            or value["goal"] != GOAL \
            or value["status"] != OWNER_FORMAL_EXECUTION_STATUS:
        raise Goal5791ContractError("owner formal authority header mismatch")
    if value["formal_contract_sha256"] != contract_sha256() \
            or value["schedule_sha256"] != schedule_sha256():
        raise Goal5791ContractError(
            "owner authority contract or schedule identity drifted"
        )
    claimed = _require_sha256(
        value["authority_sha256"], "owner authority_sha256",
    )
    unsigned = dict(value)
    del unsigned["authority_sha256"]
    if digest(unsigned) != claimed:
        raise Goal5791ContractError("owner formal authority seal mismatch")

    if value["preexecution_authority_file_sha256"] \
            != observed_preexecution_file_sha256:
        raise Goal5791ContractError("owner authority preexecution file drifted")
    target = preexecution["target_materialization_binding"]
    if not isinstance(target, dict):  # guarded above; retained fail-closed
        raise Goal5791ContractError("owner authority has no Stage-A target")
    if value["target_materialization_binding_sha256"] \
            != target["binding_sha256"]:
        raise Goal5791ContractError("owner authority target binding drifted")
    target_hashes = target["hashes"]
    if not isinstance(target_hashes, dict) \
            or value["formal_identity_sha256"] \
            != target_hashes["formal_identity_sha256"]:
        raise Goal5791ContractError("owner authority formal identity drifted")
    runtime_record = preexecution["authority_records"][
        "runtime_budget_authority"
    ]
    if not isinstance(runtime_record, dict) \
            or value["runtime_budget_authority_sha256"] \
            != runtime_record["sha256"]:
        raise Goal5791ContractError("owner authority runtime budget drifted")
    _require_sha256(value["runtime_file_sha256"], "runtime_file_sha256")
    _require_sha256(value["runtime_sha256"], "runtime_sha256")
    _require_nonce(
        value["owner_authorization_nonce"], "owner_authorization_nonce",
    )
    if value["independent_row_count"] != len(statistical_rows()) \
            or value["formal_worker_count"] != len(schedule()):
        raise Goal5791ContractError("owner authority matrix count drifted")

    resources = value["resource_confirmation"]
    if not isinstance(resources, dict):
        raise Goal5791ContractError("resource_confirmation is not an object")
    _require_exact_keys(
        resources,
        set(FORMAL_OUTPUT_LAYOUT_CONTRACT["resource_confirmation_fields"]),
        "resource_confirmation",
    )
    window = resources["owner_confirmed_uninterrupted_window_hours"]
    disk = resources["confirmed_free_disk_bytes"]
    authority_observed_disk = resources[
        "formal_output_parent_free_bytes_observed_at_authority_creation"]
    minimum_disk = resources["minimum_required_free_disk_bytes"]
    if isinstance(window, bool) or not isinstance(window, (int, float)) \
            or not math.isfinite(float(window)) or float(window) < 7.0 \
            or isinstance(disk, bool) or not isinstance(disk, int) \
            or isinstance(authority_observed_disk, bool) \
            or not isinstance(authority_observed_disk, int) \
            or isinstance(minimum_disk, bool) \
            or not isinstance(minimum_disk, int) \
            or minimum_disk != FORMAL_OUTPUT_LAYOUT_CONTRACT[
                "minimum_required_free_disk_bytes"] \
            or disk < minimum_disk \
            or authority_observed_disk < disk \
            or resources["confirmed_before_formal_worker_zero"] is not True:
        raise Goal5791ContractError("owner resource confirmation is insufficient")

    execution_target = value["execution_target"]
    if not isinstance(execution_target, dict):
        raise Goal5791ContractError("execution_target is not an object")
    _require_exact_keys(
        execution_target,
        set(FORMAL_OUTPUT_LAYOUT_CONTRACT["execution_target_fields"]),
        "execution_target",
    )
    materialization_root = PurePosixPath(_validate_narrow_goal5791_remote_root(
        execution_target["target_materialization_root"]
    ))
    formal_output_root = PurePosixPath(_validate_narrow_goal5791_remote_root(
        execution_target["create_only_formal_output_root"]
    ))
    controller_staging_root = PurePosixPath(
        _validate_narrow_goal5791_remote_root(
            execution_target["controller_incomplete_staging_root"]
        )
    )
    expected_staging_root = formal_output_root.with_name(
        f".{formal_output_root.name}.goal5791_incomplete")
    if (
        len({materialization_root, formal_output_root,
             controller_staging_root}) != 3
        or len({materialization_root.parent, formal_output_root.parent,
                controller_staging_root.parent}) != 1
        or controller_staging_root != expected_staging_root
        or resources["formal_output_parent_resolved_path"]
            != formal_output_root.parent.as_posix()
        or execution_target[
            "target_materialization_root_observed_existing_and_bound_at_authority_creation"
        ] is not True
        or execution_target[
            "formal_output_root_observed_absent_at_authority_creation"
        ] is not True
        or execution_target[
            "controller_incomplete_staging_root_observed_absent_at_authority_creation"
        ] is not True
        or execution_target[
            "preexisting_or_shared_formal_output_root_allowed"] is not False
    ):
        raise Goal5791ContractError(
            "materialization/formal-output sibling-root policy drifted")
    endpoint = execution_target["pod_endpoint"]
    if not isinstance(endpoint, dict):
        raise Goal5791ContractError("POD endpoint is not an object")
    _require_exact_keys(
        endpoint, {"ssh_user", "host", "port", "identity_sha256"},
        "pod_endpoint",
    )
    expected_endpoint = pod_endpoint_identity_record(
        ssh_user=endpoint["ssh_user"],
        host=endpoint["host"],
        port=endpoint["port"],
    )
    if endpoint != expected_endpoint:
        raise Goal5791ContractError("POD endpoint identity digest drifted")
    if value["execution_policy"] != FORMAL_EXECUTION_POLICY:
        raise Goal5791ContractError("exactly-once execution policy drifted")
    if value["authorization"] != FORMAL_AUTHORIZATION:
        raise Goal5791ContractError("owner execution authorization drifted")
    return deepcopy(value)


__all__ = [
    "ACTUAL_FUSION_OFF_CUPY_OPERATIONS",
    "ACTUAL_FUSION_ON_ENTRY",
    "ACTUAL_FUSION_ON_OPTIONS",
    "ALLOWED_DELTA_ID",
    "AUTHORITY_FILE_SHA256",
    "AUTHORITY_ROLES",
    "BOOTSTRAP_CI_INDICES",
    "BOOTSTRAP_DRAWS",
    "BOOTSTRAP_SEED_BASE",
    "CACHE_POLICY",
    "CITATION_AUTHORITY_FILE_SHA256",
    "COLD",
    "DATASETS",
    "DATA_AUTHORITY_DATASETS",
    "DATA_AUTHORITY_FILE_SHA256",
    "DATA_AUTHORITY_SHA256",
    "DATASET_IDS",
    "EXECUTE_CONTROL_CONTRACT",
    "EXECUTE_FORBIDDEN_WORK",
    "EXECUTION_STATE",
    "EXPECTED_VALUE_AUTHORITY_FILE_SHA256",
    "FUSION_OFF",
    "FUSION_OFF_OPERATION_IDS",
    "FUSION_ON",
    "FUSION_ON_OPERATION_IDS",
    "FORMAL_AUTHORIZATION",
    "FORMAL_EXECUTION_POLICY",
    "FORMAL_OUTPUT_LAYOUT_CONTRACT",
    "FORMAL_WORKER_ENVIRONMENT_CONTRACT",
    "GOAL",
    "Goal5791ContractError",
    "IMMUTABLE_CONTROL_FILE_OBSERVATION_CONTRACT",
    "INDEPENDENT_RECOUNT_REVIEW_STATUS",
    "LIFECYCLES",
    "MECHANISM_ID",
    "MECHANISM_SCOPE_DECISION",
    "NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT",
    "ORACLE_CONTRACT",
    "OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA",
    "OWNER_FORMAL_EXECUTION_STATUS",
    "OUTPUT_CONTRACT",
    "PAIR_COUNT",
    "PAPER_ALGORITHM",
    "PAPER_OUTCOME_CONSEQUENCE_CONTRACT",
    "PREPARATION_REQUIRED_WORK",
    "POSTPREPARE_STATUS",
    "PREEXECUTION_AUTHORITY_SCHEMA",
    "PRETARGET_STATUS",
    "PREPARED",
    "PROJECT_STATE_REVIEW_FILE_SHA256",
    "PROJECT_STATE_REVIEW_PATH",
    "PHYSICAL_ENCODING_SHA256",
    "SCHEMA",
    "SEMANTIC_REQUEST_SHA256",
    "SEGMENT_PLAN_INPUT_CONTRACT",
    "SIGMETRICS_DOI",
    "SOURCE_AUTHORITY_FILE_SHA256",
    "SOURCE_AUTHORITY_SHA256",
    "SOURCE_ADMISSION_POLICY",
    "STAGE_A_THIRD_POD_JUSTIFICATION",
    "CONTROLLER_BOOTSTRAP_OBSERVATION_CONTRACT",
    "RESOURCE_ADMISSION_CONTRACT",
    "RESULT_LIFECYCLE_LABELS",
    "TARGET_RUNTIME_ADMISSION_CONTRACT",
    "TARGET_BINDING_SCHEMA",
    "TARGET_BINDING_STATUS",
    "TARGET_HASH_SLOTS",
    "TARGET_NONCE_SLOTS",
    "TARGET_VERSION_SLOTS",
    "TRACE_INSTRUMENTATION_CONTRACT",
    "TRACE_COST_DIAGNOSTIC_AUTHORITY_FILE_SHA256",
    "TRACE_COST_DIAGNOSTIC_AUTHORITY_PATH",
    "TRACE_COST_DIAGNOSTIC_AUTHORITY_SHA256",
    "TRACE_COST_DIAGNOSTIC_SOURCE_SHA256",
    "RUNTIME_BUDGET_AUTHORITY_FILE_SHA256",
    "PROVIDER_PROGRAM_BUNDLE_SOURCE_HASH_SLOTS",
    "PROVIDER_PROGRAM_BUNDLE_SOURCE_NONCE_SLOTS",
    "VARIANTS",
    "contract_document",
    "contract_sha256",
    "digest",
    "expected_operation_contract",
    "file_sha256",
    "input_contract_sha256",
    "lifecycle_contract",
    "lifecycle_contract_sha256",
    "load_owner_formal_execution_authority",
    "load_preexecution_authority",
    "oracle_contract_sha256",
    "output_contract_sha256",
    "provider_program_bundle_digest_record",
    "provider_program_bundle_source_bindings",
    "pod_endpoint_identity_record",
    "result_lifecycle_label",
    "result_row_id",
    "schedule",
    "schedule_document",
    "schedule_sha256",
    "statistical_rows",
    "timer_contract",
    "timer_contract_sha256",
    "validate_citation_authority",
    "validate_data_authority",
    "validate_expected_value_authority",
    "validate_phase_accounting",
    "validate_predecessor_contract",
    "validate_runtime_budget_authority",
    "validate_source_authority",
    "validate_target_materialization_binding",
    "variant_order",
]
