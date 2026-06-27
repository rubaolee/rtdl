import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
LEDGER_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json"
)
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m62_topology_stream_contract_gate_tightening_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m62_topology_stream_contract_gate_tightening_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_m62_topology_stream_contract_gate_tightening_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "antigravity_phoenix_v3_m62_topology_stream_contract_gate_tightening_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m62_topology_stream_contract_gate_tightening_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m62_goal_completion_audit_2026-06-23.md"


class V3PhoenixM62TopologyStreamContractGateTest(unittest.TestCase):
    def test_topology_stream_runner_bodies_explicitly_close_true_zero_copy(self) -> None:
        source = PREPARED_EXECUTION.read_text(encoding="utf-8")
        point_start = source.index("def run_point_location_topology_stream_prepared_session")
        segment_start = source.index("def run_segment_intersection_topology_stream_prepared_session")
        grouped_start = source.index("def run_grouped_vector_sum_2d_prepared_session", segment_start)
        point_body = source[point_start:segment_start]
        segment_body = source[segment_start:grouped_start]

        for body in (point_body, segment_body):
            self.assertIn('metadata["external_device_buffer_interop_authorized"] = False', body)
            self.assertIn('metadata["v4_embedding_or_external_zero_copy_authorized"] = False', body)
            self.assertIn('metadata["true_zero_copy_claim_authorized"] = False', body)

    def test_ledger_uses_stable_behavioral_probe_metadata(self) -> None:
        payload = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

        self.assertEqual([], payload["failed_checks"])
        self.assertTrue(payload["checks"]["prepared_execution_surface_present"])
        self.assertTrue(payload["checks"]["internal_delta_sanity_cap"])
        self.assertGreater(payload["internal_delta"]["wall_speedup_vs_default"], 1.0)
        self.assertLess(payload["internal_delta"]["wall_speedup_vs_default"], 10.0)

        for prefix in ("point_location", "segment_intersection"):
            metadata = payload["current_surface_probe_metadata"][prefix]
            self.assertIs(metadata["true_zero_copy_claim_authorized"], False)
            self.assertIs(metadata["external_device_buffer_interop_authorized"], False)
            self.assertIs(metadata["v4_embedding_or_external_zero_copy_authorized"], False)
            self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
            self.assertEqual(
                metadata["productized_execution_path"],
                "prepared_execution_session_runner",
            )
            self.assertNotIn("measured_median_sec", metadata)
            self.assertNotIn("outer_prepare_sec", metadata)
            self.assertNotIn("prepared_session", metadata)

    def test_m62_external_reviews_and_consensus_accept_without_authorization(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW, CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            self.assertIn(
                "accept_m62_local_gate_tightening_continue_step2_no_pod_no_release",
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
            "m62_local_gate_tightening_3ai_accept_continue_step2_no_pod_no_release",
            consensus,
        )
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("m62_goal_complete_3ai_accept_continue_step2_no_pod_no_release", audit)
        self.assertIn("The initial patch attempt was", audit)


if __name__ == "__main__":
    unittest.main()
