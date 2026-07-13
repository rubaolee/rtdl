from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
DEFAULT_OUTPUT = RESULTS / "xhd_goal5404_bounded_status_state_oracle_gate_pod.json"


def _jsonable_columns(columns: dict[str, Any]) -> dict[str, list[Any]]:
    return {name: np.asarray(values).tolist() for name, values in columns.items()}


def bounded_fixture_inputs() -> dict[str, Any]:
    """Return a small app-shaped, deterministic status-state fixture.

    The values intentionally look like a bounded active-query/offload workload:
    non-contiguous source ids, repeated query rows, candidate cells, heavy/light
    work counts, and feedback rows that both update and do not update current
    best state. The fixture is app-owned and bounded; it is not the Goal5387
    full author trace.
    """

    return {
        "query_row_ids": np.asarray([1010, 1011, 1012, 1013], dtype=np.int64),
        "active_queue_indices": np.asarray([0, 2, 4, 6], dtype=np.int64),
        "source_ids": np.asarray([11168, 210712, 437119, 900001], dtype=np.int64),
        "current_best_sq": np.asarray([25.0, 16.0, 9.0, 36.0], dtype=np.float64),
        "current_best_item_ids": np.asarray([5000, 5001, 5002, 5003], dtype=np.int64),
        "candidate_query_row_ids": np.asarray([1010, 1010, 1011, 1012, 1013, 1011], dtype=np.int64),
        "candidate_cell_ids": np.asarray([2924, 3001, 17, 18, 42, 99], dtype=np.int64),
        "candidate_min_sq": np.asarray([4.0, 2.0, 6.0, 1.0, 9.0, 7.0], dtype=np.float64),
        "candidate_max_sq": np.asarray([40.0, 10.0, 30.0, 20.0, 11.0, 31.0], dtype=np.float64),
        "candidate_work_counts": np.asarray([64, 4, 65, 17, 2, 80], dtype=np.uint64),
        "heavy_threshold": 16,
        "feedback_active_queue_indices": np.asarray([0, 2, 4, 6], dtype=np.int64),
        "feedback_best_sq": np.asarray([20.0, 16.0, 10.0, 100.0], dtype=np.float64),
        "feedback_item_ids": np.asarray([4000, 4000, 4002, 9000], dtype=np.int64),
        "row_capacity": 8,
    }


def expected_oracle_columns() -> dict[str, list[Any]]:
    return {
        "active_queue_indices": [0, 2, 4, 2],
        "query_row_ids": [1010, 1011, 1012, 1011],
        "source_ids": [11168, 210712, 437119, 210712],
        "cell_ids": [2924, 17, 18, 99],
        "status_codes": [2, 2, 2, 2],
        "transition_phase_codes": [1, 1, 1, 1],
        "current_best_before_sq": [25.0, 16.0, 9.0, 16.0],
        "current_best_after_sq": [20.0, 16.0, 9.0, 16.0],
    }


def expected_telemetry() -> dict[str, Any]:
    return {
        "active_query_count": 4,
        "candidate_row_count": 6,
        "raw_offload_row_count": 4,
        "status_count_offloading": 4,
        "feedback_update_count": 2,
        "feedback_row_count": 4,
        "overflowed": False,
    }


def _trace_summary(columns: dict[str, Any]) -> dict[str, Any]:
    import rtdsl as rt

    return rt.active_query_status_trace_summary_numpy_columns(
        columns,
        active_queue_indices=[0, 2, 4, 6],
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=(
            "source_ids",
            "cell_ids",
            "active_queue_indices",
            "query_row_ids",
            "status_codes",
            "transition_phase_codes",
        ),
        return_metadata=True,
    )


def _run_native(row_capacity: int | None = None) -> dict[str, Any]:
    import rtdsl as rt

    fixture = bounded_fixture_inputs()
    if row_capacity is not None:
        fixture = dict(fixture)
        fixture["row_capacity"] = int(row_capacity)
    return rt.active_query_status_state_machine_smoke_native(**fixture)


def _build_overflow_probe() -> dict[str, Any]:
    try:
        _run_native(row_capacity=3)
    except RuntimeError as exc:
        message = str(exc)
        return {
            "raised": True,
            "message_contains_fail_closed_overflow": "fail_closed_overflow" in message,
            "message": message,
        }
    return {
        "raised": False,
        "message_contains_fail_closed_overflow": False,
        "message": "overflow probe unexpectedly succeeded",
    }


def build_summary() -> dict[str, Any]:
    result = _run_native()
    observed_columns = _jsonable_columns(result["columns"])
    expected_columns = expected_oracle_columns()
    observed_trace = _trace_summary(observed_columns)
    expected_trace = _trace_summary(expected_columns)
    observed_telemetry = dict(result["telemetry"])
    expected_tel = expected_telemetry()
    overflow_probe = _build_overflow_probe()

    comparisons = {
        "row_count_matched": int(observed_trace["row_count"]) == int(expected_trace["row_count"]),
        "raw_hash_matched": int(observed_trace["raw_offload_row_hash"]) == int(expected_trace["raw_offload_row_hash"]),
        "sample_matched": observed_trace["samples"] == expected_trace["samples"],
        "status_count_offloading_matched": int(observed_telemetry["status_count_offloading"]) == int(expected_tel["status_count_offloading"]),
        "feedback_update_count_matched": int(observed_telemetry["feedback_update_count"]) == int(expected_tel["feedback_update_count"]),
        "feedback_row_count_matched": int(observed_telemetry["feedback_row_count"]) == int(expected_tel["feedback_row_count"]),
        "current_best_before_matched": observed_columns["current_best_before_sq"] == expected_columns["current_best_before_sq"],
        "current_best_after_matched": observed_columns["current_best_after_sq"] == expected_columns["current_best_after_sq"],
        "overflow_fail_closed_matched": bool(
            overflow_probe["raised"] and overflow_probe["message_contains_fail_closed_overflow"]
        ),
    }
    matched = all(comparisons.values())
    return {
        "goal": "Goal5404",
        "schema": "rtdl.paper_reproduction.xhd.goal5404.bounded_status_state_oracle_gate.v1",
        "status": "bounded_status_state_oracle_passed" if matched else "bounded_status_state_oracle_failed",
        "matched": matched,
        "fixture": "bounded_app_shaped_four_active_queries_four_offload_rows_two_feedback_updates",
        "native_result_metadata": {key: value for key, value in result.items() if key != "columns"},
        "expected_columns": expected_columns,
        "observed_columns": observed_columns,
        "expected_telemetry": expected_tel,
        "observed_telemetry": observed_telemetry,
        "expected_trace_summary": expected_trace,
        "observed_trace_summary": observed_trace,
        "comparisons": comparisons,
        "overflow_probe": overflow_probe,
        "next_gate_decision": {
            "bounded_oracle_gate_passed": matched,
            "full_goal5387_gate_authorized_by_goal5404": False,
            "full_gate_reason": (
                "This bounded oracle proves row/hash/status/feedback mechanics "
                "on an app-shaped fixture. Full Goal5387 author-trace parity "
                "still requires a separate gate on the real full-public stream."
            ),
            "recommended_next_goal_if_passed": "Goal5405_status_state_real_stream_bridge_or_full_gate_readiness",
        },
        "claim_boundary": {
            "bounded_status_state_oracle_claimed": True,
            "generic_native_status_state_smoke_reused": True,
            "explicit_lb_support_claimed": False,
            "goal5387_row_count_parity_claimed": False,
            "goal5387_hash_sample_parity_claimed": False,
            "goal5387_feedback_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    payload = build_summary()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
