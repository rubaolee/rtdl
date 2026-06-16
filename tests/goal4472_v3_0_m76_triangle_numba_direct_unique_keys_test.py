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
REPORT = ROOT / "docs" / "reports" / "goal4472_v3_0_m76_triangle_numba_direct_unique_key_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4472_v3_0_m76_triangle_numba_direct_unique_key_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
        import numba  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4472V30M76TriangleNumbaDirectUniqueKeysTest(unittest.TestCase):
    def test_segment_unique_key_builder_is_explicit_cli_choice(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--segment-unique-key-builder", source)
        self.assertIn('choices=("cupy_repeat", "numba_direct")', source)
        self.assertIn("_get_rt_graph_2a1_fill_unique_keys_numba_kernel", source)

    def test_invalid_segment_unique_key_builder_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cupy_repeat or numba_direct"):
            app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                edge_file="missing.edge",
                edge_format="binary",
                backend="optix",
                detail="summary",
                partner="cupy",
                segment_ray_representation="unique_weighted",
                segment_query_schedule="prepared_segment_replay",
                segment_unique_key_builder="magic_keys",
            )

    def test_packet_records_mixed_total_but_backend_build_wins(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4472, packet["goal"])
        self.assertFalse(packet["claim_boundary"]["hidden_default_promotion_authorized"])
        self.assertGreater(rows["com_lj"]["segment_ray_build_speedup"], 1.1)
        self.assertGreater(rows["soc_livejournal1"]["segment_ray_build_speedup"], 1.3)
        self.assertGreater(rows["com_orkut"]["segment_ray_build_speedup"], 1.6)
        self.assertGreater(rows["com_orkut"]["backend_speedup"], 1.09)
        self.assertLess(rows["soc_livejournal1"]["total_speedup"], 1.0)
        self.assertIn("not a hidden default", packet["interpretation"]["route_decision"])

    def test_report_and_registry_record_explicit_not_default_decision(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("numba_direct", report)
        self.assertIn("hidden default", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4474.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4474.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4472", route["evidence_refs"])
        self.assertIn("Goal4472", triangle["evidence_refs"])
        self.assertIn("numba_direct", route["user_choice_guidance"])
        self.assertIn("post-M78 comparison packet", route["next_runtime_action"])
        self.assertIn("do not auto-select it", triangle["current_recommended_path"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(triangle["whole_app_speedup_claim_authorized"])

    @unittest.skipUnless(_has_cupy_optix(), "CuPy, Numba, and RTDL OptiX library are not available")
    def test_live_numba_direct_unique_keys_match_cupy_repeat(self) -> None:
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
                "repeat": 2,
                "segment_max_two_hop_rows": 100,
                "segment_ray_representation": "unique_weighted",
                "segment_query_schedule": "prepared_segment_replay",
                "validate_oracle": True,
            }
            cupy_repeat = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_unique_key_builder="cupy_repeat",
            )
            numba_direct = app.run_app(
                "rt_graph_2a1_segmented_generic_rt",
                **common,
                segment_unique_key_builder="numba_direct",
            )

        self.assertTrue(cupy_repeat["triangle_count_matches_oracle"])
        self.assertTrue(numba_direct["triangle_count_matches_oracle"])
        self.assertEqual(
            cupy_repeat["generic_rt_weighted_triangle_count"],
            numba_direct["generic_rt_weighted_triangle_count"],
        )
        self.assertEqual(cupy_repeat["ray_count"], numba_direct["ray_count"])
        self.assertEqual(
            cupy_repeat["segmentation"]["lowered_ray_weight_sum"],
            numba_direct["segmentation"]["lowered_ray_weight_sum"],
        )
        self.assertEqual("numba_direct", numba_direct["segmentation"]["segment_unique_key_builder"])
        self.assertEqual("numba_direct", numba_direct["timing_ms"]["segment_unique_key_builder"])


if __name__ == "__main__":
    unittest.main()
