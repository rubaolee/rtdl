from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2363_rtnn_packed_column_neighbor_path_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2361_rtdl_3d_neighbor_phase"


class Goal2363RtnnPackedColumnNeighborPathTest(unittest.TestCase):
    def test_runner_exposes_packed_column_input_mode(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("--input-mode", text)
        self.assertIn("packed-columns", text)
        self.assertIn("rt.pack_points(ids=ids, x=xs, y=ys, z=zs, dimension=3)", text)
        self.assertIn('"input_pack_sec": input_pack_sec', text)

    def test_artifacts_show_same_rows_and_lower_warm_wall_time(self) -> None:
        records_65 = json.loads((ARTIFACT_DIR / "rtdl_grid_phase_raw_repeat_3d_65536_r002_k50.json").read_text(encoding="utf-8"))
        packed_65 = json.loads((ARTIFACT_DIR / "rtdl_grid_phase_packed_columns_raw_repeat_3d_65536_r002_k50.json").read_text(encoding="utf-8"))
        records_262 = json.loads((ARTIFACT_DIR / "rtdl_grid_phase_raw_repeat_3d_262144_r002_k50.json").read_text(encoding="utf-8"))
        packed_262 = json.loads((ARTIFACT_DIR / "rtdl_grid_phase_packed_columns_raw_repeat_3d_262144_r002_k50.json").read_text(encoding="utf-8"))

        for row in (packed_65, packed_262):
            self.assertTrue(row["ok"])
            self.assertEqual(row["input_mode"], "packed-columns")
            self.assertEqual(row["phase_timings"]["mode"], "uniform_cell_compact")
            self.assertFalse(row["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

        self.assertEqual(records_65["row_count"], packed_65["row_count"])
        self.assertEqual(records_262["row_count"], packed_262["row_count"])
        self.assertLess(packed_65["elapsed_sec"], records_65["elapsed_sec"])
        self.assertLess(packed_262["elapsed_sec"], records_262["elapsed_sec"])

    def test_report_keeps_claim_boundary_and_next_primitive_precise(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a native RTNN hook", text)
        self.assertIn("column/packed inputs are the high-performance v2.x path", text)
        self.assertIn("prepared_bounded_neighbor_search_3d", text)
        self.assertIn("does not authorize", text)
        self.assertIn("full RTNN reproduction claim", text)


if __name__ == "__main__":
    unittest.main()
