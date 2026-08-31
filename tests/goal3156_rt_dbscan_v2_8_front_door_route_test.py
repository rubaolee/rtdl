from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal3156_rt_dbscan_v2_8_front_door_route_2026-06-03.md"


class Goal3156RTDBSCANV28FrontDoorRouteTest(unittest.TestCase):
    def test_grouped_stream_branch_uses_v2_8_front_door(self) -> None:
        app = APP.read_text(encoding="utf-8")
        start = app.index('elif mode == "optix_rt_core_grouped_stream_cupy_components_3d"')
        end = app.index('elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d"')
        grouped_branch = app[start:end]

        self.assertIn("rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d", grouped_branch)
        self.assertIn("rt.fixed_radius_graph_component_labels_3d_v2_8", grouped_branch)
        self.assertIn("component_threshold=resolved_min_neighbors", grouped_branch)
        self.assertIn('"front_door": "v2_8_fixed_radius_graph_component_continuation_3d"', grouped_branch)
        self.assertIn('"front_door_operation": "fixed_radius_graph_component_labels_3d"', grouped_branch)
        self.assertIn('"v2_8_front_door_route": True', grouped_branch)
        self.assertNotIn("rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d", grouped_branch)
        self.assertNotIn(
            "rt.radius_graph_components_3d_optix_cupy_prepared_grouped_stream_partner_columns",
            grouped_branch,
        )

    def test_old_mode_labels_stay_compatible(self) -> None:
        app = APP.read_text(encoding="utf-8")

        for mode in (
            "optix_rt_core_grouped_stream_cupy_components_3d",
            "optix_rt_core_grouped_stream_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
        ):
            self.assertIn(mode, app)

    def test_claim_boundary_stays_blocked_in_app_metadata(self) -> None:
        app = APP.read_text(encoding="utf-8")
        start = app.index('elif mode == "optix_rt_core_grouped_stream_cupy_components_3d"')
        end = app.index('elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d"')
        grouped_branch = app[start:end]

        for phrase in (
            '"optix_backend_used": True',
            '"rt_core_accelerated": True',
            '"materializes_neighbor_rows": False',
            '"materializes_directed_adjacency_stream": False',
            '"materializes_bounded_directed_adjacency_chunks": False',
            '"neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree"',
        ):
            self.assertIn(phrase, grouped_branch)

    def test_report_documents_boundary_and_compatibility(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3156",
            "routes the RT-DBSCAN benchmark app's grouped-stream execution branch through that front door",
            "RTDL runtime front door: fixed-radius graph component continuation",
            "Benchmark app policy: radius choice, component threshold choice",
            "Native engine: generic fixed-radius grouped union",
            "release_authorized: False",
            "public_speedup_claim_authorized: False",
            "rt_core_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
