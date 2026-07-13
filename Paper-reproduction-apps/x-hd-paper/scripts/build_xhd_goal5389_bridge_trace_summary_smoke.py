from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5389_bridge_trace_summary_smoke.json"

SMOKE = RESULTS / "xhd_goal5389_source64_trace_summary_smoke_pod.json"
GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5388 = RESULTS / "xhd_goal5388_status_trace_summary_contract.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(output: Path = OUT) -> dict[str, Any]:
    smoke = _read_json(SMOKE)
    author = _read_json(GOAL5387)
    contract = _read_json(GOAL5388)
    bridge = smoke["active_query_bridge"]
    trace_summary = bridge["trace_summary"]
    comparison = bridge["comparison_to_author"]
    author_target = author["author_lb_trace_v2"]

    return {
        "goal": "Goal5389",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5389.bridge_trace_summary_smoke.v1",
        "status": "source_limited_bridge_trace_summary_emitted__full_parity_not_claimed",
        "exit_label": "bridge_trace_summary_smoke_ready__full_native_stream_parity_still_required",
        "purpose": (
            "Verify that the current RTDL active-query bridge probe can emit the "
            "Goal5388 generic status-trace summary from actual RTDL offload rows "
            "on POD, before attempting a full native parity gate."
        ),
        "input_artifacts": {
            "source64_smoke_pod": str(SMOKE),
            "goal5387_author_trace_v2": str(GOAL5387),
            "goal5388_summary_contract": str(GOAL5388),
        },
        "pod": {
            "host": "213.173.108.24",
            "port": 13502,
            "wrapper": "scripts/current_pod_ssh.py",
        },
        "run_scope": {
            "input1": smoke["input1"],
            "input2": smoke["input2"],
            "source_limit": int(smoke["source_limit"]),
            "source_limit_applied": bool(smoke["source_limit_applied"]),
            "point_count_a_after_limit": int(smoke["point_count_a"]),
            "point_count_b": int(smoke["point_count_b"]),
            "frontier_status_probe_mode": smoke["frontier_status_probe_mode"],
            "initial_state": smoke["initial_state"],
            "max_inline_points": int(smoke["max_inline_points"]),
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
            "active_in_queue_size": int(author_target["active_in_queue_size"]),
            "raw_offload_rows_before_sort_reduce": int(
                author_target["raw_offload_rows_before_sort_reduce"]
            ),
            "status_count_offloading_append": int(author_target["status_count_offloading_append"]),
            "raw_offload_row_hash": int(author_target["batch_0"]["raw_offload_row_hash"]),
            "raw_offload_row_sample_point_ids": list(
                author_target["batch_0"]["raw_offload_row_sample_point_ids"]
            ),
            "raw_offload_row_sample_cell_ids": list(
                author_target["batch_0"]["raw_offload_row_sample_cell_ids"]
            ),
        },
        "comparison_to_author": {
            "active_query_count_parity": bool(comparison["active_query_count_parity"]),
            "row_count_parity": bool(comparison["row_count_parity"]),
            "hash_comparable_to_author": bool(comparison["hash_comparable_to_author"]),
            "hash_parity": bool(comparison["hash_parity"])
            if comparison["hash_parity"] is not None
            else None,
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
        },
        "decision": {
            "trace_summary_emitted_from_actual_rtdl_rows": True,
            "full_run_or_row_parity_claimed": False,
            "next_gate": "full_or_bounded_native_stream_trace_summary_against_goal5387",
            "why": (
                "The source-limited POD smoke proves the plumbing can emit the "
                "generic trace summary, but it intentionally uses only 64 source "
                "queries and does not establish full-row parity or hash parity."
            ),
        },
        "claim_boundary": {
            "trace_summary_plumbing_claimed": True,
            "source_limited_smoke_claimed_as_author_parity": False,
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
        "contract_carry_forward": {
            "goal5388_contract": contract["system_api"]["contract"],
            "next_native_requirements": contract["next_native_requirements"],
        },
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
