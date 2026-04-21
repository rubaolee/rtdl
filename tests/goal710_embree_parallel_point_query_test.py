import os
import unittest

import rtdsl as rt
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from tests._embree_support import embree_available


@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_3d_goal710():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.25, k_max=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_3d_goal710():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=4))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@unittest.skipUnless(embree_available(), "Embree runtime is not available")
class Goal710EmbreeParallelPointQueryTest(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("RTDL_EMBREE_THREADS", None)
        rt.configure_embree(threads=None)

    def _case_2d(self):
        return {
            "query_points": tuple(
                rt.Point(id=100 + index, x=(index % 4) * 0.75, y=(index // 4) * 0.5)
                for index in range(12)
            ),
            "search_points": tuple(
                rt.Point(id=200 + index, x=(index % 5) * 0.45, y=(index // 5) * 0.4)
                for index in range(25)
            ),
        }

    def _case_3d(self):
        return {
            "query_points": tuple(
                rt.Point3D(
                    id=300 + index,
                    x=(index % 4) * 0.7,
                    y=((index // 4) % 3) * 0.45,
                    z=(index // 12) * 0.35,
                )
                for index in range(18)
            ),
            "search_points": tuple(
                rt.Point3D(
                    id=400 + index,
                    x=(index % 5) * 0.42,
                    y=((index // 5) % 4) * 0.38,
                    z=(index // 20) * 0.31,
                )
                for index in range(40)
            ),
        }

    def _single_vs_parallel(self, kernel, case):
        rt.configure_embree(threads=1)
        single_thread_rows = rt.run_embree(kernel, **case)
        rt.configure_embree(threads=4)
        parallel_rows = rt.run_embree(kernel, **case)
        self.assertEqual(parallel_rows, single_thread_rows)

    def test_fixed_radius_2d_preserves_rows_across_thread_counts(self):
        self._single_vs_parallel(fixed_radius_neighbors_reference, self._case_2d())

    def test_knn_2d_preserves_rows_across_thread_counts(self):
        self._single_vs_parallel(knn_rows_reference, self._case_2d())

    def test_fixed_radius_3d_preserves_rows_across_thread_counts(self):
        self._single_vs_parallel(fixed_radius_neighbors_3d_goal710, self._case_3d())

    def test_knn_3d_preserves_rows_across_thread_counts(self):
        self._single_vs_parallel(knn_rows_3d_goal710, self._case_3d())


if __name__ == "__main__":
    unittest.main()

