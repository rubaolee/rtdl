from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5388_status_trace_summary_contract.json"

GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5381 = RESULTS / "xhd_goal5381_full_bridge_probe_pod.json"
GOAL5383 = RESULTS / "xhd_goal5383_full_seeded_active_initial_best_probe_pod.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _demo_summary() -> dict[str, Any]:
    import rtdsl as rt

    return rt.active_query_status_trace_summary_numpy_columns(
        {
            "source_ids": [100, 100, 101, 102],
            "cell_ids": [50, 51, 60, 70],
            "work_counts": [7, 9, 11, 13],
        },
        active_queue_indices=[10, 11, 12],
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=("source_ids", "cell_ids", "work_counts"),
        return_metadata=True,
    )


def build(output: Path = OUT) -> dict[str, Any]:
    author_v2 = _read_json(GOAL5387)
    goal5381 = _read_json(GOAL5381)
    goal5383 = _read_json(GOAL5383)
    demo = _demo_summary()

    author_trace = author_v2["author_lb_trace_v2"]
    author_batch = author_trace["batch_0"]
    current_candidates = [
        {
            "source": "Goal5381 full bridge probe",
            "artifact": str(GOAL5381),
            "offload_rows": int(goal5381["active_query_bridge"]["offload_row_count"]),
            "active_query_count": int(goal5381["active_query_bridge"]["active_query_count"]),
            "has_raw_row_hash": False,
            "has_raw_row_samples": False,
        },
        {
            "source": "Goal5383 active-initial-best full bridge probe",
            "artifact": str(GOAL5383),
            "offload_rows": int(goal5383["active_query_bridge"]["offload_row_count"]),
            "active_query_count": int(goal5383["active_query_bridge"]["active_query_count"]),
            "has_raw_row_hash": False,
            "has_raw_row_samples": False,
        },
    ]
    for item in current_candidates:
        item["row_count_parity"] = item["offload_rows"] == int(
            author_trace["raw_offload_rows_before_sort_reduce"]
        )
        item["hash_sample_comparable"] = bool(item["has_raw_row_hash"] and item["has_raw_row_samples"])

    return {
        "goal": "Goal5388",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5388.status_trace_summary_contract.v1",
        "status": "generic_trace_summary_contract_ready__native_full_trace_still_missing",
        "exit_label": "status_trace_summary_api_ready__next_native_stream_must_emit_summary",
        "purpose": (
            "Add a generic active-query status trace summary API so RTDL status "
            "streams can be compared to Goal5387 author trace v2 with row counts, "
            "hashes, and samples rather than count-only evidence."
        ),
        "system_api": {
            "function": "active_query_status_trace_summary_numpy_columns",
            "contract": demo["contract"],
            "app_semantics": demo["app_semantics"],
            "metadata": demo["metadata"],
            "demo_summary": {
                "row_count": demo["row_count"],
                "active_query_count": demo["active_query_count"],
                "status_count_offloading": demo["status_count_offloading"],
                "raw_offload_row_hash": demo["raw_offload_row_hash"],
                "hash_columns": demo["hash_columns"],
                "sample_indices": demo["sample_indices"],
                "samples": demo["samples"],
            },
        },
        "author_trace_v2_target": {
            "source": str(GOAL5387),
            "schema": author_trace["schema"],
            "active_in_queue_size": int(author_trace["active_in_queue_size"]),
            "raw_offload_rows_before_sort_reduce": int(
                author_trace["raw_offload_rows_before_sort_reduce"]
            ),
            "status_count_offloading_append": int(author_trace["status_count_offloading_append"]),
            "raw_offload_row_hash": int(author_batch["raw_offload_row_hash"]),
            "raw_offload_row_sample_point_ids": list(author_batch["raw_offload_row_sample_point_ids"]),
            "raw_offload_row_sample_cell_ids": list(author_batch["raw_offload_row_sample_cell_ids"]),
            "cmin2_initial_hash": int(author_batch["cmin2_initial_hash"]),
            "cmin2_after_ray_hash": int(author_batch["cmin2_after_ray_hash"]),
            "cmin2_after_load_balance_hash": int(author_batch["cmin2_after_load_balance_hash"]),
            "load_balance_input_row_count": int(author_batch["load_balance_input_row_count"]),
            "load_balance_group_count": int(author_batch["load_balance_group_count"]),
            "load_balance_feedback_update_count": int(
                author_batch["load_balance_feedback_update_count"]
            ),
        },
        "current_rtdl_candidate_gap": {
            "candidates": current_candidates,
            "any_row_count_parity": any(item["row_count_parity"] for item in current_candidates),
            "any_hash_sample_comparable": any(
                item["hash_sample_comparable"] for item in current_candidates
            ),
            "gap": (
                "Current full probes still under-count the author offload rows and "
                "do not preserve a full raw row table hash/sample comparable to "
                "Goal5387. The next native stream must emit the generic trace "
                "summary from the actual RTDL raw status rows."
            ),
        },
        "next_native_requirements": {
            "must_emit_generic_trace_summary": True,
            "must_compare_row_count_to_author_v2": True,
            "must_compare_hash_or_samples_to_author_v2": True,
            "must_keep_explicit_lb_fail_closed_until_parity": True,
            "minimum_fields": [
                "row_count",
                "status_count_offloading",
                "active_query_count",
                "raw_offload_row_hash",
                "raw_offload_row_sample_query_or_source_ids",
                "raw_offload_row_sample_cell_ids",
                "status miss/completed/aborted counts",
                "feedback update count",
            ],
        },
        "claim_boundary": {
            "generic_status_trace_summary_api_claimed": True,
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
