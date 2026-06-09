from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4094_current_route_decision_after_non_skip_partition_stream_2026-06-09.md"


class Goal4094CurrentRouteDecisionAfterNonSkipPartitionStreamTest(unittest.TestCase):
    def test_rtdbscan_route_records_goal4093_without_promoting_it(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4097.v1", route["version"])
        self.assertIn("unblocked RTDL/OptiX grouped stream plus Numba", route["current_reader_decision"])
        self.assertIn("Goal4093", route["current_reader_decision"])
        self.assertIn("1.5x-2.6x fewer rows", route["current_reader_decision"])
        self.assertIn("1.06x-1.14x", route["current_reader_decision"])
        self.assertIn("Goal4096", route["current_reader_decision"])
        self.assertIn("still does not beat the recommended route", route["current_reader_decision"])
        self.assertIn(
            "partition_convergence_hybrid non-skip default promotion after Goal4093 active-pair stream evidence",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertIn("repeated-scan work", route["next_runtime_action"])
        self.assertIn("production timing that beats the current grouped-stream Numba route", route["next_runtime_action"])
        self.assertIn("Goal4093", route["evidence_refs"])
        self.assertIn("Goal4096", route["evidence_refs"])
        self.assertEqual("numba", route["partner_policy"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])
        self.assertFalse(route["whole_app_speedup_claim_authorized"])

    def test_registry_summary_stays_non_authorizing(self) -> None:
        summary = rt.summarize_current_benchmark_route_decisions()
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual("rtdl.v2_10.current_benchmark_route_decisions.goal4097.v1", summary["version"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

    def test_report_documents_non_skip_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "RTDL/OptiX fixed-radius grouped stream",
            "Numba component/signature continuation",
            "1.795x",
            "2.635x",
            "0.815x",
            "partition-convergence preview remains explicit and unpromoted",
            "does not authorize release action",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
