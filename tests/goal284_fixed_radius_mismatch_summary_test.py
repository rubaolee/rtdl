import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal284FixedRadiusMismatchSummaryTest(unittest.TestCase):
    def test_summary_reports_missing_and_extra_pairs(self) -> None:
        reference_rows = (
            {"query_id": 1, "neighbor_id": 10, "distance": 0.0},
            {"query_id": 2, "neighbor_id": 20, "distance": 0.1},
        )
        candidate_rows = (
            {"query_id": 1, "neighbor_id": 11, "distance": 0.2},
            {"query_id": 2, "neighbor_id": 20, "distance": 0.1},
        )
        summary = rt.summarize_fixed_radius_mismatch(
            reference_rows,
            candidate_rows,
            strict_parity_ok=False,
        )
        self.assertFalse(summary.strict_parity_ok)
        self.assertEqual(summary.missing_pair_count, 1)
        self.assertEqual(summary.extra_pair_count, 1)
        self.assertEqual(summary.first_missing_pair, (1, 10))
        self.assertEqual(summary.first_extra_pair, (1, 11))
        self.assertEqual(summary.first_reference_row, reference_rows[0])
        self.assertEqual(summary.first_candidate_row, candidate_rows[0])


if __name__ == "__main__":
    unittest.main()
