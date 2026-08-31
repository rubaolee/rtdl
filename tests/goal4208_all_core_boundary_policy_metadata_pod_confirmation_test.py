import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4208_all_core_boundary_policy_metadata_pod_confirmation_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4208_all_core_boundary_metadata_rtx4000ada" / "ngsim_dense64_repeat2.json"


class Goal4208AllCoreBoundaryPolicyMetadataPodConfirmationTest(unittest.TestCase):
    def test_dense_all_core_policy_metadata_is_populated(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["commit"], "ef4b1f0f")
        self.assertEqual(len(payload["cases"]), 1)
        case = payload["cases"][0]
        self.assertEqual(case["dataset"], "ngsim_dense")
        self.assertEqual(case["point_count"], 65536)
        self.assertTrue(case["same_counts_only_signature"])

        default = case["policies"]["lowest_candidate_then_root"]
        two_pass = case["policies"]["lowest_component_root_two_pass"]
        self.assertEqual(default["signature"]["flag_true_count"], 65536)
        self.assertEqual(default["signature"]["negative_label_count"], 0)
        self.assertEqual(default["native_boundary_assignment_policy"], "lowest_candidate_then_root")
        self.assertEqual(default["native_boundary_assignment_pass_count"], 1)
        self.assertEqual(two_pass["native_boundary_assignment_policy"], "lowest_component_root_two_pass")
        self.assertEqual(two_pass["native_boundary_assignment_pass_count"], 1)

    def test_report_keeps_scope_bounded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("metadata integrity only", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("all-core case", text)


if __name__ == "__main__":
    unittest.main()
