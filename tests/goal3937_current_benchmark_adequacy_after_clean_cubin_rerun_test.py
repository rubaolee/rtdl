from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3937_current_benchmark_adequacy_after_clean_cubin_rerun_2026-06-08.md"


class Goal3937CurrentBenchmarkAdequacyAfterCleanCubinRerunTest(unittest.TestCase):
    def test_current_adequacy_version_and_validation_move_to_goal3936(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v2_10.benchmark_adequacy_after_goal3936.v1",
        )
        validation = rt.validate_current_benchmark_adequacy()
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        summary = rt.summarize_current_benchmark_adequacy()
        self.assertEqual(10, summary["app_count"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])

    def test_spatial_rayjoin_row_uses_clean_goal3936_mixed_route_evidence(self) -> None:
        spatial = {row["app"]: row for row in rt.current_benchmark_adequacy()}["spatial_rayjoin"]

        for ref in ("Goal3933", "Goal3934", "Goal3935", "Goal3936"):
            self.assertIn(ref, spatial["evidence_refs"])
        self.assertIn("clean pushed `main` checkout", spatial["current_performance_reading"])
        self.assertIn("source_dirty is empty", spatial["current_performance_reading"])
        self.assertIn("0.247x", spatial["current_performance_reading"])
        self.assertIn("0.155315ms/request", spatial["current_performance_reading"])
        self.assertIn("252.436x/202.372x", spatial["current_performance_reading"])
        self.assertIn("clean current representative confirmation", spatial["current_recommended_path"])
        self.assertIn("confirmed by Goal3936", spatial["next_generic_runtime_action"])
        self.assertFalse(spatial["automatic_partner_selection_authorized"])
        self.assertFalse(spatial["paper_reproduction_claim_authorized"])

    def test_spatial_rayjoin_scale_profile_indexes_goal3936(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_scale_profiles()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("Goal3936", spatial["evidence_refs"])
        self.assertTrue(spatial["requires_numba"])
        self.assertFalse(spatial["automatic_partner_selection_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])

    def test_report_records_project_level_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "project-level status update",
            "users choose partners explicitly",
            "primitive-first when a fused generic primitive wins",
            "Numba is the no-RawKernel reference partner",
            "does not authorize release action",
            "primitive/runtime level",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
