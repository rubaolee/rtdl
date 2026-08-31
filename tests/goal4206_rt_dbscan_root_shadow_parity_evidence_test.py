import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4206_rt_dbscan_root_shadow_parity_2026-06-09.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4206_rt_dbscan_root_shadow_parity_rtx4000ada"
    / "root_shadow_parity.json"
)


class Goal4206RtDbscanRootShadowParityEvidenceTest(unittest.TestCase):
    def test_root_shadow_fixture_matches_reference(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["commit"], "ff072bbf")
        self.assertEqual(len(payload["cases"]), 1)
        case = payload["cases"][0]
        self.assertEqual(case["dataset"], "adversarial_root_shadow_1d")
        self.assertEqual(case["point_count"], 5)
        self.assertEqual(case["candidate_pair_count"], 6)
        self.assertEqual(case["predicate_true_count"], 4)
        self.assertEqual(case["reference_component_sizes"], [5])
        self.assertTrue(case["all_policies_match_reference"])
        self.assertTrue(case["default_matches_two_pass_labels"])

        default = case["policies"]["lowest_candidate_then_root"]
        two_pass = case["policies"]["lowest_component_root_two_pass"]
        self.assertEqual(default["mismatch_count"], 0)
        self.assertEqual(two_pass["mismatch_count"], 0)
        self.assertEqual(default["native_boundary_assignment_pass_count"], 1)
        self.assertEqual(two_pass["native_boundary_assignment_pass_count"], 2)

    def test_report_keeps_promotion_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("root-shadow fixture", text)
        self.assertIn("keep one-pass as the performance route", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("rename/clarify", text)


if __name__ == "__main__":
    unittest.main()
