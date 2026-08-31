from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3353_owner_face_priority_columnar_derivation_2026-06-04.md"


def _columns_to_rows(columns):
    return tuple(
        {
            "point_id": point_id,
            "face_id": face_id,
            "priority": priority,
            "priority_rank_key": rank_key,
        }
        for point_id, face_id, priority, rank_key in zip(
            columns["point_id"],
            columns["face_id"],
            columns["priority"],
            columns["priority_rank_key"],
        )
    )


class Goal3353OwnerFacePriorityColumnarDerivationTest(unittest.TestCase):
    def test_columnar_front_door_matches_row_front_door(self):
        point_ids = (1, 1, 1, 2)
        face_ids = (10, 20, 30, 40)
        rank_columns = {
            "rank0": (1, 0, 2, 3),
            "rank1": (0, 5, 0, 1),
        }
        columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids,
            face_ids,
            rank_columns,
            rank_fields=("rank0", "rank1"),
        )

        rows = [
            {
                "point_id": point_id,
                "face_id": face_id,
                "rank0": rank_columns["rank0"][index],
                "rank1": rank_columns["rank1"][index],
            }
            for index, (point_id, face_id) in enumerate(zip(point_ids, face_ids))
        ]
        expected_rows = rt.derive_owner_face_priority_rows_from_rank_signals(
            rows,
            rank_fields=("rank0", "rank1"),
        )

        self.assertEqual(_columns_to_rows(columns), expected_rows)
        self.assertEqual(columns["point_id"], (1, 1, 1, 2))
        self.assertEqual(columns["face_id"], (20, 10, 30, 40))
        self.assertEqual(columns["priority"], (0, 1, 2, 0))

    def test_columnar_priorities_feed_existing_selector(self):
        columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=(1, 1),
            face_ids=(10, 20),
            rank_columns={"rank0": (5, 1)},
            rank_fields=("rank0",),
        )
        priority_rows = _columns_to_rows(columns)
        selected = rt.select_owner_faces_from_incident_candidates_with_priority(
            (
                {"point_id": 1, "face_id": 10, "incident_face_count": 2},
                {"point_id": 1, "face_id": 20, "incident_face_count": 2},
            ),
            priority_rows,
        )

        self.assertEqual(selected[0]["owner_face_id"], 20)
        self.assertEqual(selected[0]["selection_status"], "priority_tie_break")

    def test_columnar_front_door_fails_closed_on_bad_shapes(self):
        with self.assertRaisesRegex(ValueError, "same length"):
            rt.derive_owner_face_priority_columns_from_rank_signals(
                point_ids=(1,),
                face_ids=(10, 20),
                rank_columns={"rank0": (1,)},
                rank_fields=("rank0",),
            )
        with self.assertRaisesRegex(KeyError, "missing owner-face priority rank columns"):
            rt.derive_owner_face_priority_columns_from_rank_signals(
                point_ids=(1,),
                face_ids=(10,),
                rank_columns={},
                rank_fields=("rank0",),
            )
        with self.assertRaisesRegex(ValueError, "wrong length"):
            rt.derive_owner_face_priority_columns_from_rank_signals(
                point_ids=(1, 1),
                face_ids=(10, 20),
                rank_columns={"rank0": (1,)},
                rank_fields=("rank0",),
            )
        with self.assertRaisesRegex(ValueError, "ambiguous owner-face priority rank"):
            rt.derive_owner_face_priority_columns_from_rank_signals(
                point_ids=(1, 1),
                face_ids=(10, 20),
                rank_columns={"rank0": (1, 1)},
                rank_fields=("rank0",),
            )

    def test_contract_mentions_columnar_derivation_helper(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "derive_owner_face_priority_columns_from_rank_signals",
            contract["optional_priority_derivation_helpers"],
        )

    def test_report_keeps_columnar_path_reference_only(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("columnar same-contract front door", text)
        self.assertIn("not a device implementation", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("native/device lowering remains blocked", text)


if __name__ == "__main__":
    unittest.main()
