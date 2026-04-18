from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.rtdl_ann_candidate_app import run_app as run_ann
from examples.rtdl_db_conjunctive_scan import run_backend as run_db_scan
from examples.rtdl_dbscan_clustering_app import run_app as run_dbscan
from examples.rtdl_db_grouped_count import run_backend as run_grouped_count
from examples.rtdl_db_grouped_sum import run_backend as run_grouped_sum
from examples.rtdl_barnes_hut_force_app import run_app as run_barnes_hut
from examples.rtdl_fixed_radius_neighbors import run_case as run_fixed_radius
from examples.rtdl_graph_bfs import run_backend as run_graph_bfs
from examples.rtdl_graph_triangle_count import run_backend as run_triangle_count
from examples.rtdl_hausdorff_distance_app import run_app as run_hausdorff
from examples.rtdl_knn_rows import run_case as run_knn_rows
from examples.rtdl_outlier_detection_app import run_app as run_outlier
from examples.rtdl_polygon_pair_overlap_area_rows import (
    make_authored_polygon_pair_overlap_case,
)
from examples.rtdl_polygon_pair_overlap_area_rows import (
    polygon_pair_overlap_area_rows_reference,
)
from examples.rtdl_polygon_set_jaccard import make_authored_polygon_set_jaccard_case
from examples.rtdl_polygon_set_jaccard import polygon_set_jaccard_reference
from examples.rtdl_robot_collision_screening_app import run_app as run_robot_collision
from examples.rtdl_segment_polygon_anyhit_rows import run_case as run_segment_anyhit
from examples.rtdl_segment_polygon_hitcount import run_case as run_segment_hitcount


@rt.kernel(backend="rtdl", precision="float_approx")
def lsi_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def pip_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def overlay_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_tri_hitcount_kernel():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(nearest, fields=["point_id", "segment_id", "distance"])


def _run_reference(kernel_fn, **inputs):
    return rt.run_cpu_python_reference(kernel_fn, **inputs)


def _recipe(name: str, input_summary: str, output_summary: str, rows) -> dict[str, object]:
    return {
        "feature": name,
        "input": input_summary,
        "output": output_summary,
        "rows": rows,
    }


def run_cookbook() -> dict[str, object]:
    ann_result = run_ann("cpu_python_reference")
    barnes_hut_result = run_barnes_hut("cpu_python_reference")
    dbscan_result = run_dbscan("cpu_python_reference")
    hausdorff_result = run_hausdorff("cpu_python_reference")
    outlier_result = run_outlier("cpu_python_reference")
    robot_collision_result = run_robot_collision("cpu_python_reference")
    recipes = [
        _recipe(
            "lsi",
            "two segment sets",
            "segment/segment intersection rows",
            _run_reference(
                lsi_kernel,
                left=(rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),),
                right=(rt.Segment(id=2, x0=0.0, y0=2.0, x1=2.0, y1=0.0),),
            ),
        ),
        _recipe(
            "pip",
            "points plus polygons",
            "containment rows",
            _run_reference(
                pip_kernel,
                points=(rt.Point(id=10, x=1.0, y=1.0),),
                polygons=(
                    rt.Polygon(
                        id=20,
                        vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
                    ),
                ),
            ),
        ),
        _recipe(
            "overlay",
            "left polygons plus right polygons",
            "overlap seed rows for exact follow-up",
            _run_reference(
                overlay_kernel,
                left=(
                    rt.Polygon(
                        id=1,
                        vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
                    ),
                ),
                right=(
                    rt.Polygon(
                        id=2,
                        vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0)),
                    ),
                ),
            ),
        ),
        _recipe(
            "ray_tri_hitcount",
            "rays plus triangles",
            "one hit count per ray",
            _run_reference(
                ray_tri_hitcount_kernel,
                rays=(rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),),
                triangles=(
                    rt.Triangle(
                        id=10,
                        x0=3.0,
                        y0=-1.0,
                        x1=4.0,
                        y1=1.0,
                        x2=5.0,
                        y2=-1.0,
                    ),
                ),
            ),
        ),
        _recipe(
            "robot_collision_screening_app",
            "robot link edge rays plus obstacle triangles",
            "pose collision flags reduced from ray/triangle hit counts",
            {
                "colliding_pose_ids": robot_collision_result["colliding_pose_ids"],
                "matches_oracle": robot_collision_result["matches_oracle"],
            },
        ),
        _recipe(
            "barnes_hut_force_app",
            "bodies plus Python-built quadtree nodes",
            "body-to-node candidate rows reduced to approximate force vectors",
            {
                "candidate_row_count": barnes_hut_result["candidate_row_count"],
                "max_relative_error": barnes_hut_result["max_relative_error"],
            },
        ),
        _recipe(
            "point_nearest_segment",
            "points plus segments",
            "nearest segment and distance rows",
            _run_reference(
                point_nearest_segment_kernel,
                points=(rt.Point(id=1, x=1.0, y=1.0),),
                segments=(rt.Segment(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0),),
            ),
        ),
        _recipe(
            "segment_polygon_hitcount",
            "segments plus polygons",
            "one hit count per segment",
            run_segment_hitcount(
                "cpu_python_reference",
                "authored_segment_polygon_minimal",
            )["rows"][:3],
        ),
        _recipe(
            "segment_polygon_anyhit_rows",
            "segments plus polygons",
            "segment/polygon hit rows",
            run_segment_anyhit(
                "cpu_python_reference",
                "authored_segment_polygon_minimal",
            )["rows"][:3],
        ),
        _recipe(
            "polygon_pair_overlap_area_rows",
            "left polygons plus right polygons",
            "pairwise overlap area rows",
            _run_reference(
                polygon_pair_overlap_area_rows_reference,
                **make_authored_polygon_pair_overlap_case(),
            ),
        ),
        _recipe(
            "polygon_set_jaccard",
            "two polygon sets",
            "one set-level Jaccard row",
            _run_reference(
                polygon_set_jaccard_reference,
                **make_authored_polygon_set_jaccard_case(),
            ),
        ),
        _recipe(
            "fixed_radius_neighbors",
            "query points plus search points",
            "neighbor rows within radius",
            run_fixed_radius("cpu_python_reference")["rows"],
        ),
        _recipe(
            "knn_rows",
            "query points plus search points",
            "ranked nearest-neighbor rows",
            run_knn_rows("cpu_python_reference")["rows"],
        ),
        _recipe(
            "hausdorff_distance_app",
            "two point sets",
            "directed nearest-neighbor rows reduced to one Hausdorff distance",
            {
                "hausdorff_distance": hausdorff_result["hausdorff_distance"],
                "witness_direction": hausdorff_result["witness_direction"],
            },
        ),
        _recipe(
            "ann_candidate_app",
            "query points plus Python-selected candidate points",
            "approximate nearest-neighbor rows plus recall/distance quality",
            {
                "recall_at_1": ann_result["recall_at_1"],
                "mean_distance_ratio": ann_result["mean_distance_ratio"],
            },
        ),
        _recipe(
            "outlier_detection_app",
            "one point cloud",
            "fixed-radius neighbor rows reduced to density-threshold outlier labels",
            {
                "outlier_point_ids": outlier_result["outlier_point_ids"],
                "matches_oracle": outlier_result["matches_oracle"],
            },
        ),
        _recipe(
            "dbscan_clustering_app",
            "one point cloud",
            "fixed-radius neighbor rows expanded into density-cluster labels",
            {
                "cluster_sizes": dbscan_result["cluster_sizes"],
                "noise_point_ids": dbscan_result["noise_point_ids"],
                "matches_oracle": dbscan_result["matches_oracle"],
            },
        ),
        _recipe(
            "bfs",
            "frontier vertices plus graph CSR plus visited set",
            "newly discovered vertex rows",
            run_graph_bfs("cpu_python_reference")["rows"],
        ),
        _recipe(
            "triangle_count",
            "seed edges plus graph CSR",
            "triangle rows",
            run_triangle_count("cpu_python_reference")["rows"],
        ),
        _recipe(
            "conjunctive_scan",
            "denormalized rows plus predicates",
            "matching row IDs",
            run_db_scan("cpu_python_reference")["rows"],
        ),
        _recipe(
            "grouped_count",
            "denormalized rows plus predicates plus group key",
            "grouped count rows",
            run_grouped_count("cpu_python_reference")["rows"],
        ),
        _recipe(
            "grouped_sum",
            "denormalized rows plus predicates plus group key and value field",
            "grouped sum rows",
            run_grouped_sum("cpu_python_reference")["rows"],
        ),
    ]
    return {
        "app": "feature_quickstart_cookbook",
        "backend": "cpu_python_reference",
        "feature_count": len(recipes),
        "recipes": recipes,
        "honesty_boundary": (
            "This cookbook uses the portable CPU Python reference path so every "
            "feature shape is easy to learn. Use feature docs and support "
            "matrices before making backend/performance claims."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one compact CPU Python reference recipe for each current RTDL feature."
    )
    parser.parse_args(argv)
    print(json.dumps(run_cookbook(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
