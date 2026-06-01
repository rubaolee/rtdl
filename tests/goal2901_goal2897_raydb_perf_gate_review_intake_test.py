import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2901_goal2897_raydb_perf_gate_review_intake_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2897_external_review_goal2896_raydb_same_contract_perf_gate_2026-05-31.md"


class Goal2901Goal2897RaydbPerfGateReviewIntakeTest(unittest.TestCase):
    def test_review_file_records_accept_with_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", text)
        self.assertIn("does NOT authorize v2.5 release", text)
        self.assertIn("Compiler Flag Alignment", text)
        self.assertIn("Multi-Vendor Verification", text)

    def test_readiness_packet_indexes_goal2897_review_and_intake_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        report_path = "docs/reports/goal2901_goal2897_raydb_perf_gate_review_intake_2026-05-31.md"
        review_path = "docs/reviews/goal2897_external_review_goal2896_raydb_same_contract_perf_gate_2026-05-31.md"

        self.assertEqual(validation["status"], "accept")
        self.assertTrue(packet["required_report_presence"][report_path])
        self.assertTrue(packet["external_review_presence"][review_path])
        self.assertIn("track_goal2897_compiler_flag_alignment_before_release_packet", packet["allowed_next_actions"])
        self.assertIn(
            "track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet",
            packet["allowed_next_actions"],
        )
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertIn("v2_5_release", packet["blocked_actions"])

    def test_intake_report_preserves_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2901", text)
        self.assertIn("accept-with-boundary", text)
        self.assertIn("not v2.5 release consensus", text)
        self.assertIn("compiler flag alignment", text)
        self.assertIn("another architecture/vendor check", text)


if __name__ == "__main__":
    unittest.main()
