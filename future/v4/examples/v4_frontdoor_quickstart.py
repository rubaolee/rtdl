from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def main() -> int:
    boundary = rtdl_v4.claim_boundary_v4()
    catalog = rtdl_v4.measured_operator_catalog_v4()
    candidate_catalog = rtdl_v4.candidate_operator_catalog_v4()
    tier2_plan = rtdl_v4.plan_operator_request_v4("any-hit", partner="torch")
    aabb_plan = rtdl_v4.plan_operator_request_v4("aabb-index-query", partner="rtdl_native")
    complex_callback_plan = rtdl_v4.plan_operator_request_v4(
        "custom-collision-response",
        callback_shape="custom_action",
        mutates_shared_state=True,
        variable_length_output=True,
        dynamic_allocation=True,
        partner="torch",
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "front_door_status": boundary["status"],
                "measured_partners": list(boundary["measured_partners"]),
                "measured_surface_count": len(boundary["measured_surfaces"]),
                "candidate_surface_count": len(boundary["candidate_surfaces"]),
                "catalog_operator_count": len(catalog),
                "candidate_operator_count": len(candidate_catalog),
                "public_release_status": boundary["public_release_status"],
                "public_release_tag": boundary["public_release_tag"],
                "public_release_commit": boundary["public_release_commit"],
                "public_release_commit_source": boundary["public_release_commit_source"],
                "v4_0_0_public_tag_created": boundary["v4_0_0_public_tag_created"],
                "bounded_public_release_authorized": boundary["bounded_public_release_authorized"],
                "authorized_release_label": boundary["authorized_release_label"],
                "bounded_operator_surface_available": boundary["bounded_operator_surface_available"],
                "app_level_high_performance_authorized": boundary["app_level_high_performance_authorized"],
                "current_app_level_decision_label": boundary["current_app_level_decision_label"],
                "complete_rt_core_app_matrix_available": boundary["complete_rt_core_app_matrix_available"],
                "complete_rt_core_app_matrix_app_count": boundary["complete_rt_core_app_matrix_app_count"],
                "complete_rt_core_app_matrix_row_count": boundary["complete_rt_core_app_matrix_row_count"],
                "app_matrix_hot_path_regression_count": boundary["app_matrix_hot_path_regression_count"],
                "app_matrix_material_hot_path_apps": list(
                    boundary["app_matrix_material_hot_path_apps"]
                ),
                "app_matrix_v4_over_v2_14_hot_geomean": boundary["app_matrix_v4_over_v2_14_hot_geomean"],
                "tier2_plan_status": tier2_plan.status,
                "tier2_plan_surface": tier2_plan.api_surface,
                "aabb_plan_status": aabb_plan.status,
                "aabb_plan_surface": aabb_plan.api_surface,
                "complex_callback_status": complex_callback_plan.status,
                "release_claim_authorized": boundary["release_claim_authorized"],
                "broad_v4_speedup_claim_authorized": boundary["broad_v4_speedup_claim_authorized"],
                "broad_v4_over_v2_14_speedup_claim_authorized": boundary[
                    "broad_v4_over_v2_14_speedup_claim_authorized"
                ],
                "all_historical_benchmark_apps_faster_claim_authorized": boundary[
                    "all_historical_benchmark_apps_faster_claim_authorized"
                ],
                "whole_app_speedup_claim_authorized": boundary["whole_app_speedup_claim_authorized"],
                "true_zero_copy_authorized": boundary["true_zero_copy_authorized"],
                "tier3_callback_claim_authorized": boundary["tier3_callback_claim_authorized"],
                "raw_optix_callback_claim_authorized": boundary["raw_optix_callback_claim_authorized"],
                "cupy_performance_claim_authorized": boundary["cupy_performance_claim_authorized"],
                "embedding_c_abi_claim_authorized": boundary["embedding_c_abi_claim_authorized"],
                "non_python_host_binding_claim_authorized": boundary["non_python_host_binding_claim_authorized"],
                "app_specific_native_kernel_authorized": boundary["app_specific_native_kernel_authorized"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
