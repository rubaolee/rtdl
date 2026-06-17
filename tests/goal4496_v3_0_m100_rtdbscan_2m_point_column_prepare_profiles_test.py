from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4496_m100_rtdbscan_2m_point_column_prepare_profiles.py"


class Goal4496M100RtDbscan2MPointColumnPrepareProfilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["dataset"]: row for row in cls.packet["rows"]}

    def test_packet_covers_non_road_2m_profiles(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.rtdbscan_2m_point_column_prepare_profiles.goal4496.v1",
            self.packet["version"],
        )
        self.assertEqual(2_097_152, self.packet["point_count"])
        self.assertEqual(["clustered3d", "ngsim_dense"], self.packet["datasets"])
        self.assertEqual(2, self.packet["case_count"])
        self.assertEqual(2, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())
        self.assertTrue(self.packet["summary"]["all_signatures_match"])

        self.assertGreater(
            self.rows["clustered3d"]["prepare_speedup_if_columns_already_owned"],
            120.0,
        )
        self.assertGreater(
            self.rows["ngsim_dense"]["prepare_speedup_if_columns_already_owned"],
            75.0,
        )
        self.assertGreater(
            self.rows["clustered3d"]["prepare_phase_speedup_if_columns_already_owned"],
            110.0,
        )
        self.assertGreater(
            self.rows["ngsim_dense"]["prepare_phase_speedup_if_columns_already_owned"],
            70.0,
        )

    def test_claim_boundary_keeps_prepare_profile_narrow(self) -> None:
        boundary = self.packet["claim_boundary"]
        self.assertTrue(boundary["caller_owned_column_speedup_requires_existing_device_columns"])
        self.assertTrue(boundary["point_column_build_reported_separately"])
        self.assertTrue(boundary["isolated_direct_status_prepare_only"])
        self.assertTrue(boundary["not_count_threshold_app_route"])
        self.assertFalse(boundary["route_promotion_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])

        for dataset, row in self.rows.items():
            self.assertTrue(row["signatures_match"], dataset)
            self.assertEqual(2_097_152, row["signature"]["point_count"], dataset)
            self.assertGreater(row["point_column_build_sec"], row["column_prepare_sec"], dataset)
            self.assertTrue(row["claim_boundary"]["not_count_threshold_app_route"], dataset)

    def test_report_index_guidance_and_script_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4496", report)
        self.assertIn("isolated direct-status prepare", report)
        self.assertIn("Goal4496 RT-DBSCAN 2M point-column prepare profiles", index)
        self.assertIn('DATASETS = ("clustered3d", "ngsim_dense")', script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4499.v1", route["version"])
        self.assertIn("Goal4496", route["evidence_refs"])
        self.assertIn("2M `clustered3d` and `ngsim_dense`", route["next_runtime_action"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4499.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4496", adequacy["evidence_refs"])
        self.assertIn("non-road3d 2M isolated direct-status prepare", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
