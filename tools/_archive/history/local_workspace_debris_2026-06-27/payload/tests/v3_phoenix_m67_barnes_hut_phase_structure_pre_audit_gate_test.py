import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m67_barnes_hut_phase_structure_pre_audit.py"
PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.json"
)
REPORT = ROOT / "docs" / "reports" / "phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.md"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_2026-06-23.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_recorded_review_2026-06-23.md"
)
ANTIGRAVITY_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_review_2026-06-23.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_claude_antigravity_phoenix_v3_m67_barnes_hut_phase_structure_pre_audit_3ai_consensus_2026-06-23.md"
)
AUDIT = ROOT / "docs" / "reports" / "phoenix_v3_m67_goal_completion_audit_2026-06-23.md"


class V3PhoenixM67BarnesHutPhaseStructurePreAuditGateTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_m67_pre_audit_is_ready_for_review_not_authorization(self) -> None:
        payload = self.load()

        self.assertEqual(
            payload["status"],
            "m67_barnes_hut_phase_structure_pre_audit_ready_for_external_review_no_pod_no_release",
        )
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["decision"]["barnes_hut_should_be_current_coding_target"])
        self.assertFalse(payload["decision"]["pod_now_authorized"])
        self.assertFalse(payload["decision"]["all_app_now_authorized"])
        self.assertTrue(payload["summary"]["external_review_required_before_counting"])
        for value in payload["non_authorization"].values():
            self.assertFalse(value)

    def test_phase_structure_distinguishes_predecessor_from_current_control(self) -> None:
        phase = self.load()["phase_structure"]

        historical = phase["historical_predecessor"]
        current = phase["current_fused_control"]
        runner = phase["productized_runner"]

        self.assertTrue(historical["compressible_nonzero_phase_found"])
        self.assertGreater(historical["hot_speedup_geomean"], 12.0)
        self.assertFalse(current["new_compressible_phase_found"])
        self.assertTrue(current["runner_parity_with_existing_fused_partner"])
        self.assertGreaterEqual(current["runner_vs_control_geomean"], 0.98)
        self.assertTrue(runner["runtime_trunk_executes_end_to_end"])
        self.assertTrue(runner["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(runner["frontier_rows_materialized_on_host"])
        self.assertFalse(runner["contribution_rows_materialized_on_host"])

    def test_m45_m66_m29_reconciliation_is_recorded(self) -> None:
        payload = self.load()
        reconciliation = payload["reconciliation"]

        self.assertFalse(reconciliation["new_barnes_hut_app_tuning_allowed"])
        self.assertFalse(reconciliation["new_barnes_hut_runtime_coding_required_now"])
        self.assertTrue(reconciliation["external_review_required_before_counting_as_accepted_set_a_family"])
        self.assertEqual(
            payload["summary"]["m29_classification"],
            "v2_14_has_cpu_fused_or_typed_stream_only",
        )

    def test_report_and_call_for_review_preserve_boundaries(self) -> None:
        for path in (REPORT, CALL_FOR_REVIEW):
            text = path.read_text(encoding="utf-8")
            normalized = " ".join(text.split())
            self.assertIn("M67", text)
            self.assertTrue("no release" in normalized or "no V3 release" in normalized)
            self.assertIn("no all-app", normalized)
            self.assertIn("no POD", normalized)
            self.assertIn("no public speedup", normalized)
            self.assertIn("no broad V3-over-V2", normalized)
            self.assertIn("no true-zero-copy", normalized)
            self.assertNotIn("release_ready", text)

        call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        for verdict in (
            "accept_m67_count_barnes_hut_as_existing_step1_material_family_no_pod_no_release",
            "accept_m67_pre_audit_but_do_not_count_barnes_hut_select_next_family",
            "blocked_m67_needs_local_fix_before_decision",
            "reject_m67_barnes_hut_reopened_wrong_path",
        ):
            self.assertIn(verdict, call)

    def test_external_reviews_and_consensus_count_step1_without_authorization(self) -> None:
        verdict = "accept_m67_count_barnes_hut_as_existing_step1_material_family_no_pod_no_release"
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
                "no paid POD" in normalized
                or ("does not authorize" in normalized and "paid POD" in normalized)
            )
            self.assertTrue(
                "no focused POD" in normalized
                or ("does not authorize" in normalized and "focused POD" in normalized)
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
                "no watch-row closure" in normalized
                or ("does not authorize" in normalized and "watch-row closure" in normalized)
            )
            self.assertNotIn("release_ready", text)

        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn(
            "m67_count_barnes_hut_existing_step1_material_family_3ai_accept_no_pod_no_release",
            consensus,
        )
        self.assertIn("process-wall overhead", consensus)
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("m67_goal_complete_3ai_accept_count_barnes_hut_step1_material_no_pod_no_release", audit)
        self.assertIn("Next local work should select the next generic Set-A family", audit)

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
            self.assertIn("Phoenix V3 M67", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
