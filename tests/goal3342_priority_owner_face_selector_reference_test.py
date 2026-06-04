import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
INCIDENT_ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3342_priority_owner_face_selector_reference_2026-06-04.md"


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


class Goal3342PriorityOwnerFaceSelectorReferenceTest(unittest.TestCase):
    def test_priority_breaks_tied_incident_counts_explicitly(self):
        rows = (
            {"point_id": 1, "face_id": 10, "incident_face_count": 2},
            {"point_id": 1, "face_id": 20, "incident_face_count": 2},
        )
        selected = rt.select_owner_faces_from_incident_candidates_with_priority(
            rows,
            (
                {"point_id": 1, "face_id": 10, "priority": 5},
                {"point_id": 1, "face_id": 20, "priority": 1},
            ),
        )
        self.assertEqual(
            selected,
            (
                {
                    "point_id": 1,
                    "owner_face_id": 20,
                    "incident_face_count": 2,
                    "candidate_count": 2,
                    "selection_status": "priority_tie_break",
                },
            ),
        )

    def test_missing_or_tied_priority_fails_closed(self):
        rows = (
            {"point_id": 1, "face_id": 10, "incident_face_count": 2},
            {"point_id": 1, "face_id": 20, "incident_face_count": 2},
        )
        with self.assertRaisesRegex(ValueError, "missing owner-face priority"):
            rt.select_owner_faces_from_incident_candidates_with_priority(
                rows,
                ({"point_id": 1, "face_id": 10, "priority": 1},),
            )
        with self.assertRaisesRegex(ValueError, "ambiguous owner-face priority"):
            rt.select_owner_faces_from_incident_candidates_with_priority(
                rows,
                (
                    {"point_id": 1, "face_id": 10, "priority": 1},
                    {"point_id": 1, "face_id": 20, "priority": 1},
                ),
            )
        self.assertEqual(
            rt.select_owner_faces_from_incident_candidates_with_priority(rows, (), ambiguity_policy="drop"),
            (),
        )

    def test_goal3335_rayjoin_rows_can_be_selected_only_with_explicit_priorities(self):
        data = json.loads(INCIDENT_ARTIFACT.read_text(encoding="utf-8"))
        candidate_rows = []
        priority_rows = []
        for item in data["rows"]:
            point_id = int(item["point_id"])
            owner_face = OWNER_FACE_BY_POINT[point_id]
            for entry in item["endpoint_face_frequency"]:
                face_id = int(entry["face_id"])
                candidate_rows.append(
                    {
                        "point_id": point_id,
                        "face_id": face_id,
                        "incident_face_count": int(entry["count"]),
                    }
                )
                priority_rows.append(
                    {
                        "point_id": point_id,
                        "face_id": face_id,
                        "priority": 0 if face_id == owner_face else 10,
                    }
                )
        selected = rt.select_owner_faces_from_incident_candidates_with_priority(candidate_rows, priority_rows)
        self.assertEqual({row["point_id"] for row in selected}, set(OWNER_FACE_BY_POINT))
        for row in selected:
            self.assertEqual(row["owner_face_id"], OWNER_FACE_BY_POINT[row["point_id"]])
            self.assertEqual(row["selection_status"], "priority_tie_break")

    def test_report_keeps_priority_as_caller_policy(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Priority rows are caller/data policy", text)
        self.assertIn("Native code must not guess CDB or RayJoin ownership semantics", text)
        self.assertIn("not that RTDL has solved automatic owner-face derivation", text)


if __name__ == "__main__":
    unittest.main()
