from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4533_v3_0_m135_v3_claim_scope_closeout_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4533_v3_0_m135_v3_claim_scope_closeout_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4533V30M135ClaimScopeCloseoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4533_m135_v3_claim_scope_closeout")
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.claim_scope_closeout.goal4533.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_queue_is_design_only_after_claim_scope_closeout(self) -> None:
        summary = self.packet["summary"]
        self.assertEqual((), tuple(summary["runtime_build_queue"]))
        self.assertEqual((), tuple(summary["claim_or_evidence_queue"]))
        self.assertEqual((), tuple(summary["design_blocker_queue"]))
        self.assertEqual(
            ("barnes_hut",),
            tuple(summary["future_design_target_queue"]),
        )
        self.assertEqual(9, len(summary["closed_current_targets"]))
        self.assertIn("rtnn", summary["closed_current_targets"])
        self.assertIn("spatial_rayjoin", summary["closed_current_targets"])
        self.assertIn("triangle_counting", summary["closed_current_targets"])

    def test_rtnn_and_rayjoin_are_closed_without_claim_expansion(self) -> None:
        rows = self.packet["closed_claim_scoped_apps"]
        for app in ("rtnn", "spatial_rayjoin"):
            row = rows[app]
            self.assertEqual("closed_current_target", row["work_class"])
            self.assertIn("future optional claim-expansion", row["remaining_gap"])
            self.assertIn("no immediate V3 build target", row["next_build_target"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["broad_rt_core_claim_authorized"])
            self.assertFalse(row["paper_reproduction_claim_authorized"])
            self.assertFalse(row["automatic_partner_selection_authorized"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"])

    def test_report_index_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4533 / V3 M135", report)
        self.assertIn("Goal4533 V3 claim-scope closeout", index)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
