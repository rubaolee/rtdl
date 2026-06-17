from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4467_v3_0_m71_triangle_current_comparison_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4467_v3_0_m71_triangle_current_comparison_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4467V30M71TriangleCurrentComparisonPacketTest(unittest.TestCase):
    def test_packet_records_current_exact_large_rows(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4467, packet["goal"])
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))
        self.assertEqual(177_820_130, rows["com_lj"]["observed_triangle_count"])
        self.assertEqual(285_730_264, rows["soc_livejournal1"]["observed_triangle_count"])
        self.assertEqual(627_584_181, rows["com_orkut"]["observed_triangle_count"])
        self.assertLess(rows["com_lj"]["rt_dl_current"]["total_ms"], 15_000)
        self.assertLess(rows["soc_livejournal1"]["rt_dl_current"]["total_ms"], 26_000)
        self.assertLess(rows["com_orkut"]["rt_dl_current"]["total_ms"], 116_000)

    def test_packet_keeps_cugraph_and_author_kernel_boundary(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertGreater(rows["com_lj"]["ratios"]["cugraph_faster_than_rtdl_total"], 8.0)
        self.assertGreater(rows["soc_livejournal1"]["ratios"]["cugraph_faster_than_rtdl_total"], 10.0)
        self.assertGreater(rows["com_orkut"]["ratios"]["cugraph_faster_than_rtdl_total"], 15.0)
        self.assertGreater(rows["com_lj"]["ratios"]["rtdl_query_slower_than_author_rt_count"], 25.0)
        self.assertGreater(rows["soc_livejournal1"]["ratios"]["rtdl_query_slower_than_author_bs_count"], 200.0)
        self.assertEqual("failed", rows["com_orkut"]["author_rt_goal2593"]["status"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_and_registries_record_no_speedup_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("cuGraph remains 8.26x-15.91x faster", report)
        self.assertIn("authors pure count kernels are much faster", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4485.v1", route["version"])
        self.assertIn("Goal4467", route["evidence_refs"])
        self.assertIn("no-speedup boundary", route["user_choice_guidance"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4485.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4467", triangle["evidence_refs"])
        self.assertIn("prepared ray-batch weighted-sum API", triangle["next_generic_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(triangle["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()



