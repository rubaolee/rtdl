from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from examples.current.research_benchmarks.triangle_counting import rt_graph_contract as contract_mod
from examples.current.research_benchmarks.triangle_counting import rtdl_triangle_counting_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
PACKET = ROOT / "docs/reports/goal4481_v3_0_m85_triangle_fused_decode_project_negative_packet_2026-06-16.json"
REPORT = ROOT / "docs/reports/goal4481_v3_0_m85_triangle_fused_decode_project_negative_packet_2026-06-16.md"


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4481V30M85TriangleFusedDecodeProjectCandidateTest(unittest.TestCase):
    def test_fused_decode_project_output_builder_is_explicit_cli_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-ray-output-builder", source)
        self.assertIn('choices=("cupy_vectorized", "numba_fused_decode_project")', source)
        self.assertIn("_get_rt_graph_2a1_fill_weighted_rays_numba_kernel", source)
        self.assertIn("numba_fused_decode_project", source)

    def test_packet_rejects_fused_decode_project_candidate(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(4481, packet["goal"])
        self.assertEqual("fused_decode_project_candidate_rejected", packet["status"])
        self.assertTrue(packet["claim_boundary"]["negative_result_recorded"])
        self.assertFalse(packet["claim_boundary"]["performance_optimization_claim"])
        self.assertFalse(packet["claim_boundary"]["current_best_route_changed"])
        self.assertIn("Do not promote", report)

        rows = {row["dataset"]: row for row in packet["rows"]}
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))
        for row in rows.values():
            self.assertTrue(row["same_count_rays_weights"])
            self.assertLess(row["candidate_total_speedup"], 1.0)
            self.assertLess(row["segment_build_speedup"], 1.0)

    def test_registry_records_fused_decode_project_rejection(self) -> None:
        routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
        adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4482.v1",
            routes.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4482.v1",
            adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        route_row = {
            row["app"]: row for row in routes.current_benchmark_route_decisions()
        }["triangle_counting"]
        adequacy_row = {
            row["app"]: row for row in adequacy.current_benchmark_adequacy()
        }["triangle_counting"]

        self.assertIn("Goal4481", route_row["evidence_refs"])
        self.assertIn("Goal4481", adequacy_row["evidence_refs"])
        self.assertIn(
            "promoting the Goal4481 numba_fused_decode_project output builder",
            " ".join(route_row["rejected_or_unpromoted_candidates"]),
        )
        self.assertIn("CuPy vectorized output remains current", adequacy_row["current_performance_reading"])
        self.assertIn("grouped/local unique-count strategy", route_row["next_runtime_action"])

    def test_fused_decode_project_rejects_unsupported_layout(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires unique_weighted rays and full ray columns"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="numba_direct_sort_rle",
                segment_ray_column_layout="xz_constant_y_direction",
                segment_ray_output_builder="numba_fused_decode_project",
            )

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_fused_decode_project_matches_cupy_vectorized_on_k4(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            edge_file = Path(tmp) / "k4.edge"
            contract_mod.write_binary_edges(
                edge_file,
                (
                    (0, 1),
                    (0, 2),
                    (0, 3),
                    (1, 2),
                    (1, 3),
                    (2, 3),
                ),
            )
            common = {
                "edge_file": str(edge_file),
                "edge_format": "binary",
                "backend": "optix",
                "detail": "summary",
                "partner": "cupy",
                "warmup": 1,
                "repeat": 1,
                "segment_max_two_hop_rows": 100,
                "segment_ray_representation": "unique_weighted",
                "segment_query_schedule": "prepared_segment_replay",
                "segment_unique_key_builder": "numba_direct_sort_rle",
                "segment_ray_build_telemetry": "sync_subphases",
                "validate_oracle": True,
            }
            cupy_vectorized = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_ray_output_builder="cupy_vectorized",
            )
            fused = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_ray_output_builder="numba_fused_decode_project",
            )

        self.assertTrue(cupy_vectorized["triangle_count_matches_oracle"])
        self.assertTrue(fused["triangle_count_matches_oracle"])
        self.assertEqual(
            cupy_vectorized["generic_rt_weighted_triangle_count"],
            fused["generic_rt_weighted_triangle_count"],
        )
        self.assertEqual(cupy_vectorized["ray_count"], fused["ray_count"])
        self.assertEqual(
            cupy_vectorized["segmentation"]["lowered_ray_weight_sum"],
            fused["segmentation"]["lowered_ray_weight_sum"],
        )
        phase_names = set(fused["timing_ms"]["segment_ray_build_phase_summary_ms"]["phase_names"])
        self.assertIn("numba_fused_decode_project", phase_names)
        self.assertNotIn("ray_column_projection_full", phase_names)


if __name__ == "__main__":
    unittest.main()
