import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
ACCOUNTING = ROOT / "src" / "rtdsl" / "v3_0_topology_stream_accounting.py"
LEDGER_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json"
)
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m63_topology_stream_m3_phase_bridge_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m63_topology_stream_m3_phase_bridge_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_m63_topology_stream_m3_phase_bridge_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "antigravity_phoenix_v3_m63_topology_stream_m3_phase_bridge_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m63_topology_stream_m3_phase_bridge_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m63_goal_completion_audit_2026-06-23.md"


class V3PhoenixM63TopologyStreamM3PhaseBridgeGateTest(unittest.TestCase):
    def test_bridge_helper_is_generic_and_wired_to_both_families(self) -> None:
        source = PREPARED_EXECUTION.read_text(encoding="utf-8")
        helper_start = source.index("def _topology_stream_m3_bridge_metadata")
        point_start = source.index("def run_point_location_topology_stream_prepared_session")
        segment_start = source.index("def run_segment_intersection_topology_stream_prepared_session")
        grouped_start = source.index("def run_grouped_vector_sum_2d_prepared_session", segment_start)
        helper_body = source[helper_start:point_start]
        point_body = source[point_start:segment_start]
        segment_body = source[segment_start:grouped_start]

        self.assertNotIn("rayjoin", helper_body.lower())
        self.assertIn("build_topology_stream_m3_phase_table", helper_body)
        self.assertIn("build_topology_stream_prepared_handle_metadata", helper_body)
        self.assertIn("prepared_execution_to_topology_stream_m3_bridge_v1", helper_body)
        self.assertIn("_topology_stream_m3_bridge_metadata", point_body)
        self.assertIn("_topology_stream_m3_bridge_metadata", segment_body)

    def test_ledger_proves_complete_non_authorizing_bridge_for_both_families(self) -> None:
        payload = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

        self.assertEqual([], payload["failed_checks"])
        self.assertTrue(payload["checks"]["prepared_execution_surface_present"])
        for prefix in ("point_location", "segment_intersection"):
            self.assertTrue(
                payload["current_surface"][f"{prefix}_m3_bridge_contract_metadata_value"]
            )
            self.assertTrue(
                payload["current_surface"][f"{prefix}_m3_bridge_complete_metadata_value"]
            )
            metadata = payload["current_surface_probe_metadata"][prefix]
            self.assertEqual(
                metadata["prepared_execution_to_topology_stream_m3_bridge_contract"],
                "prepared_execution_to_topology_stream_m3_bridge_v1",
            )
            self.assertEqual(
                metadata["prepared_execution_to_topology_stream_m3_bridge_status"],
                "complete_non_authorizing_m3_bridge",
            )
            self.assertTrue(metadata["topology_stream_m3_phase_table_complete"])
            self.assertEqual(metadata["topology_stream_m3_missing_phases_for_public_row"], [])
            for phase in (
                "static_scene_prepare_sec",
                "query_stream_prepare_sec",
                "device_transfer_or_residency_sec",
                "rt_traversal_sec",
                "topology_continuation_sec",
                "host_return_or_scalar_materialization_sec",
            ):
                self.assertIn(phase, metadata["topology_stream_m3_phase_seconds"])
            self.assertIs(metadata["true_zero_copy_claim_authorized"], False)
            self.assertIs(metadata["v4_embedding_or_external_zero_copy_authorized"], False)

    def test_accounting_sentinel_comment_and_boundaries_are_present(self) -> None:
        text = ACCOUNTING.read_text(encoding="utf-8")
        self.assertIn("prepared-query marker plus no download timings", text)
        self.assertIn("topology stream M3 table cannot authorize public speedup", text)
        self.assertIn("topology stream prepared handle cannot authorize", text)

    def test_m63_reviews_and_consensus_accept_without_authorization(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            self.assertIn(
                "accept_m63_topology_stream_m3_phase_bridge_continue_local_step2_no_pod_no_release",
                text,
            )
            self.assertIn("V3 release", text)
            self.assertIn("all-app", text)
            self.assertIn("paid POD", text)
            self.assertIn("public speedup", text)
            self.assertIn("true-zero-copy", text)
            self.assertIn("V4", text)
            self.assertNotIn("release_ready", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn(
            "m63_topology_stream_m3_phase_bridge_3ai_accept_continue_local_step2_no_pod_no_release",
            consensus,
        )
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("m63_goal_complete_3ai_accept_continue_local_step2_no_pod_no_release", audit)


if __name__ == "__main__":
    unittest.main()
