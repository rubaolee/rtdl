from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4455_v3_0_m59_triangle_partner_rerank_after_m58_2026-06-16.md"
EVIDENCE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4455_v3_0_m59_triangle_partner_rerank_after_m58_200000_2026-06-16.json"
)

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")


class Goal4455V30M59TrianglePartnerRerankAfterM58Test(unittest.TestCase):
    def test_evidence_keeps_cupy_as_performance_partner(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual(4455, evidence["goal"])
        self.assertEqual("triangle_partner_rerank_after_m58", evidence["implementation"])
        self.assertTrue(evidence["comparison"]["all_triangle_counts_match_oracle"])
        self.assertEqual("cupy", evidence["comparison"]["current_performance_partner"])
        self.assertEqual("no_cpp_python_source_reference", evidence["comparison"]["numba_role"])
        self.assertGreater(evidence["comparison"]["cupy_faster_than_numba_by_mode"]["rt_graph_2a1_generic_rt"], 2.8)
        self.assertGreater(evidence["comparison"]["cupy_faster_than_numba_by_mode"]["rt_graph_1a2_generic_rt"], 2.8)

    def test_report_and_route_record_post_m58_rerank(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")

        self.assertIn("Goal4455", report)
        self.assertIn("CuPy remains the large-scale performance route", report)
        self.assertIn("does not authorize automatic partner selection", report)
        self.assertIn("Goal4455", route["evidence_refs"])
        self.assertIn("CuPy remains the measured performance partner", route["current_reader_decision"])
        self.assertIn("Numba remains the no-C++ reference", route["user_choice_guidance"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
