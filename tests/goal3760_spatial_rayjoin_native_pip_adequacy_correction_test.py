from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.v2_9_benchmark_adequacy import (
    V2_9_BENCHMARK_ADEQUACY_VERSION,
    validate_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3760_spatial_rayjoin_native_pip_adequacy_correction_2026-06-07.md"
CURRENT_REPORT = (
    ROOT / "docs" / "reports" / "goal3759_current_benchmark_adequacy_after_rt_dbscan_numba_repeat_2026-06-07.md"
)


class Goal3760SpatialRayjoinNativePipAdequacyCorrectionTest(unittest.TestCase):
    def test_matrix_records_native_pip_current_route_without_promoting_release_claims(self) -> None:
        self.assertEqual(V2_9_BENCHMARK_ADEQUACY_VERSION, "rtdl.v2_10.benchmark_adequacy_after_goal3785.v1")
        validation = validate_v2_9_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        rayjoin = rows["spatial_rayjoin"]
        self.assertEqual(rayjoin["adequacy"], "strong")
        self.assertIn("Goal3713", rayjoin["evidence_refs"])
        self.assertIn("Goal3761", rayjoin["evidence_refs"])
        self.assertIn("native-PIP", rayjoin["current_performance_reading"])
        self.assertIn("RTDL/OptiX resident", rayjoin["current_recommended_path"])
        self.assertIn("CuPy remains the dense CUDA-core baseline/opponent", rayjoin["current_partner_role"])
        self.assertNotIn("CuPy remains in the conservative PIP leg", rayjoin["current_partner_role"])
        self.assertFalse(rayjoin["public_speedup_claim_authorized"])
        self.assertFalse(rayjoin["paper_reproduction_claim_authorized"])

    def test_reports_explain_cross_size_boundary_and_current_native_pip_packet(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        current = CURRENT_REPORT.read_text(encoding="utf-8")
        for text in (report, current):
            self.assertIn("native-PIP", text)
            self.assertIn("CuPy", text)
            self.assertIn("does not authorize", text)
        self.assertIn("older cross-size", report)
        self.assertIn("268.798x", report)
        self.assertIn("Goal3737", report)
        self.assertNotIn("CuPy remains in the conservative PIP leg", current)


if __name__ == "__main__":
    unittest.main()
