from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@rt.kernel(backend="rtdl", precision="float_approx")
def segment_intersection_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_polygon_kernel():
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
def ray_hitcount_kernel():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_closest_3d_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


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
def polygon_overlap_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.polygon_pair_overlap_area_rows(exact=False))
    return rt.emit(
        hits,
        fields=["left_polygon_id", "right_polygon_id", "intersection_area", "left_area", "right_area", "union_area"],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_jaccard_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.polygon_set_jaccard(exact=False))
    return rt.emit(hits, fields=["intersection_area", "left_area", "right_area", "union_area", "jaccard_similarity"])


@rt.kernel(backend="rtdl", precision="float_approx")
def point_nearest_segment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_kernel():
    queries = rt.input("queries", rt.Points, role="probe")
    points = rt.input("points", rt.Points, role="build")
    candidates = rt.traverse(queries, points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.1, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_kernel():
    queries = rt.input("queries", rt.Points, role="probe")
    points = rt.input("points", rt.Points, role="build")
    candidates = rt.traverse(queries, points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_kernel():
    queries = rt.input("queries", rt.Points, role="probe")
    points = rt.input("points", rt.Points, role="build")
    candidates = rt.traverse(queries, points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.5, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    hits = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(hits, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    hits = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(hits, fields=["u", "v", "w"])


@rt.kernel(backend="rtdl", precision="float_approx")
def db_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    hits = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(hits, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    hits = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(hits, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def grouped_sum_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    hits = rt.refine(candidates, predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"))
    return rt.emit(hits, fields=["region", "sum"])


def _square(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(id=polygon_id, vertices=((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def _assert_rows_almost_equal(testcase: unittest.TestCase, actual, expected) -> None:
    testcase.assertEqual(len(actual), len(expected))
    for actual_row, expected_row in zip(actual, expected):
        testcase.assertEqual(set(actual_row), set(expected_row))
        for key, expected_value in expected_row.items():
            actual_value = actual_row[key]
            if isinstance(expected_value, float):
                testcase.assertAlmostEqual(float(actual_value), expected_value, places=5)
            else:
                testcase.assertEqual(actual_value, expected_value)


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal582AppleRtFullSurfaceDispatchTest(unittest.TestCase):
    def test_support_matrix_marks_native_and_compatibility_modes(self) -> None:
        self.assertIn("apple_rt_predicate_mode", rt.__all__)
        self.assertIn("apple_rt_support_matrix", rt.__all__)
        self.assertIn("segment_intersection_apple_rt", rt.__all__)
        modes = {row["predicate"]: row["mode"] for row in rt.apple_rt_support_matrix()}
        self.assertEqual(modes["ray_triangle_closest_hit"], "native_mps_rt")
        self.assertEqual(modes["ray_triangle_hit_count"], "native_mps_rt_2d_3d")
        self.assertEqual(modes["segment_intersection"], "native_mps_rt")
        self.assertEqual(modes["conjunctive_scan"], "native_metal_compute")
        self.assertEqual(modes["grouped_count"], "native_metal_filter_cpu_aggregate")
        self.assertEqual(modes["grouped_sum"], "native_metal_filter_cpu_aggregate")
        self.assertEqual(modes["bfs_discover"], "cpu_reference_compat")
        self.assertEqual(len(modes), 18)

    def test_segment_intersection_native_matches_cpu_reference(self) -> None:
        inputs = {
            "left": (
                rt.Segment(1, 0.0, 0.0, 2.0, 2.0),
                rt.Segment(2, 0.0, 3.0, 2.0, 3.0),
                rt.Segment(3, -1.0, 1.0, 3.0, 1.0),
            ),
            "right": (
                rt.Segment(10, 0.0, 2.0, 2.0, 0.0),
                rt.Segment(12, 1.0, -1.0, 1.0, 3.0),
                rt.Segment(11, 3.0, 0.0, 3.0, 2.0),
            ),
        }
        actual = rt.run_apple_rt(segment_intersection_kernel, native_only=True, **inputs)
        expected = rt.run_cpu_python_reference(segment_intersection_kernel, **inputs)
        _assert_rows_almost_equal(self, actual, expected)
        direct = tuple(rt.segment_intersection_apple_rt(inputs["left"], inputs["right"]))
        _assert_rows_almost_equal(self, direct, expected)

    def test_all_current_predicates_are_callable_through_run_apple_rt(self) -> None:
        square = _square(1, 0.0, 0.0, 2.0, 2.0)
        shifted_square = _square(2, 1.0, 1.0, 3.0, 3.0)
        table = (
            {"row_id": 1, "region": "east", "ship_date": 10, "quantity": 12, "discount": 5, "revenue": 5},
            {"row_id": 2, "region": "west", "ship_date": 11, "quantity": 30, "discount": 8, "revenue": 8},
            {"row_id": 3, "region": "east", "ship_date": 12, "quantity": 18, "discount": 6, "revenue": 6},
            {"row_id": 4, "region": "west", "ship_date": 13, "quantity": 10, "discount": 6, "revenue": 10},
        )
        cases = (
            (
                segment_intersection_kernel,
                {"left": (rt.Segment(1, 0.0, 0.0, 2.0, 2.0),), "right": (rt.Segment(2, 0.0, 2.0, 2.0, 0.0),)},
            ),
            (point_in_polygon_kernel, {"points": (rt.Point(1, 0.5, 0.5), rt.Point(2, 3.0, 3.0)), "polygons": (square,)}),
            (overlay_kernel, {"left": (square,), "right": (shifted_square,)}),
            (
                ray_hitcount_kernel,
                {
                    "rays": (rt.Ray2D(1, -1.0, 0.5, 1.0, 0.0, 3.0),),
                    "triangles": (rt.Triangle(2, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0),),
                },
            ),
            (
                ray_closest_3d_kernel,
                {
                    "rays": (rt.Ray3D(1, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 3.0),),
                    "triangles": (rt.Triangle3D(2, 0.5, -1.0, -1.0, 0.5, 1.0, 0.0, 0.5, -1.0, 1.0),),
                },
            ),
            (segment_polygon_hitcount_kernel, {"segments": (rt.Segment(1, -1.0, 1.0, 3.0, 1.0),), "polygons": (square,)}),
            (segment_polygon_anyhit_kernel, {"segments": (rt.Segment(1, -1.0, 1.0, 3.0, 1.0),), "polygons": (square,)}),
            (polygon_overlap_kernel, {"left": (square,), "right": (shifted_square,)}),
            (polygon_jaccard_kernel, {"left": (square,), "right": (shifted_square,)}),
            (point_nearest_segment_kernel, {"points": (rt.Point(1, 0.5, 1.0),), "segments": (rt.Segment(2, 0.0, 0.0, 2.0, 0.0),)}),
            (fixed_radius_kernel, {"queries": (rt.Point(1, 0.0, 0.0),), "points": (rt.Point(2, 0.5, 0.0), rt.Point(3, 2.0, 0.0))}),
            (knn_kernel, {"queries": (rt.Point(1, 0.0, 0.0),), "points": (rt.Point(2, 0.5, 0.0), rt.Point(3, 2.0, 0.0))}),
            (bounded_knn_kernel, {"queries": (rt.Point(1, 0.0, 0.0),), "points": (rt.Point(2, 0.5, 0.0), rt.Point(3, 2.0, 0.0))}),
            (
                bfs_kernel,
                {
                    "frontier": (rt.FrontierVertex(vertex_id=0, level=0),),
                    "graph": rt.csr_graph(row_offsets=(0, 2, 3, 3), column_indices=(1, 2, 2)),
                    "visited": (0,),
                },
            ),
            (
                triangle_match_kernel,
                {
                    "seeds": ((0, 1),),
                    "graph": rt.csr_graph(row_offsets=(0, 2, 4, 6), column_indices=(1, 2, 0, 2, 0, 1)),
                },
            ),
            (db_scan_kernel, {"predicates": (("ship_date", "between", 11, 13), ("discount", "eq", 6)), "table": table}),
            (
                grouped_count_kernel,
                {"query": {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",)}, "table": table},
            ),
            (
                grouped_sum_kernel,
                {
                    "query": {"predicates": (("ship_date", "ge", 11),), "group_keys": ("region",), "value_field": "revenue"},
                    "table": table,
                },
            ),
        )
        self.assertEqual(len(cases), 18)
        for kernel, inputs in cases:
            with self.subTest(kernel=kernel.__name__):
                actual = rt.run_apple_rt(kernel, **inputs)
                expected = rt.run_cpu_python_reference(kernel, **inputs)
                _assert_rows_almost_equal(self, actual, expected)

    def test_native_only_rejects_compatibility_paths(self) -> None:
        with self.assertRaises(NotImplementedError):
            rt.run_apple_rt(
                bfs_kernel,
                native_only=True,
                frontier=(rt.FrontierVertex(vertex_id=0, level=0),),
                graph=rt.csr_graph(row_offsets=(0, 1, 1), column_indices=(1,)),
                visited=(0,),
            )


if __name__ == "__main__":
    unittest.main()
