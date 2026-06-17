from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4490M94RtDbscanPointColumnPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.comparisons = cls.packet["comparisons"]

    def test_packet_completed_two_protocols_and_preserves_signatures(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.rtdbscan_point_column_app_mode.goal4490.v1",
            self.packet["version"],
        )
        self.assertEqual(1_048_576, self.packet["point_count"])
        self.assertEqual(12, self.packet["case_count"])
        self.assertEqual(12, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertEqual(6, len(self.comparisons))
        self.assertTrue(JSONL.exists())
        self.assertTrue(self.packet["summary"]["all_signatures_match"])

    def test_charged_column_build_boundary_is_mixed_not_default_promoted(self) -> None:
        charged_prepare = [
            row["row_prepare_speedup_vs_charged_columns"] for row in self.comparisons
        ]
        already_owned = [
            row["row_prepare_speedup_if_columns_already_owned"] for row in self.comparisons
        ]
        charged_total = [
            row["prepare_plus_replay_speedup_vs_charged_columns"] for row in self.comparisons
        ]

        self.assertGreater(min(already_owned), 100.0)
        self.assertLess(min(charged_prepare), 1.0)
        self.assertGreater(max(charged_prepare), 1.4)
        self.assertLess(min(charged_total), 1.0)
        self.assertGreater(max(charged_total), 1.1)
        self.assertIn("charges app-constructed", self.packet["claim_boundary"])
        for row in self.comparisons:
            self.assertTrue(row["signatures_match"])
            self.assertGreater(row["column_coordinate_build_sec"], row["column_handle_prepare_sec"])

    def test_report_index_and_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4490", report)
        self.assertIn("app-constructed coordinate columns", report)
        self.assertIn("not promote the route as the default", report)
        self.assertIn("Goal4490 RT-DBSCAN point-column app mode", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4492.v1", route["version"])
        self.assertIn("Goal4490", route["evidence_refs"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4492.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4490", adequacy["evidence_refs"])
        self.assertIn("app-constructed columns", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
