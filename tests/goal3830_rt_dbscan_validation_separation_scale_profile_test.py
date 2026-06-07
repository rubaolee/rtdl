from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3830_rt_dbscan_validation_separation_scale_profile_2026-06-07.md"
GOAL3826 = ROOT / "docs" / "reports" / "goal3826_scale_profile_calibration_a5000_2026-06-07.md"
GOAL3827 = ROOT / "docs" / "reports" / "goal3827_scale_profile_file_stdout_correction_a5000_2026-06-07.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3828_current_benchmark_scale_profiles_a5000" / "summary.json"


class Goal3830RtDbscanValidationSeparationScaleProfileTest(unittest.TestCase):
    def test_scale_registry_uses_large_no_validation_rt_dbscan_profile(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "rt_dbscan")
        self.assertEqual(row["row_id"], "rt_dbscan_optix_numba_scale_default_65536_no_validation")
        self.assertIn("65536", row["command"])
        self.assertIn("--no-validation", row["command"])
        self.assertIn("Goal3830", row["evidence_refs"])
        self.assertEqual(row["expected_runtime_class"], "default_scale_about_3s_no_validation")

    def test_prior_calibration_reports_are_corrected_not_rewritten(self) -> None:
        goal3826 = GOAL3826.read_text(encoding="utf-8")
        goal3827 = GOAL3827.read_text(encoding="utf-8")
        self.assertIn("validation-inclusive command", goal3826)
        self.assertIn("validation-inclusive command", goal3827)
        self.assertIn("Goal3830", goal3826)
        self.assertIn("Goal3830", goal3827)
        self.assertNotIn("real heavy timeout", goal3826)
        self.assertNotIn("real heavy timeout", goal3827)

    def test_report_records_validation_timing_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in (
            "Goal3830",
            "included CPU reference validation",
            "large scale-profile timing uses `--no-validation`",
            "point-count 65536",
            "elapsed_sec=2.429",
            "elapsed_sec=3.503",
            "matches_reference=null",
            "zero forbidden true claim flags",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)
        self.assertIn("does not weaken correctness requirements", normalized)

    def test_a5000_artifact_contains_65k_no_validation_scale_row(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        row = next(row for row in payload["rows"] if row["app"] == "rt_dbscan")
        self.assertEqual(row["row_id"], "rt_dbscan_optix_numba_scale_default_65536_no_validation")
        self.assertEqual(row["status"], "pass")
        self.assertLess(row["elapsed_sec"], 10.0)
        self.assertIn("--no-validation", row["command"])
        self.assertIn("65536", row["command"])
        self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])
        self.assertIn('"reference_signature": null', row["stdout_tail"])
        self.assertIn('"point_count": 65536', row["stdout_tail"])


if __name__ == "__main__":
    unittest.main()
