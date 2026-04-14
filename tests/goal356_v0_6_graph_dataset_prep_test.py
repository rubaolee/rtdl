import gzip
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, "src")

import rtdsl as rt


class Goal356GraphDatasetPrepTest(unittest.TestCase):
    def test_graph_dataset_candidates_include_snap_and_graphalytics(self) -> None:
        names = {entry.name for entry in rt.graph_dataset_candidates()}
        self.assertIn("snap_wiki_talk", names)
        self.assertIn("graphalytics_wiki_talk", names)
        self.assertIn("graphalytics_cit_patents", names)

    def test_graph_dataset_spec_resolves_cit_patents_download_url(self) -> None:
        spec = rt.graph_dataset_spec("graphalytics_cit_patents")
        self.assertEqual(spec.source, "Graphalytics")
        self.assertEqual(
            spec.download_url,
            "https://snap.stanford.edu/data/cit-Patents.txt.gz",
        )
        self.assertTrue(spec.directed)

    def test_load_snap_edge_list_graph_reads_directed_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "wiki-Talk.txt"
            path.write_text("# comment\n0 1\n0 2\n2 3\n", encoding="utf-8")

            graph = rt.load_snap_edge_list_graph(path)

            self.assertEqual(
                rt.bfs_levels_cpu(graph, source_id=0),
                (
                    {"vertex_id": 0, "level": 0},
                    {"vertex_id": 1, "level": 1},
                    {"vertex_id": 2, "level": 1},
                    {"vertex_id": 3, "level": 2},
                ),
            )

    def test_load_snap_edge_list_graph_reads_gzip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "wiki-Talk.txt.gz"
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                handle.write("0 1\n1 2\n")

            graph = rt.load_snap_edge_list_graph(path)
            self.assertEqual(graph.vertex_count, 3)
            self.assertEqual(graph.column_indices, (1, 2))

    def test_load_snap_simple_undirected_graph_drops_loops_and_dedupes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "wiki-Talk.txt"
            path.write_text("0 0\n0 1\n1 0\n1 2\n2 1\n", encoding="utf-8")

            graph = rt.load_snap_simple_undirected_graph(path)

            self.assertEqual(graph.vertex_count, 3)
            self.assertEqual(graph.row_offsets, (0, 1, 3, 4))
            self.assertEqual(graph.column_indices, (1, 0, 2, 1))
            self.assertEqual(rt.triangle_count_cpu(graph), 0)


    def test_load_snap_edge_list_graph_undirected_adds_reverse_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("0 1\n1 2\n", encoding="utf-8")

            graph = rt.load_snap_edge_list_graph(path, directed=False)

            # Undirected: both (0,1)/(1,0) and (1,2)/(2,1) should appear.
            self.assertEqual(graph.vertex_count, 3)
            # row_offsets for 3-vertex undirected path graph: 0 has neighbor 1;
            # 1 has neighbors 0, 2; 2 has neighbor 1.
            self.assertEqual(graph.row_offsets, (0, 1, 3, 4))
            self.assertEqual(graph.column_indices, (1, 0, 2, 1))


    def test_load_snap_edge_list_graph_respects_expected_vertex_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("0 1\n", encoding="utf-8")

            # Max ID in edges is 1, but we expect 5 vertices (0..4).
            graph = rt.load_snap_edge_list_graph(path, expected_vertex_count=5)

            self.assertEqual(graph.vertex_count, 5)
            # Neighborhoods: 0:[1], 1:[0] if undirected... wait, default is directed=True
            self.assertEqual(graph.row_offsets, (0, 1, 1, 1, 1, 1))
            self.assertEqual(graph.column_indices, (1,))

    def test_load_snap_simple_undirected_graph_respects_expected_vertex_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("0 1\n", encoding="utf-8")

            graph = rt.load_snap_simple_undirected_graph(path, expected_vertex_count=5)

            self.assertEqual(graph.vertex_count, 5)
            # Neighborhoods: 0:[1], 1:[0], 2:[], 3:[], 4:[]
            self.assertEqual(graph.row_offsets, (0, 1, 2, 2, 2, 2))
            self.assertEqual(graph.column_indices, (1, 0))


if __name__ == "__main__":
    unittest.main()
