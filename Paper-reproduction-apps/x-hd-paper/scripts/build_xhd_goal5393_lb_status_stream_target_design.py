from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5393_lb_status_stream_target_design.json"

GOAL5392 = RESULTS / "xhd_goal5392_lb_denominator_surface_reconciliation.json"
GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5384 = RESULTS / "xhd_goal5384_multiround_status_requirements.json"
GOAL5365 = RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _surface_by_name(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for surface in payload["surfaces"]:
        if surface["name"] == name:
            return surface
    raise KeyError(name)


def build(output: Path = OUT) -> dict[str, Any]:
    surfaces = _read_json(GOAL5392)
    author_payload = _read_json(GOAL5387)
    multiround = _read_json(GOAL5384)
    full_cover_gate = _read_json(GOAL5365)

    author_rows = int(surfaces["author_oracle"]["raw_offload_rows_before_sort_reduce"])
    active_count = int(surfaces["author_oracle"]["active_in_queue_size"])
    selected = _surface_by_name(surfaces, "full_cover_lb256_behavior_gate_surface")
    bridge = _surface_by_name(surfaces, "current_bridge_materialized_offload_rows")
    default = _surface_by_name(surfaces, "default_inline_raw_kind2_count")
    overcount = _surface_by_name(surfaces, "noinline_or_heavy_before_raw_kind2_overcount")

    selected_rows = int(selected["row_count"])
    missing_rows = author_rows - selected_rows
    missing_quotient, missing_remainder = divmod(missing_rows, active_count)
    bridge_missing_rows = author_rows - int(bridge["row_count"])
    default_missing_rows = author_rows - int(default["row_count"])

    author_trace = author_payload["author_lb_trace_v2"]
    author_batch = author_trace["batch_0"]
    full_cover_comparison = full_cover_gate["comparison"]

    return {
        "goal": "Goal5393",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5393.lb_status_stream_target_design.v1",
        "status": "status_stream_target_selected__full_cover_delta_requires_generic_transitions",
        "exit_label": "lb_status_stream_target_selected__implement_generic_full_cover_delta_probe_next",
        "purpose": (
            "Select the next explicit -lb native status-stream target after "
            "Goal5392 reconciled denominator surfaces. This goal chooses the "
            "author-compatible raw-status semantics target and defines the next "
            "generic implementation gate without claiming explicit -lb support."
        ),
        "input_artifacts": {
            "goal5392_denominator_surface_reconciliation": str(GOAL5392),
            "goal5387_author_trace_v2": str(GOAL5387),
            "goal5384_multiround_status_requirements": str(GOAL5384),
            "goal5365_full_cover_behavior_gate": str(GOAL5365),
        },
        "author_oracle": {
            "active_in_queue_size": active_count,
            "raw_offload_rows_before_sort_reduce": author_rows,
            "raw_offload_row_hash": int(author_batch["raw_offload_row_hash"]),
            "load_balance_feedback_update_count": int(author_trace["load_balance_feedback_update_count"]),
            "status_count_offloading_append": int(author_trace["status_count_offloading_append"]),
        },
        "target_selection": {
            "selected_starting_surface": selected["name"],
            "why_selected": (
                "It is the closest known RTDL row-count surface to the author "
                "raw offload denominator while staying in generic RTDL row "
                "semantics. It still fails parity and must not be treated as "
                "correctness."
            ),
            "selected_surface_rows": selected_rows,
            "selected_rows_per_active": selected["division"]["rows_per_active_average"],
            "author_rows_per_active": surfaces["author_oracle"]["division"]["rows_per_active_average"],
            "missing_rows_to_author": missing_rows,
            "missing_rows_per_active_if_exact": missing_quotient if missing_remainder == 0 else None,
            "missing_rows_per_active_remainder": missing_remainder,
            "bridge_missing_rows": bridge_missing_rows,
            "default_raw_kind2_missing_rows": default_missing_rows,
            "overcount_rows": int(overcount["row_count"]) - author_rows,
            "full_cover_promoted_to_correctness": False,
            "bridge_surface_rejected_as_implementation_target": True,
            "hardcoded_fanout_rejected": True,
        },
        "semantic_gap_hypotheses": [
            {
                "name": "multi_round_feedback_or_reactivation_delta",
                "required_evidence": (
                    "Rows or state transitions added by feedback / next-active "
                    "rounds, keyed by active_queue_index, explain the remaining "
                    "6 rows per active on aggregate."
                ),
                "generic": True,
            },
            {
                "name": "author_current_best_restore_delta",
                "required_evidence": (
                    "Author cmin2/current-best restoration by active queue index "
                    "changes which cells remain offload candidates compared with "
                    "the full-cover single-surface approximation."
                ),
                "generic": True,
            },
            {
                "name": "miss_completed_aborted_transition_delta",
                "required_evidence": (
                    "Generic terminal transitions are counted or sampled in a way "
                    "not represented by the full-cover row surface."
                ),
                "generic": True,
            },
            {
                "name": "load_balance_processing_feedback_delta",
                "required_evidence": (
                    "Author loadBalanceProcessing feedback changes later current "
                    "best or offload rows; RTDL must expose generic feedback "
                    "updates rather than author-specific logic."
                ),
                "generic": True,
            },
        ],
        "selected_next_gate": {
            "name": "generic_full_cover_delta_status_probe",
            "goal_hint": "Goal5394",
            "description": (
                "Add a generic status-stream probe that starts from the closest "
                "full-cover-like raw surface and measures whether generic "
                "multi-round feedback/current-best/terminal transitions can "
                "explain the remaining delta to the author trace v2 oracle."
            ),
            "must_compare": [
                "row_count against author 27,133,990",
                "raw offload row hash or deterministic samples",
                "status_count_offloading",
                "feedback update count or explicit not-applicable evidence",
                "miss/completed/aborted counters or explicit not-applicable evidence",
            ],
            "success_label": "generic_status_stream_moves_denominator_toward_author",
            "failure_label": "generic_status_stream_target_not_author_compatible__lb_fail_closed_candidate",
        },
        "existing_generic_contracts_to_reuse": {
            "multiround_status_contract": multiround["generic_system_addition"]["contract"],
            "trace_summary_contract": "generic_active_query_status_trace_summary_v1",
            "app_semantics": "none",
        },
        "supporting_behavior_gate": {
            "goal5365_value_match": bool(full_cover_comparison["matched"]),
            "goal5365_author_offloading_size": int(full_cover_comparison["author_lb256_offloading_size"]),
            "goal5365_rtdl_heavy_offload_peak_rows": int(
                full_cover_comparison["rtdl_lb256_heavy_offload_peak_rows"]
            ),
            "goal5365_explicit_lb_support_authorized": False,
            "why_not_enough": (
                "Goal5365 passes a bounded behavior/value gate but explicitly "
                "does not establish row-count denominator parity or explicit -lb "
                "support."
            ),
        },
        "decision": {
            "native_code_authorized_by_this_goal": False,
            "next_work_is_design_to_implementation_transition": True,
            "selected_direction": "implement_generic_full_cover_delta_status_probe_next",
            "fail_closed_if_requires_xhd_specific_logic": True,
        },
        "claim_boundary": {
            "status_stream_target_selection_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "full_cover_surface_promoted_to_author_semantics": False,
            "native_backend_completion_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
