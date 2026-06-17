from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4536V30M138InternalCompletionPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4536_m138_v3_internal_completion_packet")
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.internal_completion_packet.goal4536.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_app_matrix_covers_all_ten_apps(self) -> None:
        rows = {row["app"]: row for row in self.packet["app_rows"]}
        self.assertEqual(10, len(rows))
        self.assertEqual(
            {
                "barnes_hut",
                "contact_manifold",
                "hausdorff_xhd",
                "librts_spatial_index",
                "raydb_style",
                "robot_collision",
                "rt_dbscan",
                "rtnn",
                "spatial_rayjoin",
                "triangle_counting",
            },
            set(rows),
        )
        self.assertEqual("closed_current_target", rows["barnes_hut"]["queue_class"])
        self.assertIn("Goal4541", rows["barnes_hut"]["evidence_refs"])
        self.assertEqual("closed_current_target", rows["triangle_counting"]["queue_class"])
        self.assertIn("non-graph stream", rows["triangle_counting"]["remaining_gap"])
        self.assertEqual("closed_current_target", rows["rtnn"]["queue_class"])

    def test_claims_remain_blocked_for_every_app(self) -> None:
        for row in self.packet["app_rows"]:
            self.assertFalse(row["public_speedup_claim_authorized"], row["app"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["app"])
            self.assertFalse(row["paper_reproduction_claim_authorized"], row["app"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["app"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["app"])

    def test_report_index_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4536 / V3 M138", report)
        self.assertIn("Goal4536 V3 internal completion packet", index)
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
