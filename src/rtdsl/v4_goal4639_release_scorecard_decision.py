from __future__ import annotations

from typing import Any


V4_GOAL4639_STATUS = "goal4639_serious_release_scorecard_pod_gate_passed_not_release"
V4_GOAL4639_DECISION = "accept_release_scorecard_continue_to_docs_clean_tree_and_3ai"
V4_GOAL4639_EVIDENCE = (
    "tools/_archive/future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.json",
    "tools/_archive/future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md",
    "tools/_archive/future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/run.log",
)
V4_GOAL4639_SURFACE_RATIOS = {
    "v4_fixed_radius_count_threshold_2d_device_arrays": 1.69721,
    "v4_closest_hit_grouped_argmin_3d_device_arrays": 1.25677,
    "v4_ray_triangle_any_hit_flags_2d_device_arrays": 5.67055,
    "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays": 1.38362,
    "v4_point_group_nearest_witness_2d_device_arrays": 389.707,
    "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays": 1.48181,
    "v4_fixed_radius_graph_component_union_3d_device_arrays": 1.20294,
    "v4_aabb_index_query_2d_all_ops_count_prepared_runner": 164.716,
}
V4_GOAL4639_SURFACE_DENOMINATORS = {
    "v4_fixed_radius_count_threshold_2d_device_arrays": {
        "baseline": "torch brute-force/reference",
        "scale": "script default fixture; repeat=7 warmup=1",
        "presentation_class": "core_cluster_1_2_to_1_7x",
    },
    "v4_closest_hit_grouped_argmin_3d_device_arrays": {
        "baseline": "torch brute-force/reference",
        "scale": "script default grouped-argmin fixtures; repeat=7 warmup=1",
        "presentation_class": "core_cluster_1_2_to_1_7x",
    },
    "v4_ray_triangle_any_hit_flags_2d_device_arrays": {
        "baseline": "torch brute-force/reference",
        "scale": "max_torch_reference_count=8192; repeat=5 warmup=1",
        "presentation_class": "mid_large_operator_win",
    },
    "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays": {
        "baseline": "torch brute-force/reference",
        "scale": "ray_counts=32768,131072; group_widths=1,16,256; repeat=7 warmup=2",
        "presentation_class": "core_cluster_1_2_to_1_7x",
    },
    "v4_point_group_nearest_witness_2d_device_arrays": {
        "baseline": "torch/cpu-style brute-force nearest witness reference",
        "scale": "query_counts=32768,131072; fixture_variants=mixed4,mixed6; repeat=7 warmup=2",
        "presentation_class": "algorithmic_complexity_outlier_o_n2_vs_bvh",
    },
    "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays": {
        "baseline": "torch brute-force/reference comparable route",
        "scale": "Goal4633 promotion gate shapes=32768,131072,262144,524288",
        "presentation_class": "core_cluster_1_2_to_1_7x",
    },
    "v4_fixed_radius_graph_component_union_3d_device_arrays": {
        "baseline": "legacy prepared-runner wall route with Embree same-contract controls",
        "scale": "clustered3d point_count=262144; repeat=5 warmup=1",
        "presentation_class": "core_cluster_1_2_to_1_7x",
    },
    "v4_aabb_index_query_2d_all_ops_count_prepared_runner": {
        "baseline": "Embree same-contract prepared AABB query control",
        "scale": "box_count=1000000; query_count=1000; operation=all; embree/optix repeats=240",
        "presentation_class": "algorithmic_complexity_outlier_indexed_bvh_vs_slower_control",
    },
}
V4_GOAL4639_PUBLIC_RATIO_DISTRIBUTION = {
    "core_operator_cluster": "Most release surfaces are 1.2-1.7x against their stated brute-force partner/CPU baselines.",
    "mid_large_operator_win": "Any-hit flags is a larger 5.671x operator win against its stated Torch reference baseline.",
    "complexity_outliers": (
        "Point-group nearest witness and AABB all-ops are large scale-dependent "
        "wins where the alternative is brute-force or a slower same-contract index control."
    ),
    "headline_rule": "Do not headline the 5.185x geomean; show the distribution and denominators.",
}


def v4_goal4639_release_scorecard_decision() -> dict[str, Any]:
    return {
        "status": V4_GOAL4639_STATUS,
        "decision": V4_GOAL4639_DECISION,
        "recommendation_from_scorecard": "release_candidate_possible_pending_3ai",
        "strong_families_passed": 4,
        "strong_families_total": 4,
        "measured_surfaces_passed": 8,
        "measured_surfaces_total": 8,
        "partial_controls_passed": 4,
        "partial_controls_total": 4,
        "deferred_excluded_rows": 2,
        "failed_surfaces": (),
        "strong_representative_ratio_geomean": 5.1848067367961095,
        "surface_representative_ratios": V4_GOAL4639_SURFACE_RATIOS,
        "surface_denominators": V4_GOAL4639_SURFACE_DENOMINATORS,
        "public_ratio_distribution": V4_GOAL4639_PUBLIC_RATIO_DISTRIBUTION,
        "evidence": V4_GOAL4639_EVIDENCE,
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


def validate_v4_goal4639_release_scorecard_decision() -> dict[str, Any]:
    decision = v4_goal4639_release_scorecard_decision()
    if decision["decision"] != V4_GOAL4639_DECISION:
        raise ValueError("Goal4639 decision drift")
    if decision["strong_families_passed"] != 4 or decision["strong_families_total"] != 4:
        raise ValueError("Goal4639 must preserve 4/4 strong-family pass")
    if decision["measured_surfaces_passed"] != 8 or decision["measured_surfaces_total"] != 8:
        raise ValueError("Goal4639 must preserve 8/8 measured-surface pass")
    if decision["failed_surfaces"] != ():
        raise ValueError("Goal4639 must preserve zero failed surfaces")
    if decision["strong_representative_ratio_geomean"] <= 1.0:
        raise ValueError("Goal4639 strong representative geomean must remain above parity")
    for surface in (
        "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        "v4_fixed_radius_graph_component_union_3d_device_arrays",
    ):
        if decision["surface_representative_ratios"][surface] <= 1.20:
            raise ValueError(f"Goal4639 {surface} must preserve a material ratio above 1.20x")
    for surface in decision["surface_representative_ratios"]:
        denominator = decision["surface_denominators"].get(surface)
        if not denominator:
            raise ValueError(f"Goal4639 missing denominator metadata for {surface}")
        if not denominator["baseline"] or not denominator["scale"]:
            raise ValueError(f"Goal4639 incomplete denominator metadata for {surface}")
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
        if decision[flag]:
            raise ValueError(f"Goal4639 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4639_STATUS",
    "V4_GOAL4639_DECISION",
    "V4_GOAL4639_EVIDENCE",
    "V4_GOAL4639_SURFACE_RATIOS",
    "V4_GOAL4639_SURFACE_DENOMINATORS",
    "V4_GOAL4639_PUBLIC_RATIO_DISTRIBUTION",
    "v4_goal4639_release_scorecard_decision",
    "validate_v4_goal4639_release_scorecard_decision",
]
