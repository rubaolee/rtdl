import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2898_raydb_perf_gate_readiness_integration_2026-05-31.md"


class Goal2898RaydbPerfGateReadinessIntegrationTest(unittest.TestCase):
    def test_raydb_migration_plan_uses_goal2896_as_current_decision_evidence(self) -> None:
        plan = rt.v2_5_triton_benchmark_app_migration_plan()
        validation = rt.validate_v2_5_triton_benchmark_app_migration_plan()
        apps = {app["app_id"]: app for app in plan["apps"]}
        raydb = apps["raydb_style"]

        self.assertEqual(validation["status"], "accept")
        self.assertIn("primitive_first", raydb["current_hot_path_partner"])
        self.assertIn("Goal2896", raydb["v2_5_status"])
        self.assertIn("Goal2896", raydb["first_port_action"])
        self.assertIn("22.58x-205.08x slower", raydb["notes"])
        self.assertFalse(raydb["auto_select_preview_partner_allowed"])
        self.assertEqual(raydb["measured_negative_preview_guidance_count"], 4)

    def test_raydb_tier_manifest_indexes_goal2896_same_contract_gate(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        validation = rt.validate_v2_5_tiered_benchmark_manifest()
        rows = {row["app_id"]: row for row in manifest["apps"]}
        raydb = rows["raydb_style"]

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(raydb["tier"], "A")
        self.assertIn("Goal2896", raydb["canonical_harness_status"])
        self.assertIn("Goal2896", raydb["same_contract_opponent"])
        self.assertIn("Goal2896", raydb["pod_evidence_status"])
        self.assertIn("Goal2896", raydb["next_action"])
        self.assertIn("typed hit-stream plus Triton alternative", raydb["same_contract_opponent"])

    def test_internal_readiness_indexes_goal2896_report_but_not_release(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        report_path = "docs/reports/goal2896_raydb_same_contract_performance_decision_gate_2026-05-31.md"

        self.assertEqual(validation["status"], "accept")
        self.assertTrue(packet["required_report_presence"][report_path])
        self.assertIn("triage_goal2897_external_review_for_goal2896_raydb_perf_gate", packet["allowed_next_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertIn("v2_5_release", packet["blocked_actions"])

    def test_report_documents_goal2896_integration_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2898", text)
        self.assertIn("Goal2896", text)
        self.assertIn("primitive-first", text)
        self.assertIn("not a release authorization", text)
        self.assertIn("external review remains required", text)


if __name__ == "__main__":
    unittest.main()
