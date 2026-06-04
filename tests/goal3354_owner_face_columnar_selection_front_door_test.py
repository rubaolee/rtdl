from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3354_owner_face_columnar_selection_front_door_2026-06-04.md"


class Goal3354OwnerFaceColumnarSelectionFrontDoorTest(unittest.TestCase):
    def test_columnar_selector_matches_row_selector(self):
        selected_columns = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1, 2),
            incident_face_ids=(10, 20, 30),
            incident_face_counts=(2, 2, 1),
            priority_point_ids=(1, 1, 2),
            priority_face_ids=(10, 20, 30),
            priorities=(5, 1, 0),
        )
        self.assertEqual(
            selected_columns,
            {
                "point_id": (1, 2),
                "owner_face_id": (20, 30),
                "incident_face_count": (2, 1),
                "candidate_count": (2, 1),
                "selection_status": ("priority_tie_break", "unique_max_incident_face"),
            },
        )

    def test_derived_priority_columns_feed_columnar_selector(self):
        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=(1, 1),
            face_ids=(10, 20),
            rank_columns={"rank0": (5, 1)},
            rank_fields=("rank0",),
        )
        selected_columns = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1),
            incident_face_ids=(10, 20),
            incident_face_counts=(2, 2),
            priority_point_ids=priority_columns["point_id"],
            priority_face_ids=priority_columns["face_id"],
            priorities=priority_columns["priority"],
        )

        self.assertEqual(selected_columns["owner_face_id"], (20,))
        self.assertEqual(selected_columns["selection_status"], ("priority_tie_break",))

    def test_columnar_selector_fails_closed_on_bad_shapes_or_missing_priority(self):
        with self.assertRaisesRegex(ValueError, "incident point, face, and count columns"):
            rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
                incident_point_ids=(1,),
                incident_face_ids=(10, 20),
                incident_face_counts=(2,),
                priority_point_ids=(1,),
                priority_face_ids=(10,),
                priorities=(0,),
            )
        with self.assertRaisesRegex(ValueError, "priority point, face, and priority columns"):
            rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
                incident_point_ids=(1,),
                incident_face_ids=(10,),
                incident_face_counts=(2,),
                priority_point_ids=(1,),
                priority_face_ids=(10, 20),
                priorities=(0,),
            )
        with self.assertRaisesRegex(ValueError, "missing owner-face priority"):
            rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
                incident_point_ids=(1, 1),
                incident_face_ids=(10, 20),
                incident_face_counts=(2, 2),
                priority_point_ids=(1,),
                priority_face_ids=(10,),
                priorities=(0,),
            )

    def test_contract_mentions_columnar_selection_helper(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "select_owner_faces_from_incident_candidate_columns_with_priority_columns",
            contract["optional_columnar_pipeline_helpers"],
        )

    def test_report_keeps_columnar_selector_reference_only(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("columnar front door", text)
        self.assertIn("shares the row selector semantics", text)
        self.assertIn("not a native/device implementation", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
