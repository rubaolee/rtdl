from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3359_owner_face_columnar_review_gap_closure_2026-06-04.md"


class Goal3359OwnerFaceReviewGapClosureTest(unittest.TestCase):
    def test_contract_documents_missing_topology_drop_policy(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertEqual(contract["filter_policy"]["missing_topology"], "drop_candidate")
        self.assertEqual(contract["filter_policy"]["missing_owner"], "fail_closed_by_default")
        self.assertEqual(
            contract["filter_policy"]["topology_face_presence_columns"],
            "gate_left_and_right_face_ids_when_present",
        )

    def test_columnar_filter_drops_candidates_with_missing_topology(self):
        filtered = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1,),
            candidate_shape_ids=(100,),
            topology_shape_ids=(),
            topology_left_face_ids=(),
            topology_right_face_ids=(),
            owner_point_ids=(1,),
            owner_face_ids=(10,),
        )

        self.assertEqual(
            filtered,
            {"point_id": (), "shape_id": (), "membership": (), "owner_face_id": ()},
        )

    def test_columnar_filter_honors_optional_topology_face_presence_columns(self):
        without_left_face = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1,),
            candidate_shape_ids=(100,),
            topology_shape_ids=(100,),
            topology_left_face_ids=(10,),
            topology_right_face_ids=(20,),
            topology_has_left_faces=(0,),
            topology_has_right_faces=(1,),
            owner_point_ids=(1,),
            owner_face_ids=(10,),
        )
        with_left_face = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1,),
            candidate_shape_ids=(100,),
            topology_shape_ids=(100,),
            topology_left_face_ids=(10,),
            topology_right_face_ids=(20,),
            topology_has_left_faces=(1,),
            topology_has_right_faces=(1,),
            owner_point_ids=(1,),
            owner_face_ids=(10,),
        )

        self.assertEqual(
            without_left_face,
            {"point_id": (), "shape_id": (), "membership": (), "owner_face_id": ()},
        )
        self.assertEqual(
            with_left_face,
            {"point_id": (1,), "shape_id": (100,), "membership": (1,), "owner_face_id": (10,)},
        )

    def test_conflicting_owner_face_selection_rows_remain_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "conflicting owner face"):
            rt.owner_face_ids_by_point_from_selection_rows(
                (
                    {"point_id": 1, "owner_face_id": 10},
                    {"point_id": 1, "owner_face_id": 20},
                )
            )

    def test_report_maps_claude_findings_to_closures(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3357 Claude review", text)
        self.assertIn("Goal3358 closed", text)
        self.assertIn("missing_topology = drop_candidate", text)
        self.assertIn("topology face-presence columns", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
