from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4542_v3_0_m143_post_closure_surface_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4542_v3_0_m143_post_closure_surface_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4542V30M143PostClosureSurfaceAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4542_m143_v3_post_closure_surface_audit")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_post_closure_audit_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.post_closure_surface_audit.goal4542.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_all_ten_apps_are_closed_and_queues_are_empty(self) -> None:
        summary = self.packet["summary"]
        self.assertEqual((), tuple(summary["runtime_build_queue"]))
        self.assertEqual((), tuple(summary["claim_or_evidence_queue"]))
        self.assertEqual((), tuple(summary["design_blocker_queue"]))
        self.assertEqual((), tuple(summary["future_design_target_queue"]))
        self.assertEqual(10, len(summary["closed_current_targets"]))
        self.assertIn("barnes_hut", summary["closed_current_targets"])
        self.assertIn("triangle_counting", summary["closed_current_targets"])

    def test_surface_scan_has_no_stale_post_closure_wording(self) -> None:
        self.assertGreaterEqual(self.packet["audited_file_count"], 20)
        self.assertEqual({}, self.packet["stale_post_closure_pattern_hits"])
        self.assertTrue(all(self.packet["goal4541_mentions"].values()))

    def test_report_index_and_claim_boundary_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4542 / V3 M143", report)
        self.assertIn("Goal4542 post-closure surface audit", index)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["rt_native_hierarchical_traversal_implemented"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
