import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4212_boundary_policy_default_canonical_pod_confirmation_2026-06-09.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4212_boundary_policy_default_canonical_pod_rtx4000ada"
    / "default_canonical_smoke.json"
)


class Goal4212BoundaryPolicyDefaultCanonicalPodConfirmationTest(unittest.TestCase):
    def test_no_policy_argument_uses_canonical_default_on_pod(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal4212.boundary_policy_default_canonical_pod_smoke.v1")
        self.assertEqual(payload["commit"], "7eea73ca")
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

    def test_report_keeps_scope_bounded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("no-policy-argument", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("default naming behavior only", text)


if __name__ == "__main__":
    unittest.main()
