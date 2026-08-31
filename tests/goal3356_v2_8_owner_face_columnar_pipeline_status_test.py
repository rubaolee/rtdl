from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3356_v2_8_owner_face_columnar_pipeline_status_2026-06-04.md"


class Goal3356V28OwnerFaceColumnarPipelineStatusTest(unittest.TestCase):
    def test_report_summarizes_row_and_columnar_contracts(self):
        text = REPORT.read_text(encoding="utf-8")
        for goal in ("Goal3349", "Goal3350", "Goal3351", "Goal3353", "Goal3354", "Goal3355"):
            self.assertIn(goal, text)
        for helper in (
            "derive_owner_face_priority_rows_from_rank_signals",
            "derive_owner_face_priority_columns_from_rank_signals",
            "select_owner_faces_from_incident_candidate_columns_with_priority_columns",
            "filter_closed_shape_membership_candidate_columns_by_owner_face_columns",
        ):
            self.assertIn(helper, text)

    def test_report_keeps_boundaries_and_next_steps_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not authorize release", text)
        self.assertIn("not a native/device implementation", text)
        self.assertIn("native engine must not infer", text)
        self.assertIn("75 tests", text)
        self.assertIn("Next engineering steps", text)


if __name__ == "__main__":
    unittest.main()
