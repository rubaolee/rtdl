import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_polygon_pair_overlap_area_rows import make_authored_polygon_pair_overlap_case
from examples.rtdl_polygon_pair_overlap_area_rows import polygon_pair_overlap_area_rows_reference


class Goal138PolygonPairOverlapAreaRowsTest(unittest.TestCase):
    def test_reference_kernel_lowers_to_expected_workload(self) -> None:
        compiled = rt.compile_kernel(polygon_pair_overlap_area_rows_reference)
        plan = rt.lower_to_execution_plan(compiled)
        self.assertEqual(plan.workload_kind, "polygon_pair_overlap_area_rows")
        self.assertEqual(
            plan.emit_fields,
            (
                "left_polygon_id",
                "right_polygon_id",
                "intersection_area",
                "left_area",
                "right_area",
                "union_area",
            ),
        )

    def test_cpu_python_reference_authored_rows(self) -> None:
        rows = rt.run_cpu_python_reference(
            polygon_pair_overlap_area_rows_reference,
            **make_authored_polygon_pair_overlap_case(),
        )
        self.assertEqual(
            rows,
            (
                {
                    "left_polygon_id": 1,
                    "right_polygon_id": 10,
                    "intersection_area": 4,
                    "left_area": 9,
                    "right_area": 9,
                    "union_area": 14,
                },
                {
                    "left_polygon_id": 2,
                    "right_polygon_id": 11,
                    "intersection_area": 1,
                    "left_area": 4,
                    "right_area": 2,
                    "union_area": 5,
                },
            ),
        )

    def test_cpu_oracle_matches_python_when_available(self) -> None:
        try:
            rt.oracle_version()
        except Exception as exc:  # pragma: no cover - platform-specific oracle availability
            self.skipTest(f"native oracle unavailable: {exc}")
        python_rows = rt.run_cpu_python_reference(
            polygon_pair_overlap_area_rows_reference,
            **make_authored_polygon_pair_overlap_case(),
        )
        cpu_rows = rt.run_cpu(
            polygon_pair_overlap_area_rows_reference,
            **make_authored_polygon_pair_overlap_case(),
        )
        self.assertEqual(cpu_rows, python_rows)

    def test_rejects_diagonal_or_non_integer_polygon(self) -> None:
        bad_case = {
            "left": (
                rt.Polygon(id=1, vertices=((0.0, 0.0), (2.5, 0.0), (2.5, 2.0), (0.0, 2.0))),
            ),
            "right": (
                rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
            ),
        }
        with self.assertRaisesRegex(ValueError, "integer-grid polygon vertices|orthogonal integer-grid polygons"):
            rt.run_cpu_python_reference(polygon_pair_overlap_area_rows_reference, **bad_case)


if __name__ == "__main__":
    unittest.main()
