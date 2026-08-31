from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3105_v2_7_internal_closeout_and_v2_8_runtime_gap_kickoff_2026-06-03.md"


class Goal3105V28BenchmarkRuntimeGapMapTest(unittest.TestCase):
    def test_v2_7_is_closed_as_internal_version(self) -> None:
        closeout = rt.v2_7_internal_closeout_status()

        self.assertEqual(closeout["status"], rt.V2_7_INTERNAL_CLOSEOUT_STATUS)
        self.assertTrue(closeout["d1_through_d8_closed"])
        self.assertTrue(closeout["d8_semantic_search_preview_only"])
        self.assertFalse(closeout["release_authorized"])
        self.assertFalse(closeout["public_speedup_claim_authorized"])
        self.assertFalse(closeout["rt_core_speedup_claim_authorized"])
        self.assertFalse(closeout["true_zero_copy_claim_authorized"])

    def test_gap_map_covers_ten_promoted_benchmark_apps(self) -> None:
        rows = rt.v2_8_benchmark_runtime_gap_matrix()
        apps = tuple(row["benchmark_app"] for row in rows)

        self.assertEqual(apps, rt.V2_8_PROMOTED_BENCHMARK_APPS)
        self.assertEqual(len(rows), 10)
        self.assertEqual(len(set(apps)), 10)
        for row in rows:
            with self.subTest(app=row["benchmark_app"]):
                self.assertTrue(row["current_bottleneck"])
                self.assertTrue(row["generic_runtime_target"])
                self.assertTrue(row["evidence_refs"])

    def test_first_runtime_target_is_shared_and_generic(self) -> None:
        summary = rt.v2_8_runtime_target_summary()

        self.assertEqual(summary["first_runtime_target"], rt.V2_8_FIRST_RUNTIME_TARGET)
        self.assertGreaterEqual(summary["first_target_app_count"], 7)
        for app in (
            "hausdorff_xhd",
            "spatial_rayjoin",
            "rt_dbscan",
            "raydb_style",
            "rtnn",
            "triangle_counting",
        ):
            with self.subTest(app=app):
                self.assertIn(app, summary["first_target_apps"])
        self.assertIn("user-defined shader injection", summary["not_first_target"])
        self.assertIn("v3.0", summary["v3_boundary"])

    def test_gap_map_preserves_claim_boundaries(self) -> None:
        validation = rt.validate_v2_8_benchmark_runtime_gap_map()
        rows = rt.v2_8_benchmark_runtime_gap_matrix()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])
        self.assertFalse(validation["rt_core_speedup_claim_authorized"])
        self.assertFalse(validation["true_zero_copy_claim_authorized"])
        for row in rows:
            with self.subTest(app=row["benchmark_app"]):
                self.assertFalse(row["app_specific_engine_logic_allowed"])
                self.assertFalse(row["automatic_partner_selection_allowed"])
                self.assertFalse(row["release_authorized"])
                self.assertFalse(row["public_speedup_claim_authorized"])
                self.assertFalse(row["rt_core_speedup_claim_authorized"])
                self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_report_records_closeout_and_v2_8_start(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("v2.7 is now closed as an internal version", text)
        self.assertIn("v2.8 moves back from metadata ergonomics to benchmark-runtime engineering", text)
        self.assertIn(rt.V2_8_FIRST_RUNTIME_TARGET, text)
        for app in (
            "Hausdorff / X-HD style",
            "Spatial RayJoin",
            "RT-DBSCAN",
            "Robot collision",
            "Contact manifold",
            "RayDB-style grouped aggregates",
            "Barnes-Hut / RT-BarnesHut style",
            "LibRTS-style spatial index",
            "RTNN neighbor search",
            "Triangle counting",
        ):
            with self.subTest(app=app):
                self.assertIn(app, text)
        for phrase in (
            "a v2.8 release",
            "public speedup wording",
            "broad RT-core wording",
            "true-zero-copy wording",
            "app-specific native engine behavior",
            "v3.0 lane",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
