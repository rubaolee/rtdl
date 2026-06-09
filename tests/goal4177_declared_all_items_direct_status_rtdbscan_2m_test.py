from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4177_declared_all_items_direct_status_rtdbscan_2m_2026-06-09.md"


class Goal4177DeclaredAllItemsDirectStatusRtDbscan2MPodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.rows = {row["label"]: row for row in cls.payload["rows"]}

    def test_artifact_records_environment_and_per_route_warmups(self) -> None:
        self.assertEqual(self.payload["goal"], "Goal4177")
        self.assertEqual(self.payload["source_commit"], "d9b9d60f605440f4c16e182f3ebd38ece0fa958e")
        self.assertIn("NVIDIA RTX 4000 Ada Generation", self.payload["gpu"])
        self.assertEqual(self.payload["point_count"], 2_097_152)
        self.assertEqual(self.payload["warmup_point_count"], 4096)
        self.assertEqual(
            self.payload["warmup_policy"],
            "per_route_small_input_warmup_before_large_measurement",
        )
        self.assertEqual(
            {row["label"] for row in self.payload["warmup_rows"]},
            {
                "warmup_current_grouped_stream_numba",
                "warmup_measured_alltrue_predicate_direct_status",
                "warmup_declared_all_items_direct_status",
            },
        )

    def test_declared_route_is_same_signature_and_uses_generic_all_items_contract(self) -> None:
        current = self.rows["current_grouped_stream_numba"]
        measured = self.rows["measured_alltrue_predicate_direct_status"]
        declared = self.rows["declared_all_items_direct_status"]
        self.assertEqual(declared["signature"], current["signature"])
        self.assertEqual(measured["signature"], current["signature"])
        self.assertTrue(declared["same_signature_as_current"])
        self.assertEqual(
            declared["signature"],
            {"cluster_sizes": {"1": 2_097_152}, "core_count": 2_097_152, "noise_count": 0},
        )
        self.assertFalse(declared["predicate_columns_materialized"])
        self.assertFalse(declared["rt_count_threshold_executed"])
        self.assertTrue(declared["uses_generic_all_items_direct_status_signature"])
        self.assertFalse(declared["rt_core_accelerated"])
        self.assertEqual(
            declared["native_engine_summary_contract"],
            "generic_all_items_direct_status_component_signature_wrapped_as_all_predicate_signature",
        )

    def test_measured_speedups_are_recorded_without_claim_authorization(self) -> None:
        current = self.rows["current_grouped_stream_numba"]
        measured = self.rows["measured_alltrue_predicate_direct_status"]
        declared = self.rows["declared_all_items_direct_status"]
        current_vs_declared = float(current["elapsed_sec"]) / float(declared["elapsed_sec"])
        measured_vs_declared = float(measured["elapsed_sec"]) / float(declared["elapsed_sec"])
        self.assertAlmostEqual(current_vs_declared, 1.7037499601567259, places=9)
        self.assertAlmostEqual(measured_vs_declared, 1.2687000547115994, places=9)
        self.assertAlmostEqual(
            self.payload["declared_speedup_vs_current_elapsed"],
            current_vs_declared,
            places=12,
        )
        for key in (
            "release_authorized",
            "paper_speedup_claim_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "native_abi_added",
        ):
            self.assertFalse(self.payload[key])

    def test_report_summarizes_timing_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted pod evidence; no automatic route promotion",
            "per-route 4,096-point warmup",
            "`34.321601`",
            "`25.557633`",
            "`20.144741`",
            "`1.704x`",
            "`1.269x`",
            "predicate_columns_materialized = false",
            "rt_count_threshold_executed = false",
            "uses_generic_all_items_direct_status_signature = true",
            "does not authorize release",
            "Mixed-predicate RT-DBSCAN rows remain on the\n"
            "grouped-stream Numba route",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
