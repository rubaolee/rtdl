from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5516RangeIntersectsCoverageLedgerTest(unittest.TestCase):
    def test_inventory_is_reconciled_without_claim_upgrade(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5516_range_intersects_coverage_ledger.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["exact_archive_pair_count"], 42)
        self.assertEqual(result["status_counts"]["matched"], 14)
        self.assertEqual(result["status_counts"]["author_capacity_failure"], 2)
        self.assertEqual(result["status_counts"]["not_checkpointed"], 26)
        self.assertTrue(result["claim_boundary"]["coverage_ledger_only"])
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])

    def test_capacity_and_uncheckpointed_states_are_explicit(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5516_range_intersects_coverage_ledger.json").read_text(
                encoding="utf-8"
            )
        )
        capacity = [case for case in result["cases"] if case["status"] == "author_capacity_failure"]
        missing = [case for case in result["cases"] if case["status"] == "not_checkpointed"]
        self.assertEqual(len(capacity), 2)
        self.assertEqual(len(missing), 26)
        self.assertTrue(all("evidence_source" in case for case in capacity))
        self.assertTrue(all("evidence_source" not in case for case in missing))


if __name__ == "__main__":
    unittest.main()
