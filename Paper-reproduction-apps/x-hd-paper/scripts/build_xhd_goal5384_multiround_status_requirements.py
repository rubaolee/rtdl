from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _roundtrip_demo() -> dict[str, Any]:
    import rtdsl as rt

    result = rt.active_query_status_multiround_reference_numpy_columns(
        query_row_ids=[0, 1, 2],
        active_queue_indices=[10, 11, 12],
        source_ids=[100, 101, 102],
        current_best_sq=[np.inf, np.inf, 1.0],
        current_best_item_ids=[-1, -1, 200],
        round_candidate_tables=[
            {
                "candidate_query_row_ids": [0, 1],
                "candidate_cell_ids": [50, 51],
                "candidate_min_sq": [0.5, 1.0],
                "candidate_max_sq": [3.0, 8.0],
                "candidate_work_counts": [2, 9],
                "candidate_exact_best_sq": [3.0, np.inf],
                "candidate_exact_item_ids": [300, -1],
                "feedback_active_queue_indices": [11],
                "feedback_best_sq": [2.5],
                "feedback_item_ids": [250],
            },
            {
                "candidate_query_row_ids": [1],
                "candidate_cell_ids": [52],
                "candidate_min_sq": [0.25],
                "candidate_max_sq": [3.0],
                "candidate_work_counts": [1],
                "candidate_exact_best_sq": [2.0],
                "candidate_exact_item_ids": [220],
            },
        ],
        heavy_threshold=5,
        return_metadata=True,
    )
    return {
        "contract": result["metadata"]["contract"],
        "app_semantics": result["metadata"]["app_semantics"],
        "native_engine_row_contract": result["metadata"]["native_engine_row_contract"],
        "telemetry": result["telemetry"],
        "offload_active_queue_indices": result["offload_rows"]["active_queue_indices"].tolist(),
        "completed_active_queue_indices": result["completed_rows"]["active_queue_indices"].tolist(),
        "completed_nearest_item_ids": result["completed_rows"]["nearest_item_ids"].tolist(),
        "completed_nearest_distance_sq": result["completed_rows"]["nearest_distance_sq"].tolist(),
    }


def build(output: Path) -> dict[str, Any]:
    results_dir = output.parent
    author_oracle = _load_json(results_dir / "xhd_goal5374_author_lb_status_trace_oracle.json")
    goal5383 = _load_json(results_dir / "xhd_goal5383_full_seeded_active_initial_best_probe_pod.json")

    author_offload_rows = None
    if author_oracle:
        author_offload_rows = author_oracle.get("author_lb_trace", {}).get("raw_offload_rows_before_sort_reduce")

    goal5383_rows = None
    goal5383_ratio = None
    if goal5383:
        comparison = goal5383.get("comparison", {})
        bridge = goal5383.get("active_query_bridge", {})
        bridge_comparison = bridge.get("comparison_to_author", {})
        goal5383_rows = (
            comparison.get("bridge_offload_row_count")
            or bridge_comparison.get("rtdl_bridge_offload_rows")
            or bridge.get("offload_row_count")
        )
        goal5383_ratio = (
            comparison.get("row_ratio_rtdl_div_author")
            or bridge_comparison.get("row_ratio_rtdl_bridge_div_author")
        )

    artifact = {
        "goal": "Goal5384",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5384.multiround_status_requirements.v1",
        "status": "implemented_review_pending",
        "exit_label": "multiround_status_reference_ready__native_or_author_trace_required_for_lb_parity",
        "purpose": (
            "Introduce a generic multi-round active-query status reference and "
            "turn the post-Goal5383 -lb gap into explicit native/oracle requirements."
        ),
        "generic_system_addition": {
            "contract": "generic_active_query_multiround_status_reference_v1",
            "function": "active_query_status_multiround_reference_numpy_columns",
            "owner": "rtdl_core_generic_reference",
            "app_semantics": "none",
            "native_backend_complete": False,
            "explicit_app_option_support_claimed": False,
        },
        "synthetic_multiround_demo": _roundtrip_demo(),
        "author_oracle_carry_forward": {
            "source": "Goal5374",
            "available": author_oracle is not None,
            "active_in_queue_size": (
                None
                if author_oracle is None
                else author_oracle.get("author_lb_trace", {}).get("active_in_queue_size")
            ),
            "offload_rows": author_offload_rows,
            "author_width_bytes": (
                None
                if author_oracle is None
                else author_oracle.get("author_lb_trace", {}).get("raw_offload_rows_author_width_bytes")
            ),
        },
        "latest_rejected_probe_carry_forward": {
            "source": "Goal5383",
            "available": goal5383 is not None,
            "probe": "active-initial-best-prune with local-grid seed",
            "offload_rows": goal5383_rows,
            "row_ratio_rtdl_div_author": goal5383_ratio,
            "row_count_parity": False if goal5383_rows is not None and author_offload_rows is not None else None,
        },
        "requirements_for_next_native_or_author_gate": {
            "must_compare_against_goal5374_author_oracle": True,
            "same_input_pair": "Dragon -> AsianDragon Level-B lb=256 diagnostic",
            "same_active_in_queue_size_required": True,
            "required_fields": [
                "active_query_count",
                "active_in_queue_indices",
                "current_best_state_source",
                "status_count_init",
                "status_count_offloading",
                "status_count_aborted",
                "miss_queue_count",
                "cmax2_mbr_abort_count",
                "raw_offload_rows_before_sort_reduce",
                "offload_row_count",
                "author_width_bytes",
                "row_count_parity_against_goal5374",
            ],
            "rejected_next_work": [
                "single_pass_prune_mode_variants",
                "bridge_vectorization_before_row_parity",
                "scalar_radius_or_raw_kind_count_retries",
                "xhd_specific_core_kernel",
            ],
            "acceptable_next_paths": [
                "native_generic_multiround_status_stream_against_author_oracle",
                "stronger_author_trace_with_per_round_cmin2_and_raw_offload_rows",
                "explicit_lb_fail_closed_closeout_if_parity_is_not_feasible",
            ],
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "Paper-reproduction-apps"
        / "x-hd-paper"
        / "results"
        / "xhd_goal5384_multiround_status_requirements.json",
    )
    args = parser.parse_args()
    artifact = build(args.output)
    print(json.dumps({"output": str(args.output), "status": artifact["status"]}, indent=2))


if __name__ == "__main__":
    main()
