from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4489M93DirectStatusPointColumnsPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = [row for row in cls.packet["rows"] if row.get("status") == "ok"]

    def test_packet_completed_and_preserves_signatures(self) -> None:
        self.assertEqual("rtdl.v3_0.direct_status_point_columns.goal4489.v1", self.packet["version"])
        self.assertEqual(1_048_576, self.packet["point_count"])
        self.assertEqual(3, self.packet["case_count"])
        self.assertEqual(3, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())
        self.assertTrue(self.packet["summary"]["all_signatures_match"])

    def test_column_prepare_speedups_are_claim_bounded(self) -> None:
        speedups = self.packet["summary"]["prepare_speedups_if_columns_already_owned"]
        self.assertGreater(speedups["clustered3d"], 100.0)
        self.assertGreater(speedups["road3d"], 75.0)
        self.assertGreater(speedups["ngsim_dense"], 10.0)
        self.assertIn("already owns", self.packet["claim_boundary"])
        for row in self.rows:
            self.assertGreater(row["point_column_build_sec"], row["column_prepare_sec"])
            self.assertTrue(row["column_prepare_metadata"]["point_coordinate_upload_avoided"])
            self.assertFalse(row["row_prepare_metadata"]["point_coordinate_upload_avoided"])

    def test_report_index_and_current_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4489", report)
        self.assertIn("caller-owned", report)
        self.assertIn("Goal4489 RT-DBSCAN direct-status caller-owned point columns", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4497.v1", route["version"])
        self.assertIn("Goal4489", route["evidence_refs"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4497.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4489", adequacy["evidence_refs"])
        self.assertIn("already own partner columns", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
