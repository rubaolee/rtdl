from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4492M96TriangleSourceGroupUniqueFeasibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["dataset"]: row for row in cls.packet["rows"]}

    def test_packet_records_paper_scale_source_group_tail(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.triangle_source_group_unique_feasibility.goal4492.v1",
            self.packet["version"],
        )
        self.assertEqual(3, self.packet["case_count"])
        self.assertEqual(3, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertEqual(
            [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 65536],
            self.packet["thresholds"],
        )
        self.assertTrue(JSONL.exists())
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(self.rows))

        orkut = self.rows["com_orkut"]
        self.assertEqual(8_579_930_671, orkut["total_two_hop_rows"])
        self.assertGreater(orkut["max_source_two_hop_rows"], 100_000)
        self.assertGreater(orkut["source_two_hop_quantiles"]["99"], 30_000)
        self.assertLess(orkut["bounded_source_group_coverage"]["8192"]["two_hop_pct"], 61.0)
        self.assertGreater(orkut["bounded_source_group_coverage"]["8192"]["two_hop_pct"], 55.0)
        self.assertLess(orkut["bounded_source_group_coverage"]["16384"]["two_hop_pct"], 72.0)
        self.assertGreater(orkut["bounded_source_group_coverage"]["16384"]["two_hop_pct"], 65.0)
        self.assertGreater(orkut["bounded_source_group_coverage"]["65536"]["two_hop_pct"], 98.0)

    def test_claim_boundary_is_feasibility_only(self) -> None:
        boundary = self.packet["claim_boundary"]

        self.assertTrue(boundary["feasibility_only"])
        self.assertFalse(boundary["route_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["native_engine_customization"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])
        self.assertIn("hybrid/two-pass", self.packet["decision"])

    def test_report_index_and_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("triangle_counting")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["triangle_counting"]

        self.assertIn("Goal4492", report)
        self.assertIn("hybrid/two-pass", report)
        self.assertIn("Goal4492 Triangle source-group unique feasibility", index)
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4499.v1",
            route["version"],
        )
        self.assertIn("Goal4492", route["evidence_refs"])
        self.assertIn("Goal4494", route["next_runtime_action"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4499.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("Goal4492", adequacy["evidence_refs"])
        self.assertIn("Goal4494", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
