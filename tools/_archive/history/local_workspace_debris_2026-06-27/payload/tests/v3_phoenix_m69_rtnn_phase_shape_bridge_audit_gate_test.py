import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m69_rtnn_phase_shape_bridge_audit.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.json"
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT / "docs" / "reviews" / "claude_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m69_rtnn_phase_shape_bridge_audit_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m69_goal_completion_audit_2026-06-23.md"
SUPERSEDED_BLOCKED_REVIEW = (
    ROOT / "docs" / "reviews" / "external_review_blocked_phoenix_v3_m69_claude_session_limit_2026-06-23.md"
)


class V3PhoenixM69RtnnPhaseShapeBridgeAuditGateTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_m69_bridgeable_but_not_authorized(self) -> None:
        payload = self.load()

        self.assertEqual(
            payload["status"],
            "m69_rtnn_phase_shape_bridge_audit_ready_for_external_review_no_pod_no_release",
        )
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertEqual(payload["summary"]["bridge_status"], "bridgeable_but_not_runbook_authorized")
        self.assertFalse(payload["summary"]["runbook_authorized"])
        self.assertFalse(payload["summary"]["pod_authorized"])
        self.assertFalse(payload["summary"]["all_app_authorized"])
        self.assertFalse(payload["summary"]["release_authorized"])
        for value in payload["non_authorization"].values():
            self.assertFalse(value)

    def test_rtnn_all_app_shape_mapping_is_complete(self) -> None:
        payload = self.load()

        self.assertEqual(payload["summary"]["rtnn_row_count"], 14)
        self.assertEqual(payload["summary"]["rtnn_rows_below_1_05x"], 13)
        self.assertEqual(payload["summary"]["rtnn_shape_groups_below_1_05x"], 6)
        self.assertTrue(all(row["is_ranked_summary"] for row in payload["rtnn_all_app_rows"]))
        distributions = {row["distribution"] for row in payload["rtnn_all_app_rows"]}
        self.assertEqual(distributions, {"uniform", "clustered", "shell"})
        point_counts = {row["point_count"] for row in payload["rtnn_all_app_rows"]}
        self.assertEqual(point_counts, {65536, 262144})

    def test_phase_attribution_splits_packing_from_runner_phase(self) -> None:
        phase = self.load()["phase_attribution"]

        self.assertGreater(phase["total_runner_wall_delta_sec"], 0.8)
        self.assertAlmostEqual(phase["input_load_pack_share_of_delta"], 0.3229305393002245)
        self.assertAlmostEqual(phase["runner_after_input_pack_share_of_delta"], 0.6770928895191847)
        self.assertGreater(phase["runner_after_input_pack_delta_sec"], 0.5)
        self.assertGreater(phase["execution_prepare_delta_sec"], 0.3)
        self.assertLess(phase["hot_query_speedup_vs_legacy"], 1.0)
        self.assertTrue(phase["not_input_loading_packing_only"])
        self.assertTrue(phase["hot_query_is_not_the_material_source"])

    def test_source_surface_preserves_contract_boundaries(self) -> None:
        surface = self.load()["source_surface"]

        self.assertTrue(surface["front_door_uses_prepared_optix_ranked_summary"])
        self.assertTrue(surface["scale_profile_uses_prepared_optix_ranked_summary"])
        self.assertTrue(surface["app_prepared_execution_ranked_summary_mode_exists"])
        self.assertTrue(surface["app_productized_mode_calls_generic_helper"])
        self.assertTrue(surface["prepared_helper_generic_contract_present"])
        self.assertTrue(surface["prepared_execution_requires_full_batch_self_queries"])
        self.assertTrue(all(surface["distribution_support"].values()))
        self.assertTrue(surface["route_decision_separates_contracts"])
        required = " ".join(self.load()["bridge_decision"]["required_before_any_later_runbook"])
        stops = " ".join(self.load()["bridge_decision"]["stop_conditions"])
        self.assertIn("uniform distribution only", required)
        self.assertIn("per-distribution phase bounds", required)
        self.assertIn("full-batch self-query constraint", required)
        self.assertIn("clustered or shell", stops)
        self.assertIn("non-self-query batches", stops)

    def test_report_and_call_for_review_preserve_boundaries(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            self.assertIn("M69", text)
            self.assertIn("RTNN", text)
            self.assertIn("no all-app", normalized)
            self.assertIn("no POD", normalized)
            self.assertIn("no runbook", normalized)
            self.assertIn("no public speedup", normalized)
            self.assertIn("no broad V3-over-V2", normalized)
            self.assertIn("no route-specific RTNN app tuning", normalized)
            self.assertNotIn("release_ready", text)

        call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        for verdict in (
            "accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release",
            "accept_m69_bridge_shape_but_select_reserve_candidate_before_m70",
            "blocked_m69_needs_local_fix_before_bridge_decision",
            "reject_m69_rtnn_not_bridgeable_repeats_leaf_first_error",
        ):
            self.assertIn(verdict, call)

    def test_external_reviews_consensus_and_audit_accept_without_authorization(self) -> None:
        verdict = "accept_m69_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release"
        for path in (CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            normalized_lower = normalized.lower()
            self.assertIn(verdict, text)
            self.assertTrue(
                "no v3 release" in normalized_lower
                or ("does not authorize" in normalized_lower and "v3 release" in normalized_lower)
            )
            self.assertTrue(
                "no all-app" in normalized_lower
                or ("does not authorize" in normalized_lower and "all-app" in normalized_lower)
            )
            self.assertTrue(
                "no pod" in normalized_lower
                or ("does not authorize" in normalized_lower and "pod" in normalized_lower)
            )
            self.assertTrue(
                "no runbook" in normalized_lower
                or ("does not authorize" in normalized_lower and "runbook" in normalized_lower)
            )
            self.assertTrue(
                "no public speedup" in normalized_lower
                or ("does not authorize" in normalized_lower and "public speedup" in normalized_lower)
            )
            self.assertTrue(
                "no broad v3-over-v2" in normalized_lower
                or ("does not authorize" in normalized_lower and "broad v3-over-v2" in normalized_lower)
            )
            self.assertTrue(
                "no route-specific rtnn app tuning" in normalized_lower
                or ("does not authorize" in normalized_lower and "route-specific rtnn app tuning" in normalized_lower)
            )
            self.assertNotIn("release_ready", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn(
            "m69_rtnn_bridgeable_continue_m70_protocol_draft_3ai_accept_no_pod_no_release",
            consensus,
        )
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn(
            "m69_goal_complete_3ai_accept_rtnn_bridgeable_continue_m70_protocol_draft_no_pod_no_release",
            audit,
        )

        for text in (consensus, audit):
            normalized = " ".join(text.split())
            self.assertIn("uniform-distribution", normalized)
            self.assertIn("only", normalized)
            self.assertIn("full-batch self-queries", normalized)
            self.assertIn("0.988781x", normalized)

        blocked = SUPERSEDED_BLOCKED_REVIEW.read_text(encoding="utf-8")
        normalized_blocked = " ".join(blocked.split())
        self.assertIn("superseded_by_recorded_claude_m69_review", blocked)
        self.assertIn("must not be treated as open Claude review debt", normalized_blocked)

    def test_script_rebuilds_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
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
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("Phoenix V3 M69", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
