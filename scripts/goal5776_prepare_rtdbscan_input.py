#!/usr/bin/env python3
"""Freeze the public 4,096-point RT-DBSCAN clustered3d benchmark contract.

This utility deliberately imports neither the RT-DBSCAN paper adapter nor a
V2/V4 execution route.  It reproduces the published benchmark fixture from
its documented deterministic generator and computes the exact float32 radius
graph and predicate-aware boundary partition independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random

import numpy as np


SCHEMA = "rtdl.goal5776.rtdbscan_real_scale_input.v1"
DEFAULT_POINT_COUNT = 4096
DEFAULT_SEED = 57760017
DEFAULT_EPSILON = 0.055
DEFAULT_MIN_POINTS = 12


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def generate_clustered3d(*, point_count: int, seed: int) -> np.ndarray:
    if point_count != DEFAULT_POINT_COUNT:
        raise ValueError("Goal5776 freezes the semantic maximum of 4096 points")
    rng = random.Random(int(seed))
    centers = (
        (0.22, 0.25, 0.30),
        (0.74, 0.30, 0.25),
        (0.54, 0.74, 0.72),
        (0.22, 0.77, 0.42),
    )
    points = np.empty((point_count, 3), dtype=np.float32)
    for index in range(point_count):
        cx, cy, cz = centers[index % len(centers)]
        points[index] = (
            _clamp01(rng.gauss(cx, 0.025)),
            _clamp01(rng.gauss(cy, 0.025)),
            _clamp01(rng.gauss(cz, 0.025)),
        )
    if not np.isfinite(points).all():
        raise RuntimeError("generated RT-DBSCAN points must be finite")
    return points


def exact_f32_adjacency(points: np.ndarray, *, epsilon: float) -> np.ndarray:
    """Return the full directed closed-radius graph using float32 arithmetic."""

    points = np.ascontiguousarray(points, dtype=np.float32)
    count = int(points.shape[0])
    adjacency = np.empty((count, count), dtype=np.bool_)
    epsilon_f32 = np.float32(epsilon)
    radius_sq = np.multiply(epsilon_f32, epsilon_f32, dtype=np.float32)
    # Bounded chunks avoid an N x N x 3 temporary while preserving the exact
    # subtract -> multiply -> add -> add float32 operation order of the routes.
    for start in range(0, count, 128):
        stop = min(count, start + 128)
        delta = np.subtract(
            points[start:stop, None, :], points[None, :, :], dtype=np.float32)
        squared = np.multiply(delta, delta, dtype=np.float32)
        xy = np.add(squared[:, :, 0], squared[:, :, 1], dtype=np.float32)
        distance_sq = np.add(xy, squared[:, :, 2], dtype=np.float32)
        adjacency[start:stop] = distance_sq <= radius_sq
    if not np.array_equal(adjacency, adjacency.T):
        raise RuntimeError("exact float32 self-radius graph must be symmetric")
    if not np.all(np.diag(adjacency)):
        raise RuntimeError("closed-radius graph must include every self edge")
    return adjacency


def predicate_aware_partition(
    adjacency: np.ndarray, *, min_points: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Independent lowest-root core/boundary partition used by the paper app."""

    adjacency = np.asarray(adjacency, dtype=np.bool_)
    count = int(adjacency.shape[0])
    core = np.asarray(adjacency.sum(axis=1) >= int(min_points), dtype=np.bool_)
    labels = np.full(count, -1, dtype=np.int32)
    unvisited = core.copy()
    roots: list[int] = []
    while bool(unvisited.any()):
        root = int(np.flatnonzero(unvisited)[0])
        component = np.zeros(count, dtype=np.bool_)
        frontier = np.zeros(count, dtype=np.bool_)
        frontier[root] = True
        while bool(frontier.any()):
            component |= frontier
            reached = adjacency[frontier].any(axis=0) & core
            frontier = reached & ~component
        component_root = int(np.flatnonzero(component)[0])
        labels[component] = component_root
        unvisited &= ~component
        roots.append(component_root)

    # Non-core boundary points attach to the lowest root of an adjacent core
    # component.  False-false edges never join components.
    for item in np.flatnonzero(~core):
        adjacent_core = np.flatnonzero(adjacency[item] & core)
        if adjacent_core.size:
            labels[item] = int(labels[adjacent_core].min())

    canonical = np.full(count, -1, dtype=np.int32)
    remap: dict[int, int] = {}
    for index, raw in enumerate(labels.tolist()):
        if raw < 0:
            continue
        if raw not in remap:
            remap[raw] = len(remap)
        canonical[index] = remap[raw]
    return core, canonical


def _write_array(root: Path, name: str, value: np.ndarray) -> dict[str, object]:
    path = root / name
    np.save(path, np.ascontiguousarray(value), allow_pickle=False)
    return {
        "sha256": _sha256(path),
        "dtype": str(value.dtype),
        "shape": list(value.shape),
        "bytes": path.stat().st_size,
    }


def prepare(output: Path, *, seed: int) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=False)
    points = generate_clustered3d(point_count=DEFAULT_POINT_COUNT, seed=seed)
    adjacency = exact_f32_adjacency(points, epsilon=DEFAULT_EPSILON)
    core, labels = predicate_aware_partition(
        adjacency, min_points=DEFAULT_MIN_POINTS)
    neighbor_counts = adjacency.sum(axis=1, dtype=np.uint32)
    members = {
        "points_f32.npy": _write_array(output, "points_f32.npy", points),
        "neighbor_counts_u32.npy": _write_array(
            output, "neighbor_counts_u32.npy", neighbor_counts),
        "core_flags_u8.npy": _write_array(
            output, "core_flags_u8.npy", core.astype(np.uint8)),
        "canonical_component_labels_i32.npy": _write_array(
            output, "canonical_component_labels_i32.npy", labels),
    }
    component_sizes = sorted(
        int(np.count_nonzero(labels == label))
        for label in sorted(set(labels.tolist())) if label >= 0)
    manifest = {
        "schema": SCHEMA,
        "provenance": {
            "family": "public_rtdl_rt_dbscan_benchmark_clustered3d",
            "generator": "documented deterministic clustered3d generator",
            "paper_dataset_replacement_claimed": False,
            "semantic_bound_point_count": DEFAULT_POINT_COUNT,
            "seed": int(seed),
        },
        "contract": {
            "point_count": DEFAULT_POINT_COUNT,
            "dimension": 3,
            "epsilon": DEFAULT_EPSILON,
            "min_points": DEFAULT_MIN_POINTS,
            "closed_radius": True,
            "self_neighbor_included": True,
            "distance_arithmetic": "float32_sub_mul_add_add",
            "boundary_assignment": "lowest_component_root",
        },
        "oracle": {
            "route_independent": True,
            "imports_v2_or_v4_route": False,
            "directed_edge_count": int(adjacency.sum(dtype=np.uint64)),
            "core_count": int(core.sum()),
            "component_count": len(component_sizes),
            "component_sizes": component_sizes,
            "noise_count": int(np.count_nonzero(labels < 0)),
            "neighbor_count_min": int(neighbor_counts.min()),
            "neighbor_count_max": int(neighbor_counts.max()),
        },
        "members": members,
    }
    manifest_path = output / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    manifest = prepare(args.output.resolve(), seed=args.seed)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
