from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


NOISE_CLUSTER_ID = -1
DEFAULT_DATASET_CONFIG = {
    "tiny": {"point_count": 9, "radius": 0.20, "min_neighbors": 3},
    "clustered3d": {"point_count": 512, "radius": 0.055, "min_neighbors": 12},
    "road3d": {"point_count": 512, "radius": 0.030, "min_neighbors": 8},
    "ngsim_dense": {"point_count": 512, "radius": 0.012, "min_neighbors": 20},
}
DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET = 160_000_000
DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS = 8_000_000
DEFAULT_GROUPED_UNION_QUERY_BLOCK_SIZE = 8192
RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA = "rt_dbscan_grouped_stream_host_overhead_breakdown_v1"
DIRECTED_ADJACENCY_INDEX_BYTES = 4
DIRECTED_ADJACENCY_OFFSET_BYTES = 8


def estimate_rt_dbscan_directed_adjacency_edges(dataset: str, point_count: int) -> int:
    """Return an evidence-bounded estimate for directed fixed-radius adjacency size."""
    point_count = int(point_count)
    if point_count < 1:
        raise ValueError("point_count must be positive")
    if dataset == "tiny":
        return 33
    if dataset == "clustered3d":
        return max(point_count, int(round(0.126 * point_count * point_count)))
    if dataset == "road3d":
        return max(point_count, int(round(0.018 * point_count * point_count)))
    if dataset == "ngsim_dense":
        return max(point_count, int(round(0.055 * point_count * point_count)))
    raise ValueError("dataset must be tiny, clustered3d, road3d, or ngsim_dense")


def _estimated_directed_adjacency_bytes(point_count: int, directed_edges: int) -> int:
    return (
        int(directed_edges) * DIRECTED_ADJACENCY_INDEX_BYTES
        + (int(point_count) + 1) * DIRECTED_ADJACENCY_OFFSET_BYTES
    )


def plan_rt_dbscan_execution(dataset: str, point_count: int) -> dict[str, object]:
    """Return an explicit benchmark-app plan from the current reviewed evidence."""
    point_count = int(point_count)
    if dataset == "tiny":
        selected_mode = "cpu_reference"
        reason = "tiny correctness fixture; no GPU performance claim"
    elif dataset == "ngsim_dense":
        selected_mode = "partner_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed compact ngsim_dense rows favor the prepared pure-CuPy continuation through 262k"
    elif dataset == "road3d" and point_count < 524288:
        selected_mode = "partner_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed road3d favors the prepared pure-CuPy continuation below the 524k crossover"
    elif dataset == "clustered3d" and point_count < 65536:
        selected_mode = "partner_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed clustered3d needs at least the 65k scale before prepared RT wins over prepared pure CuPy"
    else:
        selected_mode = "optix_rt_core_flags_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed prepared RT-count plus prepared CuPy grid wins for this measured scale/shape"
    return {
        "adapter": "plan_rt_dbscan_execution",
        "selected_mode": selected_mode,
        "reason": reason,
        "policy": "explicit_benchmark_plan_from_goal2425_prepared_fairness_evidence",
        "not_hidden_dispatcher": True,
        "release_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def plan_rt_dbscan_continuation_execution(
    dataset: str,
    point_count: int,
    *,
    directed_edge_budget: int | None = None,
) -> dict[str, object]:
    """Plan the explicit adjacency-continuation contract for RT-DBSCAN experiments."""
    point_count = int(point_count)
    edge_budget = int(
        DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET
        if directed_edge_budget is None
        else directed_edge_budget
    )
    if edge_budget < 1:
        raise ValueError("directed_edge_budget must be positive")
    estimated_edges = estimate_rt_dbscan_directed_adjacency_edges(dataset, point_count)
    estimated_bytes = _estimated_directed_adjacency_bytes(point_count, estimated_edges)
    full_stream_fits_budget = estimated_edges <= edge_budget

    if dataset == "tiny":
        selected_mode = "cpu_reference"
        reason = "tiny correctness fixture; no GPU continuation plan is needed"
    elif full_stream_fits_budget:
        selected_mode = "optix_rt_core_adjacency_cupy_components_3d"
        reason = (
            "estimated directed adjacency stream fits the explicit budget; "
            "Goal2431/2435/2452/2457 evidence says the full stream is faster than chunked or grouped when it fits"
        )
    else:
        selected_mode = "optix_rt_core_grouped_stream_cupy_components_3d"
        reason = (
            "estimated directed adjacency stream exceeds the explicit budget; "
            "Goal2457/2461/2463/2465/2475/2476 evidence says the grouped stream avoids the giant "
            "neighbor-index table, reuses prepared device search points, reduces avoidable anyhit work, "
            "and beats chunked continuation for the measured dense branch"
        )
    return {
        "adapter": "plan_rt_dbscan_continuation_execution",
        "selected_mode": selected_mode,
        "reason": reason,
        "policy": (
            "explicit_continuation_plan_from_goal2431_2433_2435_2452_2457_2461_2463_2465_2475_2476_evidence"
        ),
        "evidence_goals": [
            "Goal2431",
            "Goal2433",
            "Goal2435",
            "Goal2452",
            "Goal2457",
            "Goal2461",
            "Goal2463",
            "Goal2465",
            "Goal2475",
            "Goal2476",
        ],
        "estimated_directed_edge_count": estimated_edges,
        "directed_edge_budget": edge_budget,
        "estimated_full_adjacency_bytes": estimated_bytes,
        "full_stream_fits_budget": full_stream_fits_budget,
        "planner_surface": "benchmark_app_plan_explain_not_engine_dispatch",
        "not_hidden_dispatcher": True,
        "release_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def plan_rt_dbscan_blocked_grouped_continuation_design(
    dataset: str,
    point_count: int,
    *,
    segment_target_hits: int = DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS,
) -> dict[str, object]:
    """Return the Goal2467 non-executable design plan for blocked grouped union.

    This is deliberately not a runtime dispatcher. It records the next generic
    primitive shape and a sizing estimate so native work can be reviewed before
    implementation and pod timing.
    """
    point_count = int(point_count)
    segment_target_hits = int(segment_target_hits)
    if segment_target_hits < 1:
        raise ValueError("segment_target_hits must be positive")
    estimated_edges = estimate_rt_dbscan_directed_adjacency_edges(dataset, point_count)
    estimated_segments = max(1, math.ceil(estimated_edges / segment_target_hits))
    return {
        "adapter": "plan_rt_dbscan_blocked_grouped_continuation_design",
        "design_status": "needs-more-evidence",
        "runtime_executable": False,
        "selected_mode": "design_only_generic_blocked_grouped_stream_candidate",
        "target_primitive": "generic_fixed_radius_blocked_grouped_component_continuation_3d",
        "candidate_native_contract": "fixed_radius_hit_stream_to_segmented_grouped_union_workspaces",
        "reason": (
            "Goal2461/2463/2465 removed transfer and all-items avoidable anyhit overhead; "
            "the remaining target is generic grouped-union global atomic pressure"
        ),
        "policy": "goal2467_design_only_no_hidden_dispatch_no_native_abi_until_review",
        "evidence_goals": [
            "Goal2457",
            "Goal2459",
            "Goal2461",
            "Goal2463",
            "Goal2465",
        ],
        "estimated_directed_edge_count": estimated_edges,
        "segment_target_hits": segment_target_hits,
        "estimated_segment_count": estimated_segments,
        "app_independent_engine_required": True,
        "forbidden_native_vocabulary": ["dbscan", "cluster", "min_neighbors"],
        "planner_surface": "benchmark_app_design_explain_not_engine_dispatch",
        "not_hidden_dispatcher": True,
        "release_claim_authorized": False,
        "performance_claim_authorized": False,
        "pod_validation_required": True,
    }


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def make_rt_dbscan_points(dataset: str, *, point_count: int, seed: int) -> tuple[rt.Point3D, ...]:
    """Generate deterministic 3-D point fixtures for the RT-DBSCAN study.

    These are paper-inspired stressors, not paper-dataset replacements.
    """
    if point_count < 1:
        raise ValueError("point_count must be positive")
    rng = random.Random(seed)

    if dataset == "tiny":
        base = (
            (0.00, 0.00, 0.00),
            (0.08, 0.04, 0.01),
            (-0.07, 0.05, 0.02),
            (0.04, -0.08, -0.01),
            (0.62, 0.62, 0.04),
            (0.70, 0.66, 0.02),
            (0.58, 0.55, 0.00),
            (0.72, 0.55, 0.03),
            (0.98, 0.04, 0.97),
        )
        return tuple(rt.Point3D(id=index + 1, x=x, y=y, z=z) for index, (x, y, z) in enumerate(base[:point_count]))

    points: list[rt.Point3D] = []
    if dataset == "clustered3d":
        centers = [(0.22, 0.25, 0.30), (0.74, 0.30, 0.25), (0.54, 0.74, 0.72), (0.22, 0.77, 0.42)]
        for index in range(point_count):
            cx, cy, cz = centers[index % len(centers)]
            points.append(
                rt.Point3D(
                    id=index + 1,
                    x=_clamp01(rng.gauss(cx, 0.025)),
                    y=_clamp01(rng.gauss(cy, 0.025)),
                    z=_clamp01(rng.gauss(cz, 0.025)),
                )
            )
    elif dataset == "road3d":
        for index in range(point_count):
            t = (index + 0.5) / point_count
            lane = -0.012 if index % 2 == 0 else 0.012
            points.append(
                rt.Point3D(
                    id=index + 1,
                    x=t,
                    y=_clamp01(0.50 + lane + 0.030 * math.sin(8.0 * math.pi * t) + rng.gauss(0.0, 0.004)),
                    z=_clamp01(0.20 + 0.10 * t + rng.gauss(0.0, 0.006)),
                )
            )
    elif dataset == "ngsim_dense":
        side = max(1, round(point_count ** (1.0 / 3.0)))
        for index in range(point_count):
            ix = index % side
            iy = (index // side) % side
            iz = (index // (side * side)) % side
            points.append(
                rt.Point3D(
                    id=index + 1,
                    x=_clamp01(0.45 + 0.10 * (ix / max(1, side - 1)) + rng.gauss(0.0, 0.0015)),
                    y=_clamp01(0.45 + 0.10 * (iy / max(1, side - 1)) + rng.gauss(0.0, 0.0015)),
                    z=_clamp01(0.45 + 0.10 * (iz / max(1, side - 1)) + rng.gauss(0.0, 0.0015)),
                )
            )
    else:
        raise ValueError("dataset must be tiny, clustered3d, road3d, or ngsim_dense")
    return tuple(points)


def make_fixed_radius_neighbors_3d_embree_kernel(*, radius: float, k_max: int):
    """Build a generic Embree fixed-radius row kernel for the app's chosen radius."""

    @rt.kernel(backend="rtdl", precision="float_approx")
    def _rt_dbscan_fixed_radius_neighbors_3d_embree():
        query_points = rt.input("query_points", rt.Points3D, role="probe")
        search_points = rt.input("search_points", rt.Points3D, role="build")
        candidates = rt.traverse(query_points, search_points, accel="bvh")
        hits = rt.refine(
            candidates,
            predicate=rt.fixed_radius_neighbors(radius=radius, k_max=k_max),
        )
        return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])

    return _rt_dbscan_fixed_radius_neighbors_3d_embree


def fixed_radius_pairs_and_neighbor_counts_3d(
    points: tuple[rt.Point3D, ...],
    *,
    radius: float,
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    """Return undirected fixed-radius pairs and inclusive neighbor counts."""
    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    radius_sq = radius * radius
    neighbor_counts = [1 for _ in points]
    pairs: list[tuple[int, int]] = []
    for left, left_point in enumerate(points):
        for right in range(left + 1, len(points)):
            right_point = points[right]
            dx = left_point.x - right_point.x
            dy = left_point.y - right_point.y
            dz = left_point.z - right_point.z
            if dx * dx + dy * dy + dz * dz <= radius_sq:
                neighbor_counts[left] += 1
                neighbor_counts[right] += 1
                pairs.append((left, right))
    return tuple(pairs), tuple(neighbor_counts)


def _component_rows_from_pairs_and_flags(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: Iterable[int],
    *,
    predicate_flags: Iterable[bool],
) -> tuple[dict[str, object], ...]:
    counts = [int(count) for count in neighbor_counts]
    is_core = [bool(flag) for flag in predicate_flags]
    if len(counts) != len(points) or len(is_core) != len(points):
        raise ValueError("neighbor_counts and predicate_flags must match points")
    parent = list(range(len(points)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root

    pairs = tuple(within_pairs)
    for left, right in pairs:
        if is_core[left] and is_core[right]:
            union(left, right)

    roots = [-1 for _ in points]
    for index, core in enumerate(is_core):
        if core:
            roots[index] = find(index)
    for left, right in pairs:
        if roots[left] == -1 and is_core[right]:
            roots[left] = find(right)
        if roots[right] == -1 and is_core[left]:
            roots[right] = find(left)

    dense_by_root: dict[int, int] = {}
    next_label = 1
    rows: list[dict[str, object]] = []
    for index, point in enumerate(points):
        root = roots[index]
        if root < 0:
            cluster_id = NOISE_CLUSTER_ID
        else:
            if root not in dense_by_root:
                dense_by_root[root] = next_label
                next_label += 1
            cluster_id = dense_by_root[root]
        rows.append(
            {
                "point_id": point.id,
                "cluster_id": cluster_id,
                "is_core": bool(is_core[index]),
                "neighbor_count": int(counts[index]),
            }
        )
    return tuple(rows)


def _component_rows_from_pairs(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: list[int],
    *,
    min_neighbors: int,
) -> tuple[dict[str, object], ...]:
    return _component_rows_from_pairs_and_flags(
        points,
        within_pairs,
        neighbor_counts,
        predicate_flags=(count >= min_neighbors for count in neighbor_counts),
    )


def _component_rows_from_parent_and_pairs(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: Iterable[int],
    *,
    predicate_flags: Iterable[bool],
    parent: Iterable[int],
) -> tuple[dict[str, object], ...]:
    counts = [int(count) for count in neighbor_counts]
    is_core = [bool(flag) for flag in predicate_flags]
    parent_copy = [int(item) for item in parent]
    if len(counts) != len(points) or len(is_core) != len(points) or len(parent_copy) != len(points):
        raise ValueError("neighbor_counts, predicate_flags, and parent must match points")

    def find(item: int) -> int:
        while parent_copy[item] != item:
            parent_copy[item] = parent_copy[parent_copy[item]]
            item = parent_copy[item]
        return item

    roots = [-1 for _ in points]
    for index, core in enumerate(is_core):
        if core:
            roots[index] = find(index)
    for left, right in within_pairs:
        if roots[left] == -1 and is_core[right]:
            roots[left] = find(right)
        if roots[right] == -1 and is_core[left]:
            roots[right] = find(left)

    dense_by_root: dict[int, int] = {}
    next_label = 1
    rows: list[dict[str, object]] = []
    for index, point in enumerate(points):
        root = roots[index]
        if root < 0:
            cluster_id = NOISE_CLUSTER_ID
        else:
            if root not in dense_by_root:
                dense_by_root[root] = next_label
                next_label += 1
            cluster_id = dense_by_root[root]
        rows.append(
            {
                "point_id": point.id,
                "cluster_id": cluster_id,
                "is_core": bool(is_core[index]),
                "neighbor_count": int(counts[index]),
            }
        )
    return tuple(rows)


def _deduplicate_segment_union_proposals(
    segment_pairs: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    local_parent: dict[int, int] = {}

    def ensure(item: int) -> None:
        if item not in local_parent:
            local_parent[item] = item

    def find(item: int) -> int:
        ensure(item)
        while local_parent[item] != item:
            local_parent[item] = local_parent[local_parent[item]]
            item = local_parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            local_parent[right_root] = left_root
        else:
            local_parent[left_root] = right_root

    for left, right in segment_pairs:
        union(left, right)

    components: dict[int, list[int]] = {}
    for item in local_parent:
        components.setdefault(find(item), []).append(item)

    proposals: list[tuple[int, int]] = []
    for members in components.values():
        if len(members) < 2:
            continue
        ordered = sorted(members)
        anchor = ordered[0]
        proposals.extend((anchor, item) for item in ordered[1:])
    return tuple(proposals)


def simulate_fixed_radius_blocked_grouped_component_continuation_3d(
    points: tuple[rt.Point3D, ...],
    *,
    radius: float,
    predicate_flags: Iterable[bool],
    neighbor_counts: Iterable[int] | None = None,
    segment_target_hits: int = DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS,
    segment_capacity_hits: int | None = None,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    """Local oracle for the Goal2467 blocked grouped-continuation contract."""
    segment_target_hits = int(segment_target_hits)
    if segment_target_hits < 1:
        raise ValueError("segment_target_hits must be positive")
    segment_capacity = segment_target_hits if segment_capacity_hits is None else int(segment_capacity_hits)
    if segment_capacity < 1:
        raise ValueError("segment_capacity_hits must be positive")

    flags = tuple(bool(flag) for flag in predicate_flags)
    if len(flags) != len(points):
        raise ValueError("predicate_flags must match points")

    pairs, computed_counts = fixed_radius_pairs_and_neighbor_counts_3d(points, radius=radius)
    counts = computed_counts if neighbor_counts is None else tuple(int(count) for count in neighbor_counts)
    if len(counts) != len(points):
        raise ValueError("neighbor_counts must match points")

    segments = tuple(pairs[index : index + segment_target_hits] for index in range(0, len(pairs), segment_target_hits))
    max_segment_hits = max((len(segment) for segment in segments), default=0)
    overflow_segment_count = sum(1 for segment in segments if len(segment) > segment_capacity)
    fallback_to_unblocked = overflow_segment_count > 0

    local_or_segment_union_proposals = 0
    deduplicated_union_proposals = 0
    global_parent_atomic_successes = 0
    parent = list(range(len(points)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> bool:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root
        return True

    if not fallback_to_unblocked:
        for segment in segments:
            core_pairs = tuple((left, right) for left, right in segment if flags[left] and flags[right])
            local_or_segment_union_proposals += len(core_pairs)
            deduplicated = _deduplicate_segment_union_proposals(core_pairs)
            deduplicated_union_proposals += len(deduplicated)
            for left, right in deduplicated:
                if union(left, right):
                    global_parent_atomic_successes += 1
    else:
        local_or_segment_union_proposals = sum(1 for left, right in pairs if flags[left] and flags[right])

    global_parent_atomic_attempts = 0 if fallback_to_unblocked else deduplicated_union_proposals
    proposal_rejection_rate = 0.0
    if local_or_segment_union_proposals > 0 and not fallback_to_unblocked:
        proposal_rejection_rate = 1.0 - (
            deduplicated_union_proposals / max(1, local_or_segment_union_proposals)
        )

    if fallback_to_unblocked:
        rows = _component_rows_from_pairs_and_flags(
            points,
            pairs,
            counts,
            predicate_flags=flags,
        )
    else:
        rows = _component_rows_from_parent_and_pairs(
            points,
            pairs,
            counts,
            predicate_flags=flags,
            parent=parent,
        )
    metadata = {
        "adapter": "simulate_fixed_radius_blocked_grouped_component_continuation_3d",
        "reference_only": True,
        "target_primitive": "generic_fixed_radius_blocked_grouped_component_continuation_3d",
        "candidate_native_contract": "fixed_radius_hit_stream_to_segmented_grouped_union_workspaces",
        "input_contract": "host_point_rows_fixed_radius_3d_with_predicate_flags",
        "hit_stream_pair_count": len(pairs),
        "predicate_true_count": sum(1 for flag in flags if flag),
        "segment_count": len(segments),
        "segment_target_hits": segment_target_hits,
        "segment_capacity_hits": segment_capacity,
        "max_segment_hits": max_segment_hits,
        "overflow_segment_count": overflow_segment_count,
        "fallback_to_unblocked_grouped_union": fallback_to_unblocked,
        "baseline_global_parent_atomic_attempts": local_or_segment_union_proposals,
        "global_parent_atomic_attempts": global_parent_atomic_attempts,
        "global_parent_atomic_successes": global_parent_atomic_successes,
        "local_or_segment_union_proposals": local_or_segment_union_proposals,
        "deduplicated_union_proposals": deduplicated_union_proposals,
        "proposal_rejection_rate": proposal_rejection_rate,
        "component_label_policy": "positive_root_index_labels_noise_minus_one",
        "app_independent_engine_required": True,
        "native_abi_added": False,
        "runtime_route_authorized": False,
        "rt_core_accelerated": False,
        "performance_claim_authorized": False,
        "release_claim_authorized": False,
    }
    return rows, metadata


def cpu_spatial_bucket_dbscan(
    points: tuple[rt.Point3D, ...],
    *,
    radius: float,
    min_neighbors: int,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    cells: dict[tuple[int, int, int], list[int]] = {}
    cell_size = radius if radius > 0.0 else 1.0
    radius_sq = radius * radius
    for index, point in enumerate(points):
        key = (math.floor(point.x / cell_size), math.floor(point.y / cell_size), math.floor(point.z / cell_size))
        cells.setdefault(key, []).append(index)

    neighbor_counts = [1 for _ in points]
    pairs: list[tuple[int, int]] = []
    offsets = tuple((dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1))
    for cell_key, left_indices in cells.items():
        cx, cy, cz = cell_key
        for ox, oy, oz in offsets:
            other_key = (cx + ox, cy + oy, cz + oz)
            if other_key not in cells or other_key < cell_key:
                continue
            right_indices = cells[other_key]
            for left_offset, left in enumerate(left_indices):
                start = left_offset + 1 if other_key == cell_key else 0
                for right in right_indices[start:]:
                    left_point = points[left]
                    right_point = points[right]
                    dx = left_point.x - right_point.x
                    dy = left_point.y - right_point.y
                    dz = left_point.z - right_point.z
                    if dx * dx + dy * dy + dz * dz <= radius_sq:
                        neighbor_counts[left] += 1
                        neighbor_counts[right] += 1
                        pairs.append((left, right))
    rows = _component_rows_from_pairs(points, pairs, neighbor_counts, min_neighbors=min_neighbors)
    return rows, {"cell_count": len(cells), "candidate_edge_count": len(pairs), "path": "cpu_spatial_bucket_reference"}


def _rows_from_partner_columns(columns: dict[str, object], *, partner: str) -> tuple[dict[str, object], ...]:
    if partner == "torch":
        point_ids = columns["point_ids"].detach().cpu().tolist()
        labels = columns["component_labels"].detach().cpu().tolist()
        core_flags = columns["is_core"].detach().cpu().tolist()
        counts = columns["neighbor_counts"].detach().cpu().tolist()
    elif partner == "cupy":
        import cupy

        point_ids = cupy.asnumpy(columns["point_ids"]).tolist()
        labels = cupy.asnumpy(columns["component_labels"]).tolist()
        core_flags = cupy.asnumpy(columns["is_core"]).tolist()
        counts = cupy.asnumpy(columns["neighbor_counts"]).tolist()
    else:
        raise ValueError("partner must be torch or cupy")
    return tuple(
        {
            "point_id": int(point_id),
            "cluster_id": int(label),
            "is_core": bool(core),
            "neighbor_count": int(count),
        }
        for point_id, label, core, count in zip(point_ids, labels, core_flags, counts)
    )


def _cluster_signature_from_host_columns(
    point_ids: Iterable[int],
    component_labels: Iterable[int],
    core_flags: Iterable[object],
) -> dict[str, object]:
    dense_by_original: dict[int, int] = {}
    cluster_sizes: dict[int, int] = {}
    next_label = 1
    core_count = 0
    noise_count = 0
    for _point_id, label_value, core_value in sorted(
        zip(point_ids, component_labels, core_flags),
        key=lambda item: int(item[0]),
    ):
        if bool(core_value):
            core_count += 1
        label = int(label_value)
        if label == NOISE_CLUSTER_ID:
            noise_count += 1
            continue
        if label not in dense_by_original:
            dense_by_original[label] = next_label
            next_label += 1
        dense_label = dense_by_original[label]
        cluster_sizes[dense_label] = cluster_sizes.get(dense_label, 0) + 1
    return {
        "cluster_sizes": dict(sorted(cluster_sizes.items())),
        "core_count": core_count,
        "noise_count": noise_count,
    }


def _cluster_signature_from_partner_columns(columns: dict[str, object], *, partner: str) -> dict[str, object]:
    if partner == "torch":
        point_ids = columns["point_ids"].detach().cpu().tolist()
        labels = columns["component_labels"].detach().cpu().tolist()
        core_flags = columns["is_core"].detach().cpu().tolist()
    elif partner == "cupy":
        import cupy

        point_ids = cupy.asnumpy(columns["point_ids"]).tolist()
        labels = cupy.asnumpy(columns["component_labels"]).tolist()
        core_flags = cupy.asnumpy(columns["is_core"]).tolist()
    else:
        raise ValueError("partner must be torch or cupy")
    return _cluster_signature_from_host_columns(point_ids, labels, core_flags)


def _optix_ranked_summaries_to_cupy_core_columns(
    points: tuple[rt.Point3D, ...],
    summaries: Iterable[dict[str, object]],
    *,
    min_neighbors: int,
):
    import cupy

    by_query_id = {int(row["query_id"]): row for row in summaries}
    counts: list[int] = []
    flags: list[int] = []
    for point in points:
        row = by_query_id.get(point.id)
        count = 0 if row is None else int(row["neighbor_count"])
        counts.append(count)
        flags.append(1 if count >= min_neighbors else 0)
    return {
        "neighbor_counts": cupy.asarray(counts, dtype=cupy.uint32),
        "core_flags": cupy.asarray(flags, dtype=cupy.uint32),
        "summary_rows": len(by_query_id),
    }


def _component_rows_from_neighbor_rows(
    points: tuple[rt.Point3D, ...],
    neighbor_rows: Iterable[dict[str, object]],
    *,
    min_neighbors: int,
) -> tuple[dict[str, object], ...]:
    index_by_id = {point.id: index for index, point in enumerate(points)}
    neighbor_counts = [0 for _ in points]
    pairs: set[tuple[int, int]] = set()
    for row in neighbor_rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        if query_id not in index_by_id or neighbor_id not in index_by_id:
            continue
        left = index_by_id[query_id]
        right = index_by_id[neighbor_id]
        neighbor_counts[left] += 1
        if left != right:
            pairs.add((min(left, right), max(left, right)))
    return _component_rows_from_pairs(points, sorted(pairs), neighbor_counts, min_neighbors=min_neighbors)


def cluster_signature(rows: Iterable[dict[str, object]]) -> dict[str, object]:
    cluster_sizes: dict[int, int] = {}
    core_count = 0
    noise_count = 0
    for row in rows:
        if bool(row["is_core"]):
            core_count += 1
        cluster_id = int(row["cluster_id"])
        if cluster_id == NOISE_CLUSTER_ID:
            noise_count += 1
        else:
            cluster_sizes[cluster_id] = cluster_sizes.get(cluster_id, 0) + 1
    return {
        "cluster_sizes": dict(sorted(cluster_sizes.items())),
        "core_count": core_count,
        "noise_count": noise_count,
    }


def _densify_cluster_labels(rows: Iterable[dict[str, object]]) -> tuple[dict[str, object], ...]:
    dense_by_original: dict[int, int] = {}
    next_label = 1
    normalized: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: int(item["point_id"])):
        item = dict(row)
        cluster_id = int(item["cluster_id"])
        if cluster_id != NOISE_CLUSTER_ID:
            if cluster_id not in dense_by_original:
                dense_by_original[cluster_id] = next_label
                next_label += 1
            item["cluster_id"] = dense_by_original[cluster_id]
        normalized.append(item)
    return tuple(normalized)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_grouped_stream_timing_breakdown(
    timing_sec: dict[str, float],
    metadata: dict[str, object],
    *,
    elapsed_sec: float,
) -> dict[str, object]:
    """Build a host-observed grouped-stream timing packet without changing runtime semantics."""
    sec = {key: float(value) for key, value in timing_sec.items()}
    native_metadata = metadata.get("native_grouped_stream_metadata", {})
    if not isinstance(native_metadata, dict):
        native_metadata = {}
    count_metadata = metadata.get("count_metadata", {})
    if not isinstance(count_metadata, dict):
        count_metadata = {}
    count_native_metadata = count_metadata.get("native_metadata", {})
    if not isinstance(count_native_metadata, dict):
        count_native_metadata = {}

    grouped_native_sec = _optional_float(native_metadata.get("native_elapsed_sec")) or 0.0
    count_native_sec = _optional_float(count_native_metadata.get("native_elapsed_sec")) or 0.0
    count_native_current_run_sec = 0.0 if metadata.get("core_flag_cache_reused") else count_native_sec
    adapter_run_sec = sec.get("adapter_run_sec", 0.0)
    known_host_phase_sec = sum(sec.values())

    derived_sec = {
        "elapsed_sec": float(elapsed_sec),
        "known_host_phase_sec": known_host_phase_sec,
        "unattributed_elapsed_sec": max(0.0, float(elapsed_sec) - known_host_phase_sec),
        "grouped_native_sec": grouped_native_sec,
        "count_native_current_run_sec": count_native_current_run_sec,
        "known_native_current_run_sec": grouped_native_sec + count_native_current_run_sec,
        "adapter_non_native_estimated_sec": max(
            0.0,
            adapter_run_sec - grouped_native_sec - count_native_current_run_sec,
        ),
    }
    return {
        "schema": RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA,
        "host_observed_sec": sec,
        "derived_sec": derived_sec,
        "notes": [
            "Host-observed timings are diagnostic and may include async GPU synchronization effects.",
            "Native elapsed fields come from RTDL native metadata where available.",
            "This timing packet does not authorize a paper, broad RT-core, or whole-app speedup claim.",
        ],
        "performance_claim_authorized": False,
    }


def run_rt_dbscan_benchmark(
    *,
    mode: str,
    dataset: str,
    point_count: int | None,
    radius: float | None,
    min_neighbors: int | None,
    seed: int,
    partner: str,
    include_rows: bool,
    validate: bool,
    adjacency_edge_budget: int | None = None,
    chunk_adjacency_edge_budget: int | None = None,
    reuse_chunk_neighbor_index_workspace: bool = False,
    chunk_neighbor_index_workspace_pool_size: int = 0,
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
) -> dict[str, object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_point_count = int(point_count if point_count is not None else config["point_count"])
    resolved_radius = float(radius if radius is not None else config["radius"])
    resolved_min_neighbors = int(min_neighbors if min_neighbors is not None else config["min_neighbors"])
    if include_rows and mode in {
        "optix_rt_core_grouped_stream_cupy_column_signature_3d",
        "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
    }:
        raise ValueError("column-signature mode does not materialize Python rows")
    if mode == "planned_rt_dbscan":
        plan = plan_rt_dbscan_execution(dataset, resolved_point_count)
        selected_mode = str(plan["selected_mode"])
        payload = run_rt_dbscan_benchmark(
            mode=selected_mode,
            dataset=dataset,
            point_count=resolved_point_count,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            seed=seed,
            partner=partner,
            include_rows=include_rows,
            validate=validate,
            adjacency_edge_budget=adjacency_edge_budget,
            chunk_adjacency_edge_budget=chunk_adjacency_edge_budget,
            reuse_chunk_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
            chunk_neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
            grouped_union_query_block_size=grouped_union_query_block_size,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
        )
        payload["mode"] = mode
        payload["selected_mode"] = selected_mode
        metadata = dict(payload.get("metadata", {}))
        metadata["execution_plan"] = plan
        payload["metadata"] = metadata
        claim_boundary = dict(payload.get("claim_boundary", {}))
        claim_boundary["planned_execution"] = True
        claim_boundary["automatic_hidden_dispatcher"] = False
        claim_boundary["release_claim_authorized"] = False
        payload["claim_boundary"] = claim_boundary
        return payload
    if mode == "planned_rt_dbscan_continuation":
        plan = plan_rt_dbscan_continuation_execution(
            dataset,
            resolved_point_count,
            directed_edge_budget=adjacency_edge_budget,
        )
        selected_mode = str(plan["selected_mode"])
        payload = run_rt_dbscan_benchmark(
            mode=selected_mode,
            dataset=dataset,
            point_count=resolved_point_count,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            seed=seed,
            partner=partner,
            include_rows=include_rows,
            validate=validate,
            adjacency_edge_budget=adjacency_edge_budget,
            chunk_adjacency_edge_budget=chunk_adjacency_edge_budget,
            reuse_chunk_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
            chunk_neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
            grouped_union_query_block_size=grouped_union_query_block_size,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
        )
        payload["mode"] = mode
        payload["selected_mode"] = selected_mode
        metadata = dict(payload.get("metadata", {}))
        metadata["execution_plan"] = plan
        payload["metadata"] = metadata
        claim_boundary = dict(payload.get("claim_boundary", {}))
        claim_boundary["planned_continuation_execution"] = True
        claim_boundary["automatic_hidden_dispatcher"] = False
        claim_boundary["release_claim_authorized"] = False
        claim_boundary["paper_reproduction_claim_authorized"] = False
        payload["claim_boundary"] = claim_boundary
        return payload
    points = make_rt_dbscan_points(dataset, point_count=resolved_point_count, seed=seed)

    start = time.perf_counter()
    timing_breakdown_sec: dict[str, float] | None = None
    signature_override: dict[str, object] | None = None
    metadata: dict[str, object]
    if mode == "cpu_reference":
        rows, metadata = cpu_spatial_bucket_dbscan(points, radius=resolved_radius, min_neighbors=resolved_min_neighbors)
    elif mode == "rtdl_cpu_rows":
        neighbor_rows = rt.fixed_radius_neighbors_cpu(
            points,
            points,
            radius=resolved_radius,
            k_max=len(points),
        )
        rows = _component_rows_from_neighbor_rows(points, neighbor_rows, min_neighbors=resolved_min_neighbors)
        metadata = {
            "path": "rtdl_cpu_fixed_radius_neighbor_rows",
            "neighbor_row_count": len(neighbor_rows),
            "native_engine_row_contract": "generic_fixed_radius_neighbors_3d_rows",
        }
    elif mode == "embree_prepared_rows":
        kernel = make_fixed_radius_neighbors_3d_embree_kernel(
            radius=resolved_radius,
            k_max=len(points),
        )
        neighbor_rows = rt.run_embree(
            kernel,
            query_points=points,
            search_points=points,
        )
        rows = _component_rows_from_neighbor_rows(points, neighbor_rows, min_neighbors=resolved_min_neighbors)
        metadata = {
            "path": "embree_fixed_radius_neighbor_rows_3d",
            "neighbor_row_count": len(neighbor_rows),
            "native_engine_row_contract": "generic_fixed_radius_neighbors_3d_rows",
            "native_execution_path": "embree_point_query_fixed_radius_3d",
            "embree_backend_used": True,
            "rt_core_accelerated": False,
            "materializes_neighbor_rows": True,
        }
    elif mode == "partner_spatial_bucket_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner=partner)
        result = rt.radius_graph_components_3d_spatial_bucket_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner=partner,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner=partner)
        metadata = dict(result["metadata"])
    elif mode == "partner_cupy_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        result = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
    elif mode == "partner_cupy_prepared_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        prepared_grid = rt.prepare_radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="cupy",
        )
        result = rt.radius_graph_components_3d_cupy_prepared_grid_partner_columns(
            prepared_grid,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_prepared_grid_radius_graph_components_3d",
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
            }
        )
    elif mode == "partner_cupy_prepared_adjacency_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        prepared_adjacency = rt.prepare_radius_graph_adjacency_3d_cupy_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="cupy",
        )
        result = rt.radius_graph_components_3d_cupy_prepared_adjacency_partner_columns(
            prepared_adjacency,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_prepared_directed_adjacency_radius_graph_components_3d",
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": True,
            }
        )
    elif mode == "optix_core_flags_cupy_grid_components_3d":
        if resolved_min_neighbors > 64:
            raise ValueError("optix_core_flags_cupy_grid_components_3d currently requires min_neighbors <= 64")
        optix_start = time.perf_counter()
        with rt.prepare_optix_fixed_radius_neighbors_3d(points, max_radius=resolved_radius) as prepared:
            summaries = prepared.run_ranked_summary(
                points,
                radius=resolved_radius,
                k_max=max(1, resolved_min_neighbors),
            )
        optix_elapsed = time.perf_counter() - optix_start
        core_columns = _optix_ranked_summaries_to_cupy_core_columns(
            points,
            summaries,
            min_neighbors=resolved_min_neighbors,
        )
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        continuation_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            core_flags=core_columns["core_flags"],
            neighbor_counts=core_columns["neighbor_counts"],
            core_flag_source="optix_ranked_fixed_radius_summary_threshold",
            return_metadata=True,
        )
        continuation_elapsed = time.perf_counter() - continuation_start
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_core_flags_cupy_grid_radius_graph_components_3d",
                "optix_core_flag_summary_rows": core_columns["summary_rows"],
                "optix_core_flag_sec": optix_elapsed,
                "cupy_component_continuation_sec": continuation_elapsed,
                "native_engine_summary_contract": "generic_prepared_ranked_fixed_radius_neighbor_summaries_3d",
                "native_execution_path": "prepared_uniform_cell_cuda_grid_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": False,
                "materializes_neighbor_summaries": True,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
            }
        )
    elif mode == "optix_rt_core_flags_cupy_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        output_columns = rt.allocate_fixed_radius_count_threshold_3d_partner_device_output_columns(
            len(points),
            partner="cupy",
        )
        optix_start = time.perf_counter()
        with rt.prepare_optix_fixed_radius_count_threshold_3d(points, max_radius=resolved_radius) as prepared:
            threshold_result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
                prepared,
                points,
                radius=resolved_radius,
                threshold=resolved_min_neighbors,
                partner="cupy",
                output_columns=output_columns,
                return_metadata=True,
            )
        optix_elapsed = time.perf_counter() - optix_start
        continuation_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            core_flags=threshold_result["columns"]["threshold_flags"],
            neighbor_counts=threshold_result["columns"]["neighbor_counts"],
            core_flag_source="optix_rt_fixed_radius_count_threshold_3d_device_outputs",
            return_metadata=True,
        )
        continuation_elapsed = time.perf_counter() - continuation_start
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_count_threshold_cupy_grid_radius_graph_components_3d",
                "optix_rt_count_threshold_sec": optix_elapsed,
                "cupy_component_continuation_sec": continuation_elapsed,
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "threshold_metadata": threshold_result["metadata"],
            }
        )
    elif mode == "optix_rt_core_flags_cupy_prepared_grid_components_3d":
        with rt.prepare_optix_cupy_radius_graph_components_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
        ) as prepared:
            result = rt.radius_graph_components_3d_optix_cupy_prepared_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_count_threshold_cupy_prepared_grid_radius_graph_components_3d",
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
            }
        )
    elif mode == "optix_rt_core_adjacency_cupy_components_3d":
        with rt.prepare_optix_cupy_radius_graph_adjacency_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
        ) as prepared:
            result = rt.radius_graph_components_3d_optix_cupy_prepared_adjacency_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_adjacency_cupy_radius_graph_components_3d",
                "native_engine_summary_contract": "generic_prepared_fixed_radius_adjacency_3d_device_columns",
                "native_execution_path": "prepared_rt_core_adjacency_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": True,
                "neighbor_count_policy": "exact_full_degree_from_prepared_rt_adjacency_stream",
            }
        )
    elif mode == "optix_rt_core_chunked_adjacency_cupy_components_3d":
        with rt.prepare_optix_cupy_radius_graph_chunked_adjacency_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
            max_directed_edges_per_chunk=chunk_adjacency_edge_budget,
            reuse_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
            neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
        ) as prepared:
            result = rt.radius_graph_components_3d_optix_cupy_prepared_chunked_adjacency_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_chunked_adjacency_cupy_radius_graph_components_3d",
                "native_engine_summary_contract": "generic_prepared_fixed_radius_adjacency_3d_device_columns",
                "native_execution_path": "prepared_rt_core_chunked_adjacency_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "materializes_bounded_directed_adjacency_chunks": True,
                "neighbor_count_policy": "exact_full_degree_from_prepared_rt_chunked_adjacency_stream",
            }
        )
    elif mode == "optix_rt_core_grouped_stream_cupy_components_3d" or mode in {
        "optix_rt_core_grouped_stream_cupy_column_signature_3d",
        "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
        "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
    }:
        blocked_grouped_stream = mode.startswith("optix_rt_core_grouped_stream_blocked")
        resolved_query_block_size = (
            int(grouped_union_query_block_size)
            if grouped_union_query_block_size is not None
            else DEFAULT_GROUPED_UNION_QUERY_BLOCK_SIZE
        )
        timing_breakdown_sec = {}
        prepare_start = time.perf_counter()
        with rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
            grouped_union_query_block_size=resolved_query_block_size if blocked_grouped_stream else None,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
        ) as prepared:
            timing_breakdown_sec["prepare_sec"] = time.perf_counter() - prepare_start
            adapter_start = time.perf_counter()
            result = rt.radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
            timing_breakdown_sec["adapter_run_sec"] = time.perf_counter() - adapter_start
        column_signature_mode = mode in {
            "optix_rt_core_grouped_stream_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
        }
        if column_signature_mode:
            signature_start = time.perf_counter()
            signature_override = _cluster_signature_from_partner_columns(result["columns"], partner="cupy")
            timing_breakdown_sec["column_signature_sec"] = time.perf_counter() - signature_start
            rows = ()
        else:
            rows_start = time.perf_counter()
            rows = _rows_from_partner_columns(result["columns"], partner="cupy")
            timing_breakdown_sec["rows_materialization_sec"] = time.perf_counter() - rows_start
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": (
                    "optix_rt_grouped_stream_blocked_cupy_radius_graph_column_signature_3d"
                    if mode == "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d"
                    else "optix_rt_grouped_stream_blocked_cupy_radius_graph_components_3d"
                    if mode == "optix_rt_core_grouped_stream_blocked_cupy_components_3d"
                    else "optix_rt_grouped_stream_cupy_radius_graph_column_signature_3d"
                    if mode == "optix_rt_core_grouped_stream_cupy_column_signature_3d"
                    else "optix_rt_grouped_stream_cupy_radius_graph_components_3d"
                ),
                "native_engine_summary_contract": (
                    "generic_prepared_fixed_radius_grouped_union_3d_self_range_device_workspaces"
                    if blocked_grouped_stream
                    else "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces"
                ),
                "native_execution_path": (
                    "prepared_rt_core_grouped_union_3d_self_query_blocked_ranges"
                    if blocked_grouped_stream
                    else "prepared_rt_core_grouped_union_3d_self_query"
                ),
                "query_source": (
                    "prepared_search_points_self_query_device_range"
                    if blocked_grouped_stream
                    else "prepared_search_points_self_query_device"
                ),
                "grouped_union_query_blocked_candidate": blocked_grouped_stream,
                "grouped_union_query_block_size": resolved_query_block_size if blocked_grouped_stream else None,
                "grouped_union_same_root_culling_enabled": grouped_union_same_root_culling,
                "grouped_union_direct_side_effect_enabled": grouped_union_direct_side_effect,
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "materializes_bounded_directed_adjacency_chunks": False,
                "materializes_python_rows": mode in {
                    "optix_rt_core_grouped_stream_cupy_components_3d",
                    "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
                },
                "signature_source": (
                    "partner_column_arrays_no_python_row_dicts"
                    if column_signature_mode
                    else "python_row_dicts_after_label_densification"
                ),
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
            }
        )
    elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        output_columns = rt.allocate_fixed_radius_count_threshold_3d_partner_device_output_columns(
            len(points),
            partner="cupy",
        )
        optix_start = time.perf_counter()
        with rt.prepare_optix_fixed_radius_count_threshold_3d(points, max_radius=resolved_radius) as prepared:
            threshold_result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
                prepared,
                points,
                radius=resolved_radius,
                threshold=resolved_min_neighbors,
                partner="cupy",
                output_columns=output_columns,
                return_metadata=True,
            )
        optix_elapsed = time.perf_counter() - optix_start
        continuation_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_microcell_graph_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            core_flags=threshold_result["columns"]["threshold_flags"],
            neighbor_counts=threshold_result["columns"]["neighbor_counts"],
            core_flag_source="optix_rt_fixed_radius_count_threshold_3d_device_outputs",
            return_metadata=True,
        )
        continuation_elapsed = time.perf_counter() - continuation_start
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_count_threshold_cupy_microcell_radius_graph_components_3d",
                "optix_rt_count_threshold_sec": optix_elapsed,
                "cupy_component_continuation_sec": continuation_elapsed,
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "threshold_metadata": threshold_result["metadata"],
            }
        )
    elif mode == "partner_core_flags_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner=partner)
        result = rt.fixed_radius_count_threshold_3d_partner_columns(
            point_columns,
            point_columns,
            radius=resolved_radius,
            threshold=resolved_min_neighbors,
            partner=partner,
            return_metadata=True,
        )
        columns = result["columns"]
        if partner == "torch":
            point_ids = columns["query_ids"].detach().cpu().tolist()
            counts = columns["neighbor_counts"].detach().cpu().tolist()
            flags = columns["threshold_flags"].detach().cpu().tolist()
        else:
            import cupy

            point_ids = cupy.asnumpy(columns["query_ids"]).tolist()
            counts = cupy.asnumpy(columns["neighbor_counts"]).tolist()
            flags = cupy.asnumpy(columns["threshold_flags"]).tolist()
        rows = tuple(
            {
                "point_id": int(point_id),
                "cluster_id": 1 if int(flag) else NOISE_CLUSTER_ID,
                "is_core": bool(flag),
                "neighbor_count": int(count),
            }
            for point_id, count, flag in zip(point_ids, counts, flags)
        )
        metadata = dict(result["metadata"])
        metadata["path"] = "generic_3d_core_flag_only_not_full_dbscan"
    elif mode == "optix_prepared_rows":
        with rt.prepare_optix_fixed_radius_neighbors_3d(points, max_radius=resolved_radius) as prepared:
            neighbor_rows = prepared.run_exact(points, radius=resolved_radius, k_max=len(points))
        rows = _component_rows_from_neighbor_rows(points, neighbor_rows, min_neighbors=resolved_min_neighbors)
        metadata = {
            "path": "optix_prepared_fixed_radius_neighbor_rows_3d",
            "neighbor_row_count": len(neighbor_rows),
            "native_engine_row_contract": "generic_prepared_fixed_radius_neighbors_3d_rows",
            "native_execution_path": "prepared_uniform_cell_cuda_grid_3d",
            "optix_backend_used": True,
            "rt_core_accelerated": False,
            "materializes_neighbor_rows": True,
        }
    else:
        raise ValueError("unsupported mode")
    if signature_override is None:
        densify_start = time.perf_counter()
        rows = _densify_cluster_labels(rows)
        if timing_breakdown_sec is not None:
            timing_breakdown_sec["densify_cluster_labels_sec"] = time.perf_counter() - densify_start
    elapsed = time.perf_counter() - start
    if timing_breakdown_sec is not None:
        metadata["benchmark_timing_breakdown"] = _build_grouped_stream_timing_breakdown(
            timing_breakdown_sec,
            metadata,
            elapsed_sec=elapsed,
        )

    signature = signature_override if signature_override is not None else cluster_signature(rows)
    reference_signature = None
    matches_reference = None
    if validate and mode != "cpu_reference":
        reference_rows, _ = cpu_spatial_bucket_dbscan(points, radius=resolved_radius, min_neighbors=resolved_min_neighbors)
        reference_signature = cluster_signature(reference_rows)
        matches_reference = signature == reference_signature
    elif mode == "cpu_reference":
        reference_signature = signature
        matches_reference = True

    payload = {
        "app": "rt_dbscan_benchmark",
        "paper": {
            "title": "RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware",
            "venue": "IPDPS 2023",
            "authors": ["Vani Nagarajan", "Milind Kulkarni"],
            "doi": "10.1109/IPDPS54959.2023.00100",
        },
        "mode": mode,
        "dataset": dataset,
        "point_count": len(points),
        "radius": resolved_radius,
        "min_neighbors": resolved_min_neighbors,
        "seed": seed,
        "elapsed_sec": elapsed,
        "signature": signature,
        "reference_signature": reference_signature,
        "matches_reference": matches_reference,
        "metadata": metadata,
        "claim_boundary": {
            "paper_dataset_reproduction": False,
            "paper_speedup_claim_authorized": False,
            "native_dbscan_abi_added": False,
            "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
            "full_dbscan": mode != "partner_core_flags_3d",
            "host_bucket_index_used": bool(metadata.get("host_bucket_index_used", False)),
        },
    }
    if include_rows:
        payload["rows"] = rows
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RT-DBSCAN-inspired RTDL v2.x benchmark app.")
    parser.add_argument(
        "--mode",
        choices=(
            "cpu_reference",
            "planned_rt_dbscan",
            "planned_rt_dbscan_continuation",
            "rtdl_cpu_rows",
            "embree_prepared_rows",
            "partner_spatial_bucket_3d",
            "partner_cupy_grid_components_3d",
            "partner_cupy_prepared_grid_components_3d",
            "partner_cupy_prepared_adjacency_components_3d",
            "optix_core_flags_cupy_grid_components_3d",
            "optix_rt_core_flags_cupy_grid_components_3d",
            "optix_rt_core_flags_cupy_prepared_grid_components_3d",
            "optix_rt_core_adjacency_cupy_components_3d",
            "optix_rt_core_chunked_adjacency_cupy_components_3d",
            "optix_rt_core_grouped_stream_cupy_components_3d",
            "optix_rt_core_grouped_stream_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
            "optix_rt_core_flags_cupy_microcell_graph_components_3d",
            "partner_core_flags_3d",
            "optix_prepared_rows",
        ),
        default="cpu_reference",
    )
    parser.add_argument("--dataset", choices=tuple(DEFAULT_DATASET_CONFIG), default="tiny")
    parser.add_argument("--point-count", type=int, default=None)
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--min-neighbors", type=int, default=None)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--partner", choices=("torch", "cupy"), default="cupy")
    parser.add_argument("--include-rows", action="store_true")
    parser.add_argument("--no-validation", action="store_true")
    parser.add_argument("--adjacency-edge-budget", type=int, default=None)
    parser.add_argument("--chunk-adjacency-edge-budget", type=int, default=None)
    parser.add_argument("--reuse-chunk-neighbor-index-workspace", action="store_true")
    parser.add_argument("--chunk-neighbor-index-workspace-pool-size", type=int, default=0)
    parser.add_argument("--grouped-union-query-block-size", type=int, default=None)
    parser.add_argument("--disable-grouped-union-same-root-culling", action="store_true")
    parser.add_argument("--enable-grouped-union-direct-side-effect", action="store_true")
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_rt_dbscan_benchmark(
                mode=args.mode,
                dataset=args.dataset,
                point_count=args.point_count,
                radius=args.radius,
                min_neighbors=args.min_neighbors,
                seed=args.seed,
                partner=args.partner,
                include_rows=args.include_rows,
                validate=not args.no_validation,
                adjacency_edge_budget=args.adjacency_edge_budget,
                chunk_adjacency_edge_budget=args.chunk_adjacency_edge_budget,
                reuse_chunk_neighbor_index_workspace=args.reuse_chunk_neighbor_index_workspace,
                chunk_neighbor_index_workspace_pool_size=args.chunk_neighbor_index_workspace_pool_size,
                grouped_union_query_block_size=args.grouped_union_query_block_size,
                grouped_union_same_root_culling=not args.disable_grouped_union_same_root_culling,
                grouped_union_direct_side_effect=args.enable_grouped_union_direct_side_effect,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
