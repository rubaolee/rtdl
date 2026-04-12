import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def bounded_knn_rows_reference():
    query_points = rt.input("query_points", rt.Points3D, role="probe")
    search_points = rt.input("search_points", rt.Points3D, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.bounded_knn_rows(radius=1.0, k_max=2))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])


class Goal263V05BoundedKnnRowsSurfaceTest(unittest.TestCase):
    def test_api_validates_bounded_knn_rows(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded_knn_rows radius must be non-negative"):
            rt.bounded_knn_rows(radius=-1.0, k_max=1)
        with self.assertRaisesRegex(ValueError, "bounded_knn_rows k_max must be positive"):
            rt.bounded_knn_rows(radius=1.0, k_max=0)

    def test_reference_cpu_rows_are_radius_bounded_and_ranked(self) -> None:
        rows = rt.bounded_knn_rows_cpu(
            (rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            (
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.4),
                rt.Point3D(id=3, x=0.0, y=0.0, z=0.8),
            ),
            radius=0.5,
            k_max=3,
        )
        self.assertEqual(
            rows,
            (
                {"query_id": 10, "neighbor_id": 1, "distance": 0.0, "neighbor_rank": 1},
                {"query_id": 10, "neighbor_id": 2, "distance": 0.4, "neighbor_rank": 2},
            ),
        )

    def test_cpu_python_reference_runs_bounded_knn_rows_kernel(self) -> None:
        rows = rt.run_cpu_python_reference(
            bounded_knn_rows_reference,
            query_points=(rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),),
            search_points=(
                rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=2, x=0.0, y=0.0, z=0.25),
                rt.Point3D(id=3, x=0.0, y=0.0, z=2.0),
            ),
        )
        self.assertEqual(tuple(row["neighbor_id"] for row in rows), (1, 2))
        self.assertEqual(tuple(row["neighbor_rank"] for row in rows), (1, 2))

    def test_lowering_emits_distinct_workload_kind(self) -> None:
        compiled = rt.compile_kernel(bounded_knn_rows_reference)
        plan = rt.lower_to_execution_plan(compiled)
        self.assertEqual(plan.workload_kind, "bounded_knn_rows")
        self.assertEqual(plan.predicate, "bounded_knn_rows")
        self.assertIn("neighbor_rank", plan.emit_fields)

    def test_knn_rows_surface_remains_stable(self) -> None:
        predicate = rt.knn_rows(k=3)
        self.assertEqual(predicate.name, "knn_rows")
        self.assertEqual(predicate.options, {"k": 3})


if __name__ == "__main__":
    unittest.main()
