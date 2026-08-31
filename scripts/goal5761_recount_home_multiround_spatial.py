#!/usr/bin/env python3
"""Independent raw recount for Goal5761/M3 Home evidence.

This file deliberately imports neither the V4 runtime nor either Paper-App
migration.  It rebuilds the two frozen answers directly from the embedded raw
float32 inputs and checks the physical-lifecycle receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _distance_sq(left: np.ndarray, right: np.ndarray) -> np.float32:
    delta = np.subtract(left, right, dtype=np.float32)
    squared = np.multiply(delta, delta, dtype=np.float32)
    value = np.add(squared[0], squared[1], dtype=np.float32)
    return np.add(value, squared[2], dtype=np.float32)


def _rtnn_reference(spec: dict[str, object]) -> tuple[tuple[object, ...], ...]:
    search = np.asarray(spec["search_points_f32"], dtype=np.float32)
    queries = np.asarray(spec["query_points_f32"], dtype=np.float32)
    k = int(spec["k"])
    minimum = float(spec["minimum_distance"])
    maximum = float(spec["maximum_distance"])
    if spec.get("boundary_policy") != "open_min_open_max_v1":
        raise RuntimeError("frozen RTNN oracle requires explicit open boundaries")
    rows: list[tuple[object, ...]] = []
    for query_id, query in enumerate(queries):
        candidates: list[tuple[np.float32, int]] = []
        for item_id, item in enumerate(search):
            distance = np.sqrt(_distance_sq(query, item), dtype=np.float32)
            if minimum < float(distance) < maximum:
                candidates.append((distance, item_id))
        candidates.sort(key=lambda row: (float(row[0]), row[1]))
        for rank, (distance, item_id) in enumerate(candidates[:k], start=1):
            distance_sq = np.multiply(distance, distance, dtype=np.float32)
            rows.append((query_id, item_id, rank, float(distance_sq)))
    return tuple(rows)


def _canonical_labels(labels: list[int]) -> tuple[int, ...]:
    mapping: dict[int, int] = {}
    result: list[int] = []
    for label in labels:
        if label < 0:
            result.append(-1)
        else:
            if label not in mapping:
                mapping[label] = len(mapping)
            result.append(mapping[label])
    return tuple(result)


def _dbscan_reference(spec: dict[str, object]) -> dict[str, object]:
    points = np.asarray(spec["points_f32"], dtype=np.float32)
    epsilon = np.float32(spec["epsilon"])
    radius_sq = np.multiply(epsilon, epsilon, dtype=np.float32)
    min_points = int(spec["min_points"])
    edges = tuple(
        (left_id, right_id)
        for left_id, left in enumerate(points)
        for right_id, right in enumerate(points)
        if _distance_sq(left, right) <= radius_sq
    )
    counts = [0] * len(points)
    for left, _ in edges:
        counts[left] += 1
    core = tuple(count >= min_points for count in counts)
    parent = list(range(len(points)))

    def find(item: int) -> int:
        root = item
        while parent[root] != root:
            root = parent[root]
        while parent[item] != item:
            successor = parent[item]
            parent[item] = root
            item = successor
        return root

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for left, right in edges:
        if core[left] and core[right]:
            union(left, right)
    boundary_roots: dict[int, set[int]] = {}
    for left, right in edges:
        if core[left] and not core[right]:
            boundary_roots.setdefault(right, set()).add(find(left))
        elif core[right] and not core[left]:
            boundary_roots.setdefault(left, set()).add(find(right))
    labels = [-1] * len(points)
    for item, is_core in enumerate(core):
        if is_core:
            labels[item] = find(item)
        elif item in boundary_roots:
            labels[item] = min(boundary_roots[item])
    return {
        "edge_count": len(edges),
        "edge_rows": edges,
        "neighbor_counts": tuple(counts),
        "core_flags": core,
        "canonical_component_labels": _canonical_labels(labels),
    }


def _as_rows(value: object) -> tuple[tuple[object, ...], ...]:
    return tuple(tuple(row) for row in value)


def _check_lifecycle(lane: dict[str, object]) -> None:
    telemetry = lane["telemetry"]
    counts = tuple(int(value) for value in lane["round_candidate_counts"])
    rounds = len(counts)
    if telemetry["gas_build_count"] != 1:
        raise RuntimeError("prepared owner did not build exactly one GAS")
    if telemetry["gas_refit_count"] != max(0, rounds - 1):
        raise RuntimeError("GAS refit count does not match bounded rounds")
    if telemetry["launch_count"] != rounds or rounds == 0 or rounds > 64:
        raise RuntimeError("launch count violates explicit bounded controller")
    if telemetry["traversable_handle_first"] <= 0 \
            or telemetry["traversable_handle_last"] <= 0:
        raise RuntimeError("nonzero persistent traversable handles were not observed")
    receipt = lane["traversal_receipt"]
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("lane is not behaviorally true-OptiX")
    snapshot = receipt["native_snapshot"]
    if int(snapshot["failed_launch_count"]) != 0 \
            or int(snapshot["incomplete_context_launch_count"]) != 0 \
            or int(snapshot["pending_context_at_finish"]) != 0 \
            or int(snapshot["session_error"]) != 0 \
            or int(snapshot["successful_launch_count"]) \
            != int(snapshot["complete_context_launch_count"]):
        raise RuntimeError("lane contains failed, unbound, or incomplete launches")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    payload = json.loads((args.raw / "RESULT.json").read_text(encoding="utf-8"))
    lanes = {row["lane"]: row for row in payload["lanes"]}
    if set(lanes) != {
        "rtnn.point_selection.spatial_bounded.v1",
        "rt_dbscan.fixed_radius.prepared_spatial_components.v1",
    }:
        raise RuntimeError("raw evidence does not contain the exact two frozen lanes")

    rtnn = lanes["rtnn.point_selection.spatial_bounded.v1"]
    rtnn_recount = _rtnn_reference(rtnn["input"])
    rtnn_actual = _as_rows(rtnn["actual"])
    if rtnn_recount != rtnn_actual or rtnn_actual != _as_rows(rtnn["expected"]):
        raise RuntimeError("independent RTNN recount mismatch")
    _check_lifecycle(rtnn)

    dbscan = lanes["rt_dbscan.fixed_radius.prepared_spatial_components.v1"]
    dbscan_recount = _dbscan_reference(dbscan["input"])
    actual = dbscan["actual"]
    if dbscan_recount["edge_count"] != actual["edge_count"] \
            or dbscan_recount["edge_rows"] != _as_rows(actual["edge_rows"]) \
            or dbscan_recount["neighbor_counts"] != tuple(actual["neighbor_counts"]) \
            or dbscan_recount["core_flags"] != tuple(actual["core_flags"]) \
            or dbscan_recount["canonical_component_labels"] \
            != tuple(actual["canonical_component_labels"]):
        raise RuntimeError("independent RT-DBSCAN recount mismatch")
    _check_lifecycle(dbscan)

    result = {
        "schema": "rtdl.goal5761.independent_home_recount.v1",
        "raw_result_sha256": _sha(args.raw / "RESULT.json"),
        "native_library_sha256": _sha(args.raw / "librtdl_optix.so"),
        "lane_count": 2,
        "exact_cpu_recount_count": 2,
        "behavioral_true_optix_count": 2,
        "persistent_single_build_count": 2,
        "registered_performance_timing_count": 0,
        "imports_primary_runtime_or_paper_app": False,
        "rtnn_recount_rows": len(rtnn_recount),
        "rt_dbscan_recount_edges": dbscan_recount["edge_count"],
        "verdict": "pass",
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
