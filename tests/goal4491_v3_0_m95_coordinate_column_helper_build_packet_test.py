from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4491M95CoordinateColumnHelperBuildPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = cls.packet["rows"]

    def test_packet_completed_and_records_modest_speedup(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.coordinate_column_helper_build.goal4491.v1",
            self.packet["version"],
        )
        self.assertEqual(1_048_576, self.packet["point_count"])
        self.assertEqual(3, self.packet["case_count"])
        self.assertEqual(3, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())
        self.assertGreaterEqual(self.packet["summary"]["min_speedup"], 1.03)
        self.assertLess(self.packet["summary"]["max_speedup"], 1.20)
        self.assertIn("does not make app-constructed columns a default route", self.packet["claim_boundary"])

    def test_report_index_and_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4491", report)
        self.assertIn("redundant full-row", report)
        self.assertIn("Goal4491 coordinate-column helper build cleanup", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4504.v1", route["version"])
        self.assertIn("Goal4491", route["evidence_refs"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4504.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4491", adequacy["evidence_refs"])
        self.assertIn("no-promotion boundary", adequacy["current_performance_reading"])


if __name__ == "__main__":
    unittest.main()
