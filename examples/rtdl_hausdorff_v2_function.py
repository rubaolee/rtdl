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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_hausdorff_v2_user_benchmark as lab
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
    raise ValueError("method must be one of: rtdl_v2_user_cuda, openmp_cpu, cuda_cpp, cupy_rawkernel")


def _columns_to_points(columns: dict[str, np.ndarray]) -> tuple[Point, ...]:
    return tuple(
        Point(id=int(columns["ids"][i]), x=float(columns["x"][i]), y=float(columns["y"][i]))
        for i in range(int(columns["ids"].size))
    )


def _point_set_upper_bound(points_a: dict[str, np.ndarray], points_b: dict[str, np.ndarray]) -> float:
    min_x = min(float(points_a["x"].min()), float(points_b["x"].min()))
    max_x = max(float(points_a["x"].max()), float(points_b["x"].max()))
    min_y = min(float(points_a["y"].min()), float(points_b["y"].min()))
    max_y = max(float(points_a["y"].max()), float(points_b["y"].max()))
    return math.hypot(max_x - min_x, max_y - min_y)


def _directed_rt_nearest_witness(
    source_columns: dict[str, np.ndarray],
    target_columns: dict[str, np.ndarray],
    *,
    backend: str,
    radius: float,
) -> dict[str, object]:
    source_points = _columns_to_points(source_columns)
    target_points = _columns_to_points(target_columns)
    target_by_id = {int(point.id): point for point in target_points}
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=target_points,
        backend=backend,
        max_radius=radius if backend == "optix" else None,
    ) as prepared:
        if not hasattr(prepared._prepared_scene, "nearest_witness_rows"):
            raise RuntimeError(f"{backend} prepared fixed-radius scene does not expose nearest_witness_rows")
        rows = prepared._prepared_scene.nearest_witness_rows(source_points, radius=radius)
    if len(rows) != len(source_points):
        raise RuntimeError("nearest_witness_rows must return one row per source point")
    best_distance = -1.0
    best_source_index = -1
    best_target_index = -1
    target_id_to_index = {int(target_columns["ids"][i]): i for i in range(int(target_columns["ids"].size))}
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
    for iteration in range(1, max_iterations + 1):
        mid = (low + high) * 0.5
        result = prepared.count_threshold_reached(source_points, radius=mid, threshold=1)
        if int(result["threshold_reached_count"]) == len(source_points):
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

    This is the v2.0 RT-core-facing HD path. It reduces directed HD to the
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

    This is the user-facing v2.0 shape:

    - RTDL converts Python point rows to partner-owned columns;
    - user-owned CUDA/CuPy continuation computes exact directed HD;
    - Python combines A->B and B->A into the final undirected HD.

    The `openmp_cpu`, `cuda_cpp`, and `cupy_rawkernel` methods are independent
    validation/performance baselines for the same exact function.
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
    parser = argparse.ArgumentParser(description="Compute exact 2D Hausdorff distance using the v2.0 user API.")
    parser.add_argument("--points-a", type=int, default=8192)
    parser.add_argument("--points-b", type=int, default=8192)
    parser.add_argument(
        "--method",
        choices=(
            "rtdl_v2_user_cuda",
            "rtdl_rt_nearest_witness",
            "rtdl_rt_threshold_search",
            "openmp_cpu",
            "cuda_cpp",
            "cupy_rawkernel",
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
        for method in ("openmp_cpu", "cuda_cpp", "cupy_rawkernel", "rtdl_v2_user_cuda"):
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
