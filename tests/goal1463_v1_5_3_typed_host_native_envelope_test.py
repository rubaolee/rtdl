import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


class _TypedHostNativeCollectKSymbol:
    def __init__(self) -> None:
        self.input_addresses = []
        self.output_addresses = []

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
        self.input_addresses.append(ctypes.addressof(candidate_rows.contents))
        self.output_addresses.append(ctypes.addressof(rows_out.contents))
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
            for column_index, value in enumerate(row):
                rows_out[row_index * int(row_width) + column_index] = value
        return 0


class _LyingTypedHostNativeCollectKSymbol:
    def __init__(self) -> None:
        self.argtypes = None
        self.restype = None

    def __call__(
        self,
        _candidate_rows,
        _candidate_count,
        _row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        _error,
        _error_size,
    ):
        capacity = int(row_capacity)
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = capacity + 1
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for index in range(capacity):
            rows_out[index] = 100 + index
        return 0


class Goal1463V153TypedHostNativeEnvelopeTest(unittest.TestCase):
    def test_native_envelope_uses_prepared_input_and_output_buffers(self) -> None:
        symbol = _TypedHostNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        input_descriptor = rt.prepare_collect_k_i64_host_input_buffer(
            ((2, 20), (1, 10), (1, 10)),
            row_width=2,
        )
        output_buffer = (ctypes.c_int64 * 4)()
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        envelope = rt.run_native_collect_k_bounded_with_typed_host_buffers(
            input_descriptor,
            output_descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            backend="embree",
        )

        self.assertEqual(envelope["status"], "typed_host_input_prepared_host_output_native_envelope")
        self.assertEqual(envelope["result"]["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(envelope["result_buffer_descriptor"]["valid_shape"], (2, 2))
        self.assertTrue(envelope["typed_contiguous_host_buffer_path"])
        self.assertTrue(envelope["prepared_output_buffer_reused_by_python_wrapper"])
        self.assertEqual(symbol.input_addresses, [envelope["input_buffer_address"]])
        self.assertEqual(symbol.output_addresses, [envelope["output_buffer_address"]])
        self.assertIs(envelope["true_zero_copy_authorized"], False)
        self.assertIs(envelope["public_speedup_wording_authorized"], False)
        self.assertIn("partner tensor handoff", envelope["claim_boundary"])

    def test_native_envelope_rejects_row_width_mismatch(self) -> None:
        input_descriptor = rt.prepare_collect_k_i64_host_input_buffer(((1, 10),), row_width=2)
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=1,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )
        output_buffer = (ctypes.c_int64 * 1)()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=_TypedHostNativeCollectKSymbol())

        with self.assertRaisesRegex(ValueError, "row_width mismatch"):
            rt.run_native_collect_k_bounded_with_typed_host_buffers(
                input_descriptor,
                output_descriptor,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                backend="embree",
            )

    def test_native_envelope_fails_closed_when_emitted_count_exceeds_capacity(self) -> None:
        input_descriptor = rt.prepare_collect_k_i64_host_input_buffer(((1,), (2,)), row_width=1)
        output_descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=1,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )
        output_buffer = (ctypes.c_int64 * 1)()
        library = SimpleNamespace(
            rtdl_embree_collect_k_bounded_i64=_LyingTypedHostNativeCollectKSymbol()
        )

        with self.assertRaisesRegex(RuntimeError, "emitted_count exceeded prepared output capacity"):
            rt.run_native_collect_k_bounded_with_typed_host_buffers(
                input_descriptor,
                output_descriptor,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                backend="embree",
            )


if __name__ == "__main__":
    unittest.main()
