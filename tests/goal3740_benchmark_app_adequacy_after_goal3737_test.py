from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from rtdsl.v2_9_benchmark_adequacy import (
    validate_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
    summarize_v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3740_benchmark_app_adequacy_after_goal3737_2026-06-07.md"


class Goal3740BenchmarkAppAdequacyAfterGoal3737Test(unittest.TestCase):
    def test_matrix_covers_all_ten_promoted_benchmark_apps(self) -> None:
        rows = v2_9_benchmark_adequacy()
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertEqual(len(rows), len(V2_8_PROMOTED_BENCHMARK_APPS))

    def test_matrix_validates_and_blocks_public_claims(self) -> None:
        validation = validate_v2_9_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        for row in v2_9_benchmark_adequacy():
            for flag in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "broad_rt_core_claim_authorized",
                "true_zero_copy_claim_authorized",
                "paper_reproduction_claim_authorized",
                "automatic_partner_selection_authorized",
                "app_specific_native_engine_logic_allowed",
            ):
                self.assertFalse(row[flag], (row["app"], flag))

    def test_numba_reference_pressure_points_are_explicit(self) -> None:
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(set(summary["numba_reference_needed_apps"]), set())
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        self.assertIn("numba grid", rows["rt_dbscan"]["numba_reference_reason"].lower())
        self.assertIn("numba cuda jit", rows["barnes_hut"]["numba_reference_reason"].lower())
        self.assertIn("goal3749", rows["spatial_rayjoin"]["numba_reference_reason"].lower())

    def test_adequacy_summary_names_remaining_major_followup(self) -> None:
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["adequacy_counts"].get("needs_major_followup", 0), 0)
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        self.assertEqual(rows["barnes_hut"]["adequacy"], "adequate")
        self.assertEqual(rows["rt_dbscan"]["adequacy"], "adequate")
        self.assertEqual(rows["spatial_rayjoin"]["adequacy"], "strong")

    def test_report_is_reader_facing_and_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Benchmark-App Adequacy", text)
        self.assertIn("324.324x", text)
        self.assertIn("Numba Reference Scope", text)
        self.assertIn("AMD HIPRT Preparation Scope", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL-beats-RayJoin", text)


if __name__ == "__main__":
    unittest.main()
