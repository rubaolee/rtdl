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
PACKET = ROOT / "docs/reports/goal4479_v3_0_m83_triangle_sort_rle_unique_count_packet_2026-06-16.json"
REPORT = ROOT / "docs/reports/goal4479_v3_0_m83_triangle_sort_rle_unique_count_packet_2026-06-16.md"


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4479V30M83TriangleSortRleUniqueCountsCandidateTest(unittest.TestCase):
    def test_sort_rle_unique_count_candidate_is_explicit_cli_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("numba_direct_sort_rle", source)
        self.assertIn("_unique_counts_sort_rle_cupy", source)
        self.assertIn("cupy_sort_rle_counts", source)
        self.assertIn('choices=("cupy_repeat", "numba_direct", "numba_direct_sort_rle")', source)

    def test_packet_records_positive_same_commit_candidate(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(4479, packet["goal"])
        self.assertEqual("sort_rle_unique_count_candidate_positive", packet["status"])
        self.assertTrue(packet["claim_boundary"]["internal_performance_optimization_claim"])
        self.assertTrue(packet["claim_boundary"]["current_best_route_changed"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertIn("M83 is a real internal optimization", report)
        self.assertIn("no public speedup claim", report)

        rows = {row["dataset"]: row for row in packet["performance_rows"]}
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))
        for row in rows.values():
            self.assertTrue(row["same_count_rays_weights"])
            self.assertGreater(row["total_speedup"], 1.05)
            self.assertGreater(row["segment_build_speedup"], 1.10)
            self.assertIn("candidate_telemetry_sort_rle_s", row)
        self.assertGreater(rows["com_orkut"]["candidate_telemetry_sort_rle_s"], 5.0)

    def test_registry_promotes_sort_rle_as_internal_route(self) -> None:
        routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
        adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4483.v1",
            routes.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4483.v1",
            adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        route_rows = {
            row["app"]: row for row in routes.current_benchmark_route_decisions()
        }
        adequacy_rows = {
            row["app"]: row for row in adequacy.current_benchmark_adequacy()
        }
        route_row = route_rows["triangle_counting"]
        adequacy_row = adequacy_rows["triangle_counting"]

        self.assertIn("Goal4479", route_row["evidence_refs"])
        self.assertIn("Goal4479", adequacy_row["evidence_refs"])
        self.assertIn("numba_direct_sort_rle", route_row["user_choice_guidance"])
        self.assertIn("numba_direct_sort_rle", route_row["next_runtime_action"])
        self.assertIn("numba_direct_sort_rle", adequacy_row["current_partner_role"])
        self.assertIn("sort/RLE", adequacy_row["next_generic_runtime_action"])

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_sort_rle_matches_numba_direct_on_k4(self) -> None:
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
                "segment_ray_build_telemetry": "sync_subphases",
                "validate_oracle": True,
            }
            numba_direct = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_unique_key_builder="numba_direct",
            )
            sort_rle = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_unique_key_builder="numba_direct_sort_rle",
            )

        self.assertTrue(numba_direct["triangle_count_matches_oracle"])
        self.assertTrue(sort_rle["triangle_count_matches_oracle"])
        self.assertEqual(
            numba_direct["generic_rt_weighted_triangle_count"],
            sort_rle["generic_rt_weighted_triangle_count"],
        )
        self.assertEqual(numba_direct["ray_count"], sort_rle["ray_count"])
        self.assertEqual(
            numba_direct["segmentation"]["lowered_ray_weight_sum"],
            sort_rle["segmentation"]["lowered_ray_weight_sum"],
        )
        self.assertEqual(
            "numba_direct_sort_rle",
            sort_rle["segmentation"]["segment_unique_key_builder"],
        )
        phase_names = set(sort_rle["timing_ms"]["segment_ray_build_phase_summary_ms"]["phase_names"])
        self.assertIn("cupy_sort_rle_counts", phase_names)
        self.assertNotIn("cupy_unique_counts", phase_names)


if __name__ == "__main__":
    unittest.main()
