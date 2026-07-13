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


class Goal4946NativeDeviceColumnsNumbaExecutionTest(unittest.TestCase):
    def test_uint32_equal_mask_is_registered_as_generic_numba_preview(self) -> None:
        self.assertIn(rt.NUMBA_UINT32_EQUAL_MASK_OPERATION, rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
        self.assertIn(rt.NUMBA_UINT32_EQUAL_MASK_OPERATION, rt.V2_5_NUMBA_PREVIEW_OPERATIONS)

        descriptor = rt.describe_numba_uint32_equal_mask()
        self.assertEqual(descriptor["operation"], "uint32_equal_mask")
        self.assertEqual(descriptor["input_columns"], ("values:uint32",))
        self.assertEqual(descriptor["scalar_inputs"], ("target:uint32",))
        self.assertEqual(descriptor["output_columns"], ("mask:bool",))
        self.assertFalse(descriptor["app_specific_semantics_allowed"])
        self.assertFalse(descriptor["host_column_materialization_used"])

        support = rt.plan_v2_5_partner_support("uint32_equal_mask", "numba")
        self.assertTrue(support["supported"])
        self.assertEqual(support["status"], rt.V2_5_STATUS_PREVIEW_NOT_PROMOTED)
        self.assertFalse(support["public_speedup_claim_authorized"])
        self.assertFalse(support["true_zero_copy_claim_authorized"])

    def test_numba_runtime_does_not_gain_app_identity_terms(self) -> None:
        runtime_source = NUMBA_RUNTIME.read_text(encoding="utf-8").lower()
        self.assertIn("def run_numba_uint32_equal_mask", runtime_source)
        for forbidden in ("rayjoin", "overlay", "polygon", "output_chain", "authorofficial"):
            self.assertNotIn(forbidden, runtime_source)

    def test_uint32_equal_mask_executes_on_cuda_when_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        values = cuda.to_device(np.asarray([1, 7, 7, 2, 9, 7], dtype=np.uint32))
        result = rt.run_numba_uint32_equal_mask(values, target=7)

        self.assertEqual(result["operation"], rt.NUMBA_UINT32_EQUAL_MASK_OPERATION)
        self.assertTrue(
            np.array_equal(
                result["outputs"]["mask"].copy_to_host(),
                np.asarray([False, True, True, False, False, True], dtype=np.bool_),
            )
        )
        self.assertFalse(result["app_specific_semantics_allowed"])
        self.assertFalse(result["host_column_materialization_used"])

    def test_uint32_equal_mask_rejects_out_of_range_target_when_cuda_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        values = cuda.to_device(np.asarray([1], dtype=np.uint32))
        with self.assertRaisesRegex(ValueError, "target must fit uint32"):
            rt.run_numba_uint32_equal_mask(values, target=-1)
        with self.assertRaisesRegex(ValueError, "target must fit uint32"):
            rt.run_numba_uint32_equal_mask(values, target=0x1_0000_0000)

    def test_uint32_equal_mask_reference_fallback_matches_contract(self) -> None:
        result = rt.execute_v2_5_partner_continuation_reference(
            "uint32_equal_mask",
            {"values": [0, 3, 3, 9], "target": 3},
        )
        self.assertEqual(result["partner"], rt.V2_5_REFERENCE_PARTNER)
        self.assertEqual(result["outputs"], {"mask": [False, True, True, False]})
        self.assertFalse(result["promoted_performance_path"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])

    def test_uint32_equal_mask_reference_rejects_out_of_range_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "values values must fit uint32"):
            rt.execute_v2_5_partner_continuation_reference(
                "uint32_equal_mask",
                {"values": [0x1_0000_0000], "target": 0},
            )
        with self.assertRaisesRegex(ValueError, "target must fit uint32"):
            rt.execute_v2_5_partner_continuation_reference(
                "uint32_equal_mask",
                {"values": [0], "target": 0x1_0000_0000},
            )


if __name__ == "__main__":
    unittest.main()
