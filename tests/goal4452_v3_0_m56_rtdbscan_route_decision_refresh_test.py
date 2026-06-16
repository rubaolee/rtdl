from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4452_v3_0_m56_rtdbscan_route_decision_refresh_2026-06-16.md"
EVIDENCE_INDEX = ROOT / "docs" / "learn" / "benchmark_evidence_index.md"


class Goal4452V30M56RtdbscanRouteDecisionRefreshTest(unittest.TestCase):
    def test_rtdbscan_route_is_current_output_contract_first(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4483.v1", route["version"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn('output_mode="component_signature"', route["current_reader_decision"])
        self.assertIn('output_mode="full"', route["current_reader_decision"])
        self.assertIn("Choose the output contract first", route["user_choice_guidance"])
        self.assertIn("CuPy and Numba explicitly", route["user_choice_guidance"])
        self.assertIn("full Python row materialization", route["next_runtime_action"])
        self.assertIn("Goal4445", route["evidence_refs"])
        self.assertIn("Goal4452", route["evidence_refs"])
        self.assertLess(len(route["current_reader_decision"]), 900)
        self.assertLess(len(route["user_choice_guidance"]), 900)
        self.assertFalse(route["automatic_partner_selection_authorized"])

    def test_rtdbscan_old_candidates_remain_explicit_not_defaulted(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")
        rejected = route["rejected_or_unpromoted_candidates"]

        self.assertIn(
            "partition_convergence_hybrid universal default promotion after Goal4108 prepared replay and Goal4109 app smoke",
            rejected,
        )
        self.assertIn("automatic output_mode/partner selection after Goal4452 route refresh", rejected)
        self.assertIn("profile/reuse advisor", route["next_runtime_action"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("automatic partner selection", route["next_runtime_action"])

    def test_report_and_index_record_m56_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")

        for phrase in (
            "Goal4452",
            "output contract first",
            "component_signature",
            "full Python rows",
            "does not authorize automatic partner selection",
        ):
            self.assertIn(phrase, report)
        self.assertIn("Goal4452 RT-DBSCAN route decision refresh", evidence_index)


if __name__ == "__main__":
    unittest.main()


