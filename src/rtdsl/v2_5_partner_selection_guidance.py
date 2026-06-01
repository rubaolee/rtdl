from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER
from .v2_5_execution_path_policy import V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION


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
            "guidance_status": "measured_negative_preview_guidance",
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


@dataclass(frozen=True)
class V25PartnerConditionalGuidanceRow:
    operation: str
    workload_shape: str
    measured_partner: str
    comparison_partner: str
    evidence_goal: str
    artifact_path: str
    measured_partner_over_comparison_min_ratio: float
    measured_partner_over_comparison_max_ratio: float
    measured_partner_faster_shape_count: int
    measured_partner_slower_shape_count: int
    measured_crossover_summary: str
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
            raise ValueError("conditional guidance row operation is not a v2.5 continuation operation")
        if self.measured_partner != V2_5_PRIMARY_PARTNER:
            raise ValueError("current v2.5 conditional rows measure the Triton preview partner")
        if self.measured_partner_over_comparison_min_ratio <= 0.0:
            raise ValueError("minimum timing ratio must be positive")
        if self.measured_partner_over_comparison_max_ratio < self.measured_partner_over_comparison_min_ratio:
            raise ValueError("maximum timing ratio must be >= minimum timing ratio")
        if self.measured_partner_faster_shape_count <= 0:
            raise ValueError("conditional guidance must record at least one faster measured shape")
        if self.measured_partner_slower_shape_count <= 0:
            raise ValueError("conditional guidance must record at least one slower measured shape")
        if self.auto_select_measured_partner_allowed:
            raise ValueError("conditional preview guidance must not auto-select the measured partner")
        if self.promoted_performance_path:
            raise ValueError("conditional preview guidance must not promote a performance path")
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
            "guidance_status": "measured_mixed_preview_guidance",
            "operation": self.operation,
            "workload_shape": self.workload_shape,
            "measured_partner": self.measured_partner,
            "comparison_partner": self.comparison_partner,
            "evidence_goal": self.evidence_goal,
            "artifact_path": self.artifact_path,
            "measurement_ratio_kind": "measured_partner_wall_time_over_comparison_partner_wall_time",
            "ratio_less_than_one_means_measured_partner_faster": True,
            "measured_partner_over_comparison_min_ratio": self.measured_partner_over_comparison_min_ratio,
            "measured_partner_over_comparison_max_ratio": self.measured_partner_over_comparison_max_ratio,
            "measured_partner_faster_shape_count": self.measured_partner_faster_shape_count,
            "measured_partner_slower_shape_count": self.measured_partner_slower_shape_count,
            "measured_crossover_summary": self.measured_crossover_summary,
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


V2_5_PARTNER_SELECTION_GUIDANCE_ROWS: tuple[
    V25PartnerSelectionGuidanceRow | V25PartnerConditionalGuidanceRow, ...
] = (
    V25PartnerSelectionGuidanceRow(
        operation="segmented_count_i64",
        workload_shape="raydb_scalar_grouped_reduction_frontdoor",
        measured_partner="triton",
        comparison_partner="torch_cuda_same_contract_reduction",
        evidence_goal="Goal2796",
        artifact_path="docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json",
        measured_partner_slower_min_ratio=22.78,
        measured_partner_slower_max_ratio=38.04,
        recommendation=(
            "Do not auto-select Triton for RayDB-style scalar grouped count. "
            "Goal2796 shows the Triton public front door is correct, but "
            "Torch CUDA is 22.78x-38.04x faster on the measured RTX A5000 "
            "row-count sweep. Keep primitive-first RTDL or another explicitly "
            "selected same-contract partner until the scalar reduction preview "
            "wins timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="segmented_sum_f64",
        workload_shape="raydb_scalar_grouped_reduction_frontdoor",
        measured_partner="triton",
        comparison_partner="torch_cuda_same_contract_reduction",
        evidence_goal="Goal2796",
        artifact_path="docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json",
        measured_partner_slower_min_ratio=38.29,
        measured_partner_slower_max_ratio=84.10,
        recommendation=(
            "Do not auto-select Triton for RayDB-style scalar grouped sum. "
            "Goal2796 shows the Triton public front door is correct, but "
            "Torch CUDA is 38.29x-84.10x faster on the measured RTX A5000 "
            "row-count sweep. Keep primitive-first RTDL or another explicitly "
            "selected same-contract partner until the scalar reduction preview "
            "wins timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="segmented_min_f64",
        workload_shape="raydb_scalar_grouped_reduction_frontdoor",
        measured_partner="triton",
        comparison_partner="torch_cuda_same_contract_reduction",
        evidence_goal="Goal2796",
        artifact_path="docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json",
        measured_partner_slower_min_ratio=44.84,
        measured_partner_slower_max_ratio=192.49,
        recommendation=(
            "Do not auto-select Triton for RayDB-style scalar grouped min. "
            "Goal2796 shows the Triton public front door is correct, but "
            "Torch CUDA is 44.84x-192.49x faster on the measured RTX A5000 "
            "row-count sweep. Keep primitive-first RTDL or another explicitly "
            "selected same-contract partner until the scalar reduction preview "
            "wins timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="segmented_max_f64",
        workload_shape="raydb_scalar_grouped_reduction_frontdoor",
        measured_partner="triton",
        comparison_partner="torch_cuda_same_contract_reduction",
        evidence_goal="Goal2796",
        artifact_path="docs/reports/goal2796_pod_artifacts/raydb_triton_frontdoor_current.json",
        measured_partner_slower_min_ratio=36.00,
        measured_partner_slower_max_ratio=142.23,
        recommendation=(
            "Do not auto-select Triton for RayDB-style scalar grouped max. "
            "Goal2796 shows the Triton public front door is correct, but "
            "Torch CUDA is 36.00x-142.23x faster on the measured RTX A5000 "
            "row-count sweep. Keep primitive-first RTDL or another explicitly "
            "selected same-contract partner until the scalar reduction preview "
            "wins timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="grouped_topk_f64",
        workload_shape="dense_exact_topk_candidate_ranking",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2784",
        artifact_path=(
            "docs/reports/goal2784_pod_artifacts/"
            "goal2784_dense_point_topk_triton_adapter_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_slower_min_ratio=4.91,
        measured_partner_slower_max_ratio=10.04,
        recommendation=(
            "Do not auto-select Triton for dense exact top-k ranking. Goal2784 removed "
            "dense score materialization and improved the preview substantially, but "
            "Torch is still 4.91x-10.04x faster on the measured RTX A5000 shapes. Keep "
            "Torch/CuPy or another explicitly selected partner as the performance path "
            "until a stronger tiled/block-level top-k kernel wins same-contract timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="grouped_vector_sum_f64x2",
        workload_shape="dense_grouped_vector_sum_2d",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2786",
        artifact_path=(
            "docs/reports/goal2786_pod_artifacts/"
            "goal2786_batched_vector_sum_offsets_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_slower_min_ratio=3.76,
        measured_partner_slower_max_ratio=16.86,
        recommendation=(
            "Do not auto-select Triton for dense grouped vector sums. Goal2786 tested "
            "batched presegmented row-offset programs, but the single-group offset path "
            "was still best and Torch scatter-add remained 3.76x-16.86x faster on the "
            "measured RTX A5000 shapes. Keep Torch or another explicitly selected "
            "same-contract partner as the performance path until a stronger segmented "
            "or block-reduction Triton design wins timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="grouped_argmin_f64",
        workload_shape="dense_exact_hausdorff_argmin_argmax",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2787",
        artifact_path=(
            "docs/reports/goal2787_pod_artifacts/"
            "goal2787_hausdorff_generic_argmin_argmax_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_slower_min_ratio=31.88,
        measured_partner_slower_max_ratio=45.15,
        recommendation=(
            "Do not auto-select Triton for dense exact Hausdorff-style "
            "argmin-then-argmax witness reduction. Goal2787 wires the app wrapper "
            "through generic grouped_argmin_f64 plus grouped_argmax_f64, but the "
            "two-kernel generic route is 31.88x-45.15x slower than the dense Torch "
            "same-contract branch on measured RTX A5000 shapes. Keep optimized "
            "Torch/CuPy/CUDA or another explicitly selected same-contract partner "
            "as the performance path until a fused/tiled generic witness-reduction "
            "design wins timing."
        ),
    ),
    V25PartnerSelectionGuidanceRow(
        operation="grouped_argmin_f64",
        workload_shape="dense_exact_hausdorff_nearest_then_global_max",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2788",
        artifact_path=(
            "docs/reports/goal2788_pod_artifacts/"
            "goal2788_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_slower_min_ratio=3.77,
        measured_partner_slower_max_ratio=30.73,
        recommendation=(
            "Do not auto-select Triton for dense exact Hausdorff-style "
            "nearest-then-global-max witness reduction yet. Goal2788's fused "
            "dense_point_nearest_2d route removes dense score-row materialization "
            "and is faster than the Goal2787 generic score-row route, but it is "
            "still 3.77x-30.73x slower than the dense Torch same-contract branch "
            "on measured RTX A5000 shapes. Keep optimized Torch/CuPy/CUDA or "
            "another explicitly selected same-contract partner as the performance "
            "path until a stronger tiled/fused generic witness-reduction design "
            "wins timing."
        ),
    ),
    V25PartnerConditionalGuidanceRow(
        operation="grouped_argmin_f64",
        workload_shape="dense_exact_hausdorff_tiled_nearest_then_global_max",
        measured_partner="triton",
        comparison_partner="torch_same_contract_branch",
        evidence_goal="Goal2790",
        artifact_path=(
            "docs/reports/goal2790_pod_artifacts/"
            "goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json"
        ),
        measured_partner_over_comparison_min_ratio=0.745,
        measured_partner_over_comparison_max_ratio=19.61,
        measured_partner_faster_shape_count=1,
        measured_partner_slower_shape_count=3,
        measured_crossover_summary=(
            "Goal2790 measured the tiled Triton route slower than Torch at "
            "2048x2048, 4096x4096, and 8192x8192, but faster at 16384x16384 "
            "(16K x 16K) on the RTX A5000 pod."
        ),
        recommendation=(
            "Treat tiled dense point-nearest Hausdorff-style reduction as "
            "thresholded preview evidence, not a default. It may be explicitly "
            "selected for large dense shapes after same-contract measurement, "
            "but planners must not auto-select it or publish a blanket Triton "
            "speedup claim from the mixed Goal2790 evidence."
        ),
    ),
)


def v2_5_partner_selection_guidance() -> dict[str, Any]:
    rows = tuple(row.to_metadata() for row in V2_5_PARTNER_SELECTION_GUIDANCE_ROWS)
    return {
        "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        "primitive_first_selection_doctrine_version": V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION,
        "rows": rows,
        "row_count": len(rows),
        "planner_policy": "advisory_only_explicit_app_partner_choice",
        "fast_path_rule": "primitive_first_native_rtdl_when_fused_generic_primitive_exactly_expresses_continuation",
        "partner_use_rule": "partner_continuation_only_for_unfused_continuations_or_explicit_app_choice",
        "partner_choice_rule": "same_contract_evidence_never_default_triton",
        "preview_kernel_available_does_not_imply_auto_select": True,
        "no_partner_forced": True,
        "automatic_triton_selection_allowed": False,
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
    status = str(matches[0].get("guidance_status", "measured_negative_preview_guidance"))
    if len(matches) > 1:
        statuses = {str(match.get("guidance_status", "")) for match in matches}
        status = next(iter(statuses)) if len(statuses) == 1 else "measured_preview_guidance_multiple"
    return {
        "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        "operation": normalized_operation,
        "workload_shape": normalized_shape,
        "status": status,
        "matches": matches,
        "auto_select_partner_allowed": False,
        "recommendation": matches[0]["recommendation"] if len(matches) == 1 else "Review all matching guidance rows.",
        "claim_boundary": V2_5_PARTNER_SELECTION_GUIDANCE_CLAIM_BOUNDARY,
    }


def explain_v2_5_partner_selection(
    operation: str,
    workload_shape: str,
    *,
    source_count: int | None = None,
    target_count: int | None = None,
    row_count: int | None = None,
    dtype: str = "float64",
    available_device_bytes: int | None = None,
    candidate_block_size: int = 4096,
) -> dict[str, Any]:
    """Return an explain-only partner-selection plan.

    This helper deliberately does not execute and does not select a partner for
    the caller. It turns measured guidance into explicit, claim-safe planner
    metadata that examples or benchmark harnesses can show to users before the
    user/app chooses a partner.
    """

    guidance = plan_v2_5_partner_selection(operation, workload_shape)
    normalized_dtype = str(dtype).strip().lower()
    normalized_source_count = None if source_count is None else int(source_count)
    normalized_target_count = None if target_count is None else int(target_count)
    normalized_row_count = None if row_count is None else int(row_count)
    normalized_candidate_block_size = int(candidate_block_size)
    if normalized_candidate_block_size <= 0:
        raise ValueError("candidate_block_size must be positive")
    for name, value in (
        ("source_count", normalized_source_count),
        ("target_count", normalized_target_count),
        ("row_count", normalized_row_count),
        ("available_device_bytes", available_device_bytes),
    ):
        if value is not None and int(value) < 0:
            raise ValueError(f"{name} must be non-negative when provided")

    estimated_dense_score_bytes = None
    estimated_tiled_witness_bytes = None
    if normalized_source_count is not None and normalized_target_count is not None:
        estimated_dense_score_bytes = normalized_source_count * normalized_target_count * 8
        tile_count = (normalized_target_count + normalized_candidate_block_size - 1) // normalized_candidate_block_size
        # tile_query_indices, tile_neighbor_ids, and tile_scores are i64/i64/f64.
        estimated_tiled_witness_bytes = normalized_source_count * tile_count * 24

    reasons: list[str] = []
    suggested_explicit_partner_candidate = None
    suggested_explicit_strategy_candidate = None
    planner_status = "no_measured_guidance_explicit_choice_required"
    threshold_shape_met = False
    memory_note = "not_evaluated"

    if guidance["status"] == "measured_negative_preview_guidance":
        match = guidance["matches"][0]
        suggested_explicit_partner_candidate = match["comparison_partner"]
        planner_status = "comparison_partner_candidate_due_to_negative_preview"
        reasons.append("Measured Triton preview evidence is negative for this workload shape.")
    elif guidance["status"] == "measured_mixed_preview_guidance":
        match = guidance["matches"][0]
        if normalized_source_count is None or normalized_target_count is None:
            planner_status = "shape_required_for_thresholded_guidance"
            reasons.append("Thresholded guidance needs source_count and target_count.")
        else:
            threshold_shape_met = normalized_source_count >= 16384 and normalized_target_count >= 16384
            if threshold_shape_met and normalized_dtype in {"float64", "f64", "double"}:
                suggested_explicit_partner_candidate = match["measured_partner"]
                suggested_explicit_strategy_candidate = "dense_point_nearest_tiled"
                planner_status = "thresholded_triton_candidate_explicit_choice_required"
                reasons.append("Measured Goal2790 crossover threshold is met for the float64 dense shape.")
            else:
                suggested_explicit_partner_candidate = match["comparison_partner"]
                planner_status = "comparison_partner_candidate_below_threshold_or_unmeasured_dtype"
                reasons.append("Measured Goal2790 crossover threshold is not met or dtype is unmeasured.")
    else:
        reasons.append("No measured guidance row exists for this operation/workload shape.")

    if available_device_bytes is not None and estimated_dense_score_bytes is not None:
        if estimated_dense_score_bytes > int(available_device_bytes):
            memory_note = "dense_score_matrix_exceeds_available_device_bytes"
        else:
            memory_note = "dense_score_matrix_fits_reported_available_device_bytes"

    return {
        "guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        "operation": str(operation).strip(),
        "workload_shape": str(workload_shape).strip(),
        "input_shape": {
            "source_count": normalized_source_count,
            "target_count": normalized_target_count,
            "row_count": normalized_row_count,
            "dtype": normalized_dtype,
            "candidate_block_size": normalized_candidate_block_size,
        },
        "guidance_status": guidance["status"],
        "planner_status": planner_status,
        "guidance": guidance,
        "threshold_shape_met": threshold_shape_met,
        "suggested_explicit_partner_candidate": suggested_explicit_partner_candidate,
        "suggested_explicit_strategy_candidate": suggested_explicit_strategy_candidate,
        "execution_strategy_selected": False,
        "auto_select_partner_allowed": False,
        "requires_explicit_caller_choice": True,
        "estimated_dense_score_bytes": estimated_dense_score_bytes,
        "estimated_tiled_witness_bytes": estimated_tiled_witness_bytes,
        "available_device_bytes": available_device_bytes,
        "memory_note": memory_note,
        "reasons": tuple(reasons),
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "release_readiness_authorized": False,
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
    if guidance.get("primitive_first_selection_doctrine_version") != V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION:
        errors.append("partner guidance must index the primitive-first doctrine")
    if "primitive_first" not in str(guidance.get("fast_path_rule", "")):
        errors.append("partner guidance must name primitive-first as the fast path")
    if "unfused" not in str(guidance.get("partner_use_rule", "")):
        errors.append("partner guidance must reserve partners for unfused continuation work")
    if "same_contract" not in str(guidance.get("partner_choice_rule", "")):
        errors.append("partner guidance must require same-contract evidence")
    rows = tuple(guidance.get("rows", ()))
    if int(guidance.get("row_count", -1)) != len(rows):
        errors.append("row_count does not match rows")
    if guidance.get("preview_kernel_available_does_not_imply_auto_select") is not True:
        errors.append("guidance must distinguish preview availability from partner selection")
    if guidance.get("automatic_triton_selection_allowed") is not False:
        errors.append("guidance must block automatic Triton selection")
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
        guidance_status = str(row.get("guidance_status", ""))
        if guidance_status not in {"measured_negative_preview_guidance", "measured_mixed_preview_guidance"}:
            errors.append(f"{operation} has unknown guidance status: {guidance_status}")
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
