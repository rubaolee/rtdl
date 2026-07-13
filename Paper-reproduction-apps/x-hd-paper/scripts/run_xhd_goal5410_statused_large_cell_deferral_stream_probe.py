from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import rtdsl as rt


DEFAULT_OUTPUT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5410_statused_large_cell_deferral_stream_probe.json"
)


def synthetic_statused_deferral_fixture() -> dict[str, Any]:
    """Return an app-neutral fixture for the generic active-query status stream."""

    return {
        "query_row_ids": np.asarray([0, 1, 2, 3, 4], dtype=np.int64),
        "active_queue_indices": np.asarray([10, 11, 12, 13, 14], dtype=np.int64),
        "source_ids": np.asarray([100, 101, 102, 103, 104], dtype=np.int64),
        "current_best_sq": np.asarray([10.0, np.inf, np.inf, 8.0, 5.0], dtype=np.float64),
        "current_best_item_ids": np.asarray([1000, -1, -1, 1003, 1004], dtype=np.int64),
        "candidate_query_row_ids": np.asarray([0, 1, 1, 3, 4], dtype=np.int64),
        "candidate_cell_ids": np.asarray([50, 51, 52, 53, 54], dtype=np.int64),
        "candidate_min_sq": np.asarray([1.0, 1.0, 2.0, 0.2, 6.0], dtype=np.float64),
        "candidate_max_sq": np.asarray([4.0, 10.0, 8.0, 1.5, 7.0], dtype=np.float64),
        "candidate_work_counts": np.asarray([3, 9, 8, 2, 1], dtype=np.int64),
        "candidate_exact_best_sq": np.asarray([2.0, np.inf, np.inf, 0.5, 4.0], dtype=np.float64),
        "candidate_exact_item_ids": np.asarray([900, -1, -1, 903, 904], dtype=np.int64),
        "heavy_threshold": 5,
        "radius_sq": 100.0,
        "global_bound_sq": 2.0,
    }


def _tolist_columns(columns: dict[str, np.ndarray]) -> dict[str, list[Any]]:
    return {name: values.tolist() for name, values in columns.items()}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if np.isposinf(value):
            return "inf"
        if np.isneginf(value):
            return "-inf"
        if np.isnan(value):
            return "nan"
        return value
    return value


def build_payload() -> dict[str, Any]:
    fixture = synthetic_statused_deferral_fixture()
    result = rt.active_query_status_machine_reference_numpy_columns(
        query_row_ids=fixture["query_row_ids"],
        active_queue_indices=fixture["active_queue_indices"],
        source_ids=fixture["source_ids"],
        current_best_sq=fixture["current_best_sq"],
        current_best_item_ids=fixture["current_best_item_ids"],
        candidate_query_row_ids=fixture["candidate_query_row_ids"],
        candidate_cell_ids=fixture["candidate_cell_ids"],
        candidate_min_sq=fixture["candidate_min_sq"],
        candidate_max_sq=fixture["candidate_max_sq"],
        candidate_work_counts=fixture["candidate_work_counts"],
        candidate_exact_best_sq=fixture["candidate_exact_best_sq"],
        candidate_exact_item_ids=fixture["candidate_exact_item_ids"],
        heavy_threshold=fixture["heavy_threshold"],
        radius_sq=fixture["radius_sq"],
        global_bound_sq=fixture["global_bound_sq"],
        return_metadata=True,
    )
    summary = rt.active_query_status_trace_summary_numpy_columns(
        result["offload_rows"],
        active_queue_indices=fixture["active_queue_indices"],
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=("active_queue_indices", "source_ids", "cell_ids", "work_counts"),
        return_metadata=True,
    )
    telemetry = result["telemetry"]
    expected = {
        "offload_row_count": 2,
        "completed_row_count": 2,
        "miss_row_count": 1,
        "aborted_row_count": 1,
        "pruned_by_radius_or_current_best_count": 1,
    }
    matched = all(int(telemetry[name]) == value for name, value in expected.items())
    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5410.statused_large_cell_deferral_stream_probe.v1",
        "goal": "Goal5410",
        "status": "synthetic_app_neutral_status_stream_gate_passed__bounded_xhd_gate_pending",
        "matched": bool(matched),
        "generic_semantic": {
            "name": "statused_large_cell_deferral_stream",
            "app_semantics": "none",
            "contract": rt.ACTIVE_QUERY_STATUS_MACHINE_CONTRACT,
            "summary_contract": rt.ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT,
            "native_execution_claimed": False,
        },
        "fixture": {
            "name": "synthetic_non_app_statused_large_cell_deferral_stream",
            "active_query_count": int(fixture["query_row_ids"].size),
            "candidate_row_count": int(fixture["candidate_query_row_ids"].size),
            "heavy_threshold": int(fixture["heavy_threshold"]),
            "radius_sq": float(fixture["radius_sq"]),
            "global_bound_sq": float(fixture["global_bound_sq"]),
            "contains_xhd_or_paper_semantics": False,
        },
        "expected_counts": expected,
        "observed_telemetry": {
            name: (int(value) if isinstance(value, (np.integer, int, bool)) else value)
            for name, value in telemetry.items()
        },
        "offload_rows": _tolist_columns(result["offload_rows"]),
        "completed_rows": _tolist_columns(result["completed_rows"]),
        "miss_rows": _tolist_columns(result["miss_rows"]),
        "aborted_rows": _tolist_columns(result["aborted_rows"]),
        "trace_summary": summary,
        "decision": {
            "synthetic_app_neutral_gate_passed": bool(matched),
            "bounded_xhd_author_sample_row_gate_passed": False,
            "full_goal5387_row_identity_gate_passed": False,
            "explicit_lb_support_authorized": False,
            "recommended_next_goal": "Goal5411_bounded_xhd_statused_deferral_sample_row_gate",
        },
        "claim_boundary": {
            "synthetic_status_stream_claimed": True,
            "bounded_xhd_author_sample_recovery_claimed": False,
            "full_goal5387_row_identity_parity_claimed": False,
            "explicit_lb_support_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }
    return _json_safe(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "status": payload["status"], "matched": payload["matched"]}, indent=2))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
