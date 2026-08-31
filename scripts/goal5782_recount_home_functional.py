#!/usr/bin/env python3
"""Independent recount of the Goal5782 Home V2/V4 functional cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
METHODS = (V2, V4)
LANES = (
    "triangle__rt_1a2", "triangle__rt_2a1", "raydb__q21",
    "librts__range_rows", "librts__overlap_filter", "rtnn__ranked_window",
    "rtdbscan__components", "xhd__global_witness",
    "rayjoin__point_location", "rayjoin__segment_pairs",
    "rayjoin__grouped_events", "rtbh__force", "particle__cell_transition",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_leaves(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        if "physical_executor_classification" in value \
                and "native_snapshot" in value:
            yield value
        for child in value.values():
            yield from receipt_leaves(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from receipt_leaves(child)


def validate_leaf(receipt: Mapping[str, Any], expected_native: str) -> None:
    snapshot = receipt["native_snapshot"]
    successful = int(snapshot["successful_launch_count"])
    if receipt["physical_executor_classification"] != "optix_traversal_observed" \
            or successful <= 0 \
            or int(snapshot["complete_context_launch_count"]) != successful \
            or any(int(snapshot[name]) != 0 for name in (
                "failed_launch_count", "incomplete_context_launch_count",
                "pending_context_at_finish", "session_error",
            )) \
            or not int(snapshot["first_traversable"]) \
            or not int(snapshot["last_traversable"]):
        raise RuntimeError("functional traversal receipt is incomplete")
    if receipt.get("provider_library_sha256") != expected_native:
        raise RuntimeError("functional receipt native identity changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--expected-native-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    files = sorted(args.raw.glob("*.json"))
    if len(files) != len(LANES) * len(METHODS):
        raise RuntimeError("Goal5782 functional cohort must contain 26 workers")
    rows = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    expected_keys = {(lane, method) for lane in LANES for method in METHODS}
    actual_keys = {(row["lane_id"], row["method"]) for row in rows}
    if actual_keys != expected_keys:
        raise RuntimeError("Goal5782 lane/method matrix is incomplete or duplicated")
    if len({int(row["parent_pid"]) for row in rows}) != len(rows):
        raise RuntimeError("Goal5782 workers do not have fresh parent PIDs")

    leaf_count = 0
    successful_launches = 0
    raygen_invocations = 0
    for row in rows:
        endpoint = row["endpoint"]
        if row.get("formal_worker") or row.get("registered_performance_observation") \
                or row.get("performance_interpretation_allowed"):
            raise RuntimeError("Goal5782 functional worker became performance evidence")
        if not endpoint["matched"] or endpoint.get("performance_claimed"):
            raise RuntimeError("Goal5782 functional output mismatch or performance claim")
        leaves = tuple(receipt_leaves(endpoint["traversal_receipt"]))
        if not leaves:
            raise RuntimeError("Goal5782 functional worker has no traversal receipt")
        for leaf in leaves:
            validate_leaf(leaf, args.expected_native_sha256)
            leaf_count += 1
            successful_launches += int(
                leaf["native_snapshot"]["successful_launch_count"])
            raygen_invocations += int(
                leaf["native_snapshot"]["raygen_invocation_count"])

    for lane in LANES:
        cohort = [row["endpoint"] for row in rows if row["lane_id"] == lane]
        if len({row["input_sha256"] for row in cohort}) != 1 \
                or len({row["output_sha256"] for row in cohort}) != 1:
            raise RuntimeError(f"V2/V4 input or output mismatch: {lane}")

    result = {
        "schema": "rtdl.goal5782.home_functional_independent_recount.v1",
        "status": "PASS__26_OF_26_EXACT_AND_BEHAVIORALLY_TRUE_OPTIX",
        "worker_count": len(rows),
        "unique_parent_pid_count": len({int(row["parent_pid"]) for row in rows}),
        "lane_count": len(LANES),
        "method_count": len(METHODS),
        "exact_output_count": len(rows),
        "behavioral_true_optix_worker_count": len(rows),
        "leaf_receipt_count": leaf_count,
        "successful_launch_count": successful_launches,
        "raygen_invocation_count": raygen_invocations,
        "native_library_sha256": args.expected_native_sha256,
        "raw_payload_count": len(files),
        "raw_payload_bytes": sum(path.stat().st_size for path in files),
        "raw_payloads": [
            {"path": path.name, "sha256": sha(path), "size_bytes": path.stat().st_size}
            for path in files
        ],
        "claim_boundary": {
            "functional_only": True,
            "registered_performance_result": False,
            "pod_used": False,
            "modern_rtx_claimed": False,
            "no_slower_claimed": False,
        },
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "workers": len(rows), "leaf_receipts": leaf_count,
        "successful_launches": successful_launches,
        "raygen_invocations": raygen_invocations,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
