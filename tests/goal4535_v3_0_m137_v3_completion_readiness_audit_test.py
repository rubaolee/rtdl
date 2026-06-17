from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4535V30M137CompletionReadinessAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4535_m137_v3_completion_readiness_audit")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.completion_readiness_audit.goal4535.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_queue_shape_is_completion_ready(self) -> None:
        summary = self.packet["summary"]
        self.assertEqual((), tuple(summary["runtime_build_queue"]))
        self.assertEqual((), tuple(summary["claim_or_evidence_queue"]))
        self.assertEqual((), tuple(summary["design_blocker_queue"]))
        self.assertEqual(
            ("barnes_hut", "triangle_counting"),
            tuple(summary["future_design_target_queue"]),
        )
        self.assertEqual(8, len(summary["closed_current_targets"]))

    def test_current_docs_have_no_stale_queue_wording(self) -> None:
        self.assertEqual({}, self.packet["stale_current_pattern_hits"])
        self.assertGreaterEqual(len(self.packet["audited_files"]), 10)

    def test_report_index_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4535 / V3 M137", report)
        self.assertIn("Goal4535 V3 completion readiness audit", index)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
