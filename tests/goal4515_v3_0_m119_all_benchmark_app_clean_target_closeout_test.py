from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4515_m119_all_benchmark_app_clean_target_closeout.py"

EXPECTED_APPS = {
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "contact_manifold",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
}


class Goal4515V30M119AllBenchmarkAppCleanTargetCloseoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4515_m119_all_benchmark_app_clean_target_closeout"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["app"]: row for row in cls.packet["rows"]}

    def test_all_ten_benchmark_apps_have_closeout_reports(self) -> None:
        summary = self.packet["summary"]

        self.assertEqual(
            "rtdl.v3_0.all_benchmark_app_clean_target_closeout.goal4515.v1",
            self.packet["version"],
        )
        self.assertEqual(10, self.packet["app_count"])
        self.assertEqual(EXPECTED_APPS, set(self.rows))
        self.assertTrue(summary["all_ten_benchmark_apps_accounted_for"])
        self.assertTrue(summary["all_closeout_reports_exist"])
        self.assertTrue(summary["all_internal_clean_targets_closed"])
        self.assertTrue(summary["all_public_speedup_claims_blocked"])
        self.assertTrue(summary["all_whole_app_speedup_claims_blocked"])
        self.assertTrue(summary["all_broad_rt_core_claims_blocked"])
        self.assertTrue(summary["all_automatic_partner_selection_blocked"])
        self.assertTrue(summary["all_app_specific_native_engine_logic_blocked"])

    def test_closeout_goal_mapping_is_current(self) -> None:
        self.assertEqual("Goal4508", self.rows["rtnn"]["closeout_goal"])
        self.assertEqual("Goal4510", self.rows["rt_dbscan"]["closeout_goal"])
        self.assertEqual("Goal4511", self.rows["triangle_counting"]["closeout_goal"])
        self.assertEqual("Goal4512", self.rows["barnes_hut"]["closeout_goal"])
        self.assertEqual("Goal4514", self.rows["spatial_rayjoin"]["closeout_goal"])
        for app in (
            "hausdorff_xhd",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "librts_spatial_index",
        ):
            self.assertEqual("Goal4513", self.rows[app]["closeout_goal"], app)

        for app, row in self.rows.items():
            self.assertEqual(
                "rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1",
                row["route_version"],
                app,
            )
            self.assertTrue((ROOT / row["closeout_report"]).exists(), app)

    def test_decision_kind_groups_match_current_reader_state(self) -> None:
        groups = self.packet["summary"]["apps_by_decision_kind"]

        self.assertEqual(
            {"spatial_rayjoin", "rt_dbscan", "barnes_hut", "rtnn"},
            set(groups["mixed_explicit"]),
        )
        self.assertEqual(
            {"robot_collision", "contact_manifold", "librts_spatial_index"},
            set(groups["no_partner_needed"]),
        )
        self.assertEqual(
            {"hausdorff_xhd", "raydb_style", "triangle_counting"},
            set(groups["primitive_first"]),
        )

    def test_report_index_and_script_capture_goal4515(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4515 / V3 M119", report)
        self.assertIn("All ten benchmark apps are accounted for", report)
        self.assertIn("Goal4515 all benchmark app clean-target closeout", index)
        self.assertIn("PACKET_VERSION", script)
        self.assertNotIn("\\\\", json.dumps(self.checked_in))


if __name__ == "__main__":
    unittest.main()
