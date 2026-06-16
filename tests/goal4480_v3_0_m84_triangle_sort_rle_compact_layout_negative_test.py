from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs/reports/goal4480_v3_0_m84_triangle_sort_rle_compact_layout_negative_packet_2026-06-16.json"
)
REPORT = (
    ROOT
    / "docs/reports/goal4480_v3_0_m84_triangle_sort_rle_compact_layout_negative_packet_2026-06-16.md"
)


class Goal4480V30M84TriangleSortRleCompactLayoutNegativeTest(unittest.TestCase):
    def test_packet_rejects_compact_layout_candidate(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")

        self.assertEqual(4480, packet["goal"])
        self.assertEqual("compact_layout_sort_rle_candidate_rejected", packet["status"])
        self.assertTrue(packet["claim_boundary"]["negative_result_recorded"])
        self.assertFalse(packet["claim_boundary"]["performance_optimization_claim"])
        self.assertFalse(packet["claim_boundary"]["current_best_route_changed"])
        self.assertIn("Do not promote compact constant-ray columns", report)

        rows = {row["dataset"]: row for row in packet["rows"]}
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))
        for row in rows.values():
            self.assertTrue(row["same_count_rays_weights"])
            self.assertLess(row["candidate_total_speedup"], 1.0)
            self.assertGreater(row["prepared_batch_speedup"], 1.0)

    def test_registry_records_compact_layout_rejection(self) -> None:
        routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
        adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4481.v1",
            routes.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4481.v1",
            adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        route_row = {
            row["app"]: row for row in routes.current_benchmark_route_decisions()
        }["triangle_counting"]
        adequacy_row = {
            row["app"]: row for row in adequacy.current_benchmark_adequacy()
        }["triangle_counting"]

        self.assertIn("Goal4480", route_row["evidence_refs"])
        self.assertIn("Goal4480", adequacy_row["evidence_refs"])
        self.assertIn(
            "promoting the Goal4480 compact constant-ray layout retest",
            " ".join(route_row["rejected_or_unpromoted_candidates"]),
        )
        self.assertIn("full ray columns remain the current route", adequacy_row["current_performance_reading"])
        self.assertIn("compact constant-ray columns should not", route_row["next_runtime_action"])


if __name__ == "__main__":
    unittest.main()
