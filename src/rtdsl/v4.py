from __future__ import annotations

from .v4_fixed_radius import V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE
from .v4_fixed_radius import V4FixedRadiusCountThreshold2DDeviceArraySession
from .v4_fixed_radius import allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4
from .v4_fixed_radius import fixed_radius_count_threshold_2d_device_array_claim_boundary_v4
from .v4_fixed_radius import prepare_fixed_radius_count_threshold_2d_device_arrays_v4
from .v4_operator_catalog import V4_OPERATOR_CATALOG_STATUS
from .v4_operator_catalog import V4OperatorPlan
from .v4_operator_catalog import measured_v4_tier2_operator_catalog
from .v4_operator_catalog import plan_v4_operator_request
from .v4_ray_triangle import V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE
from .v4_ray_triangle import V4_RAY_TRIANGLE_ANY_HIT_FLAGS_DEVICE_ARRAY_SURFACE
from .v4_ray_triangle import V4ClosestHitGroupedArgmin3DDeviceArraySession
from .v4_ray_triangle import V4RayTriangleAnyHitFlags2DDeviceArraySession
from .v4_ray_triangle import allocate_closest_hit_grouped_argmin_3d_device_array_outputs_v4
from .v4_ray_triangle import allocate_ray_triangle_any_hit_flags_2d_device_array_outputs_v4
from .v4_ray_triangle import closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4
from .v4_ray_triangle import prepare_closest_hit_grouped_argmin_3d_device_arrays_v4
from .v4_ray_triangle import prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4
from .v4_ray_triangle import ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4
from .v4_scope import V4ScopeGate
from .v4_scope import v4_0_scope_gate
from .v4_scope import validate_v4_0_scope_gate


V4_FRONT_DOOR_STATUS = "v4_development_front_door_not_release"
V4_FRONT_DOOR_MEASURED_PARTNER = "torch"


def claim_boundary_v4() -> dict[str, object]:
    """Return the unified V4 front-door claim boundary."""

    return {
        "status": V4_FRONT_DOOR_STATUS,
        "measured_partner": V4_FRONT_DOOR_MEASURED_PARTNER,
        "measured_surfaces": (
            V4_FIXED_RADIUS_DEVICE_ARRAY_SURFACE,
            V4_CLOSEST_HIT_GROUPED_ARGMIN_DEVICE_ARRAY_SURFACE,
            V4_RAY_TRIANGLE_ANY_HIT_FLAGS_DEVICE_ARRAY_SURFACE,
        ),
        "operator_catalog_status": V4_OPERATOR_CATALOG_STATUS,
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "embedding_c_abi_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def measured_operator_catalog_v4() -> list[dict[str, object]]:
    """Return the measured V4 Tier-2 operator catalog through the unified front door."""

    return measured_v4_tier2_operator_catalog()


def plan_operator_request_v4(*args, **kwargs) -> V4OperatorPlan:
    """Plan a V4 operator/callback request through the unified front door."""

    return plan_v4_operator_request(*args, **kwargs)


__all__ = [
    "V4_FRONT_DOOR_STATUS",
    "V4_FRONT_DOOR_MEASURED_PARTNER",
    "claim_boundary_v4",
    "measured_operator_catalog_v4",
    "plan_operator_request_v4",
    "V4OperatorPlan",
    "V4ScopeGate",
    "v4_0_scope_gate",
    "validate_v4_0_scope_gate",
    "V4FixedRadiusCountThreshold2DDeviceArraySession",
    "V4ClosestHitGroupedArgmin3DDeviceArraySession",
    "V4RayTriangleAnyHitFlags2DDeviceArraySession",
    "fixed_radius_count_threshold_2d_device_array_claim_boundary_v4",
    "prepare_fixed_radius_count_threshold_2d_device_arrays_v4",
    "allocate_fixed_radius_count_threshold_2d_device_array_outputs_v4",
    "closest_hit_grouped_argmin_3d_device_array_claim_boundary_v4",
    "prepare_closest_hit_grouped_argmin_3d_device_arrays_v4",
    "allocate_closest_hit_grouped_argmin_3d_device_array_outputs_v4",
    "ray_triangle_any_hit_flags_2d_device_array_claim_boundary_v4",
    "prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4",
    "allocate_ray_triangle_any_hit_flags_2d_device_array_outputs_v4",
]
