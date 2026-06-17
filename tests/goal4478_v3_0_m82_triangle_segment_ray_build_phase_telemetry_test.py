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
REPORT = (
    ROOT
    / "docs/reports/goal4478_v3_0_m82_triangle_segment_build_phase_telemetry_packet_2026-06-16.md"
)
PACKET = (
    ROOT
    / "docs/reports/goal4478_v3_0_m82_triangle_segment_build_phase_telemetry_packet_2026-06-16.json"
)


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4478V30M82TriangleSegmentRayBuildPhaseTelemetryTest(unittest.TestCase):
    def test_segment_ray_build_subphase_telemetry_is_explicit_cli_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-ray-build-telemetry", source)
        self.assertIn('choices=("none", "sync_subphases")', source)
        self.assertIn("segment_ray_build_phase_summary_ms", source)
        self.assertIn("triangle_counting.segment_ray_build_phase_summary.v1", source)
        self.assertIn("numba_key_fill", source)
        self.assertIn("cupy_unique_counts", source)
        self.assertIn("ray_column_projection_full", source)
        self.assertIn("sync_subphases", source)

    def test_invalid_segment_ray_build_telemetry_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "none or sync_subphases"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="numba_direct",
                segment_ray_build_telemetry="timeline_magic",
            )

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_segment_ray_build_subphase_summary_is_reported(self) -> None:
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
            payload = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file=str(edge_file),
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                warmup=1,
                repeat=1,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="numba_direct",
                segment_ray_build_telemetry="sync_subphases",
                validate_oracle=True,
            )

        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(4, payload["generic_rt_weighted_triangle_count"])
        self.assertEqual("sync_subphases", payload["timing_ms"]["segment_ray_build_telemetry"])
        summary = payload["timing_ms"]["segment_ray_build_phase_summary_ms"]
        self.assertEqual("triangle_counting.segment_ray_build_phase_summary.v1", summary["schema_version"])
        self.assertEqual(1, summary["run_count"])
        phase_names = set(summary["phase_names"])
        self.assertIn("numba_key_fill", phase_names)
        self.assertIn("cupy_unique_counts", phase_names)
        self.assertIn("unique_decode_weights", phase_names)
        self.assertIn("ray_column_projection_full", phase_names)
        self.assertGreater(summary["phases"]["cupy_unique_counts"]["median_ms"], 0.0)

    def test_packet_records_cupy_unique_counts_as_next_target(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(4478, packet["goal"])
        self.assertEqual("segment_ray_build_phase_telemetry_recorded", packet["status"])
        self.assertFalse(packet["claim_boundary"]["performance_optimization_claim"])
        self.assertTrue(packet["claim_boundary"]["instrumentation_claim"])
        self.assertFalse(packet["claim_boundary"]["current_best_route_changed"])
        self.assertIn("not a speedup claim", report)
        self.assertIn("next optimization target is `cupy_unique_counts`", report)

        rows = {row["dataset"]: row for row in packet["rows"]}
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))
        for row in rows.values():
            self.assertEqual("cupy_unique_counts", row["top_phase"])
            self.assertIn("cupy_unique_counts", row["phases_ms"])
            self.assertGreater(row["segment_ray_build_ms"], row["top_phase_ms"])
        self.assertGreater(rows["com_orkut"]["top_phase_percent"], 50.0)

    def test_registry_preserves_m82_evidence_after_m83_route_update(self) -> None:
        routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
        adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4485.v1",
            routes.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4485.v1",
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

        self.assertIn("Goal4478", route_row["evidence_refs"])
        self.assertIn("Goal4478", adequacy_row["evidence_refs"])
        self.assertIn("Goal4479", route_row["evidence_refs"])
        self.assertIn("Goal4479", adequacy_row["evidence_refs"])
        self.assertIn("cupy_unique_counts", route_row["current_reader_decision"])
        self.assertIn("numba_direct_sort_rle", route_row["next_runtime_action"])
        self.assertIn("sort/RLE", adequacy_row["next_generic_runtime_action"])
        self.assertIn("cupy_unique_counts", adequacy_row["current_performance_reading"])


if __name__ == "__main__":
    unittest.main()
