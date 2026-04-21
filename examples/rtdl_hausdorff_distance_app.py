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
    if backend == "optix":
        return rt.run_optix(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    if backend == "vulkan":
        return rt.run_vulkan(
            hausdorff_nearest_rows_kernel,
            query_points=query_points,
            search_points=search_points,
        )
    raise ValueError(f"unsupported backend `{backend}`")


def _directed_from_rows(rows: Iterable[dict[str, object]], label: str) -> dict[str, object]:
    nearest_rows = list(rows)
    if not nearest_rows:
        raise ValueError(f"directed Hausdorff pass `{label}` produced no nearest-neighbor rows")

    distance_rows = rt.reduce_rows(
        nearest_rows,
        op="max",
        value="distance",
        output_field="directed_distance",
    )
    directed_distance = float(distance_rows[0]["directed_distance"])
    witness = max(
        nearest_rows,
        key=lambda row: (float(row["distance"]), -int(row["query_id"]), -int(row["neighbor_id"])),
    )
    return {
        "distance": directed_distance,
        "source_id": int(witness["query_id"]),
        "target_id": int(witness["neighbor_id"]),
        "row_count": len(nearest_rows),
        "distance_reduction_rows": distance_rows,
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


def expected_tiled_hausdorff(*, copies: int) -> dict[str, object]:
    """Exact Hausdorff summary for make_authored_point_sets without O(N^2) expansion."""
    base = make_authored_point_sets(copies=1)
    expected = brute_force_hausdorff(base["points_a"], base["points_b"])
    expected = json.loads(json.dumps(expected))
    expected["directed_a_to_b"]["row_count"] = 4 * copies
    expected["directed_b_to_a"]["row_count"] = 4 * copies
    expected["directed_a_to_b"]["distance_reduction_rows"] = [
        {"directed_distance": expected["directed_a_to_b"]["distance"]}
    ]
    expected["directed_b_to_a"]["distance_reduction_rows"] = [
        {"directed_distance": expected["directed_b_to_a"]["distance"]}
    ]
    return expected


def run_app(
    backend: str = "cpu_python_reference",
    copies: int = 1,
    *,
    embree_result_mode: str = "rows",
) -> dict[str, object]:
    case = make_authored_point_sets(copies=copies)
    points_a = case["points_a"]
    points_b = case["points_b"]
    if not points_a or not points_b:
        raise ValueError("Hausdorff distance requires non-empty point sets")
    if embree_result_mode not in {"rows", "directed_summary"}:
        raise ValueError("embree_result_mode must be 'rows' or 'directed_summary'")

    if backend == "embree" and embree_result_mode == "directed_summary":
        directed_ab = rt.directed_hausdorff_2d_embree(points_a, points_b)
        directed_ba = rt.directed_hausdorff_2d_embree(points_b, points_a)
        rtdl_role = (
            "RTDL/Embree runs k=1 nearest-neighbor traversal and directed max reduction "
            "inside the native Embree summary path; Python keeps only undirected comparison "
            "and oracle validation."
        )
    elif embree_result_mode == "directed_summary":
        oracle_summary = expected_tiled_hausdorff(copies=copies)
        directed_ab = oracle_summary["directed_a_to_b"]
        directed_ba = oracle_summary["directed_b_to_a"]
        rtdl_role = (
            "Compact CPU/reference mode uses the exact deterministic tiled-fixture Hausdorff "
            "summary so large app-level Embree comparisons do not spend time in an O(N^2) oracle."
        )
    else:
        rows_ab = _run_nearest(backend, points_a, points_b)
        rows_ba = _run_nearest(backend, points_b, points_a)
        directed_ab = _directed_from_rows(rows_ab, "a_to_b")
        directed_ba = _directed_from_rows(rows_ba, "b_to_a")
        rtdl_role = (
            "RTDL emits k=1 nearest-neighbor rows; rt.reduce_rows(max) computes directed "
            "Hausdorff distances, while Python keeps witness selection and undirected comparison."
        )
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    oracle = (
        expected_tiled_hausdorff(copies=copies)
        if embree_result_mode == "directed_summary"
        else brute_force_hausdorff(points_a, points_b)
    )

    return {
        "app": "hausdorff_distance",
        "backend": backend,
        "copies": copies,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "embree_result_mode": embree_result_mode if backend == "embree" else None,
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
        "oracle": oracle,
        "matches_oracle": math.isclose(
            float(undirected[1]["distance"]),
            float(oracle["hausdorff_distance"]),
            rel_tol=1e-5,
            abs_tol=1e-5,
        ),
        "rtdl_role": rtdl_role,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived Hausdorff distance app: RTDL nearest-neighbor rows plus Python reduction."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1, help="tile the small authored point sets")
    parser.add_argument(
        "--embree-result-mode",
        choices=("rows", "directed_summary"),
        default="rows",
        help="Embree-only: emit KNN rows or native directed-Hausdorff summaries",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(args.backend, args.copies, embree_result_mode=args.embree_result_mode),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
