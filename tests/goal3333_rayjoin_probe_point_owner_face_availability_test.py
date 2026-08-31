import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3333_rayjoin_probe_point_owner_face_availability_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3333_rayjoin_probe_point_owner_face_availability_2026-06-04.md"


class Goal3333RayJoinProbePointOwnerFaceAvailabilityTest(unittest.TestCase):
    def test_simple_left_or_right_face_policy_is_insufficient(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3333.rayjoin_probe_point_owner_face_availability.v1")
        self.assertEqual(data["point_count"], 7)
        self.assertEqual(data["simple_left_policy_matches"], 4)
        self.assertEqual(data["simple_right_policy_matches"], 1)

        rows = {int(row["point_id"]): row for row in data["point_chain_rows"]}
        neither = {
            point_id
            for point_id, row in rows.items()
            if int(row["owner_face_is_left"]) == 0 and int(row["owner_face_is_right"]) == 0
        }
        self.assertEqual(neither, {538, 564})
        self.assertEqual(rows[538]["owner_face_used_in_goal3330"], 217)
        self.assertEqual(rows[564]["owner_face_used_in_goal3330"], 187)

    def test_claims_stay_blocked(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = data["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])

    def test_report_keeps_next_work_explicit(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("whether those owner face ids are trivially available", text)
        self.assertIn("They are not", text)
        self.assertIn("derive or provide owner-face columns as explicit input", text)
        self.assertIn("native engine must not infer RayJoin or CDB ownership semantics", text)


if __name__ == "__main__":
    unittest.main()
