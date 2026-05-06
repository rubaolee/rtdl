from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1409V151CollectKBoundedContractTest(unittest.TestCase):
    def test_contract_is_app_generic_and_not_yet_public_promotion(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_contract()

        self.assertEqual(contract["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(contract["track"], "python_rtdl")
        self.assertTrue(contract["app_generic"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertEqual(contract["active_backend_scope"], ("embree", "optix"))
        self.assertEqual(contract["result_layout"], "dense_candidate_id_rows_with_valid_count")
        self.assertEqual(contract["overflow_policy"], "fail_closed_before_result_materialization")
        self.assertFalse(contract["truncation_allowed"])
        self.assertFalse(contract["partial_result_on_overflow_allowed"])
        self.assertFalse(contract["score_or_reduction_after_overflow_allowed"])
        self.assertTrue(contract["complete_candidate_coverage_required"])
        self.assertIn("not a Jaccard-specific", contract["claim_boundary"])
        self.assertIn("not a performance or zero-copy claim", contract["claim_boundary"])

    def test_collect_k_zero_accepts_zero_results(self) -> None:
        result = rt.collect_k_bounded_rows((), k=0)

        self.assertEqual(result["candidate_id_rows"], ())
        self.assertEqual(result["capacity"], 0)
        self.assertEqual(result["valid_count"], 0)
        self.assertFalse(result["overflowed"])
        self.assertTrue(result["complete_candidate_coverage"])

    def test_collect_k_zero_fails_closed_for_positive_results(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "COLLECT_K_BOUNDED overflowed capacity 0; emitted 1",
        ):
            rt.collect_k_bounded_rows((7,), k=0)

    def test_exact_k_full_buffer_succeeds_with_stable_ordering(self) -> None:
        result = rt.collect_k_bounded_rows(((2, 20), (1, 30), (1, 10)), k=3, row_width=2)

        self.assertEqual(result["candidate_id_rows"], ((1, 10), (1, 30), (2, 20)))
        self.assertEqual(result["capacity"], 3)
        self.assertEqual(result["valid_count"], 3)
        self.assertEqual(result["emitted_count"], 3)
        self.assertFalse(result["overflowed"])

    def test_k_plus_one_fails_closed_without_partial_result(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "failure_mode=fail_closed_overflow; partial_result_returned=False",
        ):
            rt.collect_k_bounded_rows(((1, 10), (2, 20), (3, 30)), k=2, row_width=2)

    def test_duplicate_rows_are_deduplicated_before_capacity_check(self) -> None:
        result = rt.collect_k_bounded_rows(((2, 20), (2, 20), (1, 10)), k=2, row_width=2)

        self.assertEqual(result["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(result["valid_count"], 2)
        self.assertEqual(result["duplicate_policy"], "deduplicate_before_capacity_check")

    def test_row_width_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate row width mismatch"):
            rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=1)

    def test_negative_k_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "capacity k must be non-negative"):
            rt.collect_k_bounded_rows((), k=-1)


if __name__ == "__main__":
    unittest.main()
