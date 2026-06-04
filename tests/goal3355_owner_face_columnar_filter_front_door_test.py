from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3355_owner_face_columnar_filter_front_door_2026-06-04.md"


class Goal3355OwnerFaceColumnarFilterFrontDoorTest(unittest.TestCase):
    def test_columnar_pipeline_reaches_membership_filter(self):
        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=(1, 1, 2),
            face_ids=(10, 20, 30),
            rank_columns={"rank0": (5, 1, 0)},
            rank_fields=("rank0",),
        )
        selected_columns = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1, 2),
            incident_face_ids=(10, 20, 30),
            incident_face_counts=(2, 2, 1),
            priority_point_ids=priority_columns["point_id"],
            priority_face_ids=priority_columns["face_id"],
            priorities=priority_columns["priority"],
        )
        filtered_columns = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1, 1, 2),
            candidate_shape_ids=(100, 101, 102),
            topology_shape_ids=(100, 101, 102),
            topology_left_face_ids=(10, 20, 30),
            topology_right_face_ids=(11, 21, 31),
            owner_point_ids=selected_columns["point_id"],
            owner_face_ids=selected_columns["owner_face_id"],
        )

        self.assertEqual(
            filtered_columns,
            {
                "point_id": (1, 2),
                "shape_id": (101, 102),
                "membership": (1, 1),
                "owner_face_id": (20, 30),
            },
        )

    def test_columnar_filter_matches_row_filter(self):
        filtered_columns = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1, 1, 2),
            candidate_shape_ids=(100, 101, 102),
            topology_shape_ids=(100, 101, 102),
            topology_left_face_ids=(10, 20, 30),
            topology_right_face_ids=(11, 21, 31),
            owner_point_ids=(1, 2),
            owner_face_ids=(20, 30),
        )
        filtered_rows = rt.filter_closed_shape_membership_candidates_by_owner_face(
            (
                {"point_id": 1, "shape_id": 100},
                {"point_id": 1, "shape_id": 101},
                {"point_id": 2, "shape_id": 102},
            ),
            (
                {"shape_id": 100, "left_face_id": 10, "right_face_id": 11},
                {"shape_id": 101, "left_face_id": 20, "right_face_id": 21},
                {"shape_id": 102, "left_face_id": 30, "right_face_id": 31},
            ),
            {1: 20, 2: 30},
        )

        self.assertEqual(
            filtered_columns,
            {
                "point_id": tuple(row["point_id"] for row in filtered_rows),
                "shape_id": tuple(row["shape_id"] for row in filtered_rows),
                "membership": tuple(row["membership"] for row in filtered_rows),
                "owner_face_id": tuple(row["owner_face_id"] for row in filtered_rows),
            },
        )

    def test_columnar_filter_fails_closed_on_bad_shapes_or_missing_owner(self):
        with self.assertRaisesRegex(ValueError, "candidate point and shape columns"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
                candidate_point_ids=(1,),
                candidate_shape_ids=(100, 101),
                topology_shape_ids=(100,),
                topology_left_face_ids=(10,),
                topology_right_face_ids=(11,),
                owner_point_ids=(1,),
                owner_face_ids=(10,),
            )
        with self.assertRaisesRegex(ValueError, "topology shape and face columns"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
                candidate_point_ids=(1,),
                candidate_shape_ids=(100,),
                topology_shape_ids=(100,),
                topology_left_face_ids=(10, 20),
                topology_right_face_ids=(11,),
                owner_point_ids=(1,),
                owner_face_ids=(10,),
            )
        with self.assertRaisesRegex(ValueError, "owner point and face columns"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
                candidate_point_ids=(1,),
                candidate_shape_ids=(100,),
                topology_shape_ids=(100,),
                topology_left_face_ids=(10,),
                topology_right_face_ids=(11,),
                owner_point_ids=(1,),
                owner_face_ids=(10, 20),
            )
        with self.assertRaisesRegex(KeyError, "missing owner face"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
                candidate_point_ids=(1,),
                candidate_shape_ids=(100,),
                topology_shape_ids=(100,),
                topology_left_face_ids=(10,),
                topology_right_face_ids=(11,),
                owner_point_ids=(),
                owner_face_ids=(),
            )

    def test_missing_owner_drop_policy_stays_empty(self):
        filtered = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1,),
            candidate_shape_ids=(100,),
            topology_shape_ids=(100,),
            topology_left_face_ids=(10,),
            topology_right_face_ids=(11,),
            owner_point_ids=(),
            owner_face_ids=(),
            missing_owner_policy="drop",
        )
        self.assertEqual(
            filtered,
            {"point_id": (), "shape_id": (), "membership": (), "owner_face_id": ()},
        )

    def test_contract_mentions_columnar_filter_helper(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "filter_closed_shape_membership_candidate_columns_by_owner_face_columns",
            contract["optional_columnar_pipeline_helpers"],
        )

    def test_report_keeps_filter_reference_only(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("complete columnar Python reference pipeline", text)
        self.assertIn("not a native/device lowering", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("native engine still must not infer", text)


if __name__ == "__main__":
    unittest.main()
