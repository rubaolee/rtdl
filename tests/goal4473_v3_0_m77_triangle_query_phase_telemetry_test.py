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
REPORT = ROOT / "docs" / "reports" / "goal4473_v3_0_m77_triangle_query_phase_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4473_v3_0_m77_triangle_query_phase_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4473V30M77TriangleQueryPhaseTelemetryTest(unittest.TestCase):
    def test_backend_query_phase_summary_math(self) -> None:
        summary = app._backend_query_phase_summary_ms(
            [
                {"query_pack": 1.0, "traversal": 10.0},
                {"query_pack": 3.0, "traversal": 14.0},
                {"query_pack": 2.0, "traversal": 12.0},
            ]
        )

        self.assertEqual("triangle_counting.backend_query_phase_summary.v1", summary["schema_version"])
        self.assertEqual(3, summary["run_count"])
        self.assertEqual(2.0, summary["phases"]["query_pack"]["median_ms"])
        self.assertEqual(12.0, summary["phases"]["traversal"]["median_ms"])
        self.assertEqual(36.0, summary["phases"]["traversal"]["total_ms"])

    def test_segmented_app_exposes_backend_query_phase_summary(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("backend_query_phase_summary_ms", source)
        self.assertIn("_accumulate_backend_query_phase_ms", source)
        self.assertIn("triangle_counting.backend_query_phase_summary.v1", source)

    def test_packet_records_m77_query_phase_reading(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4473, packet["goal"])
        self.assertFalse(packet["claim_boundary"]["hidden_default_promotion_authorized"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertGreater(rows["com_lj"]["total_speedup"], 1.08)
        self.assertGreater(rows["soc_livejournal1"]["total_speedup"], 1.07)
        self.assertGreater(rows["com_orkut"]["total_speedup"], 1.11)
        self.assertGreater(rows["com_orkut"]["segment_ray_build_speedup"], 1.6)
        self.assertAlmostEqual(1.0, rows["com_lj"]["native_traversal_speedup"], delta=0.01)
        self.assertAlmostEqual(1.0, rows["soc_livejournal1"]["native_known_query_speedup"], delta=0.01)
        self.assertAlmostEqual(1.0, rows["com_orkut"]["native_known_query_speedup"], delta=0.01)
        self.assertIn("replay/envelope", packet["interpretation"]["query_wall_result"])

    def test_report_and_registry_record_query_phase_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("Native pack median", report)
        self.assertIn("replay envelope", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4486.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4486.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4473", route["evidence_refs"])
        self.assertIn("Goal4473", triangle["evidence_refs"])
        self.assertIn("native query pack/traversal", route["user_choice_guidance"])
        self.assertIn("post-M78 comparison packet", route["next_runtime_action"])
        self.assertIn("native pack/traversal", triangle["next_generic_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(triangle["public_speedup_claim_authorized"])

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_prepared_segment_replay_reports_pack_and_traversal(self) -> None:
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
                repeat=2,
                segment_max_two_hop_rows=100,
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="cupy_repeat",
                validate_oracle=True,
            )

        summary = payload["timing_ms"]["backend_query_phase_summary_ms"]
        self.assertEqual(2, summary["run_count"])
        self.assertIn("query_pack", summary["phases"])
        self.assertIn("traversal", summary["phases"])
        self.assertGreaterEqual(summary["phases"]["query_pack"]["median_ms"], 0.0)
        self.assertGreater(summary["phases"]["traversal"]["median_ms"], 0.0)
        self.assertTrue(payload["triangle_count_matches_oracle"])


if __name__ == "__main__":
    unittest.main()
