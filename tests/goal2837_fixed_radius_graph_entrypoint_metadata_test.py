from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md"
POD_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal2837_fixed_radius_graph_entrypoint_metadata_pod"
    / "goal2837_summary.json"
)
REVIEW = ROOT / "docs" / "reviews" / "goal2838_gemini_review_goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2838_goal2837_fixed_radius_graph_entrypoint_metadata_consensus_2026-05-31.md"


class Goal2837FixedRadiusGraphEntrypointMetadataTest(unittest.TestCase):
    def test_runtime_wires_planner_metadata_into_same_stream_graph_api(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("describe_primitive_payload_partner_continuation_entrypoint", runtime)
        self.assertIn("primitive_payload_column_descriptors = (", runtime)
        self.assertIn("primitive_payload_continuation_entrypoint", runtime)
        self.assertIn("primitive_payload_continuation_plan", runtime)
        self.assertIn("primitive_payload_planner_fallback_required", runtime)
        self.assertIn("completed_same_stream_consumer", runtime)
        self.assertIn("hit_stream_grouped_ray_id_primitive_i64", runtime)
        self.assertIn("partner=\"cupy\"", runtime)

    def test_pod_artifact_records_accepted_preview_plan(self) -> None:
        summary = POD_SUMMARY.read_text(encoding="utf-8")

        self.assertIn('"ok": true', summary)
        self.assertIn('"entrypoint_plan_status": "accepted_preview"', summary)
        self.assertIn('"entrypoint_runtime_action": "execute_preview_with_explicit_descriptor_plan"', summary)
        self.assertIn('"entrypoint_resolved_partner": "cupy_conformance"', summary)
        self.assertIn('"entrypoint_fallback_required": false', summary)
        self.assertIn('"entrypoint_descriptor_count": 1', summary)
        self.assertIn('"host_scalar_read_before_consumer": false', summary)

    def test_report_review_and_consensus_lock_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("real same-stream graph API", report)
        self.assertIn("accepted_preview", report)
        self.assertIn("does not change native execution", report)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("accepted_preview", review)
        self.assertIn("does not authorize", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2837 with boundary", consensus)
        self.assertIn("Same-stream graph API carries planner metadata | accept", consensus)
        self.assertIn("Broad public performance/release claims | not authorized", consensus)


if __name__ == "__main__":
    unittest.main()
