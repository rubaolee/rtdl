import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4198_predicate_boundary_two_pass_policy_pod_evidence_2026-06-09.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4198_predicate_boundary_two_pass_policy_pod_rtx4000ada"
CLUSTERED = ARTIFACT_DIR / "two_pass_clustered_smoke.stdout.json"
SPARSE = ARTIFACT_DIR / "two_pass_smoke.stdout.json"


class Goal4198PredicateBoundaryTwoPassPolicyPodEvidenceTest(unittest.TestCase):
    def test_clustered_artifact_records_two_pass_policy_metadata(self) -> None:
        payload = json.loads(CLUSTERED.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal4198.predicate_boundary_two_pass_policy_clustered_smoke.v1")
        self.assertEqual(payload["commit"], "96e63e37")
        self.assertEqual(payload["dataset"], "clustered3d")
        self.assertEqual(payload["point_count"], 16384)
        self.assertTrue(payload["same_counts_only_signature"])

        default = payload["policies"]["lowest_candidate_then_root"]
        two_pass = payload["policies"]["lowest_component_root_two_pass"]

        self.assertEqual(default["native_boundary_assignment_policy"], "lowest_candidate_then_root")
        self.assertEqual(default["native_boundary_assignment_pass_count"], 1)
        self.assertEqual(two_pass["native_boundary_assignment_policy"], "lowest_component_root_two_pass")
        self.assertEqual(two_pass["native_boundary_assignment_pass_count"], 2)
        self.assertEqual(
            two_pass["native_symbol"],
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs",
        )
        self.assertEqual(default["flag_true_count"], two_pass["flag_true_count"])
        self.assertEqual(default["negative_label_count"], two_pass["negative_label_count"])
        self.assertEqual(default["component_count"], two_pass["component_count"])
        self.assertEqual(default["largest_component_size"], two_pass["largest_component_size"])

    def test_claim_boundaries_remain_false_in_pod_artifacts(self) -> None:
        for path in (CLUSTERED, SPARSE):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for policy_payload in payload["policies"].values():
                self.assertFalse(policy_payload["public_speedup_claim_authorized"])
                self.assertFalse(policy_payload["true_zero_copy_claim_authorized"])

    def test_report_states_timing_is_not_perf_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4198", text)
        self.assertIn("make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk", text)
        self.assertIn("Timing Boundary", text)
        self.assertIn("does not use them as", text)
        self.assertIn("performance evidence", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
