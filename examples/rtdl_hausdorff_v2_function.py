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

from examples import rtdl_hausdorff_v2_user_benchmark as lab


@dataclass(frozen=True)
class HausdorffResult:
    distance: float
    direction: str
    source_index: int
    target_index: int
    elapsed_sec: float
    method: str


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
        choices=("rtdl_v2_user_cuda", "openmp_cpu", "cuda_cpp", "cupy_rawkernel"),
        default="rtdl_v2_user_cuda",
    )
    parser.add_argument("--compare", action="store_true", help="also run all available baselines and compare")
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args(list(argv) if argv is not None else None)

    points_a = make_demo_points(args.points_a, seed=11)
    points_b = make_demo_points(args.points_b, seed=29, offset=(0.08, -0.06))
    primary = hausdorff_distance_2d(points_a, points_b, method=args.method, warmup=args.warmup)
    payload: dict[str, object] = {"primary": asdict(primary)}
    if args.compare:
        comparisons = {}
        for method in ("openmp_cpu", "cuda_cpp", "cupy_rawkernel", "rtdl_v2_user_cuda"):
            start = time.perf_counter()
            try:
                result = hausdorff_distance_2d(points_a, points_b, method=method, warmup=args.warmup)
                comparisons[method] = asdict(result)
                comparisons[method]["matches_primary"] = math.isclose(
                    result.distance,
                    primary.distance,
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                )
            except Exception as exc:
                comparisons[method] = {"error": repr(exc), "elapsed_sec": time.perf_counter() - start}
        payload["comparisons"] = comparisons
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
