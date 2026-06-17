from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4488M92RtdbscanDirectStatusRowColumnizationPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = [row for row in cls.packet["rows"] if row.get("status") == "ok"]

    def test_packet_completed_and_preserves_signatures(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.rtdbscan_direct_status_row_columnization.goal4488.v1",
            self.packet["version"],
        )
        self.assertEqual(1_048_576, self.packet["point_count"])
        self.assertEqual(6, self.packet["case_count"])
        self.assertEqual(6, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())
        self.assertTrue(self.packet["summary"]["all_signatures_match_between_diagnostic_and_production"])

    def test_fast_coordinate_source_and_prepare_speedups_are_recorded(self) -> None:
        for row in self.rows:
            metadata = row["direct_status_prepare_metadata"]
            self.assertEqual("attribute_xyz_rows_direct", metadata["point_coordinate_host_extraction"])
            self.assertTrue(metadata["point_coordinate_host_intermediate_tuple_avoided"])

        comparison = self.packet["summary"]["m92_vs_m91"]
        self.assertGreater(comparison["clustered3d"]["diagnostic_phase_total_speedup"], 2.0)
        self.assertGreater(comparison["road3d"]["diagnostic_phase_total_speedup"], 2.3)
        self.assertGreater(comparison["ngsim_dense"]["diagnostic_phase_total_speedup"], 1.9)
        self.assertGreater(comparison["road3d"]["production_prepare_speedup"], 2.0)
        self.assertGreater(comparison["ngsim_dense"]["production_prepare_speedup"], 2.0)

    def test_report_index_and_current_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4488", report)
        self.assertIn("row-columnization", report)
        self.assertIn("Goal4488 RT-DBSCAN direct-status row-columnization", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4489.v1", route["version"])
        self.assertIn("Goal4488", route["evidence_refs"])
        self.assertIn("Goal4489", route["evidence_refs"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4489.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4488", adequacy["evidence_refs"])
        self.assertIn("Goal4489", adequacy["evidence_refs"])
        self.assertIn("shared device-coordinate-column", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
