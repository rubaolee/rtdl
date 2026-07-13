from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _jsonable_columns(columns: dict[str, object]) -> dict[str, list[object]]:
    return {name: values.tolist() for name, values in columns.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_goal5402_status_state_machine_native_smoke_pod.json"
        ),
    )
    args = parser.parse_args()

    import numpy as np
    import rtdsl as rt

    result = rt.active_query_status_state_machine_smoke_native(
        query_row_ids=np.asarray([10, 11, 12], dtype=np.int64),
        active_queue_indices=np.asarray([0, 1, 2], dtype=np.int64),
        source_ids=np.asarray([100, 101, 102], dtype=np.int64),
        current_best_sq=np.asarray([5.0, 7.0, 9.0], dtype=np.float64),
        current_best_item_ids=np.asarray([500, 501, 502], dtype=np.int64),
        candidate_query_row_ids=np.asarray([10, 11, 12], dtype=np.int64),
        candidate_cell_ids=np.asarray([50, 51, 52], dtype=np.int64),
        candidate_min_sq=np.asarray([1.0, 2.0, 3.0], dtype=np.float64),
        candidate_max_sq=np.asarray([6.0, 3.0, 10.0], dtype=np.float64),
        candidate_work_counts=np.asarray([6, 2, 9], dtype=np.uint64),
        heavy_threshold=5,
        row_capacity=4,
        feedback_active_queue_indices=np.asarray([1], dtype=np.int64),
        feedback_best_sq=np.asarray([6.5], dtype=np.float64),
        feedback_item_ids=np.asarray([601], dtype=np.int64),
    )

    columns = result["columns"]
    observed = {
        "valid_count": int(result["valid_count"]),
        "attempted_count": int(result["attempted_count"]),
        "active_queue_indices": columns["active_queue_indices"].astype(np.int64).tolist(),
        "query_row_ids": columns["query_row_ids"].astype(np.int64).tolist(),
        "source_ids": columns["source_ids"].astype(np.int64).tolist(),
        "cell_ids": columns["cell_ids"].astype(np.int64).tolist(),
        "status_codes": columns["status_codes"].astype(np.int64).tolist(),
        "transition_phase_codes": columns["transition_phase_codes"].astype(np.int64).tolist(),
        "current_best_before_sq": columns["current_best_before_sq"].astype(np.float64).tolist(),
        "current_best_after_sq": columns["current_best_after_sq"].astype(np.float64).tolist(),
        "telemetry": result["telemetry"],
    }
    expected = {
        "valid_count": 2,
        "attempted_count": 2,
        "active_queue_indices": [0, 2],
        "query_row_ids": [10, 12],
        "source_ids": [100, 102],
        "cell_ids": [50, 52],
        "status_codes": [2, 2],
        "transition_phase_codes": [1, 1],
        "current_best_before_sq": [5.0, 9.0],
        "current_best_after_sq": [5.0, 9.0],
        "telemetry": {
            "raw_offload_row_count": 2,
            "status_count_offloading": 2,
            "feedback_update_count": 1,
            "feedback_row_count": 1,
            "overflowed": False,
        },
    }
    matched = (
        observed["valid_count"] == expected["valid_count"]
        and observed["attempted_count"] == expected["attempted_count"]
        and observed["active_queue_indices"] == expected["active_queue_indices"]
        and observed["query_row_ids"] == expected["query_row_ids"]
        and observed["source_ids"] == expected["source_ids"]
        and observed["cell_ids"] == expected["cell_ids"]
        and observed["status_codes"] == expected["status_codes"]
        and observed["transition_phase_codes"] == expected["transition_phase_codes"]
        and observed["current_best_before_sq"] == expected["current_best_before_sq"]
        and observed["current_best_after_sq"] == expected["current_best_after_sq"]
        and observed["telemetry"]["raw_offload_row_count"] == expected["telemetry"]["raw_offload_row_count"]
        and observed["telemetry"]["status_count_offloading"] == expected["telemetry"]["status_count_offloading"]
        and observed["telemetry"]["feedback_update_count"] == expected["telemetry"]["feedback_update_count"]
        and observed["telemetry"]["feedback_row_count"] == expected["telemetry"]["feedback_row_count"]
        and observed["telemetry"]["overflowed"] == expected["telemetry"]["overflowed"]
    )

    summary = {
        "goal": "Goal5402",
        "schema": "rtdl.paper_reproduction.xhd.goal5402.status_state_machine_native_smoke.v1",
        "status": "native_status_state_machine_smoke_passed" if matched else "native_status_state_machine_smoke_failed",
        "matched": matched,
        "fixture": "synthetic_three_active_queries_two_heavy_candidates_one_feedback_update",
        "expected": expected,
        "observed": observed,
        "native_result_metadata": {key: value for key, value in result.items() if key != "columns"},
        "columns": _jsonable_columns(columns),
        "claim_boundary": {
            "generic_native_status_state_smoke_claimed": True,
            "synthetic_non_app_gate_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
