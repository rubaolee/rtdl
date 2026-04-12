import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from tests._embree_support import embree_available


@rt.kernel(backend="rtdl", precision="float_approx")
def knn_rows_3d_embree_goal300():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.knn_rows(k=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


@unittest.skipUnless(embree_available(), "Embree runtime is not available")
class Goal300V05Embree3DKnnTest(unittest.TestCase):
    def _case(self) -> dict[str, tuple[rt.Point3D, ...]]:
        return {
            "query_points": (
                rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=20, x=5.0, y=0.0, z=0.0),
            ),
            "search_points": (
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.6),
                rt.Point3D(id=3, x=0.0, y=0.8, z=0.0),
                rt.Point3D(id=4, x=5.0, y=0.0, z=0.9),
            ),
        }

    def test_run_embree_matches_python_reference_for_3d_knn_rows(self) -> None:
        case = self._case()
        embree_rows = rt.run_embree(knn_rows_3d_embree_goal300, **case)
        python_rows = rt.run_cpu_python_reference(knn_rows_3d_embree_goal300, **case)
        self.assertEqual(len(embree_rows), len(python_rows))
        for embree_row, python_row in zip(embree_rows, python_rows):
            self.assertEqual(embree_row["query_id"], python_row["query_id"])
            self.assertEqual(embree_row["neighbor_id"], python_row["neighbor_id"])
            self.assertEqual(embree_row["neighbor_rank"], python_row["neighbor_rank"])
            self.assertTrue(math.isclose(embree_row["distance"], python_row["distance"], rel_tol=1e-12, abs_tol=1e-12))

    def test_prepared_embree_matches_run_embree_for_3d_knn_rows(self) -> None:
        case = self._case()
        prepared = rt.prepare_embree(knn_rows_3d_embree_goal300)
        prepared_rows = prepared.run(**case)
        direct_rows = rt.run_embree(knn_rows_3d_embree_goal300, **case)
        self.assertEqual(prepared_rows, direct_rows)

    def test_run_embree_raw_mode_returns_expected_fields(self) -> None:
        rows = rt.run_embree(knn_rows_3d_embree_goal300, result_mode="raw", **self._case())
        try:
            self.assertEqual(rows.field_names, ("query_id", "neighbor_id", "distance", "neighbor_rank"))
            self.assertEqual(len(rows), len(rt.run_cpu_python_reference(knn_rows_3d_embree_goal300, **self._case())))
        finally:
            rows.close()

    def test_run_embree_orders_ties_by_neighbor_id(self) -> None:
        case = {
            "query_points": (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
            "search_points": (
                rt.Point3D(id=8, x=1.0, y=0.0, z=0.0),
                rt.Point3D(id=7, x=0.0, y=1.0, z=0.0),
                rt.Point3D(id=6, x=0.0, y=0.0, z=2.0),
            ),
        }
        self.assertEqual(
            rt.run_embree(knn_rows_3d_embree_goal300, **case),
            (
                {"query_id": 1, "neighbor_id": 7, "distance": 1.0, "neighbor_rank": 1},
                {"query_id": 1, "neighbor_id": 8, "distance": 1.0, "neighbor_rank": 2},
            ),
        )


if __name__ == "__main__":
    unittest.main()
