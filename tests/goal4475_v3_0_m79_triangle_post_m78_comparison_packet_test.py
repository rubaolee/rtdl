from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4475_v3_0_m79_triangle_post_m78_comparison_packet_2026-06-16.md"
PACKET = ROOT / "docs" / "reports" / "goal4475_v3_0_m79_triangle_post_m78_comparison_packet_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4475V30M79TrianglePostM78ComparisonPacketTest(unittest.TestCase):
    def test_packet_records_post_m78_current_rows(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertEqual(4475, packet["goal"])
        self.assertEqual("post_m78_current_comparison_packet", packet["status"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(packet["claim_boundary"]["rtdl_beats_cugraph_claim_authorized"])
        self.assertLess(rows["com_lj"]["rtdl_m78_total_s"], rows["com_lj"]["rtdl_m73_total_s"])
        self.assertLess(rows["soc_livejournal1"]["rtdl_m78_total_s"], rows["soc_livejournal1"]["rtdl_m73_total_s"])
        self.assertLess(rows["com_orkut"]["rtdl_m78_total_s"], rows["com_orkut"]["rtdl_m73_total_s"])
        self.assertGreater(rows["com_orkut"]["m78_speedup_vs_m73_total"], 1.7)
        self.assertEqual(627584181, rows["com_orkut"]["count"])

    def test_packet_keeps_cugraph_and_author_kernel_boundary(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["dataset"]: row for row in packet["rows"]}

        self.assertGreater(rows["com_lj"]["cugraph_faster_than_m78_total"], 3.0)
        self.assertGreater(rows["soc_livejournal1"]["cugraph_faster_than_m78_total"], 4.8)
        self.assertGreater(rows["com_orkut"]["cugraph_faster_than_m78_total"], 4.8)
        self.assertGreater(rows["com_lj"]["m78_total_faster_than_author_rt_pipeline"], 7.9)
        self.assertGreater(rows["soc_livejournal1"]["m78_total_faster_than_author_rt_pipeline"], 5.9)
        self.assertGreater(rows["com_lj"]["m78_query_slower_than_author_rt_count"], 2.4)
        self.assertGreater(rows["soc_livejournal1"]["m78_query_slower_than_author_bs_count"], 19.0)
        self.assertEqual("failed_sigkill_after_149151_ms", rows["com_orkut"]["author_rt_status"])

    def test_report_and_registries_record_m79_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("3.15x-4.89x", report)
        self.assertIn("not public speedup wording", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4477.v1", route["version"])
        self.assertIn("Goal4475", route["evidence_refs"])
        self.assertIn("post-M78", route["user_choice_guidance"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4477.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4475", triangle["evidence_refs"])
        self.assertIn("3.15x-4.89x", triangle["current_performance_reading"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(triangle["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
