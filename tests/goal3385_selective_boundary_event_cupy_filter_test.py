from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3385_selective_boundary_event_cupy_filter_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(cp_module, array):
    return tuple(int(value) for value in cp_module.asnumpy(array).tolist())


class Goal3385SelectiveBoundaryEventCupyFilterTest(unittest.TestCase):
    def test_selected_candidates_filter_through_zero_boundary_events(self):
        cp = _cupy_or_skip(self)
        actual = rt.run_selective_closed_shape_boundary_event_membership_pipeline_cupy(
            candidate_point_ids=cp.asarray((1, 1, 1, 2, 2), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((10, 20, 30, 40, 50), dtype=cp.int64),
            boundary_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            boundary_shape_ids=cp.asarray((10, 30, 40), dtype=cp.int64),
            boundary_crossing_t=cp.asarray((0.0, 0.25, 0.0), dtype=cp.float64),
            selected_point_ids=cp.asarray((1,), dtype=cp.int64),
        )

        self.assertEqual(_host_tuple(cp, actual["point_id"]), (1, 2, 2))
        self.assertEqual(_host_tuple(cp, actual["shape_id"]), (10, 40, 50))
        self.assertEqual(_host_tuple(cp, actual["membership"]), (1, 1, 1))
        self.assertEqual(_host_tuple(cp, actual["boundary_event_filter_status"]), (1, 0, 0))
        self.assertEqual(actual["selected_candidate_row_count"], 3)
        self.assertEqual(actual["passthrough_candidate_row_count"], 2)
        self.assertEqual(actual["selected_kept_row_count"], 1)
        self.assertEqual(actual["selected_dropped_row_count"], 2)
        self.assertEqual(actual["selected_point_filter_mode"], "caller_supplied_ambiguity_set")
        self.assertEqual(actual["boundary_event_filter"], "candidate_pair_has_zero_crossing_t")

    def test_crossing_tolerance_is_explicit(self):
        cp = _cupy_or_skip(self)
        actual = rt.run_selective_closed_shape_boundary_event_membership_pipeline_cupy(
            candidate_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((10, 20), dtype=cp.int64),
            boundary_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            boundary_shape_ids=cp.asarray((10, 20), dtype=cp.int64),
            boundary_crossing_t=cp.asarray((0.0, 0.001), dtype=cp.float64),
            selected_point_ids=cp.asarray((1,), dtype=cp.int64),
            crossing_tolerance=0.01,
        )

        self.assertEqual(_host_tuple(cp, actual["shape_id"]), (10, 20))
        self.assertEqual(actual["selected_kept_row_count"], 2)
        self.assertEqual(actual["crossing_tolerance"], 0.01)

    def test_contract_and_report_keep_helper_non_default(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "run_selective_closed_shape_boundary_event_membership_pipeline_cupy",
            contract["optional_columnar_pipeline_helpers"],
        )
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not infer which points are ambiguous", text)
        self.assertIn("does not authorize a native default route", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
