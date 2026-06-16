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
CONTRACT = ROOT / "examples/current/research_benchmarks/triangle_counting/rt_graph_contract.py"
REPORT = ROOT / "docs" / "reports" / "goal4461_v3_0_m65_triangle_segmented_2a1_2026-06-16.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal4461_v3_0_m65_triangle_segmented_2a1_200000_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")


def _has_cupy_optix() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    optix_library = os.environ.get("RTDL_OPTIX_LIBRARY")
    return bool(optix_library and Path(optix_library).exists())


class Goal4461V30M65TriangleSegmented2A1Test(unittest.TestCase):
    def test_segment_planner_bounds_ranges_without_splitting_single_oversized_edge(self) -> None:
        ranges = app._segment_edge_ranges_from_counts((3, 4, 10, 1, 2), max_two_hop_rows=5)

        self.assertEqual(ranges, ((0, 1, 3), (1, 2, 4), (2, 3, 10), (3, 5, 3)))

    def test_segmented_route_source_skips_global_two_hop_summary(self) -> None:
        app_source = APP.read_text(encoding="utf-8")
        contract_source = CONTRACT.read_text(encoding="utf-8")

        self.assertIn("materialize_two_hop_summary: bool = True", contract_source)
        self.assertIn("two_hop_summary_materialized", contract_source)
        self.assertIn("CuPy directed-CSR route skipped global two-hop summary materialization", contract_source)
        self.assertIn("rt_graph_2a1_segmented_generic_rt", app_source)
        self.assertIn("materialize_two_hop_summary=False", app_source)
        self.assertIn("global_two_hop_summary_materialized", app_source)

    @unittest.skipUnless(_has_cupy_optix(), "CuPy plus RTDL OptiX library are not available")
    def test_live_segmented_route_matches_small_oracle(self) -> None:
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
                warmup=0,
                repeat=1,
                segment_max_two_hop_rows=2,
                validate_oracle=True,
            )

        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(payload["oracle_triangle_count"], 4)
        self.assertEqual(payload["generic_rt_weighted_triangle_count"], 4)
        self.assertGreater(payload["segmentation"]["segment_count"], 1)
        self.assertFalse(payload["primitive_layout"]["global_two_hop_summary_materialized"])
        self.assertFalse(payload["partner_timing_ms"]["two_hop_summary_materialized"])
        self.assertFalse(payload["rt_graph_contract"]["partner_timing_ms"]["two_hop_summary_materialized"])

    def test_report_evidence_and_route_record_m65_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        route = routes.explain_current_benchmark_route("triangle_counting")

        self.assertIn("Goal4461", report)
        self.assertIn("segmented duplicate two-hop rays", report)
        self.assertIn("not a triangle-counting RT-core speedup claim", report)
        self.assertEqual(4461, evidence["goal"])
        self.assertEqual("segmented_2a1_cupy_directed_csr", evidence["implementation"])
        self.assertFalse(evidence["comparison"]["global_two_hop_summary_materialized"])
        self.assertTrue(evidence["comparison"]["triangle_count_matches_oracle"])
        self.assertGreater(evidence["comparison"]["segment_count"], 1)
        self.assertIn("Goal4461", route["evidence_refs"])
        self.assertIn("segmented duplicate two-hop", route["current_reader_decision"])
        self.assertFalse(route["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
