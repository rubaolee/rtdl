import ctypes
import unittest
from types import SimpleNamespace

import rtdsl as rt


class _CapturingNativeCollectKSymbol:
    def __init__(self) -> None:
        self.rows_out_address = None

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


class Goal1447V152PreparedHostOutputEnvelopeTest(unittest.TestCase):
    def test_native_host_output_envelope_binds_caller_owned_buffer_to_descriptor(self) -> None:
        symbol = _CapturingNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        output_buffer = (ctypes.c_int64 * 4)()
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=2,
            row_width=2,
            backend="embree",
            device="cpu",
            owner="native",
            copy_boundary="prepared_host_buffer_reuse",
        )

        envelope = rt.run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
            ((2, 20), (1, 10), (1, 10)),
            prepared,
            output_buffer=output_buffer,
            library=library,
            symbol_name="rtdl_embree_collect_k_bounded_i64",
            candidate_source_symbol="test_candidate_rows",
        )

        self.assertEqual(symbol.rows_out_address, ctypes.addressof(output_buffer))
        self.assertEqual(tuple(output_buffer), (1, 10, 2, 20))
        self.assertEqual(envelope["execution_mode"], "native_generic_symbol_prepared_host_output_envelope")
        self.assertEqual(envelope["result"]["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(envelope["result_buffer_descriptor"]["valid_shape"], (2, 2))
        self.assertEqual(envelope["result_buffer_descriptor"]["prepared_copy_boundary"], "prepared_host_buffer_reuse")
        self.assertIs(envelope["prepared_descriptor_compatible"], True)
        self.assertIs(envelope["prepared_output_buffer_reused_by_python_wrapper"], True)
        self.assertIs(envelope["true_zero_copy_authorized"], False)

    def test_native_host_output_envelope_rejects_cuda_or_non_host_boundary(self) -> None:
        symbol = _CapturingNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        output_buffer = (ctypes.c_int64 * 2)()

        cuda_prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            device="cuda",
            owner="native",
            copy_boundary="prepared_device_buffer_reuse",
        )
        with self.assertRaisesRegex(ValueError, "requires device=cpu"):
            rt.run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
                ((1, 10),),
                cuda_prepared,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

        metadata_prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            device="cpu",
            copy_boundary="native_row_buffer_metadata",
        )
        with self.assertRaisesRegex(ValueError, "prepared_host_buffer_reuse"):
            rt.run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
                ((1, 10),),
                metadata_prepared,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )

    def test_native_host_output_envelope_keeps_overflow_fail_closed(self) -> None:
        symbol = _CapturingNativeCollectKSymbol()
        library = SimpleNamespace(rtdl_embree_collect_k_bounded_i64=symbol)
        output_buffer = (ctypes.c_int64 * 2)()
        prepared = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=1,
            row_width=2,
            backend="embree",
            copy_boundary="prepared_host_buffer_reuse",
        )

        with self.assertRaisesRegex(RuntimeError, "overflowed capacity"):
            rt.run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
                ((1, 10), (2, 20)),
                prepared,
                output_buffer=output_buffer,
                library=library,
                symbol_name="rtdl_embree_collect_k_bounded_i64",
                candidate_source_symbol="test_candidate_rows",
            )


if __name__ == "__main__":
    unittest.main()
