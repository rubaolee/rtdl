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
from rtdsl.reference import Point


@rt.kernel(backend="rtdl", precision="float_approx")
def hausdorff_nearest_rows_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.knn_rows(k=1))
    return rt.emit(nearest, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


def make_authored_point_sets(copies: int = 1) -> dict[str, tuple[Point, ...]]:
    if copies < 1:
        raise ValueError("copies must be at least 1")

    base_a = (
        Point(id=1, x=0.0, y=0.0),
        Point(id=2, x=1.0, y=0.0),
        Point(id=3, x=1.0, y=1.0),
        Point(id=4, x=0.0, y=1.0),
    )
    base_b = (
        Point(id=101, x=0.0, y=0.0),
        Point(id=102, x=1.2, y=0.1),
        Point(id=103, x=1.0, y=1.3),
        Point(id=104, x=-0.2, y=0.8),
    )

    points_a: list[Point] = []
    points_b: list[Point] = []
    for copy_index in range(copies):
        offset = 10.0 * copy_index
        id_offset = 1000 * copy_index
        for point in base_a:
            points_a.append(Point(id=point.id + id_offset, x=point.x + offset, y=point.y))
        for point in base_b:
            points_b.append(Point(id=point.id + id_offset, x=point.x + offset, y=point.y))
    return {"points_a": tuple(points_a), "points_b": tuple(points_b)}


def _run_nearest(backend: str, query_points: tuple[Point, ...], search_points: tuple[Point, ...]):
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "cpu":
        return rt.run_cpu(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "embree":
        return rt.run_embree(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _directed_from_rows(rows: Iterable[dict[str, object]], label: str) -> dict[str, object]:
    nearest_rows = list(rows)
    if not nearest_rows:
        raise ValueError(f"directed Hausdorff pass `{label}` produced no nearest-neighbor rows")

    witness = max(
        nearest_rows,
        key=lambda row: (float(row["distance"]), -int(row["query_id"]), -int(row["neighbor_id"])),
    )
    return {
        "distance": float(witness["distance"]),
        "source_id": int(witness["query_id"]),
        "target_id": int(witness["neighbor_id"]),
        "row_count": len(nearest_rows),
    }


def directed_hausdorff_bruteforce(source: tuple[Point, ...], target: tuple[Point, ...]) -> dict[str, object]:
    if not source or not target:
        raise ValueError("Hausdorff distance requires non-empty point sets")

    best_source: Point | None = None
    best_target: Point | None = None
    best_distance = -1.0
    for source_point in source:
        nearest_target = min(
            target,
            key=lambda target_point: (
                math.hypot(source_point.x - target_point.x, source_point.y - target_point.y),
                target_point.id,
            ),
        )
        distance = math.hypot(source_point.x - nearest_target.x, source_point.y - nearest_target.y)
        if (
            distance > best_distance
            or (math.isclose(distance, best_distance) and best_source is not None and source_point.id < best_source.id)
            or best_source is None
        ):
            best_source = source_point
            best_target = nearest_target
            best_distance = distance

    assert best_source is not None
    assert best_target is not None
    return {
        "distance": best_distance,
        "source_id": best_source.id,
        "target_id": best_target.id,
        "row_count": len(source),
    }


def brute_force_hausdorff(points_a: tuple[Point, ...], points_b: tuple[Point, ...]) -> dict[str, object]:
    directed_ab = directed_hausdorff_bruteforce(points_a, points_b)
    directed_ba = directed_hausdorff_bruteforce(points_b, points_a)
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    return {
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
    }


def run_app(backend: str = "cpu_python_reference", copies: int = 1) -> dict[str, object]:
    case = make_authored_point_sets(copies=copies)
    points_a = case["points_a"]
    points_b = case["points_b"]
    if not points_a or not points_b:
        raise ValueError("Hausdorff distance requires non-empty point sets")

    rows_ab = _run_nearest(backend, points_a, points_b)
    rows_ba = _run_nearest(backend, points_b, points_a)
    directed_ab = _directed_from_rows(rows_ab, "a_to_b")
    directed_ba = _directed_from_rows(rows_ba, "b_to_a")
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    oracle = brute_force_hausdorff(points_a, points_b)

    return {
        "app": "hausdorff_distance",
        "backend": backend,
        "copies": copies,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
        "oracle": oracle,
        "matches_oracle": math.isclose(
            float(undirected[1]["distance"]),
            float(oracle["hausdorff_distance"]),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        "rtdl_role": "RTDL emits k=1 nearest-neighbor rows; Python reduces them to directed and undirected Hausdorff scalars.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived Hausdorff distance app: RTDL nearest-neighbor rows plus Python reduction."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1, help="tile the small authored point sets")
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, args.copies), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
