#!/usr/bin/env python3
"""Standalone raw recount for Goal5759; imports no compiler/runtime route."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED = {
    "raydb.keyed_i64_sum": [[[0], 47], [[2], 5], [[3], 13]],
    "triangle_counting.rt_1a2_all_hit": 2_224_385,
    "triangle_counting.rt_2a1_weighted": 2_224_385,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _keyed(rows):
    seen = {}
    grouped = {}
    for index, row in enumerate(rows):
        identity = (int(row["primitive.stable_id"]), int(row["launch_index"]))
        fingerprint = (
            int(row["launch_index"]), int(row["primitive.signed_value"]),
            int(row["primitive.include"]),
        )
        if identity in seen:
            if seen[identity] != fingerprint:
                raise RuntimeError(f"conflicting duplicate at raw row {index}")
            continue
        seen[identity] = fingerprint
        if fingerprint[2] == 1:
            grouped[fingerprint[0]] = grouped.get(fingerprint[0], 0) + fingerprint[1]
    return [[[key], grouped[key]] for key in sorted(grouped) if grouped[key] != 0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    submitted = json.loads((args.raw / "RESULT.json").read_text())
    lanes = {row["lane"]: row for row in submitted["lanes"]}
    if set(lanes) != set(EXPECTED):
        raise RuntimeError("raw lane membership differs")
    recounted = []
    native_shas = set()
    for lane_name in sorted(lanes):
        lane = lanes[lane_name]
        rows = lane["raw_reducer_rows"]
        if lane_name == "raydb.keyed_i64_sum":
            value = _keyed(rows)
            if sum(map(int, lane["per_ray_u64"])) != len(rows):
                raise RuntimeError("RayDB accepted payload disagrees with raw events")
        elif lane_name.endswith("rt_1a2_all_hit"):
            value = sum(int(row["count"]) for row in rows)
        else:
            value = sum(
                int(row["count"]) * int(row["query.weight"]) for row in rows)
        expected = EXPECTED[lane_name]
        if value != expected or lane["observed_reduced_output"] != expected:
            raise RuntimeError(f"{lane_name}: independent exact output mismatch")
        receipt = lane["traversal_receipt"]
        snapshot = receipt["native_snapshot"]
        query_count = len(lane["per_ray_u64"])
        if receipt["physical_executor_classification"] != "optix_traversal_observed" \
                or snapshot["successful_launch_count"] != 1 \
                or snapshot["complete_context_launch_count"] != 1 \
                or snapshot["incomplete_context_launch_count"] != 0 \
                or snapshot["failed_launch_count"] != 0 \
                or snapshot["raygen_invocation_count"] != query_count \
                or snapshot["session_error"] != 0 \
                or snapshot["pending_context_at_finish"] != 0 \
                or not receipt["expected_program_observed_at_receipt_edge"]:
            raise RuntimeError(f"{lane_name}: behavioral traversal receipt failed")
        counters = tuple(map(int, lane["role_counters"]))
        if counters[1] != query_count or counters[5] != query_count \
                or counters[6] != query_count or counters[3] <= 0:
            raise RuntimeError(f"{lane_name}: role lifecycle mismatch")
        if any(int(row["error_code"]) or int(row["first_error_claimed"])
               for row in lane["launch_status"]):
            raise RuntimeError(f"{lane_name}: device status failure")
        native_shas.add(lane["native_library_sha256"])
        recounted.append({
            "lane": lane_name,
            "independent_reduced_output": value,
            "raw_reducer_row_count": len(rows),
            "query_count": query_count,
            "role_counters": counters,
            "successful_launch_count": snapshot["successful_launch_count"],
            "complete_context_launch_count": snapshot["complete_context_launch_count"],
            "raygen_invocation_count": snapshot["raygen_invocation_count"],
            "exact_output_matched": True,
            "behavioral_true_optix": True,
        })
    native_path = args.raw / "librtdl_optix.so"
    if len(native_shas) != 1 or _sha(native_path) not in native_shas:
        raise RuntimeError("exact native bytes do not bind all raw lanes")
    output = {
        "schema": "rtdl.goal5759.independent_home_recount.v1",
        "goal": 5759,
        "raw_result_sha256": _sha(args.raw / "RESULT.json"),
        "native_library_sha256": _sha(native_path),
        "lane_count": len(recounted),
        "exact_output_count": sum(row["exact_output_matched"] for row in recounted),
        "behavioral_true_optix_count": sum(
            row["behavioral_true_optix"] for row in recounted),
        "compiler_or_runtime_route_imported": False,
        "performance_claimed": False,
        "lanes": recounted,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
