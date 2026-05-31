from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2845_v2_5_internal_readiness_refresh_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2846_gemini_review_goal2845_v2_5_internal_readiness_refresh_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2846_goal2845_v2_5_internal_readiness_refresh_consensus_2026-05-31.md"
GOAL2811_TEST = ROOT / "tests" / "goal2811_rtnn_direct_aggregate_kernel_test.py"


class Goal2845V25InternalReadinessRefreshTest(unittest.TestCase):
    def test_internal_readiness_packet_indexes_post_2808_hardening_chain(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(packet["core_validations"]["execution_path_policy"]["status"], "accept")
        for path in (
            "docs/reports/goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md",
            "docs/reports/goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md",
            "docs/reports/goal2839_rtnn_same_stream_runner_mode_2026-05-31.md",
            "docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md",
            "docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(packet["required_report_presence"][path])
        for path in (
            "docs/reviews/goal2836_gemini_review_goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md",
            "docs/reviews/goal2838_gemini_review_goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md",
            "docs/reviews/goal2840_gemini_review_goal2839_rtnn_same_stream_runner_mode_2026-05-31.md",
            "docs/reviews/goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md",
            "docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(packet["external_review_presence"][path])

    def test_goal2811_guard_tracks_current_device_pointer_contract(self) -> None:
        source = GOAL2811_TEST.read_text(encoding="utf-8")

        self.assertIn(
            "CUdeviceptr d_aggregate = prepared->d_ranked_aggregate->ptr",
            source,
        )
        self.assertIn('"&d_aggregate"', source)
        self.assertNotIn('"&d_aggregate.ptr"', source)

    def test_report_review_and_consensus_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2845", report)
        self.assertIn("Goal2835 through Goal2844", report)
        self.assertIn("execution_path_policy", report)
        self.assertIn("Goal2811 stale source-shape assertion", report)
        self.assertIn("does not authorize release", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("post-2808 hardening chain", review)
        self.assertIn("Goal2811", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2845 with boundary", consensus)
        self.assertIn("Post-2808 hardening chain indexed | accept", consensus)
        self.assertIn("Public/release claims | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()

