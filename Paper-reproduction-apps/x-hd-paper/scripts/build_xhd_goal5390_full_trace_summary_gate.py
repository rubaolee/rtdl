from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5390_full_trace_summary_gate.json"

FULL_POD = RESULTS / "xhd_goal5390_full_trace_summary_pod.json"
GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5389 = RESULTS / "xhd_goal5389_bridge_trace_summary_smoke.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(output: Path = OUT) -> dict[str, Any]:
    full = _read_json(FULL_POD)
    author = _read_json(GOAL5387)
    prior_smoke = _read_json(GOAL5389)
    bridge = full["active_query_bridge"]
    comparison = bridge["comparison_to_author"]
    trace_summary = bridge["trace_summary"]
    author_trace = author["author_lb_trace_v2"]
    author_batch = author_trace["batch_0"]

    active_parity = bool(comparison["active_query_count_parity"])
    row_parity = bool(comparison["row_count_parity"])
    hash_parity = bool(comparison["hash_parity"])

    return {
        "goal": "Goal5390",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5390.full_trace_summary_gate.v1",
        "status": "full_bridge_trace_summary_emitted__row_hash_parity_failed",
        "exit_label": "native_status_stream_denominator_mismatch__lb_remains_unsupported",
        "purpose": (
            "Run the full-source X-HD active-query bridge probe with the "
            "Goal5388 generic trace summary and compare it to the Goal5387 "
            "author trace v2 oracle."
        ),
        "input_artifacts": {
            "full_pod": str(FULL_POD),
            "goal5387_author_trace_v2": str(GOAL5387),
            "goal5389_source_limited_smoke": str(GOAL5389),
        },
        "pod": {
            "host": "213.173.108.24",
            "port": 13502,
            "wrapper": "scripts/current_pod_ssh.py",
        },
        "run_scope": {
            "input1": full["input1"],
            "input2": full["input2"],
            "source_limit": full["source_limit"],
            "source_limit_applied": bool(full["source_limit_applied"]),
            "point_count_a": int(full["point_count_a"]),
            "point_count_b": int(full["point_count_b"]),
            "grid_shape": list(full["grid_shape"]),
            "grid_cell_builder": full["grid_cell_builder"],
            "grid_cell_point_order": full["grid_cell_point_order"],
            "initial_state": full["initial_state"],
            "local_grid_seed_executor": full["local_grid_seed_executor"],
            "frontier_status_probe_mode": full["frontier_status_probe_mode"],
            "max_inline_points": int(full["max_inline_points"]),
            "frontier_row_capacity": int(full["frontier_row_capacity"]),
            "inline_nearest": bool(full["inline_nearest"]),
        },
        "frontier": {
            "row_count": int(full["frontier"]["row_count"]),
            "attempted_count": int(full["frontier"]["attempted_count"]),
            "overflowed": bool(full["frontier"]["overflowed"]),
            "native_symbol": full["frontier"]["native_symbol"],
            "frontier_status_probe_contract": full["frontier"]["frontier_status_probe_contract"],
        },
        "rtdl_trace_summary": {
            "contract": trace_summary["contract"],
            "row_count": int(trace_summary["row_count"]),
            "status_count_offloading": int(trace_summary["status_count_offloading"]),
            "active_query_count": int(trace_summary["active_query_count"]),
            "raw_offload_row_hash": int(trace_summary["raw_offload_row_hash"]),
            "hash_columns": list(trace_summary["hash_columns"]),
            "sample_indices": list(trace_summary["sample_indices"]),
            "samples": trace_summary["samples"],
            "app_semantics": trace_summary["app_semantics"],
        },
        "author_trace_v2_target": {
            "active_in_queue_size": int(author_trace["active_in_queue_size"]),
            "raw_offload_rows_before_sort_reduce": int(
                author_trace["raw_offload_rows_before_sort_reduce"]
            ),
            "status_count_offloading_append": int(author_trace["status_count_offloading_append"]),
            "raw_offload_row_hash": int(author_batch["raw_offload_row_hash"]),
            "raw_offload_row_sample_point_ids": list(author_batch["raw_offload_row_sample_point_ids"]),
            "raw_offload_row_sample_cell_ids": list(author_batch["raw_offload_row_sample_cell_ids"]),
        },
        "comparison_to_author": {
            "active_query_count_parity": active_parity,
            "row_count_parity": row_parity,
            "hash_comparable_to_author": bool(comparison["hash_comparable_to_author"]),
            "hash_parity": hash_parity,
            "sample_comparable_to_author": bool(comparison["sample_comparable_to_author"]),
            "rtdl_bridge_offload_rows": int(comparison["rtdl_bridge_offload_rows"]),
            "author_raw_offload_rows_before_sort_reduce": int(
                comparison["author_raw_offload_rows_before_sort_reduce"]
            ),
            "row_delta_author_minus_rtdl_bridge": int(
                comparison["row_delta_author_minus_rtdl_bridge"]
            ),
            "row_ratio_rtdl_bridge_div_author": float(
                comparison["row_ratio_rtdl_bridge_div_author"]
            ),
            "rtdl_raw_offload_row_hash": int(comparison["rtdl_raw_offload_row_hash"]),
            "author_raw_offload_row_hash": int(comparison["author_raw_offload_row_hash"]),
            "rtdl_sample_source_ids": list(comparison["rtdl_sample_source_ids"]),
            "rtdl_sample_cell_ids": list(comparison["rtdl_sample_cell_ids"]),
            "author_raw_offload_row_sample_point_ids": list(
                comparison["author_raw_offload_row_sample_point_ids"]
            ),
            "author_raw_offload_row_sample_cell_ids": list(
                comparison["author_raw_offload_row_sample_cell_ids"]
            ),
        },
        "timings_sec": {
            "load_inputs": float(full["timings_sec"]["load_inputs"]),
            "grid_cell_mbrs": float(full["timings_sec"]["grid_cell_mbrs"]),
            "initial_seed": float(full["timings_sec"]["initial_seed"]),
            "frontier_rows": float(full["timings_sec"]["frontier_rows"]),
            "active_query_bridge": float(full["timings_sec"]["active_query_bridge"]),
            "total": float(full["timings_sec"]["total"]),
        },
        "comparison_to_goal5389_smoke": {
            "prior_source_limited_row_count": int(prior_smoke["rtdl_trace_summary"]["row_count"]),
            "full_row_count": int(trace_summary["row_count"]),
            "full_active_query_count": int(trace_summary["active_query_count"]),
            "source_limited_smoke_superseded_for_full_parity_question": True,
        },
        "decision": {
            "full_source_trace_summary_emitted": True,
            "active_query_count_matches_author": active_parity,
            "row_count_parity": row_parity,
            "hash_parity": hash_parity,
            "explicit_lb_support_remains_unsupported": True,
            "next_gate": "native_status_stream_semantics_or_fail_closed_lb_closeout",
            "why": (
                "The full-source bridge reaches the same active query count as "
                "the author trace v2 oracle, but it emits only 2,188,225 offload "
                "rows versus the author 27,133,990 rows and its row hash/samples "
                "do not match. The remaining gap is native status-stream "
                "semantics, not source-limited plumbing."
            ),
        },
        "claim_boundary": {
            "full_trace_summary_gate_claimed": True,
            "explicit_lb_support_claimed": False,
            "rtdl_row_count_parity_claimed": False,
            "rtdl_hash_sample_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
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
