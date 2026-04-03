from __future__ import annotations

import json
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import rtdsl as rt
from rtdsl import datasets


DATASET_DIR = Path("build/datasets/uscounty_zipcode/uscounty_feature_layer")
RESULTS_PATH = Path("build/goal44_results.json")
POINT_COUNT = 10_000
POINT_SEED = 20260402
SCALE_FEATURE_LIMITS = {
    "smoke": 10,
    "medium": 250,
}


@dataclass(frozen=True)
class ScaleResult:
    scale: str
    max_features: int
    n_polygons: int
    n_points: int
    total_intersections: int
    embree_sec: float
    optix_jit_sec: float
    optix_warm_sec: float
    speedup: float
    row_count_parity: bool
    exact_row_parity: bool | None
    parity_mode: str


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_county():
    polys = rt.input("polys", rt.Polygons)
    points = rt.input("points", rt.Points)
    candidates = rt.traverse(points, polys, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon())
    return rt.emit(hits, fields=["point_id", "poly_id"])


def _pack_polygons(max_features: int):
    cdb = datasets.arcgis_pages_to_cdb(DATASET_DIR, name="uscounty", max_features=max_features)
    poly_list = datasets.chains_to_polygons(cdb)
    poly_ids: list[int] = []
    vertex_offsets: list[int] = []
    vertex_counts: list[int] = []
    vertices_xy: list[float] = []
    current_offset = 0
    for poly in poly_list:
        poly_ids.append(poly["id"])
        vertex_offsets.append(current_offset)
        vertex_counts.append(len(poly["vertices"]))
        for x, y in poly["vertices"]:
            vertices_xy.extend([float(x), float(y)])
        current_offset += len(poly["vertices"])
    return rt.pack_polygons(
        ids=poly_ids,
        vertex_offsets=vertex_offsets,
        vertex_counts=vertex_counts,
        vertices_xy=vertices_xy,
    )


def _generate_points(n_points: int, *, seed: int):
    rng = random.Random(seed)
    point_ids = list(range(n_points))
    px = [rng.uniform(-125.0, -66.0) for _ in range(n_points)]
    py = [rng.uniform(24.0, 49.0) for _ in range(n_points)]
    return rt.pack_points(ids=point_ids, x=px, y=py)


def _run_scale(scale: str, max_features: int) -> ScaleResult:
    print(f"\n--- Scale: {scale} (max_features={max_features}) ---")
    polys = _pack_polygons(max_features)
    points = _generate_points(POINT_COUNT, seed=POINT_SEED)
    print(f"Loaded {polys.polygon_count} polygons and generated {POINT_COUNT} deterministic points.")

    os.environ["RTDL_OPTIX_PTX_COMPILER"] = "nvcc"
    os.environ["RTDL_NVCC"] = "/usr/bin/nvcc"

    start_cpu = time.perf_counter()
    cpu_rows = rt.run_embree(point_in_county, polys=polys, points=points, result_mode="raw")
    end_cpu = time.perf_counter()

    start_optix_jit = time.perf_counter()
    optix_rows = rt.run_optix(point_in_county, polys=polys, points=points, result_mode="raw")
    end_optix_jit = time.perf_counter()

    start_optix_warm = time.perf_counter()
    optix_rows_warm = rt.run_optix(point_in_county, polys=polys, points=points, result_mode="raw")
    end_optix_warm = time.perf_counter()

    try:
        row_count_parity = cpu_rows.row_count == optix_rows.row_count == optix_rows_warm.row_count
        exact_row_parity = None
        parity_mode = "row_count"
        if scale == "smoke":
            parity_mode = "exact_rows"
            exact_row_parity = cpu_rows.to_tuple_rows() == optix_rows.to_tuple_rows() == optix_rows_warm.to_tuple_rows()
        speedup = (end_cpu - start_cpu) / (end_optix_warm - start_optix_warm) if (end_optix_warm - start_optix_warm) > 0 else 0.0
        total_intersections = optix_rows_warm.row_count
        print(
            f"Embree: {end_cpu - start_cpu:.4f}s, "
            f"OptiX jit: {end_optix_jit - start_optix_jit:.4f}s, "
            f"OptiX warm: {end_optix_warm - start_optix_warm:.4f}s, "
            f"rows: {total_intersections}, parity_mode: {parity_mode}"
        )
        return ScaleResult(
            scale=scale,
            max_features=max_features,
            n_polygons=polys.polygon_count,
            n_points=POINT_COUNT,
            total_intersections=total_intersections,
            embree_sec=end_cpu - start_cpu,
            optix_jit_sec=end_optix_jit - start_optix_jit,
            optix_warm_sec=end_optix_warm - start_optix_warm,
            speedup=speedup,
            row_count_parity=row_count_parity,
            exact_row_parity=exact_row_parity,
            parity_mode=parity_mode,
        )
    finally:
        cpu_rows.close()
        optix_rows.close()
        optix_rows_warm.close()


def run_benchmark() -> dict[str, object]:
    if not DATASET_DIR.exists():
        print(f"Error: Dataset directory {DATASET_DIR} not found.")
        sys.exit(1)

    print("--- Goal 44: OptiX vs Embree Performance Benchmark ---")
    print("Dataset: US County Feature Layer (Staged) + deterministic synthetic points")

    results = [_run_scale(scale, max_features) for scale, max_features in SCALE_FEATURE_LIMITS.items()]
    payload = {
        "dataset": "uscounty_zipcode/uscounty_feature_layer",
        "point_seed": POINT_SEED,
        "point_count": POINT_COUNT,
        "scales": [result.__dict__ for result in results],
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Results saved to {RESULTS_PATH}")
    return payload


if __name__ == "__main__":
    run_benchmark()
