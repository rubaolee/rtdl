from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"


class Goal3918RtDbscanBlockedNumbaGroupedStreamModesTest(unittest.TestCase):
    def test_app_declares_blocked_numba_grouped_stream_modes(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("optix_rt_core_grouped_stream_blocked_numba_components_3d", source)
        self.assertIn("optix_rt_core_grouped_stream_blocked_numba_column_signature_3d", source)
        self.assertIn("optix_rt_grouped_stream_blocked_numba_radius_graph_components_3d", source)
        self.assertIn("optix_rt_grouped_stream_blocked_numba_radius_graph_column_signature_3d", source)

    def test_blocked_numba_modes_share_generic_grouped_stream_contract(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('grouped_stream_partner = "numba" if "_numba_" in mode else "cupy"', source)
        self.assertIn("grouped_union_query_block_size=resolved_query_block_size if blocked_grouped_stream else None", source)
        self.assertIn('"generic_prepared_fixed_radius_grouped_union_3d_self_range_device_workspaces"', source)
        self.assertIn('"prepared_rt_core_grouped_union_3d_self_query_blocked_ranges"', source)
        self.assertIn("numba_label_count_and_flag_count_label_columns", source)


if __name__ == "__main__":
    unittest.main()
