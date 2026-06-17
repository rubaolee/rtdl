from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4501_v3_0_m105_rtnn_author_same_input_comparison_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4501_v3_0_m105_rtnn_author_same_input_comparison_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
SCRIPT = ROOT / "scripts/goal4501_m105_rtnn_author_same_input_comparison.py"


class Goal4501V30M105RtnnAuthorSameInputComparisonTest(unittest.TestCase):
    def test_script_rebuilds_packet_from_evidence(self) -> None:
        module = importlib.import_module("scripts.goal4501_m105_rtnn_author_same_input_comparison")
        packet = module.build_packet(ROOT)
        self.assertEqual("rtdl.v3_0.rtnn_author_same_input_comparison.goal4501.v1", packet["version"])
        self.assertEqual("Goal4501 / V3 M105", packet["goal"])
        self.assertEqual(1_000_000, packet["input_contract"]["point_count"])
        self.assertEqual(5, packet["author_rtnn"]["repeat"])
        self.assertLess(packet["rtdl"]["optix_direct_graph_best"]["median_query_sec"], 0.5)
        self.assertGreater(packet["comparisons"]["rtdl_direct_graph_over_m104_generic_query"], 20.0)
        self.assertGreater(packet["comparisons"]["rtdl_direct_graph_query_over_author_total_search"], 1.0)
        self.assertGreater(packet["comparisons"]["author_compute_over_rtdl_direct_graph_query"], 10.0)
        self.assertFalse(packet["claim_boundary"]["same_output_contract_author_vs_rtdl"])
        self.assertFalse(packet["claim_boundary"]["paper_reproduction_wording_allowed"])

    def test_packet_report_and_guidance_are_refreshed(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rtnn"]

        self.assertEqual("rtdl.v3_0.rtnn_author_same_input_comparison.goal4501.v1", packet["version"])
        self.assertIn("Performance Matrix", report)
        self.assertIn("Author RTNN C++/CUDA/OptiX", report)
        self.assertIn("RTDL OptiX direct graph", report)
        self.assertIn("Same output surface: no", report)
        self.assertIn("Goal4501 RTNN author same-input comparison", index)
        self.assertIn("Goal4501 adds the author same-input comparison", readme)
        self.assertIn("AUTHOR_REPEAT_GLOB", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4503.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4503.v1", adequacy["version"])
        self.assertIn("Goal4501", route["evidence_refs"])
        self.assertIn("Goal4501", adequacy["evidence_refs"])
        self.assertIn("full-batch", route["primary_route"])
        self.assertIn("full-batch", adequacy["current_recommended_path"])


if __name__ == "__main__":
    unittest.main()
