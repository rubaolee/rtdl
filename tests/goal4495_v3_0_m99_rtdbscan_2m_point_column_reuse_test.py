from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4495_m99_rtdbscan_2m_point_column_reuse.py"


class Goal4495M99RtDbscan2MPointColumnReuseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.comparisons = {row["protocol"]: row for row in cls.packet["comparisons"]}
        cls.rows = cls.packet["rows"]

    def test_packet_extends_point_column_reuse_to_2m_road3d(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.rtdbscan_2m_point_column_reuse.goal4495.v1",
            self.packet["version"],
        )
        self.assertEqual("road3d", self.packet["dataset"])
        self.assertEqual(2_097_152, self.packet["point_count"])
        self.assertEqual(5, self.packet["case_count"])
        self.assertEqual(5, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())
        self.assertTrue(self.packet["summary"]["primitive_signatures_match"])
        self.assertTrue(self.packet["summary"]["all_app_signatures_match"])
        self.assertGreater(
            self.packet["summary"]["primitive_prepare_speedup_if_columns_already_owned"],
            40.0,
        )
        self.assertGreater(
            self.packet["summary"]["primitive_prepare_phase_speedup_if_columns_already_owned"],
            40.0,
        )

    def test_app_mode_keeps_charged_column_boundary(self) -> None:
        one_shot = self.comparisons["one_shot"]
        warm = self.comparisons["warm_replay"]

        self.assertGreater(one_shot["row_prepare_speedup_if_columns_already_owned"], 60.0)
        self.assertGreater(warm["row_prepare_speedup_if_columns_already_owned"], 70.0)
        self.assertLess(one_shot["row_prepare_speedup_vs_charged_columns"], 1.0)
        self.assertGreater(warm["row_prepare_speedup_vs_charged_columns"], 1.0)
        self.assertLess(one_shot["prepare_plus_replay_speedup_vs_charged_columns"], 1.03)
        self.assertGreater(one_shot["prepare_plus_replay_speedup_vs_charged_columns"], 1.0)
        self.assertLess(warm["prepare_plus_replay_speedup_vs_charged_columns"], 1.0)
        self.assertGreater(warm["prepare_plus_replay_speedup_vs_charged_columns"], 0.99)
        for row in self.comparisons.values():
            self.assertEqual("reuse_columns_only", row["decision"])
            self.assertTrue(row["signatures_match"])
            self.assertGreater(row["column_coordinate_build_sec"], row["column_handle_prepare_sec"])

        boundary = self.packet["claim_boundary"]
        self.assertTrue(boundary["caller_owned_column_speedup_requires_existing_device_columns"])
        self.assertTrue(boundary["point_column_build_charged_when_app_constructs_columns"])
        self.assertFalse(boundary["route_promotion_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])

    def test_report_index_guidance_and_script_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4495", report)
        self.assertIn("2,097,152", report)
        self.assertIn("true-zero-copy", report)
        self.assertIn("Goal4495 RT-DBSCAN 2M point-column reuse", index)
        self.assertIn("POINT_COUNT = 2_097_152", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4504.v1", route["version"])
        self.assertIn("Goal4495", route["evidence_refs"])
        self.assertIn("2M `road3d`", route["next_runtime_action"])
        self.assertIn(
            "promoting temporary app-constructed point columns",
            " ".join(route["rejected_or_unpromoted_candidates"]),
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4504.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4495", adequacy["evidence_refs"])
        self.assertIn("2M `road3d`", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
