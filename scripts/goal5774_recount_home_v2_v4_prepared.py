#!/usr/bin/env python3
"""Independent Home recount for Goal5774; imports no measured implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


LANES = (
    "triangle__rt_1a2", "triangle__rt_2a1", "raydb__q21",
    "librts__range_rows", "librts__overlap_filter", "rtnn__ranked_window",
    "rtdbscan__components", "xhd__global_witness",
    "rayjoin__point_location", "rayjoin__segment_pairs",
    "rayjoin__grouped_events", "rtbh__force", "particle__cell_transition",
)
METHODS = (
    "v2_direct_true_optix_backport",
    "v4_restricted_callback_true_optix",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"]
        == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def recount(result_path: Path, output_path: Path) -> Path:
    if output_path.exists():
        raise FileExistsError(output_path)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if (
        result["schema"] != "rtdl.goal5774.home_v2_v4_prepared_functional.v1"
        or tuple(result["methods"]) != METHODS
        or result["lane_count"] != 13
        or result["owner_count"] != 26
        or len(result["records"]) != 26
        or result["formal_worker"] is not False
        or result["registered_performance_observation"] is not False
        or result["v3_required_or_executed"] is not False
        or result["pod_used_or_authorized"] is not False
    ):
        raise RuntimeError("Home result envelope failed independent admission")

    by_key: dict[tuple[str, str], dict[str, object]] = {}
    receipt_native_shas: set[str] = set()
    activation_seconds: list[float] = []
    measured_seconds: list[float] = []
    for row in result["records"]:
        key = (str(row["lane_id"]), str(row["method"]))
        if (
            key in by_key
            or key[0] not in LANES
            or key[1] not in METHODS
            or row["prepare_count"] != 1
            or row["activation_count"] != 1
            or row["execute_count"] != 2
            or len(row["calls"]) != 2
        ):
            raise RuntimeError("Home owner shape failed independent admission")
        by_key[key] = row
        activation = row["activation"]
        calls = row["calls"]
        if (
            activation["matched"] is not True
            or activation["activation_only"] is not True
            or activation["registered_performance_observation"] is not False
            or set(call["call_index"] for call in calls) != {0, 1}
            or any(call["matched"] is not True for call in calls)
            or any(call["activation_only"] is not False for call in calls)
            or any(call["registered_performance_observation"] is not True
                   for call in calls)
        ):
            raise RuntimeError("Home activation/call role failed admission")
        digests = {activation["dynamic_input_sha256"]}
        digests.update(call["dynamic_input_sha256"] for call in calls)
        if len(digests) != 3:
            raise RuntimeError("Home owner did not consume three distinct requests")
        for call in (activation, *calls):
            receipt = call["behavioral_traversal_receipt"]
            if not _receipt_ok(receipt):
                raise RuntimeError("Home behavioral receipt failed admission")
            receipt_native_shas.add(str(receipt["provider_library_sha256"]))
        activation_value = float(activation["activation_seconds"])
        if not math.isfinite(activation_value) or activation_value <= 0.0:
            raise RuntimeError("Home activation seconds invalid")
        activation_seconds.append(activation_value)
        for call in calls:
            value = float(call["registered_prepared_execution_seconds"])
            if not math.isfinite(value) or value <= 0.0:
                raise RuntimeError("Home measured-shape seconds invalid")
            measured_seconds.append(value)

    if set(by_key) != {(lane, method) for lane in LANES for method in METHODS}:
        raise RuntimeError("Home owner matrix incomplete")
    for lane in LANES:
        v2 = by_key[(lane, METHODS[0])]
        v4 = by_key[(lane, METHODS[1])]
        if v2["activation"]["dynamic_input_sha256"] != v4["activation"]["dynamic_input_sha256"]:
            raise RuntimeError("Home cross-method activation input mismatch")
        if v2["activation"]["output_sha256"] != v4["activation"]["output_sha256"]:
            raise RuntimeError("Home cross-method activation output mismatch")
        for index in (0, 1):
            left, right = v2["calls"][index], v4["calls"][index]
            if (
                left["dynamic_input_sha256"] != right["dynamic_input_sha256"]
                or left["output_sha256"] != right["output_sha256"]
            ):
                raise RuntimeError("Home cross-method call mismatch")

    native_sha = str(result["native_library_sha256"])
    if receipt_native_shas != {native_sha}:
        raise RuntimeError("Home receipt/native identity mismatch")
    payload = {
        "schema": "rtdl.goal5774.home_v2_v4_prepared_independent_recount.v1",
        "result_sha256": _sha(result_path),
        "lane_count": 13,
        "owner_count": 26,
        "activation_call_count": 26,
        "measured_shape_call_count": 52,
        "correct_call_count": 78,
        "behavioral_true_optix_call_count": 78,
        "distinct_request_triplet_count": 26,
        "cross_method_input_output_match_count": 39,
        "native_library_sha256": native_sha,
        "minimum_activation_seconds": min(activation_seconds),
        "maximum_activation_seconds": max(activation_seconds),
        "minimum_measured_shape_seconds": min(measured_seconds),
        "maximum_measured_shape_seconds": max(measured_seconds),
        "registered_performance_claim_created": False,
        "imports_measured_frontdoor_or_application": False,
        "all_checks_passed": True,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(recount(args.result, args.output))


if __name__ == "__main__":
    main()
