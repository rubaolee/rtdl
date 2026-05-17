import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2308_bounded_probe_scale_smoke_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2308_bounded_probe_scale_smoke_pod_2026-05-17.json"


class Goal2308BoundedProbeScaleSmokeTest(unittest.TestCase):
    def test_artifact_records_all_expected_single_shape_hits(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], 2308)
        self.assertEqual(data["schema"], "rtdl.closed_shape_bounded_probe_scale_smoke.v1")
        self.assertTrue(data["all_match_expected"])
        self.assertEqual(len(data["records"]), 10)
        for record in data["records"]:
            self.assertEqual(record["count"], 1)
            self.assertEqual(len(record["rows"]), 1)
            self.assertTrue(record["matches_expected"])

    def test_artifact_keeps_claim_boundary(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = data["claim_boundary"]
        self.assertTrue(boundary["synthetic_single_shape_correctness_smoke"])
        self.assertFalse(boundary["broad_coordinate_scale_claim_authorized"])
        self.assertFalse(boundary["broad_performance_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])

    def test_report_preserves_narrow_interpretation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not remove the broader boundary", text)
        self.assertIn("No broad coordinate-scale validation", text)
        self.assertIn("No broad performance validation", text)
        self.assertIn("No v2.0 release authorization", text)


if __name__ == "__main__":
    unittest.main()
