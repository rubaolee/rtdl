from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER


V2_5_PARTNER_SELECTION_GUIDANCE_VERSION = "rtdl.v2_5.partner_selection_guidance.v1"
V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY = (
    "v2.5 partner-selection guidance records measured preview evidence and "
    "planner cautions only. It does not force a partner, promote a performance "
    "path, authorize public speedup wording, authorize RT-core speedup wording, "
    "authorize whole-app speedup wording, authorize true zero-copy wording, or "
    "authorize release readiness."
)


@dataclass(frozen=True)
class V25PartnerSelectionGuidanceRow:
    operation: str
    workload_shape: str
    measured_partner: str
    comparison_partner: str
    evidence_goal: str
    artifact_path: str
    measured_partner_slower_min_ratio: float
    measured_partner_slower_max_ratio: float
    recommendation: str
    auto_select_measured_partner_allowed: bool = False
    promoted_performance_path: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    release_readiness_authorized: bool = False

    def __post_init__(self) -> None:
        if self.operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            raise ValueError("guidance row operation is not a v2.5 continuation operation")
        if self.measured_partner != V2_5_PRIMARY_PARTNER:
            raise ValueError("current v2.5 guidance rows measure the Triton preview partner")
        if self.measured_partner_slower_min_ratio <= 0.0:
            raise ValueError("minimum slower ratio must be positive")
        if self.measured_partner_slower_max_ratio < self.measured_partner_slower_min_ratio:
            raise ValueError("maximum slower ratio must be >= minimum slower ratio")
        if self.auto_select_measured_partner_allowed:
            raise ValueError("negative guidance must not auto-select the measured partner")
        if self.promoted_performance_path:
            raise ValueError("negative guidance must not promote a performance path")
        if self.public_speedup_claim_authorized:
            raise ValueError("partner guidance must not authorize public speedup claims")
        if self.rt_core_speedup_claim_authorized:
            raise ValueError("partner guidance must not authorize RT-core speedup claims")
        if self.whole_app_speedup_claim_authorized:
            raise ValueError("partner guidance must not authorize whole-app speedup claims")
        if self.true_zero_copy_claim_authorized:
            raise ValueError("partner guidance must not authorize true zero-copy claims")
        if self.release_readiness_authorized:
            raise ValueError("partner guidance must not authorize release readiness")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
            "operation": self.operation,
            "workload_shape": self.workload_shape,
            "measured_partner": self.measured_partner,
            "comparison_partner": self.comparison_partner,
            "evidence_goal": self.evidence_goal,
            "artifact_path": self.artifact_path,
            "measured_partner_slower_min_ratio": self.measured_partner_slower_min_ratio,
            "measured_partner_slower_max_ratio": self.measured_partner_slower_max_ratio,
            "recommendation": self.recommendation,
            "auto_select_measured_partner_allowed": self.auto_select_measured_partner_allowed,
            "promoted_performance_path": self.promoted_performance_path,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "release_readiness_authorized": self.release_readiness_authorized,
            "claim_boundary": V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY,
        }


V2_5_PARTNER_SELECTION_GUIDANCE_ROWS = (
    V25PartnerSelectionGuidanceRow(
        operation="grouped_topk_f64",
        workload_shape="dense_exact_topk_candidate_ranking",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2780",
        artifact_path=(
            "docs/reports/goal2780_pod_artifacts/"
            "goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_slower_min_ratio=47.28,
        measured_partner_slower_max_ratio=150.90,
        recommendation=(
            "Do not auto-select Triton for dense exact top-k ranking. Keep Torch/CuPy "
            "or another explicitly selected partner as the performance path until a "
            "tiled/block-level top-k kernel replaces the iterative preview."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="grouped_vector_sum_f64x2",
        workload_shape="dense_grouped_vector_sum_2d",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2781",
        artifact_path=(
            "docs/reports/goal2781_pod_artifacts/"
            "goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_slower_min_ratio=4.09,
        measured_partner_slower_max_ratio=16.59,
        recommendation=(
            "Do not auto-select Triton for dense grouped vector sums. Keep Torch "
            "scatter-add as the measured better same-contract branch until a segmented "
            "or block-reduction Triton design replaces the atomic-add preview."
        ),
    ),
)


def v2_5_partner_selection_guidance() -> dict[str, Any]:
    rows = tuple(row.to_metadata() for row in V2_5_PARTNER_SELECTION_GUIDANCE_ROWS)
    return {
        "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        "rows": rows,
        "row_count": len(rows),
        "planner_policy": "advisory_only_explicit_app_partner_choice",
        "preview_kernel_available_does_not_imply_auto_select": True,
        "no_partner_forced": True,
        "promoted_performance_path": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "release_readiness_authorized": False,
        "claim_boundary": V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY,
    }


def plan_v2_5_partner_selection(operation: str, workload_shape: str | None = None) -> dict[str, Any]:
    normalized_operation = str(operation).strip()
    normalized_shape = None if workload_shape is None else str(workload_shape).strip()
    matches = tuple(
        row.to_metadata()
        for row in V2_5_PARTNER_SELECTION_GUIDANCE_ROWS
        if row.operation == normalized_operation
        and (normalized_shape is None or row.workload_shape == normalized_shape)
    )
    if not matches:
        return {
            "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
            "operation": normalized_operation,
            "workload_shape": normalized_shape,
            "status": "no_measured_guidance",
            "auto_select_partner_allowed": False,
            "recommendation": "Require explicit app/user partner choice and same-contract evidence.",
            "claim_boundary": V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY,
        }
    return {
        "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        "operation": normalized_operation,
        "workload_shape": normalized_shape,
        "status": "measured_negative_preview_guidance",
        "matches": matches,
        "auto_select_partner_allowed": False,
        "recommendation": matches[0]["recommendation"] if len(matches) == 1 else "Review all matching guidance rows.",
        "claim_boundary": V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY,
    }


def validate_v2_5_partner_selection_guidance(
    guidance: dict[str, Any] | None = None,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    guidance = v2_5_partner_selection_guidance() if guidance is None else guidance
    root = Path.cwd() if repo_root is None else Path(repo_root)
    errors: list[str] = []
    if guidance.get("guidance_version") != V2_5_PARTNER_SELECTION_GUIDANCE_VERSION:
        errors.append("unexpected partner-selection guidance version")
    rows = tuple(guidance.get("rows", ()))
    if int(guidance.get("row_count", -1)) != len(rows):
        errors.append("row_count does not match rows")
    if guidance.get("preview_kernel_available_does_not_imply_auto_select") is not True:
        errors.append("guidance must distinguish preview availability from partner selection")
    for field in (
        "promoted_performance_path",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "release_readiness_authorized",
    ):
        if guidance.get(field) is not False:
            errors.append(f"{field} must remain false")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("guidance rows must be metadata dictionaries")
            continue
        operation = str(row.get("operation", ""))
        if operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            errors.append(f"unknown operation in guidance row: {operation}")
        if row.get("measured_partner") != V2_5_PRIMARY_PARTNER:
            errors.append(f"{operation} must record Triton as the measured preview partner")
        if row.get("auto_select_measured_partner_allowed") is not False:
            errors.append(f"{operation} must not auto-select the slower measured partner")
        if row.get("promoted_performance_path") is not False:
            errors.append(f"{operation} must not promote a performance path")
        artifact = root / str(row.get("artifact_path", ""))
        if not artifact.exists():
            errors.append(f"{operation} evidence artifact is missing: {artifact}")
    return {
        "status": "accept" if not errors else "reject",
        "guidance_version": guidance.get("guidance_version"),
        "row_count": guidance.get("row_count"),
        "errors": tuple(errors),
    }
