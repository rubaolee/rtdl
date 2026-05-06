from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1411V151PolygonCollectKHelperBridgeTest(unittest.TestCase):
    def test_polygon_candidate_helper_bridges_to_generic_row_buffer_contract(self) -> None:
        result = rt.collect_k_bounded_candidate_pairs(
            ((2, 20), (1, 30), (1, 10)),
            k=3,
        )

        self.assertEqual(result["primitive"], "COLLECT_K_BOUNDED")
        self.assertTrue(result["app_generic"])
        self.assertEqual(result["candidate_pairs"], ((1, 10), (1, 30), (2, 20)))
        self.assertEqual(result["candidate_id_rows"], ((1, 10), (1, 30), (2, 20)))
        self.assertEqual(result["row_width"], 2)
        self.assertEqual(result["capacity"], 3)
        self.assertEqual(result["valid_count"], 3)
        self.assertEqual(result["emitted_count"], 3)
        self.assertEqual(result["generic_result_layout"], "dense_candidate_id_rows_with_valid_count")
        self.assertEqual(result["ordering_policy"], "stable_lexicographic_by_candidate_id_row")
        self.assertEqual(result["duplicate_policy"], "deduplicate_before_capacity_check")
        self.assertFalse(result["partial_result_on_overflow_allowed"])
        self.assertFalse(result["score_or_reduction_after_overflow_allowed"])

    def test_polygon_candidate_helper_deduplicates_before_capacity_check(self) -> None:
        result = rt.collect_k_bounded_candidate_pairs(
            ((2, 20), (2, 20), (1, 10)),
            k=2,
        )

        self.assertEqual(result["candidate_pairs"], ((1, 10), (2, 20)))
        self.assertEqual(result["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(result["valid_count"], 2)

    def test_polygon_candidate_helper_keeps_none_capacity_as_fit_to_data_compatibility(self) -> None:
        result = rt.collect_k_bounded_candidate_pairs(((2, 20), (1, 10)), k=None)

        self.assertEqual(result["capacity"], 2)
        self.assertEqual(result["valid_count"], 2)
        self.assertEqual(result["candidate_pairs"], ((1, 10), (2, 20)))

    def test_polygon_candidate_helper_overflow_uses_generic_fail_closed_message(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "COLLECT_K_BOUNDED overflowed capacity 1; emitted 2",
        ):
            rt.collect_k_bounded_candidate_pairs(((2, 20), (1, 10)), k=1)


if __name__ == "__main__":
    unittest.main()
