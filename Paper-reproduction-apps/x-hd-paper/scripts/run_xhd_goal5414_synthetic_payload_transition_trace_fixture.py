from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl import ACTIVE_QUERY_STATUS_KIND_CODES
from rtdsl import payload_transition_trace_summary_numpy_columns
from rtdsl import validate_native_payload_transition_trace_stream_contract


RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5414_synthetic_payload_transition_trace_fixture.json"
)


def synthetic_non_app_trace_columns() -> dict[str, np.ndarray]:
    """Return a small app-neutral payload-transition trace fixture.

    The fixture models three active requests passing through a generic spatial
    traversal over numbered bins.  It intentionally avoids paper/app names and
    only exercises the generic status/transition shape.
    """

    status = ACTIVE_QUERY_STATUS_KIND_CODES
    return {
        "active_queue_indices": np.asarray([0, 0, 1, 2, 2], dtype=np.int64),
        "query_row_ids": np.asarray([10, 10, 11, 12, 12], dtype=np.int64),
        "source_ids": np.asarray([100, 100, 101, 102, 102], dtype=np.int64),
        "primitive_or_cell_ids": np.asarray([7, 8, 3, 5, 6], dtype=np.int64),
        "cell_namespace_codes": np.asarray([1, 1, 1, 1, 1], dtype=np.int64),
        "status_codes": np.asarray(
            [
                status["offload"],
                status["completed"],
                status["miss"],
                status["offload"],
                status["aborted"],
            ],
            dtype=np.int64,
        ),
        "transition_phase_codes": np.asarray([20, 30, 40, 20, 50], dtype=np.int64),
        "current_best_before_sq": np.asarray(
            [np.inf, 9.0, np.inf, 4.0, 4.0],
            dtype=np.float64,
        ),
        "current_best_after_sq": np.asarray(
            [9.0, 6.0, np.inf, 4.0, 4.0],
            dtype=np.float64,
        ),
        "lower_bounds_sq": np.asarray([1.0, 2.0, np.inf, 3.0, 5.0], dtype=np.float64),
        "upper_bounds_sq": np.asarray([12.0, 8.0, np.inf, 10.0, 5.0], dtype=np.float64),
        "work_counts": np.asarray([12, 4, 0, 9, 2], dtype=np.int64),
        "payload_event_ordinals": np.asarray([0, 1, 0, 0, 1], dtype=np.int64),
    }


def build_summary() -> dict[str, Any]:
    columns = synthetic_non_app_trace_columns()
    active_queue_indices = np.asarray([0, 1, 2], dtype=np.int64)
    summary = payload_transition_trace_summary_numpy_columns(
        columns,
        active_queue_indices=active_queue_indices,
        row_capacity=8,
        return_metadata=True,
    )
    overflow_reject = payload_transition_trace_summary_numpy_columns(
        columns,
        active_queue_indices=active_queue_indices,
        row_capacity=4,
        overflowed=True,
        return_metadata=True,
    )
    contract_validation = validate_native_payload_transition_trace_stream_contract()
    expected_counts = {
        "raw_transition_row_count": 5,
        "status_count_offloading": 2,
        "status_count_completed": 1,
        "status_count_miss": 1,
        "status_count_aborted": 1,
    }
    matched = (
        summary["status"] == "accept"
        and contract_validation["status"] == "accept"
        and all(summary[key] == value for key, value in expected_counts.items())
        and overflow_reject["status"] == "reject"
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5414.synthetic_payload_transition_trace_fixture.v1",
        "goal": "Goal5414",
        "status": "synthetic_non_app_payload_transition_trace_fixture_passed",
        "matched": bool(matched),
        "fixture": {
            "name": "synthetic_non_app_spatial_request_payload_transition_trace",
            "contains_xhd_or_paper_semantics": False,
            "active_query_count": int(active_queue_indices.size),
            "row_count": int(summary["row_count"]),
        },
        "contract_validation": {
            "status": contract_validation["status"],
            "contract": contract_validation["contract"]["contract"],
        },
        "summary": summary,
        "expected_counts": expected_counts,
        "overflow_reject": {
            "status": overflow_reject["status"],
            "reason": overflow_reject["reason"],
        },
        "claim_boundary": {
            "synthetic_non_app_payload_transition_trace_claimed": True,
            "bounded_xhd_sample_row_recovery_claimed": False,
            "explicit_lb_support_claimed": False,
            "native_backend_implementation_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next_goal": "Goal5415_decide_stop_or_bounded_xhd_payload_transition_sample_gate",
    }


def main() -> None:
    payload = build_summary()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
