from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION


V2_5_DETERMINISM_POLICY_VERSION = "rtdl.v2_5.determinism_policy.v1"
V2_5_DETERMINISM_POLICY_CLAIM_BOUNDARY = (
    "v2.5 determinism policies define comparison contracts only. They do not "
    "authorize public speedup claims, whole-app claims, release readiness, or "
    "RT traversal replacement."
)


@dataclass(frozen=True)
class V25ContinuationDeterminismPolicy:
    operation: str
    determinism_class: str
    tie_break_policy: str
    tolerance_policy: str
    output_order_policy: str
    missing_group_policy: str
    overflow_policy: str
    notes: str = ""
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    release_readiness_authorized: bool = False
    rt_traversal_replacement_allowed: bool = False

    def __post_init__(self) -> None:
        if self.operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            raise ValueError("determinism policy operation is not a v2.5 continuation operation")
        for field_name in (
            "determinism_class",
            "tie_break_policy",
            "tolerance_policy",
            "output_order_policy",
            "missing_group_policy",
            "overflow_policy",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"determinism policy field must be non-empty: {field_name}")
        if self.public_speedup_claim_authorized:
            raise ValueError("determinism policy must not authorize public speedup claims")
        if self.whole_app_speedup_claim_authorized:
            raise ValueError("determinism policy must not authorize whole-app speedup claims")
        if self.release_readiness_authorized:
            raise ValueError("determinism policy must not authorize release readiness")
        if self.rt_traversal_replacement_allowed:
            raise ValueError("determinism policy must not allow RT traversal replacement")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "policy_version": V2_5_DETERMINISM_POLICY_VERSION,
            "continuation_contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
            "operation": self.operation,
            "determinism_class": self.determinism_class,
            "tie_break_policy": self.tie_break_policy,
            "tolerance_policy": self.tolerance_policy,
            "output_order_policy": self.output_order_policy,
            "missing_group_policy": self.missing_group_policy,
            "overflow_policy": self.overflow_policy,
            "notes": self.notes,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "release_readiness_authorized": self.release_readiness_authorized,
            "rt_traversal_replacement_allowed": self.rt_traversal_replacement_allowed,
            "claim_boundary": V2_5_DETERMINISM_POLICY_CLAIM_BOUNDARY,
        }


V2_5_DETERMINISM_POLICIES: tuple[V25ContinuationDeterminismPolicy, ...] = (
    V25ContinuationDeterminismPolicy(
        operation="segmented_count_i64",
        determinism_class="exact_integer_commutative",
        tie_break_policy="not_applicable",
        tolerance_policy="exact_match_required",
        output_order_policy="dense_group_id_order",
        missing_group_policy="zero_count_for_missing_groups",
        overflow_policy="int64_overflow_is_contract_error",
    ),
    V25ContinuationDeterminismPolicy(
        operation="segmented_sum_f64",
        determinism_class="floating_reduction_tolerance_required",
        tie_break_policy="not_applicable",
        tolerance_policy="backend_must_publish_reduction_order_or_abs_rel_tolerance",
        output_order_policy="dense_group_id_order",
        missing_group_policy="zero_sum_for_missing_groups",
        overflow_policy="nan_inf_follow_partner_float_semantics_and_must_be_tested_by_caller",
    ),
    V25ContinuationDeterminismPolicy(
        operation="grouped_vector_sum_f64x2",
        determinism_class="floating_vector_reduction_tolerance_required",
        tie_break_policy="not_applicable",
        tolerance_policy="backend_must_publish_reduction_order_or_abs_rel_tolerance_per_component",
        output_order_policy="dense_group_id_order",
        missing_group_policy="zero_vector_for_missing_groups",
        overflow_policy="nan_inf_follow_partner_float_semantics_and_must_be_tested_by_caller",
    ),
    V25ContinuationDeterminismPolicy(
        operation="segmented_min_f64",
        determinism_class="value_extremum",
        tie_break_policy="not_applicable_no_item_witness_returned",
        tolerance_policy="exact_value_or_documented_float_tolerance_for_backend",
        output_order_policy="compact_present_group_id_order_plus_missing_group_ids",
        missing_group_policy="missing_group_ids_returned_explicitly",
        overflow_policy="not_applicable",
    ),
    V25ContinuationDeterminismPolicy(
        operation="segmented_max_f64",
        determinism_class="value_extremum",
        tie_break_policy="not_applicable_no_item_witness_returned",
        tolerance_policy="exact_value_or_documented_float_tolerance_for_backend",
        output_order_policy="compact_present_group_id_order_plus_missing_group_ids",
        missing_group_policy="missing_group_ids_returned_explicitly",
        overflow_policy="not_applicable",
    ),
    V25ContinuationDeterminismPolicy(
        operation="compact_mask_i64",
        determinism_class="stable_filter",
        tie_break_policy="not_applicable",
        tolerance_policy="exact_match_required",
        output_order_policy="preserve_input_row_order",
        missing_group_policy="not_applicable",
        overflow_policy="output_capacity_must_fit_input_mask_count",
    ),
    V25ContinuationDeterminismPolicy(
        operation="edge_list_components_i64",
        determinism_class="canonical_component_labeling",
        tie_break_policy="component_label_is_smallest_node_id",
        tolerance_policy="exact_match_required",
        output_order_policy="node_id_order",
        missing_group_policy="isolated_nodes_label_to_self",
        overflow_policy="max_iterations_exhaustion_is_contract_error",
    ),
    V25ContinuationDeterminismPolicy(
        operation="bounded_collect_finalize_i64",
        determinism_class="stable_bounded_collection",
        tie_break_policy="preserve_input_row_order_within_group",
        tolerance_policy="exact_match_required",
        output_order_policy="group_id_order_then_input_row_order",
        missing_group_policy="empty_row_offset_span",
        overflow_policy="fail_closed_overflow_no_silent_truncation",
    ),
    V25ContinuationDeterminismPolicy(
        operation="grouped_argmin_f64",
        determinism_class="score_witness_tie_break",
        tie_break_policy="lowest_score_then_lowest_item_id",
        tolerance_policy="exact_score_or_documented_float_tolerance_for_backend",
        output_order_policy="compact_present_group_id_order_plus_missing_group_ids",
        missing_group_policy="missing_group_ids_returned_explicitly",
        overflow_policy="not_applicable",
    ),
    V25ContinuationDeterminismPolicy(
        operation="grouped_argmax_f64",
        determinism_class="score_witness_tie_break",
        tie_break_policy="highest_score_then_lowest_item_id",
        tolerance_policy="exact_score_or_documented_float_tolerance_for_backend",
        output_order_policy="compact_present_group_id_order_plus_missing_group_ids",
        missing_group_policy="missing_group_ids_returned_explicitly",
        overflow_policy="not_applicable",
    ),
    V25ContinuationDeterminismPolicy(
        operation="grouped_topk_f64",
        determinism_class="ranked_score_witness_tie_break",
        tie_break_policy="lowest_score_then_lowest_item_id_per_rank_deduplicate_items_by_lowest_score",
        tolerance_policy="exact_score_or_documented_float_tolerance_for_backend",
        output_order_policy="group_id_order_then_rank_order",
        missing_group_policy="missing_group_ids_returned_explicitly",
        overflow_policy="k_must_fit_declared_max_and_output_capacity",
    ),
    V25ContinuationDeterminismPolicy(
        operation="hit_stream_grouped_ray_id_primitive_i64",
        determinism_class="event_ordered_grouped_hit_stream",
        tie_break_policy="first_last_use_producer_event_row_order",
        tolerance_policy="exact_integer_reductions_required",
        output_order_policy="dense_ray_id_group_order",
        missing_group_policy="empty_groups_use_signed_minus_one_sentinels_for_first_last",
        overflow_policy="producer_overflow_fails_closed_before_reduction",
    ),
    V25ContinuationDeterminismPolicy(
        operation="hit_stream_primitive_payload_grouped_sum_f64",
        determinism_class="event_ordered_hit_stream_payload_sum",
        tie_break_policy="not_applicable_commutative_payload_sum",
        tolerance_policy="backend_must_publish_reduction_order_or_abs_rel_tolerance",
        output_order_policy="dense_primitive_group_id_order",
        missing_group_policy="zero_count_and_zero_sum_for_missing_groups",
        overflow_policy="producer_overflow_fails_closed_before_reduction",
        notes="primitive_id rows map through generic primitive_group_ids and primitive_values columns",
    ),
)


def v2_5_continuation_determinism_policies() -> dict[str, Any]:
    rows = tuple(policy.to_metadata() for policy in V2_5_DETERMINISM_POLICIES)
    return {
        "policy_version": V2_5_DETERMINISM_POLICY_VERSION,
        "continuation_contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation_count": len(rows),
        "operations": V2_5_PARTNER_CONTINUATION_OPERATION_NAMES,
        "rows": rows,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "release_readiness_authorized": False,
        "rt_traversal_replacement_allowed": False,
        "claim_boundary": V2_5_DETERMINISM_POLICY_CLAIM_BOUNDARY,
    }


def plan_v2_5_continuation_determinism(operation: str) -> dict[str, Any]:
    normalized_operation = str(operation).strip()
    for policy in V2_5_DETERMINISM_POLICIES:
        if policy.operation == normalized_operation:
            return policy.to_metadata()
    raise ValueError("unknown v2.5 continuation determinism policy")


def validate_v2_5_continuation_determinism_policies(
    policies: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policies = v2_5_continuation_determinism_policies() if policies is None else policies
    errors: list[str] = []
    rows = tuple(policies.get("rows", ()))
    if policies.get("policy_version") != V2_5_DETERMINISM_POLICY_VERSION:
        errors.append("unexpected determinism policy version")
    if int(policies.get("operation_count", -1)) != len(V2_5_PARTNER_CONTINUATION_OPERATION_NAMES):
        errors.append("operation_count must match v2.5 continuation operations")
    operations = tuple(row.get("operation") for row in rows if isinstance(row, dict))
    if set(operations) != set(V2_5_PARTNER_CONTINUATION_OPERATION_NAMES):
        errors.append("determinism policies must cover every v2.5 continuation operation exactly once")
    if len(operations) != len(set(operations)):
        errors.append("determinism policies contain duplicate operations")
    for claim_field in (
        "public_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "release_readiness_authorized",
        "rt_traversal_replacement_allowed",
    ):
        if policies.get(claim_field) is not False:
            errors.append(f"top-level determinism policy must keep {claim_field} false")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("determinism policy rows must be metadata dictionaries")
            continue
        operation = str(row.get("operation", ""))
        if operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            errors.append(f"unknown operation in determinism policy: {operation}")
        for claim_field in (
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "release_readiness_authorized",
            "rt_traversal_replacement_allowed",
        ):
            if row.get(claim_field) is not False:
                errors.append(f"{operation} must keep {claim_field} false")
        if operation in {"grouped_argmin_f64", "grouped_argmax_f64", "grouped_topk_f64"}:
            if "item_id" not in str(row.get("tie_break_policy", "")):
                errors.append(f"{operation} must publish an item_id tie-break")
        if operation in {"segmented_sum_f64", "grouped_vector_sum_f64x2"}:
            if "tolerance" not in str(row.get("tolerance_policy", "")):
                errors.append(f"{operation} must publish a float tolerance/order policy")
        if operation in {"bounded_collect_finalize_i64", "hit_stream_grouped_ray_id_primitive_i64"}:
            if "fail" not in str(row.get("overflow_policy", "")).lower():
                errors.append(f"{operation} must fail closed on overflow")
    return {
        "status": "accept" if not errors else "reject",
        "policy_version": policies.get("policy_version"),
        "operation_count": policies.get("operation_count"),
        "errors": tuple(errors),
    }
