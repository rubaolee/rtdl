import ctypes
import unittest
from pathlib import Path
from types import SimpleNamespace

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1525_v1_5_4_typed_host_zero_capacity_guard_2026-05-08.md"


class _ZeroCapacityTypedHostSymbol:
    def __init__(self) -> None:
        self.argtypes = None
        self.restype = None
        self.calls = []

    def __call__(
        self,
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        self.calls.append(
            {
                "candidate_rows_is_none": candidate_rows is None,
                "candidate_count": int(candidate_count),
                "row_width": int(row_width),
                "rows_out_is_none": rows_out is None,
                "row_capacity": int(row_capacity),
            }
        )
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = 0
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        return 0


class Goal1525V154TypedHostZeroCapacityGuardTest(unittest.TestCase):
    def test_report_records_narrow_zero_capacity_boundary(self) -> None:
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("empty-input, zero-capacity boundary", text)
        self.assertIn("output_buffer=None", text)
        self.assertIn("does not authorize stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("does not measure Embree performance", text)

    def test_typed_host_native_envelope_allows_empty_zero_capacity_without_output_buffer(self) -> None:
        symbol = _ZeroCapacityTypedHostSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        input_descriptor = rt.prepare_collect_k_i64_host_input_buffer((), row_width=2)
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=0,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        envelope = rt.run_native_collect_k_bounded_with_typed_host_buffers(
            input_descriptor,
            output_descriptor,
            output_buffer=None,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            backend="embree",
        )

        self.assertEqual(symbol.calls, [
            {
                "candidate_rows_is_none": False,
                "candidate_count": 0,
                "row_width": 2,
                "rows_out_is_none": True,
                "row_capacity": 0,
            }
        ])
        self.assertEqual(envelope["result"]["candidate_id_rows"], ())
        self.assertEqual(envelope["result"]["valid_count"], 0)
        self.assertEqual(envelope["result_buffer_descriptor"]["shape"], (0, 2))
        self.assertEqual(envelope["result_buffer_descriptor"]["valid_shape"], (0, 2))
        self.assertIsNone(envelope["output_buffer_address"])
        self.assertIs(envelope["true_zero_copy_authorized"], False)


if __name__ == "__main__":
    unittest.main()
