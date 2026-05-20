from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPEAT_PROBE = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2447_rt_dbscan_neighbor_workspace_reuse_2026-05-19.md"


class Goal2447RtDbscanNeighborWorkspaceReuseTest(unittest.TestCase):
    def test_chunked_runtime_has_explicit_opt_in_workspace_reuse(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("reuse_neighbor_index_workspace: bool = False", adapters)
        self.assertIn("self.reuse_neighbor_index_workspace", adapters)
        self.assertIn("self.neighbor_index_workspaces", adapters)
        self.assertIn("single_prepared_workspace_with_explicit_chunk_sync", adapters)
        self.assertIn("prepared_workspace_pool_with_explicit_reuse_sync", adapters)
        self.assertIn("chunk_sync_for_neighbor_index_workspace_reuse", adapters)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("opt-in", report)
        self.assertIn("explicit chunk synchronization", report)

    def test_default_policy_still_avoids_cross_stream_reuse_race(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        repeat_probe = REPEAT_PROBE.read_text(encoding="utf-8")

        self.assertIn("allocated_per_chunk_to_avoid_cross_stream_reuse_race", adapters)
        self.assertIn("reuse_neighbor_index_workspace: bool = False", adapters)
        self.assertIn("--reuse-chunk-neighbor-index-workspace", app)
        self.assertIn("reuse_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace", app)
        self.assertIn("--reuse-chunk-neighbor-index-workspace", repeat_probe)
        self.assertIn("neighbor_index_workspace_reused", repeat_probe)
        self.assertIn("--chunk-neighbor-index-workspace-pool-size", repeat_probe)

    def test_workspace_reuse_syncs_before_overwriting_a_pool_slot(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        loop_start = adapters.index("        for chunk_index, (start, end) in enumerate(self.chunk_ranges):")
        loop_end = adapters.index("            edge_offsets, neighbor_indices", loop_start)
        loop = adapters[loop_start:loop_end]

        self.assertIn("self.neighbor_index_workspaces", loop)
        self.assertIn("chunk_index >= self.neighbor_index_workspace_pool_size", loop)
        self.assertIn("self.runtime[\"sync\"]()", loop)


if __name__ == "__main__":
    unittest.main()
