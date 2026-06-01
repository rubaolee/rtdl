from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_v2_user_benchmark as lab
from rtdsl.reference import Point


@dataclass(frozen=True)
class HausdorffResult:
    distance: float
    direction: str
    source_index: int
    target_index: int
    elapsed_sec: float
    method: str


@dataclass(frozen=True)
class HausdorffThresholdResult:
    distance_upper_bound: float
    distance_lower_bound: float
    tolerance: float
    direction: str
    elapsed_sec: float
    method: str
    backend: str
    iterations: int
    rt_core_accelerated: bool
    exact_value: bool


@dataclass(frozen=True)
class HausdorffRtNearestResult:
    distance: float
    direction: str
    source_index: int
    target_index: int
    elapsed_sec: float
    method: str
    backend: str
    rt_core_accelerated: bool
    exact_value: bool
    witness_radius: float
    radius_strategy: str
    threshold_iterations: int


def _as_point_columns(points: Sequence[Sequence[float]] | np.ndarray, *, name: str) -> dict[str, np.ndarray]:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError(f"{name} must be an Nx2 array-like object")
    if array.shape[0] == 0:
        raise ValueError(f"{name} must contain at least one point")
    return {
        "ids": np.arange(array.shape[0], dtype=np.int64),
        "x": np.ascontiguousarray(array[:, 0], dtype=np.float64),
        "y": np.ascontiguousarray(array[:, 1], dtype=np.float64),
    }


def _select_directed_runner(method: str, *, cache_dir: Path):
    if method == "rtdl_v2_user_cuda":
        return lab.run_rtdl_v2_user_cuda
    if method == "openmp_cpu":
        return lambda source, target: lab.run_cpu_openmp(source, target, cache_dir=cache_dir)
    if method == "cuda_cpp":
        return lambda source, target: lab.run_cuda_ctypes_baseline(source, target, cache_dir=cache_dir)
    if method == "cupy_rawkernel":
        return lab.run_cuda_rawkernel
    if method == "cupy_grouped_grid_rawkernel":
        return lab.run_cuda_grouped_grid_rawkernel
    raise ValueError(
        "method must be one of: rtdl_v2_user_cuda, openmp_cpu, cuda_cpp, "
        "cupy_rawkernel, cupy_grouped_grid_rawkernel"
    )


def _columns_to_points(columns: dict[str, np.ndarray]) -> tuple[Point, ...]:
    return tuple(
        Point(id=int(columns["ids"][i]), x=float(columns["x"][i]), y=float(columns["y"][i]))
        for i in range(int(columns["ids"].size))
    )


def _pack_point_columns_for_optix(columns: dict[str, np.ndarray]):
    from rtdsl.optix_runtime import pack_points

    return pack_points(
        ids=np.asarray(columns["ids"], dtype=np.int64),
        x=np.asarray(columns["x"], dtype=np.float64),
        y=np.asarray(columns["y"], dtype=np.float64),
        dimension=2,
    )


def _build_uniform_point_group_columns(
    columns: dict[str, np.ndarray],
    *,
    target_points_per_group: int = 64,
) -> tuple[dict[str, np.ndarray], tuple[dict[str, object], ...]]:
    if target_points_per_group <= 0:
        raise ValueError("target_points_per_group must be positive")
    count = int(columns["ids"].size)
    if count == 0:
        empty = {
            "ids": np.asarray([], dtype=np.int64),
            "x": np.asarray([], dtype=np.float64),
            "y": np.asarray([], dtype=np.float64),
        }
        return empty, ()
    grid_width = max(1, int(math.ceil(math.sqrt(count / float(target_points_per_group)))))
    x = np.asarray(columns["x"], dtype=np.float64)
    y = np.asarray(columns["y"], dtype=np.float64)
    min_x = float(x.min())
    max_x = float(x.max())
    min_y = float(y.min())
    max_y = float(y.max())
    span_x = max(max_x - min_x, 1.0e-12)
    span_y = max(max_y - min_y, 1.0e-12)
    cell_x = np.floor((x - min_x) / span_x * grid_width).astype(np.int64)
    cell_y = np.floor((y - min_y) / span_y * grid_width).astype(np.int64)
    np.clip(cell_x, 0, grid_width - 1, out=cell_x)
    np.clip(cell_y, 0, grid_width - 1, out=cell_y)
    cell_ids = cell_y * grid_width + cell_x
    order = np.argsort(cell_ids, kind="stable")
    sorted_columns = {
        "ids": np.ascontiguousarray(columns["ids"][order], dtype=np.int64),
        "x": np.ascontiguousarray(x[order], dtype=np.float64),
        "y": np.ascontiguousarray(y[order], dtype=np.float64),
    }
    groups: list[dict[str, object]] = []
    start = 0
    while start < count:
        cell_id = int(cell_ids[order[start]])
        end = start + 1
        while end < count and int(cell_ids[order[end]]) == cell_id:
            end += 1
        group_x = sorted_columns["x"][start:end]
        group_y = sorted_columns["y"][start:end]
        groups.append(
            {
                "id": len(groups),
                "point_offset": start,
                "point_count": end - start,
                "min_x": float(group_x.min()),
                "min_y": float(group_y.min()),
                "max_x": float(group_x.max()),
                "max_y": float(group_y.max()),
            }
        )
        start = end
    return sorted_columns, tuple(groups)


def default_target_points_per_group(point_count: int) -> int:
    """Return a scale-aware default for grouped point-set RT traversal.

    Small rows should keep groups fine enough for useful pruning. Large rows
    need coarser groups to keep OptiX primitive count and launch-side metadata
    under control. The powers-of-two shape keeps benchmark sweeps reproducible.
    """

    count = max(1, int(point_count))
    target = max(64, count // 128)
    return min(8192, 1 << int(math.ceil(math.log2(target))))


def default_adaptive_target_points_per_group(point_count: int) -> int:
    """Return the warmed v2.5 default for adaptive grouped RT traversal."""

    return max(512, default_target_points_per_group(point_count))


def _resolve_target_points_per_group(columns: dict[str, np.ndarray], target_points_per_group: int | None) -> int:
    if target_points_per_group is None:
        return default_target_points_per_group(int(columns["ids"].size))
    if target_points_per_group <= 0:
        raise ValueError("target_points_per_group must be positive")
    return int(target_points_per_group)


def _resolve_adaptive_target_points_per_group(
    columns: dict[str, np.ndarray],
    target_points_per_group: int | None,
) -> int:
    if target_points_per_group is None:
        return default_adaptive_target_points_per_group(int(columns["ids"].size))
    return _resolve_target_points_per_group(columns, target_points_per_group)


def _build_uniform_point_groups(
    columns: dict[str, np.ndarray],
    *,
    target_points_per_group: int = 64,
) -> tuple[tuple[Point, ...], tuple[dict[str, object], ...]]:
    sorted_columns, groups = _build_uniform_point_group_columns(
        columns,
        target_points_per_group=target_points_per_group,
    )
    return _columns_to_points(sorted_columns), groups


def _point_set_upper_bound(points_a: dict[str, np.ndarray], points_b: dict[str, np.ndarray]) -> float:
    min_x = min(float(points_a["x"].min()), float(points_b["x"].min()))
    max_x = max(float(points_a["x"].max()), float(points_b["x"].max()))
    min_y = min(float(points_a["y"].min()), float(points_b["y"].min()))
    max_y = max(float(points_a["y"].max()), float(points_b["y"].max()))
    return math.hypot(max_x - min_x, max_y - min_y)


def _prepared_radius_guard(radius: float) -> float:
    """Return a conservative preparation radius for exact-radius OptiX queries."""

    value = float(radius)
    if value <= 0.0:
        return 0.0
    return value + max(1.0e-9, abs(value) * 1.0e-6)


def _subset_point_columns(columns: dict[str, np.ndarray], indices: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "ids": np.ascontiguousarray(np.asarray(columns["ids"], dtype=np.int64)[indices], dtype=np.int64),
        "x": np.ascontiguousarray(np.asarray(columns["x"], dtype=np.float64)[indices], dtype=np.float64),
        "y": np.ascontiguousarray(np.asarray(columns["y"], dtype=np.float64)[indices], dtype=np.float64),
    }


def _seed_sample_point_columns(
    columns: dict[str, np.ndarray],
    *,
    sample_count: int,
    seed: int,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    count = int(columns["ids"].size)
    if sample_count <= 0 or sample_count >= count:
        indices = np.arange(count, dtype=np.int64)
        return _subset_point_columns(columns, indices), indices
    x = np.asarray(columns["x"], dtype=np.float64)
    y = np.asarray(columns["y"], dtype=np.float64)
    extrema = np.asarray(
        [int(x.argmin()), int(x.argmax()), int(y.argmin()), int(y.argmax())],
        dtype=np.int64,
    )
    extrema = np.unique(extrema)
    budget = max(0, int(sample_count) - int(extrema.size))
    all_indices = np.arange(count, dtype=np.int64)
    remaining = np.setdiff1d(all_indices, extrema, assume_unique=False)
    if budget > 0 and remaining.size > 0:
        rng = np.random.default_rng(seed)
        chosen = rng.choice(remaining, size=min(budget, int(remaining.size)), replace=False)
        indices = np.sort(np.concatenate([extrema, chosen]).astype(np.int64))
    else:
        indices = np.sort(extrema)
    return _subset_point_columns(columns, indices), indices


def _reduce_nearest_witness_rows(
    source_points: tuple[Point, ...],
    target_points: tuple[Point, ...],
    target_columns: dict[str, np.ndarray],
    rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    if len(rows) != len(source_points):
        raise RuntimeError("nearest_witness_rows must return one row per source point")
    target_by_id = {int(point.id): point for point in target_points}
    target_id_to_index = {int(target_columns["ids"][i]): i for i in range(int(target_columns["ids"].size))}
    best_distance = -1.0
    best_source_index = -1
    best_target_index = -1
    for source_index, row in enumerate(rows):
        neighbor_id = int(row["neighbor_id"])
        if neighbor_id == 0xFFFFFFFF:
            raise RuntimeError("nearest_witness_rows did not find a witness; increase radius")
        target_point = target_by_id[neighbor_id]
        source_point = source_points[source_index]
        distance = math.hypot(source_point.x - target_point.x, source_point.y - target_point.y)
        if distance > best_distance or (
            math.isclose(distance, best_distance) and source_index < best_source_index
        ):
            best_distance = distance
            best_source_index = source_index
            best_target_index = target_id_to_index[neighbor_id]
    return {
        "distance": best_distance,
        "source_index": best_source_index,
        "target_index": best_target_index,
        "row_count": len(rows),
    }


def _reduce_nearest_max_distance_row(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    row: dict[str, object],
) -> dict[str, object]:
    source_id = int(row["query_id"])
    target_id = int(row["neighbor_id"])
    if source_id == 0xFFFFFFFF or target_id == 0xFFFFFFFF or not math.isfinite(float(row["distance"])):
        raise RuntimeError("nearest_max_distance_row did not find a witness; increase radius")
    source_ids = np.asarray(source_columns["ids"], dtype=np.int64)
    target_ids = np.asarray(target_columns["ids"], dtype=np.int64)
    source_matches = np.nonzero(source_ids == source_id)[0]
    target_matches = np.nonzero(target_ids == target_id)[0]
    if source_matches.size == 0:
        raise RuntimeError(f"nearest_max_distance_row returned unknown query id {source_id}")
    if target_matches.size == 0:
        raise RuntimeError(f"nearest_max_distance_row returned unknown neighbor id {target_id}")
    source_index = int(source_matches[0])
    target_index = int(target_matches[0])
    distance = math.hypot(
        float(source_columns["x"][source_index]) - float(target_columns["x"][target_index]),
        float(source_columns["y"][source_index]) - float(target_columns["y"][target_index]),
    )
    return {
        "distance": distance,
        "source_index": source_index,
        "target_index": target_index,
        "row_count": 1,
    }


def _threshold_search_prepared(
    source_points: tuple[Point, ...],
    prepared,
    *,
    tolerance: float,
    max_iterations: int,
    upper_bound: float,
) -> dict[str, object]:
    low = 0.0
    high = float(upper_bound)
    if high <= 0.0:
        return {"lower_bound": 0.0, "upper_bound": 0.0, "iterations": 0, "elapsed_sec": 0.0}
    start = time.perf_counter()
    source_count = int(source_points.count) if hasattr(source_points, "count") else len(source_points)
    for iteration in range(1, max_iterations + 1):
        mid = (low + high) * 0.5
        result = prepared.count_threshold_reached(source_points, radius=mid, threshold=1)
        threshold_reached_count = result["threshold_reached_count"] if isinstance(result, dict) else result
        if int(threshold_reached_count) == source_count:
            high = mid
        else:
            low = mid
        if high - low <= tolerance:
            break
    else:
        iteration = max_iterations
    return {
        "lower_bound": low,
        "upper_bound": high,
        "iterations": iteration,
        "elapsed_sec": time.perf_counter() - start,
    }


def _directed_rt_threshold_seeded_nearest_witness(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    backend: str,
    upper_bound: float,
    radius: float | None,
    seed_with_threshold: bool,
    threshold_tolerance: float,
    threshold_max_iterations: int,
) -> dict[str, object]:
    source_points = _columns_to_points(source_columns)
    target_points = _columns_to_points(target_columns)
    witness_radius = float(upper_bound) if radius is None else float(radius)
    threshold_iterations = 0
    threshold_elapsed_sec = 0.0
    radius_strategy = "bbox_upper_bound" if radius is None else "explicit_radius"
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=target_points,
        backend=backend,
        max_radius=upper_bound if backend == "optix" else None,
    ) as prepared:
        if radius is None and seed_with_threshold:
            threshold = _threshold_search_prepared(
                source_points,
                prepared,
                tolerance=threshold_tolerance,
                max_iterations=threshold_max_iterations,
                upper_bound=upper_bound,
            )
            witness_radius = float(threshold["upper_bound"])
            threshold_iterations = int(threshold["iterations"])
            threshold_elapsed_sec = float(threshold["elapsed_sec"])
            radius_strategy = "rt_threshold_upper_bound"
        if not hasattr(prepared._prepared_scene, "nearest_witness_rows"):
            raise RuntimeError(f"{backend} prepared fixed-radius scene does not expose nearest_witness_rows")
        rows = prepared._prepared_scene.nearest_witness_rows(source_points, radius=witness_radius)
    reduced = _reduce_nearest_witness_rows(source_points, target_points, target_columns, rows)
    reduced["witness_radius"] = witness_radius
    reduced["radius_strategy"] = radius_strategy
    reduced["threshold_iterations"] = threshold_iterations
    reduced["threshold_elapsed_sec"] = threshold_elapsed_sec
    return reduced


def _directed_rt_grouped_threshold_seeded_nearest_witness(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    upper_bound: float,
    radius: float | None,
    seed_with_threshold: bool,
    threshold_tolerance: float,
    threshold_max_iterations: int,
    target_points_per_group: int,
) -> dict[str, object]:
    from rtdsl.optix_runtime import prepare_optix_point_group_nearest_witness_2d

    source_points = _columns_to_points(source_columns)
    sorted_target_points, target_groups = _build_uniform_point_groups(
        target_columns,
        target_points_per_group=target_points_per_group,
    )
    witness_radius = float(upper_bound) if radius is None else float(radius)
    threshold_iterations = 0
    threshold_elapsed_sec = 0.0
    radius_strategy = "bbox_upper_bound" if radius is None else "explicit_radius"
    with prepare_optix_point_group_nearest_witness_2d(
        sorted_target_points,
        target_groups,
        max_radius=_prepared_radius_guard(upper_bound),
    ) as prepared:
        if radius is None and seed_with_threshold:
            threshold = _threshold_search_prepared(
                source_points,
                prepared,
                tolerance=threshold_tolerance,
                max_iterations=threshold_max_iterations,
                upper_bound=upper_bound,
            )
            witness_radius = float(threshold["upper_bound"])
            threshold_iterations = int(threshold["iterations"])
            threshold_elapsed_sec = float(threshold["elapsed_sec"])
            radius_strategy = "rt_grouped_threshold_upper_bound"
        rows = prepared.nearest_witness_rows(source_points, radius=witness_radius)
    reduced = _reduce_nearest_witness_rows(source_points, sorted_target_points, target_columns, rows)
    reduced["witness_radius"] = witness_radius
    reduced["radius_strategy"] = radius_strategy
    reduced["threshold_iterations"] = threshold_iterations
    reduced["threshold_elapsed_sec"] = threshold_elapsed_sec
    reduced["target_group_count"] = len(target_groups)
    reduced["target_points_per_group"] = target_points_per_group
    return reduced


def _directed_rt_grouped_reduced_nearest_witness(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    upper_bound: float,
    radius: float | None,
    seed_with_threshold: bool,
    threshold_tolerance: float,
    threshold_max_iterations: int,
    target_points_per_group: int,
) -> dict[str, object]:
    from rtdsl.optix_runtime import prepare_optix_point_group_nearest_witness_2d

    source_points = _pack_point_columns_for_optix(source_columns)
    sorted_target_columns, target_groups = _build_uniform_point_group_columns(
        target_columns,
        target_points_per_group=target_points_per_group,
    )
    sorted_target_points = _pack_point_columns_for_optix(sorted_target_columns)
    witness_radius = float(upper_bound) if radius is None else float(radius)
    threshold_iterations = 0
    threshold_elapsed_sec = 0.0
    radius_strategy = "bbox_upper_bound" if radius is None else "explicit_radius"
    with prepare_optix_point_group_nearest_witness_2d(
        sorted_target_points,
        target_groups,
        max_radius=_prepared_radius_guard(upper_bound),
    ) as prepared:
        if radius is None and seed_with_threshold:
            threshold = _threshold_search_prepared(
                source_points,
                prepared,
                tolerance=threshold_tolerance,
                max_iterations=threshold_max_iterations,
                upper_bound=upper_bound,
            )
            witness_radius = float(threshold["upper_bound"])
            threshold_iterations = int(threshold["iterations"])
            threshold_elapsed_sec = float(threshold["elapsed_sec"])
            radius_strategy = "rt_grouped_threshold_upper_bound"
        row = prepared.nearest_max_distance_row(source_points, radius=witness_radius)
    reduced = _reduce_nearest_max_distance_row(source_columns, sorted_target_columns, row)
    reduced["witness_radius"] = witness_radius
    reduced["radius_strategy"] = radius_strategy
    reduced["threshold_iterations"] = threshold_iterations
    reduced["threshold_elapsed_sec"] = threshold_elapsed_sec
    reduced["target_group_count"] = len(target_groups)
    reduced["target_points_per_group"] = target_points_per_group
    reduced["native_reduction"] = "point_group_nearest_max_distance"
    return reduced


def _directed_rt_grouped_seeded_pruned_nearest_witness(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    upper_bound: float,
    radius: float | None,
    seed_with_threshold: bool,
    seed_sample_count: int,
    target_points_per_group: int,
) -> dict[str, object]:
    from rtdsl.optix_runtime import prepare_optix_point_group_nearest_witness_2d

    source_points = _pack_point_columns_for_optix(source_columns)
    sorted_target_columns, target_groups = _build_uniform_point_group_columns(
        target_columns,
        target_points_per_group=target_points_per_group,
    )
    sorted_target_points = _pack_point_columns_for_optix(sorted_target_columns)
    witness_radius = float(upper_bound) if radius is None else float(radius)
    radius_strategy = "xhd_sample_seed_threshold_prune" if seed_with_threshold else "bbox_upper_bound"
    threshold_iterations = 0
    threshold_elapsed_sec = 0.0
    seed_distance = -1.0
    unsafe_count = int(source_columns["ids"].size)
    selected: dict[str, object] | None = None
    search_start = time.perf_counter()
    with prepare_optix_point_group_nearest_witness_2d(
        sorted_target_points,
        target_groups,
        max_radius=_prepared_radius_guard(witness_radius),
    ) as prepared:
        if seed_with_threshold and int(source_columns["ids"].size) > int(seed_sample_count) > 0:
            seed_columns, _seed_indices = _seed_sample_point_columns(
                source_columns,
                sample_count=seed_sample_count,
                seed=2131 + int(source_columns["ids"].size),
            )
            seed_points = _pack_point_columns_for_optix(seed_columns)
            seed_row = prepared.nearest_max_distance_row(seed_points, radius=witness_radius)
            seed_reduced = _reduce_nearest_max_distance_row(source_columns, target_columns, seed_row)
            seed_distance = float(seed_reduced["distance"])
            safety_margin = max(1.0e-7, abs(seed_distance) * 1.0e-6)
            threshold_radius = max(0.0, seed_distance - safety_margin)
            flags = np.asarray(
                prepared.threshold_flags(source_points, radius=threshold_radius, threshold=1),
                dtype=np.uint32,
            )
            unsafe_indices = np.nonzero(flags == 0)[0].astype(np.int64)
            unsafe_count = int(unsafe_indices.size)
            threshold_iterations = 1
            if unsafe_count == 0:
                selected = seed_reduced
            else:
                unsafe_columns = _subset_point_columns(source_columns, unsafe_indices)
                unsafe_points = _pack_point_columns_for_optix(unsafe_columns)
                unsafe_row = prepared.nearest_max_distance_row(unsafe_points, radius=witness_radius)
                unsafe_reduced = _reduce_nearest_max_distance_row(source_columns, target_columns, unsafe_row)
                if (
                    float(unsafe_reduced["distance"]) > seed_distance
                    or (
                        math.isclose(float(unsafe_reduced["distance"]), seed_distance)
                        and int(unsafe_reduced["source_index"]) < int(seed_reduced["source_index"])
                    )
                ):
                    selected = unsafe_reduced
                else:
                    selected = seed_reduced
        if selected is None:
            row = prepared.nearest_max_distance_row(source_points, radius=witness_radius)
            selected = _reduce_nearest_max_distance_row(source_columns, target_columns, row)
            seed_distance = float(selected["distance"])
            unsafe_count = int(source_columns["ids"].size)
    selected["witness_radius"] = witness_radius
    selected["radius_strategy"] = radius_strategy
    selected["threshold_iterations"] = threshold_iterations
    selected["threshold_elapsed_sec"] = time.perf_counter() - search_start
    selected["target_group_count"] = len(target_groups)
    selected["target_points_per_group"] = target_points_per_group
    selected["native_reduction"] = "point_group_nearest_max_distance_with_threshold_flags"
    selected["seed_sample_count"] = min(int(seed_sample_count), int(source_columns["ids"].size))
    selected["seed_distance"] = seed_distance
    selected["unsafe_count"] = unsafe_count
    return selected


def _directed_rt_grouped_adaptive_nearest_witness(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    upper_bound: float,
    initial_radius: float | None,
    growth_factor: float,
    max_iterations: int,
    target_points_per_group: int,
) -> dict[str, object]:
    from rtdsl.optix_runtime import prepare_optix_point_group_nearest_witness_2d

    if growth_factor <= 1.0:
        raise ValueError("growth_factor must be greater than 1.0")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    source_points = _columns_to_points(source_columns)
    sorted_target_points, target_groups = _build_uniform_point_groups(
        target_columns,
        target_points_per_group=target_points_per_group,
    )
    if upper_bound <= 0.0:
        return {
            "distance": 0.0,
            "source_index": 0,
            "target_index": 0,
            "witness_radius": 0.0,
            "radius_strategy": "rt_grouped_adaptive_radius",
            "threshold_iterations": 0,
            "threshold_elapsed_sec": 0.0,
        }
    radius = float(initial_radius) if initial_radius is not None else upper_bound / max(16.0, math.sqrt(len(sorted_target_points)))
    radius = min(max(radius, 1.0e-12), upper_bound)
    target_by_id = {int(point.id): point for point in sorted_target_points}
    target_id_to_index = {int(target_columns["ids"][i]): i for i in range(int(target_columns["ids"].size))}
    active_indices = list(range(len(source_points)))
    best_distance = -1.0
    best_source_index = -1
    best_target_index = -1
    iterations = 0
    search_start = time.perf_counter()
    with prepare_optix_point_group_nearest_witness_2d(
        sorted_target_points,
        target_groups,
        max_radius=_prepared_radius_guard(upper_bound),
    ) as prepared:
        while active_indices:
            iterations += 1
            active_points = tuple(source_points[index] for index in active_indices)
            rows = prepared.nearest_witness_rows(active_points, radius=radius)
            if len(rows) != len(active_points):
                raise RuntimeError("adaptive nearest_witness_rows must return one row per active source point")
            next_active: list[int] = []
            for local_index, row in enumerate(rows):
                source_index = active_indices[local_index]
                neighbor_id = int(row["neighbor_id"])
                if neighbor_id == 0xFFFFFFFF:
                    next_active.append(source_index)
                    continue
                target_point = target_by_id[neighbor_id]
                source_point = source_points[source_index]
                distance = math.hypot(source_point.x - target_point.x, source_point.y - target_point.y)
                if distance > best_distance or (
                    math.isclose(distance, best_distance) and source_index < best_source_index
                ):
                    best_distance = distance
                    best_source_index = source_index
                    best_target_index = target_id_to_index[neighbor_id]
            active_indices = next_active
            if not active_indices:
                break
            if radius >= upper_bound:
                raise RuntimeError("adaptive point-group nearest witness exhausted the upper bound without witnesses")
            if iterations >= max_iterations:
                radius = upper_bound
            else:
                radius = min(upper_bound, radius * growth_factor)
    if best_distance < 0.0:
        raise RuntimeError("adaptive point-group nearest witness did not produce any witness rows")
    return {
        "distance": best_distance,
        "source_index": best_source_index,
        "target_index": best_target_index,
        "witness_radius": radius,
        "radius_strategy": "rt_grouped_adaptive_radius",
        "threshold_iterations": iterations,
        "threshold_elapsed_sec": time.perf_counter() - search_start,
        "target_group_count": len(target_groups),
        "target_points_per_group": target_points_per_group,
    }


def hausdorff_distance_2d_rt_nearest_witness(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    backend: str = "optix",
    radius: float | None = None,
    seed_with_threshold: bool = True,
    threshold_tolerance: float = 1e-4,
    threshold_max_iterations: int = 32,
) -> HausdorffRtNearestResult:
    """Return exact HD using RTDL fixed-radius nearest-witness traversal.

    The primitive is generic: a prepared fixed-radius point scene emits one
    nearest in-radius witness row per query. This function uses a conservative
    radius upper bound so every query has a witness, then reduces the returned
    nearest witnesses into directed and undirected Hausdorff distances.
    """

    if backend != "optix":
        raise ValueError("rt nearest-witness HD currently requires backend='optix'")
    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    upper_bound = _point_set_upper_bound(columns_a, columns_b)
    start = time.perf_counter()
    ab = _directed_rt_threshold_seeded_nearest_witness(
        columns_a,
        columns_b,
        backend=backend,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        threshold_tolerance=threshold_tolerance,
        threshold_max_iterations=threshold_max_iterations,
    )
    ba = _directed_rt_threshold_seeded_nearest_witness(
        columns_b,
        columns_a,
        backend=backend,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        threshold_tolerance=threshold_tolerance,
        threshold_max_iterations=threshold_max_iterations,
    )
    if (float(ab["distance"]), "a_to_b") >= (float(ba["distance"]), "b_to_a"):
        selected = ab
        direction = "a_to_b"
    else:
        selected = ba
        direction = "b_to_a"
    return HausdorffRtNearestResult(
        distance=float(selected["distance"]),
        direction=direction,
        source_index=int(selected["source_index"]),
        target_index=int(selected["target_index"]),
        elapsed_sec=time.perf_counter() - start,
        method="rtdl_rt_nearest_witness",
        backend=backend,
        rt_core_accelerated=True,
        exact_value=True,
        witness_radius=max(float(ab["witness_radius"]), float(ba["witness_radius"])),
        radius_strategy=str(selected["radius_strategy"]),
        threshold_iterations=int(ab["threshold_iterations"]) + int(ba["threshold_iterations"]),
    )


def hausdorff_distance_2d_rt_grouped_nearest_witness(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    radius: float | None = None,
    seed_with_threshold: bool = True,
    threshold_tolerance: float = 1e-4,
    threshold_max_iterations: int = 32,
    target_points_per_group: int | None = None,
) -> HausdorffRtNearestResult:
    """Return exact HD using X-HD-style grouped point-bound traversal.

    The RTDL engine still sees only a generic point-group nearest-witness
    primitive. The app-level Python code builds uniform groups over target
    points, mirroring X-HD's first-stage cell MBR idea without adding
    Hausdorff-specific ABI names or reducers to the native engine.
    """

    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    group_size_ab = _resolve_target_points_per_group(columns_b, target_points_per_group)
    group_size_ba = _resolve_target_points_per_group(columns_a, target_points_per_group)
    upper_bound = _point_set_upper_bound(columns_a, columns_b)
    start = time.perf_counter()
    ab = _directed_rt_grouped_threshold_seeded_nearest_witness(
        columns_a,
        columns_b,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        threshold_tolerance=threshold_tolerance,
        threshold_max_iterations=threshold_max_iterations,
        target_points_per_group=group_size_ab,
    )
    ba = _directed_rt_grouped_threshold_seeded_nearest_witness(
        columns_b,
        columns_a,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        threshold_tolerance=threshold_tolerance,
        threshold_max_iterations=threshold_max_iterations,
        target_points_per_group=group_size_ba,
    )
    if (float(ab["distance"]), "a_to_b") >= (float(ba["distance"]), "b_to_a"):
        selected = ab
        direction = "a_to_b"
    else:
        selected = ba
        direction = "b_to_a"
    return HausdorffRtNearestResult(
        distance=float(selected["distance"]),
        direction=direction,
        source_index=int(selected["source_index"]),
        target_index=int(selected["target_index"]),
        elapsed_sec=time.perf_counter() - start,
        method="rtdl_rt_grouped_nearest_witness",
        backend="optix",
        rt_core_accelerated=True,
        exact_value=True,
        witness_radius=max(float(ab["witness_radius"]), float(ba["witness_radius"])),
        radius_strategy=str(selected["radius_strategy"]),
        threshold_iterations=int(ab["threshold_iterations"]) + int(ba["threshold_iterations"]),
    )


def hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    radius: float | None = None,
    seed_with_threshold: bool = True,
    threshold_tolerance: float = 1e-4,
    threshold_max_iterations: int = 32,
    target_points_per_group: int | None = None,
) -> HausdorffRtNearestResult:
    """Return exact HD using grouped RT traversal plus device-side max reduction."""

    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    group_size_ab = _resolve_target_points_per_group(columns_b, target_points_per_group)
    group_size_ba = _resolve_target_points_per_group(columns_a, target_points_per_group)
    upper_bound = _point_set_upper_bound(columns_a, columns_b)
    start = time.perf_counter()
    ab = _directed_rt_grouped_reduced_nearest_witness(
        columns_a,
        columns_b,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        threshold_tolerance=threshold_tolerance,
        threshold_max_iterations=threshold_max_iterations,
        target_points_per_group=group_size_ab,
    )
    ba = _directed_rt_grouped_reduced_nearest_witness(
        columns_b,
        columns_a,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        threshold_tolerance=threshold_tolerance,
        threshold_max_iterations=threshold_max_iterations,
        target_points_per_group=group_size_ba,
    )
    if (float(ab["distance"]), "a_to_b") >= (float(ba["distance"]), "b_to_a"):
        selected = ab
        direction = "a_to_b"
    else:
        selected = ba
        direction = "b_to_a"
    return HausdorffRtNearestResult(
        distance=float(selected["distance"]),
        direction=direction,
        source_index=int(selected["source_index"]),
        target_index=int(selected["target_index"]),
        elapsed_sec=time.perf_counter() - start,
        method="rtdl_rt_grouped_reduced_nearest_witness",
        backend="optix",
        rt_core_accelerated=True,
        exact_value=True,
        witness_radius=max(float(ab["witness_radius"]), float(ba["witness_radius"])),
        radius_strategy=str(selected["radius_strategy"]),
        threshold_iterations=int(ab["threshold_iterations"]) + int(ba["threshold_iterations"]),
    )


def hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    radius: float | None = None,
    seed_with_threshold: bool = True,
    seed_sample_count: int = 8192,
    target_points_per_group: int | None = None,
) -> HausdorffRtNearestResult:
    """Return exact HD using X-HD-style sample seeding and safe-point pruning.

    A sample exact pass produces a real lower-bound witness. A generic
    point-group threshold-flags pass then marks source points that already have
    a target within that distance; those points cannot improve the directed HD,
    so only the remaining unsafe subset needs the exact nearest-witness
    reduction. The native engine still only sees generic point/group/radius
    operations.
    """

    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    group_size_ab = _resolve_target_points_per_group(columns_b, target_points_per_group)
    group_size_ba = _resolve_target_points_per_group(columns_a, target_points_per_group)
    upper_bound = _point_set_upper_bound(columns_a, columns_b)
    start = time.perf_counter()
    ab = _directed_rt_grouped_seeded_pruned_nearest_witness(
        columns_a,
        columns_b,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        seed_sample_count=seed_sample_count,
        target_points_per_group=group_size_ab,
    )
    ba = _directed_rt_grouped_seeded_pruned_nearest_witness(
        columns_b,
        columns_a,
        upper_bound=upper_bound,
        radius=radius,
        seed_with_threshold=seed_with_threshold,
        seed_sample_count=seed_sample_count,
        target_points_per_group=group_size_ba,
    )
    if (float(ab["distance"]), "a_to_b") >= (float(ba["distance"]), "b_to_a"):
        selected = ab
        direction = "a_to_b"
    else:
        selected = ba
        direction = "b_to_a"
    return HausdorffRtNearestResult(
        distance=float(selected["distance"]),
        direction=direction,
        source_index=int(selected["source_index"]),
        target_index=int(selected["target_index"]),
        elapsed_sec=time.perf_counter() - start,
        method="rtdl_rt_grouped_seeded_pruned_nearest_witness",
        backend="optix",
        rt_core_accelerated=True,
        exact_value=True,
        witness_radius=max(float(ab["witness_radius"]), float(ba["witness_radius"])),
        radius_strategy=str(selected["radius_strategy"]),
        threshold_iterations=int(ab["threshold_iterations"]) + int(ba["threshold_iterations"]),
    )


def hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    initial_radius: float | None = None,
    growth_factor: float = 8.0,
    max_iterations: int = 12,
    target_points_per_group: int | None = None,
) -> HausdorffRtNearestResult:
    """Return exact HD using grouped RT traversal with X-HD-style worklist shrink."""

    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    group_size_ab = _resolve_adaptive_target_points_per_group(columns_b, target_points_per_group)
    group_size_ba = _resolve_adaptive_target_points_per_group(columns_a, target_points_per_group)
    upper_bound = _point_set_upper_bound(columns_a, columns_b)
    start = time.perf_counter()
    ab = _directed_rt_grouped_adaptive_nearest_witness(
        columns_a,
        columns_b,
        upper_bound=upper_bound,
        initial_radius=initial_radius,
        growth_factor=growth_factor,
        max_iterations=max_iterations,
        target_points_per_group=group_size_ab,
    )
    ba = _directed_rt_grouped_adaptive_nearest_witness(
        columns_b,
        columns_a,
        upper_bound=upper_bound,
        initial_radius=initial_radius,
        growth_factor=growth_factor,
        max_iterations=max_iterations,
        target_points_per_group=group_size_ba,
    )
    if (float(ab["distance"]), "a_to_b") >= (float(ba["distance"]), "b_to_a"):
        selected = ab
        direction = "a_to_b"
    else:
        selected = ba
        direction = "b_to_a"
    return HausdorffRtNearestResult(
        distance=float(selected["distance"]),
        direction=direction,
        source_index=int(selected["source_index"]),
        target_index=int(selected["target_index"]),
        elapsed_sec=time.perf_counter() - start,
        method="rtdl_rt_grouped_adaptive_nearest_witness",
        backend="optix",
        rt_core_accelerated=True,
        exact_value=True,
        witness_radius=max(float(ab["witness_radius"]), float(ba["witness_radius"])),
        radius_strategy=str(selected["radius_strategy"]),
        threshold_iterations=int(ab["threshold_iterations"]) + int(ba["threshold_iterations"]),
    )


def _directed_hd_threshold_search(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    backend: str,
    tolerance: float,
    max_iterations: int,
    upper_bound: float,
) -> dict[str, object]:
    source_points = _columns_to_points(source_columns)
    target_points = _columns_to_points(target_columns)
    low = 0.0
    high = float(upper_bound)
    if high <= 0.0:
        return {"lower_bound": 0.0, "upper_bound": 0.0, "iterations": 0, "elapsed_sec": 0.0}

    start = time.perf_counter()
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=target_points,
        backend=backend,
        max_radius=high if backend == "optix" else None,
    ) as prepared:
        result = _threshold_search_prepared(
            source_points,
            prepared,
            tolerance=tolerance,
            max_iterations=max_iterations,
            upper_bound=high,
        )
    result["elapsed_sec"] = time.perf_counter() - start
    return result


def hausdorff_distance_2d_rt_threshold_search(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    backend: str = "optix",
    tolerance: float = 1e-5,
    max_iterations: int = 32,
) -> HausdorffThresholdResult:
    """Compute a tolerance-bounded HD interval using RTDL fixed-radius decisions.

    This is the v2.x RT-core-facing HD path. It reduces directed HD to the
    monotone question: "is every source point within radius r of some target?"
    With `backend="optix"`, RTDL/OptiX handles the fixed-radius BVH traversal.
    The current v2 primitive returns aggregate coverage counts, so this returns
    a tight interval rather than an exact witness pair.
    """

    if backend not in {"embree", "optix"}:
        raise ValueError("backend must be 'embree' or 'optix'")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    upper_bound = _point_set_upper_bound(columns_a, columns_b)
    start = time.perf_counter()
    ab = _directed_hd_threshold_search(
        columns_a,
        columns_b,
        backend=backend,
        tolerance=tolerance,
        max_iterations=max_iterations,
        upper_bound=upper_bound,
    )
    ba = _directed_hd_threshold_search(
        columns_b,
        columns_a,
        backend=backend,
        tolerance=tolerance,
        max_iterations=max_iterations,
        upper_bound=upper_bound,
    )
    if (float(ab["upper_bound"]), "a_to_b") >= (float(ba["upper_bound"]), "b_to_a"):
        direction = "a_to_b"
        low = float(ab["lower_bound"])
        high = float(ab["upper_bound"])
    else:
        direction = "b_to_a"
        low = float(ba["lower_bound"])
        high = float(ba["upper_bound"])
    return HausdorffThresholdResult(
        distance_upper_bound=high,
        distance_lower_bound=low,
        tolerance=tolerance,
        direction=direction,
        elapsed_sec=time.perf_counter() - start,
        method="rtdl_rt_threshold_search",
        backend=backend,
        iterations=int(ab["iterations"]) + int(ba["iterations"]),
        rt_core_accelerated=backend == "optix",
        exact_value=False,
    )


def hausdorff_distance_2d(
    points_a: Sequence[Sequence[float]] | np.ndarray,
    points_b: Sequence[Sequence[float]] | np.ndarray,
    *,
    method: str = "rtdl_v2_user_cuda",
    warmup: int = 1,
    cache_dir: Path | None = None,
) -> HausdorffResult:
    """Return the exact undirected 2D Hausdorff distance between two point sets.

    This is the user-facing v2.x shape:

    - RTDL converts Python point rows to partner-owned columns;
    - user-owned CUDA/CuPy continuation computes exact directed HD;
    - Python combines A->B and B->A into the final undirected HD.

    The `openmp_cpu`, `cuda_cpp`, `cupy_rawkernel`, and
    `cupy_grouped_grid_rawkernel` methods are independent validation/performance
    baselines for the same exact function.
    """

    if method == "rtdl_rt_nearest_witness":
        rt_result = hausdorff_distance_2d_rt_nearest_witness(points_a, points_b, backend="optix")
        return HausdorffResult(
            distance=rt_result.distance,
            direction=rt_result.direction,
            source_index=rt_result.source_index,
            target_index=rt_result.target_index,
            elapsed_sec=rt_result.elapsed_sec,
            method=method,
        )
    if method == "rtdl_rt_grouped_nearest_witness":
        rt_result = hausdorff_distance_2d_rt_grouped_nearest_witness(points_a, points_b)
        return HausdorffResult(
            distance=rt_result.distance,
            direction=rt_result.direction,
            source_index=rt_result.source_index,
            target_index=rt_result.target_index,
            elapsed_sec=rt_result.elapsed_sec,
            method=method,
        )
    if method == "rtdl_rt_grouped_reduced_nearest_witness":
        rt_result = hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(points_a, points_b)
        return HausdorffResult(
            distance=rt_result.distance,
            direction=rt_result.direction,
            source_index=rt_result.source_index,
            target_index=rt_result.target_index,
            elapsed_sec=rt_result.elapsed_sec,
            method=method,
        )
    if method == "rtdl_rt_grouped_seeded_pruned_nearest_witness":
        rt_result = hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness(points_a, points_b)
        return HausdorffResult(
            distance=rt_result.distance,
            direction=rt_result.direction,
            source_index=rt_result.source_index,
            target_index=rt_result.target_index,
            elapsed_sec=rt_result.elapsed_sec,
            method=method,
        )
    if method == "rtdl_rt_grouped_adaptive_nearest_witness":
        rt_result = hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness(points_a, points_b)
        return HausdorffResult(
            distance=rt_result.distance,
            direction=rt_result.direction,
            source_index=rt_result.source_index,
            target_index=rt_result.target_index,
            elapsed_sec=rt_result.elapsed_sec,
            method=method,
        )

    cache = cache_dir or (ROOT / "build" / "hausdorff_v2_user_benchmark")
    columns_a = _as_point_columns(points_a, name="points_a")
    columns_b = _as_point_columns(points_b, name="points_b")
    runner = _select_directed_runner(method, cache_dir=cache)
    result = lab.undirected(runner, columns_a, columns_b, warmup=warmup if method != "openmp_cpu" else 0)
    if result["direction"] == "a_to_b":
        directed = result["directed_a_to_b"]
    else:
        directed = result["directed_b_to_a"]
    return HausdorffResult(
        distance=float(result["distance"]),
        direction=str(result["direction"]),
        source_index=int(directed["source_index"]),
        target_index=int(directed["target_index"]),
        elapsed_sec=float(result["elapsed_sec"]),
        method=method,
    )


def make_demo_points(n: int, *, seed: int, offset: tuple[float, float] = (0.0, 0.0)) -> np.ndarray:
    columns = lab.make_point_columns(n, seed=seed, offset_x=offset[0], offset_y=offset[1])
    return np.column_stack([columns["x"], columns["y"]])


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute exact 2D Hausdorff distance using the v2.x user API.")
    parser.add_argument("--points-a", type=int, default=8192)
    parser.add_argument("--points-b", type=int, default=8192)
    parser.add_argument(
        "--method",
        choices=(
            "rtdl_v2_user_cuda",
            "rtdl_rt_nearest_witness",
            "rtdl_rt_grouped_nearest_witness",
            "rtdl_rt_grouped_reduced_nearest_witness",
            "rtdl_rt_grouped_seeded_pruned_nearest_witness",
            "rtdl_rt_grouped_adaptive_nearest_witness",
            "rtdl_rt_threshold_search",
            "openmp_cpu",
            "cuda_cpp",
            "cupy_rawkernel",
            "cupy_grouped_grid_rawkernel",
        ),
        default="rtdl_v2_user_cuda",
    )
    parser.add_argument("--rt-backend", choices=("optix", "embree"), default="optix")
    parser.add_argument("--rt-tolerance", type=float, default=1e-5)
    parser.add_argument("--rt-max-iterations", type=int, default=32)
    parser.add_argument(
        "--rt-nearest-radius",
        type=float,
        default=None,
        help="explicit radius for rtdl_rt_nearest_witness; defaults to an RT threshold-search upper bound",
    )
    parser.add_argument(
        "--rt-nearest-no-threshold-seed",
        action="store_true",
        help="use the dataset bounding-box diagonal for rtdl_rt_nearest_witness instead of threshold seeding",
    )
    parser.add_argument(
        "--target-points-per-group",
        type=int,
        default=None,
        help="override the scale-aware grouped RT target group size",
    )
    parser.add_argument(
        "--seed-sample-count",
        type=int,
        default=8192,
        help="sample count for X-HD-style seeded-pruned RT witness methods",
    )
    parser.add_argument("--compare", action="store_true", help="also run all available baselines and compare")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    points_a = make_demo_points(args.points_a, seed=11)
    points_b = make_demo_points(args.points_b, seed=29, offset=(0.08, -0.06))
    if args.method == "rtdl_rt_nearest_witness":
        rt_exact = hausdorff_distance_2d_rt_nearest_witness(
            points_a,
            points_b,
            backend=args.rt_backend,
            radius=args.rt_nearest_radius,
            seed_with_threshold=not args.rt_nearest_no_threshold_seed,
            threshold_tolerance=args.rt_tolerance,
            threshold_max_iterations=args.rt_max_iterations,
        )
        primary_distance = rt_exact.distance
        payload: dict[str, object] = {"primary": asdict(rt_exact)}
    elif args.method == "rtdl_rt_grouped_nearest_witness":
        rt_exact = hausdorff_distance_2d_rt_grouped_nearest_witness(
            points_a,
            points_b,
            radius=args.rt_nearest_radius,
            seed_with_threshold=not args.rt_nearest_no_threshold_seed,
            threshold_tolerance=args.rt_tolerance,
            threshold_max_iterations=args.rt_max_iterations,
            target_points_per_group=args.target_points_per_group,
        )
        primary_distance = rt_exact.distance
        payload = {"primary": asdict(rt_exact)}
    elif args.method == "rtdl_rt_grouped_reduced_nearest_witness":
        rt_exact = hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(
            points_a,
            points_b,
            radius=args.rt_nearest_radius,
            seed_with_threshold=not args.rt_nearest_no_threshold_seed,
            threshold_tolerance=args.rt_tolerance,
            threshold_max_iterations=args.rt_max_iterations,
            target_points_per_group=args.target_points_per_group,
        )
        primary_distance = rt_exact.distance
        payload = {"primary": asdict(rt_exact)}
    elif args.method == "rtdl_rt_grouped_seeded_pruned_nearest_witness":
        rt_exact = hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness(
            points_a,
            points_b,
            radius=args.rt_nearest_radius,
            seed_with_threshold=not args.rt_nearest_no_threshold_seed,
            seed_sample_count=args.seed_sample_count,
            target_points_per_group=args.target_points_per_group,
        )
        primary_distance = rt_exact.distance
        payload = {"primary": asdict(rt_exact)}
    elif args.method == "rtdl_rt_grouped_adaptive_nearest_witness":
        rt_exact = hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness(
            points_a,
            points_b,
            max_iterations=args.rt_max_iterations,
            target_points_per_group=args.target_points_per_group,
        )
        primary_distance = rt_exact.distance
        payload = {"primary": asdict(rt_exact)}
    elif args.method == "rtdl_rt_threshold_search":
        rt_primary = hausdorff_distance_2d_rt_threshold_search(
            points_a,
            points_b,
            backend=args.rt_backend,
            tolerance=args.rt_tolerance,
            max_iterations=args.rt_max_iterations,
        )
        primary_distance = rt_primary.distance_upper_bound
        payload = {"primary": asdict(rt_primary)}
    else:
        primary = hausdorff_distance_2d(points_a, points_b, method=args.method, warmup=args.warmup)
        primary_distance = primary.distance
        payload = {"primary": asdict(primary)}
    if args.compare:
        comparisons = {}
        for method in (
            "openmp_cpu",
            "cuda_cpp",
            "cupy_rawkernel",
            "cupy_grouped_grid_rawkernel",
            "rtdl_v2_user_cuda",
        ):
            start = time.perf_counter()
            try:
                result = hausdorff_distance_2d(points_a, points_b, method=method, warmup=args.warmup)
                comparisons[method] = asdict(result)
                comparisons[method]["matches_primary"] = math.isclose(
                    result.distance,
                    primary_distance,
                    rel_tol=max(1e-9, args.rt_tolerance if args.method == "rtdl_rt_threshold_search" else 1e-9),
                    abs_tol=max(1e-9, args.rt_tolerance if args.method == "rtdl_rt_threshold_search" else 1e-9),
                )
            except Exception as exc:
                comparisons[method] = {"error": repr(exc), "elapsed_sec": time.perf_counter() - start}
        payload["comparisons"] = comparisons
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
