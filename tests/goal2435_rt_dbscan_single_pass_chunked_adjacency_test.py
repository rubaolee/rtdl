from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2435_rt_dbscan_single_pass_chunked_adjacency_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2435_rt_dbscan_single_pass_chunked_adjacency_pod"
OLD_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2433_rt_dbscan_chunked_adjacency_pod"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal2435RtDbscanSinglePassChunkedAdjacencyTest(unittest.TestCase):
    def test_single_pass_kernels_and_metadata_are_wired(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("radius_graph_3d_chunk_adjacency_union_border_candidate_kernel", adapters)
        self.assertIn("radius_graph_3d_border_candidate_label_kernel", adapters)
        self.assertIn("border_core_candidate_workspace", adapters)
        self.assertIn('"adjacency_write_pass_count": 1', adapters)
        self.assertIn("one_core_neighbor_candidate_per_border_point", adapters)
        self.assertIn("without a", readme)
        self.assertIn("second RT adjacency fill", readme)

    def test_pod_artifacts_show_correctness_and_speedup_over_goal2433_chunked(self) -> None:
        tiny = json.loads((ARTIFACT_DIR / "tiny_app.json").read_text(encoding="utf-8"))
        self.assertTrue(tiny["matches_reference"])
        self.assertEqual(tiny["metadata"]["adjacency_write_pass_count"], 1)
        self.assertEqual(tiny["metadata"]["total_directed_edge_count"], 33)

        for artifact_name in ("clustered4096_repeat.json", "clustered8192_repeat.json"):
            with self.subTest(artifact=artifact_name):
                new_payload = json.loads((ARTIFACT_DIR / artifact_name).read_text(encoding="utf-8"))
                old_payload = json.loads((OLD_ARTIFACT_DIR / artifact_name).read_text(encoding="utf-8"))
                self.assertTrue(new_payload["signatures_match"])
                new_rows = [
                    row for row in new_payload["rows"]
                    if row["mode"] == "optix_rt_core_chunked_adjacency_cupy_components_3d"
                ]
                old_rows = [
                    row for row in old_payload["rows"]
                    if row["mode"] == "optix_rt_core_chunked_adjacency_cupy_components_3d"
                ]
                new_tail = statistics.median(float(row["outer_elapsed_sec"]) for row in new_rows[1:])
                old_tail = statistics.median(float(row["outer_elapsed_sec"]) for row in old_rows[1:])
                self.assertLess(new_tail, old_tail)

        dense = json.loads((ARTIFACT_DIR / "clustered32768_chunked.json").read_text(encoding="utf-8"))
        row = dense["rows"][0]
        self.assertTrue(dense["signatures_match"])
        self.assertEqual(int(row["directed_edge_count"]), 136345984)
        self.assertEqual(int(row["max_chunk_directed_edge_count"]), 17197789)
        self.assertLess(float(row["outer_elapsed_sec"]), 0.75)

    def test_report_and_todo_keep_boundary_clear(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        todo = TODO.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("No DBSCAN-native engine", report)
        self.assertIn("ABI was added", report)
        self.assertIn("not raw speed", report)
        self.assertIn("does not authorize a broad", report)
        self.assertIn("Goal2435 removed that second RT fill", todo)
        self.assertIn("full adjacency, chunked", todo)


if __name__ == "__main__":
    unittest.main()
