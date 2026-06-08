from __future__ import annotations

from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    _cluster_signature_from_nonnegative_label_counts,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"


class Goal3898RtDbscanNumbaSegmentedCountSignatureTest(unittest.TestCase):
    def test_nonnegative_label_counts_densify_to_existing_signature_shape(self) -> None:
        signature = _cluster_signature_from_nonnegative_label_counts(
            [0, 4, 0, 3, 0, 2],
            core_count=9,
        )

        self.assertEqual(
            signature,
            {
                "cluster_sizes": {1: 4, 2: 3, 3: 2},
                "core_count": 9,
                "noise_count": 0,
            },
        )

    def test_app_uses_generic_numba_label_count_for_column_signature_fast_path(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("_cluster_signature_from_numba_label_columns", source)
        self.assertIn("rt.run_numba_label_count_and_flag_count_i64", source)
        self.assertIn("numba_label_count_and_flag_count_label_columns", source)
        self.assertIn("column_signature_uses_numba_label_count_and_flag_count", source)
        self.assertIn("column_signature_uses_numba_segmented_count", source)
        self.assertIn("column_signature_materializes_point_ids", source)
        self.assertIn("column_signature_materializes_core_flags", source)
        self.assertNotIn('"native_dbscan_abi_added": true', source)


if __name__ == "__main__":
    unittest.main()
