from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def lsi_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


@rt.kernel(backend="rtdl", precision="float_approx")
def pip_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def overlay_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(hits, fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_2d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_hitcount_kernel():
    segments = rt.input("segments", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_anyhit_kernel():
    segments = rt.input("segments", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.1, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.1, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.1, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


@rt.kernel(backend="rtdl", precision="float_approx")
def conjunctive_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"))
    return rt.emit(groups, fields=["region", "sum"])


def _square(poly_id: int, x0: float, y0: float, size: float) -> rt.Polygon:
    return rt.Polygon(
        id=poly_id,
        vertices=((x0, y0), (x0 + size, y0), (x0 + size, y0 + size), (x0, y0 + size)),
    )


def _graph():
    return rt.csr_graph(row_offsets=(0, 2, 4, 6, 6), column_indices=(1, 2, 0, 2, 0, 1))


def _table():
    return (
        {"row_id": 1, "region": "east", "ship_date": 10, "discount": 5, "quantity": 12, "revenue": 100},
        {"row_id": 2, "region": "east", "ship_date": 12, "discount": 6, "quantity": 18, "revenue": 150},
        {"row_id": 3, "region": "west", "ship_date": 13, "discount": 6, "quantity": 10, "revenue": 200},
        {"row_id": 4, "region": "west", "ship_date": 14, "discount": 7, "quantity": 30, "revenue": 300},
    )


def cases() -> tuple[dict[str, object], ...]:
    points_2d = (
        rt.Point(id=1, x=0.0, y=0.0),
        rt.Point(id=2, x=1.0, y=0.0),
        rt.Point(id=3, x=3.0, y=0.0),
    )
    points_3d = (
        rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
        rt.Point3D(id=2, x=1.0, y=0.0, z=0.0),
        rt.Point3D(id=3, x=3.0, y=0.0, z=0.0),
    )
    return (
        {
            "workload": "segment_intersection",
            "kernel": lsi_kernel,
            "inputs": {
                "left": (rt.Segment(id=1, x0=0, y0=0, x1=2, y1=2),),
                "right": (rt.Segment(id=10, x0=0, y0=2, x1=2, y1=0),),
            },
        },
        {
            "workload": "point_in_polygon",
            "kernel": pip_kernel,
            "inputs": {"points": points_2d[:2], "polygons": (_square(10, -0.5, -0.5, 2.0),)},
        },
        {
            "workload": "overlay_compose",
            "kernel": overlay_kernel,
            "inputs": {"left": (_square(1, 0, 0, 2),), "right": (_square(2, 1, 1, 2),)},
        },
        {
            "workload": "ray_triangle_hit_count_2d",
            "kernel": ray_triangle_2d_kernel,
            "inputs": {
                "rays": (rt.Ray2D(id=1, ox=0, oy=0, dx=1, dy=0, tmax=10),),
                "triangles": (rt.Triangle(id=10, x0=2, y0=-1, x1=3, y1=1, x2=4, y2=-1),),
            },
        },
        {
            "workload": "ray_triangle_hit_count_3d",
            "kernel": ray_triangle_3d_kernel,
            "inputs": {
                "rays": (
                    rt.Ray3D(id=1, ox=0.25, oy=0.25, oz=-1, dx=0, dy=0, dz=1, tmax=3),
                    rt.Ray3D(id=2, ox=2, oy=2, oz=-1, dx=0, dy=0, dz=1, tmax=3),
                ),
                "triangles": (
                    rt.Triangle3D(id=10, x0=0, y0=0, z0=0, x1=1, y1=0, z1=0, x2=0, y2=1, z2=0),
                    rt.Triangle3D(id=11, x0=0, y0=0, z0=1, x1=1, y1=0, z1=1, x2=0, y2=1, z2=1),
                ),
            },
        },
        {
            "workload": "segment_polygon_hitcount",
            "kernel": segment_polygon_hitcount_kernel,
            "inputs": {"segments": (rt.Segment(id=1, x0=-1, y0=1, x1=3, y1=1),), "polygons": (_square(10, 0, 0, 2),)},
        },
        {
            "workload": "segment_polygon_anyhit_rows",
            "kernel": segment_polygon_anyhit_kernel,
            "inputs": {"segments": (rt.Segment(id=1, x0=-1, y0=1, x1=3, y1=1),), "polygons": (_square(10, 0, 0, 2),)},
        },
        {
            "workload": "point_nearest_segment",
            "kernel": point_nearest_segment_kernel,
            "inputs": {"points": (rt.Point(id=1, x=0.2, y=0.5),), "segments": (rt.Segment(id=10, x0=0, y0=0, x1=1, y1=0),)},
        },
        {"workload": "fixed_radius_neighbors_2d", "kernel": fixed_radius_2d_kernel, "inputs": {"query_points": points_2d, "search_points": points_2d}},
        {"workload": "fixed_radius_neighbors_3d", "kernel": fixed_radius_3d_kernel, "inputs": {"query_points": points_3d, "search_points": points_3d}},
        {"workload": "bounded_knn_rows_3d", "kernel": bounded_knn_3d_kernel, "inputs": {"query_points": points_3d, "search_points": points_3d}},
        {"workload": "knn_rows_2d", "kernel": knn_2d_kernel, "inputs": {"query_points": points_2d, "search_points": points_2d}},
        {"workload": "knn_rows_3d", "kernel": knn_3d_kernel, "inputs": {"query_points": points_3d, "search_points": points_3d}},
        {
            "workload": "bfs_discover",
            "kernel": bfs_kernel,
            "inputs": {"frontier": (rt.FrontierVertex(vertex_id=0, level=0),), "graph": _graph(), "visited": ()},
        },
        {
            "workload": "triangle_match",
            "kernel": triangle_match_kernel,
            "inputs": {"seeds": ((0, 1),), "graph": _graph()},
        },
        {
            "workload": "conjunctive_scan",
            "kernel": conjunctive_scan_kernel,
            "inputs": {"predicates": (("discount", "eq", 6),), "table": _table()},
        },
        {
            "workload": "grouped_count",
            "kernel": grouped_count_kernel,
            "inputs": {"query": {"group_keys": ("region",), "predicates": (("discount", "ge", 6),)}, "table": _table()},
        },
        {
            "workload": "grouped_sum",
            "kernel": grouped_sum_kernel,
            "inputs": {
                "query": {"group_keys": ("region",), "value_field": "revenue", "predicates": (("discount", "ge", 6),)},
                "table": _table(),
            },
        },
    )


def _run_timed(fn: Callable[[], object]) -> tuple[object, float]:
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def run_matrix() -> dict[str, object]:
    results = []
    summary = {"pass": 0, "not_implemented": 0, "hiprt_unavailable": 0, "fail": 0}
    for case in cases():
        workload = str(case["workload"])
        kernel = case["kernel"]
        inputs = dict(case["inputs"])
        cpu_rows, cpu_seconds = _run_timed(lambda: rt.run_cpu_python_reference(kernel, **inputs))
        try:
            hiprt_rows, hiprt_seconds = _run_timed(lambda: rt.run_hiprt(kernel, **inputs))
        except NotImplementedError as exc:
            summary["not_implemented"] += 1
            results.append(
                {
                    "workload": workload,
                    "status": "NOT_IMPLEMENTED",
                    "cpu_reference_row_count": len(cpu_rows),
                    "cpu_reference_seconds": cpu_seconds,
                    "message": str(exc),
                }
            )
            continue
        except (FileNotFoundError, OSError) as exc:
            summary["hiprt_unavailable"] += 1
            results.append(
                {
                    "workload": workload,
                    "status": "HIPRT_UNAVAILABLE",
                    "cpu_reference_row_count": len(cpu_rows),
                    "cpu_reference_seconds": cpu_seconds,
                    "error_type": type(exc).__name__,
                    "message": str(exc).splitlines()[0],
                }
            )
            continue
        except Exception as exc:  # noqa: BLE001 - this is a matrix report, not a library boundary.
            summary["fail"] += 1
            results.append(
                {
                    "workload": workload,
                    "status": "FAIL",
                    "cpu_reference_row_count": len(cpu_rows),
                    "cpu_reference_seconds": cpu_seconds,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )
            continue
        parity = tuple(hiprt_rows) == tuple(cpu_rows)
        summary["pass" if parity else "fail"] += 1
        results.append(
            {
                "workload": workload,
                "status": "PASS" if parity else "FAIL",
                "cpu_reference_row_count": len(cpu_rows),
                "hiprt_row_count": len(hiprt_rows),
                "cpu_reference_seconds": cpu_seconds,
                "hiprt_seconds": hiprt_seconds,
                "parity": parity,
            }
        )
    return {
        "goal": 547,
        "description": "HIPRT correctness matrix across v0.9 target workloads",
        "summary": summary,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Goal 547 HIPRT correctness matrix.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_matrix()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if payload["summary"]["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
