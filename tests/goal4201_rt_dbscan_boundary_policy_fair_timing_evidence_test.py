import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4201_rt_dbscan_boundary_policy_fair_timing_2026-06-09.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4201_rt_dbscan_boundary_policy_fair_timing_rtx4000ada"
    / "fair_timing_repeat5.json"
)


class Goal4201RtDbscanBoundaryPolicyFairTimingEvidenceTest(unittest.TestCase):
    def test_artifact_records_all_expected_cases(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal4201.rt_dbscan_boundary_policy_fair_timing.v1")
        self.assertEqual(payload["commit"], "0cfdad4a")
        cases = {(case["dataset"], case["point_count"]): case for case in payload["cases"]}
        self.assertEqual(
            set(cases),
            {
                ("clustered3d", 16384),
                ("clustered3d", 65536),
                ("road3d", 65536),
                ("ngsim_dense", 65536),
            },
        )
        for case in cases.values():
            self.assertEqual(case["repeat"], 5)
            self.assertEqual(case["warmup"], 2)
            self.assertTrue(case["same_counts_only_signature"])
            self.assertFalse(case["route_promotion_authorized"])
            self.assertFalse(case["public_speedup_claim_authorized"])
            self.assertFalse(case["true_zero_copy_claim_authorized"])

    def test_two_pass_is_not_promoted_by_timing(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        ratios = {
            (case["dataset"], case["point_count"]): case["two_pass_vs_default_median_ratio"]
            for case in payload["cases"]
        }
        self.assertGreater(ratios[("clustered3d", 16384)], 1.5)
        self.assertGreater(ratios[("clustered3d", 65536)], 1.5)
        self.assertGreater(ratios[("road3d", 65536)], 1.3)
        self.assertLess(ratios[("ngsim_dense", 65536)], 1.05)

    def test_report_records_next_generic_runtime_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not promote", text)
        self.assertIn("single-traversal boundary-candidate", text)
        self.assertIn("not an RT-DBSCAN app-specific trick", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
