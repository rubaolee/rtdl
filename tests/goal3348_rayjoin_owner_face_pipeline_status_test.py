from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3348_rayjoin_owner_face_pipeline_status_2026-06-04.md"


class Goal3348RayJoinOwnerFacePipelineStatusTest(unittest.TestCase):
    def test_status_report_records_known_counts_and_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("exact `1417`, fast `1429`, delta `+12`", text)
        self.assertIn("Soil slice validates: exact `1471`, fast `1471`", text)
        self.assertIn("This proves expressiveness of the generic pipeline, not automatic RayJoin support", text)
        self.assertIn("The native engine must continue to consume explicit generic columns", text)

    def test_status_report_lists_current_generic_pieces(self):
        text = REPORT.read_text(encoding="utf-8")
        for name in (
            "chains_to_topology_rows",
            "chains_to_incident_face_candidate_rows",
            "as_cupy_columns",
            "filter_closed_shape_membership_candidates_by_owner_face",
            "select_unique_owner_faces_from_incident_candidates",
            "select_owner_faces_from_incident_candidates_with_priority",
            "owner_face_ids_by_point_from_selection_rows",
        ):
            self.assertIn(name, text)

    def test_status_report_keeps_claims_blocked(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("broad fast PIP count correctness", text)
        self.assertIn("automatic owner-face derivation", text)
        self.assertIn("RayJoin paper reproduction claims", text)
        self.assertIn("RTDL-beats-RayJoin claims", text)
        self.assertIn("broad RT-core speedup claims", text)


if __name__ == "__main__":
    unittest.main()
