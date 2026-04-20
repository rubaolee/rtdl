from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


RADIUS = 0.35
K_MAX = 16
MIN_NEIGHBORS_INCLUDING_SELF = 3


@rt.kernel(backend="rtdl", precision="float_approx")
def outlier_neighbor_rows_kernel():
    points = rt.input("points", rt.Points, role="probe")
    candidates = rt.traverse(points, points, accel="bvh")
    neighbors = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=RADIUS, k_max=K_MAX))
    return rt.emit(neighbors, fields=["query_id", "neighbor_id", "distance"])


def make_outlier_case(*, copies: int = 1) -> dict[str, tuple[rt.Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_points = (
        rt.Point(id=1, x=0.00, y=0.00),
        rt.Point(id=2, x=0.12, y=0.04),
        rt.Point(id=3, x=-0.10, y=0.08),
        rt.Point(id=4, x=2.00, y=2.00),
        rt.Point(id=5, x=2.14, y=2.05),
        rt.Point(id=6, x=1.88, y=1.94),
        rt.Point(id=7, x=4.50, y=0.00),
        rt.Point(id=8, x=-3.00, y=2.50),
    )
    points: list[rt.Point] = []
    for copy_index in range(copies):
        id_offset = 100 * copy_index
        x_offset = 7.0 * copy_index
        for point in base_points:
            points.append(rt.Point(id=point.id + id_offset, x=point.x + x_offset, y=point.y))
    return {"points": tuple(points)}


def _run_rows(backend: str, case: dict[str, tuple[rt.Point, ...]]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(outlier_neighbor_rows_kernel, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(outlier_neighbor_rows_kernel, **case))
    if backend == "embree":
        return tuple(rt.run_embree(outlier_neighbor_rows_kernel, **case))
    if backend == "optix":
        return tuple(rt.run_optix(outlier_neighbor_rows_kernel, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(outlier_neighbor_rows_kernel, **case))
    if backend == "scipy":
        return tuple(rt.run_scipy_fixed_radius_neighbors(case["points"], case["points"], radius=RADIUS, k_max=K_MAX))
    raise ValueError(f"unsupported backend `{backend}`")


def density_rows_from_neighbor_rows(
    points: tuple[rt.Point, ...],
    rows: Iterable[dict[str, object]],
    *,
    min_neighbors_including_self: int = MIN_NEIGHBORS_INCLUDING_SELF,
) -> tuple[dict[str, object], ...]:
    counts: dict[int, int] = {point.id: 0 for point in points}
    for row in rt.reduce_rows(
        tuple(rows),
        group_by="query_id",
        op="count",
        output_field="neighbor_count",
    ):
        query_id = int(row["query_id"])
        if query_id in counts:
            counts[query_id] = int(row["neighbor_count"])

    return tuple(
        {
            "point_id": point_id,
            "neighbor_count": counts[point_id],
            "is_outlier": counts[point_id] < min_neighbors_including_self,
        }
        for point_id in sorted(counts)
    )


def brute_force_outlier_rows(
    points: tuple[rt.Point, ...],
    *,
    radius: float = RADIUS,
    min_neighbors_including_self: int = MIN_NEIGHBORS_INCLUDING_SELF,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for query in points:
        for neighbor in points:
            distance = math.hypot(query.x - neighbor.x, query.y - neighbor.y)
            if distance <= radius:
                rows.append({"query_id": query.id, "neighbor_id": neighbor.id, "distance": distance})
    return density_rows_from_neighbor_rows(
        points,
        rows,
        min_neighbors_including_self=min_neighbors_including_self,
    )


def run_app(backend: str = "cpu_python_reference", *, copies: int = 1) -> dict[str, object]:
    case = make_outlier_case(copies=copies)
    neighbor_rows = _run_rows(backend, case)
    density_rows = density_rows_from_neighbor_rows(case["points"], neighbor_rows)
    oracle_rows = brute_force_outlier_rows(case["points"])
    outlier_ids = [int(row["point_id"]) for row in density_rows if bool(row["is_outlier"])]

    return {
        "app": "outlier_detection",
        "backend": backend,
        "radius": RADIUS,
        "k_max": K_MAX,
        "min_neighbors_including_self": MIN_NEIGHBORS_INCLUDING_SELF,
        "copies": copies,
        "point_count": len(case["points"]),
        "neighbor_row_count": len(neighbor_rows),
        "density_rows": density_rows,
        "outlier_point_ids": outlier_ids,
        "oracle_density_rows": oracle_rows,
        "matches_oracle": density_rows == oracle_rows,
        "rtdl_role": "RTDL emits fixed-radius neighbor rows; rt.reduce_rows(count) converts them into local density counts, and Python applies the outlier threshold.",
        "boundary": "Bounded density-threshold outlier demo only; RTDL does not yet expose density scoring as a language primitive.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived outlier detection app: RTDL neighbor rows plus Python density thresholding."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan", "scipy"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, copies=args.copies), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
