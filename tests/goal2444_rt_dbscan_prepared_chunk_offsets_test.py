from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal2444_rt_dbscan_prepared_chunk_offsets_2026-05-19.md"


class Goal2444RtDbscanPreparedChunkOffsetsTest(unittest.TestCase):
    def test_chunked_runtime_prepares_offsets_once_and_reports_boundary(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("self.chunk_edge_offsets", adapters)
        self.assertIn("self.chunk_directed_edge_counts", adapters)
        self.assertIn("prepared_chunk_edge_offsets_reused", adapters)
        self.assertIn("degree_prefix_offsets_prepared_once_per_chunk", adapters)
        self.assertIn("allocated_per_chunk_to_avoid_cross_stream_reuse_race", adapters)
        self.assertIn("accept-with-boundary", report)
        self.assertIn("does not reuse a single neighbor-index workspace", report)
        self.assertIn("cross-stream reuse race", report)

    def test_offsets_are_used_by_chunk_index_without_per_run_cumsum(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        method_start = adapters.index("    def _chunk_adjacency(self, chunk_index")
        method_end = adapters.index("    def run(self", method_start)
        method = adapters[method_start:method_end]

        self.assertIn("edge_offsets = self.chunk_edge_offsets[chunk_index]", method)
        self.assertIn("directed_edge_count = self.chunk_directed_edge_counts[chunk_index]", method)
        self.assertNotIn("cumsum", method)
        self.assertNotIn("self.cupy.empty((end - start + 1,)", method)


if __name__ == "__main__":
    unittest.main()
