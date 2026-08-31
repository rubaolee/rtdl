import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4210_boundary_policy_canonical_alias_pod_confirmation_2026-06-09.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4210_boundary_policy_canonical_alias_pod_rtx4000ada"
    / "canonical_alias_smoke.json"
)


class Goal4210BoundaryPolicyCanonicalAliasPodConfirmationTest(unittest.TestCase):
    def test_canonical_alias_runs_and_propagates_to_metadata(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal4210.boundary_policy_canonical_alias_pod_smoke.v1")
        self.assertEqual(payload["commit"], "4cb13dc4")
        for key in (
            "plan_boundary_assignment_policy",
            "plan_boundary_assignment_canonical_policy",
            "metadata_boundary_assignment_policy",
            "metadata_boundary_assignment_canonical_policy",
            "native_boundary_assignment_policy",
            "native_boundary_assignment_canonical_policy",
        ):
            self.assertEqual(payload[key], "single_pass_candidate_root_rebased")
        self.assertEqual(payload["native_boundary_assignment_pass_count"], 1)
        self.assertEqual(payload["labels"], [1, 1, 1, 1, 1])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])

    def test_report_bounds_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("compatibility-safe metadata/API cleanup only", text)
        self.assertIn("does not authorize", text)
        self.assertIn("single_pass_candidate_root_rebased", text)


if __name__ == "__main__":
    unittest.main()
