from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"


class Goal2817RtnnBlockPartialAggregateTest(unittest.TestCase):
    def test_block_partial_kernel_is_generic_summary_path(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks", core)
        self.assertIn("FrnRankedAggregate* partials_out", core)
        self.assertIn("partials_out[blockIdx.x].query_count", core)
        self.assertNotIn("rtnn", core.lower())

    def test_prepared_query_handle_owns_partial_workspace(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("size_t aggregate_block_count", workloads)
        self.assertIn("std::unique_ptr<DevPtr> d_aggregate_partials", workloads)
        self.assertIn("aggregate_block_count = (count + 255u) / 256u", workloads)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks", workloads)
        self.assertIn("use_block_partial_direct", workloads)
        self.assertIn("prepared_queries->query_count <= 65536u", workloads)

    def test_python_phase_label_names_block_partial_mode(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn(
            '15: "prepared_query_uniform_cell_ranked_summary_aggregate_f32_block_partials"',
            runtime,
        )


if __name__ == "__main__":
    unittest.main()
