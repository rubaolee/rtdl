import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_polygon_set_jaccard import make_authored_polygon_set_jaccard_case
from examples.rtdl_polygon_set_jaccard import polygon_set_jaccard_reference


class Goal140PolygonSetJaccardTest(unittest.TestCase):
    def test_reference_kernel_lowers_to_expected_workload(self) -> None:
        compiled = rt.compile_kernel(polygon_set_jaccard_reference)
        plan = rt.lower_to_execution_plan(compiled)
        self.assertEqual(plan.workload_kind, "polygon_set_jaccard")

    def test_cpu_python_reference_authored_row(self) -> None:
        rows = rt.run_cpu_python_reference(
            polygon_set_jaccard_reference,
            **make_authored_polygon_set_jaccard_case(),
        )
        self.assertEqual(
            rows,
            (
                {
                    "intersection_area": 5,
                    "left_area": 13,
                    "right_area": 11,
                    "union_area": 19,
                    "jaccard_similarity": 5.0 / 19.0,
                },
            ),
        )

    def test_cpu_oracle_matches_python_when_available(self) -> None:
        try:
            rt.oracle_version()
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"native oracle unavailable: {exc}")
        python_rows = rt.run_cpu_python_reference(
            polygon_set_jaccard_reference,
            **make_authored_polygon_set_jaccard_case(),
        )
        cpu_rows = rt.run_cpu(
            polygon_set_jaccard_reference,
            **make_authored_polygon_set_jaccard_case(),
        )
        self.assertEqual(cpu_rows, python_rows)

    def test_empty_sets_emit_zero_row(self) -> None:
        rows = rt.run_cpu_python_reference(
            polygon_set_jaccard_reference,
            left=(),
            right=(),
        )
        self.assertEqual(
            rows,
            (
                {
                    "intersection_area": 0,
                    "left_area": 0,
                    "right_area": 0,
                    "union_area": 0,
                    "jaccard_similarity": 0.0,
                },
            ),
        )

    def test_non_orthogonal_polygon_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rt.run_cpu_python_reference(
                polygon_set_jaccard_reference,
                left=(
                    rt.Polygon(
                        id=1,
                        vertices=((0.0, 0.0), (2.0, 0.0), (1.0, 1.0)),
                    ),
                ),
                right=(),
            )


if __name__ == "__main__":
    unittest.main()
