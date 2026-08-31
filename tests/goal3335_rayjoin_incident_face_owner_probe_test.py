import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.md"


class Goal3335RayJoinIncidentFaceOwnerProbeTest(unittest.TestCase):
    def test_owner_face_is_present_but_not_unique_in_incident_faces(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3335.rayjoin_incident_face_owner_probe.v1")
        self.assertEqual(data["point_count"], 7)
        self.assertEqual(data["owner_face_present_in_all_vertex_incident_faces"], 7)
        self.assertEqual(data["owner_face_present_in_endpoint_incident_faces"], 7)
        for row in data["rows"]:
            frequencies = row["endpoint_face_frequency"]
            self.assertGreaterEqual(len(frequencies), 3)
            self.assertIn(
                row["owner_face_used_in_goal3330"],
                {entry["face_id"] for entry in frequencies},
            )
            counts = {entry["count"] for entry in frequencies[:3]}
            self.assertEqual(counts, {2})

    def test_claims_stay_blocked(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for value in data["claim_boundary"].values():
            self.assertFalse(value)

    def test_report_states_next_contract_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Simple maximum-frequency rule: insufficient", text)
        self.assertIn("deterministic, generic vertex/face ownership derivation contract", text)
        self.assertIn("native engine can consume owner-face columns once they are explicit", text)


if __name__ == "__main__":
    unittest.main()
