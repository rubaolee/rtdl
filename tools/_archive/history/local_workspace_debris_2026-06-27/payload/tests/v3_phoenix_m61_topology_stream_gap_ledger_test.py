import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m61_topology_stream_gap_ledger.py"
LEDGER_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json"
)
LEDGER_MD = LEDGER_JSON.with_suffix(".md")
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.md"
)


class V3PhoenixM61TopologyStreamGapLedgerTest(unittest.TestCase):
    def load(self):
        return json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

    def test_m61_ledger_is_local_no_pod_not_release(self) -> None:
        payload = self.load()

        self.assertEqual(
            "m61_topology_stream_gap_ledger_ready_local_no_pod_not_release",
            payload["status"],
        )
        self.assertEqual("point_location_topology_stream", payload["selected_family"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["all_app_benchmark_authorized"])
        self.assertFalse(payload["paid_pod_spend_authorized"])
        self.assertFalse(payload["focused_pod_spend_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["v4_work_authorized"])
        self.assertEqual([], payload["failed_checks"])
        self.assertTrue(all(payload["checks"].values()))

    def test_internal_delta_is_labeled_not_public_row(self) -> None:
        delta = self.load()["internal_delta"]

        self.assertEqual("internal_routing_delta_not_public_row", delta["label"])
        self.assertGreater(delta["wall_speedup_vs_default"], 2.0)
        self.assertGreater(delta["wall_speedup_vs_default"], delta["sanity_min_exclusive"])
        self.assertLess(delta["wall_speedup_vs_default"], delta["sanity_max_exclusive"])
        self.assertTrue(delta["within_sanity_cap"])
        self.assertTrue(delta["counts_match"])
        self.assertFalse(delta["public_row_authorized"])
        self.assertFalse(delta["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(delta["true_zero_copy_claim_authorized"])

    def test_phase_bridge_records_prepared_report_to_m3_gap(self) -> None:
        bridge = self.load()["phase_bridge"]

        self.assertTrue(bridge["bridge_required"])
        self.assertNotEqual(
            bridge["prepared_execution_required_phases"],
            bridge["topology_stream_m3_required_phases"],
        )
        for phase in (
            "static_scene_prepare_sec",
            "query_stream_prepare_sec",
            "device_transfer_or_residency_sec",
            "rt_traversal_sec",
            "topology_continuation_sec",
            "host_return_or_scalar_materialization_sec",
        ):
            self.assertIn(phase, bridge["topology_stream_m3_required_phases"])

    def test_current_surface_and_fail_closed_runner_are_machine_checked(self) -> None:
        payload = self.load()

        self.assertTrue(all(payload["current_surface"].values()))
        self.assertTrue(all(payload["fail_closed_execution_surface"].values()))
        self.assertTrue(payload["checks"]["internal_delta_sanity_cap"])
        for prefix in ("point_location", "segment_intersection"):
            self.assertTrue(payload["current_surface"][f"{prefix}_runner_callable"])
            self.assertTrue(
                payload["current_surface"][
                    f"{prefix}_m3_phase_table_contract_metadata_value"
                ]
            )
            self.assertTrue(
                payload["current_surface"][
                    f"{prefix}_m3_bridge_contract_metadata_value"
                ]
            )
            self.assertTrue(
                payload["current_surface"][
                    f"{prefix}_m3_bridge_complete_metadata_value"
                ]
            )
            self.assertTrue(
                payload["current_surface"][
                    f"{prefix}_prepared_handle_contract_metadata_value"
                ]
            )
            self.assertTrue(payload["current_surface"][f"{prefix}_no_true_zero_copy_claim"])
            metadata = payload["current_surface_probe_metadata"][prefix]
            self.assertIs(metadata["true_zero_copy_claim_authorized"], False)
            self.assertIs(metadata["external_device_buffer_interop_authorized"], False)
            self.assertIs(metadata["v4_embedding_or_external_zero_copy_authorized"], False)
            self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
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
            self.assertIn("rt_traversal_sec", metadata["topology_stream_m3_phase_seconds"])
        self.assertIn("run M50", " ".join(payload["m61_next_contract"]["m61_must_not_do"]))
        self.assertIn(
            "define machine-readable prepared-handle/residency contract gaps",
            payload["m61_next_contract"]["m61_may_do"],
        )

    def test_markdown_records_boundaries_and_audit(self) -> None:
        text = LEDGER_MD.read_text(encoding="utf-8")
        for phrase in (
            "internal_routing_delta_not_public_row",
            "Bridge required: `true`",
            "no focused POD spend",
            "no RTDL-beats-RayJoin claim",
            "no true-zero-copy claim",
            "Was I foolish?",
            "No.",
        ):
            self.assertIn(phrase, text)

    def test_report_and_review_packet_preserve_boundaries(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            self.assertIn("internal_routing_delta_not_public_row", text)
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark run", text)
            self.assertIn("no paid POD spend", text)
            self.assertIn("no focused POD spend", text)
            self.assertIn("no public speedup wording", text)
            self.assertIn("no RTDL-beats-RayJoin claim", text)
            self.assertIn("no true-zero-copy claim", text)
            self.assertNotIn("release_ready", text)

    def test_m61_external_reviews_and_consensus_close_goal_not_run(self) -> None:
        claude = (
            ROOT
            / "docs"
            / "reviews"
            / "claude_phoenix_v3_m61_topology_stream_gap_ledger_recorded_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        antigravity = (
            ROOT
            / "docs"
            / "reviews"
            / "antigravity_phoenix_v3_m61_topology_stream_gap_ledger_review_2026-06-23.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reviews"
            / "codex_claude_antigravity_phoenix_v3_m61_topology_stream_gap_ledger_3ai_consensus_2026-06-23.md"
        ).read_text(encoding="utf-8")
        audit = (
            ROOT
            / "docs"
            / "reports"
            / "phoenix_v3_m61_goal_completion_audit_2026-06-23.md"
        ).read_text(encoding="utf-8")

        for text in (claude, antigravity, consensus, audit):
            self.assertIn("accept_m61_gap_ledger_continue_local_m62", text)
            self.assertIn("no V3 release", text)
            self.assertIn("no all-app benchmark", text)
            self.assertIn("no paid POD spend", text)
            self.assertIn("no true-zero-copy", text)
            self.assertNotIn("release_ready", text)

        self.assertIn("m61_gap_ledger_complete_continue_local_m62_no_pod_no_release", consensus)
        self.assertIn("true_zero_copy_claim_authorized=false", consensus)
        self.assertIn("m61_goal_complete_3ai_accept_continue_local_m62", audit)

    def test_script_rebuilds_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "ledger.json"
            md_out = Path(tmp) / "ledger.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("Phoenix V3 M61 Topology-Stream Gap Ledger", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
