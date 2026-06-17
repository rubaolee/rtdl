from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_1m_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_1m_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4486V30M90RtdbscanSelfQueryCountThresholdTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = [row for row in cls.packet["rows"] if row.get("status") == "ok"]

    def test_packet_completed_and_preserves_signatures(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.rtdbscan_self_query_count_threshold_1m.goal4486.v1",
            self.packet["version"],
        )
        self.assertEqual(1_048_576, self.packet["point_count"])
        self.assertEqual(6, self.packet["case_count"])
        self.assertEqual(6, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())
        self.assertTrue(all(row["signature_matches_m89"] for row in self.rows))

    def test_self_query_metadata_is_present_on_all_rows(self) -> None:
        self.assertEqual(
            ["prepared_device_search_points_self_count_threshold_columns"],
            self.packet["summary"]["transfer_modes"],
        )
        self.assertEqual(
            ["prepared_search_points_self_query_device"],
            self.packet["summary"]["query_sources"],
        )
        self.assertTrue(self.packet["summary"]["host_query_upload_avoided_all"])
        for row in self.rows:
            metadata = row["metadata_focus"]
            self.assertEqual(
                "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
                metadata["threshold_adapter"],
            )
            self.assertEqual(
                "prepared_device_search_points_self_count_threshold_columns",
                metadata["threshold_transfer_mode"],
            )
            self.assertTrue(metadata["threshold_host_query_point_upload_avoided"])

    def test_one_shot_rows_improve_and_count_run_is_subsecond(self) -> None:
        one_shot = [row for row in self.rows if row["case"]["protocol"] == "one_shot_no_warmup"]
        self.assertEqual(3, len(one_shot))
        for row in one_shot:
            timing = row["metadata_focus"]["timing_breakdown_sec"]
            self.assertGreater(row["m90_vs_m89_speedup"], 1.0)
            self.assertLess(float(timing["optix_rt_count_threshold_sec"]), 0.5)

    def test_report_index_and_current_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4486", report)
        self.assertIn("self-query", report)
        self.assertIn("Do not overclaim the warmed-replay rows", report)
        self.assertIn("Goal4486 RT-DBSCAN self-query count-threshold optimization", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4486.v1", route["version"])
        self.assertIn("self-query", route["current_reader_decision"])
        self.assertIn("Goal4486", route["evidence_refs"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4486.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("self-query", adequacy["current_recommended_path"])
        self.assertIn("Goal4486", adequacy["evidence_refs"])


if __name__ == "__main__":
    unittest.main()
