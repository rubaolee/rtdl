from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"


def _source_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


class PhoenixFixedRadiusGraphSelfQueryRefreshTest(unittest.TestCase):
    def test_cupy_grouped_stream_refresh_uses_runner_backed_self_query_count_columns(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        cupy_class = _source_between(
            source,
            "class PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D:",
            "def _run_cupy_grouped_stream_same_stream_evidence",
        )

        self.assertIn(
            "run_fixed_radius_count_threshold_3d_self_query_prepared_session",
            cupy_class,
        )
        self.assertIn("prepared_execution_session_runner_used", cupy_class)
        self.assertIn('"productized_execution_path": "prepared_execution_session_runner"', cupy_class)
        self.assertIn("core_flag_refresh_runtime_executed", cupy_class)
        self.assertNotIn(
            "fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(\n"
            "                self.prepared_native,\n"
            "                self.point_rows,",
            cupy_class,
        )
        self.assertIn('"query_source": "prepared_search_points_self_query_device"', cupy_class)

    def test_same_stream_evidence_refresh_uses_self_query_count_columns(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        same_stream = _source_between(
            source,
            "def _run_cupy_grouped_stream_same_stream_evidence",
            "_RADIUS_GRAPH_BOUNDARY_ASSIGNMENT_POLICIES",
        )

        self.assertIn(
            "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
            same_stream,
        )
        self.assertNotIn(
            "fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(\n"
            "            prepared.prepared_native,\n"
            "            prepared.point_rows,",
            same_stream,
        )
        self.assertIn('"query_source": "prepared_search_points_self_query_device"', same_stream)

    def test_numba_grouped_stream_refresh_uses_self_query_count_columns(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        numba_class = _source_between(
            source,
            "class PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D:",
            "def radius_graph_components_3d_optix_cupy_prepared_partner_columns",
        )

        self.assertIn(
            "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
            numba_class,
        )
        self.assertNotIn(
            "fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(\n"
            "            self.prepared_native,\n"
            "            self.point_rows,",
            numba_class,
        )
        self.assertIn('"query_source": "prepared_search_points_self_query_device"', numba_class)


if __name__ == "__main__":
    unittest.main()
