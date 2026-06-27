from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE


V4_OPERATOR_CATALOG_STATUS = "v4_0_0_formal_release_catalog"
V4_GOAL4630_PUSHDOWN_RECOGNIZER_STATUS = "goal4630_minimum_pushdown_recognizer_not_release"
V4_TIER2_MEASURED_SURFACE_STATUS = "tier2_measured_v4_0_0_release_surface"
V4_TIER2_DEFERRED_PARTNER_STATUS = "tier2_declared_unmeasured_partner"
V4_CERTIFIED_PARTNER_SURFACE_STATUS = "certified_partner_surface_goal4651_not_formal_v4_speed_win"
V4_CERTIFIED_PARTNER_DEFERRED_STATUS = "certified_partner_declared_unmeasured"
V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS = "tier3_protocol_goal4622_spike_only_not_support"
V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC = "future/v4/tier3_callback_spike_protocol_2026-06-24.md"
V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS = "rejected_by_goal4622_action_shape_boundary"
V4_TIER2_DEFERRED_SURFACE_STATUS = "deferred_goal4678_serious_scale_parity_not_release"

V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD = "fixed_radius_count_threshold"
V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN = "closest_hit_grouped_argmin"
V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS = "ray_triangle_any_hit_flags"
V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION = "primitive_grouped_i64_reduction"
V4_TIER2_POINT_GROUP_NEAREST_WITNESS = "point_group_nearest_witness"
V4_TIER2_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM = "ray_triangle_any_hit_weighted_sum"
V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION = "fixed_radius_graph_component_union_3d"
V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT = "aabb_index_query_2d_all_ops_count"
V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D = "fixed_radius_ranked_summary_3d"
V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D = "aggregate_frontier_device_columns_2d"
V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT = "ray_triangle_custom_predicate_early_exit"

V4_TIER2_OPERATOR_SURFACES = {
    V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD: {
        "api_surface": "v4_fixed_radius_count_threshold_2d_device_arrays",
        "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "count_threshold",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_section8_pod",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
    },
    V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN: {
        "api_surface": "v4_closest_hit_grouped_argmin_3d_device_arrays",
        "generic_primitive": "CLOSEST_HIT_GROUPED_ARGMIN_3D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "argmin",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_section8_pod",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
    },
    V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS: {
        "api_surface": "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        "generic_primitive": "RAY_TRIANGLE_ANY_HIT_FLAGS_2D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "any_hit_flag",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_section8_pod",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
    },
    V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION: {
        "api_surface": "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        "generic_primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "grouped_i64_reduction",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_goal4617_pod_optix8",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "optix_9_1_validated": False,
    },
    V4_TIER2_POINT_GROUP_NEAREST_WITNESS: {
        "api_surface": "v4_point_group_nearest_witness_2d_device_arrays",
        "generic_primitive": "POINT_GROUP_NEAREST_WITNESS_2D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "nearest_witness",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_goal4618_pod_optix8",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "distance_precision": "float32_computed_float64_output",
        "prepared_search_groups": "rtdl_owned_native_scene",
        "optix_9_1_validated": False,
    },
    V4_TIER2_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM: {
        "api_surface": "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        "generic_primitive": "RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D",
        "measured_partners": ("torch",),
        "declared_unmeasured_partners": ("cupy",),
        "continuation_class": "any_hit_weighted_sum",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_goal4633_pod_optix8",
        "direct_device_input_columns": True,
        "direct_device_output_columns": False,
        "direct_device_output_scalar": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "optix_9_1_validated": False,
        "comparison_class": "same_operator_comparable_route",
        "comparable_route_ratio_range": "1.2011x-2.1459x",
        "comparable_route_geomean": 1.5457333064727565,
        "performance_caveat": "largest_shape_barely_clears_1_20x_floor_not_large_speedup",
    },
    V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION: {
        "api_surface": "v4_fixed_radius_graph_component_union_3d_device_arrays",
        "generic_primitive": "FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D",
        "measured_partners": ("numba",),
        "declared_unmeasured_partners": ("torch", "cupy"),
        "continuation_class": "component_union",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_goal4635_pod_optix8_numba",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "numba 0.65.1 / CUDA on RTX A5000",
        "optix_9_1_validated": False,
        "comparison_class": "same_contract_embree_control_and_legacy_optix_control",
        "runner_vs_embree_hot_speedup": 1.3930791165731065,
        "runner_vs_embree_wall_speedup": 1.6001250028719352,
        "runner_vs_legacy_wall_speedup": 1.2080037787208602,
        "performance_caveat": "component-union gate is Numba-scoped operator coverage, not whole-app RTDBSCAN speedup",
    },
    V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT: {
        "api_surface": "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
        "generic_primitive": "AABB_INDEX_QUERY_2D",
        "measured_partners": ("rtdl_native",),
        "declared_unmeasured_partners": ("torch", "cupy", "numba"),
        "continuation_class": "aabb_index_all_ops_count",
        "surface_status": V4_TIER2_MEASURED_SURFACE_STATUS,
        "partner_claim_status": "measured_on_v4_goal4636c_pod_optix8_native",
        "direct_device_input_columns": False,
        "direct_device_output_columns": False,
        "direct_device_output_scalar": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "rtdl_native OptiX prepared query set / Embree control",
        "optix_9_1_validated": False,
        "comparison_class": "same_contract_family_embree_control",
        "runner_vs_embree_hot_speedup": 264.8223871986397,
        "runner_vs_embree_wall_speedup": 115.00724056766381,
        "performance_caveat": "AABB gate is generic operator coverage, not LibRTS paper reproduction or whole-app speedup",
    },
    V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D: {
        "api_surface": "v4_aggregate_frontier_device_columns_2d_prepared_runner",
        "generic_primitive": "AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D",
        "measured_partners": ("rtdl_native", "cupy"),
        "declared_unmeasured_partners": ("torch", "numba"),
        "continuation_class": "aggregate_frontier_device_columns",
        "surface_status": "tier2_measured_goal4677_v2_14_host_frontier_bottleneck_no_release",
        "partner_claim_status": "measured_on_v4_goal4676_pod_optix8_cupy_continuation_not_broad_cupy_claim",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "direct_device_output_scalar": False,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "CuPy 14.1.1 downstream continuation on RTX A5000; RTDL native frontier-only route",
        "optix_9_1_validated": False,
        "comparison_class": "v2_14_host_frontier_bottleneck_vs_device_columns_controlled_by_v3_parity",
        "runner_vs_v2_14_frontier_only_hot_speedup": 302.9977973413469,
        "runner_vs_v2_14_full_hot_speedup": 310.02390072012497,
        "runner_vs_v2_14_full_wall_speedup": 200.82645806332002,
        "runner_vs_v3_0_2_full_hot_ratio": 0.9975684883734833,
        "performance_caveat": (
            "Goal4676 measures removal of the V2.14 host-materialized aggregate-frontier bottleneck; "
            "V4 is parity with V3.0.2 because V3.0.2 already contains the same device-column primitive family"
        ),
        "source_evidence": (
            "future/v4/evidence/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.json",
            "future/v4/evidence/v4_goal4676_serious_2026-06-25/summary.json",
            "future/v4/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.md",
        ),
    },
    V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT: {
        "api_surface": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
        "generic_primitive": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE,
        "measured_partners": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS,
        "declared_unmeasured_partners": ("torch", "cupy", "rtdl_native"),
        "continuation_class": "custom_predicate_early_exit",
        "surface_status": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS,
        "partner_claim_status": "measured_on_v4_goal4715_pod_optix8_numba_callback",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "direct_device_output_scalar": False,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": (
            "Numba C-ABI boolean/scalar device predicate linked into generated OptiX any-hit route"
        ),
        "optix_9_1_validated": False,
        "comparison_class": "operator_pushdown_vs_materialized_device_fallback",
        "constrained_user_predicate_authorized": True,
        "accepted_callback_shapes": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES,
        "accepted_actions": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS,
        "rtdl_owned_action": True,
        "arbitrary_callback_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "primary_v2_speedup_geomean": 3.608025018751732,
        "primary_v3_speedup_geomean": 3.608025018751732,
        "min_primary_v3_speedup": 1.9761904761904763,
        "max_primary_v3_speedup": 8.130865199087879,
        "control_v3_speedup_geomean": 1.5585401086027044,
        "serious_scale_primary_v2_speedup_geomean": 4.632757911153888,
        "serious_scale_primary_v3_speedup_geomean": 4.632757911153888,
        "serious_scale_min_primary_v3_speedup": 2.054686620906942,
        "serious_scale_max_primary_v3_speedup": 9.673329274891774,
        "serious_scale_control_v3_speedup_geomean": 1.6303665522050805,
        "performance_caveat": (
            "focused predicate early-exit operator-pushdown timing gate; "
            "not arbitrary callback support and not an all-app speed claim"
        ),
        "source_evidence": (
            "future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.json",
            "future/v4/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md",
            "future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.json",
        ),
    },
}

V4_TIER2_CANDIDATE_OPERATOR_SURFACES = {}

V4_TIER2_DEFERRED_OPERATOR_SURFACES = {
    V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D: {
        "api_surface": "v4_fixed_radius_ranked_summary_3d_prepared_runner",
        "generic_primitive": "FIXED_RADIUS_RANKED_SUMMARY_3D",
        "measured_partners": (),
        "declared_unmeasured_partners": ("rtdl_native", "torch", "cupy", "numba"),
        "continuation_class": "ranked_summary_topk",
        "status": V4_TIER2_DEFERRED_SURFACE_STATUS,
        "surface_status": V4_TIER2_DEFERRED_SURFACE_STATUS,
        "partner_claim_status": "deferred_not_measured_not_release",
        "direct_device_input_columns": False,
        "direct_device_output_columns": False,
        "direct_device_output_scalar": True,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "comparison_class": "goal4660_4661_serious_scale_parity_no_go",
        "performance_caveat": (
            "executed and validated as a generic prepared runner, but serious "
            "262144 and 1048576 point rows did not produce material speedup"
        ),
        "source_evidence": (
            "future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json",
            "future/v4/v4_goal4660_4661_rtnn_ranked_summary_candidate_evidence_2026-06-25.md",
        ),
    },
}

V4_CERTIFIED_PARTNER_OPERATOR_SURFACES = {
    "grouped_vector_sum_f64x2": {
        "api_surface": "prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')",
        "generic_primitive": "GROUPED_VECTOR_SUM_F64X2",
        "measured_partners": ("cupy",),
        "declared_unmeasured_partners": ("torch", "numba", "rtdl_native"),
        "continuation_class": "grouped_vector_sum",
        "surface_status": V4_CERTIFIED_PARTNER_SURFACE_STATUS,
        "partner_claim_status": "certified_on_v4_goal4649_pod_cupy_not_v4_speed_win",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "direct_device_output_scalar": False,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "cupy 14.1.1 / CUDA runtime 12090 on RTX A5000",
        "baseline_denominator": "same_contract_python_cpu_row_loop_and_optional_numba_partner_control",
        "scale": "rows 262144/524288, groups 1024/2048, repeat 100, warmup 3",
        "representative_speedup_floor": 1.20,
        "partner_parity_floor": 0.98,
        "min_representative_speedup": 1716.8217704918034,
        "representative_speedup_range": "1716.8218x-2390.9160x",
        "comparison_class": "partner_certification_same_contract_python_cpu_row_loop_denominator",
        "claim_class": "partner_certified_surface_not_formal_v4_speed_win",
        "rt_core_operator_surface": False,
        "source_evidence": (
            "future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json",
            "future/v4/v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md",
            "future/v4/reviews/goal4649_completion_consensus_2026-06-25.md",
        ),
        "partner_migration_counts_as_v4_speed_win": False,
        "partner_parity_counts_as_v4_speed_win": False,
    },
    V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION: {
        "api_surface": "v4_fixed_radius_graph_component_union_3d_device_arrays",
        "generic_primitive": "FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D",
        "measured_partners": ("numba",),
        "declared_unmeasured_partners": ("torch", "cupy"),
        "continuation_class": "component_union",
        "surface_status": V4_CERTIFIED_PARTNER_SURFACE_STATUS,
        "partner_claim_status": "certified_on_v4_goal4650_from_goal4635_pod_numba",
        "direct_device_input_columns": True,
        "direct_device_output_columns": True,
        "direct_device_output_scalar": False,
        "host_materialization_in_hot_path": False,
        "true_zero_copy_authorized": False,
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_driver": "570.195.03",
        "validated_partner_scope": "numba 0.65.1 / CUDA on RTX A5000",
        "baseline_denominator": "same_contract_embree_control_and_legacy_optix_control",
        "scale": "clustered3d 262144 points, repeat 5, warmup 1",
        "representative_speedup_floor": 1.20,
        "partner_parity_floor": 0.98,
        "min_representative_speedup": 1.3930791165731065,
        "representative_speedup_range": "1.3931x-1.6001x vs Embree, 1.2080x wall vs legacy",
        "comparison_class": "same_contract_embree_control_and_legacy_optix_control",
        "claim_class": "fixed_numba_certified_tier2_operator_surface_not_whole_app_speed_win",
        "rt_core_operator_surface": True,
        "source_evidence": (
            "future/v4/evidence/v4_goal4650_fixed_numba_continuation_certification_2026-06-25.json",
            "future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json",
            "future/v4/reviews/goal4650_completion_consensus_2026-06-25.md",
        ),
        "partner_migration_counts_as_v4_speed_win": False,
        "partner_parity_counts_as_v4_speed_win": False,
    },
}

V4_OPERATOR_ALIASES = {
    "fixed_radius": V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD,
    "radius_count_threshold": V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD,
    "count_threshold": V4_TIER2_FIXED_RADIUS_COUNT_THRESHOLD,
    "grouped_argmin": V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN,
    "closest_hit_argmin": V4_TIER2_CLOSEST_HIT_GROUPED_ARGMIN,
    "any_hit": V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS,
    "any_hit_flags": V4_TIER2_RAY_TRIANGLE_ANY_HIT_FLAGS,
    "grouped_i64": V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION,
    "grouped_i64_reduction": V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION,
    "primitive_grouped_i64": V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION,
    "primitive_grouped_reduction": V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION,
    "grouped_sum": "grouped_vector_sum_f64x2",
    "grouped_vector_sum": "grouped_vector_sum_f64x2",
    "grouped_vector_sum_2d": "grouped_vector_sum_f64x2",
    "grouped_vector_sum_f64x2": "grouped_vector_sum_f64x2",
    "grouped_reduction": "grouped_vector_sum_f64x2",
    "nearest_witness": V4_TIER2_POINT_GROUP_NEAREST_WITNESS,
    "point_group_nearest": V4_TIER2_POINT_GROUP_NEAREST_WITNESS,
    "point_group_nearest_witness": V4_TIER2_POINT_GROUP_NEAREST_WITNESS,
    "point_group_witness": V4_TIER2_POINT_GROUP_NEAREST_WITNESS,
    "weighted_sum": V4_TIER2_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM,
    "any_hit_weighted_sum": V4_TIER2_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM,
    "ray_triangle_weighted_sum": V4_TIER2_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM,
    "ray_triangle_any_hit_weighted_sum": V4_TIER2_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM,
    "component_union": V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION,
    "radius_graph_component_union": V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION,
    "fixed_radius_graph_component_union": V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION,
    "fixed_radius_graph_component_union_3d": V4_TIER2_FIXED_RADIUS_GRAPH_COMPONENT_UNION,
    "aabb": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "aabb_index": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "aabb_index_query": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "aabb_index_query_2d": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "aabb_index_all_ops": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "aabb_index_all_ops_count": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "aabb_index_query_2d_all_ops_count": V4_TIER2_AABB_INDEX_QUERY_2D_ALL_OPS_COUNT,
    "ranked_summary": V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D,
    "ranked_topk": V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D,
    "topk_summary": V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D,
    "fixed_radius_ranked_summary": V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D,
    "fixed_radius_ranked_summary_3d": V4_TIER2_FIXED_RADIUS_RANKED_SUMMARY_3D,
    "aggregate_frontier": V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D,
    "aggregate_frontier_columns": V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D,
    "aggregate_frontier_device_columns": V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D,
    "aggregate_frontier_device_columns_2d": V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D,
    "frontier_device_columns": V4_TIER2_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D,
    "custom_predicate_early_exit": V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT,
    "predicate_early_exit": V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT,
    "early_exit_predicate": V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT,
    "ray_triangle_custom_predicate_early_exit": V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT,
    "terminate_on_first_accept": V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT,
    "first_acceptable_hit": V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT,
}

V4_SCALAR_TIER3_CANDIDATE_CONTINUATIONS = {
    "custom_scalar_reduce",
    "custom_score",
    "custom_threshold",
    "custom_minmax",
}

V4_APP_IDENTITY_KERNEL_NAMES = {
    "barnes_hut",
    "dbscan",
    "rt_dbscan",
    "rayjoin",
    "spatial_rayjoin",
    "triangle_counting",
    "librts_spatial_index",
    "contact_manifold",
    "robot_collision",
}


@dataclass(frozen=True)
class V4OperatorPlan:
    """Planner result for one V4 operator or callback request."""

    request: str
    status: str
    tier: str
    api_surface: str | None
    generic_primitive: str | None
    measured_partner: bool
    partner: str
    continuation_class: str | None
    guidance: str
    tier3_protocol_status: str | None = None
    tier3_protocol_doc: str | None = None
    release_claim_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_authorized: bool = False
    tier3_callback_claim_authorized: bool = False
    tier3_spike_authorized: bool = False
    raw_optix_callback_claim_authorized: bool = False
    cupy_performance_claim_authorized: bool = False
    embedding_c_abi_claim_authorized: bool = False
    non_python_host_binding_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "request": self.request,
            "status": self.status,
            "tier": self.tier,
            "api_surface": self.api_surface,
            "generic_primitive": self.generic_primitive,
            "measured_partner": self.measured_partner,
            "partner": self.partner,
            "continuation_class": self.continuation_class,
            "guidance": self.guidance,
            "tier3_protocol_status": self.tier3_protocol_status,
            "tier3_protocol_doc": self.tier3_protocol_doc,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "true_zero_copy_authorized": self.true_zero_copy_authorized,
            "tier3_callback_claim_authorized": self.tier3_callback_claim_authorized,
            "tier3_spike_authorized": self.tier3_spike_authorized,
            "raw_optix_callback_claim_authorized": self.raw_optix_callback_claim_authorized,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "embedding_c_abi_claim_authorized": self.embedding_c_abi_claim_authorized,
            "non_python_host_binding_claim_authorized": self.non_python_host_binding_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
        }


@dataclass(frozen=True)
class V4PushdownRecognition:
    """Minimum Goal4630 recognizer result for one declarative request."""

    expression: dict[str, object]
    status: str
    pushdown_recognized: bool
    fail_closed: bool
    operator_source: str | None
    plan: V4OperatorPlan
    guidance: str
    recognizer_status: str = V4_GOAL4630_PUSHDOWN_RECOGNIZER_STATUS
    release_claim_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_authorized: bool = False
    measured_catalog_claim_authorized: bool = False
    tier3_callback_claim_authorized: bool = False
    raw_optix_callback_claim_authorized: bool = False
    cupy_performance_claim_authorized: bool = False
    embedding_c_abi_claim_authorized: bool = False
    non_python_host_binding_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "expression": self.expression,
            "status": self.status,
            "pushdown_recognized": self.pushdown_recognized,
            "fail_closed": self.fail_closed,
            "operator_source": self.operator_source,
            "plan": self.plan.as_dict(),
            "api_surface": self.plan.api_surface,
            "generic_primitive": self.plan.generic_primitive,
            "measured_partner": self.plan.measured_partner,
            "partner": self.plan.partner,
            "continuation_class": self.plan.continuation_class,
            "guidance": self.guidance,
            "recognizer_status": self.recognizer_status,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "true_zero_copy_authorized": self.true_zero_copy_authorized,
            "measured_catalog_claim_authorized": self.measured_catalog_claim_authorized,
            "tier3_callback_claim_authorized": self.tier3_callback_claim_authorized,
            "raw_optix_callback_claim_authorized": self.raw_optix_callback_claim_authorized,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "embedding_c_abi_claim_authorized": self.embedding_c_abi_claim_authorized,
            "non_python_host_binding_claim_authorized": self.non_python_host_binding_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
        }


def _normalize_operator_name(operator: str) -> str:
    key = str(operator).strip().lower().replace("-", "_").replace(" ", "_")
    return V4_OPERATOR_ALIASES.get(key, key)


def _bool_from_expression(expression: Mapping[str, object], key: str) -> bool:
    value = expression.get(key, False)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _first_text_value(expression: Mapping[str, object], keys: tuple[str, ...]) -> tuple[str | None, str | None]:
    for key in keys:
        value = expression.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text, key
    return None, None


def plan_v4_operator_request(
    operator: str,
    *,
    partner: str = "torch",
    callback_shape: str | None = None,
    numba_device_function: bool = False,
    mutates_shared_state: bool = False,
    variable_length_output: bool = False,
    dynamic_allocation: bool = False,
) -> V4OperatorPlan:
    """Classify a V4 request into Tier-2, Tier-3 spike, or rejected guidance.

    The planner is intentionally conservative. It does not execute callbacks or
    authorize release wording; it gives users the V4 boundary before they spend
    time on a path that the engine cannot honestly fuse.
    """

    partner = str(partner)
    normalized = _normalize_operator_name(operator)
    if partner not in {"torch", "cupy", "numba", "rtdl_native"}:
        raise ValueError("partner must be one of: torch, cupy, numba, rtdl_native")

    if normalized == V4_TIER2_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT:
        callback_key = str(callback_shape or "").strip().lower().replace("-", "_").replace(" ", "_")
        if mutates_shared_state or dynamic_allocation or variable_length_output:
            return V4OperatorPlan(
                request=normalized,
                status="rejected_action_shaped_callback_deferred",
                tier="unsupported_v4_0_deferred",
                api_surface=None,
                generic_primitive=None,
                measured_partner=False,
                partner=partner,
                continuation_class=callback_key or "custom_predicate_early_exit",
                guidance=(
                    "custom predicate early-exit accepts only pure boolean/scalar predicates. "
                    "Shared mutation, dynamic allocation, and variable-length output are rejected."
                ),
                tier3_protocol_status=V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS,
                tier3_protocol_doc=V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC,
            )
        if partner != "numba":
            return V4OperatorPlan(
                request=normalized,
                status="tier2_declared_unmeasured_partner",
                tier="tier2_operator_pushdown",
                api_surface=None,
                generic_primitive=V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE,
                measured_partner=False,
                partner=partner,
                continuation_class="custom_predicate_early_exit",
                guidance=(
                    "custom predicate early-exit is measured only for Numba C-ABI device predicates. "
                    "Torch, CuPy, and rtdl_native partner front doors are V4.x deferred."
                ),
            )
        if not numba_device_function or callback_key not in V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES:
            return V4OperatorPlan(
                request=normalized,
                status="rejected_missing_constrained_numba_predicate",
                tier="unsupported_v4_0_deferred",
                api_surface=None,
                generic_primitive=V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE,
                measured_partner=False,
                partner=partner,
                continuation_class=callback_key or "custom_predicate_early_exit",
                guidance=(
                    "custom predicate early-exit requires callback_shape="
                    "pure_boolean_numba_cabi_device_function and numba_device_function=True. "
                    "It is not arbitrary Python callback support."
                ),
            )
        surface = V4_TIER2_OPERATOR_SURFACES[normalized]
        return V4OperatorPlan(
            request=normalized,
            status="tier2_measured_ready",
            tier="tier2_operator_pushdown",
            api_surface=str(surface["api_surface"]),
            generic_primitive=str(surface["generic_primitive"]),
            measured_partner=True,
            partner=partner,
            continuation_class=str(surface["continuation_class"]),
            guidance=(
                f"Use {surface['api_surface']} for constrained Numba predicate early-exit. "
                "RTDL owns terminate/filter actions; the user callback is a pure predicate only."
            ),
        )

    if normalized in V4_TIER2_OPERATOR_SURFACES and callback_shape in (None, "", "builtin"):
        surface = V4_TIER2_OPERATOR_SURFACES[normalized]
        measured = partner in surface["measured_partners"]
        status = "tier2_measured_ready" if measured else "tier2_declared_unmeasured_partner"
        measured_partners = ", ".join(str(item) for item in surface["measured_partners"])
        guidance = (
            f"Use {surface['api_surface']} for this recognized fused operator."
            if measured
            else f"This operator is measured for {measured_partners} only. No V4.0 API surface is exposed for {partner}; treat this partner as V4.x deferred."
        )
        return V4OperatorPlan(
            request=normalized,
            status=status,
            tier="tier2_fused_operator",
            api_surface=str(surface["api_surface"]) if measured else None,
            generic_primitive=str(surface["generic_primitive"]),
            measured_partner=measured,
            partner=partner,
            continuation_class=str(surface["continuation_class"]),
            guidance=guidance,
        )

    if normalized in V4_TIER2_CANDIDATE_OPERATOR_SURFACES and callback_shape in (None, "", "builtin"):
        surface = V4_TIER2_CANDIDATE_OPERATOR_SURFACES[normalized]
        continuation = str(surface["continuation_class"])
        candidate_partners = tuple(surface.get("measured_partners", ())) + tuple(
            surface.get("declared_unmeasured_partners", ())
        )
        exposed = partner in candidate_partners
        return V4OperatorPlan(
            request=normalized,
            status=str(surface["status"]),
            tier="tier2_fused_operator_candidate",
            api_surface=str(surface["api_surface"]) if exposed else None,
            generic_primitive=str(surface["generic_primitive"]),
            measured_partner=False,
            partner=partner,
            continuation_class=continuation,
            guidance=(
                f"{surface['api_surface']} is implemented as a V4 candidate surface, "
                "but it is not a measured V4.0 release surface until external review "
                "and a release decision promote it."
                if exposed
                else f"This {continuation} candidate is not exposed for CuPy performance claims."
            ),
        )

    if normalized in V4_TIER2_DEFERRED_OPERATOR_SURFACES and callback_shape in (None, "", "builtin"):
        surface = V4_TIER2_DEFERRED_OPERATOR_SURFACES[normalized]
        return V4OperatorPlan(
            request=normalized,
            status=str(surface["status"]),
            tier="deferred_v4_x_or_research",
            api_surface=None,
            generic_primitive=str(surface["generic_primitive"]),
            measured_partner=False,
            partner=partner,
            continuation_class=str(surface["continuation_class"]),
            guidance=(
                f"{surface['api_surface']} executed and validated as a generic runner, "
                "but Goal4660/4661 serious rows were parity or below parity. It is "
                "not exposed as a measured or candidate V4 front-door surface."
            ),
        )

    if normalized in V4_CERTIFIED_PARTNER_OPERATOR_SURFACES and callback_shape in (None, "", "builtin"):
        surface = V4_CERTIFIED_PARTNER_OPERATOR_SURFACES[normalized]
        measured = partner in surface["measured_partners"]
        measured_partners = ", ".join(str(item) for item in surface["measured_partners"])
        return V4OperatorPlan(
            request=normalized,
            status="certified_partner_measured_ready" if measured else V4_CERTIFIED_PARTNER_DEFERRED_STATUS,
            tier="certified_partner_surface",
            api_surface=str(surface["api_surface"]) if measured else None,
            generic_primitive=str(surface["generic_primitive"]),
            measured_partner=measured,
            partner=partner,
            continuation_class=str(surface["continuation_class"]),
            guidance=(
                f"Use {surface['api_surface']} for this certified partner surface. "
                "This is partner-front-door certification and must not be counted as a formal V4 speed win."
                if measured
                else f"This certified partner surface is measured for {measured_partners} only. No V4 certified partner API surface is exposed for {partner}; treat this partner as V4.x deferred."
            ),
        )

    if mutates_shared_state or dynamic_allocation or variable_length_output:
        reasons = []
        if mutates_shared_state:
            reasons.append("shared mutation")
        if dynamic_allocation:
            reasons.append("dynamic allocation")
        if variable_length_output:
            reasons.append("variable-length output")
        return V4OperatorPlan(
            request=normalized,
            status="rejected_action_shaped_callback_deferred",
            tier="unsupported_v4_0_deferred",
            api_surface=None,
            generic_primitive=None,
            measured_partner=False,
            partner=partner,
            continuation_class=callback_shape,
            guidance=(
                "This callback is action-shaped ("
                + ", ".join(reasons)
                + "). V4.0 does not expose raw OptiX callbacks or app-specific native kernels; "
                "rewrite as a recognized reduce/filter operator or defer to the constrained Tier-3 spike protocol."
            ),
            tier3_protocol_status=V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS,
            tier3_protocol_doc=V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC,
        )

    callback_key = str(callback_shape or normalized).strip().lower().replace("-", "_").replace(" ", "_")
    if numba_device_function and callback_key in V4_SCALAR_TIER3_CANDIDATE_CONTINUATIONS:
        return V4OperatorPlan(
            request=normalized,
            status="tier3_spike_only_not_v4_0_release_surface",
            tier="tier3_numba_ptx_spike",
            api_surface=None,
            generic_primitive=None,
            measured_partner=False,
            partner=partner,
            continuation_class=callback_key,
            guidance=(
                "This is a scalar per-hit reduce candidate for the Numba->PTX->OptiX spike. "
                "It is not a V4.0 measured surface and must not be documented as supported until "
                "the goal4622 spike protocol links, runs, meets correctness parity, meets compile reliability, "
                "and stays under the fixed overhead ceiling."
            ),
            tier3_protocol_status=V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS,
            tier3_protocol_doc=V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC,
            tier3_spike_authorized=True,
        )

    return V4OperatorPlan(
        request=normalized,
        status="unsupported_no_fused_surface",
        tier="unsupported",
        api_surface=None,
        generic_primitive=None,
        measured_partner=False,
        partner=partner,
        continuation_class=callback_shape,
        guidance=(
            "No V4 fused operator matches this request. Use a measured Tier-2 operator, "
            "rewrite the logic as count/threshold/argmin/any-hit, or treat it as future Tier-3 research."
        ),
    )


def recognize_v4_pushdown_request(
    expression: Mapping[str, object],
    *,
    partner: str = "torch",
) -> V4PushdownRecognition:
    """Recognize a minimal declarative V4 push-down request.

    The recognizer is intentionally a thin Goal4630 slice. It recognizes one
    generic operator at a time, delegates claim boundaries to
    :func:`plan_v4_operator_request`, and fails closed for app-identity kernels,
    action-shaped callbacks, unsupported custom logic, and unmeasured partners.
    """

    if not isinstance(expression, Mapping):
        raise TypeError("expression must be a mapping")

    expr = dict(expression)
    operator_text, operator_source = _first_text_value(
        expr,
        (
            "operator",
            "op",
            "reduce",
            "reduction",
            "continuation",
            "relation",
            "pattern",
            "callback",
        ),
    )
    operator = operator_text or "unsupported"
    normalized = _normalize_operator_name(operator)
    callback_shape = expr.get("callback_shape")
    if callback_shape is not None:
        callback_shape = str(callback_shape)

    kernel_text, _kernel_source = _first_text_value(expr, ("kernel", "native_kernel", "app_kernel"))
    app_identity_probe = _normalize_operator_name(kernel_text or normalized)
    if app_identity_probe in V4_APP_IDENTITY_KERNEL_NAMES:
        plan = V4OperatorPlan(
            request=app_identity_probe,
            status="rejected_app_identity_kernel_deferred",
            tier="unsupported_v4_0_deferred",
            api_surface=None,
            generic_primitive=None,
            measured_partner=False,
            partner=str(partner),
            continuation_class=callback_shape,
            guidance=(
                "This request names an application-identity kernel. V4.0 push-down "
                "recognizes generic continuation operators only; rewrite it as a "
                "count/threshold/argmin/any-hit/grouped-reduction request or defer it."
            ),
        )
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_fail_closed_app_identity_kernel",
            pushdown_recognized=False,
            fail_closed=True,
            operator_source=operator_source,
            plan=plan,
            guidance=plan.guidance,
        )

    plan = plan_v4_operator_request(
        normalized,
        partner=str(partner),
        callback_shape=callback_shape,
        numba_device_function=_bool_from_expression(expr, "numba_device_function"),
        mutates_shared_state=_bool_from_expression(expr, "mutates_shared_state"),
        variable_length_output=_bool_from_expression(expr, "variable_length_output"),
        dynamic_allocation=_bool_from_expression(expr, "dynamic_allocation"),
    )

    if plan.status == "tier2_measured_ready":
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_recognized_measured_tier2",
            pushdown_recognized=True,
            fail_closed=False,
            operator_source=operator_source,
            plan=plan,
            guidance=f"Recognized generic operator; route to {plan.api_surface}.",
        )

    if plan.tier == "tier2_fused_operator_candidate":
        if plan.api_surface is None:
            return V4PushdownRecognition(
                expression=expr,
                status="pushdown_fail_closed_unmeasured_partner",
                pushdown_recognized=False,
                fail_closed=True,
                operator_source=operator_source,
                plan=plan,
                guidance=plan.guidance,
            )
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_recognized_candidate_tier2_not_measured",
            pushdown_recognized=True,
            fail_closed=False,
            operator_source=operator_source,
            plan=plan,
            guidance=(
                "Recognized generic candidate operator, but it is not a measured "
                "release surface and must not be counted as one."
            ),
        )

    if plan.status == "certified_partner_measured_ready":
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_recognized_certified_partner_surface",
            pushdown_recognized=True,
            fail_closed=False,
            operator_source=operator_source,
            plan=plan,
            guidance=(
                f"Recognized certified partner operator; route to {plan.api_surface}. "
                "Do not count this as formal V4-vs-V2.14 speed evidence."
            ),
        )

    if plan.status == V4_CERTIFIED_PARTNER_DEFERRED_STATUS:
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_fail_closed_unmeasured_certified_partner",
            pushdown_recognized=False,
            fail_closed=True,
            operator_source=operator_source,
            plan=plan,
            guidance=plan.guidance,
        )

    if plan.status == "tier2_declared_unmeasured_partner":
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_fail_closed_unmeasured_partner",
            pushdown_recognized=False,
            fail_closed=True,
            operator_source=operator_source,
            plan=plan,
            guidance=plan.guidance,
        )

    if plan.status == "tier3_spike_only_not_v4_0_release_surface":
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_fail_closed_tier3_spike_only",
            pushdown_recognized=False,
            fail_closed=True,
            operator_source=operator_source,
            plan=plan,
            guidance=plan.guidance,
        )

    if plan.status == "rejected_action_shaped_callback_deferred":
        return V4PushdownRecognition(
            expression=expr,
            status="pushdown_fail_closed_action_shape",
            pushdown_recognized=False,
            fail_closed=True,
            operator_source=operator_source,
            plan=plan,
            guidance=plan.guidance,
        )

    return V4PushdownRecognition(
        expression=expr,
        status="pushdown_fail_closed_unsupported",
        pushdown_recognized=False,
        fail_closed=True,
        operator_source=operator_source,
        plan=plan,
        guidance=plan.guidance,
    )


def measured_v4_tier2_operator_catalog() -> list[dict[str, object]]:
    """Return the current measured V4 Tier-2 operator catalog."""

    rows: list[dict[str, object]] = []
    for name, surface in V4_TIER2_OPERATOR_SURFACES.items():
        rows.append(
            {
                "operator": name,
                "catalog_class": "measured",
                "surface_status": surface["surface_status"],
                "api_surface": surface["api_surface"],
                "generic_primitive": surface["generic_primitive"],
                "measured_partners": surface["measured_partners"],
                "declared_unmeasured_partners": surface["declared_unmeasured_partners"],
                "pod_candidate_partners": (),
                "partner_claim_status": surface["partner_claim_status"],
                "continuation_class": surface["continuation_class"],
                "direct_device_input_columns": surface["direct_device_input_columns"],
                "direct_device_output_columns": surface.get("direct_device_output_columns", True),
                "direct_device_output_scalar": surface.get("direct_device_output_scalar", False),
                "host_materialization_in_hot_path": surface["host_materialization_in_hot_path"],
                "true_zero_copy_authorized": surface["true_zero_copy_authorized"],
                "validated_optix_abi": surface.get("validated_optix_abi"),
                "validated_gpu_family": surface.get("validated_gpu_family"),
                "validated_driver": surface.get("validated_driver"),
                "validated_partner_scope": surface.get("validated_partner_scope"),
                "optix_9_1_validated": surface.get("optix_9_1_validated"),
                "distance_precision": surface.get("distance_precision"),
                "prepared_search_groups": surface.get("prepared_search_groups"),
                "comparison_class": surface.get("comparison_class"),
                "comparable_route_ratio_range": surface.get("comparable_route_ratio_range"),
                "comparable_route_geomean": surface.get("comparable_route_geomean"),
                "runner_vs_embree_hot_speedup": surface.get("runner_vs_embree_hot_speedup"),
                "runner_vs_embree_wall_speedup": surface.get("runner_vs_embree_wall_speedup"),
                "runner_vs_legacy_wall_speedup": surface.get("runner_vs_legacy_wall_speedup"),
                "runner_vs_v2_14_frontier_only_hot_speedup": surface.get(
                    "runner_vs_v2_14_frontier_only_hot_speedup"
                ),
                "runner_vs_v2_14_full_hot_speedup": surface.get("runner_vs_v2_14_full_hot_speedup"),
                "runner_vs_v2_14_full_wall_speedup": surface.get("runner_vs_v2_14_full_wall_speedup"),
                "runner_vs_v3_0_2_full_hot_ratio": surface.get("runner_vs_v3_0_2_full_hot_ratio"),
                "constrained_user_predicate_authorized": surface.get(
                    "constrained_user_predicate_authorized", False
                ),
                "accepted_callback_shapes": surface.get("accepted_callback_shapes", ()),
                "accepted_actions": surface.get("accepted_actions", ()),
                "rtdl_owned_action": surface.get("rtdl_owned_action", False),
                "arbitrary_callback_authorized": surface.get("arbitrary_callback_authorized", False),
                "primary_v2_speedup_geomean": surface.get("primary_v2_speedup_geomean"),
                "primary_v3_speedup_geomean": surface.get("primary_v3_speedup_geomean"),
                "min_primary_v3_speedup": surface.get("min_primary_v3_speedup"),
                "max_primary_v3_speedup": surface.get("max_primary_v3_speedup"),
                "control_v3_speedup_geomean": surface.get("control_v3_speedup_geomean"),
                "serious_scale_primary_v2_speedup_geomean": surface.get(
                    "serious_scale_primary_v2_speedup_geomean"
                ),
                "serious_scale_primary_v3_speedup_geomean": surface.get(
                    "serious_scale_primary_v3_speedup_geomean"
                ),
                "serious_scale_min_primary_v3_speedup": surface.get(
                    "serious_scale_min_primary_v3_speedup"
                ),
                "serious_scale_max_primary_v3_speedup": surface.get(
                    "serious_scale_max_primary_v3_speedup"
                ),
                "serious_scale_control_v3_speedup_geomean": surface.get(
                    "serious_scale_control_v3_speedup_geomean"
                ),
                "performance_caveat": surface.get("performance_caveat"),
                "source_evidence": surface.get("source_evidence"),
                "release_claim_authorized": False,
                "broad_v4_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "tier3_callback_claim_authorized": False,
                "raw_optix_callback_claim_authorized": False,
                "cupy_performance_claim_authorized": False,
                "embedding_c_abi_claim_authorized": False,
                "non_python_host_binding_claim_authorized": False,
                "app_specific_native_kernel_authorized": False,
            }
        )
    return rows


def candidate_v4_tier2_operator_catalog() -> list[dict[str, object]]:
    """Return current non-release V4 Tier-2 candidate operators."""

    rows: list[dict[str, object]] = []
    for name, surface in V4_TIER2_CANDIDATE_OPERATOR_SURFACES.items():
        rows.append(
            {
                "operator": name,
                "catalog_class": "candidate",
                "surface_status": surface["status"],
                "api_surface": surface["api_surface"],
                "generic_primitive": surface["generic_primitive"],
                "measured_partners": surface["measured_partners"],
                "pod_candidate_partners": surface["pod_candidate_partners"],
                "declared_unmeasured_partners": surface["declared_unmeasured_partners"],
                "partner_claim_status": surface["partner_claim_status"],
                "continuation_class": surface["continuation_class"],
                "status": surface["status"],
                "direct_device_input_columns": surface["direct_device_input_columns"],
                "direct_device_output_columns": surface.get("direct_device_output_columns", False),
                "direct_device_output_scalar": surface["direct_device_output_scalar"],
                "host_materialization_in_hot_path": surface["host_materialization_in_hot_path"],
                "true_zero_copy_authorized": surface["true_zero_copy_authorized"],
                "release_claim_authorized": False,
                "broad_v4_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "tier3_callback_claim_authorized": False,
                "raw_optix_callback_claim_authorized": False,
                "cupy_performance_claim_authorized": False,
                "embedding_c_abi_claim_authorized": False,
                "non_python_host_binding_claim_authorized": False,
                "app_specific_native_kernel_authorized": False,
            }
        )
    return rows


def certified_v4_partner_operator_catalog() -> list[dict[str, object]]:
    """Return Goal4651 certified partner surfaces.

    These rows are intentionally separate from the measured Tier-2 RT-core
    operator catalog. They document partner front-door certification without
    turning partner migration or partner parity into a formal V4 speed claim.
    """

    rows: list[dict[str, object]] = []
    for name, surface in V4_CERTIFIED_PARTNER_OPERATOR_SURFACES.items():
        rows.append(
            {
                "operator": name,
                "catalog_class": "certified_partner",
                "surface_status": surface["surface_status"],
                "api_surface": surface["api_surface"],
                "generic_primitive": surface["generic_primitive"],
                "measured_partners": surface["measured_partners"],
                "declared_unmeasured_partners": surface["declared_unmeasured_partners"],
                "partner_claim_status": surface["partner_claim_status"],
                "continuation_class": surface["continuation_class"],
                "direct_device_input_columns": surface["direct_device_input_columns"],
                "direct_device_output_columns": surface["direct_device_output_columns"],
                "direct_device_output_scalar": surface["direct_device_output_scalar"],
                "host_materialization_in_hot_path": surface["host_materialization_in_hot_path"],
                "true_zero_copy_authorized": surface["true_zero_copy_authorized"],
                "validated_optix_abi": surface.get("validated_optix_abi"),
                "validated_gpu_family": surface.get("validated_gpu_family"),
                "validated_driver": surface.get("validated_driver"),
                "validated_partner_scope": surface.get("validated_partner_scope"),
                "baseline_denominator": surface["baseline_denominator"],
                "scale": surface["scale"],
                "comparison_class": surface["comparison_class"],
                "claim_class": surface["claim_class"],
                "representative_speedup_floor": surface["representative_speedup_floor"],
                "partner_parity_floor": surface["partner_parity_floor"],
                "min_representative_speedup": surface["min_representative_speedup"],
                "representative_speedup_range": surface["representative_speedup_range"],
                "rt_core_operator_surface": surface["rt_core_operator_surface"],
                "source_evidence": surface["source_evidence"],
                "partner_migration_counts_as_v4_speed_win": surface[
                    "partner_migration_counts_as_v4_speed_win"
                ],
                "partner_parity_counts_as_v4_speed_win": surface[
                    "partner_parity_counts_as_v4_speed_win"
                ],
                "release_claim_authorized": False,
                "broad_v4_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "tier3_callback_claim_authorized": False,
                "raw_optix_callback_claim_authorized": False,
                "cupy_performance_claim_authorized": False,
                "embedding_c_abi_claim_authorized": False,
                "non_python_host_binding_claim_authorized": False,
                "app_specific_native_kernel_authorized": False,
            }
        )
    return rows
