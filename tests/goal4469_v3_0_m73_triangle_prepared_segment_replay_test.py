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
REPORT = ROOT / "docs" / "reports" / "goal4469_v3_0_m73_triangle_prepared_segment_replay_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4469_v3_0_m73_triangle_prepared_segment_replay_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4469V30M73TrianglePreparedSegmentReplayTest(unittest.TestCase):
    def test_segmented_modes_expose_prepared_segment_replay_schedule(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-query-schedule", source)
        self.assertIn('choices=("per_run", "prepared_segment_replay")', source)
        self.assertIn("segment_query_schedule", source)
        self.assertIn("prepared_segment_replay", source)

    def test_invalid_segment_query_schedule_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "per_run or prepared_segment_replay"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="rebuild_everything_forever",
            )

    def test_packet_records_prepared_replay_large_row_speedups(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4469, packet["goal"])
        self.assertEqual("prepared_segment_replay_validated", packet["status"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertGreater(rows["com_lj"]["m73_speedup_vs_m71_total"], 1.4)
        self.assertGreater(rows["soc_livejournal1"]["m73_speedup_vs_m72_total"], 1.3)
        self.assertGreater(rows["com_orkut"]["m73_speedup_vs_m71_total"], 1.8)
        self.assertLess(rows["com_orkut"]["m73_prepared_segment_replay_total_s"], 63.0)
        self.assertEqual(627_584_181, rows["com_orkut"]["count"])

    def test_report_and_registries_record_m73_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("1.43x-1.84x", report)
        self.assertIn("prepared_segment_replay", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4480.v1", route["version"])
        self.assertIn("Goal4469", route["evidence_refs"])
        self.assertIn("prepared_segment_replay", route["user_choice_guidance"])
        self.assertIn("one-shot build cost", route["next_runtime_action"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4480.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4469", triangle["evidence_refs"])
        self.assertIn("Goal4471", triangle["evidence_refs"])
        self.assertIn("prepared ray-batch weighted-sum API", triangle["next_generic_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(triangle["whole_app_speedup_claim_authorized"])

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_prepared_segment_replay_matches_per_run_schedule(self) -> None:
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
            per_run = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=1,
                repeat=2,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="per_run",
                validate_oracle=True,
            )
            prepared = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=1,
                repeat=2,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                validate_oracle=True,
            )

        self.assertTrue(per_run["triangle_count_matches_oracle"])
        self.assertTrue(prepared["triangle_count_matches_oracle"])
        self.assertEqual(per_run["generic_rt_weighted_triangle_count"], prepared["generic_rt_weighted_triangle_count"])
        self.assertEqual(per_run["ray_count"], prepared["ray_count"])
        self.assertEqual("prepared_segment_replay", prepared["segmentation"]["segment_query_schedule"])
        self.assertEqual("prepared_segment_replay", prepared["timing_ms"]["segment_query_schedule"])
        self.assertEqual(2, prepared["timing_ms"]["query_measured_runs"])


if __name__ == "__main__":
    unittest.main()


