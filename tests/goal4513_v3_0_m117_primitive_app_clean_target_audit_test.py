from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4513_m117_primitive_app_clean_target_audit.py"
READMES = {
    "robot_collision": ROOT / "examples/benchmark_apps/robot_collision/README.md",
    "contact_manifold": ROOT / "examples/benchmark_apps/contact_manifold/README.md",
    "raydb_style": ROOT / "examples/benchmark_apps/raydb_style/README.md",
    "librts_spatial_index": ROOT / "examples/benchmark_apps/librts_spatial_index/README.md",
    "hausdorff_xhd": ROOT / "examples/benchmark_apps/hausdorff_xhd/README.md",
}


class Goal4513V30M117PrimitiveAppCleanTargetAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4513_m117_primitive_app_clean_target_audit")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["app"]: row for row in cls.packet["rows"]}

    def test_packet_closes_five_primitive_or_no_partner_apps(self) -> None:
        summary = self.packet["summary"]

        self.assertEqual("rtdl.v3_0.primitive_app_clean_target_audit.goal4513.v1", self.packet["version"])
        self.assertEqual(5, summary["app_count"])
        self.assertEqual(
            {"robot_collision", "contact_manifold", "raydb_style", "librts_spatial_index", "hausdorff_xhd"},
            set(self.rows),
        )
        self.assertTrue(summary["all_internal_clean_targets_closed"])
        self.assertFalse(summary["all_m113_current_route_needed"])
        self.assertTrue(summary["all_public_speedup_claims_blocked"])
        self.assertTrue(summary["all_whole_app_speedup_claims_blocked"])
        self.assertTrue(summary["all_broad_rt_core_claims_blocked"])
        self.assertTrue(summary["all_automatic_partner_selection_blocked"])
        self.assertEqual(
            {"robot_collision", "contact_manifold", "librts_spatial_index"},
            set(summary["no_partner_needed_apps"]),
        )
        self.assertEqual({"raydb_style", "hausdorff_xhd"}, set(summary["primitive_only_apps"]))

    def test_per_app_route_reading_matches_current_registry(self) -> None:
        self.assertEqual("no_partner_needed", self.rows["robot_collision"]["decision_kind"])
        self.assertIn("grouped-segment any-hit", self.rows["robot_collision"]["primary_route"])
        self.assertEqual("no_partner_needed", self.rows["contact_manifold"]["decision_kind"])
        self.assertIn("bounded contact-witness", self.rows["contact_manifold"]["primary_route"])
        self.assertEqual("primitive_first", self.rows["raydb_style"]["decision_kind"])
        self.assertIn("grouped count/sum", self.rows["raydb_style"]["primary_route"])
        self.assertEqual("no_partner_needed", self.rows["librts_spatial_index"]["decision_kind"])
        self.assertIn("AABB spatial-index", self.rows["librts_spatial_index"]["primary_route"])
        self.assertEqual("primitive_first", self.rows["hausdorff_xhd"]["decision_kind"])
        self.assertIn("nearest-witness", self.rows["hausdorff_xhd"]["primary_route"])

        for app, row in self.rows.items():
            self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1", row["route_version"], app)
            self.assertFalse(row["m113_applicability"]["current_route_should_use_m113"], app)
            self.assertFalse(row["public_speedup_claim_authorized"], app)
            self.assertFalse(row["whole_app_speedup_claim_authorized"], app)
            self.assertFalse(row["automatic_partner_selection_authorized"], app)

    def test_report_readmes_index_and_script_capture_goal4513(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4513 / V3 M117", report)
        self.assertIn("RayJoin is intentionally excluded", report)
        self.assertIn("Goal4513 primitive app clean-target audit", index)
        self.assertIn("PACKET_VERSION", script)
        for app, path in READMES.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn("Goal4513", text, app)
            self.assertIn("M113 is not", text, app)


if __name__ == "__main__":
    unittest.main()
