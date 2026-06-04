import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3378_owner_face_all_point_priority_negative_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.json"


class Goal3378OwnerFaceAllPointPriorityNegativeProbeTest(unittest.TestCase):
    def test_artifact_rejects_all_point_priority_policy(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3378.owner_face_all_point_priority_negative_probe.v1")
        self.assertEqual(data["goal"], 3378)
        self.assertEqual(data["rtdl_commit"], "75876b18c45fe3c22edaa616198b2e35f4ceefb4")
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertEqual(data["policy_under_test"], "incident_chain_length_rank")
        self.assertEqual(data["policy_result"], "reject_for_default_route")
        self.assertEqual(data["point_count"], 512)
        self.assertEqual(data["shape_count"], 478)
        self.assertEqual(data["incident_row_count"], 1507)
        self.assertEqual(data["priority_row_count"], 1507)
        self.assertEqual(data["optix_candidate_row_count"], 1429)
        self.assertFalse(data["optix_candidate_overflow"])
        self.assertEqual(data["exact_row_count"], 1417)
        self.assertEqual(data["filtered_row_count"], 1007)
        self.assertFalse(data["matches_exact"])
        self.assertEqual(data["missing_exact_row_count"], 410)
        self.assertEqual(data["extra_row_count"], 0)
        self.assertEqual(data["missing_sample"][0], [260, 260])
        self.assertFalse(any(data["claim_boundary"].values()))

    def test_report_and_script_keep_negative_boundary_visible(self):
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("must be rejected for default route use", report)
        self.assertIn("drops true exact rows", report)
        self.assertIn("route-scale promotion still needs a better ambiguity-detection", report)
        self.assertIn("does not authorize release", report)
        self.assertIn("native default route claims", report)
        self.assertIn("policy_result", script)
        self.assertIn("reject_for_default_route", script)
        self.assertIn("incident_chain_length_rank", script)


if __name__ == "__main__":
    unittest.main()
