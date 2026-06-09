from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4116RtDbscanExplicitPartitionCellFactorSourceTest(unittest.TestCase):
    def test_app_exposes_explicit_partition_cell_factor_without_hidden_autotune(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("partition_cell_factor: float = 0.125", text)
        self.assertIn("--partition-cell-factor", text)
        self.assertIn("partition_cell_factor_user_selection", text)
        self.assertIn("does not authorize hidden auto-tuning", text)
        self.assertNotIn("auto_partition_cell_factor", text)
        self.assertNotIn("autotune_partition_cell_factor", text)

    def test_invalid_partition_cell_factor_rejected_before_cupy_is_needed(self) -> None:
        with self.assertRaisesRegex(ValueError, "partition_cell_factor must be positive"):
            run_rt_dbscan_benchmark(
                mode="partner_cupy_prepared_direct_status_union_component_signature_3d",
                dataset="tiny",
                point_count=None,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=False,
                validate=False,
                partition_cell_factor=0.0,
            )


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4116RtDbscanExplicitPartitionCellFactorRuntimeTest(unittest.TestCase):
    def test_prepared_direct_status_mode_honors_explicit_partition_cell_factor(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="partner_cupy_prepared_direct_status_union_component_signature_3d",
            dataset="tiny",
            point_count=None,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=True,
            partition_cell_factor=0.5,
        )

        self.assertTrue(payload["matches_reference"])
        metadata = payload["metadata"]
        self.assertEqual(metadata["path"], "partner_cupy_prepared_direct_status_union_component_signature_3d")
        self.assertEqual(metadata["partition_cell_factor_user_selection"], 0.5)
        self.assertEqual(metadata["cell_factor"], 0.5)
        self.assertEqual(metadata["prepared_direct_status_union_handle_metadata"]["cell_factor"], 0.5)
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["hidden_dispatch_allowed"])
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
