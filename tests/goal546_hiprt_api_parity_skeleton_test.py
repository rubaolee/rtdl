from __future__ import annotations

import unittest

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
def fixed_radius_2d_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.0, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="build")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def conjunctive_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


class Goal546HiprtApiParitySkeletonTest(unittest.TestCase):
    def assert_not_implemented_without_cpu_fallback(self, kernel) -> None:
        with self.assertRaisesRegex(NotImplementedError, "No CPU fallback is used"):
            rt.run_hiprt(kernel)

    def test_peer_2d_geometry_predicate_is_recognized_as_implemented_shape(self) -> None:
        try:
            self.assertEqual(rt.run_hiprt(overlay_kernel, left=(), right=()), ())
        except (FileNotFoundError, OSError, RuntimeError):
            pass

    def test_peer_2d_ray_triangle_shape_is_recognized_as_implemented_shape(self) -> None:
        try:
            self.assertEqual(rt.run_hiprt(ray_triangle_2d_kernel, rays=(), triangles=()), ())
        except (FileNotFoundError, OSError, RuntimeError):
            pass

    def test_peer_2d_nearest_neighbor_shape_is_recognized_as_implemented_shape(self) -> None:
        try:
            self.assertEqual(rt.run_hiprt(fixed_radius_2d_kernel, query_points=(), search_points=()), ())
        except (FileNotFoundError, OSError, RuntimeError):
            pass

    def test_peer_graph_predicate_is_recognized_as_implemented_shape(self) -> None:
        graph = rt.csr_graph(row_offsets=(0, 1, 1), column_indices=(1,))
        try:
            self.assertEqual(
                rt.run_hiprt(
                    bfs_kernel,
                    frontier=(rt.FrontierVertex(vertex_id=0, level=0),),
                    graph=graph,
                    visited=(),
                ),
                ({"src_vertex": 0, "dst_vertex": 1, "level": 1},),
            )
        except (FileNotFoundError, OSError, RuntimeError):
            pass

    def test_peer_db_predicate_is_recognized_as_implemented_shape(self) -> None:
        try:
            self.assertEqual(
                rt.run_hiprt(
                    conjunctive_scan_kernel,
                    predicates=(("discount", "eq", 6),),
                    table=({"row_id": 1, "discount": 6},),
                ),
                ({"row_id": 1},),
            )
        except (FileNotFoundError, OSError, RuntimeError):
            pass

    def test_prepare_hiprt_rejects_unimplemented_peer_predicate(self) -> None:
        with self.assertRaisesRegex(NotImplementedError, "fixed_radius_neighbors"):
            rt.prepare_hiprt(fixed_radius_3d_kernel)


if __name__ == "__main__":
    unittest.main()
