from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPEAT_PROBE = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2449_rt_dbscan_neighbor_workspace_pool_2026-05-19.md"


class Goal2449RtDbscanNeighborWorkspacePoolTest(unittest.TestCase):
    def test_runtime_exposes_bounded_workspace_pool(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("neighbor_index_workspace_pool_size: int = 0", adapters)
        self.assertIn("self.neighbor_index_workspaces: list[object] = []", adapters)
        self.assertIn("prepared_workspace_pool_with_explicit_reuse_sync", adapters)
        self.assertIn("neighbor_index_workspace_pool_size", adapters)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("bounded workspace pool", report)

    def test_pool_reuse_syncs_only_when_reusing_a_slot(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        loop_start = adapters.index("        for chunk_index, (start, end) in enumerate(self.chunk_ranges):")
        loop_end = adapters.index("            edge_offsets, neighbor_indices", loop_start)
        loop = adapters[loop_start:loop_end]

        self.assertIn("chunk_index >= self.neighbor_index_workspace_pool_size", loop)
        self.assertIn("self.runtime[\"sync\"]()", loop)
        self.assertNotIn("if self.reuse_neighbor_index_workspace:\n                self.runtime", loop)

    def test_benchmark_and_repeat_probe_accept_pool_size(self) -> None:
        app = APP.read_text(encoding="utf-8")
        repeat_probe = REPEAT_PROBE.read_text(encoding="utf-8")

        self.assertIn("--chunk-neighbor-index-workspace-pool-size", app)
        self.assertIn("neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size", app)
        self.assertIn("--chunk-neighbor-index-workspace-pool-size", repeat_probe)
        self.assertIn("neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size", repeat_probe)


if __name__ == "__main__":
    unittest.main()
