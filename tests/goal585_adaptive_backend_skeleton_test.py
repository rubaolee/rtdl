from __future__ import annotations

import unittest

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_intersection_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    hits = rt.refine(rt.traverse(left, right, accel="bvh"), predicate=rt.segment_intersection())
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygon_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    hits = rt.refine(rt.traverse(points, polygons, accel="bvh"), predicate=rt.point_in_polygon())
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def overlay_compose_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    hits = rt.refine(rt.traverse(left, right, accel="bvh"), predicate=rt.overlay_compose())
    return rt.emit(hits, fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hitcount_2d_kernel():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    hits = rt.refine(rt.traverse(rays, triangles, accel="bvh"), predicate=rt.ray_triangle_hit_count())
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hitcount_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, role="build")
    hits = rt.refine(rt.traverse(rays, triangles, accel="bvh"), predicate=rt.ray_triangle_hit_count())
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_hitcount_kernel():
    segments = rt.input("segments", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    hits = rt.refine(rt.traverse(segments, polygons, accel="bvh"), predicate=rt.segment_polygon_hitcount())
    return rt.emit(hits, fields=["segment_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_polygon_anyhit_kernel():
    segments = rt.input("segments", rt.Segments, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    hits = rt.refine(rt.traverse(segments, polygons, accel="bvh"), predicate=rt.segment_polygon_anyhit_rows())
    return rt.emit(hits, fields=["segment_id", "polygon_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    hits = rt.refine(rt.traverse(points, segments, accel="bvh"), predicate=rt.point_nearest_segment())
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_2d_kernel():
    queries = rt.input("queries", rt.Points, role="probe")
    points = rt.input("points", rt.Points, role="build")
    hits = rt.refine(rt.traverse(queries, points, accel="bvh"), predicate=rt.fixed_radius_neighbors(radius=1.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_3d_kernel():
    queries = rt.input("queries", rt.Points3D, role="probe")
    points = rt.input("points", rt.Points3D, role="build")
    hits = rt.refine(rt.traverse(queries, points, accel="bvh"), predicate=rt.fixed_radius_neighbors(radius=1.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_3d_kernel():
    queries = rt.input("queries", rt.Points3D, role="probe")
    points = rt.input("points", rt.Points3D, role="build")
    hits = rt.refine(rt.traverse(queries, points, accel="bvh"), predicate=rt.bounded_knn_rows(radius=3.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_2d_kernel():
    queries = rt.input("queries", rt.Points, role="probe")
    points = rt.input("points", rt.Points, role="build")
    hits = rt.refine(rt.traverse(queries, points, accel="bvh"), predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_3d_kernel():
    queries = rt.input("queries", rt.Points3D, role="probe")
    points = rt.input("points", rt.Points3D, role="build")
    hits = rt.refine(rt.traverse(queries, points, accel="bvh"), predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    hits = rt.refine(
        rt.traverse(frontier, graph, accel="bvh", mode="graph_expand"),
        predicate=rt.bfs_discover(visited=visited, dedupe=True),
    )
    return rt.emit(hits, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    hits = rt.refine(
        rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect"),
        predicate=rt.triangle_match(order="id_ascending", unique=True),
    )
    return rt.emit(hits, fields=["u", "v", "w"])


@rt.kernel(backend="rtdl", precision="float_approx")
def db_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    hits = rt.refine(
        rt.traverse(predicates, table, accel="bvh", mode="db_scan"),
        predicate=rt.conjunctive_scan(),
    )
    return rt.emit(hits, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    hits = rt.refine(
        rt.traverse(query, table, accel="bvh", mode="db_group"),
        predicate=rt.grouped_count(group_keys=("region",)),
    )
    return rt.emit(hits, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    hits = rt.refine(
        rt.traverse(query, table, accel="bvh", mode="db_group"),
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(hits, fields=["region", "sum"])


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(polygon_id, ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


class Goal585AdaptiveBackendSkeletonTest(unittest.TestCase):
    def test_support_matrix_is_explicit_18_workload_compatibility_surface(self) -> None:
        matrix = rt.adaptive_support_matrix()
        workloads = {row["workload"] for row in matrix}

        self.assertEqual(len(matrix), 18)
        self.assertEqual(
            workloads,
            {
                "segment_intersection",
                "point_in_polygon",
                "overlay_compose",
                "ray_triangle_hit_count_2d",
                "ray_triangle_hit_count_3d",
                "segment_polygon_hitcount",
                "segment_polygon_anyhit_rows",
                "point_nearest_segment",
                "fixed_radius_neighbors_2d",
                "fixed_radius_neighbors_3d",
                "bounded_knn_rows_3d",
                "knn_rows_2d",
                "knn_rows_3d",
                "bfs_discover",
                "triangle_match",
                "conjunctive_scan",
                "grouped_count",
                "grouped_sum",
            },
        )
        by_workload = {row["workload"]: row for row in matrix}
        if rt.adaptive_available():
            self.assertEqual(by_workload["segment_intersection"]["mode"], "native_adaptive_cpu_soa_2d")
            self.assertTrue(by_workload["segment_intersection"]["native"])
            self.assertEqual(
                by_workload["point_nearest_segment"]["mode"],
                "native_adaptive_cpu_soa_min_distance_2d",
            )
            self.assertTrue(by_workload["point_nearest_segment"]["native"])
            self.assertEqual(by_workload["ray_triangle_hit_count_3d"]["mode"], "native_adaptive_cpu_soa_3d")
            self.assertTrue(by_workload["ray_triangle_hit_count_3d"]["native"])
        else:
            self.assertTrue(all(row["mode"] == "cpu_reference_compat" for row in matrix))
            self.assertTrue(all(row["native"] is False for row in matrix))

    def test_all_18_workloads_route_to_reference_with_visible_modes(self) -> None:
        square = _square(1, 0.0, 0.0, 2.0, 2.0)
        shifted = _square(2, 1.0, 1.0, 3.0, 3.0)
        table = (
            {"row_id": 1, "region": "east", "quantity": 10, "revenue": 7},
            {"row_id": 2, "region": "west", "quantity": 25, "revenue": 11},
            {"row_id": 3, "region": "east", "quantity": 15, "revenue": 13},
        )
        graph = {"row_offsets": (0, 2, 4, 6), "column_indices": (1, 2, 0, 2, 0, 1), "vertex_count": 3}
        point2d = (rt.Point(1, 0.0, 0.0), rt.Point(2, 1.0, 0.0), rt.Point(3, 3.0, 0.0))
        point3d = (rt.Point3D(1, 0.0, 0.0, 0.0), rt.Point3D(2, 1.0, 0.0, 0.0), rt.Point3D(3, 3.0, 0.0, 0.0))

        cases = (
            (segment_intersection_kernel, {"left": (rt.Segment(1, 0.0, 0.0, 2.0, 2.0),), "right": (rt.Segment(2, 0.0, 2.0, 2.0, 0.0),)}, "segment_intersection"),
            (point_in_polygon_kernel, {"points": (rt.Point(1, 0.5, 0.5), rt.Point(2, 3.0, 3.0)), "polygons": (square,)}, "point_in_polygon"),
            (overlay_compose_kernel, {"left": (square,), "right": (shifted,)}, "overlay_compose"),
            (ray_hitcount_2d_kernel, {"rays": (rt.Ray2D(1, -1.0, 0.5, 1.0, 0.0, 3.0),), "triangles": (rt.Triangle(2, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0),)}, "ray_triangle_hit_count_2d"),
            (ray_hitcount_3d_kernel, {"rays": (rt.Ray3D(1, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 3.0),), "triangles": (rt.Triangle3D(2, 0.5, -1.0, -1.0, 0.5, 1.0, 0.0, 0.5, -1.0, 1.0),)}, "ray_triangle_hit_count_3d"),
            (segment_polygon_hitcount_kernel, {"segments": (rt.Segment(1, -1.0, 1.0, 3.0, 1.0),), "polygons": (square,)}, "segment_polygon_hitcount"),
            (segment_polygon_anyhit_kernel, {"segments": (rt.Segment(1, -1.0, 1.0, 3.0, 1.0),), "polygons": (square,)}, "segment_polygon_anyhit_rows"),
            (point_nearest_segment_kernel, {"points": (rt.Point(1, 0.5, 0.2),), "segments": (rt.Segment(2, 0.0, 0.0, 1.0, 0.0),)}, "point_nearest_segment"),
            (fixed_radius_2d_kernel, {"queries": (rt.Point(10, 0.0, 0.0),), "points": point2d}, "fixed_radius_neighbors_2d"),
            (fixed_radius_3d_kernel, {"queries": (rt.Point3D(10, 0.0, 0.0, 0.0),), "points": point3d}, "fixed_radius_neighbors_3d"),
            (bounded_knn_3d_kernel, {"queries": (rt.Point3D(10, 0.0, 0.0, 0.0),), "points": point3d}, "bounded_knn_rows_3d"),
            (knn_2d_kernel, {"queries": (rt.Point(10, 0.0, 0.0),), "points": point2d}, "knn_rows_2d"),
            (knn_3d_kernel, {"queries": (rt.Point3D(10, 0.0, 0.0, 0.0),), "points": point3d}, "knn_rows_3d"),
            (bfs_kernel, {"frontier": ({"vertex_id": 0, "level": 1},), "graph": graph, "visited": ({"vertex_id": 0},)}, "bfs_discover"),
            (triangle_match_kernel, {"seeds": ((0, 1),), "graph": graph}, "triangle_match"),
            (db_scan_kernel, {"predicates": (("quantity", "lt", 20),), "table": table}, "conjunctive_scan"),
            (grouped_count_kernel, {"query": {"predicates": (("quantity", "lt", 20),), "group_keys": ("region",)}, "table": table}, "grouped_count"),
            (grouped_sum_kernel, {"query": {"predicates": (("quantity", "lt", 20),), "group_keys": ("region",), "value_field": "revenue"}, "table": table}, "grouped_sum"),
        )

        for kernel, inputs, workload in cases:
            with self.subTest(workload=workload):
                mode = rt.adaptive_predicate_mode(kernel)
                self.assertEqual(mode["workload"], workload)
                if workload in {
                    "segment_intersection",
                    "point_nearest_segment",
                    "ray_triangle_hit_count_3d",
                } and rt.adaptive_available():
                    expected_mode = {
                        "segment_intersection": "native_adaptive_cpu_soa_2d",
                        "point_nearest_segment": "native_adaptive_cpu_soa_min_distance_2d",
                        "ray_triangle_hit_count_3d": "native_adaptive_cpu_soa_3d",
                    }[workload]
                    self.assertEqual(mode["mode"], expected_mode)
                    self.assertTrue(mode["native"])
                else:
                    self.assertEqual(mode["mode"], "cpu_reference_compat")
                    self.assertFalse(mode["native"])
                self.assertEqual(rt.run_adaptive(kernel, **inputs), rt.run_cpu_python_reference(kernel, **inputs))
                self.assertEqual(rt.prepare_adaptive(kernel, **inputs).run(), rt.run_cpu_python_reference(kernel, **inputs))


if __name__ == "__main__":
    unittest.main()
