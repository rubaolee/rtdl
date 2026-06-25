from __future__ import annotations

from .v4_aabb_index import V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE
from .v4_aabb_index import V4AabbIndexQuery2DAllOpsCountPreparedRunner
from .v4_aabb_index import aabb_index_query_2d_all_ops_count_claim_boundary_v4
from .v4_aabb_index import prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4
from .v4_fixed_radius import V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE
from .v4_fixed_radius import V4FixedRadiusCountThreshold2DDeviceArraySession
from .v4_fixed_radius import allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4
from .v4_fixed_radius import fixed_radius_count_threshold_2d_device_array_claim_boundary_v4
from .v4_fixed_radius import prepare_fixed_radius_count_threshold_2d_device_arrays_v4
from .v4_operator_catalog import V4_OPERATOR_CATALOG_STATUS
from .v4_operator_catalog import V4OperatorPlan
from .v4_operator_catalog import V4PushdownRecognition
from .v4_operator_catalog import candidate_v4_tier2_operator_catalog
from .v4_operator_catalog import measured_v4_tier2_operator_catalog
from .v4_operator_catalog import plan_v4_operator_request
from .v4_operator_catalog import recognize_v4_pushdown_request
from .v4_point_group import V4_POINT_GROUP_NEAREST_WITNESS_DEVICE_ARRAY_SURFACE
from .v4_point_group import V4PointGroupNearestWitness2DDeviceArraySession
from .v4_point_group import allocate_point_group_nearest_witness_2d_device_array_outputs_v4
from .v4_point_group import point_group_nearest_witness_2d_device_array_claim_boundary_v4
from .v4_point_group import prepare_point_group_nearest_witness_2d_device_arrays_v4
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


V4_FRONT_DOOR_STATUS = "v4_scorecard_passed_front_door_pending_final_authorization"
V4_FRONT_DOOR_MEASURED_PARTNER = "mixed_torch_numba_and_rtdl_native"


def claim_boundary_v4() -> dict[str, object]:
    """Return the unified V4 front-door claim boundary."""

    measured_catalog = measured_v4_tier2_operator_catalog()
    measured_surfaces = tuple(str(row["api_surface"]) for row in measured_catalog)
    measured_partners = tuple(
        sorted({str(partner) for row in measured_catalog for partner in row["measured_partners"]})
    )
    return {
        "status": V4_FRONT_DOOR_STATUS,
        "measured_partner": V4_FRONT_DOOR_MEASURED_PARTNER,
        "measured_partners": measured_partners,
        "measured_surfaces": measured_surfaces,
        "operator_catalog_status": V4_OPERATOR_CATALOG_STATUS,
        "candidate_surfaces": (),
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_authorized": False,
        "tier3_callback_claim_authorized": False,
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


def plan_operator_request_v4(*args, **kwargs) -> V4OperatorPlan:
    """Plan a V4 operator/callback request through the unified front door."""

    return plan_v4_operator_request(*args, **kwargs)


def recognize_pushdown_request_v4(*args, **kwargs) -> V4PushdownRecognition:
    """Recognize a minimal declarative V4 push-down request through the front door."""

    return recognize_v4_pushdown_request(*args, **kwargs)


__all__ = [
    "V4_FRONT_DOOR_STATUS",
    "V4_FRONT_DOOR_MEASURED_PARTNER",
    "claim_boundary_v4",
    "measured_operator_catalog_v4",
    "candidate_operator_catalog_v4",
    "plan_operator_request_v4",
    "recognize_pushdown_request_v4",
    "V4AabbIndexQuery2DAllOpsCountPreparedRunner",
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
    "V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE",
    "aabb_index_query_2d_all_ops_count_claim_boundary_v4",
    "prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4",
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
]
