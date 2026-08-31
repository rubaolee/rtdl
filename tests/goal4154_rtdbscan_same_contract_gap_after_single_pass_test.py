from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4154_rtdbscan_same_contract_gap_after_single_pass_2026-06-09.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal4154RtDbscanSameContractGapAfterSinglePassTest(unittest.TestCase):
    def test_report_identifies_predicate_aware_generic_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "design-gap-identified",
            "not the same contract",
            "predicate-aware fixed-radius grouped-union continuation",
            "caller-supplied vertex predicate flags",
            "must stay generic",
            "does not authorize route promotion",
        ):
            self.assertIn(fragment, report)

    def test_future_todo_records_generic_next_primitive_not_dbscan_abi(self) -> None:
        todo = TODO.read_text(encoding="utf-8")

        for fragment in (
            "Goal4149/4150",
            "Goal4153",
            "predicate-aware direct-status",
            "grouped union",
            "caller-supplied vertex predicate",
            "do not encode DBSCAN/min-points semantics in the engine ABI",
        ):
            self.assertIn(fragment, todo)


if __name__ == "__main__":
    unittest.main()
