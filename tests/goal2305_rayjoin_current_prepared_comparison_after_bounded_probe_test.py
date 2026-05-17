import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2305_rayjoin_current_prepared_comparison_after_bounded_probe_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2305_rayjoin_current_prepared_comparison_after_bounded_probe_pod_2026-05-17.json"


class Goal2305RayjoinCurrentPreparedComparisonAfterBoundedProbeTest(unittest.TestCase):
    def test_artifact_records_current_routes_and_counts(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], 2305)
        self.assertEqual(data["schema"], "rtdl.rayjoin.current_prepared_comparison_after_bounded_probe.v1")
        self.assertEqual(data["lsi"]["route"], "prepared_segment_pair_intersection_optix_with_prepacked_left")
        self.assertEqual(data["pip"]["route"], "prepared_point_closed_shape_membership_2d_optix_with_prepacked_points")
        self.assertTrue(data["lsi"]["matches_prior_expected_count"])
        self.assertTrue(data["pip"]["matches_prior_expected_count"])
        self.assertEqual(data["lsi"]["raw_rows"]["values"], [8921] * 7)
        self.assertEqual(data["pip"]["scalar_count"]["values"], [8686] * 7)

    def test_artifact_records_bounded_probe_current_pip_performance(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertLess(data["pip"]["scalar_count"]["median_sec"], 0.010)
        self.assertLess(data["pip"]["positive_rows"]["median_sec"], 0.024)
        self.assertLess(data["lsi"]["raw_rows"]["median_sec"], 0.010)

    def test_report_keeps_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Current Table", text)
        self.assertIn("prepared point/closed-shape scalar count with bounded probe", text)
        self.assertIn("No RayJoin paper reproduction", text)
        self.assertIn("No claim that RTDL beats RayJoin", text)
        self.assertIn("No true zero-copy claim", text)
        self.assertIn("No v2.0 release authorization", text)
        self.assertIn("validated only for the current", text)


if __name__ == "__main__":
    unittest.main()
