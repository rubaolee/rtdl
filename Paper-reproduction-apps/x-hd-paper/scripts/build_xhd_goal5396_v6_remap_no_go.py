from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5396_v6_remap_no_go.json"

GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5392 = RESULTS / "xhd_goal5392_lb_denominator_surface_reconciliation.json"
GOAL5395 = RESULTS / "xhd_goal5395_native_status_stream_abi_gate.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    author = _read_json(GOAL5387)
    surfaces = _read_json(GOAL5392)
    abi_gate = _read_json(GOAL5395)

    active_count = int(author["author_lb_trace_v2"]["active_in_queue_size"])
    author_rows = int(author["author_lb_trace_v2"]["raw_offload_rows_before_sort_reduce"])
    author_rows_per_active = author_rows // active_count
    author_remainder = author_rows % active_count

    surface_by_name = {surface["name"]: surface for surface in surfaces["surfaces"]}
    bridge = surface_by_name["current_bridge_materialized_offload_rows"]
    full_cover = surface_by_name["full_cover_lb256_behavior_gate_surface"]
    raw_kind2 = surface_by_name["default_inline_raw_kind2_count"]
    overcount = surface_by_name["noinline_or_heavy_before_raw_kind2_overcount"]

    full_cover_rows = int(full_cover["row_count"])
    missing_rows = author_rows - full_cover_rows
    missing_rows_per_active = missing_rows // active_count
    missing_remainder = missing_rows % active_count

    current_native = abi_gate["current_native_surface_audit"]
    required_missing_columns = list(current_native["missing_required_output_columns"])
    required_missing_semantics = list(current_native["missing_required_semantics"])

    v6_remap_assessment = {
        "would_change_denominator": False,
        "would_add_missing_rows": False,
        "would_add_transition_semantics": False,
        "would_add_feedback_semantics": False,
        "would_add_before_after_current_best_per_row": False,
        "would_only_relabel_existing_rows": True,
        "known_best_v6_like_rows": full_cover_rows,
        "author_rows": author_rows,
        "row_delta_author_minus_best_v6_like": missing_rows,
        "row_delta_per_active": missing_rows_per_active,
        "row_delta_remainder": missing_remainder,
        "verdict": "reject_v6_remap_as_native_status_stream_backend",
    }

    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5396.v6_remap_no_go.v1",
        "goal": "Goal5396",
        "date": "2026-07-10",
        "status": "v6_remap_rejected__real_generic_native_status_stream_required",
        "exit_label": "v6_remap_no_go__implement_real_v7_or_keep_lb_fail_closed",
        "purpose": (
            "Decide whether the current v6 native frontier collector can be "
            "safely promoted to the Goal5395 native status-stream ABI by a "
            "column remap. It cannot."
        ),
        "input_artifacts": {
            "goal5387_author_trace_v2": str(GOAL5387),
            "goal5392_denominator_surfaces": str(GOAL5392),
            "goal5395_native_status_stream_abi_gate": str(GOAL5395),
        },
        "author_oracle": {
            "active_count": active_count,
            "raw_offload_rows_before_sort_reduce": author_rows,
            "rows_per_active": author_rows_per_active,
            "rows_per_active_remainder": author_remainder,
            "raw_offload_row_hash": int(
                author["author_lb_trace_v2"].get(
                    "raw_offload_row_hash",
                    author["author_lb_trace_v2"]["batch_0"]["raw_offload_row_hash"],
                )
            ),
            "status_count_offloading": int(author["author_lb_trace_v2"]["status_count_offloading_append"]),
            "feedback_update_count": int(author["author_lb_trace_v2"]["load_balance_feedback_update_count"]),
        },
        "known_rtdl_surfaces": {
            "bridge_rows": int(bridge["row_count"]),
            "bridge_rows_per_active": bridge["division"]["rows_per_active_average"],
            "raw_kind2_rows": int(raw_kind2["row_count"]),
            "raw_kind2_rows_per_active": raw_kind2["division"]["rows_per_active_average"],
            "full_cover_rows": full_cover_rows,
            "full_cover_rows_per_active": full_cover["division"]["rows_per_active_average"],
            "overcount_rows": int(overcount["row_count"]),
            "overcount_rows_per_active": overcount["division"]["rows_per_active_average"],
            "any_surface_has_row_count_parity": bool(surfaces["summary"]["any_surface_has_row_count_parity"]),
            "any_surface_has_hash_parity": bool(surfaces["summary"]["any_surface_has_hash_parity"]),
        },
        "goal5395_abi_gap": {
            "contract": abi_gate["generic_native_abi_contract"]["contract"],
            "current_v6_symbol": current_native["latest_cell_mbr_status_probe_symbol"],
            "current_surface_is_single_launch_frontier_probe": bool(
                current_native["current_surface_is_single_launch_frontier_probe"]
            ),
            "current_surface_satisfies_goal5394_native_probe": bool(
                current_native["current_surface_satisfies_goal5394_native_probe"]
            ),
            "missing_required_output_columns": required_missing_columns,
            "missing_required_semantics": required_missing_semantics,
            "existing_native_v6_is_sufficient": bool(
                abi_gate["decision"]["existing_native_v6_is_sufficient"]
            ),
        },
        "v6_remap_assessment": v6_remap_assessment,
        "decision": {
            "v6_column_remap_authorized": False,
            "native_status_stream_backend_implemented_by_goal5396": False,
            "explicit_lb_support_claimed": False,
            "explicit_lb_remains_fail_closed": True,
            "real_v7_backend_required": True,
            "real_v7_definition": (
                "A new generic native active-query status stream emitted at the "
                "traversal/status transition point, with current-best before/after, "
                "transition phase, and feedback/miss/completed/aborted telemetry. "
                "It cannot be a post-hoc relabeling of v6 frontier rows."
            ),
            "recommended_next_goal": "Goal5397",
            "recommended_next_action": (
                "Implement a real generic v7 native status-stream backend in the "
                "OptiX payload/any-hit status path, or keep explicit -lb fail-closed "
                "if that would require app-specific constants."
            ),
            "pod_required_for_next_goal": True,
        },
        "claim_boundary": {
            "native_backend_completion_claimed": False,
            "existing_native_v6_parity_claimed": False,
            "v6_column_remap_claimed_sufficient": False,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }

    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
