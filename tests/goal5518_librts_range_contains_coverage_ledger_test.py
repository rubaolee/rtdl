from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5518_range_contains_coverage_ledger.json"


class Goal5518RangeContainsCoverageLedgerTest(unittest.TestCase):
    def test_coverage_states_are_exact(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(result["exact_archive_pair_count"], 14)
        self.assertEqual(result["status_counts"], {"matched": 4, "not_checkpointed": 10})
        self.assertEqual(len(result["cases"]), 14)
        self.assertEqual(len({(case["geometry"], case["query"]) for case in result["cases"]}), 14)

    def test_missing_evidence_is_not_promoted(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        missing = [case for case in result["cases"] if case["status"] == "not_checkpointed"]
        self.assertEqual(len(missing), 10)
        self.assertTrue(all("evidence_source" not in case for case in missing))
        boundary = result["claim_boundary"]
        self.assertTrue(boundary["coverage_ledger_only"])
        self.assertFalse(boundary["complete_range_contains_matrix_claimed"])
        self.assertFalse(boundary["pointwise_containment_equivalence_claimed"])


if __name__ == "__main__":
    unittest.main()
