import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


class _CapturingNativeCollectKSymbol:
    def __init__(self) -> None:
        self.rows_out_address = None
        self.row_capacity = None

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
        self.rows_out_address = ctypes.addressof(rows_out.contents) if rows_out else None
        self.row_capacity = int(row_capacity)
        rows = []
        for row_index in range(int(candidate_count)):
            start = row_index * int(row_width)
            rows.append(tuple(int(candidate_rows[start + column]) for column in range(int(row_width))))
        normalized = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(normalized)
        overflowed = len(normalized) > int(row_capacity)
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1 if overflowed else 0
        if overflowed:
            return 0
        for row_index, row in enumerate(normalized):
            for column, value in enumerate(row):
                rows_out[row_index * int(row_width) + column] = value
        return 0


class Goal1446V152NativePreparedHostOutputBufferTest(unittest.TestCase):
    def test_native_wrapper_passes_caller_owned_ctypes_output_buffer(self) -> None:
        symbol = _CapturingNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        output_buffer = (ctypes.c_int64 * 4)()

        result = rt.collect_native_i64_rows_into_prepared_output_buffer(
            ((2, 20), (1, 10), (1, 10)),
            output_buffer=output_buffer,
            capacity=2,
            row_width=2,
            backend="embree",
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
        )

        self.assertEqual(symbol.rows_out_address, ctypes.addressof(output_buffer))
        self.assertEqual(symbol.row_capacity, 2)
        self.assertEqual(tuple(output_buffer), (1, 10, 2, 20))
        self.assertEqual(result["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertIs(result["prepared_output_buffer_supplied"], True)
        self.assertEqual(result["prepared_output_buffer_kind"], "ctypes_host_i64")
        self.assertIs(result["prepared_output_buffer_reused_by_python_wrapper"], True)
        self.assertIn("host prepared-buffer plumbing only", result["claim_boundary"])

    def test_zero_capacity_allows_none_output_buffer_for_empty_collection(self) -> None:
        symbol = _CapturingNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)

        result = rt.collect_native_i64_rows_into_prepared_output_buffer(
            (),
            output_buffer=None,
            capacity=0,
            row_width=2,
            backend="embree",
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
        )

        self.assertIsNone(symbol.rows_out_address)
        self.assertEqual(result["candidate_id_rows"], ())
        self.assertEqual(result["valid_count"], 0)

    def test_prepared_output_buffer_rejects_too_small_buffer(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_CapturingNativeCollectKSymbol())
        output_buffer = (ctypes.c_int64 * 1)()

        with self.assertRaisesRegex(ValueError, "smaller than capacity"):
            rt.collect_native_i64_rows_into_prepared_output_buffer(
                ((1, 10),),
                output_buffer=output_buffer,
                capacity=1,
                row_width=2,
                backend="embree",
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

    def test_prepared_output_buffer_fails_closed_on_overflow(self) -> None:
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_CapturingNativeCollectKSymbol())
        output_buffer = (ctypes.c_int64 * 2)()

        with self.assertRaisesRegex(RuntimeError, "overflowed capacity"):
            rt.collect_native_i64_rows_into_prepared_output_buffer(
                ((1, 10), (2, 20)),
                output_buffer=output_buffer,
                capacity=1,
                row_width=2,
                backend="embree",
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )


if __name__ == "__main__":
    unittest.main()
