import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference


class DslNegativeTest(unittest.TestCase):
    def test_input_rejects_duplicate_name(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def bad_kernel():
            rt.input("left", rt.Segments, role="probe")
            rt.input("left", rt.Segments, role="build")
            candidates = rt.traverse(rt.input("other", rt.Segments, role="probe"), rt.input("more", rt.Segments, role="build"), accel="bvh")
            return rt.emit(rt.refine(candidates, predicate=rt.segment_intersection(exact=False)), fields=["left_id"])

        with self.assertRaisesRegex(ValueError, "duplicate input name"):
            rt.compile_kernel(bad_kernel)

    def test_input_rejects_invalid_role(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def bad_role():
            left = rt.input("left", rt.Segments, role="invalid")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            return rt.emit(rt.refine(candidates, predicate=rt.segment_intersection(exact=False)), fields=["left_id"])

        with self.assertRaisesRegex(ValueError, "input role must be one of"):
            rt.compile_kernel(bad_role)

    def test_kernel_must_return_emit(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def bad_return():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            return rt.traverse(left, right, accel="bvh")

        with self.assertRaisesRegex(TypeError, "kernel function must return rt.emit"):
            rt.compile_kernel(bad_return)

    def test_run_cpu_rejects_unexpected_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "unexpected RTDL simulator inputs"):
            rt.run_cpu(county_zip_join_reference, left=(), right=(), extra=())

    def test_run_cpu_rejects_invalid_polygon_vertices(self) -> None:
        from examples.rtdl_language_reference import point_in_counties_reference

        with self.assertRaisesRegex(ValueError, "requires at least 3 vertices"):
            rt.run_cpu(
                point_in_counties_reference,
                points=({"id": 1, "x": 0.0, "y": 0.0},),
                polygons=({"id": 10, "vertices": ((0.0, 0.0), (1.0, 0.0))},),
            )

    def test_run_baseline_case_rejects_invalid_backend(self) -> None:
        with self.assertRaisesRegex(ValueError, "baseline backend must be one of"):
            rt.run_baseline_case(county_zip_join_reference, "authored_lsi_minimal", backend="bogus")


if __name__ == "__main__":
    unittest.main()
