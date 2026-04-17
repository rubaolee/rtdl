from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.rtdl_hausdorff_distance_app import hausdorff_nearest_rows_kernel
from rtdsl.reference import Point


def _module_version(name: str) -> str | None:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return None
    module = __import__(name)
    return str(getattr(module, "__version__", "unknown"))


def _host_info() -> dict[str, object]:
    def _command(cmd: list[str]) -> str | None:
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=5).strip()
        except Exception:
            return None

    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "processor": platform.processor(),
        "nvidia_smi": _command(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "embree_version": _safe_version(rt.embree_version),
        "optix_version": _safe_version(rt.optix_version),
        "vulkan_version": _safe_version(rt.vulkan_version),
        "libraries": {
            "numpy": _module_version("numpy"),
            "scipy": _module_version("scipy"),
            "sklearn": _module_version("sklearn"),
            "faiss": _module_version("faiss"),
        },
    }


def _safe_version(fn: Callable[[], object]) -> str | None:
    try:
        return str(fn())
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def _make_points(count: int, *, seed: int, phase: float) -> tuple[Point, ...]:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("numpy is required for the Goal507 benchmark") from exc

    rng = np.random.default_rng(seed)
    grid = int(math.ceil(math.sqrt(count)))
    xs, ys = np.meshgrid(np.arange(grid, dtype=np.float64), np.arange(grid, dtype=np.float64))
    coords = np.column_stack((xs.ravel()[:count], ys.ravel()[:count]))
    jitter = rng.uniform(-0.05, 0.05, size=(count, 2))
    coords = coords + jitter + np.array([phase, phase * 0.5])
    scale = 1.0 / max(1, grid)
    coords *= scale
    return tuple(Point(id=i + 1, x=float(x), y=float(y)) for i, (x, y) in enumerate(coords))


def _points_to_numpy(points: tuple[Point, ...]):
    import numpy as np

    return np.asarray([(p.x, p.y) for p in points], dtype=np.float32)


def _directed_from_rows(rows) -> tuple[float, int]:
    max_distance = -1.0
    row_count = 0
    for row in rows:
        row_count += 1
        distance = float(row["distance"])
        if distance > max_distance:
            max_distance = distance
    return max_distance, row_count


def _run_rtdl_backend(backend: str, points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    run_map = {
        "cpu": rt.run_cpu,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
    }
    runner = run_map[backend]
    rows_ab = runner(hausdorff_nearest_rows_kernel, query_points=points_a, search_points=points_b)
    directed_ab, rows_ab_count = _directed_from_rows(rows_ab)
    rows_ba = runner(hausdorff_nearest_rows_kernel, query_points=points_b, search_points=points_a)
    directed_ba, rows_ba_count = _directed_from_rows(rows_ba)
    return {
        "hausdorff_distance": max(directed_ab, directed_ba),
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "row_count": rows_ab_count + rows_ba_count,
    }


def _run_scipy_ckdtree(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    from scipy.spatial import cKDTree

    a = _points_to_numpy(points_a)
    b = _points_to_numpy(points_b)
    tree_b = cKDTree(b)
    dist_ab, _ = tree_b.query(a, k=1)
    tree_a = cKDTree(a)
    dist_ba, _ = tree_a.query(b, k=1)
    return {
        "hausdorff_distance": max(float(dist_ab.max()), float(dist_ba.max())),
        "directed_a_to_b": float(dist_ab.max()),
        "directed_b_to_a": float(dist_ba.max()),
        "row_count": len(points_a) + len(points_b),
    }


def _run_sklearn_nearest_neighbors(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    from sklearn.neighbors import NearestNeighbors

    a = _points_to_numpy(points_a)
    b = _points_to_numpy(points_b)
    nn_b = NearestNeighbors(n_neighbors=1, algorithm="auto", metric="euclidean")
    nn_b.fit(b)
    dist_ab, _ = nn_b.kneighbors(a)
    nn_a = NearestNeighbors(n_neighbors=1, algorithm="auto", metric="euclidean")
    nn_a.fit(a)
    dist_ba, _ = nn_a.kneighbors(b)
    return {
        "hausdorff_distance": max(float(dist_ab.max()), float(dist_ba.max())),
        "directed_a_to_b": float(dist_ab.max()),
        "directed_b_to_a": float(dist_ba.max()),
        "row_count": len(points_a) + len(points_b),
    }


def _run_faiss_flat_l2(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    import faiss
    import numpy as np

    a = _points_to_numpy(points_a)
    b = _points_to_numpy(points_b)
    index_b = faiss.IndexFlatL2(2)
    index_b.add(b)
    dist_ab_sq, _ = index_b.search(a, 1)
    index_a = faiss.IndexFlatL2(2)
    index_a.add(a)
    dist_ba_sq, _ = index_a.search(b, 1)
    directed_ab = float(np.sqrt(dist_ab_sq).max())
    directed_ba = float(np.sqrt(dist_ba_sq).max())
    return {
        "hausdorff_distance": max(directed_ab, directed_ba),
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "row_count": len(points_a) + len(points_b),
    }


def _measure(name: str, fn: Callable[[], dict[str, object]], iterations: int) -> dict[str, object]:
    samples: list[float] = []
    payload: dict[str, object] | None = None
    error: str | None = None
    for _ in range(iterations):
        gc.collect()
        start = time.perf_counter()
        try:
            payload = fn()
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            break
        samples.append(time.perf_counter() - start)
    if error is not None:
        return {"name": name, "status": "error", "error": error}
    assert payload is not None
    return {
        "name": name,
        "status": "ok",
        "iterations": iterations,
        "median_sec": statistics.median(samples),
        "min_sec": min(samples),
        "max_sec": max(samples),
        "last_result": payload,
    }


def run_benchmark(sizes: tuple[int, ...], iterations: int, backends: tuple[str, ...]) -> dict[str, object]:
    baseline_fns: dict[str, Callable[[tuple[Point, ...], tuple[Point, ...]], dict[str, object]]] = {
        "scipy_ckdtree": _run_scipy_ckdtree,
        "sklearn_nearest_neighbors": _run_sklearn_nearest_neighbors,
        "faiss_index_flat_l2": _run_faiss_flat_l2,
    }
    available_baselines = {
        name: fn
        for name, fn in baseline_fns.items()
        if (name != "scipy_ckdtree" or importlib.util.find_spec("scipy") is not None)
        and (name != "sklearn_nearest_neighbors" or importlib.util.find_spec("sklearn") is not None)
        and (name != "faiss_index_flat_l2" or importlib.util.find_spec("faiss") is not None)
    }

    cases = []
    for size in sizes:
        points_a = _make_points(size, seed=1000 + size, phase=0.0)
        points_b = _make_points(size, seed=2000 + size, phase=0.0075)
        measurements = []
        for backend in backends:
            measurements.append(
                _measure(
                    f"rtdl_{backend}",
                    lambda backend=backend, points_a=points_a, points_b=points_b: _run_rtdl_backend(
                        backend, points_a, points_b
                    ),
                    iterations,
                )
            )
        for name, fn in available_baselines.items():
            measurements.append(
                _measure(
                    name,
                    lambda fn=fn, points_a=points_a, points_b=points_b: fn(points_a, points_b),
                    iterations,
                )
            )

        reference_distance = None
        for measurement in measurements:
            if measurement["status"] == "ok":
                reference_distance = float(measurement["last_result"]["hausdorff_distance"])
                break
        for measurement in measurements:
            if measurement["status"] == "ok" and reference_distance is not None:
                distance = float(measurement["last_result"]["hausdorff_distance"])
                measurement["matches_reference_distance"] = math.isclose(
                    distance, reference_distance, rel_tol=1e-5, abs_tol=1e-5
                )
        cases.append({"point_count_a": size, "point_count_b": size, "measurements": measurements})
    return {
        "goal": "goal507_hausdorff_linux_perf",
        "host": _host_info(),
        "pid": os.getpid(),
        "iterations": iterations,
        "sizes": list(sizes),
        "backends_requested": list(backends),
        "baseline_sources": {
            "scipy_ckdtree": "SciPy cKDTree.query exact nearest-neighbor API",
            "sklearn_nearest_neighbors": "scikit-learn NearestNeighbors exact Euclidean query API",
            "faiss_index_flat_l2": "FAISS IndexFlatL2 exact flat L2 search",
        },
        "cases": cases,
    }


def _parse_sizes(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(",") if part.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal507 Linux Hausdorff performance benchmark.")
    parser.add_argument("--sizes", default="1000,5000,10000")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--backends", default="embree,optix,vulkan")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run_benchmark(
        sizes=_parse_sizes(args.sizes),
        iterations=args.iterations,
        backends=tuple(part.strip() for part in args.backends.split(",") if part.strip()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "cases": len(payload["cases"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
