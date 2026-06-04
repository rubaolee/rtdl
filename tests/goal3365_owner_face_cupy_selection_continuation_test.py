from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3365_owner_face_cupy_selection_continuation_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3365OwnerFaceCupySelectionContinuationTest(unittest.TestCase):
    def test_contract_lists_cupy_selector_helper(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "select_owner_faces_from_incident_candidate_columns_with_priority_cupy",
            contract["optional_columnar_pipeline_helpers"],
        )

    def test_cupy_selector_matches_columnar_reference_with_status_codes(self):
        cp = _cupy_or_skip(self)
        expected = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1, 2),
            incident_face_ids=(10, 20, 30),
            incident_face_counts=(2, 2, 1),
            priority_point_ids=(1, 1, 2),
            priority_face_ids=(10, 20, 30),
            priorities=(5, 1, 0),
        )
        actual = rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
            incident_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            incident_face_ids=cp.asarray((10, 20, 30), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2, 1), dtype=cp.int64),
            priority_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            priority_face_ids=cp.asarray((10, 20, 30), dtype=cp.int64),
            priorities=cp.asarray((5, 1, 0), dtype=cp.int64),
        )

        codes = actual["selection_status_code_labels"]
        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(
            _host_tuple(actual["incident_face_count"]),
            expected["incident_face_count"],
        )
        self.assertEqual(_host_tuple(actual["candidate_count"]), expected["candidate_count"])
        self.assertEqual(
            _host_tuple(actual["selection_status_code"]),
            (
                codes["priority_tie_break"],
                codes["unique_max_incident_face"],
            ),
        )

    def test_cupy_selector_fails_closed_on_missing_priority_and_duplicates(self):
        cp = _cupy_or_skip(self)
        with self.assertRaisesRegex(ValueError, "missing owner-face priority"):
            rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
                incident_point_ids=cp.asarray((1, 1), dtype=cp.int64),
                incident_face_ids=cp.asarray((10, 20), dtype=cp.int64),
                incident_face_counts=cp.asarray((2, 2), dtype=cp.int64),
                priority_point_ids=cp.asarray((1,), dtype=cp.int64),
                priority_face_ids=cp.asarray((10,), dtype=cp.int64),
                priorities=cp.asarray((0,), dtype=cp.int64),
            )
        with self.assertRaisesRegex(ValueError, "incident point/face pairs must be unique"):
            rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
                incident_point_ids=cp.asarray((1, 1), dtype=cp.int64),
                incident_face_ids=cp.asarray((10, 10), dtype=cp.int64),
                incident_face_counts=cp.asarray((2, 2), dtype=cp.int64),
                priority_point_ids=cp.asarray((1,), dtype=cp.int64),
                priority_face_ids=cp.asarray((10,), dtype=cp.int64),
                priorities=cp.asarray((0,), dtype=cp.int64),
            )
        with self.assertRaisesRegex(ValueError, "priority point/face pairs must be unique"):
            rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
                incident_point_ids=cp.asarray((1,), dtype=cp.int64),
                incident_face_ids=cp.asarray((10,), dtype=cp.int64),
                incident_face_counts=cp.asarray((2,), dtype=cp.int64),
                priority_point_ids=cp.asarray((1, 1), dtype=cp.int64),
                priority_face_ids=cp.asarray((10, 10), dtype=cp.int64),
                priorities=cp.asarray((0, 1), dtype=cp.int64),
            )

    def test_cupy_selector_can_emit_ambiguous_priority_status(self):
        cp = _cupy_or_skip(self)
        actual = rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
            incident_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            incident_face_ids=cp.asarray((10, 20), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2), dtype=cp.int64),
            priority_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            priority_face_ids=cp.asarray((10, 20), dtype=cp.int64),
            priorities=cp.asarray((0, 0), dtype=cp.int64),
            ambiguity_policy="emit_ambiguous",
        )
        codes = actual["selection_status_code_labels"]

        self.assertEqual(_host_tuple(actual["point_id"]), (1,))
        self.assertEqual(_host_tuple(actual["owner_face_id"]), (-1,))
        self.assertEqual(_host_tuple(actual["candidate_count"]), (2,))
        self.assertEqual(
            _host_tuple(actual["selection_status_code"]),
            (codes["ambiguous_priority_tie"],),
        )

    def test_report_keeps_selector_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("CuPy device-column continuation", text)
        self.assertIn("numeric selection_status_code", text)
        self.assertIn("not native RT traversal", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Ran 26 tests in 1.230s", text)
        self.assertIn("Ran 85 tests in 0.687s", text)


if __name__ == "__main__":
    unittest.main()
