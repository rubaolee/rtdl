#!/usr/bin/env python3
"""Frozen targeted Goal5784 V2-direct/V4 confirmation contract."""

from __future__ import annotations

import hashlib
import json

from goal5776_real_scale_formal_contract import (
    COLD,
    FORMAL_WORKER_TIMEOUT_SECONDS,
    LIFECYCLES,
    METHODS,
    PAIR_COUNT,
    PREPARED,
    UNIT_BY_ID as GOAL5776_UNIT_BY_ID,
    V2,
    V4,
)


TARGET_UNIT_IDS = (
    "triangle__com_dblp__rt_2a1",
    "triangle__cit_patents__rt_2a1",
    "triangle__soc_livejournal1__rt_2a1",
    "rtbh__author_32768",
)
UNITS = tuple(GOAL5776_UNIT_BY_ID[name] for name in TARGET_UNIT_IDS)
UNIT_BY_ID = {unit.unit_id: unit for unit in UNITS}


def statistical_rows() -> tuple[dict[str, str], ...]:
    return tuple({
        "lifecycle": lifecycle,
        "unit_id": unit.unit_id,
        "row_id": unit.statistical_row_ids_for(lifecycle)[0],
        "app": unit.app,
        "paper_algorithm": unit.paper_algorithm,
    } for lifecycle in LIFECYCLES for unit in UNITS)


def schedule() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for lifecycle in LIFECYCLES:
        for unit in UNITS:
            for pair_index in range(PAIR_COUNT):
                order = METHODS if pair_index % 2 == 0 else tuple(reversed(METHODS))
                for order_ordinal, method in enumerate(order):
                    rows.append({
                        "worker_index": len(rows),
                        "lifecycle": lifecycle,
                        "unit_id": unit.unit_id,
                        "pair_index": pair_index,
                        "order_ordinal": order_ordinal,
                        "method": method,
                    })
    return tuple(rows)


def contract_document() -> dict[str, object]:
    return {
        "schema": "rtdl.goal5784.targeted_v2_v4_formal_contract.v1",
        "goal": 5784,
        "scientific_predecessor": "Goal5782",
        "immutable_control_result": "Goal5776_v9__9_median_pass_25_fail",
        "methods": list(METHODS),
        "lifecycles": list(LIFECYCLES),
        "pair_count_per_unit_lifecycle": PAIR_COUNT,
        "execution_unit_count": len(UNITS),
        "formal_worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "worker_count_derivation": "4 units * 2 lifecycles * 8 ABBA pairs * 2 methods = 128",
        "row_count_derivation": "4 affected units * 2 independently reported lifecycles = 8",
        "units": [{
            "unit_id": unit.unit_id,
            "app": unit.app,
            "paper_algorithm": unit.paper_algorithm,
            "workload": unit.workload,
            "input_scale": unit.input_scale,
            "input_identity_level": unit.input_identity_level,
            "supported_lifecycles": list(unit.supported_lifecycles),
            "v4_numba_leaf_cache_required": unit.v4_numba_leaf_cache_required,
            "statistical_row_ids_by_lifecycle": {
                lifecycle: list(unit.statistical_row_ids_for(lifecycle))
                for lifecycle in LIFECYCLES
            },
            "mechanism": (
                "compiler_fused_checked_u64_device_reduction"
                if unit.app == "triangle_counting"
                else "canonical_packed_hierarchy_output_binding"
            ),
        } for unit in UNITS],
        "timing_contract": {
            "registered_seconds_are_same_worker_mutually_exclusive_phase_sum": True,
            "cold": "load + prepare + execute + teardown",
            "prepared": "execute_only__loading_and_preparation_reported_separately",
            "correctness_comparator_inside_timer": False,
            "v2_and_v4_same_endpoint_boundary": True,
            "prepared_work_called_free": False,
            "cold_result_may_be_replaced_by_prepared": False,
        },
        "statistics_contract": {
            "ratio": "v2_direct_seconds / v4_seconds",
            "greater_than_one_favors": V4,
            "summary": "median of eight paired ABBA ratios",
            "bootstrap_draws": 10_000,
            "bootstrap_ci_indices": [249, 9749],
            "bootstrap_seed": "57_760_000 + row_index__reused_frozen_goal5776_convention",
            "row_local_no_slower_gate": "paired_ratio_median >= 1.0",
            "clear_favorable_row": "bootstrap_ci95_lower > 1.0",
            "cross_row_or_lifecycle_compensation_allowed": False,
            "fixed_speedup_target_used": False,
        },
        "mechanism_claim_contract": {
            "triangle_may_become_second_named_fusion_family_only_if": (
                "at_least_one_preregistered_RT_2A1_row_has_ci95_lower_gt_1_and_"
                "all_workers_bind_the_fused_checked_u64_mechanism"
            ),
            "rt_barneshut_is_fusion": False,
            "unfavorable_or_uncertain_rows_must_be_preserved": True,
            "goal5776_may_be_replaced_or_relabelled": False,
        },
        "worker_contract": {
            "fresh_parent_pid_required": True,
            "behavioral_true_optix_required": True,
            "exact_application_output_required": True,
            "one_source_native_plan_target_identity": True,
            "default_may_select_between_application_algorithms": False,
            "retry_resume_replacement_row_drop_relabel_allowed": False,
            "per_worker_timeout_seconds": FORMAL_WORKER_TIMEOUT_SECONDS,
        },
        "scope_exclusions": {
            "rt_1a2": True,
            "unaffected_apps": True,
            "goal5783_rtxrmq": True,
            "v3": True,
            "full_nine_app_matrix": True,
        },
    }


def contract_sha256() -> str:
    return hashlib.sha256(json.dumps(
        contract_document(), sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode()).hexdigest()


__all__ = [
    "COLD", "FORMAL_WORKER_TIMEOUT_SECONDS", "LIFECYCLES", "METHODS",
    "PAIR_COUNT", "PREPARED", "TARGET_UNIT_IDS", "UNIT_BY_ID", "UNITS",
    "V2", "V4", "contract_document", "contract_sha256", "schedule",
    "statistical_rows",
]
