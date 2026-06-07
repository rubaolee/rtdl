from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3826_scale_profile_calibration_a5000_2026-06-07.md"
CANDIDATE = ROOT / "docs" / "reports" / "goal3826_scale_profile_candidate_a5000" / "summary.json"
CALIBRATION = ROOT / "docs" / "reports" / "goal3826_scale_profile_calibration_a5000" / "summary.json"
BARNES = ROOT / "docs" / "reports" / "goal3826_barnes_hut_calibration_a5000" / "summary.json"


class Goal3826ScaleProfileCalibrationA5000Test(unittest.TestCase):
    def test_candidate_sweep_records_expected_passes_and_timeouts(self) -> None:
        payload = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}
        self.assertEqual(payload["commit"], "b00286c5")
        self.assertFalse(payload["all_pass"])
        self.assertEqual(rows["rt_dbscan_numba_65536"]["status"], "timeout")
        self.assertEqual(rows["robot_collision_4096"]["status"], "timeout")
        self.assertEqual(rows["barnes_hut_numba_8192"]["status"], "timeout")
        for name in (
            "hausdorff_xhd_scale",
            "spatial_rayjoin_pip_count_repeat",
            "contact_manifold_grid64",
            "raydb_style_count_262k",
            "librts_spatial_index_32768",
            "rtnn_prepared_optix_65536",
            "triangle_counting_native_2048",
        ):
            self.assertEqual(rows[name]["status"], "pass", name)
            self.assertTrue(rows[name]["json_ok"], name)

    def test_calibration_finds_rt_dbscan_and_robot_scale_candidates(self) -> None:
        payload = json.loads(CALIBRATION.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}
        self.assertEqual(rows["rt_dbscan_numba_8192"]["status"], "pass")
        self.assertLess(rows["rt_dbscan_numba_8192"]["elapsed_sec"], 15.0)
        self.assertEqual(rows["rt_dbscan_numba_16384"]["status"], "pass")
        self.assertEqual(rows["rt_dbscan_numba_32768"]["status"], "pass")
        self.assertEqual(rows["robot_collision_1024"]["status"], "pass")
        self.assertLess(rows["robot_collision_1024"]["elapsed_sec"], 20.0)
        self.assertEqual(rows["robot_collision_2048"]["status"], "timeout")
        self.assertEqual(rows["barnes_hut_numba_2048"]["status"], "timeout")
        self.assertEqual(rows["barnes_hut_numba_4096"]["status"], "timeout")

    def test_barnes_hut_ladder_records_scalability_cliff(self) -> None:
        payload = json.loads(BARNES.read_text(encoding="utf-8"))
        rows = {row["name"]: row for row in payload["rows"]}
        self.assertFalse(payload["all_pass"])
        for name in ("barnes_hut_numba_1152", "barnes_hut_numba_1280", "barnes_hut_numba_1536"):
            self.assertEqual(rows[name]["status"], "timeout", name)

    def test_report_records_boundary_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3826",
            "RT-DBSCAN: `8192` points is a good default scale profile",
            "Robot collision: `1024` poses",
            "Barnes-Hut: the current no-RawKernel Numba exact-force path has a severe scaling cliff",
            "Next Engineering Target",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
