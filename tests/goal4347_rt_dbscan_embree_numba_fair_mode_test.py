from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"


class Goal4347RtDbscanEmbreeNumbaFairModeTest(unittest.TestCase):
    def test_embree_numba_column_signature_mode_is_explicit(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"embree_core_flags_numba_prepared_grid_column_signature_3d"', source)
        self.assertIn("prepare_embree_fixed_radius_count_threshold_3d", source)
        self.assertIn("embree_prepared_count_threshold_compact_rows_numba_prepared_grid_radius_graph_column_signature_3d", source)
        self.assertIn("generic_prepared_fixed_radius_count_threshold_3d_host_compact_rows", source)
        self.assertIn('"materializes_neighbor_rows": False', source)
        self.assertIn('"current_embree_3d_scene_setup_paid_in_threshold_phase": False', source)
        self.assertNotIn("embree_threshold_capped_rows_numba_prepared_grid_radius_graph_column_signature_3d", source)
        self.assertNotIn("generic_fixed_radius_count_threshold_3d_host_columns_via_threshold_capped_rows", source)

    def test_embree_3d_threshold_native_symbol_is_exposed(self) -> None:
        prelude = (ROOT / "src" / "native" / "embree" / "rtdl_embree_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "embree_runtime.py").read_text(encoding="utf-8")
        init = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")

        symbol = "rtdl_embree_fixed_radius_count_threshold_3d_run"
        self.assertIn("struct RtdlEmbreeFixedRadiusCountThreshold3D", prelude)
        self.assertIn(symbol, prelude)
        self.assertIn(f"RTDL_EMBREE_EXPORT int {symbol}", api)
        self.assertIn("class PreparedEmbreeFixedRadiusCountThreshold3D", runtime)
        self.assertIn("prepare_embree_fixed_radius_count_threshold_3d", runtime)
        self.assertIn("prepare_embree_fixed_radius_count_threshold_3d", init)


if __name__ == "__main__":
    unittest.main()
