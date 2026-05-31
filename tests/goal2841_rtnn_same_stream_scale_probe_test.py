from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2841_rtnn_same_stream_scale_probe_2026-05-31.md"
SUMMARY = ROOT / "docs" / "reports" / "goal2841_rtnn_same_stream_scale_pod" / "goal2841_summary.json"
DIRECT = ROOT / "docs" / "reports" / "goal2841_rtnn_same_stream_scale_pod" / "direct_graph_65536.json"
SAME = ROOT / "docs" / "reports" / "goal2841_rtnn_same_stream_scale_pod" / "same_stream_graph_65536.json"
REVIEW = ROOT / "docs" / "reviews" / "goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2842_goal2841_rtnn_same_stream_scale_probe_consensus_2026-05-31.md"


class Goal2841RtnnSameStreamScaleProbeTest(unittest.TestCase):
    def test_scale_artifacts_compare_direct_and_same_stream_modes(self) -> None:
        summary = SUMMARY.read_text(encoding="utf-8")
        direct = DIRECT.read_text(encoding="utf-8")
        same = SAME.read_text(encoding="utf-8")

        self.assertIn('"point_count": 65536', summary)
        self.assertIn('"direct_ok": true', summary)
        self.assertIn('"same_stream_ok": true', summary)
        self.assertIn('"mismatches": []', summary)
        self.assertIn('"entrypoint_plan_status": "accepted_preview"', summary)
        self.assertIn('"entrypoint_resolved_partner": "cupy_conformance"', summary)
        self.assertIn('"host_scalar_read_before_consumer": false', summary)
        self.assertIn('"public_speedup_claim_authorized": false', summary)

        self.assertIn('"result_mode": "ranked-summary-aggregate-prepared-query-batch-graph-float32"', direct)
        self.assertIn(
            '"result_mode": "ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32"',
            same,
        )
        self.assertIn('"same_stream_entrypoint_metadata"', same)

    def test_report_review_and_consensus_state_cost_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("65K", report)
        self.assertIn("1.923x", report)
        self.assertIn("traceability path, not a speedup path", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("same-stream", review)
        self.assertIn("avoids public speedup claims", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2841 with boundary", consensus)
        self.assertIn("Direct and same-stream summaries match | accept", consensus)
        self.assertIn("Public performance claim | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()
