from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4524_m128_benchmark_implementation_queue.py"


class Goal4524V30M128BenchmarkImplementationQueueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4524_m128_benchmark_implementation_queue")
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["app"]: row for row in cls.packet["rows"]}

    def test_queue_validates_all_ten_apps_and_next_runtime_order(self) -> None:
        validation = rt.validate_v3_benchmark_implementation_queue()
        summary = cls_summary = self.packet["summary"]

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "rtdl.v3_0.benchmark_implementation_queue.goal4530.v4",
            self.packet["version"],
        )
        self.assertEqual(10, summary["app_count"])
        self.assertTrue(summary["all_ten_benchmark_apps_accounted_for"])
        self.assertEqual(
            ("triangle_counting",),
            tuple(summary["runtime_build_queue"]),
        )
        self.assertEqual(("barnes_hut",), tuple(summary["design_blocker_queue"]))
        self.assertEqual("triangle_counting", summary["next_runtime_build_target"])
        self.assertTrue(cls_summary["runtime_targets_need_pod"])

    def test_runtime_blockers_are_separate_from_claim_evidence_blockers(self) -> None:
        self.assertEqual("design_blocker", self.rows["barnes_hut"]["work_class"])
        self.assertIn("subtree-skip semantics", self.rows["barnes_hut"]["remaining_gap"])
        self.assertEqual("closed_current_target", self.rows["rt_dbscan"]["work_class"])
        self.assertIn("Goal4528 prepared graph", self.rows["rt_dbscan"]["remaining_gap"])
        self.assertEqual("runtime_blocker", self.rows["triangle_counting"]["work_class"])
        self.assertIn("weighted-summary graph capture", self.rows["triangle_counting"]["next_build_target"])

        self.assertEqual("claim_or_evidence_blocker", self.rows["rtnn"]["work_class"])
        self.assertIn("output-contract differences", self.rows["rtnn"]["remaining_gap"])
        self.assertEqual("claim_or_evidence_blocker", self.rows["spatial_rayjoin"]["work_class"])
        self.assertIn("8/8 overlay", self.rows["spatial_rayjoin"]["remaining_gap"])

    def test_closed_apps_have_no_current_runtime_build_target(self) -> None:
        closed = {
            "hausdorff_xhd",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "librts_spatial_index",
            "rt_dbscan",
        }
        for app in closed:
            row = self.rows[app]
            self.assertEqual("closed_current_target", row["work_class"], app)
            self.assertIsNone(row["priority"], app)
            self.assertIn("no immediate V3 build target", row["next_build_target"], app)

    def test_report_index_exports_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertTrue(hasattr(rt, "v3_benchmark_implementation_queue"))
        self.assertTrue(hasattr(rt, "validate_v3_benchmark_implementation_queue"))
        self.assertIn("Goal4524 / V3 M128", report)
        self.assertIn("Goal4524 benchmark implementation queue", index)
        self.assertIn("build_packet", script)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])


if __name__ == "__main__":
    unittest.main()
