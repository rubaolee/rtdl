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
GOAL5393_TARGET = RESULTS / "xhd_goal5393_lb_status_stream_target_design.json"
GOAL5394_SPEC = RESULTS / "xhd_goal5394_full_cover_delta_status_probe.json"
DEFAULT_OUTPUT = RESULTS / "xhd_goal5405_full_cover_delta_status_bridge_pod.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def target_shape_from_prior_artifacts() -> dict[str, Any]:
    goal5393 = _read_json(GOAL5393_TARGET)
    goal5394 = _read_json(GOAL5394_SPEC)
    target = goal5393["target_selection"]
    selected = goal5394["selected_surface"]
    return {
        "author_rows_per_active": int(target["author_rows_per_active"]),
        "selected_rows_per_active": int(target["selected_rows_per_active"]),
        "missing_rows_per_active": int(target["missing_rows_per_active_if_exact"]),
        "selected_surface_rows": int(target["selected_surface_rows"]),
        "missing_rows_to_author": int(target["missing_rows_to_author"]),
        "goal5394_shape_matches_target": bool(
            selected["rows_per_active"] == target["selected_rows_per_active"]
            and selected["missing_rows_per_active"] == target["missing_rows_per_active_if_exact"]
        ),
    }


def bounded_full_cover_delta_fixture(*, active_count: int = 2) -> dict[str, Any]:
    """Build a small 56+6 rows/active fixture from the Goal5393/5394 target.

    The fixture uses the author-derived row shape, but not author constants in
    RTDL core. It is app-owned and bounded: two active queries, 56 base rows per
    active query, and 6 generic delta rows per active query.
    """

    target = target_shape_from_prior_artifacts()
    base_rows = int(target["selected_rows_per_active"])
    delta_rows = int(target["missing_rows_per_active"])
    query_row_ids = np.arange(active_count, dtype=np.int64)
    active_queue_indices = np.arange(active_count, dtype=np.int64)
    source_ids = np.asarray([11168, 210712, 437119, 900001][:active_count], dtype=np.int64)
    current_best_sq = np.full(active_count, np.inf, dtype=np.float64)
    current_best_item_ids = np.full(active_count, -1, dtype=np.int64)

    candidate_query_ids: list[int] = []
    candidate_cell_ids: list[int] = []
    candidate_min_sq: list[float] = []
    candidate_max_sq: list[float] = []
    candidate_work_counts: list[int] = []
    row_source: list[str] = []
    for query_id in range(active_count):
        for local in range(base_rows):
            candidate_query_ids.append(query_id)
            candidate_cell_ids.append(100000 + query_id * 1000 + local)
            candidate_min_sq.append(float(local + 1))
            candidate_max_sq.append(float(local + 2))
            candidate_work_counts.append(9)
            row_source.append("base")
    for query_id in range(active_count):
        for local in range(delta_rows):
            candidate_query_ids.append(query_id)
            candidate_cell_ids.append(900000 + query_id * 1000 + local)
            candidate_min_sq.append(float(100 + local))
            candidate_max_sq.append(float(101 + local))
            candidate_work_counts.append(9)
            row_source.append("delta")

    return {
        "target_shape": target,
        "row_source": row_source,
        "native_inputs": {
            "query_row_ids": query_row_ids,
            "active_queue_indices": active_queue_indices,
            "source_ids": source_ids,
            "current_best_sq": current_best_sq,
            "current_best_item_ids": current_best_item_ids,
            "candidate_query_row_ids": np.asarray(candidate_query_ids, dtype=np.int64),
            "candidate_cell_ids": np.asarray(candidate_cell_ids, dtype=np.int64),
            "candidate_min_sq": np.asarray(candidate_min_sq, dtype=np.float64),
            "candidate_max_sq": np.asarray(candidate_max_sq, dtype=np.float64),
            "candidate_work_counts": np.asarray(candidate_work_counts, dtype=np.uint64),
            "heavy_threshold": 5,
            "row_capacity": len(candidate_query_ids),
            "feedback_active_queue_indices": np.asarray([], dtype=np.int64),
            "feedback_best_sq": np.asarray([], dtype=np.float64),
            "feedback_item_ids": np.asarray([], dtype=np.int64),
        },
    }


def expected_columns_from_fixture(fixture: dict[str, Any]) -> dict[str, list[Any]]:
    native_inputs = fixture["native_inputs"]
    query_ids = native_inputs["query_row_ids"]
    active_queues = native_inputs["active_queue_indices"]
    sources = native_inputs["source_ids"]
    current_best = native_inputs["current_best_sq"]
    index_by_query = {int(query): idx for idx, query in enumerate(query_ids)}
    active_out: list[int] = []
    query_out: list[int] = []
    source_out: list[int] = []
    cell_out: list[int] = []
    before_out: list[float] = []
    after_out: list[float] = []
    for query_id, cell_id, work_count in zip(
        native_inputs["candidate_query_row_ids"],
        native_inputs["candidate_cell_ids"],
        native_inputs["candidate_work_counts"],
    ):
        if int(work_count) <= int(native_inputs["heavy_threshold"]):
            continue
        offset = index_by_query[int(query_id)]
        active_out.append(int(active_queues[offset]))
        query_out.append(int(query_ids[offset]))
        source_out.append(int(sources[offset]))
        cell_out.append(int(cell_id))
        before_out.append(float(current_best[offset]))
        after_out.append(float(current_best[offset]))

    return {
        "active_queue_indices": active_out,
        "query_row_ids": query_out,
        "source_ids": source_out,
        "cell_ids": cell_out,
        "status_codes": [2] * len(cell_out),
        "transition_phase_codes": [1] * len(cell_out),
        "current_best_before_sq": before_out,
        "current_best_after_sq": after_out,
    }


def _jsonable_columns(columns: dict[str, Any]) -> dict[str, list[Any]]:
    return {name: np.asarray(values).tolist() for name, values in columns.items()}


def _trace_summary(columns: dict[str, Any], active_count: int) -> dict[str, Any]:
    import rtdsl as rt

    return rt.active_query_status_trace_summary_numpy_columns(
        columns,
        active_queue_indices=np.arange(active_count, dtype=np.int64),
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


def _multiround_reference_shape(fixture: dict[str, Any]) -> dict[str, Any]:
    import rtdsl as rt

    native_inputs = fixture["native_inputs"]
    target = fixture["target_shape"]
    active_count = int(native_inputs["query_row_ids"].size)
    base_rows = int(target["selected_rows_per_active"])
    delta_rows = int(target["missing_rows_per_active"])
    base_count = active_count * base_rows
    base_table = {
        "candidate_query_row_ids": native_inputs["candidate_query_row_ids"][:base_count],
        "candidate_cell_ids": native_inputs["candidate_cell_ids"][:base_count],
        "candidate_min_sq": native_inputs["candidate_min_sq"][:base_count],
        "candidate_max_sq": native_inputs["candidate_max_sq"][:base_count],
        "candidate_work_counts": native_inputs["candidate_work_counts"][:base_count],
    }
    delta_table = {
        "candidate_query_row_ids": native_inputs["candidate_query_row_ids"][base_count:],
        "candidate_cell_ids": native_inputs["candidate_cell_ids"][base_count:],
        "candidate_min_sq": native_inputs["candidate_min_sq"][base_count:],
        "candidate_max_sq": native_inputs["candidate_max_sq"][base_count:],
        "candidate_work_counts": native_inputs["candidate_work_counts"][base_count:],
    }
    result = rt.active_query_status_multiround_reference_numpy_columns(
        native_inputs["query_row_ids"],
        native_inputs["active_queue_indices"],
        native_inputs["source_ids"],
        native_inputs["current_best_sq"],
        native_inputs["current_best_item_ids"],
        [base_table, delta_table],
        heavy_threshold=int(native_inputs["heavy_threshold"]),
        return_metadata=True,
    )
    telemetry = result["telemetry"]
    return {
        "contract": result["metadata"]["contract"],
        "app_semantics": result["metadata"]["app_semantics"],
        "raw_offload_rows_before_sort_reduce": int(telemetry["raw_offload_rows_before_sort_reduce"]),
        "total_feedback_updates": int(telemetry["feedback_updates_applied"]),
        "rounds": telemetry["rounds"],
        "expected_base_rows": int(base_count),
        "expected_delta_rows": int(active_count * delta_rows),
        "expected_total_rows": int(active_count * (base_rows + delta_rows)),
    }


def _run_native(fixture: dict[str, Any], *, row_capacity: int | None = None) -> dict[str, Any]:
    import rtdsl as rt

    inputs = dict(fixture["native_inputs"])
    if row_capacity is not None:
        inputs["row_capacity"] = int(row_capacity)
    return rt.active_query_status_state_machine_smoke_native(**inputs)


def _overflow_probe(fixture: dict[str, Any]) -> dict[str, Any]:
    capacity = int(fixture["native_inputs"]["row_capacity"]) - 1
    try:
        _run_native(fixture, row_capacity=capacity)
    except RuntimeError as exc:
        message = str(exc)
        return {
            "raised": True,
            "capacity": capacity,
            "message_contains_fail_closed_overflow": "fail_closed_overflow" in message,
            "message": message,
        }
    return {
        "raised": False,
        "capacity": capacity,
        "message_contains_fail_closed_overflow": False,
        "message": "overflow probe unexpectedly succeeded",
    }


def build_summary() -> dict[str, Any]:
    fixture = bounded_full_cover_delta_fixture(active_count=2)
    expected_columns = expected_columns_from_fixture(fixture)
    expected_trace = _trace_summary(expected_columns, active_count=2)
    reference_shape = _multiround_reference_shape(fixture)
    native = _run_native(fixture)
    observed_columns = _jsonable_columns(native["columns"])
    observed_trace = _trace_summary(observed_columns, active_count=2)
    overflow_probe = _overflow_probe(fixture)
    target = fixture["target_shape"]

    comparisons = {
        "goal5394_shape_matches_target": bool(target["goal5394_shape_matches_target"]),
        "native_row_count_matched_expected": int(observed_trace["row_count"]) == int(expected_trace["row_count"]),
        "native_hash_matched_expected": int(observed_trace["raw_offload_row_hash"]) == int(expected_trace["raw_offload_row_hash"]),
        "native_sample_matched_expected": observed_trace["samples"] == expected_trace["samples"],
        "native_status_count_matched_expected": int(native["telemetry"]["status_count_offloading"]) == int(expected_trace["status_count_offloading"]),
        "native_feedback_count_zero_matched": int(native["telemetry"]["feedback_update_count"]) == 0,
        "native_current_best_after_matched": observed_columns["current_best_after_sq"] == expected_columns["current_best_after_sq"],
        "multiround_reference_total_rows_matched": int(reference_shape["raw_offload_rows_before_sort_reduce"]) == int(expected_trace["row_count"]),
        "overflow_fail_closed_matched": bool(
            overflow_probe["raised"] and overflow_probe["message_contains_fail_closed_overflow"]
        ),
    }
    matched = all(comparisons.values())
    return {
        "goal": "Goal5405",
        "schema": "rtdl.paper_reproduction.xhd.goal5405.full_cover_delta_status_bridge.v1",
        "status": "bounded_full_cover_delta_status_bridge_passed" if matched else "bounded_full_cover_delta_status_bridge_failed",
        "matched": matched,
        "fixture": "bounded_two_active_queries_56_base_plus_6_delta_rows_per_active",
        "target_shape": target,
        "expected_rows": {
            "active_count": 2,
            "base_rows_per_active": int(target["selected_rows_per_active"]),
            "delta_rows_per_active": int(target["missing_rows_per_active"]),
            "total_rows_per_active": int(target["author_rows_per_active"]),
            "expected_total_rows": int(expected_trace["row_count"]),
        },
        "expected_trace_summary": expected_trace,
        "observed_trace_summary": observed_trace,
        "multiround_reference_shape": reference_shape,
        "native_result_metadata": {key: value for key, value in native.items() if key != "columns"},
        "comparisons": comparisons,
        "overflow_probe": overflow_probe,
        "next_gate_decision": {
            "bounded_full_cover_delta_bridge_passed": matched,
            "full_goal5387_gate_authorized_by_goal5405": False,
            "reason_full_gate_still_pending": (
                "The bounded 56+6 rows/active bridge matches a small full-cover-"
                "delta-shaped fixture. Full Goal5387 parity still requires "
                "generating the real full-public row stream and comparing "
                "27,133,990 rows plus hash/status/feedback against the author oracle."
            ),
            "recommended_next_goal_if_passed": "Goal5406_real_full_cover_surface_or_full_goal5387_stream_gate",
        },
        "claim_boundary": {
            "bounded_full_cover_delta_bridge_claimed": True,
            "generic_multiround_reference_shape_reused": True,
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
