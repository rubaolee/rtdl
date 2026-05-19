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


def _component_rows_from_pairs(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: list[int],
    *,
    min_neighbors: int,
) -> tuple[dict[str, object], ...]:
    is_core = [count >= min_neighbors for count in neighbor_counts]
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
                "neighbor_count": int(neighbor_counts[index]),
            }
        )
    return tuple(rows)


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
) -> dict[str, object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_point_count = int(point_count if point_count is not None else config["point_count"])
    resolved_radius = float(radius if radius is not None else config["radius"])
    resolved_min_neighbors = int(min_neighbors if min_neighbors is not None else config["min_neighbors"])
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
    points = make_rt_dbscan_points(dataset, point_count=resolved_point_count, seed=seed)

    start = time.perf_counter()
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
    rows = _densify_cluster_labels(rows)
    elapsed = time.perf_counter() - start

    signature = cluster_signature(rows)
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
            "rtdl_cpu_rows",
            "partner_spatial_bucket_3d",
            "partner_cupy_grid_components_3d",
            "partner_cupy_prepared_grid_components_3d",
            "optix_core_flags_cupy_grid_components_3d",
            "optix_rt_core_flags_cupy_grid_components_3d",
            "optix_rt_core_flags_cupy_prepared_grid_components_3d",
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
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
