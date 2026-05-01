from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count


class _FakeRawRows:
    def __init__(self, row_count: int) -> None:
        self.row_count = row_count
        self.closed = False

    def __len__(self) -> int:
        return self.row_count

    def close(self) -> None:
        self.closed = True


class Goal1158GraphRawSummaryContractTest(unittest.TestCase):
    def test_bfs_embree_summary_uses_raw_row_view_without_dict_materialization(self) -> None:
        raw_rows = _FakeRawRows(7)
        with (
            mock.patch.object(rtdl_graph_bfs.rt, "run_embree", return_value=raw_rows) as run_embree,
            mock.patch.object(
                rtdl_graph_bfs.rt,
                "summarize_bfs_row_view",
                return_value={"discovered_edge_count": 7, "discovered_vertex_count": 5, "max_level": 1},
            ) as summarize,
        ):
            payload = rtdl_graph_bfs.run_backend("embree", copies=3, output_mode="summary")

        self.assertEqual(run_embree.call_args.kwargs["result_mode"], "raw")
        summarize.assert_called_once_with(raw_rows)
        self.assertTrue(raw_rows.closed)
        self.assertEqual(payload["rows"], [])
        self.assertEqual(payload["row_count"], 7)
        self.assertEqual(payload["run_phases"]["row_materialization_sec"], 0.0)
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp_raw_row_view")

    def test_triangle_embree_summary_uses_raw_row_view_without_dict_materialization(self) -> None:
        raw_rows = _FakeRawRows(3)
        with (
            mock.patch.object(rtdl_graph_triangle_count.rt, "run_embree", return_value=raw_rows) as run_embree,
            mock.patch.object(
                rtdl_graph_triangle_count.rt,
                "summarize_triangle_row_view",
                return_value={"triangle_count": 3, "touched_vertex_count": 9},
            ) as summarize,
        ):
            payload = rtdl_graph_triangle_count.run_backend("embree", copies=3, output_mode="summary")

        self.assertEqual(run_embree.call_args.kwargs["result_mode"], "raw")
        summarize.assert_called_once_with(raw_rows)
        self.assertTrue(raw_rows.closed)
        self.assertEqual(payload["rows"], [])
        self.assertEqual(payload["row_count"], 3)
        self.assertEqual(payload["run_phases"]["row_materialization_sec"], 0.0)
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp_raw_row_view")

    def test_bfs_optix_summary_uses_raw_row_view_contract(self) -> None:
        raw_rows = _FakeRawRows(11)
        with (
            mock.patch.object(rtdl_graph_bfs.rt, "run_optix", return_value=raw_rows) as run_optix,
            mock.patch.object(
                rtdl_graph_bfs.rt,
                "summarize_bfs_row_view",
                return_value={"discovered_edge_count": 11, "discovered_vertex_count": 8, "max_level": 1},
            ),
        ):
            payload = rtdl_graph_bfs.run_backend(
                "optix",
                copies=5,
                output_mode="summary",
                optix_graph_mode="native",
            )

        self.assertEqual(run_optix.call_args.kwargs["result_mode"], "raw")
        self.assertEqual(payload["row_count"], 11)
        self.assertEqual(payload["run_phases"]["row_materialization_sec"], 0.0)
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp_raw_row_view")

    def test_triangle_optix_summary_uses_raw_row_view_contract(self) -> None:
        raw_rows = _FakeRawRows(13)
        with (
            mock.patch.object(rtdl_graph_triangle_count.rt, "run_optix", return_value=raw_rows) as run_optix,
            mock.patch.object(
                rtdl_graph_triangle_count.rt,
                "summarize_triangle_row_view",
                return_value={"triangle_count": 13, "touched_vertex_count": 39},
            ),
        ):
            payload = rtdl_graph_triangle_count.run_backend(
                "optix",
                copies=5,
                output_mode="summary",
                optix_graph_mode="native",
            )

        self.assertEqual(run_optix.call_args.kwargs["result_mode"], "raw")
        self.assertEqual(payload["row_count"], 13)
        self.assertEqual(payload["run_phases"]["row_materialization_sec"], 0.0)
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp_raw_row_view")


if __name__ == "__main__":
    unittest.main()
