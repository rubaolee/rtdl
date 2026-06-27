from __future__ import annotations

from typing import Any


V4_GOAL4638_FREEZE_STATUS = "goal4638_formal_release_scorecard_frozen_pending_external_review_not_release"
V4_GOAL4638_FREEZE_DECISION = "freeze_v4_release_scorecard_before_goal4639_pod_run"

V4_GOAL4638_STRONG_FAMILIES = (
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
)
V4_GOAL4638_PARTIAL_CONTROL_FAMILIES = (
    "hausdorff_xhd",
    "robot_collision",
    "contact_manifold",
    "rtnn",
)
V4_GOAL4638_DEFERRED_EXCLUDED_FAMILIES = (
    "spatial_rayjoin",
    "barnes_hut",
)
V4_GOAL4638_MEASURED_SURFACES = (
    "v4_fixed_radius_count_threshold_2d_device_arrays",
    "v4_closest_hit_grouped_argmin_3d_device_arrays",
    "v4_ray_triangle_any_hit_flags_2d_device_arrays",
    "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
    "v4_point_group_nearest_witness_2d_device_arrays",
    "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
    "v4_fixed_radius_graph_component_union_3d_device_arrays",
    "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
)

V4_GOAL4638_PERFORMANCE_FLOORS = (
    {
        "surface": "v4_fixed_radius_count_threshold_2d_device_arrays",
        "floor_kind": "fixed_radius_product_boundary_gate",
        "minimum_floor": ">=2 serious sizes with device_array_to_route_d_rows_gap <=100.0 and gap_reduction_over_prior_summary >=10.0; correctness must pass at all frozen sizes",
        "observed_anchor": "gap reduction 1022.93x, 3841.66x, 9699.17x; device-array-to-Route-D-row gaps 0.442x, 0.202x, 0.118x",
        "canonical_source": "tools/_archive/future/v4/evidence/v4_section8_device_array_frontdoor_result_2026-06-24.json",
    },
    {
        "surface": "v4_closest_hit_grouped_argmin_3d_device_arrays",
        "floor_kind": "same_contract_host_materialization_boundary",
        "minimum_floor": "device front door must beat legacy host-materialize route at all 3 frozen ray counts; ratio >=1.0x; correctness must pass",
        "observed_anchor": "1.542x, 1.575x, 1.729x; summary median ratio 1.575x",
        "canonical_source": "tools/_archive/future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_result_2026-06-24.json",
    },
    {
        "surface": "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        "floor_kind": "fixture_reference_plus_large_correctness",
        "minimum_floor": "8192-row torch fixture reference ratio >=1.0x; all 3 frozen ray counts must pass correctness and keep host_materialization_in_hot_path false",
        "observed_anchor": "8192-row torch-reference ratio 9.379x; 32768 and 131072 correctness pass with reference intentionally skipped by protocol",
        "canonical_source": "tools/_archive/future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json",
    },
    {
        "surface": "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        "floor_kind": "same_contract_multi_width_grouped_reduction",
        "minimum_floor": "all 6 frozen rows must pass parity and same-contract ratio >=1.0x",
        "observed_anchor": "166.546x, 411.867x, 11.271x, 21.369x, 1.641x, 2.978x; observed min 1.641x",
        "canonical_source": "tools/_archive/future/v4/v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md",
    },
    {
        "surface": "v4_point_group_nearest_witness_2d_device_arrays",
        "floor_kind": "same_contract_device_output_boundary",
        "minimum_floor": "repeat-gate and mixed6 rows must pass parity and same-contract ratio >=1.0x at both serious sizes",
        "observed_anchor": "repeat gate 663.143x and 1868.088x; mixed6 509.391x and 1863.097x; observed min 509.391x",
        "canonical_source": "tools/_archive/future/v4/point_group_device_array_frontdoor.md",
    },
    {
        "surface": "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        "floor_kind": "same_operator_comparable_route",
        "minimum_floor": "each frozen shape ratio >=1.20x and four-shape geomean >=1.50x; parity must pass at every shape",
        "observed_anchor": "2.1459x, 1.6329x, 1.3564x, 1.2011x; geomean 1.5457x",
        "canonical_source": "tools/_archive/future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json",
    },
    {
        "surface": "v4_fixed_radius_graph_component_union_3d_device_arrays",
        "floor_kind": "component_union_same_fixture_material_gate",
        "minimum_floor": "runner_vs_embree_hot >=1.20x, runner_vs_embree_wall >=1.20x, runner_vs_legacy_wall >=0.98x, and component signatures match",
        "observed_anchor": "runner_vs_embree_hot 1.393x; runner_vs_embree_wall 1.600x; runner_vs_legacy_wall 1.208x; all canonical signatures match",
        "canonical_source": "tools/_archive/future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json",
    },
    {
        "surface": "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
        "floor_kind": "aabb_same_contract_family_embree_control",
        "minimum_floor": "cross-backend count parity must pass; accepted contract family must pass; Embree/OptiX query median >=10.0x and query total >=10.0x",
        "observed_anchor": "query median 264.822x; query total 115.007x; cross-backend count parity true",
        "canonical_source": "tools/_archive/future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json",
    },
)


def v4_goal4638_formal_scorecard_freeze() -> dict[str, Any]:
    return {
        "status": V4_GOAL4638_FREEZE_STATUS,
        "decision": V4_GOAL4638_FREEZE_DECISION,
        "hardware_scope": {
            "gpu_class": "NVIDIA RTX A5000 / Ampere",
            "driver_family": "570.x",
            "validated_optix_abi": "8.0",
            "measured_scopes": ("torch", "numba", "rtdl_native"),
        },
        "benchmark_families": {
            "release_in_scope_strong_operator": V4_GOAL4638_STRONG_FAMILIES,
            "partial_operator_control": V4_GOAL4638_PARTIAL_CONTROL_FAMILIES,
            "deferred_excluded": V4_GOAL4638_DEFERRED_EXCLUDED_FAMILIES,
        },
        "measured_surfaces": V4_GOAL4638_MEASURED_SURFACES,
        "candidate_surfaces": (),
        "performance_floors": V4_GOAL4638_PERFORMANCE_FLOORS,
        "thresholds": {
            "strong_rows_require_correctness": True,
            "strong_rows_require_surface_specific_performance_floor": True,
            "partial_rows_excluded_from_release_geomean": True,
            "deferred_rows_excluded_from_release_geomean": True,
            "no_silent_skips": True,
        },
        "aggregation": {
            "compute_strong_row_pass_fail": True,
            "compute_measured_surface_pass_fail": True,
            "compute_partial_control_pass_fail_blocked": True,
            "compute_deferred_excluded_count": True,
            "geomean_must_exclude_partial_and_deferred": True,
        },
        "allowed_if_passes": (
            "measured generic RT-core operator surfaces beat their stated brute-force partner/CPU baselines for documented measured scopes",
            "bounded by partner/hardware/surface-specific evidence and per-surface denominator metadata",
        ),
        "forbidden_wording": (
            "all benchmark apps are faster",
            "whole-application speedup",
            "broad V4 speedup",
            "public true zero copy",
            "CuPy performance",
            "Tier-3 callbacks are supported",
            "C ABI / embedding / non-Python host support",
            "LibRTS paper reproduced",
            "Barnes-Hut / Spatial RayJoin covered by V4.0",
        ),
        "requires_external_review_before_goal4639": True,
        "release_authorized": False,
        "release_candidate_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4638_formal_scorecard_freeze() -> dict[str, Any]:
    freeze = v4_goal4638_formal_scorecard_freeze()
    if freeze["decision"] != V4_GOAL4638_FREEZE_DECISION:
        raise ValueError("Goal4638 scorecard freeze decision drift")
    families = freeze["benchmark_families"]
    all_families = (
        *families["release_in_scope_strong_operator"],
        *families["partial_operator_control"],
        *families["deferred_excluded"],
    )
    if len(all_families) != 10 or len(set(all_families)) != 10:
        raise ValueError("Goal4638 scorecard must classify exactly 10 unique benchmark families")
    if len(freeze["measured_surfaces"]) != 8:
        raise ValueError("Goal4638 scorecard must include exactly 8 measured surfaces")
    if freeze["candidate_surfaces"] != ():
        raise ValueError("Goal4638 scorecard must freeze zero candidate surfaces")
    floors = freeze["performance_floors"]
    if len(floors) != len(freeze["measured_surfaces"]):
        raise ValueError("Goal4638 must freeze one performance floor per measured surface")
    floor_surfaces = tuple(row["surface"] for row in floors)
    if floor_surfaces != freeze["measured_surfaces"]:
        raise ValueError("Goal4638 performance floors must match measured surface order")
    for row in floors:
        for key in ("floor_kind", "minimum_floor", "observed_anchor", "canonical_source"):
            if not row.get(key):
                raise ValueError(f"Goal4638 performance floor missing {key}")
        if "X.XX" in row["minimum_floor"]:
            raise ValueError("Goal4638 performance floors must not contain placeholder numerics")
    if not freeze["requires_external_review_before_goal4639"]:
        raise ValueError("Goal4638 must require external review before Goal4639")
    thresholds = freeze["thresholds"]
    for key in (
        "strong_rows_require_correctness",
        "strong_rows_require_surface_specific_performance_floor",
        "partial_rows_excluded_from_release_geomean",
        "deferred_rows_excluded_from_release_geomean",
        "no_silent_skips",
    ):
        if thresholds[key] is not True:
            raise ValueError(f"Goal4638 threshold {key} must stay true")
    for flag in (
        "release_authorized",
        "release_candidate_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if freeze[flag]:
            raise ValueError(f"Goal4638 must not authorize {flag}")
    return freeze


__all__ = [
    "V4_GOAL4638_FREEZE_STATUS",
    "V4_GOAL4638_FREEZE_DECISION",
    "V4_GOAL4638_STRONG_FAMILIES",
    "V4_GOAL4638_PARTIAL_CONTROL_FAMILIES",
    "V4_GOAL4638_DEFERRED_EXCLUDED_FAMILIES",
    "V4_GOAL4638_MEASURED_SURFACES",
    "V4_GOAL4638_PERFORMANCE_FLOORS",
    "v4_goal4638_formal_scorecard_freeze",
    "validate_v4_goal4638_formal_scorecard_freeze",
]
