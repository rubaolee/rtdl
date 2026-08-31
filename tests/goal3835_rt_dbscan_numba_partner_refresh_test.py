from __future__ import annotations

import json
from pathlib import Path
import statistics
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_65K = ROOT / "docs" / "reports" / "goal3835_rt_dbscan_numba_partner_refresh_a5000" / "summary.json"
ARTIFACT_131K = ROOT / "docs" / "reports" / "goal3835_rt_dbscan_numba_partner_refresh_a5000_131k" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3835_rt_dbscan_numba_partner_refresh_2026-06-08.md"


class Goal3835RtDbscanNumbaPartnerRefreshTest(unittest.TestCase):
    def test_artifacts_record_numba_prepared_grid_wins_with_signature_parity(self) -> None:
        for path, point_count, repeat_count in (
            (ARTIFACT_65K, 65536, 10),
            (ARTIFACT_131K, 131072, 5),
        ):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["point_count"], point_count)
                self.assertEqual(payload["repeat_count"], repeat_count)
                self.assertTrue(payload["signatures_match"])
                self.assertFalse(payload["claim_boundary"]["paper_speedup_claim_authorized"])
                self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

                medians = _mode_medians(payload)
                self.assertGreater(
                    medians["partner_cupy_prepared_grid_components_3d"],
                    medians["partner_numba_prepared_grid_components_3d"],
                )
                self.assertGreater(
                    medians["optix_rt_core_flags_cupy_prepared_grid_components_3d"],
                    medians["optix_rt_core_flags_numba_prepared_grid_components_3d"],
                )

                numba_rows = [
                    row
                    for row in payload["rows"]
                    if row["mode"] == "optix_rt_core_flags_numba_prepared_grid_components_3d"
                ]
                self.assertTrue(numba_rows)
                for row in numba_rows:
                    self.assertTrue(row["rt_core_accelerated"])
                    self.assertFalse(row["raw_cuda_kernel_required"])
                    self.assertTrue(row["numba_cuda_jit_used"])

    def test_report_records_recommendation_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3835",
            "RTDL/OptiX fixed-radius core flags plus the prepared Numba grid",
            "Numba route exists",
            "faster than the comparable CuPy prepared-grid continuation",
            "not authorize",
            "automatic partner selection",
        ):
            self.assertIn(phrase, text)


def _mode_medians(payload: dict[str, object]) -> dict[str, float]:
    rows = payload["rows"]
    modes = sorted({row["mode"] for row in rows})
    return {
        mode: float(
            statistics.median(float(row["outer_elapsed_sec"]) for row in rows if row["mode"] == mode)
        )
        for mode in modes
    }


if __name__ == "__main__":
    unittest.main()
