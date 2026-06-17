from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "docs/reports/goal4482_v3_0_m86_triangle_grouped_unique_source_group_stats_2026-06-16.json"
REPORT = ROOT / "docs/reports/goal4482_v3_0_m86_triangle_grouped_unique_feasibility_packet_2026-06-16.md"


class Goal4482V30M86TriangleGroupedUniqueFeasibilityTest(unittest.TestCase):
    def test_source_group_stats_reject_already_sorted_fast_path(self) -> None:
        payload = json.loads(STATS.read_text(encoding="utf-8"))

        self.assertEqual(4482, payload["goal"])
        self.assertEqual("source_group_sorted_fast_path_feasibility_rejected", payload["status"])
        self.assertEqual(
            "Triangle Counting unique_weighted + numba_direct_sort_rle + prepared_segment_replay source-group feasibility scout",
            payload["route_context"],
        )
        rows = {row["dataset"]: row for row in payload["rows"]}
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))

        expected_twohop = {
            "com_lj": 928731472,
            "soc_livejournal1": 1383299326,
            "com_orkut": 8579930671,
        }
        for dataset, row in rows.items():
            self.assertEqual("cupy_directed_csr", row["contract_partner"])
            self.assertGreater(row["source_groups"], 3_000_000)
            self.assertEqual(expected_twohop[dataset], row["group_twohop"]["sum"])
            self.assertLess(row["sorted_fast_path"]["sorted_twohop_pct"], 1.0)

    def test_report_records_no_route_change_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Do not implement", report)
        self.assertIn("already sorted source group", report)
        self.assertIn("negative feasibility result, not a route change", report)
        self.assertIn("true lower-overhead grouped/local unique-count strategy", report)
        self.assertIn("no app-specific native engine callback", report)

    def test_registry_records_goal4482_feasibility_decision(self) -> None:
        routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
        adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4486.v1",
            routes.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4486.v1",
            adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        route_row = {
            row["app"]: row for row in routes.current_benchmark_route_decisions()
        }["triangle_counting"]
        adequacy_row = {
            row["app"]: row for row in adequacy.current_benchmark_adequacy()
        }["triangle_counting"]

        self.assertIn("Goal4482", route_row["evidence_refs"])
        self.assertIn("Goal4482", adequacy_row["evidence_refs"])
        self.assertIn(
            "already-sorted source-group skip-sort fast path",
            " ".join(route_row["rejected_or_unpromoted_candidates"]),
        )
        self.assertIn("sorted two-hop row coverage is below 1%", route_row["next_runtime_action"])
        self.assertIn("sorted two-hop row coverage is below 1%", adequacy_row["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
