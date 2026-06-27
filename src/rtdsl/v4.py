from __future__ import annotations

from .v4_aabb_index import V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE
from .v4_aabb_index import V4AabbIndexQuery2DAllOpsCountPreparedRunner
from .v4_aabb_index import aabb_index_query_2d_all_ops_count_claim_boundary_v4
from .v4_aabb_index import prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4
from .v4_aggregate_frontier import V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CANDIDATE_STATUS
from .v4_aggregate_frontier import V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_MEASURED_STATUS
from .v4_aggregate_frontier import V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PREPARED_RUNNER_SURFACE
from .v4_aggregate_frontier import V4AggregateFrontierDeviceColumns2DPreparedRunner
from .v4_aggregate_frontier import aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4
from .v4_aggregate_frontier import prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS
from .v4_custom_predicate_early_exit import V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE
from .v4_custom_predicate_early_exit import V4CustomPredicateEarlyExitPlan
from .v4_custom_predicate_early_exit import V4RayTriangleCustomPredicateEarlyExit3DNumbaSession
from .v4_custom_predicate_early_exit import plan_ray_triangle_custom_predicate_early_exit_v4
from .v4_custom_predicate_early_exit import prepare_ray_triangle_custom_predicate_early_exit_3d_numba_v4
from .v4_custom_predicate_early_exit import ray_triangle_custom_predicate_early_exit_claim_boundary_v4
from .v4_fixed_radius import V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE
from .v4_fixed_radius import V4FixedRadiusCountThreshold2DDeviceArraySession
from .v4_fixed_radius import allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4
from .v4_fixed_radius import fixed_radius_count_threshold_2d_device_array_claim_boundary_v4
from .v4_fixed_radius import prepare_fixed_radius_count_threshold_2d_device_arrays_v4
from .v4_app_compatibility import V4_APP_COMPATIBILITY_STATUS
from .v4_app_compatibility import plan_v4_app_compatibility
from .v4_app_compatibility import validate_v4_app_compatibility_catalog
from .v4_app_compatibility import v4_app_compatibility_rows
from .v4_operator_catalog import V4_OPERATOR_CATALOG_STATUS
from .v4_operator_catalog import V4OperatorPlan
from .v4_operator_catalog import V4PushdownRecognition
from .v4_operator_catalog import candidate_v4_tier2_operator_catalog
from .v4_operator_catalog import certified_v4_partner_operator_catalog
from .v4_operator_catalog import measured_v4_tier2_operator_catalog
from .v4_operator_catalog import plan_v4_operator_request
from .v4_operator_catalog import recognize_v4_pushdown_request
from .v4_point_group import V4_POINT_GROUP_NEAREST_WITNESS_DEVICE_ARRAY_SURFACE
from .v4_point_group import V4PointGroupNearestWitness2DDeviceArraySession
from .v4_point_group import allocate_point_group_nearest_witness_2d_device_array_outputs_v4
from .v4_point_group import point_group_nearest_witness_2d_device_array_claim_boundary_v4
from .v4_point_group import prepare_point_group_nearest_witness_2d_device_arrays_v4
from .v4_ranked_summary import V4_FIXED_RADIUS_RANKED_SUMMARY_3D_CANDIDATE_STATUS
from .v4_ranked_summary import V4_FIXED_RADIUS_RANKED_SUMMARY_3D_DEFERRED_STATUS
from .v4_ranked_summary import V4_FIXED_RADIUS_RANKED_SUMMARY_3D_PREPARED_RUNNER_SURFACE
from .v4_ranked_summary import fixed_radius_ranked_summary_3d_prepared_runner_claim_boundary_v4
from .v4_ranked_summary import run_fixed_radius_ranked_summary_3d_prepared_runner_v4
from .v4_ray_triangle import V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE
from .v4_ray_triangle import V4_PRIMITIVE_GROUPED_I64_REDUCTION_DEVICE_ARRAY_SURFACE
from .v4_ray_triangle import V4_RAY_TRIANGLE_ANY_HIT_FLAGS_DEVICE_ARRAY_SURFACE
from .v4_ray_triangle import V4_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_DEVICE_ARRAY_SURFACE
from .v4_ray_triangle import V4ClosestHitGroupedArgmin3DDeviceArraySession
from .v4_ray_triangle import V4PrimitiveGroupedI64Reduction3DDeviceArraySession
from .v4_ray_triangle import V4RayTriangleAnyHitFlags2DDeviceArraySession
from .v4_ray_triangle import V4RayTriangleAnyHitWeightedSum3DDeviceArraySession
from .v4_ray_triangle import allocate_closest_hit_grouped_argmin_3d_device_array_outputs_v4
from .v4_ray_triangle import allocate_primitive_grouped_i64_reduction_3d_device_array_outputs_v4
from .v4_ray_triangle import allocate_ray_triangle_any_hit_flags_2d_device_array_outputs_v4
from .v4_ray_triangle import allocate_ray_triangle_any_hit_weighted_sum_3d_device_array_output_v4
from .v4_ray_triangle import closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4
from .v4_ray_triangle import prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4
from .v4_ray_triangle import prepare_closest_hit_grouped_argmin_3d_device_arrays_v4
from .v4_ray_triangle import prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4
from .v4_ray_triangle import prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4
from .v4_ray_triangle import primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4
from .v4_ray_triangle import ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4
from .v4_ray_triangle import ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4
from .v4_scope import V4ScopeGate
from .v4_scope import v4_0_scope_gate
from .v4_scope import validate_v4_0_scope_gate
from .v4_shape_pair_relation import V4ShapePairRelationActiveCount2DPreparedLeftExecutor
from .v4_shape_pair_relation import prepare_shape_pair_relation_active_count_2d_prepared_left_executor_v4
from .v4_shape_pair_relation import shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4


V4_FRONT_DOOR_STATUS = "v4_python_edsl_operator_pushdown_front_door_complete_rt_core_matrix"
V4_FRONT_DOOR_MEASURED_PARTNER = "mixed_torch_numba_cupy_and_rtdl_native"
V4_APP_LEVEL_DECISION_LABEL = (
    "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim"
)
V4_PUBLIC_RELEASE_TAG = "v4.0.0"
V4_PUBLIC_RELEASE_COMMIT = "resolved_by_git_tag_object"
V4_AUTHORIZED_RELEASE_LABEL = (
    "RTDL V4.0.0 published Python eDSL/operator-pushdown release and V2/V3 "
    "superset: complete 10-app NVIDIA RT-core V2.14/V3.0.2/V4.0 matrix, "
    "bounded material wins, and measured generic operator surfaces; broad "
    "all-benchmark speedup remains unauthorized"
)


def claim_boundary_v4() -> dict[str, object]:
    """Return the unified V4 front-door claim boundary."""

    measured_catalog = measured_v4_tier2_operator_catalog()
    certified_partner_catalog = certified_v4_partner_operator_catalog()
    candidate_catalog = candidate_v4_tier2_operator_catalog()
    app_compatibility = validate_v4_app_compatibility_catalog()
    measured_surfaces = tuple(str(row["api_surface"]) for row in measured_catalog)
    certified_partner_surfaces = tuple(str(row["api_surface"]) for row in certified_partner_catalog)
    candidate_surfaces = tuple(str(row["api_surface"]) for row in candidate_catalog)
    measured_partners = tuple(
        sorted({str(partner) for row in measured_catalog for partner in row["measured_partners"]})
    )
    certified_partners = tuple(
        sorted({str(partner) for row in certified_partner_catalog for partner in row["measured_partners"]})
    )
    return {
        "status": V4_FRONT_DOOR_STATUS,
        "measured_partner": V4_FRONT_DOOR_MEASURED_PARTNER,
        "measured_partners": measured_partners,
        "measured_surfaces": measured_surfaces,
        "certified_partners": certified_partners,
        "certified_partner_surfaces": certified_partner_surfaces,
        "certified_partner_surface_count": len(certified_partner_surfaces),
        "operator_catalog_status": V4_OPERATOR_CATALOG_STATUS,
        "app_compatibility_status": V4_APP_COMPATIBILITY_STATUS,
        "app_compatibility_row_count": app_compatibility["row_count"],
        "app_compatibility_repair_required_apps": tuple(app_compatibility["repair_required_apps"]),
        "candidate_surfaces": candidate_surfaces,
        "measured_surface_count": len(measured_surfaces),
        "current_app_level_decision_label": V4_APP_LEVEL_DECISION_LABEL,
        "complete_rt_core_app_matrix_available": True,
        "complete_rt_core_app_matrix_app_count": 10,
        "complete_rt_core_app_matrix_row_count": 30,
        "app_matrix_hot_path_regression_count": 0,
        "app_matrix_material_hot_path_apps": ("triangle_counting", "barnes_hut"),
        "app_matrix_material_hot_path_candidate_apps": ("triangle_counting", "barnes_hut"),
        "app_matrix_v4_over_v2_14_hot_geomean": 2.10069,
        "public_release_status": "published",
        "public_release_tag": V4_PUBLIC_RELEASE_TAG,
        "public_release_commit": V4_PUBLIC_RELEASE_COMMIT,
        "public_release_commit_source": "git tag object v4.0.0",
        "v4_0_0_public_tag_created": True,
        "bounded_public_release_authorized": True,
        "v4_python_edsl_release_candidate_supported": True,
        "operator_pushdown_workflow_high_performance_supported": True,
        "custom_predicate_early_exit_surface": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
        "custom_predicate_early_exit_serious_scale_v3_geomean": 4.632757911153888,
        "custom_predicate_early_exit_serious_scale_min_v3": 2.054686620906942,
        "formal_release_authorized": False,
        "authorized_release_label": V4_AUTHORIZED_RELEASE_LABEL,
        "bounded_operator_surface_available": True,
        "app_level_high_performance_authorized": False,
        "all_historical_benchmark_apps_faster_claim_authorized": False,
        "broad_v4_over_v2_14_speedup_claim_authorized": False,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "tier3_callback_claim_authorized": False,
        "tier3_specialized_callback_candidate_label": "not_public_v4_0",
        "tier3_specialized_callback_candidate_status": "deferred_not_public_v4_0",
        "tier3_specialized_callback_public_support_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "embedding_c_abi_claim_authorized": False,
        "non_python_host_binding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def measured_operator_catalog_v4() -> list[dict[str, object]]:
    """Return the measured V4 Tier-2 operator catalog through the unified front door."""

    return measured_v4_tier2_operator_catalog()


def candidate_operator_catalog_v4() -> list[dict[str, object]]:
    """Return non-release V4 Tier-2 candidates through the unified front door."""

    return candidate_v4_tier2_operator_catalog()


def certified_partner_catalog_v4() -> list[dict[str, object]]:
    """Return V4 certified partner surfaces through the unified front door."""

    return certified_v4_partner_operator_catalog()


def plan_operator_request_v4(*args, **kwargs) -> V4OperatorPlan:
    """Plan a V4 operator/callback request through the unified front door."""

    return plan_v4_operator_request(*args, **kwargs)


def recognize_pushdown_request_v4(*args, **kwargs) -> V4PushdownRecognition:
    """Recognize a minimal declarative V4 push-down request through the front door."""

    return recognize_v4_pushdown_request(*args, **kwargs)


PUBLIC_API_SYMBOLS_V4 = (
    "V4_FRONT_DOOR_STATUS",
    "V4_FRONT_DOOR_MEASURED_PARTNER",
    "V4_APP_LEVEL_DECISION_LABEL",
    "V4_PUBLIC_RELEASE_TAG",
    "V4_PUBLIC_RELEASE_COMMIT",
    "V4_AUTHORIZED_RELEASE_LABEL",
    "V4_OPERATOR_CATALOG_STATUS",
    "claim_boundary_v4",
    "measured_operator_catalog_v4",
    "candidate_operator_catalog_v4",
    "certified_partner_catalog_v4",
    "plan_operator_request_v4",
    "recognize_pushdown_request_v4",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE",
    "V4CustomPredicateEarlyExitPlan",
    "V4RayTriangleCustomPredicateEarlyExit3DNumbaSession",
    "ray_triangle_custom_predicate_early_exit_claim_boundary_v4",
    "plan_ray_triangle_custom_predicate_early_exit_v4",
    "prepare_ray_triangle_custom_predicate_early_exit_3d_numba_v4",
    "V4AabbIndexQuery2DAllOpsCountPreparedRunner",
    "V4AggregateFrontierDeviceColumns2DPreparedRunner",
    "V4OperatorPlan",
    "V4PushdownRecognition",
    "V4ScopeGate",
    "v4_0_scope_gate",
    "validate_v4_0_scope_gate",
    "V4FixedRadiusCountThreshold2DDeviceArraySession",
    "V4ClosestHitGroupedArgmin3DDeviceArraySession",
    "V4RayTriangleAnyHitFlags2DDeviceArraySession",
    "V4PrimitiveGroupedI64Reduction3DDeviceArraySession",
    "V4RayTriangleAnyHitWeightedSum3DDeviceArraySession",
    "V4PointGroupNearestWitness2DDeviceArraySession",
    "V4ShapePairRelationActiveCount2DPreparedLeftExecutor",
    "shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4",
    "prepare_shape_pair_relation_active_count_2d_prepared_left_executor_v4",
    "V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE",
    "aabb_index_query_2d_all_ops_count_claim_boundary_v4",
    "prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CANDIDATE_STATUS",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_MEASURED_STATUS",
    "V4_AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_PREPARED_RUNNER_SURFACE",
    "aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4",
    "prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4",
    "fixed_radius_count_threshold_2d_device_array_claim_boundary_v4",
    "prepare_fixed_radius_count_threshold_2d_device_arrays_v4",
    "allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4",
    "closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4",
    "prepare_closest_hit_grouped_argmin_3d_device_arrays_v4",
    "allocate_closest_hit_grouped_argmin_3d_device_array_outputs_v4",
    "ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4",
    "prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4",
    "allocate_ray_triangle_any_hit_flags_2d_device_array_outputs_v4",
    "ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4",
    "prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4",
    "allocate_ray_triangle_any_hit_weighted_sum_3d_device_array_output_v4",
    "primitive_grouped_i64_reduction_3d_device_array_claim_boundary_v4",
    "prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4",
    "allocate_primitive_grouped_i64_reduction_3d_device_array_outputs_v4",
    "point_group_nearest_witness_2d_device_array_claim_boundary_v4",
    "prepare_point_group_nearest_witness_2d_device_arrays_v4",
    "allocate_point_group_nearest_witness_2d_device_array_outputs_v4",
    "V4_FIXED_RADIUS_RANKED_SUMMARY_3D_CANDIDATE_STATUS",
    "V4_FIXED_RADIUS_RANKED_SUMMARY_3D_DEFERRED_STATUS",
    "V4_FIXED_RADIUS_RANKED_SUMMARY_3D_PREPARED_RUNNER_SURFACE",
    "fixed_radius_ranked_summary_3d_prepared_runner_claim_boundary_v4",
    "run_fixed_radius_ranked_summary_3d_prepared_runner_v4",
)


__all__ = list(PUBLIC_API_SYMBOLS_V4)


def __dir__() -> list[str]:
    """Return the clean V4 public API for interactive users."""

    return sorted(PUBLIC_API_SYMBOLS_V4)
