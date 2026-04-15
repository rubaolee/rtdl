import gzip
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.graph_perf import measure_bfs_perf
from rtdsl.graph_perf import median_seconds
from rtdsl.graph_perf import select_bfs_inputs
from rtdsl.graph_perf import select_triangle_inputs
from rtdsl.graph_perf import tune_bfs_perf
from rtdsl.graph_perf import tune_triangle_perf


class Goal401V06LargeScaleEnginePerfGateTest(unittest.TestCase):
    def test_graph_dataset_candidates_include_large_graph_specs(self) -> None:
        names = {entry.name for entry in rt.graph_dataset_candidates()}
        self.assertIn("snap_wiki_talk", names)
        self.assertIn("graphalytics_cit_patents", names)

    def test_load_snap_edge_list_graph_reads_directed_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt.gz"
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                handle.write("# comment\n0 1\n0 2\n2 3\n")
            graph = rt.load_snap_edge_list_graph(path)
            self.assertEqual(graph.vertex_count, 4)
            self.assertEqual(graph.row_offsets, (0, 2, 2, 3, 3))
            self.assertEqual(graph.column_indices, (1, 2, 3))

    def test_load_snap_simple_undirected_graph_dedupes_and_drops_loops(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.txt"
            path.write_text("0 0\n0 1\n1 0\n1 2\n2 1\n", encoding="utf-8")
            graph = rt.load_snap_simple_undirected_graph(path)
            self.assertEqual(graph.row_offsets, (0, 1, 3, 4))
            self.assertEqual(graph.column_indices, (1, 0, 2, 1))

    def test_select_bfs_inputs_prefers_expandable_vertices(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 3, 3, 4),
            column_indices=(1, 2, 3, 0),
        )
        inputs = select_bfs_inputs(graph, frontier_size=2, source_id=3)
        self.assertEqual(inputs["frontier"], ((3, 0), (0, 0)))
        self.assertEqual(inputs["visited"], (3, 0))

    def test_select_triangle_inputs_collects_canonical_seeds(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )
        inputs = select_triangle_inputs(graph, seed_count=2)
        self.assertEqual(inputs["seeds"], ((0, 1), (0, 2)))

    def test_measure_bfs_perf_reports_backend_and_postgresql_fields(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 2, 3, 3),
            column_indices=(1, 2, 3),
        )
        with mock.patch("rtdsl.graph_perf._measure_backend_family", return_value={"embree_seconds": 1.25}):
            with mock.patch("rtdsl.graph_perf._measure_postgresql_bfs", return_value=(2.5, 0.5)):
                summary = measure_bfs_perf(
                    graph,
                    frontier_size=1,
                    source_id=0,
                    repeats=1,
                    postgresql_dsn="dbname=postgres",
                )
        self.assertEqual(summary["workload"], "bfs")
        self.assertEqual(summary["frontier_size"], 1)
        self.assertEqual(summary["embree_seconds"], 1.25)
        self.assertEqual(summary["postgresql_setup_seconds"], 2.5)
        self.assertEqual(summary["postgresql_seconds"], 0.5)

    def test_median_seconds_rejects_empty_samples(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one sample"):
            median_seconds([])

    def test_tune_bfs_perf_scales_frontier_batch_toward_target(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 8, 8),
            column_indices=(1, 2, 0, 3, 1, 4, 2, 4),
        )
        samples = iter(
            (
                {
                    "workload": "bfs",
                    "vertex_count": 5,
                    "edge_count": 8,
                    "frontier_size": 128,
                    "optix_seconds": 1.0,
                    "postgresql_seconds": 0.1,
                    "postgresql_setup_seconds": 1.0,
                },
                {
                    "workload": "bfs",
                    "vertex_count": 5,
                    "edge_count": 8,
                    "frontier_size": 1280,
                    "optix_seconds": 9.5,
                    "postgresql_seconds": 0.2,
                    "postgresql_setup_seconds": 1.1,
                },
            )
        )
        with mock.patch("rtdsl.graph_perf.measure_bfs_perf", side_effect=lambda *args, **kwargs: next(samples)):
            with mock.patch("rtdsl.graph_perf._measure_postgresql_bfs", return_value=(2.0, 0.5)):
                summary = tune_bfs_perf(
                    graph,
                    frontier_size=128,
                    source_id=0,
                    repeats=1,
                    postgresql_dsn="dbname=postgres",
                    target_backend="optix",
                    target_seconds=10.0,
                )
        self.assertEqual(summary["frontier_size"], 1280)
        self.assertEqual(summary["tuning_rounds"], 2)
        self.assertEqual(summary["tuning_history"][0]["requested_frontier_size"], 128)
        self.assertEqual(summary["tuning_history"][1]["requested_frontier_size"], 1280)

    def test_tune_triangle_perf_scales_seed_batch_toward_target(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )
        samples = iter(
            (
                {
                    "workload": "triangle_count",
                    "vertex_count": 4,
                    "edge_count": 6,
                    "seed_count": 256,
                    "vulkan_seconds": 0.5,
                    "postgresql_seconds": 0.1,
                    "postgresql_setup_seconds": 1.0,
                },
                {
                    "workload": "triangle_count",
                    "vertex_count": 4,
                    "edge_count": 6,
                    "seed_count": 5120,
                    "vulkan_seconds": 8.0,
                    "postgresql_seconds": 0.2,
                    "postgresql_setup_seconds": 1.2,
                },
            )
        )
        with mock.patch("rtdsl.graph_perf.measure_triangle_perf", side_effect=lambda *args, **kwargs: next(samples)):
            with mock.patch("rtdsl.graph_perf._measure_postgresql_triangle", return_value=(2.0, 0.5)):
                summary = tune_triangle_perf(
                    graph,
                    seed_count=256,
                    repeats=1,
                    postgresql_dsn="dbname=postgres",
                    target_backend="vulkan",
                    target_seconds=10.0,
                )
        self.assertEqual(summary["seed_count"], 5120)
        self.assertEqual(summary["tuning_rounds"], 2)
        self.assertEqual(summary["tuning_history"][0]["requested_seed_count"], 256)
        self.assertEqual(summary["tuning_history"][1]["requested_seed_count"], 5120)

    def test_tune_triangle_perf_raises_execution_iterations_when_seed_batch_saturates(self) -> None:
        graph = rt.csr_graph(
            row_offsets=(0, 2, 4, 6, 6),
            column_indices=(1, 2, 0, 2, 0, 1),
        )
        samples = iter(
            (
                {
                    "workload": "triangle_count",
                    "vertex_count": 4,
                    "edge_count": 6,
                    "seed_count": 500000,
                    "execution_iterations": 1,
                    "optix_seconds": 0.1,
                    "postgresql_seconds": 0.1,
                    "postgresql_setup_seconds": 1.0,
                },
                {
                    "workload": "triangle_count",
                    "vertex_count": 4,
                    "edge_count": 6,
                    "seed_count": 500000,
                    "execution_iterations": 1,
                    "optix_seconds": 0.1,
                    "postgresql_seconds": 0.1,
                    "postgresql_setup_seconds": 1.1,
                },
                {
                    "workload": "triangle_count",
                    "vertex_count": 4,
                    "edge_count": 6,
                    "seed_count": 500000,
                    "execution_iterations": 100,
                    "optix_seconds": 9.0,
                    "postgresql_seconds": 0.2,
                    "postgresql_setup_seconds": 1.2,
                },
            )
        )
        with mock.patch("rtdsl.graph_perf.measure_triangle_perf", side_effect=lambda *args, **kwargs: next(samples)):
            with mock.patch("rtdsl.graph_perf._measure_postgresql_triangle", return_value=(2.0, 0.5)):
                summary = tune_triangle_perf(
                    graph,
                    seed_count=500000,
                    repeats=1,
                    postgresql_dsn="dbname=postgres",
                    target_backend="optix",
                    target_seconds=10.0,
                    max_seed_count=500000,
                )
        self.assertEqual(summary["seed_count"], 500000)
        self.assertEqual(summary["final_execution_iterations"], 100)
        self.assertEqual(summary["tuning_rounds"], 3)
        self.assertEqual(summary["tuning_history"][0]["execution_iterations"], 1)
        self.assertEqual(summary["tuning_history"][1]["execution_iterations"], 1)
        self.assertEqual(summary["tuning_history"][2]["execution_iterations"], 100)


if __name__ == "__main__":
    unittest.main()
