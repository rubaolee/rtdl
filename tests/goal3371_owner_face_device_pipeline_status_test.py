from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3371_owner_face_device_pipeline_status_2026-06-04.md"


class Goal3371OwnerFaceDevicePipelineStatusTest(unittest.TestCase):
    def test_status_packet_tracks_current_helpers_and_evidence(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("select_owner_faces_from_incident_candidate_columns_with_priority_cupy", text)
        self.assertIn("filter_closed_shape_membership_candidate_columns_by_owner_face_cupy", text)
        self.assertIn("run_closed_shape_owner_face_priority_membership_pipeline_cupy", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Ran 96 tests in 0.782s", text)

    def test_status_packet_keeps_review_and_blockers_visible(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal3370 Gemini review", text)
        self.assertIn("pending", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("RayJoin paper reproduction wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("native generic lowering", text)


if __name__ == "__main__":
    unittest.main()
