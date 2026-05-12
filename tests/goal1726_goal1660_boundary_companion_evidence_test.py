import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1726_goal1660_boundary_companion_evidence_2026-05-12.md"
CONSOLIDATION = ROOT / "docs" / "reports" / "goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json"


class Goal1726Goal1660BoundaryCompanionEvidenceTest(unittest.TestCase):
    def test_companion_artifacts_resolve_all_goal1723_boundaries(self) -> None:
        payload = json.loads(CONSOLIDATION.read_text(encoding="utf-8"))
        self.assertEqual(payload["rows_with_timing_artifact_boundary_notes"], 3)
        self.assertEqual(payload["rows_with_companion_resolutions"], 3)
        self.assertEqual(payload["rows_with_unresolved_boundaries"], 0)
        for row in payload["rows"]:
            if row["timing_artifact_boundary_notes"]:
                self.assertTrue(row["boundary_resolved_by_companion"])
                self.assertTrue(row["evidence_pair_ready_without_public_claim"])

    def test_facility_and_robot_validation_companions_match_oracle(self) -> None:
        facility_current = json.loads((ROOT / "docs/reports/goal1726_v1_6_11_facility_validation_companion_optix.json").read_text())
        facility_v1 = json.loads((ROOT / "docs/reports/goal1726_v1_0_facility_validation_companion_optix.json").read_text())
        robot_current = json.loads((ROOT / "docs/reports/goal1726_v1_6_11_robot_collision_validation_companion_optix.json").read_text())
        robot_v1 = json.loads((ROOT / "docs/reports/goal1726_v1_0_robot_collision_validation_companion_optix.json").read_text())
        for artifact in (facility_current, facility_v1):
            self.assertTrue(artifact["scenario"]["result"]["matches_oracle"])
            self.assertEqual(artifact["scenario"]["result"]["threshold_reached_count"], 80000)
        for artifact in (robot_current, robot_v1):
            self.assertTrue(artifact["validated"])
            self.assertTrue(artifact["matches_oracle"])
            self.assertEqual(artifact["result"]["colliding_pose_count"], 3840)

    def test_jaccard_companions_use_public_safe_chunks(self) -> None:
        current = json.loads((ROOT / "docs/reports/goal1726_v1_6_11_polygon_set_jaccard_public_safe_chunk_optix.json").read_text())
        baseline = json.loads((ROOT / "docs/reports/goal1726_v1_0_polygon_set_jaccard_public_safe_chunk_optix.json").read_text())
        for artifact in (current, baseline):
            self.assertEqual(artifact["status"], "pass")
            self.assertTrue(artifact["parity_vs_cpu"])
            self.assertTrue(artifact["chunk_policy"]["public_safe"])
            self.assertEqual(artifact["chunk_policy"]["chunk_copies"], 1024)

    def test_report_keeps_release_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", text)
        self.assertIn("Unresolved boundaries: `0`", text)
        self.assertIn("not release authorization", text)


if __name__ == "__main__":
    unittest.main()
