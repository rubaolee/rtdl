from __future__ import annotations

import unittest

import rtdsl as rt
from rtdsl.reference import Segment


@rt.kernel(backend="rtdl", precision="float_approx")
def _segment_intersection_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.primitives.intersections(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


class Goal2326ExecutionReportContractTest(unittest.TestCase):
    def test_run_returns_rows_and_explainable_report(self) -> None:
        result = rt.run(
            _segment_intersection_kernel,
            inputs={
                "left": (Segment(id=1, x0=0.0, y0=0.0, x1=1.0, y1=1.0),),
                "right": (Segment(id=2, x0=0.0, y0=1.0, x1=1.0, y1=0.0),),
            },
            execution=rt.ExecutionPolicy(
                backend="cpu_python_reference",
                partner="numpy",
                explain=True,
            ),
        )

        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0]["left_id"], 1)
        self.assertEqual(result.rows[0]["right_id"], 2)
        report = result.execution_report
        self.assertEqual(report.requested_backend, "cpu_python_reference")
        self.assertEqual(report.selected_backend, "cpu_python_reference")
        self.assertEqual(report.requested_partner, "numpy")
        self.assertEqual(report.primitive_family, "spatial_relation")
        self.assertEqual(report.predicate, "segment_intersection")
        self.assertEqual(
            report.output_schema,
            ("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
        )
        self.assertEqual(report.memory_status, "not_reported_by_runtime")
        self.assertEqual(report.copy_status, "not_reported_by_runtime")
        self.assertFalse(report.claim_boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(report.claim_boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(report.claim_boundary["zero_copy_claim_authorized"])
        self.assertIn("git_commit", report.reproducibility)

    def test_auto_policy_is_explainable_and_conservative(self) -> None:
        result = rt.run(
            _segment_intersection_kernel,
            inputs={
                "left": (Segment(id=1, x0=0.0, y0=0.0, x1=1.0, y1=1.0),),
                "right": (Segment(id=2, x0=0.0, y0=1.0, x1=1.0, y1=0.0),),
            },
            execution=rt.ExecutionPolicy(backend="auto", explain=True),
        )
        self.assertEqual(result.execution_report.requested_backend, "auto")
        self.assertEqual(result.execution_report.selected_backend, "cpu_python_reference")
        self.assertEqual(result.execution_report.fallback_backend, None)


if __name__ == "__main__":
    unittest.main()
