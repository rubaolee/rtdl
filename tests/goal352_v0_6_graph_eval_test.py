import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")

import rtdsl as rt
import rtdsl.graph_eval as graph_eval


class Goal352GraphEvalTest(unittest.TestCase):
    def test_binary_tree_graph_matches_bfs_contract(self) -> None:
        graph = rt.binary_tree_graph(7)

        self.assertEqual(
            rt.bfs_levels_cpu(graph, source_id=0),
            (
                {"vertex_id": 0, "level": 0},
                {"vertex_id": 1, "level": 1},
                {"vertex_id": 2, "level": 1},
                {"vertex_id": 3, "level": 2},
                {"vertex_id": 4, "level": 2},
                {"vertex_id": 5, "level": 2},
                {"vertex_id": 6, "level": 2},
            ),
        )

    def test_cycle_graph_matches_bfs_contract(self) -> None:
        graph = rt.cycle_graph(5)

        self.assertEqual(
            rt.bfs_levels_cpu(graph, source_id=0),
            (
                {"vertex_id": 0, "level": 0},
                {"vertex_id": 1, "level": 1},
                {"vertex_id": 4, "level": 1},
                {"vertex_id": 2, "level": 2},
                {"vertex_id": 3, "level": 2},
            ),
        )

    def test_clique_graph_matches_triangle_count_contract(self) -> None:
        graph = rt.clique_graph(4)
        self.assertEqual(rt.triangle_count_cpu(graph), 4)

    def test_baseline_evaluation_reports_oracle_match(self) -> None:
        graph = rt.grid_graph(3, 2)
        summary = rt.bfs_baseline_evaluation(graph, source_id=0, repeats=1)

        self.assertTrue(summary["oracle_match"])
        self.assertEqual(summary["workload"], "bfs")


    def test_triangle_count_baseline_evaluation_reports_oracle_match(self) -> None:
        graph = rt.clique_graph(4)
        summary = rt.triangle_count_baseline_evaluation(graph, repeats=1)

        self.assertTrue(summary["oracle_match"])
        self.assertEqual(summary["workload"], "triangle_count")
        self.assertIn("oracle_seconds", summary)
        self.assertIn("python_seconds", summary)

    def test_bfs_postgresql_timing_separates_setup_from_query(self) -> None:
        graph = rt.binary_tree_graph(7)
        connection = object()
        calls: list[str] = []

        def fake_prepare(*args, **kwargs):
            calls.append("prepare")

        def fake_query(*args, **kwargs):
            calls.append("query")
            return (
                {"vertex_id": 0, "level": 0},
                {"vertex_id": 1, "level": 1},
                {"vertex_id": 2, "level": 1},
                {"vertex_id": 3, "level": 2},
                {"vertex_id": 4, "level": 2},
                {"vertex_id": 5, "level": 2},
                {"vertex_id": 6, "level": 2},
            )

        with mock.patch.object(graph_eval, "postgresql_available", return_value=True), \
             mock.patch.object(graph_eval, "connect_postgresql") as connect_mock, \
             mock.patch.object(graph_eval, "prepare_postgresql_graph_edges_table", side_effect=fake_prepare), \
             mock.patch.object(graph_eval, "query_postgresql_bfs_levels", side_effect=fake_query):
            connect_mock.return_value = mock.Mock(close=mock.Mock(), cursor=None)
            summary = rt.bfs_baseline_evaluation(graph, source_id=0, repeats=3, postgresql_dsn="dbname=test")

        self.assertEqual(calls.count("prepare"), 1)
        self.assertEqual(calls.count("query"), 3)
        self.assertTrue(summary["postgresql_match"])
        self.assertIn("postgresql_setup_seconds", summary)
        self.assertIn("postgresql_seconds", summary)

    def test_triangle_postgresql_timing_separates_setup_from_query(self) -> None:
        graph = rt.clique_graph(4)
        calls: list[str] = []

        def fake_prepare(*args, **kwargs):
            calls.append("prepare")

        def fake_query(*args, **kwargs):
            calls.append("query")
            return 4

        with mock.patch.object(graph_eval, "postgresql_available", return_value=True), \
             mock.patch.object(graph_eval, "connect_postgresql") as connect_mock, \
             mock.patch.object(graph_eval, "prepare_postgresql_graph_edges_table", side_effect=fake_prepare), \
             mock.patch.object(graph_eval, "query_postgresql_triangle_count", side_effect=fake_query):
            connect_mock.return_value = mock.Mock(close=mock.Mock(), cursor=None)
            summary = rt.triangle_count_baseline_evaluation(graph, repeats=2, postgresql_dsn="dbname=test")

        self.assertEqual(calls.count("prepare"), 1)
        self.assertEqual(calls.count("query"), 2)
        self.assertTrue(summary["postgresql_match"])
        self.assertIn("postgresql_setup_seconds", summary)
        self.assertIn("postgresql_seconds", summary)

    def test_bfs_python_truth_path_is_timed_once_per_repeat_group(self) -> None:
        graph = rt.binary_tree_graph(7)
        python_calls = []

        expected_rows = (
            {"vertex_id": 0, "level": 0},
            {"vertex_id": 1, "level": 1},
            {"vertex_id": 2, "level": 1},
            {"vertex_id": 3, "level": 2},
            {"vertex_id": 4, "level": 2},
            {"vertex_id": 5, "level": 2},
            {"vertex_id": 6, "level": 2},
        )

        def fake_bfs_levels_cpu(*args, **kwargs):
            python_calls.append("python")
            return expected_rows

        with mock.patch.object(graph_eval, "bfs_levels_cpu", side_effect=fake_bfs_levels_cpu), \
             mock.patch.object(graph_eval, "bfs_levels_oracle", return_value=expected_rows):
            summary = graph_eval.bfs_baseline_evaluation(graph, source_id=0, repeats=3)

        self.assertEqual(python_calls.count("python"), 3)
        self.assertTrue(summary["oracle_match"])


if __name__ == "__main__":
    unittest.main()
