from __future__ import annotations

import pathlib
import unittest

from scripts.goal1908_v2_local_preflight import TEST_MODULES


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1908_v2_local_preflight_2026-05-13.md"


class Goal1908V2LocalPreflightTest(unittest.TestCase):
    def test_preflight_includes_current_non_pod_gate_tests(self) -> None:
        modules = set(TEST_MODULES)

        for module in (
            "tests.goal1898_v2_package_install_gate_audit_test",
            "tests.goal1899_v2_strict_birth_gate_current_board_test",
            "tests.goal1900_partner_acceleration_boundary_doc_test",
            "tests.goal1902_v2_source_tree_only_release_exception_proposal_test",
            "tests.goal1903_v2_partner_pod_batch_packet_test",
            "tests.goal1904_gemini_review_goal1903_batch_packet_test",
            "tests.goal1905_v2_partner_pod_batch_acceptance_test",
            "tests.goal1906_public_v2_claim_boundary_scan_test",
            "tests.goal1907_gemini_review_v2_boundary_and_source_tree_test",
            "tests.goal1908_v2_local_preflight_test",
            "tests.goal1909_v2_release_packet_skeleton_test",
            "tests.goal1910_gemini_review_v2_release_skeleton_test",
            "tests.goal1911_v2_readiness_aggregator_test",
            "tests.goal1912_post_pod_external_review_template_test",
            "tests.goal1913_v2_pod_session_runbook_test",
            "tests.goal1935_gemini_review_goal1933_1934_large_scale_perf_test",
            "tests.goal1936_claude_review_goal1933_1935_large_scale_perf_test",
            "tests.goal1937_fixed_radius_repeat3_pod_perf_test",
        ):
            self.assertIn(module, modules)

    def test_script_runs_claim_scan_and_pre_pod_acceptance_snapshot(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal1906_public_v2_claim_boundary_scan.py", text)
        self.assertIn("goal1905_v2_partner_pod_batch_acceptance.py", text)
        self.assertIn("goal1911_v2_readiness_aggregator.py", text)
        self.assertIn("--allow-missing", text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("pod_evidence_collected", text)

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: active-local-gate", text)
        self.assertIn("one-command local preflight", text)
        self.assertIn("does not run hardware performance evidence", text)
        self.assertIn("authorize v2.0 release", text)


if __name__ == "__main__":
    unittest.main()
