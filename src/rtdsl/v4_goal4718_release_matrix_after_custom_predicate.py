from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v4_custom_predicate_early_exit import (
    V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
    ray_triangle_custom_predicate_early_exit_claim_boundary_v4,
)
from .v4_operator_catalog import measured_v4_tier2_operator_catalog


V4_GOAL4718_RELEASE_MATRIX_STATUS = (
    "goal4718_v4_release_matrix_after_custom_predicate_early_exit"
)
V4_GOAL4718_DECISION_LABEL = (
    "v4_python_edsl_operator_pushdown_release_candidate_pending_docs_and_final_review"
)
V4_GOAL4718_NEXT_GOAL = "Goal4719 public docs, tutorials, examples, and release wording cleanup"


@dataclass(frozen=True)
class V4Goal4718LegacyAppState:
    decision_label: str
    formal_high_performance_v4_supported: bool
    true_v4_candidate_app_count: int
    contributing_app_count: int
    blocking_reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "decision_label": self.decision_label,
            "formal_high_performance_v4_supported": self.formal_high_performance_v4_supported,
            "true_v4_candidate_app_count": self.true_v4_candidate_app_count,
            "contributing_app_count": self.contributing_app_count,
            "blocking_reasons": self.blocking_reasons,
        }


@dataclass(frozen=True)
class V4Goal4718WorkflowRow:
    workflow: str
    api_surface: str
    claim_class: str
    v4_vs_v2_14_primary_geomean: float
    v4_vs_v3_0_2_primary_geomean: float
    min_primary_v4_vs_v3_0_2: float
    correctness_all_passed: bool
    denominator: str
    counts_as_v4_edsl_value: bool
    counts_as_legacy_all_app_speedup: bool
    evidence: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "workflow": self.workflow,
            "api_surface": self.api_surface,
            "claim_class": self.claim_class,
            "v4_vs_v2_14_primary_geomean": self.v4_vs_v2_14_primary_geomean,
            "v4_vs_v3_0_2_primary_geomean": self.v4_vs_v3_0_2_primary_geomean,
            "min_primary_v4_vs_v3_0_2": self.min_primary_v4_vs_v3_0_2,
            "correctness_all_passed": self.correctness_all_passed,
            "denominator": self.denominator,
            "counts_as_v4_edsl_value": self.counts_as_v4_edsl_value,
            "counts_as_legacy_all_app_speedup": self.counts_as_legacy_all_app_speedup,
            "evidence": self.evidence,
        }


def _legacy_app_state() -> V4Goal4718LegacyAppState:
    return V4Goal4718LegacyAppState(
        decision_label="bounded_operator_v4_only__app_level_high_performance_not_supported",
        formal_high_performance_v4_supported=False,
        true_v4_candidate_app_count=1,
        contributing_app_count=0,
        blocking_reasons=(
            "old_version_optix_uses_v4_compatibility_native_library",
            "most_full_app_rows_do_not_pass_frozen_speed_bar",
            "insufficient_independent_true_v4_app_wins",
        ),
    )


def _custom_predicate_workflow_row() -> V4Goal4718WorkflowRow:
    boundary = ray_triangle_custom_predicate_early_exit_claim_boundary_v4()
    return V4Goal4718WorkflowRow(
        workflow="ray_triangle_custom_predicate_early_exit_multi_hit",
        api_surface=V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
        claim_class="true_v4_operator_pushdown_workflow_win_candidate",
        v4_vs_v2_14_primary_geomean=float(
            boundary["goal4717_serious_scale_primary_v2_speedup_geomean"]
        ),
        v4_vs_v3_0_2_primary_geomean=float(
            boundary["goal4717_serious_scale_primary_v3_speedup_geomean"]
        ),
        min_primary_v4_vs_v3_0_2=float(boundary["goal4717_serious_scale_min_primary_v3_speedup"]),
        correctness_all_passed=bool(boundary["goal4717_serious_scale_correctness_all_passed"]),
        denominator=str(boundary["v2_v3_denominator"]),
        counts_as_v4_edsl_value=True,
        counts_as_legacy_all_app_speedup=False,
        evidence=tuple(str(item) for item in boundary["source_evidence"]),
    )


def v4_goal4718_release_matrix_after_custom_predicate() -> dict[str, object]:
    """Return the V4 release matrix after Goal4717.

    This matrix separates two facts that must not be mixed:

    * legacy promoted-app all-suite high-performance is still not supported;
    * the new constrained custom predicate early-exit workflow is a real V4
      eDSL/operator-pushdown performance win.
    """

    catalog = measured_v4_tier2_operator_catalog()
    measured_surfaces = tuple(str(row["api_surface"]) for row in catalog)
    workflow = _custom_predicate_workflow_row()
    legacy = _legacy_app_state()
    return {
        "schema": "rtdl.v4.goal4718.release_matrix_after_custom_predicate.v1",
        "status": V4_GOAL4718_RELEASE_MATRIX_STATUS,
        "decision_label": V4_GOAL4718_DECISION_LABEL,
        "next_goal": V4_GOAL4718_NEXT_GOAL,
        "measured_surface_count": len(measured_surfaces),
        "measured_surfaces": measured_surfaces,
        "legacy_promoted_app_state": legacy.as_dict(),
        "new_v4_workflow_rows": (workflow.as_dict(),),
        "v4_python_edsl_release_candidate_supported": True,
        "v4_operator_pushdown_workflow_high_performance_supported": True,
        "legacy_all_app_high_performance_supported": False,
        "broad_all_benchmark_speedup_supported": False,
        "release_authorized": False,
        "formal_tag_authorized": False,
        "public_wording_authorized_before_goal4719": False,
        "allowed_claim_if_goal4719_and_final_review_pass": (
            "RTDL V4 is a Python eDSL/runtime for measured generic RT-core operator pushdown.",
            "The V4 front door has 10 measured generic operator/workflow surfaces.",
            "The constrained Numba custom predicate early-exit workflow measured "
            "4.633x geomean versus V2.14/V3.0.2 materialized-device fallback at serious scale.",
            "Legacy promoted-app all-suite high-performance remains unsupported by Goal4669.",
        ),
        "forbidden_claims": (
            "broad all-app speedup",
            "all benchmark apps are faster",
            "arbitrary Python callback support",
            "raw OptiX callback support",
            "public Tier-3 support",
            "non-Python embedding/C ABI",
            "app-specific native kernels",
        ),
    }


def validate_v4_goal4718_release_matrix_after_custom_predicate(
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    if payload is None:
        payload = v4_goal4718_release_matrix_after_custom_predicate()
    missing: list[str] = []
    catalog = measured_v4_tier2_operator_catalog()
    catalog_surfaces = tuple(str(row["api_surface"]) for row in catalog)
    if payload.get("status") != V4_GOAL4718_RELEASE_MATRIX_STATUS:
        missing.append("status")
    if payload.get("decision_label") != V4_GOAL4718_DECISION_LABEL:
        missing.append("decision_label")
    if payload.get("measured_surface_count") != len(catalog_surfaces):
        missing.append("measured_surface_count")
    if V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE not in catalog_surfaces:
        missing.append("custom_predicate_surface_not_in_catalog")
    rows = tuple(payload.get("new_v4_workflow_rows", ()))
    if len(rows) != 1:
        missing.append("workflow_row_count")
    else:
        row = dict(rows[0])
        if row.get("api_surface") != V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE:
            missing.append("workflow_api_surface")
        if float(row.get("v4_vs_v3_0_2_primary_geomean", 0.0)) < 1.50:
            missing.append("workflow_geomean_bar")
        if float(row.get("min_primary_v4_vs_v3_0_2", 0.0)) < 1.20:
            missing.append("workflow_min_row_bar")
        if row.get("correctness_all_passed") is not True:
            missing.append("workflow_correctness")
        if row.get("counts_as_legacy_all_app_speedup") is not False:
            missing.append("workflow_legacy_all_app_lock")
    legacy = dict(payload.get("legacy_promoted_app_state", {}))
    if legacy.get("formal_high_performance_v4_supported") is not False:
        missing.append("legacy_app_high_performance_lock")
    if payload.get("legacy_all_app_high_performance_supported") is not False:
        missing.append("legacy_all_app_high_performance_supported")
    if payload.get("broad_all_benchmark_speedup_supported") is not False:
        missing.append("broad_all_benchmark_speedup_supported")
    for flag in ("release_authorized", "formal_tag_authorized", "public_wording_authorized_before_goal4719"):
        if payload.get(flag) is not False:
            missing.append(flag)
    if payload.get("v4_python_edsl_release_candidate_supported") is not True:
        missing.append("v4_python_edsl_release_candidate_supported")
    if payload.get("v4_operator_pushdown_workflow_high_performance_supported") is not True:
        missing.append("v4_operator_pushdown_workflow_high_performance_supported")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "matrix": payload,
    }


__all__ = [
    "V4_GOAL4718_RELEASE_MATRIX_STATUS",
    "V4_GOAL4718_DECISION_LABEL",
    "V4_GOAL4718_NEXT_GOAL",
    "V4Goal4718LegacyAppState",
    "V4Goal4718WorkflowRow",
    "v4_goal4718_release_matrix_after_custom_predicate",
    "validate_v4_goal4718_release_matrix_after_custom_predicate",
]
