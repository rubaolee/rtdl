from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_GOAL4636C_STATUS = "goal4636c_aabb_index_target_predeclared_pending_pod_gate_not_measured"
V4_GOAL4636C_OPERATOR = "aabb_index_query_2d_all_ops_count"
V4_GOAL4636C_API_SURFACE = "v4_aabb_index_query_2d_all_ops_count_prepared_runner"
V4_GOAL4636C_GENERIC_PRIMITIVE = "AABB_INDEX_QUERY_2D"
V4_GOAL4636C_TARGET_APP_ROW = "librts_spatial_index"
V4_GOAL4636C_SCOPE = ("rtdl_native_prepared_runner",)
V4_GOAL4636C_OUTPUT_CONTRACT = "generic_prepared_aabb_index_query_2d_family"
V4_GOAL4636C_ACCEPTED_CONTRACT_FAMILY = "generic_prepared_aabb_index_query_2d"
V4_GOAL4636C_ACCEPTED_CONTRACTS = (
    "generic_prepared_aabb_index_query_2d",
    "generic_prepared_aabb_index_query_2d_count",
    "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
)
V4_GOAL4636C_RUNNER = "scripts/v3_0_m30_librts_prepared_all_ops_refresh.py"


@dataclass(frozen=True)
class V4Goal4636AabbIndexTarget:
    operator: str
    api_surface: str
    generic_primitive: str
    target_coverage_row: str
    continuation_class: str
    scope: tuple[str, ...]
    output_contract: str
    runner: str
    status: str = V4_GOAL4636C_STATUS
    pod_gate_required: bool = True
    measured_catalog_promotion_authorized: bool = False
    release_claim_authorized: bool = False
    broad_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    cupy_performance_claim_authorized: bool = False
    c_abi_or_embedding_claim_authorized: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "operator": self.operator,
            "api_surface": self.api_surface,
            "generic_primitive": self.generic_primitive,
            "target_coverage_row": self.target_coverage_row,
            "continuation_class": self.continuation_class,
            "scope": self.scope,
            "output_contract": self.output_contract,
            "accepted_contract_family": V4_GOAL4636C_ACCEPTED_CONTRACT_FAMILY,
            "accepted_contracts": V4_GOAL4636C_ACCEPTED_CONTRACTS,
            "runner": self.runner,
            "pod_gate_required": self.pod_gate_required,
            "measured_catalog_promotion_authorized": self.measured_catalog_promotion_authorized,
            "release_claim_authorized": self.release_claim_authorized,
            "broad_speedup_claim_authorized": self.broad_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "c_abi_or_embedding_claim_authorized": self.c_abi_or_embedding_claim_authorized,
            "promotion_gate": {
                "dataset": "uniform",
                "box_count": 1_000_000,
                "query_count": 1_000,
                "operation": "all",
                "max_box_width": 0.005,
                "max_box_height": 0.005,
                "max_query_width": 0.005,
                "max_query_height": 0.005,
                "warmup": 1,
                "repeat_overrides": {"embree": 240, "optix": 240},
                "requires_rt_hardware": True,
                "requires_cross_backend_count_match": True,
                "requires_same_contract": True,
                "requires_same_contract_family": True,
                "requires_primitive_first_no_partner": True,
                "cpu_reference_skipped_acknowledged": True,
                "correctness_oracle": "cross_backend_count_match_same_fixture",
                "requires_no_public_speedup_claim": True,
                "embree_over_optix_query_median_floor": 10.0,
                "embree_over_optix_query_total_floor": 10.0,
                "promotion_scope": "operator_coverage_only_not_librts_paper_or_authors_code",
                "catalog_surface_addition_requires_frontdoor_goal": True,
            },
            "coverage_effect_if_gate_passes": {
                "row": self.target_coverage_row,
                "from": "deferred_or_uncovered_v4_0",
                "to": "strong_measured_operator_coverage",
                "reason": (
                    "LibRTS spatial-index coverage would map to an app-name-free "
                    "AABB_INDEX_QUERY_2D all-ops count surface, without adding a "
                    "LibRTS-native kernel or authors-code/paper reproduction claim."
                ),
            },
            "selection_reason": (
                "The threshold-summary and grouped-any-hit candidates both failed "
                "their promotion gates. AABB_INDEX_QUERY_2D targets a different "
                "generic relation/query class, has an existing all-ops prepared "
                "runner, and does not require CuPy."
            ),
        }


def v4_goal4636_aabb_index_target() -> dict[str, Any]:
    return V4Goal4636AabbIndexTarget(
        operator=V4_GOAL4636C_OPERATOR,
        api_surface=V4_GOAL4636C_API_SURFACE,
        generic_primitive=V4_GOAL4636C_GENERIC_PRIMITIVE,
        target_coverage_row=V4_GOAL4636C_TARGET_APP_ROW,
        continuation_class="aabb_index_all_ops_count",
        scope=V4_GOAL4636C_SCOPE,
        output_contract=V4_GOAL4636C_OUTPUT_CONTRACT,
        runner=V4_GOAL4636C_RUNNER,
    ).as_dict()


def validate_v4_goal4636_aabb_index_target() -> dict[str, Any]:
    target = v4_goal4636_aabb_index_target()
    if target["status"] != V4_GOAL4636C_STATUS:
        raise ValueError("Goal4636C AABB target status drift")
    if target["target_coverage_row"] != "librts_spatial_index":
        raise ValueError("Goal4636C AABB target must target librts_spatial_index")
    if target["generic_primitive"] != "AABB_INDEX_QUERY_2D":
        raise ValueError("Goal4636C AABB target must use AABB_INDEX_QUERY_2D")
    if target["accepted_contract_family"] != "generic_prepared_aabb_index_query_2d":
        raise ValueError("Goal4636C AABB target must declare the accepted contract family")
    if "generic_prepared_aabb_index_query_2d_count" not in target["accepted_contracts"]:
        raise ValueError("Goal4636C AABB target must accept the Embree count contract")
    if "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count" not in target["accepted_contracts"]:
        raise ValueError("Goal4636C AABB target must accept the OptiX qualified prepared contract")
    if target["scope"] != ("rtdl_native_prepared_runner",):
        raise ValueError("Goal4636C AABB target must declare native runner scope explicitly")
    if not target["pod_gate_required"]:
        raise ValueError("Goal4636C AABB target must require POD gate")
    if target["measured_catalog_promotion_authorized"]:
        raise ValueError("Goal4636C AABB target must not promote before POD evidence")
    gate = target["promotion_gate"]
    if gate["box_count"] < 1_000_000 or gate["query_count"] < 1_000:
        raise ValueError("Goal4636C AABB target must use the large all-ops fixture")
    if gate["repeat_overrides"].get("embree") != gate["repeat_overrides"].get("optix"):
        raise ValueError("Goal4636C AABB repeats must be symmetric so median and total floors mean the same thing")
    if not gate["requires_same_contract_family"]:
        raise ValueError("Goal4636C AABB target must require same accepted contract family")
    if not gate["cpu_reference_skipped_acknowledged"]:
        raise ValueError("Goal4636C AABB target must acknowledge the skipped CPU reference on the large gate")
    if gate["embree_over_optix_query_median_floor"] < 10.0:
        raise ValueError("Goal4636C AABB query median floor must be material")
    if gate["embree_over_optix_query_total_floor"] < 10.0:
        raise ValueError("Goal4636C AABB query total floor must be material")
    if gate["promotion_scope"] != "operator_coverage_only_not_librts_paper_or_authors_code":
        raise ValueError("Goal4636C AABB promotion scope must stay operator-only")
    if not gate["catalog_surface_addition_requires_frontdoor_goal"]:
        raise ValueError("Goal4636C AABB catalog addition must require a front-door goal")
    for flag in (
        "release_claim_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_specific_native_kernel_authorized",
        "true_zero_copy_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
    ):
        if target[flag]:
            raise ValueError(f"Goal4636C AABB target must not authorize {flag}")
    return target


__all__ = [
    "V4_GOAL4636C_STATUS",
    "V4_GOAL4636C_OPERATOR",
    "V4_GOAL4636C_API_SURFACE",
    "V4_GOAL4636C_GENERIC_PRIMITIVE",
    "V4_GOAL4636C_TARGET_APP_ROW",
    "V4_GOAL4636C_SCOPE",
    "V4_GOAL4636C_OUTPUT_CONTRACT",
    "V4_GOAL4636C_ACCEPTED_CONTRACT_FAMILY",
    "V4_GOAL4636C_ACCEPTED_CONTRACTS",
    "V4_GOAL4636C_RUNNER",
    "V4Goal4636AabbIndexTarget",
    "v4_goal4636_aabb_index_target",
    "validate_v4_goal4636_aabb_index_target",
]
