import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m68_next_set_a_family_selection.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m68_next_set_a_family_selection_2026-06-23.json"
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m68_next_set_a_family_selection_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT / "docs" / "reviews" / "call_for_review_phoenix_v3_m68_next_set_a_family_selection_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT / "docs" / "reviews" / "claude_phoenix_v3_m68_next_set_a_family_selection_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m68_next_set_a_family_selection_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m68_next_set_a_family_selection_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m68_goal_completion_audit_2026-06-23.md"


class V3PhoenixM68NextSetAFamilySelectionGateTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_m68_selects_rtnn_without_authorizing_execution(self) -> None:
        payload = self.load()

        self.assertEqual(
            payload["status"],
            "m68_next_set_a_family_selection_ready_for_external_review_no_pod_no_release",
        )
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertEqual(
            payload["summary"]["selected_family_id"],
            "fixed_radius_ranked_summary_3d_prepared_session",
        )
        self.assertEqual(payload["summary"]["selected_pressure_app"], "rtnn")
        self.assertEqual(payload["summary"]["selected_next_goal"], "M69")
        self.assertFalse(payload["summary"]["pod_authorized"])
        self.assertFalse(payload["summary"]["all_app_authorized"])
        self.assertFalse(payload["summary"]["release_authorized"])
        for value in payload["non_authorization"].values():
            self.assertFalse(value)

    def test_candidate_table_excludes_recent_wrong_paths(self) -> None:
        candidates = {row["pressure_app"]: row for row in self.load()["candidates"]}

        self.assertEqual(candidates["barnes_hut"]["rank"], "excluded_currently")
        self.assertIn("M67", candidates["barnes_hut"]["reason"])
        self.assertEqual(candidates["spatial_rayjoin"]["rank"], "excluded_currently")
        self.assertIn("M66", candidates["spatial_rayjoin"]["reason"])
        self.assertEqual(candidates["hausdorff_xhd"]["rank"], "defer")
        self.assertGreater(candidates["hausdorff_xhd"]["set_a_app_geomean"], 1.05)
        self.assertEqual(candidates["rtnn"]["rank"], "selected")
        self.assertLess(candidates["rtnn"]["set_a_app_geomean"], 1.05)

    def test_rtnn_selection_records_material_signal_and_hot_boundary(self) -> None:
        selected = self.load()["selected_family"]

        self.assertTrue(selected["source_surface"]["helper_present"])
        self.assertTrue(selected["source_surface"]["helper_generic_contract_present"])
        self.assertTrue(selected["source_surface"]["helper_body_has_no_rtnn_name"])
        self.assertTrue(selected["evidence"]["runtime_trunk_executes_end_to_end"])
        self.assertTrue(selected["evidence"]["internal_device_residency_between_rtdl_phases"])
        self.assertGreaterEqual(selected["evidence"]["runner_vs_legacy_runner_wall_speedup"], 1.20)
        self.assertLess(selected["evidence"]["runner_vs_legacy_hot_speedup"], 1.0)
        self.assertGreater(selected["evidence"]["input_load_pack_consolidation_sec"], 0.0)
        self.assertGreater(selected["evidence"]["runner_after_input_load_pack_sec"], 0.0)
        self.assertTrue(selected["evidence"]["signature_match_runner_vs_legacy"])
        self.assertTrue(selected["evidence"]["signature_match_runner_vs_cupy"])

        stop_text = " ".join(self.load()["next_work"]["stop_conditions"])
        self.assertIn("input-loading/packing consolidation", stop_text)
        self.assertIn("ranked-summary phase compression", stop_text)

    def test_report_and_call_for_review_preserve_boundaries(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            self.assertIn("M68", text)
            self.assertIn("RTNN", text)
            self.assertIn("no all-app", normalized)
            self.assertIn("no POD", normalized)
            self.assertIn("no public speedup", normalized)
            self.assertIn("no broad V3-over-V2", normalized)
            self.assertIn("no route-specific RTNN app tuning", normalized)
            self.assertNotIn("release_ready", text)

        call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        for verdict in (
            "accept_m68_select_rtnn_ranked_summary_for_m69_local_audit_no_pod_no_release",
            "accept_m68_selection_shape_but_change_next_family_before_m69",
            "blocked_m68_needs_local_fix_before_next_family_decision",
            "reject_m68_selection_repeats_leaf_first_error",
        ):
            self.assertIn(verdict, call)

    def test_external_reviews_and_consensus_accept_without_authorization(self) -> None:
        verdict = "accept_m68_select_rtnn_ranked_summary_for_m69_local_audit_no_pod_no_release"
        for path in (CLAUDE_REVIEW, ANTIGRAVITY_REVIEW, CONSENSUS, AUDIT):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            self.assertIn(verdict, text)
            self.assertTrue(
                "no V3 release" in normalized
                or ("does not authorize" in normalized and "V3 release" in normalized)
            )
            self.assertTrue(
                "no all-app" in normalized
                or ("does not authorize" in normalized and "all-app" in normalized)
            )
            self.assertTrue(
                "no POD" in normalized
                or ("does not authorize" in normalized and "POD" in normalized)
            )
            self.assertTrue(
                "no public speedup" in normalized
                or ("does not authorize" in normalized and "public speedup" in normalized)
            )
            self.assertTrue(
                "no broad V3-over-V2" in normalized
                or ("does not authorize" in normalized and "broad V3-over-V2" in normalized)
            )
            self.assertTrue(
                "no route-specific RTNN app tuning" in normalized
                or ("does not authorize" in normalized and "route-specific RTNN app tuning" in normalized)
            )
            self.assertNotIn("release_ready", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn(
            "m68_select_rtnn_ranked_summary_for_m69_local_audit_3ai_accept_no_pod_no_release",
            consensus,
        )
        self.assertIn("input-loading/packing consolidation", consensus)
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn(
            "m68_goal_complete_3ai_accept_select_rtnn_for_m69_local_audit_no_pod_no_release",
            audit,
        )

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
            self.assertIn("Phoenix V3 M68", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
