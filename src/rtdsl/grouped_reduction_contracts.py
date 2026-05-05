from __future__ import annotations

from typing import Any


V1_5_STABLE_REDUCTION_PRIMITIVES = (
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)

V1_5_EXPERIMENTAL_PRIMITIVES = ("COLLECT_K_BOUNDED",)


def v1_5_grouped_reduction_contracts() -> tuple[dict[str, Any], ...]:
    """Return the v1.5 grouped-reduction contracts that unblock deferred rows.

    These rows are design gates, not public claims and not proof that a native
    backend implementation exists. They deliberately express grouped boolean
    output as grouped integer count plus a boolean result layout, avoiding a new
    stable primitive outside the accepted v1.5 primitive set.
    """
    return (
        {
            "app": "robot_collision_screening",
            "subpath": "prepared_pose_flags",
            "status": "design_required",
            "input_primitive": "ANY_HIT",
            "reduction_primitive": "REDUCE_INT(COUNT)",
            "group_key": "pose_id",
            "result_layout": "grouped_threshold_bool",
            "dtype_policy": "uint32 hit counts; boolean flag is count > 0",
            "determinism_policy": "integer count is deterministic for fixed ray order",
            "correctness_contract": "per-pose flag must match app-specific prepared_pose_flags oracle",
            "unblocks": "replace app-specific pose grouping after OptiX and Embree expose grouped count output",
        },
        {
            "app": "database_analytics",
            "subpath": "sales_risk_grouped_count",
            "status": "design_required",
            "input_primitive": "numeric_predicate_rows",
            "reduction_primitive": "REDUCE_INT(COUNT)",
            "group_key": "risk_bucket_or_region_id",
            "result_layout": "grouped_int64_count",
            "dtype_policy": "signed int64 counts; overflow is a contract error",
            "determinism_policy": "integer count is deterministic after predicate lowering",
            "correctness_contract": "group counts must match Python compact-summary oracle exactly",
            "unblocks": "generic DB compact count wrapper for Embree and OptiX",
        },
        {
            "app": "database_analytics",
            "subpath": "sales_risk_grouped_sum",
            "status": "design_required",
            "input_primitive": "numeric_predicate_rows",
            "reduction_primitive": "REDUCE_INT(SUM)",
            "group_key": "risk_bucket_or_region_id",
            "result_layout": "grouped_int64_sum",
            "dtype_policy": "signed int64 payload sum; overflow is a contract error",
            "determinism_policy": "integer sum is deterministic after predicate lowering",
            "correctness_contract": "group sums must match Python compact-summary oracle exactly",
            "unblocks": "generic DB compact revenue/risk sum wrapper for Embree and OptiX",
        },
        {
            "app": "polygon_pair_overlap_area_rows",
            "subpath": "exact_area_sum",
            "status": "design_required",
            "input_primitive": "candidate_overlap_rows",
            "reduction_primitive": "REDUCE_FLOAT(SUM)",
            "group_key": "polygon_pair_id",
            "result_layout": "grouped_float64_sum",
            "dtype_policy": "float64 preferred; float32 requires explicit tolerance override",
            "determinism_policy": "backend must publish reduction order or tolerance schema",
            "correctness_contract": "area sums must satisfy documented abs/rel tolerance versus Python oracle",
            "unblocks": "move exact polygon area aggregation out of app-specific continuation",
        },
        {
            "app": "polygon_set_jaccard",
            "subpath": "chunked_candidate_scoring",
            "status": "experimental_blocked",
            "input_primitive": "COLLECT_K_BOUNDED",
            "reduction_primitive": "REDUCE_FLOAT(SUM)",
            "group_key": "polygon_pair_id",
            "result_layout": "bounded_pairs_plus_grouped_float64_score",
            "dtype_policy": "float64 preferred for scores; bounded collection must report truncation",
            "determinism_policy": "collection order, overflow, and score tolerance must be explicit",
            "correctness_contract": "bounded candidate scoring must prove no silent truncation before promotion",
            "unblocks": "only diagnostic work until COLLECT_K_BOUNDED has reviewed overflow/failure behavior",
        },
    )


def validate_v1_5_grouped_reduction_contracts() -> tuple[dict[str, Any], ...]:
    contracts = v1_5_grouped_reduction_contracts()
    required_fields = (
        "app",
        "subpath",
        "status",
        "input_primitive",
        "reduction_primitive",
        "group_key",
        "result_layout",
        "dtype_policy",
        "determinism_policy",
        "correctness_contract",
        "unblocks",
    )
    valid_statuses = {"design_required", "experimental_blocked"}
    valid_reductions = set(V1_5_STABLE_REDUCTION_PRIMITIVES)
    valid_inputs = {"ANY_HIT", "numeric_predicate_rows", "candidate_overlap_rows"} | set(
        V1_5_EXPERIMENTAL_PRIMITIVES
    )
    for contract in contracts:
        for field in required_fields:
            if field not in contract:
                raise ValueError(f"missing grouped reduction contract field: {field}")
            if not str(contract[field]).strip():
                raise ValueError(f"grouped reduction contract field must be non-empty: {field}")
        if contract["status"] not in valid_statuses:
            raise ValueError(f"invalid grouped reduction status: {contract['status']}")
        if contract["input_primitive"] not in valid_inputs:
            raise ValueError(f"invalid grouped reduction input primitive: {contract['input_primitive']}")
        if contract["reduction_primitive"] not in valid_reductions:
            raise ValueError(f"invalid grouped reduction primitive: {contract['reduction_primitive']}")
        if contract["input_primitive"] in V1_5_EXPERIMENTAL_PRIMITIVES:
            if contract["status"] != "experimental_blocked":
                raise ValueError("experimental grouped input must remain experimental_blocked")
        if contract["reduction_primitive"].startswith("GROUPED_"):
            raise ValueError("grouping is a result layout, not a new primitive name")
    return contracts
