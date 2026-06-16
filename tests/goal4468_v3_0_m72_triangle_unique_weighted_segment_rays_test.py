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
REPORT = ROOT / "docs" / "reports" / "goal4468_v3_0_m72_triangle_unique_weighted_comparison_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4468_v3_0_m72_triangle_unique_weighted_comparison_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4468V30M72TriangleUniqueWeightedSegmentRaysTest(unittest.TestCase):
    def test_segmented_modes_expose_explicit_unique_weighted_ray_representation(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-ray-representation", source)
        self.assertIn('choices=("duplicate", "unique_weighted")', source)
        self.assertIn("segmented unique weighted 2-hop relation rays", source)
        self.assertIn("segment_ray_representation", source)
        self.assertIn("ray_compression_ratio", source)

    def test_invalid_segment_ray_representation_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate or unique_weighted"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="graph_magic",
            )

    def test_packet_records_large_row_tradeoff(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4468, packet["goal"])
        self.assertEqual("unique_weighted_segment_ray_representation_validated", packet["status"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertEqual(177_820_130, rows["com_lj"]["observed_triangle_count"])
        self.assertEqual(285_730_264, rows["soc_livejournal1"]["observed_triangle_count"])
        self.assertEqual(627_584_181, rows["com_orkut"]["observed_triangle_count"])
        self.assertGreater(rows["com_lj"]["ray_compression_ratio"], 1.7)
        self.assertGreater(rows["soc_livejournal1"]["query_speedup"], 2.4)
        self.assertGreater(rows["com_orkut"]["query_speedup"], 2.4)
        self.assertGreater(rows["com_orkut"]["ray_build_slowdown"], 2.4)
        self.assertLess(rows["com_orkut"]["total_speedup"], 1.0)

    def test_report_and_registries_record_m72_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("2.36x-2.47x", report)
        self.assertIn("2.44x-2.50x slower", report)
        self.assertIn("Goal4468", route["evidence_refs"])
        self.assertIn("unique_weighted", route["user_choice_guidance"])
        self.assertIn("prepared ray-batch weighted-sum API", route["next_runtime_action"])
        self.assertIn("Goal4468", triangle["evidence_refs"])
        self.assertIn("prepared ray-batch weighted-sum API", triangle["next_generic_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(triangle["public_speedup_claim_authorized"])

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_unique_weighted_segment_rays_match_duplicate_route(self) -> None:
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
            duplicate = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=0,
                repeat=1,
                segment_max_two_hop_rows=100,
                segment_ray_representation="duplicate",
                validate_oracle=True,
            )
            unique = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=0,
                repeat=1,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                validate_oracle=True,
            )

        self.assertTrue(duplicate["triangle_count_matches_oracle"])
        self.assertTrue(unique["triangle_count_matches_oracle"])
        self.assertEqual(duplicate["generic_rt_weighted_triangle_count"], unique["generic_rt_weighted_triangle_count"])
        self.assertEqual(unique["logical_ray_count"], duplicate["logical_ray_count"])
        self.assertLess(unique["ray_count"], duplicate["ray_count"])
        self.assertEqual(unique["segmentation"]["lowered_ray_weight_sum"], unique["logical_ray_count"])
        self.assertGreater(unique["segmentation"]["ray_compression_ratio"], 1.0)

    def test_registries_still_keep_triangle_speedup_claims_blocked(self) -> None:
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4479.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4479.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(triangle["broad_rt_core_claim_authorized"])


if __name__ == "__main__":
    unittest.main()



