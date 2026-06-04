import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
INCIDENT_ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3339_fail_closed_incident_owner_face_selector_2026-06-04.md"


class Goal3339FailClosedIncidentOwnerFaceSelectorTest(unittest.TestCase):
    def test_unique_max_incident_face_selects_owner_face(self):
        rows = (
            {"point_id": 1, "face_id": 10, "incident_face_count": 3, "incident_chain_count": 4},
            {"point_id": 1, "face_id": 20, "incident_face_count": 1, "incident_chain_count": 4},
            {"point_id": 2, "face_id": 30, "incident_face_count": 2, "incident_chain_count": 3},
            {"point_id": 2, "face_id": 40, "incident_face_count": 1, "incident_chain_count": 3},
        )
        selected = rt.select_unique_owner_faces_from_incident_candidates(rows)
        self.assertEqual(
            selected,
            (
                {
                    "point_id": 1,
                    "owner_face_id": 10,
                    "incident_face_count": 3,
                    "candidate_count": 1,
                    "selection_status": "unique_max_incident_face",
                },
                {
                    "point_id": 2,
                    "owner_face_id": 30,
                    "incident_face_count": 2,
                    "candidate_count": 1,
                    "selection_status": "unique_max_incident_face",
                },
            ),
        )

    def test_ties_fail_closed_or_require_explicit_policy(self):
        rows = (
            {"point_id": 1, "face_id": 10, "incident_face_count": 2},
            {"point_id": 1, "face_id": 20, "incident_face_count": 2},
        )
        with self.assertRaisesRegex(ValueError, "ambiguous owner face"):
            rt.select_unique_owner_faces_from_incident_candidates(rows)
        self.assertEqual(
            rt.select_unique_owner_faces_from_incident_candidates(rows, ambiguity_policy="drop"),
            (),
        )
        self.assertEqual(
            rt.select_unique_owner_faces_from_incident_candidates(rows, ambiguity_policy="emit_ambiguous"),
            (
                {
                    "point_id": 1,
                    "owner_face_id": -1,
                    "incident_face_count": 2,
                    "candidate_count": 2,
                    "selection_status": "ambiguous_tie",
                },
            ),
        )
        with self.assertRaises(ValueError):
            rt.select_unique_owner_faces_from_incident_candidates(rows, ambiguity_policy="guess")

    def test_goal3335_rayjoin_incident_rows_are_ambiguous_under_unique_max_selector(self):
        data = json.loads(INCIDENT_ARTIFACT.read_text(encoding="utf-8"))
        candidate_rows = []
        for item in data["rows"]:
            for entry in item["endpoint_face_frequency"]:
                candidate_rows.append(
                    {
                        "point_id": int(item["point_id"]),
                        "face_id": int(entry["face_id"]),
                        "incident_face_count": int(entry["count"]),
                    }
                )
        with self.assertRaisesRegex(ValueError, "ambiguous owner face"):
            rt.select_unique_owner_faces_from_incident_candidates(candidate_rows)
        ambiguous = rt.select_unique_owner_faces_from_incident_candidates(
            candidate_rows,
            ambiguity_policy="emit_ambiguous",
        )
        self.assertEqual(len(ambiguous), 7)
        self.assertTrue(all(row["selection_status"] == "ambiguous_tie" for row in ambiguous))

    def test_report_states_no_silent_tie_break(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("no silent tie-break is allowed", text)
        self.assertIn("not an automatic RayJoin fix", text)
        self.assertIn("native engine still does not infer CDB or RayJoin ownership semantics", text)


if __name__ == "__main__":
    unittest.main()
