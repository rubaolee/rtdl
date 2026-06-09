import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4202_rt_dbscan_single_pass_reference_parity_2026-06-09.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4202_rt_dbscan_single_pass_reference_parity_rtx4000ada"
    / "reference_parity.json"
)


class Goal4202RtDbscanSinglePassReferenceParityEvidenceTest(unittest.TestCase):
    def test_all_cases_match_reference_and_two_pass(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal4202.rt_dbscan_single_pass_reference_parity.v1")
        self.assertEqual(payload["commit"], "801acd3b")
        self.assertEqual(len(payload["cases"]), 4)
        for case in payload["cases"]:
            self.assertTrue(case["all_policies_match_reference"])
            self.assertTrue(case["default_matches_two_pass_labels"])
            self.assertFalse(case["route_promotion_authorized"])
            for policy in ("lowest_candidate_then_root", "lowest_component_root_two_pass"):
                row = case["policies"][policy]
                self.assertTrue(row["matches_reference_labels"])
                self.assertEqual(row["mismatch_count"], 0)
                self.assertFalse(row["metadata"]["public_speedup_claim_authorized"])
                self.assertFalse(row["metadata"]["true_zero_copy_claim_authorized"])

    def test_default_is_one_pass_and_two_pass_is_two_pass(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for case in payload["cases"]:
            default = case["policies"]["lowest_candidate_then_root"]
            two_pass = case["policies"]["lowest_component_root_two_pass"]
            self.assertEqual(default["native_boundary_assignment_pass_count"], 1)
            self.assertEqual(two_pass["native_boundary_assignment_pass_count"], 2)
            self.assertEqual(
                default["native_symbol"],
                "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs",
            )

    def test_report_keeps_scope_bounded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("one-pass should remain the performance route", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("broader same-contract gate", text)
        self.assertIn("not adding a", text)
        self.assertIn("second traversal", text)


if __name__ == "__main__":
    unittest.main()
