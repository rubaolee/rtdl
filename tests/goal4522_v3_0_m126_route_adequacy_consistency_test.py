from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4522_v3_0_m126_route_adequacy_consistency_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4522_v3_0_m126_route_adequacy_consistency_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4522V30M126RouteAdequacyConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.route_adequacy_consistency.goal4522.v1", self.packet["version"])
        self.assertEqual([], self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_route_and_adequacy_registries_contain_m124_m125_boundaries(self) -> None:
        routes = {row["app"]: row for row in rt.current_benchmark_route_decisions()}
        adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}
        rt_dbscan_route = routes["rt_dbscan"]
        rt_dbscan_adequacy = adequacy["rt_dbscan"]
        triangle_route = routes["triangle_counting"]
        triangle_adequacy = adequacy["triangle_counting"]

        self.assertIn("Goal4519", rt_dbscan_route["evidence_refs"])
        self.assertIn("Goal4520", rt_dbscan_route["evidence_refs"])
        self.assertLess(len(rt_dbscan_route["current_reader_decision"]), 900)
        self.assertIn("prepared graph capture", rt_dbscan_route["current_reader_decision"])
        self.assertIn("live chunk-handle smoke", rt_dbscan_adequacy["next_generic_runtime_action"])
        self.assertIn("Goal4521", triangle_route["evidence_refs"])
        self.assertIn("Goal4521", triangle_adequacy["evidence_refs"])
        self.assertIn("key/count payloads", triangle_route["next_runtime_action"])
        self.assertIn("key/count payloads", triangle_adequacy["next_generic_runtime_action"])

    def test_report_index_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertIn("Goal4522 / V3 M126", report)
        self.assertIn("route_adequacy_consistency", report)
        self.assertIn("Goal4522 route-adequacy consistency", index)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])


if __name__ == "__main__":
    unittest.main()
