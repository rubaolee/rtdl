from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4043_rtdbscan_route_refresh_after_partition_candidate_2026-06-08.md"


class Goal4043RtdbscanRouteRefreshAfterPartitionCandidateTest(unittest.TestCase):
    def test_rtdbscan_route_records_partition_candidate_without_promoting_it(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("numba_continuation", route["decision_kind"])
        self.assertEqual("numba", route["partner_policy"])
        self.assertIn("unblocked RTDL/OptiX grouped stream", route["current_reader_decision"])
        self.assertIn("partition_convergence_hybrid", route["current_reader_decision"])
        self.assertIn("not a default speed win", route["current_reader_decision"])
        self.assertIn(
            "partition_convergence_hybrid default promotion after Goal4041 mixed timing",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("fused resident component-label continuation", route["next_runtime_action"])
        self.assertIn("prepared/native partition handle", route["next_runtime_action"])
        self.assertIn("Goal4040", route["evidence_refs"])
        self.assertIn("Goal4041", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])

    def test_rtdbscan_adequacy_records_mixed_candidate_timing(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}
        row = rows["rt_dbscan"]

        self.assertEqual("strong", row["adequacy"])
        self.assertIn("partition_convergence_hybrid", row["current_performance_reading"])
        self.assertIn("timing is mixed", row["current_performance_reading"])
        self.assertIn("not promoted", row["current_performance_reading"])
        self.assertIn("fused resident component-label continuation", row["next_generic_runtime_action"])
        self.assertIn("prepared/native partition handle", row["next_generic_runtime_action"])
        self.assertIn("Goal4040", row["evidence_refs"])
        self.assertIn("Goal4041", row["evidence_refs"])
        self.assertFalse(row["automatic_partner_selection_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["broad_rt_core_claim_authorized"])

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "promoted RT-DBSCAN-style route remains",
            "partition_convergence_hybrid",
            "default route",
            "resident component-label continuation",
            "prepared/native partition handle",
            "authorize release action",
            "automatic partner selection",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
