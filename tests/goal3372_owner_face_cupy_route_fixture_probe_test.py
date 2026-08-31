import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3372_owner_face_cupy_route_fixture_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.json"


class Goal3372OwnerFaceCupyRouteFixtureProbeTest(unittest.TestCase):
    def test_artifact_records_exact_route_fixture_recovery(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3372.owner_face_cupy_route_fixture_probe.v1")
        self.assertEqual(data["goal"], 3372)
        self.assertEqual(data["rtdl_commit"], "ef36541ed81695d79c39cdc8c08ac37fc154f4e9")
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertEqual(data["point_count"], 7)
        self.assertEqual(data["incident_row_count"], 21)
        self.assertEqual(data["candidate_row_count"], 26)
        self.assertEqual(data["topology_row_count"], 11)
        self.assertTrue(data["selected_owner_faces_match_expected"])
        self.assertTrue(data["recovered_shapes_match_exact"])
        self.assertEqual(
            data["selected_owner_face_by_point"],
            data["expected_owner_face_by_point"],
        )
        self.assertEqual(
            data["recovered_shape_ids_by_point"],
            data["exact_shape_ids_by_point"],
        )
        self.assertFalse(any(data["claim_boundary"].values()))

    def test_report_and_script_keep_probe_boundary_visible(self):
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("route-fixture probe", report)
        self.assertIn("not native RT traversal", report)
        self.assertIn("does not authorize release", report)
        self.assertIn("RayJoin paper reproduction wording", report)
        self.assertIn("true zero-copy wording", report)
        self.assertIn("Route-fixture probe only", script)
        self.assertIn("rayjoin_paper_reproduction_claim_authorized", script)


if __name__ == "__main__":
    unittest.main()
