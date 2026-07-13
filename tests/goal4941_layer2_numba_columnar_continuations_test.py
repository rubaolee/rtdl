from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_RUNTIME = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"


def _numba_cuda_available() -> bool:
    try:
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4941Layer2NumbaColumnarContinuationsTest(unittest.TestCase):
    def test_descriptors_are_generic_layer2_numeric_continuations(self) -> None:
        midpoint = rt.describe_numba_adjacent_midpoint_candidates_i64x2_by_key()
        dedupe = rt.describe_numba_consecutive_dedupe_mask_f64x2()
        range_has = rt.describe_numba_range_has_sorted_values_i64()

        self.assertEqual(midpoint["operation"], "adjacent_midpoint_candidates_i64x2_by_key")
        self.assertEqual(midpoint["input_columns"], ("keys:int64", "values_x:int64", "values_y:int64"))
        self.assertEqual(
            midpoint["output_columns"],
            ("mid_x:int64", "mid_y:int64", "left_indices:int64", "valid_mask:bool"),
        )
        self.assertEqual(midpoint["same_key_pair_policy"], "adjacent_rows_only")
        self.assertFalse(midpoint["app_specific_semantics_allowed"])
        self.assertFalse(midpoint["host_column_materialization_used"])

        self.assertEqual(dedupe["operation"], "consecutive_dedupe_mask_f64x2")
        self.assertEqual(dedupe["output_columns"], ("keep_mask:bool",))
        self.assertEqual(dedupe["comparison_policy"], "exact_float64_pair_equality_against_previous_row")
        self.assertFalse(dedupe["app_specific_semantics_allowed"])

        self.assertEqual(range_has["operation"], "range_has_sorted_values_i64")
        self.assertEqual(range_has["range_contract"], "half_open_start_start_plus_length")
        self.assertTrue(range_has["requires_sorted_values"])
        self.assertFalse(range_has["app_specific_semantics_allowed"])

    def test_operations_are_registered_as_numba_preview_without_rayjoin_identity(self) -> None:
        for operation in (
            "adjacent_midpoint_candidates_i64x2_by_key",
            "consecutive_dedupe_mask_f64x2",
            "range_has_sorted_values_i64",
        ):
            self.assertIn(operation, rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
            self.assertIn(operation, rt.V2_5_NUMBA_PREVIEW_OPERATIONS)
            support = rt.plan_v2_5_partner_support(operation, "numba")
            self.assertTrue(support["supported"])
            self.assertEqual(support["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
            self.assertFalse(support["public_speedup_claim_authorized"])
            self.assertFalse(support["true_zero_copy_claim_authorized"])

        runtime_source = NUMBA_RUNTIME.read_text(encoding="utf-8").lower()
        for function_name in (
            "run_numba_adjacent_midpoint_candidates_i64x2_by_key",
            "run_numba_consecutive_dedupe_mask_f64x2",
            "run_numba_range_has_sorted_values_i64",
        ):
            self.assertIn(f"def {function_name}", runtime_source)
        self.assertNotIn("rayjoin", runtime_source)
        self.assertNotIn("overlay", runtime_source)
        self.assertNotIn("polygon", runtime_source)

    def test_numba_cuda_columnar_continuations_match_reference_when_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        keys = cuda.to_device(np.asarray([1, 1, 1, 2, 3, 3], dtype=np.int64))
        values_x = cuda.to_device(np.asarray([10, 12, -13, 4, 5, 8], dtype=np.int64))
        values_y = cuda.to_device(np.asarray([0, 2, -3, 9, 10, 14], dtype=np.int64))
        midpoint = rt.run_numba_adjacent_midpoint_candidates_i64x2_by_key(keys, values_x, values_y)
        self.assertEqual(midpoint["operation"], rt.NUMBA_ADJACENT_MIDPOINT_CANDIDATES_I64X2_BY_KEY_OPERATION)
        self.assertTrue(np.array_equal(midpoint["outputs"]["valid_mask"].copy_to_host(), [True, True, False, False, True]))
        self.assertTrue(np.array_equal(midpoint["outputs"]["left_indices"].copy_to_host(), [0, 1, 2, 3, 4]))
        self.assertTrue(np.array_equal(midpoint["outputs"]["mid_x"].copy_to_host(), [11, 0, 0, 0, 6]))
        self.assertTrue(np.array_equal(midpoint["outputs"]["mid_y"].copy_to_host(), [1, 0, 0, 0, 12]))
        self.assertFalse(midpoint["app_specific_semantics_allowed"])
        self.assertFalse(midpoint["host_column_materialization_used"])

        point_x = cuda.to_device(np.asarray([1.0, 1.0, 2.5, 2.5, 2.5, -0.0], dtype=np.float64))
        point_y = cuda.to_device(np.asarray([3.0, 3.0, 4.0, 5.0, 5.0, -0.0], dtype=np.float64))
        dedupe = rt.run_numba_consecutive_dedupe_mask_f64x2(point_x, point_y)
        self.assertTrue(np.array_equal(dedupe["outputs"]["keep_mask"].copy_to_host(), [True, False, True, True, False, True]))
        self.assertEqual(dedupe["operation"], rt.NUMBA_CONSECUTIVE_DEDUPE_MASK_F64X2_OPERATION)

        starts = cuda.to_device(np.asarray([0, 3, 5, 8], dtype=np.int64))
        lengths = cuda.to_device(np.asarray([2, 2, 0, 4], dtype=np.int64))
        sorted_values = cuda.to_device(np.asarray([1, 4, 4, 9, 12], dtype=np.int64))
        range_has = rt.run_numba_range_has_sorted_values_i64(starts, lengths, sorted_values)
        self.assertTrue(np.array_equal(range_has["outputs"]["has_value"].copy_to_host(), [True, True, False, True]))
        self.assertEqual(range_has["operation"], rt.NUMBA_RANGE_HAS_SORTED_VALUES_I64_OPERATION)

    def test_range_validation_rejects_bad_inputs_when_cuda_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        with self.assertRaisesRegex(ValueError, "sorted_values must be sorted"):
            rt.run_numba_range_has_sorted_values_i64(
                cuda.to_device(np.asarray([0], dtype=np.int64)),
                cuda.to_device(np.asarray([4], dtype=np.int64)),
                cuda.to_device(np.asarray([2, 1], dtype=np.int64)),
            )
        with self.assertRaisesRegex(ValueError, "range_lengths must be non-negative"):
            rt.run_numba_range_has_sorted_values_i64(
                cuda.to_device(np.asarray([0], dtype=np.int64)),
                cuda.to_device(np.asarray([-1], dtype=np.int64)),
                cuda.to_device(np.asarray([1, 2], dtype=np.int64)),
            )


if __name__ == "__main__":
    unittest.main()
