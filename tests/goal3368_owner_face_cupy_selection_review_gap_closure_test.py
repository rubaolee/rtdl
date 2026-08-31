from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3368_owner_face_cupy_selection_review_gap_closure_2026-06-04.md"
REVIEW = ROOT / "docs" / "reviews" / "goal3366_claude_review_owner_face_cupy_selection_continuation_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3368OwnerFaceCupySelectionReviewGapClosureTest(unittest.TestCase):
    def test_contract_documents_status_code_translation(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        requirements = contract["promotion_requirements"]

        self.assertTrue(any("selection_status_code" in item for item in requirements))

    def test_cupy_selector_drop_policy_matches_python_reference(self):
        cp = _cupy_or_skip(self)
        expected = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1, 2),
            incident_face_ids=(10, 20, 30),
            incident_face_counts=(2, 2, 1),
            priority_point_ids=(),
            priority_face_ids=(),
            priorities=(),
            ambiguity_policy="drop",
        )
        actual = rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
            incident_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            incident_face_ids=cp.asarray((10, 20, 30), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2, 1), dtype=cp.int64),
            priority_point_ids=cp.asarray((), dtype=cp.int64),
            priority_face_ids=cp.asarray((), dtype=cp.int64),
            priorities=cp.asarray((), dtype=cp.int64),
            ambiguity_policy="drop",
        )
        codes = actual["selection_status_code_labels"]

        self.assertEqual(expected["point_id"], (2,))
        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(_host_tuple(actual["candidate_count"]), expected["candidate_count"])
        self.assertEqual(
            _host_tuple(actual["selection_status_code"]),
            (codes["unique_max_incident_face"],),
        )

    def test_cupy_selector_emit_missing_priority_matches_python_reference(self):
        cp = _cupy_or_skip(self)
        expected = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1),
            incident_face_ids=(10, 20),
            incident_face_counts=(2, 2),
            priority_point_ids=(),
            priority_face_ids=(),
            priorities=(),
            ambiguity_policy="emit_ambiguous",
        )
        actual = rt.select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
            incident_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            incident_face_ids=cp.asarray((10, 20), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2), dtype=cp.int64),
            priority_point_ids=cp.asarray((), dtype=cp.int64),
            priority_face_ids=cp.asarray((), dtype=cp.int64),
            priorities=cp.asarray((), dtype=cp.int64),
            ambiguity_policy="emit_ambiguous",
        )
        codes = actual["selection_status_code_labels"]

        self.assertEqual(expected["selection_status"], ("missing_priority",))
        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(_host_tuple(actual["candidate_count"]), expected["candidate_count"])
        self.assertEqual(
            _host_tuple(actual["selection_status_code"]),
            (codes["missing_priority"],),
        )

    def test_cupy_selector_emit_ambiguous_priority_matches_python_reference(self):
        cp = _cupy_or_skip(self)
        expected = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1),
            incident_face_ids=(10, 20),
            incident_face_counts=(2, 2),
            priority_point_ids=(1, 1),
            priority_face_ids=(10, 20),
            priorities=(0, 0),
            ambiguity_policy="emit_ambiguous",
        )
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

        self.assertEqual(expected["selection_status"], ("ambiguous_priority_tie",))
        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(_host_tuple(actual["candidate_count"]), expected["candidate_count"])
        self.assertEqual(
            _host_tuple(actual["selection_status_code"]),
            (codes["ambiguous_priority_tie"],),
        )

    def test_report_records_claude_gap_closure(self):
        text = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal3366 Claude review", text)
        self.assertIn("selection_status_code", text)
        self.assertIn("ambiguity_policy=\"drop\"", text)
        self.assertIn("missing-priority", text)
        self.assertIn("ambiguous-priority", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Ran 24 tests in 0.850s", text)
        self.assertIn("Ran 94 tests in 0.832s", text)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
