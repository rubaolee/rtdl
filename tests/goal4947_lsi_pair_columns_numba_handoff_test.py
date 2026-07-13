from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_RUNTIME = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
ROW_BUFFER = ROOT / "src" / "rtdsl" / "device_column_row_buffer.py"


def _numba_cuda_available() -> bool:
    try:
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class _CudaInterfaceOnlyColumn:
    """Small test wrapper that looks like an RTDL raw CUDA column to Numba."""

    def __init__(self, device_array) -> None:
        self._device_array = device_array

    @property
    def __cuda_array_interface__(self):
        return self._device_array.__cuda_array_interface__


class Goal4947LsiPairColumnsNumbaHandoffTest(unittest.TestCase):
    def test_segmented_count_accepts_cuda_array_interface_columns(self) -> None:
        source = NUMBA_RUNTIME.read_text(encoding="utf-8")
        start = source.index("def run_numba_segmented_count_i64(")
        end = source.index("def run_numba_label_count_and_flag_count_i64(", start)
        body = source[start:end]

        self.assertIn("_as_numba_cuda_vector(group_ids", body)
        self.assertNotIn("_validate_numba_cuda_vector(group_ids", body)

    def test_lsi_pair_row_buffer_remains_generic(self) -> None:
        source = ROW_BUFFER.read_text(encoding="utf-8")
        start = source.index("def device_column_row_buffer_from_native_pair_columns(")
        end = source.index("def device_column_row_buffer_from_point_location_id_columns(", start)
        body = source[start:end].lower()

        self.assertIn('"left_id"', body)
        self.assertIn('"right_id"', body)
        self.assertIn("native_device_columns", body)
        self.assertNotIn("rayjoin", body)
        self.assertNotIn("overlay", body)
        self.assertNotIn("output_chain", body)

    def test_segmented_count_executes_on_cuda_array_interface_column_when_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        values = cuda.to_device(np.asarray([0, 2, 2, 1, 0], dtype=np.int64))
        wrapped = _CudaInterfaceOnlyColumn(values)
        result = rt.run_numba_segmented_count_i64(wrapped, group_count=4)

        self.assertEqual(result["operation"], rt.NUMBA_SEGMENTED_COUNT_I64_OPERATION)
        self.assertEqual(result["outputs"]["counts"].copy_to_host().tolist(), [2, 1, 2, 0])
        self.assertFalse(result["promoted_performance_path"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
