import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4205_rt_dbscan_single_pass_multi_seed_parity_2026-06-09.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4205_rt_dbscan_single_pass_multi_seed_parity_rtx4000ada"
SEEDS = ("20260519", "20260609", "7", "42")


class Goal4205RtDbscanSinglePassMultiSeedParityEvidenceTest(unittest.TestCase):
    def test_all_seed_artifacts_are_present_and_clean(self) -> None:
        total_cases = 0
        for seed in SEEDS:
            path = ARTIFACT_DIR / f"reference_parity_seed_{seed}.json"
            self.assertTrue(path.exists(), path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "rtdl.goal4202.rt_dbscan_single_pass_reference_parity.v1")
            self.assertEqual(payload["commit"], "64941904")
            self.assertEqual(len(payload["cases"]), 4)
            total_cases += len(payload["cases"])
            for case in payload["cases"]:
                self.assertTrue(case["all_policies_match_reference"])
                self.assertTrue(case["default_matches_two_pass_labels"])
                self.assertFalse(case["route_promotion_authorized"])
                self.assertFalse(case["public_speedup_claim_authorized"])
                self.assertFalse(case["true_zero_copy_claim_authorized"])
                default = case["policies"]["lowest_candidate_then_root"]
                two_pass = case["policies"]["lowest_component_root_two_pass"]
                self.assertEqual(default["mismatch_count"], 0)
                self.assertEqual(two_pass["mismatch_count"], 0)
                self.assertEqual(default["native_boundary_assignment_pass_count"], 1)
                self.assertEqual(two_pass["native_boundary_assignment_pass_count"], 2)
        self.assertEqual(total_cases, 16)

    def test_report_states_one_pass_direction_without_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("keep the one-pass route as the performance route", text)
        self.assertIn("does not yet promote", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("compatibility-safe metadata/API cleanup", text)


if __name__ == "__main__":
    unittest.main()
