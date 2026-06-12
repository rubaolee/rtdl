from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"


class Goal4347RtDbscanEmbreeNumbaFairModeTest(unittest.TestCase):
    def test_embree_numba_column_signature_mode_is_explicit(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"embree_core_flags_numba_prepared_grid_column_signature_3d"', source)
        self.assertIn("embree_threshold_capped_rows_numba_prepared_grid_radius_graph_column_signature_3d", source)
        self.assertIn("current_embree_3d_scene_setup_paid_in_threshold_phase", source)
        self.assertIn("generic_fixed_radius_count_threshold_3d_host_columns_via_threshold_capped_rows", source)


if __name__ == "__main__":
    unittest.main()
