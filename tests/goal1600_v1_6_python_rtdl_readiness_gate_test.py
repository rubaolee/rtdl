from pathlib import Path
import unittest

from rtdsl.v1_6_python_rtdl_readiness import (
    V1_6_PYTHON_RTDL_BLOCKED_CLAIMS,
    validate_v1_6_python_rtdl_readiness_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal1599_v1_6_readiness_3ai_consensus_2026-05-09.md"


class Goal1600V16PythonRtdlReadinessGateTest(unittest.TestCase):
    def test_gate_validates_boundary_and_artifacts(self):
        gate = validate_v1_6_python_rtdl_readiness_gate(repo_root=ROOT)
        self.assertEqual("planning_boundary_accepted_not_release_ready", gate["status"])
        self.assertEqual(("embree", "optix"), tuple(gate["supported_backends"]))
        self.assertIn("COLLECT_K_BOUNDED", gate["pending_primitives"])
        self.assertNotIn("COLLECT_K_BOUNDED", gate["stable_primitives"])
        self.assertEqual((), tuple(gate["missing_artifacts"]))

    def test_gate_keeps_public_claims_blocked(self):
        gate = validate_v1_6_python_rtdl_readiness_gate(repo_root=ROOT)
        for flag in [
            "release_ready",
            "public_release_authorized",
            "release_tag_action_authorized",
            "stable_collect_k_bounded_promotion_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rtx_or_gpu_acceleration_claim_authorized",
            "true_zero_copy_wording_authorized",
            "partner_tensor_handoff_authorized",
            "package_install_support_authorized",
        ]:
            self.assertIs(gate[flag], False)
        self.assertEqual(V1_6_PYTHON_RTDL_BLOCKED_CLAIMS, tuple(gate["blocked_claims"]))

    def test_gate_names_all_required_closure_work(self):
        gate = validate_v1_6_python_rtdl_readiness_gate(repo_root=ROOT)
        for required in [
            "formal_v1_6_release_surface_proposal",
            "public_docs_overclaim_audit",
            "stable_native_path_app_leakage_audit",
            "blocked_claim_regression_tests",
            "windows_linux_source_tree_validation",
            "real_nvidia_optix_validation_for_claimed_surface",
            "three_ai_consensus",
        ]:
            self.assertIn(required, gate["required_closure_gates"])

    def test_report_and_consensus_preserve_do_not_publish_boundary(self):
        report_text = " ".join(REPORT.read_text(encoding="utf-8").split())
        consensus_text = " ".join(CONSENSUS.read_text(encoding="utf-8").split())
        for phrase in [
            "current `main` is not ready to publish",
            "does not take responsibility for optimizing arbitrary user Python code",
            "whole-app speedup",
            "true zero-copy",
            "partner tensor handoff",
            "Proceed toward `v1.6`, but do not publish it yet",
        ]:
            self.assertIn(phrase, report_text)
        for phrase in [
            "does not authorize a `v1.6` release",
            "public speedup wording",
            "true zero-copy wording",
            "partner support claims",
            "Do not publish `v1.6` yet",
        ]:
            self.assertIn(phrase, consensus_text)


if __name__ == "__main__":
    unittest.main()
