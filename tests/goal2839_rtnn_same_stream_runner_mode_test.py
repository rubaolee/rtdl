from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2839_rtnn_same_stream_runner_mode_2026-05-31.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2839_rtnn_same_stream_runner_pod" / "goal2839_summary.json"
POD_DETAIL = (
    ROOT
    / "docs"
    / "reports"
    / "goal2839_rtnn_same_stream_runner_pod"
    / "goal2839_same_stream_runner.json"
)
REVIEW = ROOT / "docs" / "reviews" / "goal2840_gemini_review_goal2839_rtnn_same_stream_runner_mode_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2840_goal2839_rtnn_same_stream_runner_mode_consensus_2026-05-31.md"


class Goal2839RtnnSameStreamRunnerModeTest(unittest.TestCase):
    def test_runner_exposes_explicit_same_stream_graph_result_mode(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        mode = "ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32"

        self.assertIn(mode, source)
        self.assertIn("replay_same_stream_device_partials_summary_cupy", source)
        self.assertIn("same_stream_entrypoint_metadata", source)
        self.assertIn("entrypoint_plan_status", source)
        self.assertIn("same_stream_partner_consumer", source)

    def test_pod_artifact_records_app_facing_entrypoint_metadata(self) -> None:
        summary = POD_SUMMARY.read_text(encoding="utf-8")
        detail = POD_DETAIL.read_text(encoding="utf-8")

        self.assertIn('"ok": true', summary)
        self.assertIn(
            '"result_mode": "ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32"',
            summary,
        )
        self.assertIn('"first_entrypoint_plan_status": "accepted_preview"', summary)
        self.assertIn('"first_entrypoint_resolved_partner": "cupy_conformance"', summary)
        self.assertIn('"first_entrypoint_fallback_required": false', summary)
        self.assertIn('"host_scalar_read_before_consumer": false', summary)
        self.assertIn('"public_speedup_claim_authorized": false', summary)

        self.assertIn('"same_stream_partner_consumer": true', detail)
        self.assertIn('"same_stream_entrypoint_metadata"', detail)
        self.assertIn('"producer_consumer_stream_ordering": "same_cuda_stream"', detail)

    def test_report_review_and_consensus_lock_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("app-facing result mode", report)
        self.assertIn("same-stream CuPy consumer", report)
        self.assertIn("not a public speedup claim", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("same-stream", review)
        self.assertIn("accepted_preview", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2839 with boundary", consensus)
        self.assertIn("App-facing result mode exposes planner metadata | accept", consensus)
        self.assertIn("Broad public performance/release claims | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()
